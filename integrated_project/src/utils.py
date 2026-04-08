"""
통합 분석 프로젝트 - 공통 유틸리티

모든 분석 모듈에서 사용하는 공통 함수들
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
from pathlib import Path
from typing import Dict, List, Tuple, Union
from datetime import datetime
import logging

from config import *

warnings.filterwarnings('ignore')

# ============================================
# 로깅 설정
# ============================================

def setup_logger(name: str) -> logging.Logger:
    """로거 설정"""
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)
    
    formatter = logging.Formatter(LOG_FORMAT)
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger

logger = setup_logger(__name__)

# ============================================
# 환경 초기화
# ============================================

def setup_environment():
    """분석 환경 초기화"""
    try:
        # 한글 폰트 설정
        plt.rcParams['font.family'] = FONT_NAME
        plt.rcParams['axes.unicode_minus'] = False
        
        # Seaborn 스타일
        sns.set_style(THEME)
        sns.set_palette("husl")
        
        # 디렉토리 생성
        for dir_path in [DATA_RAW_DIR, DATA_PROCESSED_DIR, CHARTS_DIR, 
                        REPORTS_DIR, RESULTS_DATA_DIR]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        logger.info("✓ 분석 환경 초기화 완료")
        return True
    
    except Exception as e:
        logger.error(f"✗ 환경 초기화 실패: {e}")
        raise


# ============================================
# 데이터 로드 및 검증
# ============================================

def load_all_data() -> Dict[str, pd.DataFrame]:
    """모든 데이터 로드"""
    data = {}
    missing_files = []
    
    logger.info("\n데이터 로딩 시작...")
    print("=" * 60)
    print("데이터 로딩 중...")
    print("=" * 60)
    
    for key, path in DATA_FILES.items():
        try:
            if not path.exists():
                missing_files.append(str(path))
                logger.warning(f"  × {key}: 파일 없음")
                continue
            
            df = pd.read_csv(path, encoding=ENCODING)
            data[key] = df
            print(f"  ✓ {key:20s} | {len(df):,} rows × {len(df.columns)} cols")
        
        except Exception as e:
            logger.error(f"  × {key}: {e}")
            missing_files.append(key)
    
    if missing_files:
        logger.warning(f"\n⚠ 로드 실패: {len(missing_files)}개 파일")
        print(f"\n⚠ 로드 실패: {missing_files}")
    
    logger.info(f"✓ {len(data)}개 데이터 로드 완료")
    print(f"\n✓ 총 {len(data)}개 데이터 로드 완료\n")
    
    return data


def validate_data(data: Dict[str, pd.DataFrame]) -> Dict[str, Dict]:
    """데이터 품질 검사"""
    print("\n" + "=" * 60)
    print("데이터 품질 검사")
    print("=" * 60)
    
    validation_results = {}
    
    for key, df in data.items():
        result = {
            'total_rows': len(df),
            'total_cols': len(df.columns),
            'missing_count': df.isna().sum().sum(),
            'missing_rate': (df.isna().sum().sum() / (len(df) * len(df.columns)) * 100),
            'dtypes': df.dtypes.value_counts().to_dict(),
            'duplicates': df.duplicated().sum()
        }
        validation_results[key] = result
        
        print(f"\n[{key}]")
        print(f"  크기: {result['total_rows']:,} × {result['total_cols']}")
        print(f"  결측치: {result['missing_count']}/{result['total_rows']*result['total_cols']} ({result['missing_rate']:.2f}%)")
        print(f"  중복: {result['duplicates']}")
    
    logger.info("✓ 데이터 검증 완료")
    return validation_results


def preprocess_datetime_columns(data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """날짜 컬럼 자동 변환"""
    date_columns = {
        'production': 'production_date',
        'inspection': 'inspection_date',
        'defect': 'defect_date',
        'sensor': 'timestamp',
        'maintenance': 'date',
        'alarm': 'timestamp',
        'energy': 'timestamp',
        'production_energy': 'date'
    }
    
    for key, col in date_columns.items():
        if key in data and col in data[key].columns:
            try:
                data[key][col] = pd.to_datetime(data[key][col])
            except:
                logger.warning(f"{key}.{col} 변환 실패")
    
    return data


# ============================================
# 데이터 정제
# ============================================

def handle_missing_values(df: pd.DataFrame, strategy: str = 'forward_fill') -> pd.DataFrame:
    """결측치 처리"""
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    if strategy == 'forward_fill':
        df[numeric_cols] = df[numeric_cols].fillna(method='ffill')
        df[numeric_cols] = df[numeric_cols].fillna(method='bfill')
    elif strategy == 'median':
        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())
    elif strategy == 'mean':
        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
    
    return df


def remove_outliers(df: pd.DataFrame, columns: List[str], 
                   method: str = 'iqr', threshold: float = 3.0) -> pd.DataFrame:
    """이상치 제거"""
    df_clean = df.copy()
    
    for col in columns:
        if col not in df_clean.columns:
            continue
        
        if method == 'iqr':
            Q1 = df_clean[col].quantile(0.25)
            Q3 = df_clean[col].quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - IQR_MULTIPLIER * IQR
            upper = Q3 + IQR_MULTIPLIER * IQR
            df_clean = df_clean[(df_clean[col] >= lower) & (df_clean[col] <= upper)]
        
        elif method == 'zscore':
            z_scores = np.abs((df_clean[col] - df_clean[col].mean()) / df_clean[col].std())
            df_clean = df_clean[z_scores < threshold]
    
    return df_clean


# ============================================
# 파생변수 생성
# ============================================

def create_time_features(df: pd.DataFrame, date_col: str) -> pd.DataFrame:
    """시간 관련 파생변수 생성"""
    if date_col not in df.columns:
        return df
    
    df[date_col] = pd.to_datetime(df[date_col])
    df['year'] = df[date_col].dt.year
    df['month'] = df[date_col].dt.month
    df['week'] = df[date_col].dt.isocalendar().week
    df['day'] = df[date_col].dt.day
    df['dayofweek'] = df[date_col].dt.dayofweek
    df['hour'] = df[date_col].dt.hour if hasattr(df[date_col].dt, 'hour') else None
    df['is_weekend'] = df['dayofweek'].isin([5, 6]).astype(int)
    
    return df


def create_rate_features(df: pd.DataFrame, numerator: str, 
                        denominator: str, new_col: str) -> pd.DataFrame:
    """비율 파생변수 생성"""
    df[new_col] = np.where(
        df[denominator] != 0,
        df[numerator] / df[denominator],
        0
    )
    return df


# ============================================
# 통계 분석
# ============================================

def calculate_summary_stats(series: pd.Series) -> Dict:
    """요약 통계"""
    return {
        'mean': series.mean(),
        'median': series.median(),
        'std': series.std(),
        'min': series.min(),
        'max': series.max(),
        'q25': series.quantile(0.25),
        'q75': series.quantile(0.75),
        'iqr': series.quantile(0.75) - series.quantile(0.25),
        'skew': series.skew(),
        'kurtosis': series.kurtosis()
    }


def compare_before_after(pre_data: pd.DataFrame, post_data: pd.DataFrame,
                        column: str) -> Dict:
    """전/후 비교 분석"""
    from scipy import stats
    
    pre_values = pre_data[column].dropna()
    post_values = post_data[column].dropna()
    
    t_stat, p_value = stats.ttest_ind(post_values, pre_values, equal_var=False)
    
    return {
        'pre_mean': pre_values.mean(),
        'post_mean': post_values.mean(),
        'difference': post_values.mean() - pre_values.mean(),
        'pct_change': ((post_values.mean() - pre_values.mean()) / pre_values.mean() * 100),
        't_statistic': t_stat,
        'p_value': p_value,
        'significant': 'Yes' if p_value < ALPHA_SIGNIFICANCE else 'No'
    }


# ============================================
# 데이터 저장
# ============================================

def save_figure(fig, name: str, formats: List[str] = ['png']) -> None:
    """그래프 저장"""
    for fmt in formats:
        path = CHARTS_DIR / f"{name}.{fmt}"
        try:
            fig.savefig(path, format=fmt, dpi=PLOT_CONFIG['dpi'], bbox_inches='tight')
            logger.info(f"  → 저장: {path.name}")
        except Exception as e:
            logger.error(f"  × {name}: {e}")


def save_dataframe(df: pd.DataFrame, name: str, fmt: str = 'csv') -> None:
    """데이터프레임 저장"""
    if fmt == 'csv':
        path = RESULTS_DATA_DIR / f"{name}.csv"
        df.to_csv(path, index=False, encoding=ENCODING)
    elif fmt == 'excel':
        path = RESULTS_DATA_DIR / f"{name}.xlsx"
        df.to_excel(path, index=False, engine='openpyxl')
    elif fmt == 'parquet':
        path = RESULTS_DATA_DIR / f"{name}.parquet"
        df.to_parquet(path, index=False)
    
    logger.info(f"  → 저장: {path.name}")


def save_report(content: str, name: str, fmt: str = 'md') -> None:
    """리포트 저장"""
    if fmt == 'md':
        path = REPORTS_DIR / f"{name}.md"
    elif fmt == 'txt':
        path = REPORTS_DIR / f"{name}.txt"
    elif fmt == 'html':
        path = REPORTS_DIR / f"{name}.html"
    
    with open(path, 'w', encoding=ENCODING) as f:
        f.write(content)
    
    logger.info(f"  → 저장: {path.name}")


# ============================================
# 형식화 함수
# ============================================

def format_large_number(num: Union[int, float], decimals: int = 1) -> str:
    """큰 숫자 포맷팅"""
    if abs(num) >= 1_000_000:
        return f"{num/1_000_000:.{decimals}f}M"
    elif abs(num) >= 1_000:
        return f"{num/1_000:.{decimals}f}K"
    else:
        return f"{num:.{decimals}f}"


def format_percentage(num: float, decimals: int = 1) -> str:
    """백분율 포맷팅"""
    return f"{num:.{decimals}f}%"


def format_currency(num: float, currency: str = '₩') -> str:
    """통화 포맷팅"""
    return f"{currency}{num:,.0f}"


# ============================================
# 프린팅 유틸
# ============================================

def print_section(title: str, level: int = 1) -> None:
    """섹션 제목 출력"""
    if level == 1:
        print("\n" + "█" * 60)
        print(f"█  {title}".ljust(59) + "█")
        print("█" * 60 + "\n")
    elif level == 2:
        print("\n" + "=" * 50)
        print(f"▶ {title}")
        print("=" * 50 + "\n")
    elif level == 3:
        print(f"\n▪ {title}")


def print_stats_table(stats_dict: Dict, title: str = "통계") -> None:
    """통계표 출력"""
    print(f"\n[{title}]")
    for key, val in stats_dict.items():
        if isinstance(val, float):
            print(f"  {key:20s}: {val:10.2f}")
        else:
            print(f"  {key:20s}: {val}")


# ============================================
# 통합 함수
# ============================================

def initialize_project() -> Dict[str, pd.DataFrame]:
    """프로젝트 초기화 및 데이터 로드"""
    
    print_section("통합 팩토리 분석 프로젝트", 1)
    
    # 1. 환경 설정
    setup_environment()
    
    # 2. 데이터 로드
    data = load_all_data()
    
    # 3. 데이터 검증
    validate_data(data)
    
    # 4. 날짜 전처리
    data = preprocess_datetime_columns(data)
    
    logger.info("\n✓ 프로젝트 초기화 완료")
    
    return data


if __name__ == "__main__":
    # 테스트
    setup_environment()
    print("✓ 유틸리티 모듈이 준비되었습니다.")
