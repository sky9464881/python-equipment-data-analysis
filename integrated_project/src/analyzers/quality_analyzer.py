"""
품질관리 분석 모듈

SPC, 공정능력, 불량 분석
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, Tuple
import warnings

from config import QUALITY_TARGETS, ALPHA_SIGNIFICANCE
from utils import logger, print_section

warnings.filterwarnings('ignore')


class QualityAnalyzer:
    """품질 분석 클래스"""
    
    def __init__(self, inspection_data: pd.DataFrame, defect_data: pd.DataFrame = None,
                spec_data: pd.DataFrame = None):
        """
        Parameters:
        -----------
        inspection_data : DataFrame
            검사 기록
        defect_data : DataFrame
            불량 기록
        spec_data : DataFrame
            제품 규격
        """
        self.inspection = inspection_data.copy()
        self.defect = defect_data.copy() if defect_data is not None else None
        self.spec = spec_data.copy() if spec_data is not None else None
        self.results = {}
    
    # ============================================
    # 1. 기본 품질 지표
    # ============================================
    
    def calculate_basic_metrics(self) -> Dict:
        """기본 품질 지표"""
        
        total = len(self.inspection)
        pass_count = (self.inspection['result'] == 'PASS').sum()
        fail_count = total - pass_count
        pass_rate = (pass_count / total * 100) if total > 0 else 0
        
        metrics = {
            'total_inspections': total,
            'pass_count': pass_count,
            'fail_count': fail_count,
            'pass_rate': round(pass_rate, 2),
            'fail_rate': round(100 - pass_rate, 2)
        }
        
        self.results['basic_metrics'] = metrics
        return metrics
    
    
    # ============================================
    # 2. 불량 분석
    # ============================================
    
    def analyze_defects(self) -> pd.DataFrame:
        """불량 유형별 분석"""
        
        if self.defect is None or len(self.defect) == 0:
            logger.warning("불량 데이터 없음")
            return pd.DataFrame()
        
        defect_analysis = self.defect.groupby('defect_type').agg({
            'defect_qty': ['sum', 'mean', 'count']
        }).round(2)
        
        defect_analysis.columns = ['total_qty', 'avg_qty', 'frequency']
        defect_analysis['percentage'] = (
            defect_analysis['total_qty'] / defect_analysis['total_qty'].sum() * 100
        ).round(2)
        defect_analysis = defect_analysis.sort_values('total_qty', ascending=False)
        
        # 파레토 분석 (80/20)
        cumulative = defect_analysis['percentage'].cumsum()
        defect_analysis['cumulative_pct'] = cumulative
        defect_analysis['is_80_pct'] = (cumulative <= 80).astype(int)
        
        self.results['defect_analysis'] = defect_analysis
        return defect_analysis
    
    
    # ============================================
    # 3. SPC (Statistical Process Control)
    # ============================================
    
    def calculate_control_limits(self, data: pd.Series, window: int = 5
                                ) -> Dict[str, np.ndarray]:
        """관리도 한계 계산"""
        
        # 이동 범위 (Moving Range)
        mr = data.diff().abs().dropna()
        mR_bar = mr.mean()
        
        # 상수 (X-R 관리도)
        d2 = 1.128
        sigma = mR_bar / d2
        
        # 중심선 및 한계
        center_line = data.mean()
        ucl = center_line + 3 * sigma
        lcl = center_line - 3 * sigma
        
        return {
            'center_line': center_line,
            'ucl': ucl,
            'lcl': lcl,
            'sigma': sigma
        }
    
    
    def detect_control_violations(self, data: pd.Series, 
                                 window: int = 5) -> Dict:
        """관리도 이상 탐지"""
        
        limits = self.calculate_control_limits(data, window)
        
        violations = {
            'out_of_control': [],
            'trend': [],
            'shift': []
        }
        
        # 1. 한계 초과
        out_of_control = (data > limits['ucl']) | (data < limits['lcl'])
        violations['out_of_control'] = out_of_control.sum()
        
        # 2. 추세 (6개 연속 증가/감소)
        direction = np.sign(data.diff())
        for i in range(len(direction) - 5):
            if direction.iloc[i:i+6].sum() == 6 or direction.iloc[i:i+6].sum() == -6:
                violations['trend'].append(i)
        
        # 3. 시프트 (8개 연속 중심선 한쪽)
        above_center = (data > limits['center_line']).astype(int)
        for i in range(len(above_center) - 7):
            if above_center.iloc[i:i+8].sum() in [0, 8]:
                violations['shift'].append(i)
        
        violations['trend'] = len(violations['trend'])
        violations['shift'] = len(violations['shift'])
        
        return violations
    
    
    # ============================================
    # 4. 공정능력 분석
    # ============================================
    
    def calculate_process_capability(self, data: pd.Series, lsl: float, usl: float
                                    ) -> Dict:
        """공정능력 지수 계산"""
        
        mean = data.mean()
        std = data.std()
        
        # Cp: 공정능력 (중심화 무시)
        cp = ((usl - lsl) / (6 * std)) if std > 0 else 0
        
        # Cpk: 치우침 공정능력 (중심화 고려)
        cpu = ((usl - mean) / (3 * std)) if std > 0 else 0  # 상한
        cpl = ((mean - lsl) / (3 * std)) if std > 0 else 0  # 하한
        cpk = min(cpu, cpl)
        
        # 규격 만족도
        in_spec = ((data >= lsl) & (data <= usl)).sum()
        spec_rate = (in_spec / len(data) * 100) if len(data) > 0 else 0
        
        # 기대 불량률
        if std > 0:
            z_upper = (usl - mean) / std
            z_lower = (mean - lsl) / std
            defect_ppm = (
                (1 - stats.norm.cdf(z_upper)) + stats.norm.cdf(-z_lower)
            ) * 1_000_000
        else:
            defect_ppm = 0
        
        return {
            'cp': round(cp, 4),
            'cpk': round(cpk, 4),
            'cpu': round(cpu, 4),
            'cpl': round(cpl, 4),
            'mean': round(mean, 4),
            'std': round(std, 4),
            'spec_lsl': lsl,
            'spec_usl': usl,
            'in_spec_rate': round(spec_rate, 2),
            'expected_defect_ppm': round(defect_ppm, 0)
        }
    
    
    # ============================================
    # 5. 시간대별 품질 추이
    # ============================================
    
    def analyze_quality_trend(self, date_col: str = 'inspection_date'
                             ) -> pd.DataFrame:
        """시간대별 품질 추이"""
        
        if date_col not in self.inspection.columns:
            logger.warning(f"{date_col} 컬럼 없음")
            return pd.DataFrame()
        
        self.inspection[date_col] = pd.to_datetime(self.inspection[date_col])
        
        daily_quality = self.inspection.groupby(
            self.inspection[date_col].dt.date
        ).agg({
            'result': lambda x: (x == 'PASS').sum() / len(x) * 100
        }).reset_index()
        
        daily_quality.columns = ['date', 'pass_rate']
        daily_quality['date'] = pd.to_datetime(daily_quality['date'])
        daily_quality = daily_quality.sort_values('date')
        
        self.results['quality_trend'] = daily_quality
        return daily_quality
    
    
    # ============================================
    # 6. 종합 분석 실행
    # ============================================
    
    def run_full_analysis(self) -> Dict:
        """전체 분석 실행"""
        
        print_section("품질관리 분석", 1)
        
        # 1. 기본 지표
        print("\n[1] 기본 품질 지표")
        basic = self.calculate_basic_metrics()
        print(f"  검사 건수: {basic['total_inspections']:,}건")
        print(f"  합격: {basic['pass_count']:,}건 ({basic['pass_rate']:.2f}%)")
        print(f"  불합격: {basic['fail_count']:,}건 ({basic['fail_rate']:.2f}%)")
        
        # 2. 불량 분석
        if self.defect is not None:
            print("\n[2] 불량 유형별 분석 (파레토)")
            defects = self.analyze_defects()
            print(defects[['total_qty', 'percentage', 'cumulative_pct']].head(10).to_string())
        
        # 3. 공정능력
        if self.spec is not None and len(self.spec) > 0:
            print("\n[3] 공정능력 분석")
            for _, spec_row in self.spec.iterrows():
                product = spec_row.get('product_code', 'Unknown')
                lsl = spec_row.get('lsl')
                usl = spec_row.get('usl')
                
                if lsl is None or usl is None:
                    continue
                
                # 해당 제품 데이터
                product_data = self.inspection[
                    (self.inspection.get('product_code') == product) & 
                    (self.inspection.get('measurement').notna())
                ]['measurement']
                
                if len(product_data) > 10:
                    cpk_result = self.calculate_process_capability(product_data, lsl, usl)
                    print(f"\n  {product}:")
                    print(f"    Cpk: {cpk_result['cpk']:.4f} (목표: ≥1.33)")
                    print(f"     규격내율: {cpk_result['in_spec_rate']:.2f}%")
                    print(f"     예상불량: {cpk_result['expected_defect_ppm']:.0f} ppm")
        
        # 4. 품질 추이
        print("\n[4] 품질 추이")
        trend = self.analyze_quality_trend()
        if len(trend) > 0:
            print(f"  기간: {trend['date'].min().date()} ~ {trend['date'].max().date()}")
            print(f"  평균 합격률: {trend['pass_rate'].mean():.2f}%")
            print(f"  최고/최저: {trend['pass_rate'].max():.2f}% / {trend['pass_rate'].min():.2f}%")
        
        logger.info("✓ 품질분석 완료")
        return self.results


if __name__ == "__main__":
    print("품질 분석 모듈 준비 완료")
