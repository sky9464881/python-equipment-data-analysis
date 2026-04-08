"""
통합 팩토리 분석 프로젝트 - 설정 파일

한국정밀산업(주)의 OEE, 품질, 설비, 에너지를 종합 분석하는 프로젝트
"""

import os
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib
from matplotlib import rcParams
import matplotlib.font_manager as fm

# ============================================
# Matplotlib 한글 폰트 설정 (확정 버전)
# ============================================

# Malgun Gothic 등록 (유일한 폰트)
malgun_path = 'C:\\Windows\\Fonts\\malgun.ttf'
if os.path.exists(malgun_path):
    try:
        fm.fontManager.addfont(malgun_path)
    except Exception as e:
        print(f"Malgun Gothic 등록 실패: {e}")
else:
    print(f"경고: Malgun Gothic을 찾을 수 없습니다: {malgun_path}")

# rcParams 설정 (모든 텍스트에 적용됨)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['font.sans-serif'] = ['Malgun Gothic']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['figure.dpi'] = 100

# ============================================
# 프로젝트 경로
# ============================================

PROJECT_ROOT = Path(__file__).parent.parent
DATA_RAW_DIR = PROJECT_ROOT / 'data' / 'raw'
DATA_PROCESSED_DIR = PROJECT_ROOT / 'data' / 'processed'
NOTEBOOKS_DIR = PROJECT_ROOT / 'notebooks'
RESULTS_DIR = PROJECT_ROOT / 'results'
CHARTS_DIR = RESULTS_DIR / 'charts'
REPORTS_DIR = RESULTS_DIR / 'reports'
RESULTS_DATA_DIR = RESULTS_DIR / 'data'
DOCS_DIR = PROJECT_ROOT / 'docs'

# 모든 결과 디렉토리 자동 생성
for dir_path in [DATA_RAW_DIR, DATA_PROCESSED_DIR, NOTEBOOKS_DIR, 
                CHARTS_DIR, REPORTS_DIR, RESULTS_DATA_DIR, DOCS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# ============================================
# 데이터 파일 정의 (4개 프로젝트)
# ============================================

DATA_FILES = {
    # Project 1: OEE 분석
    'equipment': DATA_RAW_DIR / 'project1' / 'p1_equipment.csv',
    'product': DATA_RAW_DIR / 'project1' / 'p1_product.csv',
    'production': DATA_RAW_DIR / 'project1' / 'p1_production_log.csv',
    'downtime': DATA_RAW_DIR / 'project1' / 'p1_downtime_log.csv',
    
    # Project 2: 품질관리
    'product_spec': DATA_RAW_DIR / 'project2' / 'p2_product_spec.csv',
    'inspection': DATA_RAW_DIR / 'project2' / 'p2_inspection_log.csv',
    'defect': DATA_RAW_DIR / 'project2' / 'p2_defect_log.csv',
    'process_params': DATA_RAW_DIR / 'project2' / 'p2_process_params.csv',
    
    # Project 3: 예지보전
    'equipment_pm': DATA_RAW_DIR / 'project3' / 'p3_equipment.csv',
    'sensor': DATA_RAW_DIR / 'project3' / 'p3_sensor_log.csv',
    'maintenance': DATA_RAW_DIR / 'project3' / 'p3_maintenance_log.csv',
    'alarm': DATA_RAW_DIR / 'project3' / 'p3_alarm_log.csv',
    
    # Project 4: 에너지관리
    'equipment_energy': DATA_RAW_DIR / 'project4' / 'p4_equipment.csv',
    'energy': DATA_RAW_DIR / 'project4' / 'p4_energy_log.csv',
    'production_energy': DATA_RAW_DIR / 'project4' / 'p4_production_log.csv',
    'tariff': DATA_RAW_DIR / 'project4' / 'p4_tariff.csv',
}

# ============================================
# 기본 설정
# ============================================

ENCODING = 'utf-8-sig'
FONT_NAME = 'Malgun Gothic'
THEME = 'whitegrid'

# 분석 기간
ANALYSIS_START_DATE = '2024-01-01'
ANALYSIS_END_DATE = '2024-06-30'
IMPROVEMENT_DATE = '2024-03-01'  # OEE 개선 시작일

# ============================================
# OEE 설정
# ============================================

OEE_TARGETS = {
    'overall': 85.0,      # %
    'availability': 90.0,
    'performance': 95.0,
    'quality': 99.0
}

DOWNTIME_TYPES = {
    'planned': '계획된 정지',
    'breakdown': '고장',
    'setup': '셋업',
    'minor_stop': '단순 정지',
    'other': '기타'
}

# ============================================
# 품질관리 설정
# ============================================

QUALITY_TARGETS = {
    'cpk': 1.33,           # 공정능력 목표
    'defect_rate': 1.0,    # % (1%)
    'inspection_pass_rate': 99.0  # %
}

SEVERITY_LEVELS = {
    'Low': 1,
    'Medium': 2,
    'High': 3,
    'Critical': 4
}

# ============================================
# 설비관리 설정
# ============================================

MAINTENANCE_TYPES = {
    'PM': '예방정비',
    'CM': '고장수리',
    'BM': '사후보전',
    'INS': '점검'
}

ALARM_SEVERITY = {
    '경고': 1,
    '위험': 2,
    '긴급': 3
}

SENSOR_THRESHOLDS = {
    'temperature': {'warning': 80, 'critical': 90},      # °C
    'vibration': {'warning': 7.1, 'critical': 11.0},    # mm/s
    'current': {'warning': 90, 'critical': 110},        # % of rated
    'pressure': {'warning': 90, 'critical': 110}        # % of max
}

# ============================================
# 에너지 설정
# ============================================

ENERGY_TARGETS = {
    'unit_cost_kwh': 110,  # 원/kWh 평균
    'peak_load': 80,       # % - 피크 로드 최대 비율
    'standby_loss': 5      # % - 대기전력 손실 한계
}

TARIFF_ZONES = {
    'off_peak': {'label': '경부하', 'hours': [23, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9]},
    'mid_peak': {'label': '중간부하', 'hours': [9, 10, 12, 13, 17, 18, 19, 20, 21, 22, 23]},
    'peak': {'label': '최대부하', 'hours': [10, 11, 13, 14, 15, 16, 17]}
}

# ============================================
# 시각화 설정
# ============================================

COLORS = {
    # 라인
    'line_a': '#1f77b4',
    'line_b': '#ff7f0e',
    'line_c': '#2ca02c',
    
    # 상태
    'good': '#2ca02c',
    'warning': '#ff9800',
    'bad': '#d62728',
    'neutral': '#9467bd',
    
    # 기본
    'primary': '#1f77b4',
    'secondary': '#ff7f0e',
}

PLOT_CONFIG = {
    'figsize': (14, 8),
    'dpi': 300,
    'alpha': 0.8,
    'edge_color': 'black',
    'line_width': 1.5
}

# ============================================
# 통계 설정
# ============================================

ALPHA_SIGNIFICANCE = 0.05  # 5% 유의수준
Z_SCORE_THRESHOLD = 3      # 이상치 임계값 (3-sigma)
IQR_MULTIPLIER = 1.5       # IQR 방식 이상치
CONFIDENCE_LEVEL = 0.95    # 95% 신뢰도

# ============================================
# 리포팅 설정
# ============================================

REPORT_FORMATS = {
    'summary': '요약보고서',
    'detailed': '상세보고서',
    'dashboard': '대시보드'
}

REPORT_SECTIONS = [
    'executive_summary',
    'oee_analysis',
    'quality_analysis',
    'maintenance_analysis',
    'energy_analysis',
    'integrated_insights',
    'recommendations'
]

# ============================================
# 프로젝트 메타데이터
# ============================================

PROJECT_INFO = {
    'company': '한국정밀산업(주)',
    'department': '스마트팩토리팀',
    'lines': ['A', 'B', 'C'],
    'equipment_count': 12,
    'products': 6,
    'fiscal_year': 2024,
    'currency': 'KRW'
}

# ============================================
# 로깅 설정
# ============================================

LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
