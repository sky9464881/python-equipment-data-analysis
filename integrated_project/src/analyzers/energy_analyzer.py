"""
에너지 관리 및 효율성 분석 모듈

에너지 소비, 효율성, 비용 분석
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple
from datetime import datetime, timedelta

from config import ENERGY_TARGETS
from utils import logger, print_section, format_currency, format_large_number

# 간단한 요금 정의 (config에서 가져올 수 없으므로)
TARIFF_RATES = {
    'standard': 150,
    'peak': 350,
    'offpeak': 150
}

class EnergyAnalyzer:
    """에너지 관리 및 효율성 분석 클래스"""
    
    def __init__(self, energy_data: pd.DataFrame, production_data: pd.DataFrame = None):
        """
        Parameters:
        -----------
        energy_data : DataFrame
            에너지 사용량 시계열 데이터 (시간별, 일별)
        production_data : DataFrame
            생산 데이터 (생산량)
        """
        self.energy = energy_data.copy()
        self.production = production_data.copy() if production_data is not None else None
        self.results = {}
    
    
    # ============================================
    # 1. 기본 에너지 분석
    # ============================================
    
    def analyze_energy_consumption(self) -> Dict:
        """전체 에너지 소비 분석"""
        
        energy_cols = ['electricity_kwh', 'gas_m3', 'water_m3']
        consumption = {}
        
        for col in energy_cols:
            if col in self.energy.columns:
                data = self.energy[col].dropna()
                if len(data) > 0:
                    consumption[col] = {
                        'total': data.sum(),
                        'daily_avg': data.mean(),
                        'daily_max': data.max(),
                        'daily_min': data.min(),
                        'std': data.std()
                    }
        
        self.results['consumption'] = consumption
        return consumption
    
    
    # ============================================
    # 2. 에너지 효율성 분석
    # ============================================
    
    def calculate_energy_efficiency(self) -> Dict:
        """생산량 대비 에너지 효율성"""
        
        if self.production is None or 'electricity_kwh' not in self.energy.columns:
            return {}
        
        # 일별 병합
        energy_daily = self.energy.groupby(self.energy.get('date', pd.date_range(
            start='2024-01-01', periods=len(self.energy), freq='D')))['electricity_kwh'].sum()
        
        production_daily = self.production.groupby(
            self.production.get('date', pd.date_range(start='2024-01-01', 
                                                     periods=len(self.production), freq='D'))
        )['production_units'].sum()
        
        # 공통 인덱스 찾기
        common_dates = energy_daily.index.intersection(production_daily.index)
        
        if len(common_dates) == 0:
            logger.warning("에너지-생산 데이터 날짜 불일치")
            return {}
        
        efficiency = (energy_daily.loc[common_dates] / 
                     production_daily.loc[common_dates]).dropna()
        
        if len(efficiency) == 0:
            return {}
        
        target = ENERGY_TARGETS.get('kwh_per_unit', 0.5)
        
        return {
            'avg_kwh_per_unit': round(efficiency.mean(), 4),
            'target_kwh_per_unit': target,
            'efficiency_ratio': round(target / efficiency.mean(), 3),
            'best_day_kwh_per_unit': round(efficiency.min(), 4),
            'worst_day_kwh_per_unit': round(efficiency.max(), 4)
        }
    
    
    # ============================================
    # 3. 피크 로드 관리
    # ============================================
    
    def analyze_peak_load(self, hour_col: str = 'hour') -> Dict:
        """시간대별 피크 로드 분석"""
        
        if 'electricity_kwh' not in self.energy.columns:
            return {}
        
        # 시간대별 분석
        if hour_col in self.energy.columns:
            hourly = self.energy.groupby(hour_col)['electricity_kwh'].agg([
                'mean', 'max', 'std', 'count'
            ]).round(2)
            
            # 피크: 09-17시 / 비피크: 18-08시 구분
            peak_hours = range(9, 18)
            peak_load = self.energy[self.energy[hour_col].isin(peak_hours)]['electricity_kwh'].mean()
            offpeak_load = self.energy[~self.energy[hour_col].isin(peak_hours)]['electricity_kwh'].mean()
            
            return {
                'peak_avg_kwh': round(peak_load, 2),
                'offpeak_avg_kwh': round(offpeak_load, 2),
                'peak_offpeak_ratio': round(peak_load / offpeak_load, 2) if offpeak_load > 0 else 0,
                'peak_reduction_opportunity': round((peak_load - offpeak_load) * 0.2, 2)
            }
        
        return {}
    
    
    # ============================================
    # 4. 제조 단계별 에너지 분석
    # ============================================
    
    def analyze_energy_by_process(self, process_col: str = 'process_name') -> pd.DataFrame:
        """공정별 에너지 소비 분석"""
        
        if process_col not in self.energy.columns or 'electricity_kwh' not in self.energy.columns:
            return pd.DataFrame()
        
        process_energy = self.energy.groupby(process_col)['electricity_kwh'].agg([
            'sum', 'mean', 'count'
        ]).round(2)
        
        process_energy.columns = ['total_kwh', 'avg_kwh', 'records']
        
        # 비율 계산
        process_energy['pct_of_total'] = (
            process_energy['total_kwh'] / process_energy['total_kwh'].sum() * 100
        ).round(2)
        
        process_energy = process_energy.sort_values('total_kwh', ascending=False)
        
        self.results['energy_by_process'] = process_energy
        return process_energy
    
    
    # ============================================
    # 5. 요일/월별 에너지 분석
    # ============================================
    
    def analyze_energy_by_time(self) -> Dict:
        """시간대별 에너지 소비 패턴"""
        
        if 'electricity_kwh' not in self.energy.columns:
            return {}
        
        energy_dup = self.energy.copy()
        
        # 날짜 컬럼 자동 감지
        date_col = None
        for col in ['date', 'timestamp', 'Date', 'Timestamp']:
            if col in energy_dup.columns:
                date_col = col
                break
        
        if date_col:
            energy_dup[date_col] = pd.to_datetime(energy_dup[date_col])
            
            # 요일별
            energy_dup['dayofweek'] = energy_dup[date_col].dt.day_name()
            dayofweek_energy = energy_dup.groupby('dayofweek')['electricity_kwh'].agg(['mean', 'std'])
            
            # 월별
            energy_dup['month'] = energy_dup[date_col].dt.month
            monthly_energy = energy_dup.groupby('month')['electricity_kwh'].agg(['sum', 'mean'])
        else:
            return {}
        
        return {
            'dayofweek': dayofweek_energy.to_dict() if 'dayofweek' in locals() else {},
            'monthly': monthly_energy.to_dict() if 'monthly' in locals() else {}
        }
    
    
    # ============================================
    # 6. 에너지 비용 분석
    # ============================================
    
    def calculate_energy_cost(self) -> Dict:
        """시간대별 요금제 적용 비용 계산"""
        
        if 'electricity_kwh' not in self.energy.columns:
            return {}
        
        energy_dup = self.energy.copy()
        
        # 시간 컬럼 찾기
        hour_col = None
        for col in ['hour', 'Hour', 'time']:
            if col in energy_dup.columns:
                hour_col = col
                break
        
        if hour_col is None:
            # 시간 컬럼 없으면 모든 시간 동일 요금 적용
            tariff = TARIFF_RATES.get('standard', 150)
            return {
                'total_cost_won': round(energy_dup['electricity_kwh'].sum() * tariff),
                'average_tariff': tariff,
                'total_kwh': round(energy_dup['electricity_kwh'].sum(), 2)
            }
        
        cost = 0
        peak_cost = 0
        offpeak_cost = 0
        
        peak_tariff = TARIFF_RATES.get('peak', 350)
        offpeak_tariff = TARIFF_RATES.get('offpeak', 150)
        
        for idx, row in energy_dup.iterrows():
            kwh = row['electricity_kwh']
            hour = row[hour_col]
            
            # 피크: 09-17시
            if 9 <= hour <= 17:
                cost += kwh * peak_tariff
                peak_cost += kwh * peak_tariff
            else:
                cost += kwh * offpeak_tariff
                offpeak_cost += kwh * offpeak_tariff
        
        total_kwh = energy_dup['electricity_kwh'].sum()
        
        return {
            'total_cost_won': round(cost),
            'peak_cost_won': round(peak_cost),
            'offpeak_cost_won': round(offpeak_cost),
            'average_tariff': round(cost / total_kwh, 1) if total_kwh > 0 else 0,
            'peak_tariff': peak_tariff,
            'offpeak_tariff': offpeak_tariff
        }
    
    
    # ============================================
    # 7. 에너지 절감 기회 분석
    # ============================================
    
    def identify_savings_opportunities(self) -> Dict:
        """에너지 절감 기회 식별"""
        
        opportunities = {}
        
        # 1. 피크 로드 시프팅
        peak_analysis = self.analyze_peak_load()
        if peak_analysis and peak_analysis.get('peak_offpeak_ratio', 1) > 1.3:
            monthly_cost = self.calculate_energy_cost()
            if 'peak_cost_won' in monthly_cost:
                savings = monthly_cost['peak_cost_won'] * 0.15  # 15% 절감 가능
                opportunities['peak_shifting'] = {
                    'description': '피크 로드 시프팅 (09-17시 → 18-22시)',
                    'potential_savings_won': round(savings),
                    'monthly_days': 21,
                    'annual_savings_won': round(savings * 12)
                }
        
        # 2. 공정 최적화
        process_energy = self.analyze_energy_by_process()
        if len(process_energy) > 0:
            top_process = process_energy.iloc[0]
            if top_process.get('pct_of_total', 0) > 30:
                potential_savings = top_process['total_kwh'] * 0.1  # 10% 절감
                opportunities['process_optimization'] = {
                    'process': process_energy.index[0],
                    'description': f"상위 공정 ({process_energy.index[0]}) 효율 개선",
                    'current_usage_kwh': round(top_process['total_kwh'], 2),
                    'potential_reduction_percent': 10,
                    'potential_savings_kwh': round(potential_savings, 2)
                }
        
        # 3. 설비 교체 (5년 이상)
        if 'equipment_age_years' in self.energy.columns:
            old_equipment = self.energy[self.energy['equipment_age_years'] >= 5]
            if len(old_equipment) > 0:
                opportunities['equipment_replacement'] = {
                    'description': '5년 이상 노후 설비 교체',
                    'affected_equipment_count': len(old_equipment),
                    'estimated_efficiency_improvement': '15-20%'
                }
        
        self.results['savings_opportunities'] = opportunities
        return opportunities
    
    
    # ============================================
    # 8. 종합 분석 실행
    # ============================================
    
    def run_full_analysis(self) -> Dict:
        """전체 분석 실행"""
        
        print_section("에너지 관리 및 효율성 분석", 1)
        
        # 1. 기본 소비
        print("\n[1] 에너지 소비 현황")
        consumption = self.analyze_energy_consumption()
        for resource, data in consumption.items():
            print(f"  {resource}:")
            print(f"    총 소비: {format_large_number(data['total'])}")
            print(f"    일평균: {data['daily_avg']:.2f}")
        
        # 2. 효율성
        print("\n[2] 에너지 효율성")
        efficiency = self.calculate_energy_efficiency()
        if efficiency:
            print(f"  현재: {efficiency.get('avg_kwh_per_unit', 0):.4f} kWh/단위")
            print(f"  목표: {efficiency.get('target_kwh_per_unit', 0):.4f} kWh/단위")
            print(f"  효율성 비율: {efficiency.get('efficiency_ratio', 1):.2f}배")
        
        # 3. 피크 로드
        print("\n[3] 피크 로드 분석")
        peak = self.analyze_peak_load()
        if peak:
            print(f"  피크시 평균: {peak.get('peak_avg_kwh', 0):.2f} kWh")
            print(f"  비피크 평균: {peak.get('offpeak_avg_kwh', 0):.2f} kWh")
            print(f"  비율: {peak.get('peak_offpeak_ratio', 1):.2f}배")
        
        # 4. 공정별 분석
        print("\n[4] 공정별 에너지 소비")
        process_energy = self.analyze_energy_by_process()
        if len(process_energy) > 0:
            print(process_energy.to_string())
        
        # 5. 비용 분석
        print("\n[5] 에너지 비용 분석")
        cost = self.calculate_energy_cost()
        if cost:
            print(f"  총 비용: {format_currency(cost.get('total_cost_won', 0))}")
            if 'peak_cost_won' in cost:
                print(f"  피크 비용: {format_currency(cost['peak_cost_won'])}")
                print(f"  비피크 비용: {format_currency(cost['offpeak_cost_won'])}")
        
        # 6. 절감 기회
        print("\n[6] 에너지 절감 기회")
        opportunities = self.identify_savings_opportunities()
        for opp_type, details in opportunities.items():
            print(f"  • {details.get('description', opp_type)}")
            if 'annual_savings_won' in details:
                print(f"    연간 절감: {format_currency(details['annual_savings_won'])}")
        
        logger.info("✓ 에너지 분석 완료")
        return self.results


if __name__ == "__main__":
    print("에너지 분석 모듈 준비 완료")
