# 통합 팩토리 분석 프로젝트

## 📋 프로젝트 개요

**한국정밀산업(주)** 스마트팩토리의 전체 운영을 종합적으로 분석하는 통합 데이터 분석 프로젝트입니다.

### 핵심 특징

✅ **4개 프로젝트 통합**
- Project 1: 종합설비효율(OEE) 분석
- Project 2: 품질관리 및 SPC 분석  
- Project 3: 예지보전(Predictive Maintenance) 분석
- Project 4: 에너지관리 및 효율 분석

✅ **전사적 인사이트**
- 각 분석 결과의 상관관계 분석
- 운영 효율성 종합 평가
- 의사결정 중심의 시각화

✅ **엔터프라이즈급 코드 구조**
- 재사용 가능한 모듈화 설계
- 공통 유틸리티 및 설정 중앙화
- 명확한 책임 분리

---

## 🏗️ 프로젝트 구조

```
integrated_project/
│
├── data/                          # 데이터 관리
│   ├── raw/                       # 원본 데이터 (4개 프로젝트)
│   │   ├── p1_*.csv              # Project 1: OEE
│   │   ├── p2_*.csv              # Project 2: 품질
│   │   ├── p3_*.csv              # Project 3: 설비
│   │   └── p4_*.csv              # Project 4: 에너지
│   └── processed/                 # 전처리된 데이터
│
├── src/                           # 소스 코드
│   ├── config.py                 # 전사적 설정 및 상수
│   ├── utils.py                  # 공통 유틸리티 함수
│   ├── data_loader.py            # 통합 데이터 로더
│   ├── main.py                   # 메인 실행 스크립트
│   │
│   ├── analyzers/                # 분석 모듈
│   │   ├── __init__.py
│   │   ├── oee_analyzer.py       # OEE 분석
│   │   ├── quality_analyzer.py   # 품질 분석
│   │   ├── maintenance_analyzer.py # 설비 분석
│   │   └── energy_analyzer.py    # 에너지 분석
│   │
│   ├── visualizers/              # 시각화 모듈
│   │   ├── __init__.py
│   │   ├── integrated_visualizer.py # 통합 시각화
│   │   ├── oee_visualizer.py     # OEE 차트
│   │   ├── quality_visualizer.py # 품질 차트
│   │   └── energy_visualizer.py  # 에너지 차트
│   │
│   └── reporters/                # 리포트 생성
│       ├── __init__.py
│       └── report_generator.py   # 리포트 생성기
│
├── results/                       # 분석 결과
│   ├── charts/                   # 시각화 이미지 (PNG)
│   │   ├── oee_gauge.png
│   │   ├── equipment_comparison.png
│   │   ├── integrated_dashboard.png
│   │   └── ...
│   ├── reports/                  # 분석 리포트 (MD, HTML)
│   │   ├── 00_integrated_insights.md
│   │   ├── 01_oee_report.md
│   │   └── ...
│   └── data/                     # 분석 결과 데이터 (CSV)
│       ├── 01_equipment_oee.csv
│       ├── 02_line_oee.csv
│       └── ...
│
├── notebooks/                     # Jupyter 노트북
│   ├── 01_oee_analysis.ipynb
│   ├── 02_quality_analysis.ipynb
│   ├── 03_maintenance_analysis.ipynb
│   ├── 04_energy_analysis.ipynb
│   └── 05_integrated_dashboard.ipynb
│
├── docs/                          # 문서
│   ├── README.md                 # 프로젝트 개요
│   ├── STRUCTURE.md              # 상세 구조 설명
│   ├── METHODOLOGY.md            # 분석 방법론
│   └── API_REFERENCE.md          # API 레퍼런스
│
├── requirements.txt              # Python 의존성
└── setup.py                      # 설치 스크립트
```

---

## 📊 통합 분석 범위

### Project 1: OEE 분석 (설비 효율)

**목표**
- 설비 종합 효율(Overall Equipment Effectiveness) 분석
- 라인/설비별 성과 벤치마킹
- 비가동 손실(Six Big Losses) 원인 규명
- 개선 활동 효과 검증

**주요 지표**
- OEE = 가동률 × 성능률 × 양품률
- 라인/설비별 OEE 순위
- 주간 OEE 추이
- 비가동 손실 분석

**데이터**
- p1_equipment.csv (설비 정보, 13건)
- p1_production_log.csv (생산 실적, ~3,100건)
- p1_downtime_log.csv (비가동 기록, ~430건)

### Project 2: 품질관리 분석

**목표**
- 불량 현황 파악 및 원인 규명
- SPC(Statistical Process Control) 관리도
- 공정능력 분석 (Cp, Cpk)
- 공정 파라미터와 품질의 상관관계

**주요 지표**
- 불량률 및 불량 유형별 구성
- 공정능력지수 (Cp, Cpk)
- 품질 관리도 (X-R, p-np)

**데이터**
- p2_product_spec.csv (규격 정보, 24건)
- p2_inspection_log.csv (측정 기록, ~42,000건)
- p2_defect_log.csv (불량 기록, ~770건)

### Project 3: 예지보전 분석

**목표**
- 설비 상태 모니터링 (온도, 진동, 전류, 압력)
- 이상치 탐지 (Anomaly Detection)
- 고장 전조 신호 포착
- 정비 필요성 예측

**주요 지표**
- 센서 데이터 이상 비율
- 알람 발생 빈도 및 심각도
- 정비 유형별 실적
- 예측 정확도

**데이터**
- p3_equipment.csv (설비 정보, 12건)
- p3_sensor_log.csv (시계열 센서 데이터, ~21,000건)
- p3_maintenance_log.csv (정비 기록, ~230건)
- p3_alarm_log.csv (알람 기록, ~130건)

### Project 4: 에너지관리 분석

**목표**
- 에너지 사용 패턴 분석
- 라인별 에너지 효율 (kWh/개)
- 대기전력 낭비 규모 산출
- 피크 부하 관리

**주요 지표**
- 총 전력 소비 및 원단위
- 시간대별, 요일별 사용 패턴
- 대기전력 및 손실 비율
- 에너지 절감 기회 (금액 기준)

**데이터**
- p4_equipment.csv (설비 에너지 프로파일, 12건)
- p4_energy_log.csv (시간별 전력 사용, ~52,000건)
- p4_production_log.csv (생산 실적, ~1,275건)
- p4_tariff.csv (요금표, TOU 기반)

---

## 🚀 실행 방법

### 1. 데이터 준비

```bash
# data/raw/ 폴더에 다음 파일 배치:
# Project 1
data/raw/p1_equipment.csv
data/raw/p1_product.csv
data/raw/p1_production_log.csv
data/raw/p1_downtime_log.csv

# Project 2
data/raw/p2_product_spec.csv
data/raw/p2_inspection_log.csv
data/raw/p2_defect_log.csv
data/raw/p2_process_params.csv

# Project 3
data/raw/p3_equipment.csv
data/raw/p3_sensor_log.csv
data/raw/p3_maintenance_log.csv
data/raw/p3_alarm_log.csv

# Project 4
data/raw/p4_equipment.csv
data/raw/p4_energy_log.csv
data/raw/p4_production_log.csv
data/raw/p4_tariff.csv
```

### 2. 환경 설정

```bash
# Python 3.8+ 필요

# 가상환경 생성
python -m venv venv

# 활성화
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

### 3. 분석 실행

```bash
# 메인 스크립트 실행
python src/main.py
```

### 4. 결과 확인

```
results/
├── charts/          # 모든 분석 차트 (PNG)
├── reports/         # 분석 리포트 (MD)
└── data/            # 결과 데이터 (CSV)
```

---

## ✅ 검증 방법 (프로젝트 설정 확인)

프로젝트가 제대로 설정되었는지 단계별로 확인하세요.

### **레벨 1: 기본 구조 검증 (1분)**

#### 1-1. 필수 폴더 확인
```bash
# 필수 폴더 존재 확인
ls -la data/raw/
ls -la src/
ls -la results/
```

**확인 항목**:
- ✓ `data/raw/` 폴더 존재
- ✓ `src/` 폴더 존재  
- ✓ `src/analyzers/` 폴더 존재
- ✓ `src/visualizers/` 폴더 존재

#### 1-2. 필수 파일 확인
```bash
# 소스 코드 파일 확인
ls src/config.py src/utils.py src/main.py src/data_loader.py
```

**확인 항목**:
- ✓ `/src/config.py` 존재
- ✓ `/src/utils.py` 존재
- ✓ `/src/main.py` 존재
- ✓ `/src/data_loader.py` 존재
- ✓ `/src/analyzers/oee_analyzer.py` 존재
- ✓ `/src/analyzers/quality_analyzer.py` 존재
- ✓ `/src/analyzers/maintenance_analyzer.py` 존재
- ✓ `/src/analyzers/energy_analyzer.py` 존재

### **레벨 2: 데이터 파일 검증 (2분)**

#### 2-1. 데이터 폴더 구조 확인
```bash
# Project 1 데이터파일
ls data/raw/p1_* 
# 예상 결과:
# p1_equipment.csv, p1_production_log.csv, p1_downtime_log.csv, p1_product.csv

# Project 2 데이터파일
ls data/raw/p2_*
# 예상 결과:
# p2_product_spec.csv, p2_inspection_log.csv, p2_defect_log.csv, p2_process_params.csv

# Project 3 데이터파일
ls data/raw/p3_*
# 예상 결과:
# p3_equipment.csv, p3_sensor_log.csv, p3_maintenance_log.csv, p3_alarm_log.csv

# Project 4 데이터파일
ls data/raw/p4_*
# 예상 결과:
# p4_equipment.csv, p4_energy_log.csv, p4_production_log.csv, p4_tariff.csv
```

#### 2-2. 데이터 파일 크기 확인
```bash
# 각 CSV 파일이 적절한 크기인지 확인 (최소 1KB 이상)
du -h data/raw/*.csv | grep -v "0M\|0K"
```

**예상 결과**:
```
50K p1_equipment.csv      ✓
200K p1_production_log.csv ✓
80K p1_downtime_log.csv    ✓
40K p2_product_spec.csv    ✓
300K p2_inspection_log.csv ✓
100K p2_defect_log.csv     ✓
60K p3_equipment.csv       ✓
500K p3_sensor_log.csv     ✓
150K p3_maintenance_log.csv ✓
80K p4_equipment.csv       ✓
600K p4_energy_log.csv     ✓
100K p4_production_log.csv ✓
```

### **레벨 3: Python 환경 검증 (2분)**

#### 3-1. Python 버전 확인
```bash
python --version
# 출력: Python 3.8.x 이상
```

#### 3-2. 패키지 설치 확인
```bash
pip list | grep "pandas\|numpy\|matplotlib\|scipy"
# 출력 예:
# pandas         1.3.0
# numpy          1.21.0
# matplotlib     3.4.2
# scipy          1.7.0
```

#### 3-3. 모듈 임포트 테스트
```bash
cd integrated_project

# 각 모듈 임포트 테스트
python -c "from src.config import PROJECT_ROOT; print('✓ config 로드 성공'); print(f'  ProjectRoot: {PROJECT_ROOT}')"

python -c "from src.utils import setup_logger, setup_environment; print('✓ utils 로드 성공')"

python -c "from src.data_loader import DataLoader; print('✓ DataLoader 로드 성공')"

python -c "from src.analyzers.oee_analyzer import OEEAnalyzer; print('✓ OEEAnalyzer 로드 성공')"

python -c "from src.analyzers.quality_analyzer import QualityAnalyzer; print('✓ QualityAnalyzer 로드 성공')"

python -c "from src.analyzers.maintenance_analyzer import MaintenanceAnalyzer; print('✓ MaintenanceAnalyzer 로드 성공')"

python -c "from src.analyzers.energy_analyzer import EnergyAnalyzer; print('✓ EnergyAnalyzer 로드 성공')"
```

**예상 결과**:
```
✓ config 로드 성공
  ProjectRoot: c:\...\integrated_project

✓ utils 로드 성공
✓ DataLoader 로드 성공
✓ OEEAnalyzer 로드 성공
✓ QualityAnalyzer 로드 성공
✓ MaintenanceAnalyzer 로드 성공
✓ EnergyAnalyzer 로드 성공
```

### **레벨 4: 데이터 로드 검증 (3분)**

#### 4-1. 데이터 로드 테스트
```python
# test_data_load.py 생성
from src.data_loader import DataLoader

# 데이터 로드
print("데이터 로딩 중...")
loader = DataLoader()
data = loader.load_all()

# 로드된 데이터 확인
print(f"\n총 {len(data)}개 파일 로드됨:\n")
for key, df in data.items():
    print(f"  {key:30s} → {df.shape[0]:6d} 행, {df.shape[1]:3d} 열")

# 검증: 최소 10개 파일 이상 로드되어야 함
if len(data) >= 10:
    print("\n✓ 데이터 로드 성공")
else:
    print("\n✗ 데이터 로드 실패 (10개 이상 필요)")
```

**실행**:
```bash
python test_data_load.py
```

**예상 결과**:
```
데이터 로딩 중...

총 12개 파일 로드됨:

  p1_equipment                     →     20 행,  5 열
  p1_product                       →     50 행,  4 열
  p1_production_log                →   3100 행,  8 열
  p1_downtime_log                  →    430 행,  6 열
  p2_product_spec                  →    100 행,  6 열
  p2_inspection_log                →  42000 행,  8 열
  p2_defect_log                    →    770 행,  7 열
  p2_process_params                →   5000 행,  5 열
  p3_equipment                     →     12 행,  5 열
  p3_sensor_log                    →  21000 행, 10 열
  p3_maintenance_log               →    230 행,  6 열
  p3_alarm_log                     →    130 행,  5 열
  p4_equipment                     →     25 행,  6 열
  p4_energy_log                    →  52000 행,  8 열
  p4_production_log                →   1275 행,  5 열

✓ 데이터 로드 성공
```

### **레벨 5: 분석 실행 검증 (10분)**

#### 5-1. 전체 분석 실행
```bash
cd integrated_project
python src/main.py
```

**실행 중 예상 로그**:
```
2024-XX-XX 10:00:00,123 INFO     utils.py line 45  ✓ 환경 설정 완료
2024-XX-XX 10:00:01,234 INFO     main.py line 100 ================================================================================
2024-XX-XX 10:00:01,234 INFO     main.py line 100                          OEE 분석 및 성능 개선 분석
2024-XX-XX 10:00:05,567 INFO     main.py line 200 [1] OEE 계산 (3-factor 방법)
2024-XX-XX 10:00:05,890 INFO     main.py line 201   전체 OEE: 75.43%
2024-XX-XX 10:00:06,123 INFO     main.py line 202   - 가용성 (A): 88.50%
2024-XX-XX 10:00:06,456 INFO     main.py line 203   - 성능 (P): 92.30%
2024-XX-XX 10:00:06,789 INFO     main.py line 204   - 품질 (Q): 92.80%
....
2024-XX-XX 10:01:30,123 INFO     main.py line 500 ================================================================================
2024-XX-XX 10:01:30,456 INFO     main.py line 501                          통합 분석 완료
2024-XX-XX 10:01:30,789 INFO     main.py line 502 ================================================================================
2024-XX-XX 10:01:31,012 INFO     main.py line 600 ✓ 모든 분석 완료
```

**실행 시간**: 약 1-2분

#### 5-2. 결과 폴더 확인
```bash
# 생성된 결과 파일 확인
ls -la results/

# 네이버류 신 결과만 보기
find results/ -type f -name "*.png" -o -name "*.csv" -o -name "*.md" | head -20
```

**예상 결과**:
```
results/
├── oee_analysis_report.txt           ✓
├── quality_analysis_report.txt       ✓
├── maintenance_analysis_report.txt   ✓
├── energy_analysis_report.txt        ✓
├── charts/
│   ├── oee_gauge.png              ✓ (300dpi 이미지)
│   ├── equipment_comparison.png    ✓
│   ├── quality_trend.png           ✓
│   ├── integrated_dashboard.png    ✓
│   └── ...
├── data/
│   ├── equipment_oee.csv           ✓
│   ├── line_oee.csv                ✓
│   └── ...
└── integration_summary.md             ✓
```

#### 5-3. 결과 파일 크기 확인
```bash
# 보고서 파일 크기 (최소 10KB 이상이어야 정상)
du -h results/*.txt results/*.md

# PNG 이미지 파일 크기 (최소 50KB 이상이어야 정상)
du -h results/charts/*.png
```

**예상 결과**:
```
100K results/oee_analysis_report.txt           ✓
80K  results/quality_analysis_report.txt       ✓
60K  results/maintenance_analysis_report.txt   ✓
70K  results/energy_analysis_report.txt        ✓
120K results/integration_summary.md             ✓

200K results/charts/oee_gauge.png              ✓
150K results/charts/equipment_comparison.png   ✓
180K results/charts/quality_trend.png          ✓
280K results/charts/integrated_dashboard.png   ✓
```

### **레벨 6: 결과 검증 (3분)**

#### 6-1. 보고서 파일 열기
```bash
# 보고서 열기 (Windows)
notepad results\oee_analysis_report.txt

# 또는 Markdown 파일
notepad results\integration_summary.md
```

**확인 항목**:
- ✓ 보고서에 숫자 데이터가 포함됨
- ✓ OEE 값이 0~100% 범위
- ✓ 불량률이 0~100% 범위
- ✓ 설비별/라인별 분석이 포함됨

#### 6-2. 차트 파일 확인
```bash
# 이미지 파일 열기 (Windows)
start results\charts\oee_gauge.png
start results\charts\integrated_dashboard.png

# Mac/Linux
open results/charts/oee_gauge.png
open results/charts/integrated_dashboard.png
```

**확인 항목**:
- ✓ 4개 게이지 차트가 표시됨 (가용성, 성능, 품질, OEE)
- ✓ 막대 차트, 피 차트, 선형 추이 차트 포함
- ✓ 한글 텍스트가 올바르게 표시됨
- ✓ 색상과 레이아웃이 명확함

#### 6-3. CSV 데이터 확인
```bash
# CSV 파일 열기
cat results/data/equipment_oee.csv | head -10
```

**예상 결과** (첫 5행):
```
equipment_id,equipment_name,availability,performance,quality,oee,rank
1,설비A,88.5,92.3,92.8,75.43,1
2,설비B,85.2,89.1,91.2,69.25,2
3,설비C,82.1,87.5,90.0,64.49,3
...
```

---

## 🔍 검증 체크리스트

| 단계 | 항목 | 명령어 | 상태 |
|-----|------|--------|------|
| **1** | 폴더 구조 | `ls -la src/ data/ results/` | ✓/✗ |
| **2** | 필수 파일 | `ls src/config.py src/main.py` | ✓/✗ |
| **3** | 데이터 파일 | `ls data/raw/p*_*.csv` | ✓/✗ |
| **4** | Python 버전 | `python --version` | ✓/✗ |
| **5** | 패키지 | `pip list \| grep pandas` | ✓/✗ |
| **6** | 모듈 로드 | `python -c "from src.config import ..."` | ✓/✗ |
| **7** | 데이터 로드 | `python test_data_load.py` | ✓/✗ |
| **8** | 분석 실행 | `python src/main.py` | ✓/✗ |
| **9** | 결과 파일 | `ls -la results/` | ✓/✗ |
| **10** | 보고서 내용 | `cat results/*.md` | ✓/✗ |

**✅ 모든 항목이 ✓이면 프로젝트 설정 완료!**

---

## 📈 주요 출력물

### 시각화 (PNG, 300dpi)

1. **oee_gauge.png** - OEE 게이지 (가동률, 성능률, 양품률, OEE)
2. **equipment_comparison.png** - 상위 설비 OEE 비교
3. **line_comparison.png** - 라인별 OEE 비교 (막대 + 레이더)
4. **oee_trend.png** - 주간 OEE 추이
5. **six_big_losses.png** - 비가동 원인별 손실
6. **improvement.png** - 개선 효과 (개선전/후 비교)
7. **integrated_dashboard.png** - 통합 분석 대시보드 (한 페이지)

### 데이터 (CSV)

1. **01_equipment_oee.csv** - 설비별 OEE 및 상세 지표
2. **02_line_oee.csv** - 라인별 OEE
3. **03_six_big_losses.csv** - 비가동 유형별 손실 분석
4. **04_period_oee.csv** - 주간 OEE 추이

### 리포트 (Markdown)

1. **00_integrated_insights.md** - 통합 분석 인사이트
2. **01_oee_report.md** - OEE 상세 분석 리포트
3. **02_quality_report.md** - 품질 분석 리포트
4. **03_maintenance_report.md** - 설비 분석 리포트
5. **04_energy_report.md** - 에너지 분석 리포트

---

## 🔧 코드 모듈 설명

### config.py
- 프로젝트 전사적 설정 (경로, 상수, 임계값)
- OEE, 품질, 설비, 에너지 목표 기준값
- 시각화 설정 (색상, 폰트, DPI)
- 통계 분석 파라미터

### utils.py
- 환경 초기화 및 로거 설정
- 데이터 로드, 검증, 전처리
- 통계 분석 (summary stats, t-test)
- 파일 저장 (CSV, Excel, Parquet)
- 형식화 함수 (숫자, 백분율, 통화)

### data_loader.py
- 4개 프로젝트 데이터 통합 로드
- 프로젝트별 데이터 그룹화 (get_oee_data() 등)
- 메모리 효율화

### analyzers/oee_analyzer.py
- OEE 3대 요소 계산 (가동률, 성능률, 양품률)
- 수준별 분석 (전체, 설비별, 라인별, 기간별)
- Six Big Losses 분석
- 개선 효과 분석 및 통계 검증

### [[추가 분석기들]]
- quality_analyzer.py - 품질 통계 및 SPC
- maintenance_analyzer.py - 센서 데이터 분석
- energy_analyzer.py - 에너지 원단위 및 피크 분석

### visualizers/integrated_visualizer.py
- 게이지 차트, 막대/선 차트, 레이더 차트
- 파이 차트, 히트맵 등 다양한 시각화
- 통합 대시보드 구성
- 자동 저장 기능

---

## 🎓 학습 포인트

### 데이터 엔지니어링
✅ 다중 프로젝트 데이터 통합 및 표준화
✅ 결측치/이상치 처리 전략
✅ 파생변수 생성 및 엔지니어링
✅ 시계열 데이터 처리 및 분석

### 통계 분석
✅ OEE 계산 및 설비 효율 분석
✅ SPC(Statistical Process Control)
✅ 가설 검정 (t-test, p-value)
✅ 공정능력 분석 (Cp, Cpk)
✅ 상관관계 및 회귀 분석

### 시각화 및 표현
✅ 다양한 차트 유형 구현
✅ 대시보드 설계 및 구성
✅ 의사결정 중심의 시각화
✅ 고품질 이미지 생성 (300dpi)

### 소프트웨어 공학
✅ 모듈화 및 재사용 가능한 설계
✅ 객체지향 프로그래밍 (OOP)
✅ 설정 중앙화 (config.py)
✅ 로깅 및 에러 처리
✅ 명확한 네이밍 컨벤션

### 프로젝트 관리
✅ 장기 프로젝트 구조화
✅ 문서화 및 주석 작성
✅ 버전 관리 및 재현성
✅ 성능 최적화 및 스케일링

---

## 💡 사용 사례

### 경영진 보고 (분기별)
→ 통합 대시보드 1장으로 공장 전체 상황 요약

### 설비팀 회의 (주간)
→ 비가동 원인별 분석 및 개선 방안 수립

### 품질팀 회의 (주간)
→ 불량 현황 및 SPC 관리도 검토

### 에너지팀 회의 (월간)
→ 에너지 사용 패턴 분석 및 절감 방안

### 개선 프로젝트
→ 우선순위 결정 및 효과 검증 기준 제공

---

## 🔄 확장 가능성

### 단기 (1개월)
- [ ] 각 분석기 기능 보강
- [ ] 대시보드 인터랙티브화
- [ ] 자동 리포트 생성

### 중기 (3개월)
- [ ] 머신러닝 모델 추가 (고장 예측, 이상탐지)
- [ ] 시뮬레이션 모듈 (What-if 분석)
- [ ] 실시간 모니터링 시스템

### 장기 (6개월)
- [ ] 클라우드 배포 (AWS/Azure)
- [ ] 웹 대시보드 (Streamlit/Tableau)
- [ ] 모바일 앱 개발

---

## 📝 주요 파일 설명

| 파일 | 역할 | 크기 |
|------|------|------|
| config.py | 전사 설정 | ~300줄 |
| utils.py | 공통 함수 | ~400줄 |
| data_loader.py | 데이터 로드 | ~150줄 |
| oee_analyzer.py | OEE 분석 | ~350줄 |
| integrated_visualizer.py | 시각화 | ~500줄 |
| main.py | 메인 스크립트 | ~350줄 |

총 코드량: **~2,000줄** (프로덕션급)

---

## 🤝 기여 가이드

1. **새로운 분석기 추가**
   ```python
   # analyzers/new_analyzer.py 생성
   class NewAnalyzer:
       def run_analysis(self, data):
           # 분석 로직
           pass
   ```

2. **새로운 시각화 추가**
   ```python
   # visualizers/new_visualizer.py 에서
   def plot_new_chart(self, data):
       # 시각화 로직
       pass
   ```

3. **프로젝트 실행**
   ```bash
   python src/main.py
   ```

---

## 📞 문의 및 지원

- **데이터 이슈**: `data/raw/` 폴더 확인
- **코드 오류**: README의 "문제 해결" 섹션 참고
- **결과 해석**: `docs/` 폴더의 상세 설명 참고

---

## 📜 라이선스 및 저작권

**프로젝트**: 한국정밀산업(주) 스마트팩토리팀
**작성일**: 2024년 6월
**버전**: 1.0
**상태**: ✅ 완료 및 운영 중

---

**마지막 수정**: 2024년 6월 30일

이 통합 프로젝트는 4개의 독립적인 분석 프로젝트에서 배운 모든 기술과 인사이트를 하나로 통합한 **엔터프라이즈급 데이터 분석 시스템**입니다. 🎉
