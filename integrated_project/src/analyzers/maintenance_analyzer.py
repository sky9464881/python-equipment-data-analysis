"""
설비/예지보전 분석 모듈

센서 데이터, 이상탐지, 정비 분석
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, List, Tuple
import warnings

from config import SENSOR_THRESHOLDS, MAINTENANCE_TYPES
from utils import logger, print_section

warnings.filterwarnings('ignore')


class MaintenanceAnalyzer:
    """설비관리 및 예지보전 분석 클래스"""
    
    def __init__(self, sensor_data: pd.DataFrame, maintenance_data: pd.DataFrame = None,
                equipment_data: pd.DataFrame = None, alarm_data: pd.DataFrame = None):
        """
        Parameters:
        -----------
        sensor_data : DataFrame
            센서 시계열 데이터
        maintenance_data : DataFrame
            정비 기록
        equipment_data : DataFrame
            설비 정보
        alarm_data : DataFrame
            알람 기록
        """
        self.sensor = sensor_data.copy()
        self.maintenance = maintenance_data.copy() if maintenance_data is not None else None
        self.equipment = equipment_data.copy() if equipment_data is not None else None
        self.alarm = alarm_data.copy() if alarm_data is not None else None
        self.results = {}
    
    # ============================================
    # 1. 센서 데이터 기본 분석
    # ============================================
    
    def analyze_sensor_statistics(self) -> Dict:
        """센서별 기본 통계"""
        
        sensor_cols = ['temperature_c', 'vibration_mms', 'current_a', 'pressure_bar']
        stats_dict = {}
        
        for col in sensor_cols:
            if col in self.sensor.columns:
                data = self.sensor[col].dropna()
                if len(data) > 0:
                    stats_dict[col] = {
                        'mean': data.mean(),
                        'std': data.std(),
                        'min': data.min(),
                        'max': data.max(),
                        'q25': data.quantile(0.25),
                        'q75': data.quantile(0.75)
                    }
        
        self.results['sensor_stats'] = stats_dict
        return stats_dict
    
    
    # ============================================
    # 2. 이상치 탐지 (3-sigma, IQR)
    # ============================================
    
    def detect_anomalies_zscore(self, column: str, threshold: float = 3.0
                               ) -> pd.Series:
        """Z-score 기반 이상탐지"""
        
        if column not in self.sensor.columns:
            return pd.Series(dtype=bool)
        
        data = self.sensor[column].fillna(self.sensor[column].mean())
        z_scores = np.abs((data - data.mean()) / data.std())
        
        return z_scores > threshold
    
    
    def detect_anomalies_iqr(self, column: str, multiplier: float = 1.5) -> pd.Series:
        """IQR 기반 이상탐지"""
        
        if column not in self.sensor.columns:
            return pd.Series(dtype=bool)
        
        Q1 = self.sensor[column].quantile(0.25)
        Q3 = self.sensor[column].quantile(0.75)
        IQR = Q3 - Q1
        
        lower = Q1 - multiplier * IQR
        upper = Q3 + multiplier * IQR
        
        return (self.sensor[column] < lower) | (self.sensor[column] > upper)
    
    
    def detect_all_anomalies(self) -> Dict[str, int]:
        """전체 이상치 탐지"""
        
        anomalies = {}
        sensor_cols = {
            'temperature_c': SENSOR_THRESHOLDS.get('temperature', {}),
            'vibration_mms': SENSOR_THRESHOLDS.get('vibration', {}),
            'current_a': SENSOR_THRESHOLDS.get('current', {}),
            'pressure_bar': SENSOR_THRESHOLDS.get('pressure', {})
        }
        
        for col, thresholds in sensor_cols.items():
            if col not in self.sensor.columns:
                continue
            
            # 임계값 기반
            if 'warning' in thresholds and 'critical' in thresholds:
                warning = (self.sensor[col] > thresholds['warning']).sum()
                critical = (self.sensor[col] > thresholds['critical']).sum()
                anomalies[f"{col}_warning"] = warning
                anomalies[f"{col}_critical"] = critical
            
            # 통계적 이상
            z_anomaly = self.detect_anomalies_zscore(col).sum()
            anomalies[f"{col}_zscore"] = z_anomaly
        
        self.results['anomalies'] = anomalies
        return anomalies
    
    
    # ============================================
    # 3. 트렌드 분석 (열화 진행)
    # ============================================
    
    def detect_degradation_trend(self, column: str, window: int = 10
                                ) -> Dict:
        """센서값 열화 추세 탐지"""
        
        if column not in self.sensor.columns or len(self.sensor) < window:
            return {}
        
        data = self.sensor[column].dropna()
        
        # 선형 회귀로 추세 분석
        if len(data) >= window:
            x = np.arange(len(data))
            y = data.values
            
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
            
            # 추세 판정
            trend_direction = "증가" if slope > 0 else "감소"
            trend_strength = abs(r_value)
            significant = "예" if p_value < 0.05 else "아니오"
            
            return {
                'slope': round(slope, 6),
                'r_squared': round(r_value**2, 4),
                'p_value': round(p_value, 4),
                'trend': trend_direction,
                'strength': trend_strength,
                'significant': significant
            }
        
        return {}
    
    
    # ============================================
    # 4. 정비 분석
    # ============================================
    
    def analyze_maintenance_history(self) -> pd.DataFrame:
        """정비 유형별 분석"""
        
        if self.maintenance is None or len(self.maintenance) == 0:
            logger.warning("정비 데이터 없음")
            return pd.DataFrame()
        
        maint_analysis = self.maintenance.groupby('maintenance_type').agg({
            'duration_hours': ['sum', 'mean', 'count'],
            'cost_won': 'sum'
        }).round(2)
        
        maint_analysis.columns = ['total_hours', 'avg_hours', 'frequency', 'cost']
        maint_analysis = maint_analysis.sort_values('frequency', ascending=False)
        
        # 비율 계산
        maint_analysis['cost_pct'] = (
            maint_analysis['cost'] / maint_analysis['cost'].sum() * 100
        ).round(2)
        
        self.results['maintenance_analysis'] = maint_analysis
        return maint_analysis
    
    
    def calculate_mtbf_mttr(self) -> Dict:
        """MTBF(평균고장간격), MTTR(평균수리시간) 계산"""
        
        if self.maintenance is None or len(self.maintenance) == 0:
            return {}
        
        failures = self.maintenance[self.maintenance['maintenance_type'] == 'CM']
        
        if len(failures) == 0:
            return {}
        
        # MTBF: 전체 기간 / 고장 횟수
        total_days = (self.maintenance['date'].max() - self.maintenance['date'].min()).days
        mtbf = total_days / len(failures) if len(failures) > 0 else 0
        
        # MTTR: 평균 수리 시간
        mttr = failures['duration_hours'].mean()
        
        # 가용성
        availability = (1 - (mttr / (24 * mtbf))) * 100 if mtbf > 0 else 0
        
        return {
            'mtbf_days': round(mtbf, 2),
            'mttr_hours': round(mttr, 2),
            'availability_percent': round(availability, 2),
            'failure_count': len(failures)
        }
    
    
    # ============================================
    # 5. 고장 전조 신호 분석
    # ============================================
    
    def identify_fault_precursors(self, days_before_failure: int = 7) -> Dict:
        """고장 전 센서 변화 패턴 분석"""
        
        if self.maintenance is None or len(self.maintenance) == 0:
            return {}
        
        failures = self.maintenance[self.maintenance['maintenance_type'] == 'CM']
        if len(failures) == 0:
            return {}
        
        precursor_patterns = {}
        
        for idx, failure in failures.iterrows():
            failure_date = failure['date']
            equipment_id = failure.get('equipment_id')
            
            # 고장 전 데이터
            if isinstance(failure_date, str):
                failure_date = pd.to_datetime(failure_date)
            
            mask = (self.sensor['timestamp'] >= failure_date - pd.Timedelta(days=days_before_failure)) & \
                   (self.sensor['timestamp'] <= failure_date)
            
            pre_failure_data = self.sensor[mask]
            
            if len(pre_failure_data) > 0:
                sensors = ['temperature_c', 'vibration_mms', 'current_a', 'pressure_bar']
                patterns = {}
                
                for sensor in sensors:
                    if sensor in pre_failure_data.columns:
                        data = pre_failure_data[sensor].dropna()
                        if len(data) > 1:
                            # 변화율
                            change_rate = ((data.iloc[-1] - data.iloc[0]) / data.iloc[0] * 100
                                         if data.iloc[0] != 0 else 0)
                            patterns[sensor] = change_rate
                
                if patterns:
                    precursor_patterns[f"{equipment_id}_{failure_date.date()}"] = patterns
        
        self.results['precursors'] = precursor_patterns
        return precursor_patterns
    
    
    # ============================================
    # 6. 설비 건강도 스코어
    # ============================================
    
    def calculate_equipment_health_score(self, equipment_id: str = None) -> Dict:
        """설비 건강도 스코어 (0-100)"""
        
        equipment_sensor = self.sensor.copy()
        if equipment_id and 'equipment_id' in equipment_sensor.columns:
            equipment_sensor = equipment_sensor[equipment_sensor['equipment_id'] == equipment_id]
        
        score = 100
        issues = []
        
        sensor_cols = {
            'temperature_c': SENSOR_THRESHOLDS.get('temperature', {}),
            'vibration_mms': SENSOR_THRESHOLDS.get('vibration', {}),
            'current_a': SENSOR_THRESHOLDS.get('current', {}),
            'pressure_bar': SENSOR_THRESHOLDS.get('pressure', {})
        }
        
        for col, thresholds in sensor_cols.items():
            if col not in equipment_sensor.columns:
                continue
            
            data = equipment_sensor[col].dropna()
            if len(data) == 0:
                continue
            
            current_val = data.iloc[-1]
            
            # 임계값 기반 점수 감소
            if 'critical' in thresholds and current_val > thresholds['critical']:
                score -= 30
                issues.append(f"{col}: 긴급 (임계값 {thresholds['critical']} 초과)")
            elif 'warning' in thresholds and current_val > thresholds['warning']:
                score -= 15
                issues.append(f"{col}: 경고 (경고치 {thresholds['warning']} 초과)")
            
            # 이상탐지
            if self.detect_anomalies_zscore(col).sum() > len(data) * 0.1:
                score -= 10
                issues.append(f"{col}: 이상치 탐지됨")
        
        score = max(0, min(100, score))
        
        health_level = "정상" if score >= 80 else "주의" if score >= 50 else "위험"
        
        return {
            'health_score': round(score, 1),
            'health_level': health_level,
            'issues': issues
        }
    
    
    # ============================================
    # 7. 종합 분석 실행
    # ============================================
    
    def run_full_analysis(self) -> Dict:
        """전체 분석 실행"""
        
        print_section("설비관리 및 예지보전 분석", 1)
        
        # 1. 센서 통계
        print("\n[1] 센서 데이터 통계")
        stats = self.analyze_sensor_statistics()
        for sensor, stat in stats.items():
            print(f"  {sensor}:")
            print(f"    평균: {stat['mean']:.2f}, 표준편차: {stat['std']:.2f}")
            print(f"    범위: {stat['min']:.2f} ~ {stat['max']:.2f}")
        
        # 2. 이상탐지
        print("\n[2] 이상치 탐지")
        anomalies = self.detect_all_anomalies()
        for sensor, count in anomalies.items():
            if count > 0:
                print(f"  {sensor}: {count}건")
        
        # 3. 트렌드 분석
        print("\n[3] 열화 추세 분석")
        for col in ['temperature_c', 'vibration_mms']:
            if col in self.sensor.columns:
                trend = self.detect_degradation_trend(col)
                if trend:
                    print(f"  {col}: {trend['trend']} (기울기: {trend['slope']:.6f}, p=0.{int(trend['p_value']*10000):04d})")
        
        # 4. 정비 분석
        if self.maintenance is not None:
            print("\n[4] 정비 분석")
            maint = self.analyze_maintenance_history()
            print(maint.to_string())
            
            # MTBF/MTTR
            print("\n[5] 신뢰성 지표")
            reliability = self.calculate_mtbf_mttr()
            for key, val in reliability.items():
                print(f"  {key}: {val}")
        
        # 5. 설비 건강도
        print("\n[6] 설비 건강도")
        health = self.calculate_equipment_health_score()
        print(f"  건강도 점수: {health['health_score']}/100 ({health['health_level']})")
        if health['issues']:
            print("  문제점:")
            for issue in health['issues']:
                print(f"    - {issue}")
        
        logger.info("✓ 설비 분석 완료")
        return self.results


if __name__ == "__main__":
    print("설비 분석 모듈 준비 완료")
