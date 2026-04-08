"""
OEE 분석 모듈

종합 설비 효율(Overall Equipment Effectiveness) 계산 및 분석
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple
from scipy import stats

from config import OEE_TARGETS, IMPROVEMENT_DATE, DOWNTIME_TYPES
from utils import logger, compare_before_after, print_section


class OEEAnalyzer:
    """OEE 분석 클래스"""
    
    def __init__(self, prod_data: pd.DataFrame, equip_data: pd.DataFrame, 
                downtime_data: pd.DataFrame = None):
        """
        Parameters:
        -----------
        prod_data : DataFrame
            생산 데이터 (production_log)
        equip_data : DataFrame
            설비 정보 (equipment)
        downtime_data : DataFrame
            비가동 데이터 (downtime_log)
        """
        self.prod = prod_data.copy()
        self.equip = equip_data.copy()
        self.downtime = downtime_data.copy() if downtime_data is not None else None
        self.results = {}
        
        # Equipment에서 line 정보 추가
        if 'line' not in self.prod.columns and 'line' in self.equip.columns:
            self.prod = self.prod.merge(
                self.equip[['equipment_id', 'line']],
                on='equipment_id',
                how='left'
            )
    
    # ============================================
    # OEE 계산
    # ============================================
    
    def calculate_oee(self, availability: float, performance: float, 
                     quality: float) -> float:
        """OEE = 가동률 × 성능률 × 양품률"""
        return (availability / 100) * (performance / 100) * (quality / 100) * 100
    
    
    def calculate_metrics(self, data: pd.DataFrame, equip_data: pd.DataFrame
                         ) -> Dict[str, float]:
        """
        OEE 3대 요소 계산
        
        Returns:
        --------
        {'availability': float, 'performance': float, 'quality': float, 'oee': float}
        """
        
        # 1. 양품률 (Quality) = 양품 / 전체
        total_qty = data['actual_quantity'].sum()
        good_qty = data['good_quantity'].sum()
        quality = (good_qty / total_qty * 100) if total_qty > 0 else 0
        
        # 2. 성능률 (Performance)
        operating_time = data['actual_operating_time_min'].sum()
        if operating_time > 0 and total_qty > 0:
            avg_cycle_time = operating_time / total_qty
            standard_cycle_time = avg_cycle_time * 0.95
            performance = min((total_qty * standard_cycle_time) / operating_time * 100, 100)
        else:
            performance = 0
        
        # 3. 가동률 (Availability)
        n_days = (data['production_date'].max() - data['production_date'].min()).days + 1
        planned_hours_per_day = 16  # 1일 2교대 8시간씩
        planned_time_min = planned_hours_per_day * 60 * n_days * len(equip_data)
        actual_time_min = data['actual_operating_time_min'].sum()
        availability = (actual_time_min / planned_time_min * 100) if planned_time_min > 0 else 0
        
        # 4. OEE
        oee = self.calculate_oee(availability, performance, quality)
        
        return {
            'availability': round(availability, 2),
            'performance': round(performance, 2),
            'quality': round(quality, 2),
            'oee': round(oee, 2)
        }
    
    
    # ============================================
    # 수준별 분석
    # ============================================
    
    def calculate_overall_oee(self) -> Dict:
        """전체 OEE 계산"""
        metrics = self.calculate_metrics(self.prod, self.equip)
        self.results['overall'] = metrics
        return metrics
    
    
    def calculate_by_equipment(self) -> pd.DataFrame:
        """설비별 OEE 계산"""
        result = []
        
        for equip_id in self.prod['equipment_id'].unique():
            equip_prod = self.prod[self.prod['equipment_id'] == equip_id]
            if len(equip_prod) == 0:
                continue
            
            equip_info = self.equip[self.equip['equipment_id'] == equip_id]
            if len(equip_info) == 0:
                continue
            
            metrics = self.calculate_metrics(equip_prod, equip_info)
            
            result.append({
                'equipment_id': equip_id,
                'line': equip_info.iloc[0]['line'],
                'equipment_type': equip_info.iloc[0]['equipment_type'],
                'availability': metrics['availability'],
                'performance': metrics['performance'],
                'quality': metrics['quality'],
                'oee': metrics['oee'],
                'production_qty': equip_prod['actual_quantity'].sum(),
                'good_qty': equip_prod['good_quantity'].sum(),
                'operating_hours': equip_prod['actual_operating_time_min'].sum() / 60
            })
        
        df = pd.DataFrame(result).sort_values('oee', ascending=False)
        self.results['by_equipment'] = df
        return df
    
    
    def calculate_by_line(self) -> pd.DataFrame:
        """라인별 OEE 계산"""
        result = []
        
        for line in self.prod['line'].unique():
            line_prod = self.prod[self.prod['line'] == line]
            
            metrics = self.calculate_metrics(line_prod, self.equip)
            
            result.append({
                'line': line,
                'availability': metrics['availability'],
                'performance': metrics['performance'],
                'quality': metrics['quality'],
                'oee': metrics['oee'],
                'production_qty': line_prod['actual_quantity'].sum(),
                'equipment_count': line_prod['equipment_id'].nunique()
            })
        
        df = pd.DataFrame(result).sort_values('oee', ascending=False)
        self.results['by_line'] = df
        return df
    
    
    def calculate_by_period(self, period: str = 'W') -> pd.DataFrame:
        """기간별 OEE (일/주/월)"""
        
        data = self.prod.copy()
        data['period'] = data['production_date'].dt.to_period(period)
        
        result = []
        
        for period_key in sorted(data['period'].unique()):
            period_data = data[data['period'] == period_key]
            metrics = self.calculate_metrics(period_data, self.equip)
            
            result.append({
                'period': str(period_key),
                'availability': metrics['availability'],
                'performance': metrics['performance'],
                'quality': metrics['quality'],
                'oee': metrics['oee'],
                'production_qty': period_data['actual_quantity'].sum(),
            })
        
        df = pd.DataFrame(result)
        self.results['by_period'] = df
        return df
    
    
    # ============================================
    # Six Big Losses
    # ============================================
    
    def analyze_six_big_losses(self) -> pd.DataFrame:
        """Six Big Losses 분석"""
        
        if self.downtime is None or len(self.downtime) == 0:
            logger.warning("비가동 데이터 없음")
            return pd.DataFrame()
        
        losses = self.downtime.groupby('downtime_type').agg({
            'duration_min': ['sum', 'mean', 'count']
        }).round(2)
        
        losses.columns = ['total_min', 'avg_min', 'frequency']
        losses['total_hours'] = (losses['total_min'] / 60).round(2)
        losses['percentage'] = (losses['total_min'] / losses['total_min'].sum() * 100).round(2)
        losses = losses.sort_values('total_min', ascending=False)
        
        self.results['six_big_losses'] = losses
        return losses
    
    
    # ============================================
    # 개선 효과 분석
    # ============================================
    
    def analyze_improvement(self) -> Dict:
        """개선 전/후 비교 (3월 기준)"""
        
        improvement_date = pd.to_datetime(IMPROVEMENT_DATE)
        pre = self.prod[self.prod['production_date'] < improvement_date]
        post = self.prod[self.prod['production_date'] >= improvement_date]
        
        if len(pre) == 0 or len(post) == 0:
            logger.warning("개선 전/후 데이터 부족")
            return {}
        
        pre_metrics = self.calculate_metrics(pre, self.equip)
        post_metrics = self.calculate_metrics(post, self.equip)
        
        comparison = {
            'metrics': ['가동률(%)', '성능률(%)', '양품률(%)', 'OEE(%)'],
            'pre': [
                pre_metrics['availability'],
                pre_metrics['performance'],
                pre_metrics['quality'],
                pre_metrics['oee']
            ],
            'post': [
                post_metrics['availability'],
                post_metrics['performance'],
                post_metrics['quality'],
                post_metrics['oee']
            ]
        }
        
        comparison_df = pd.DataFrame(comparison)
        comparison_df['change_pp'] = comparison_df['post'] - comparison_df['pre']
        comparison_df['change_pct'] = ((comparison_df['post'] - comparison_df['pre']) 
                                      / comparison_df['pre'] * 100).round(2)
        
        self.results['improvement'] = comparison_df
        return comparison_df.to_dict()
    
    
    def statistical_test_improvement(self) -> Dict:
        """개선 효과 통계 검증"""
        
        improvement_date = pd.to_datetime(IMPROVEMENT_DATE)
        pre = self.prod[self.prod['production_date'] < improvement_date]
        post = self.prod[self.prod['production_date'] >= improvement_date]
        
        if len(pre) == 0 or len(post) == 0:
            return {}
        
        # 양품률 T-검정
        pre_quality = pre['good_quantity'] / pre['actual_quantity']
        post_quality = post['good_quantity'] / post['actual_quantity']
        
        t_stat, p_value = stats.ttest_ind(post_quality, pre_quality, equal_var=False)
        
        result = {
            't_statistic': round(t_stat, 4),
            'p_value': round(p_value, 4),
            'significant': 'Yes' if p_value < 0.05 else 'No',
            'confidence': '95%' if p_value < 0.05 else '불충분'
        }
        
        self.results['statistical_test'] = result
        return result
    
    
    # ============================================
    # 종합 분석 실행
    # ============================================
    
    def run_full_analysis(self) -> Dict:
        """전체 분석 실행"""
        
        print_section("OEE 분석", 1)
        
        # 전체 OEE
        print("\n[1] 전체 OEE")
        overall = self.calculate_overall_oee()
        print(f"  OEE: {overall['oee']:.2f}%")
        print(f"  가동률: {overall['availability']:.2f}%")
        print(f"  성능률: {overall['performance']:.2f}%")
        print(f"  양품률: {overall['quality']:.2f}%")
        
        # 설비별 OEE
        print("\n[2] 설비별 OEE (상위 10개)")
        equip_oee = self.calculate_by_equipment()
        print(equip_oee[['equipment_id', 'line', 'oee', 'quality']].head(10).to_string())
        
        # 라인별 OEE
        print("\n[3] 라인별 OEE")
        line_oee = self.calculate_by_line()
        print(line_oee.to_string())
        
        # 기간별 OEE
        print("\n[4] 기간별 OEE (주간)")
        period_oee = self.calculate_by_period('W')
        print(period_oee.tail(10).to_string())
        
        # Six Big Losses
        if self.downtime is not None:
            print("\n[5] Six Big Losses")
            losses = self.analyze_six_big_losses()
            print(losses.to_string())
        
        # 개선 효과
        print("\n[6] 개선 효과 (3월 기준)")
        improvement = self.analyze_improvement()
        if improvement:
            imp_df = pd.DataFrame(improvement)
            print(imp_df.to_string())
            
            # 통계 검증
            print("\n[7] 통계적 유의성")
            stat_test = self.statistical_test_improvement()
            for k, v in stat_test.items():
                print(f"  {k}: {v}")
        
        logger.info("✓ OEE 분석 완료")
        return self.results


if __name__ == "__main__":
    print("OEE 분석 모듈 준비 완료")
