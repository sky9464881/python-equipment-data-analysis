# 🏭 스마트팩토리 데이터 분석 통합 시스템


> ** 데이터 분석 플랫폼**

**OEE 분석**, **품질관리**, **예지보전**, **에너지효율**을 4개 독립 분석 모듈로 나누어  
각각 최적화된 분석을 수행한 후 **통합 대시보드**로 전체 상황을 한눈에 파악합니다.

### 🎯 핵심 목표
- ✅ 설비 효율성 극대화 (OEE 85% 이상)
- ✅ 품질 관리 고도화 (Cpk ≥ 1.33)
- ✅ 예기치 않은 고장 예방 (예지보전)
- ✅ 에너지 비용 절감 (원단위 최적화)

---

## 📦 프로젝트 구조

```
work/
│
├── 🎯 integrated_project/          ⭐ 메인 분석 프로젝트
│   ├── data/
│   │   ├── raw/                    # 원본 데이터
│   │   │   ├── project1/           # OEE 분석 데이터
│   │   │   ├── project2/           # 품질 분석 데이터
│   │   │   ├── project3/           # 설비/정비 데이터
│   │   │   └── project4/           # 에너지 분석 데이터
│   │   └── processed/              # 분석 결과 데이터
│   │
│   ├── src/                        # 핵심 소스 코드 (~2,500줄)
│   │   ├── config.py               # 전사 설정 (경로, 임계값)
│   │   ├── utils.py                # 공통 유틸리티
│   │   ├── data_loader.py          # 데이터 로딩
│   │   ├── main.py                 # 메인 실행 스크립트
│   │   ├── analyzers/              # 4개 분석 모듈
│   │   │   ├── oee_analyzer.py     # OEE 분석 (가동/성능/품질)
│   │   │   ├── quality_analyzer.py # 품질 분석 (SPC, Cpk)
│   │   │   ├── maintenance_analyzer.py  # 정비 분석 (이상탐지)
│   │   │   └── energy_analyzer.py  # 에너지 분석 (효율성)
│   │   ├── visualizers/            # 시각화 모듈
│   │   │   └── integrated_visualizer.py # 통합 차트
│   │   └── reporters/              # 리포트 생성
│   │
│   ├── docs/                       # 📖 프로젝트 문서
│   │   ├── README.md               # 상세 가이드 + 검증 방법
│   │   └── [기타 가이드]
│   │
│   ├── notebooks/                  # 📓 분석 노트북
│   │
│   ├── results/                    # 📈 분석 결과
│   │   ├── charts/                 # 시각화 차트 (PNG)
│   │   ├── data/                   # 결과 데이터 (CSV)
│   │   └── reports/                # 분석 리포트 (MD)
│   │
│   ├── requirements.txt             # Python 의존성
│   └── setup.py                     # 설치 스크립트
│
├── 📚 lectures/                     # 교육 자료
│   ├── basic/                       # Python 기초
│   ├── practice/                    # 실습 자료
│   └── visualization/               # 시각화 과정
│   └── *.ipynb (15개 강의 노트북)
│
├── 🎓 실습/                         # 연습용 프로젝트
│   ├── data/
│   ├── src/
│   ├── notebooks/
│   ├── practice/
│   ├── results/
│   └── *.ipynb (9개 연습 노트북)
│       ├── 01-05: Pandas, 전처리, 집계, 병합, 고급
│       ├── 06-08: Matplotlib, Seaborn, 차트
│       └── project1~4: 프로젝트 실습
│
└── 📊 data/                         # 기본 예제 데이터 (CSV)
    └── *.csv (40+ 데이터 파일)
```

---

## 🚀 사용 방법 (Step-by-Step)

초보자도 따라할 수 있는 단계별 가이드입니다. **약 5분이면 첫 분석 결과를 얻을 수 있습니다.**

### **STEP 1️⃣ : 프로젝트 폴더로 이동**

```bash
cd integrated_project
```

**확인**: 다음 폴더/파일이 보이는지 확인하세요
```
data/          ← 데이터 폴더
src/           ← 코드 폴더
docs/          ← 문서 폴더
results/       ← 결과 폴더
requirements.txt
```

---

### **STEP 2️⃣ : Python 환경 설정**

#### 2-1) Python 버전 확인
```bash
python --version
```

**예상 결과**:
```
Python 3.8.10   ← 3.8 이상이어야 함 ✓
```

> ⚠️ Python 3.7 이하면 `python` 대신 `python3` 사용

#### 2-2) 필수 패키지 설치

```bash
pip install -r requirements.txt
```

**설치 내용**:
```
pandas          ← 데이터 처리
numpy           ← 수치 계산
matplotlib      ← 시각화
seaborn         ← 통계 플롯
scipy           ← 통계 분석
openpyxl        ← Excel 처리
jupyter         ← 노트북
...
```

**소요 시간**: 1-2분

**설치 완료 확인**:
```bash
pip list | grep pandas
# 출력: pandas                             2.0.0
```

> ⚠️ **openpyxl 버전 에러 발생 시**:
> ```
> ERROR: No matching distribution found for openpyxl>=3.7.0
> ```
> → 이미 수정됨 (requirements.txt에서 3.0.0으로 변경)
> → 다시 실행: `pip install -r requirements.txt`

---

### **STEP 3️⃣ : 데이터 확인 (필수!)**

#### 3-1) 데이터 폴더 구조 확인

```bash
# Linux/Mac
ls -la data/raw/

# Windows (PowerShell)
Get-ChildItem data/raw/ -Recurse
```

**예상 결과**:
```
data/raw/
├── project1/    ← 4개 CSV 파일
├── project2/    ← 4개 CSV 파일
├── project3/    ← 4개 CSV 파일
└── project4/    ← 4개 CSV 파일
```

> ⚠️ 데이터 폴더가 비어있으면 분석을 못합니다. 확인하세요!

#### 3-2) 데이터 파일 목록 확인

```bash
# Project 1 확인
ls data/raw/project1/
```

**예상 결과**:
```
p1_downtime_log.csv      (약 430건의 정비 기록)
p1_equipment.csv         (약 20개 설비 정보)
p1_product.csv           (약 50개 제품 정보)
p1_production_log.csv    (약 3,100건의 생산 기록)
```

---

### **STEP 4️⃣ : 분석 실행**

#### 4-1) 한 줄로 모든 분석 실행

**Windows 환경**:
```bash
# Windows cmd 또는 PowerShell에서 UTF-8 인코딩으로 실행
chcp 65001
python src/main.py
```

**또는 (더 안정적)**:
```bash
# 환경 변수 설정과 함께 실행
set PYTHONIOENCODING=utf-8
python src/main.py
```

**Mac/Linux**:
```bash
python src/main.py
```

**실행 중 화면**:
```
================================================================================
        한국정밀산업(주) 통합 팩토리 분석 시스템
================================================================================

✓ 초기화
✓ 데이터 로드
✓ OEE 분석 - [1] OEE 계산 → 전체 OEE: 75.43%
✓ 품질 분석 - [2] 품질 분석 → 합격률: 96.50%
✓ 정비 분석 - [3] 설비 건강도 → 건강도: 82/100 (정상)
✓ 에너지 분석 - [4] 에너지 효율 → 총 소비: 52,000 kWh
✓ 시각화
✓ 분석 완료
```

**소요 시간**: 1-2분

---

#### 4-2) 개별 분석만 실행하기 (선택사항)

```python
# Python 인터랙티브 모드에서
python

# 또는 새 파일 analyze_single.py 작성
```

```python
from src.data_loader import DataLoader
from src.analyzers.oee_analyzer import OEEAnalyzer
from utils import print_section

# 데이터 로드
loader = DataLoader()
oee_data = loader.get_oee_data()

# OEE 분석만 실행
if oee_data.get('equipment') is not None:
    analyzer = OEEAnalyzer(
        oee_data['production'],
        oee_data['equipment'],
        oee_data['downtime']
    )
    results = analyzer.run_full_analysis()
    print("✓ OEE 분석 완료")
```

---

### **STEP 5️⃣ : 결과 확인**

#### 5-1) 생성된 결과 파일 확인

```bash
ls -la results/
```

**예상 결과**:
```
results/
├── charts/                          ← 이미지 파일 (PNG)
│   ├── oee_gauge.png                (게이지 차트)
│   ├── equipment_comparison.png      (설비 비교)
│   ├── quality_trend.png             (품질 추세)
│   ├── integrated_dashboard.png      (통합 대시보드)
│   └── ... (10+ 파일)
│
├── data/                            ← 데이터 파일 (CSV)
│   ├── equipment_oee.csv
│   ├── quality_metrics.csv
│   ├── energy_consumption.csv
│   └── ... (5+ 파일)
│
└── reports/                         ← 리포트 (Markdown)
    ├── 00_integrated_insights.md
    ├── 01_oee_report.md
    └── ... (4+ 파일)
```

#### 5-2) 이미지 보기

```bash
# Mac
open results/charts/oee_gauge.png

# Windows (PowerShell)
start results/charts/oee_gauge.png

# Linux
xdg-open results/charts/oee_gauge.png
```

#### 5-3) 리포트 읽기

```bash
# 통합 분석 리포트 보기
cat results/reports/00_integrated_insights.md

# 또는 텍스트 에디터에서 열기 (Notepad, VS Code 등)
```

#### 5-4) 데이터 파일 확인

```bash
# CSV 파일 미리보기
head -5 results/data/equipment_oee.csv
```

**예상 결과**:
```
equipment_id,equipment_name,availability,performance,quality,oee,rank
1,설비A,88.5,92.3,92.8,75.43,1
2,설비B,85.2,89.1,91.2,69.25,2
3,설비C,82.1,87.5,90.0,64.49,3
```

---

## 🔍 상세 분석 설명

### 1️⃣ OEE 분석 (Project 1)

**OEE = 가동률 × 성능률 × 양품률**

```
목표: OEE 85% 이상 달성

OEE 분석 결과:
├─ 전체 OEE: 75.43%
├─ 가용성 (A): 88.50% ← 설비 가동 가능 시간의 88.5%만 가동
├─ 성능 (P): 92.30% ← 목표 속도의 92.3% 달성
└─ 품질 (Q): 92.80% ← 양품 비율 92.8%

결과:
├─ 설비별 순위: 설비A 1위 (75.43%), 설비B 2위 (69.25%)
├─ 라인별 분석: 라인1 80.5%, 라인2 72.1%
├─ 주간 추이: 월요일 73%, 금요일 78% (금요일에 효율 증가)
└─ Six Big Losses:
    ├─ 계획 정지: 5%
    ├─ 비계획 정지: 6.5%
    ├─ 속도 저하: 7.7%
    └─ 불량/수율 손실: 7.2%
```

**어떻게 활용하나?**
- 🎯 불량률이 높은 라인 → 품질 개선 집중
- 🎯 성능률이 낮은 설비 → 유지보수 우선순위 결정
- 🎯 가용성 저하 → 정비 스케줄 최적화

---

### 2️⃣ 품질 분석 (Project 2)

**SPC(Statistical Process Control) + 공정능력 분석**

```
목표: Cpk ≥ 1.33 (공정능력 우수)

품질 분석 결과:
├─ 합격률: 96.50%
├─ 공정능력 (Cpk): 1.45 ✓ 목표 달성
├─ 예상 불량율: 170 ppm (170개/100만개)
│
├─ 불량 유형 (Pareto 분석):
│  ├─ 치수 불량: 45% ← 상위 1개가 전체 45% 차지
│  ├─ 표면 불량: 35%
│  └─ 기타: 20% ← 상위 2개가 전체 80% 차지 (80/20 법칙)
│
└─ SPC 관리도 (X-R 차트):
   ├─ 관리한계: ±2.5σ
   ├─ 이상 신호 횟수: 3회 ← 프로세스 개선 필요
   └─ 추세: 안정적
```

**어떻게 활용하나?**
- 📊 Cpk 1.45 → 공정이 안정적이고 우수함
- 📊 불량 유형 45% → **이것만 개선해도 전체 불량 45% 감소**
- 📊 SPC 이상 신호 3회 → 그 시점의 공정 조건 조사

---

### 3️⃣ 정비/예지보전 분석 (Project 3)

**센서 데이터 기반 설비 상태 모니터링**

```
목표: 예기치 않은 고장 제로화

정비 분석 결과:
├─ 설비 건강도: 82/100 (정상)
├─ MTBF (평균 고장 간격): 45일
├─ MTTR (평균 수리 시간): 2.5시간
├─ 가용성: 98.5%
│
├─ 이상탐지:
│  ├─ 온도 경고: 5건 (임계값 70°C 초과)
│  ├─ 진동 경고: 3건 (임계값 8 mm/s 초과)
│  └─ 이상치 (Z-score): 12건
│
└─ 고장 전조 신호:
   ├─ 온도: 고장 7일 전 +5°C 상승 감지
   ├─ 진동: 고장 3일 전 50% 증가 감지
   └─ 전류: 고장 1일 전 튀는 패턴 감지
```

**어떻게 활용하나?**
- 🔧 건강도 82 → 앞으로 1-2개월 내 정비 필요
- 🔧 온도 경고 5건 → 냉각 시스템 점검
- 🔧 진동 증가 5일 전 감지 → 계획 정비 가능 (비상 정지 회피)

---

### 4️⃣ 에너지 분석 (Project 4)

**에너지 효율 + 절감 기회 분석**

```
목표: 에너지 원단위 0.50 kWh/개 이하 달성

에너지 분석 결과:
├─ 총 전력 소비: 52,000 kWh
├─ 평균 소비: 2.5 kW
├─ 최대 로드: 8.5 kW
│
├─ 효율성:
│  ├─ 현황: 0.45 kWh/제품
│  ├─ 목표: 0.50 kWh/제품
│  └─ 달성율: 110% ✓ 목표 달성
│
├─ 시간대별 분석:
│  ├─ 피크시간 (09-17시): 3.5 kW
│  ├─ 비피크 (18-08시): 1.8 kW
│  └─ 비율: 1.94배
│
└─ 절감 기회:
   ├─ 피크 시프팅: 월 500만원 절감
   ├─ 공정 최적화: 월 300만원 절감
   ├─ 설비 교체: 월 200만원 절감
   └─ 합계: 월 1,000만원 절감 가능
```

**어떻게 활용하나?**
- 💡 현황 0.45 → 목표 달성 중! 더 개선 시도하면 최고 효율
- 💡 피크시간 3.5kW → 일부 공정을 18시 이후로 시프트하면 전기료 30% 절감
- 💡 월 1,000만원 절감 → 연간 1.2억원 절감 기회!



---

## ✅ 검증 및 문제 해결

### 문제 1️⃣ : `ModuleNotFoundError: No module named 'pandas'`

**원인**: 패키지가 설치되지 않음

**해결방법**:
```bash
pip install -r requirements.txt
# 또는 개별 설치
pip install pandas numpy matplotlib seaborn scipy
```

---

### 문제 2️⃣ : `FileNotFoundError: data/raw/project1 폴더를 찾을 수 없음`

**원인**: 데이터가 올바른 위치에 없음

**확인 방법**:
```bash
# 현재 위치 확인
pwd  # /c/Users/.../integrated_project 이어야 함

# 데이터 폴더 확인
ls -la data/raw/
```

**해결방법**:
1. `/integrated_project` 폴더로 이동 확인
2. `data/raw/project1~4/` 폴더가 모두 있는지 확인
3. 각 폴더에 CSV 파일이 있는지 확인

---

### 문제 3️⃣ : `UnicodeEncodeError: 'cp949' codec can't encode character` (Windows)

**원인**: Windows의 기본 인코딩(cp949)가 UTF-8 문자를 지원하지 않음

**해결방법**:

**방법 1** (추천):
```bash
# PowerShell에서 UTF-8로 변경
chcp 65001

# 그 후 실행
python src/main.py
```

**방법 2** (더 안정적):
```bash
# 환경 변수 설정
set PYTHONIOENCODING=utf-8
python src/main.py
```

**방법 3** (한 줄로):
```bash
# PowerShell
$env:PYTHONIOENCODING='utf-8'; python src/main.py
```

---

### 문제 3-1️⃣ : 한글이 깨져서 보임

### 문제 3-1️⃣ : 한글이 깨져서 보임

**원인**: 그래프 폰트 설정 문제

**해결방법**:
```bash
# src/config.py 파일 수정
FONT_NAME = 'Malgun Gothic'  # Windows 권장
# 또는
FONT_NAME = 'DejaVu Sans'    # Mac/Linux
```

---

### 문제 4️⃣ : 결과 폴더가 비어있음

**원인**: 분석이 성공적으로 완료되지 않음

**해결방법**:
```bash
# 로그 확인
python src/main.py 2>&1 | tee analysis.log

# 로그 파일 확인
cat analysis.log | grep ERROR
```

---

## 🎓 학습 경로

### 1️⃣ 초보자 (Python 처음)
```
lectures/
├─ 01_변수와_자료형.ipynb
├─ 02_자료구조.ipynb
└─ 03_조건문.ipynb
```

### 2️⃣ 초급자 (Pandas 배우기)
```
lectures/ + 실습/
├─ 06_numpy.ipynb
├─ 07_pandas.ipynb
├─ 01_pandas_basic_practice.ipynb
└─ 02_preprocessing_practice.ipynb
```

### 3️⃣ 중급자 (프로젝트 따라하기)
```
실습/project1~4_practice.ipynb
├─ project1_oee_practice.ipynb
├─ project2_quality_spc_practice.ipynb
├─ project3_predictive_maintenance_practice.ipynb
└─ project4_energy_analysis_practice.ipynb
```

### 4️⃣ 고급자 (프로젝트 직접 운영)
```
integrated_project/
├─ src/main.py 실행
├─ 결과 분석
└─ 새로운 분석 추가 개발
```

---

## 📚 파일별 역할

### 핵심 모듈

| 파일 | 역할 | 라인 수 |
|-----|------|--------|
| `src/config.py` | 전사 설정, 경로, 임계값 | ~300 |
| `src/utils.py` | 로깅, 데이터 처리, 통계 함수 | ~400 |
| `src/data_loader.py` | 4개 프로젝트 데이터 통합 로드 | ~150 |
| `src/main.py` | 메인 실행 스크립트 | ~350 |

### 분석 모듈

| 파일 | 기능 | 라인 수 |
|-----|------|--------|
| `analyzers/oee_analyzer.py` | OEE 3-factor 계산 | ~350 |
| `analyzers/quality_analyzer.py` | SPC, Cpk 분석 | ~350 |
| `analyzers/maintenance_analyzer.py` | 이상탐지, 건강도 | ~350 |
| `analyzers/energy_analyzer.py` | 효율성, 절감 기회 | ~350 |

### 시각화

| 파일 | 차트 | 라인 수 |
|-----|------|--------|
| `visualizers/integrated_visualizer.py` | 8+ 차트 타입 생성 | ~500 |

---

## ❓ 자주 묻는 질문

### Q1. 내 데이터를 추가하려면?

**A**: 다음 단계를 따르세요:

1. 데이터를 CSV 형식으로 준비
2. `data/raw/projectX/` 에 복사
3. `config.py` 에서 파일 경로 등록
4. `data_loader.py` 에 로드 함수 추가
5. `src/main.py` 에서 호출

---

### Q2. 분석 주기는?

**A**: 필요에 따라 다릅니다:

- **일일**: 일일 OEE 모니터링
- **주간**: 주간 품질 SPC 차트
- **월간**: 월간 에너지 비용 분석
- **분기**: 분기 개선 효과 검증

```bash
# 자동화 예제 (매일 21시 실행)
0 21 * * * cd /path/to/integrated_project && python src/main.py
```

---

### Q3. 새로운 분석을 추가하려면?

**A**: 다음 과정을 따르세요:

```python
# 1. src/analyzers/new_analyzer.py 생성
class NewAnalyzer:
    def __init__(self, data):
        self.data = data
    
    def analyze(self):
        # 분석 로직
        results = {}
        return results

# 2. src/main.py 에서 import & 호출
from src.analyzers.new_analyzer import NewAnalyzer

def run_new_analysis(data):
    analyzer = NewAnalyzer(data)
    return analyzer.analyze()

# 3. main() 함수에서 호출
results['new_analysis'] = run_new_analysis(data)
```

---

### Q4. 결과를 Excel로 내보내려면?

**A**: 이미 지원됩니다!

```python
from src.utils import save_dataframe
import pandas as pd

# CSV로 저장 (기본)
save_dataframe(df, 'my_analysis')

# Excel로 저장
df.to_excel('results/data/my_analysis.xlsx', index=False)
```

---

### Q5. 클라우드에 배포하려면?

**A**: AWS/Azure 배포 가이드:

1. `requirements.txt` 가져가기 ✓
2. `src/` 코드 업로드 ✓
3. `data/raw/` 데이터 업로드
4. 스케줄러로 자동 실행 (Lambda, Cloud Scheduler)
5. 결과를 S3/Blob Storage에 저장

---

## 📊 결과 분석 팁

### 💡 OEE가 낮을 때
```
OEE = 가동률 × 성능률 × 양품률

낮은 이유:
1. 가동률 < 80%     → 정지 시간이 많음 (정비 필요)
2. 성능률 < 90%     → 느린 속도 (설정 확인)
3. 양품률 < 95%     → 불량 많음 (품질 개선)
```

**해결책 우선순위**:
1. 가장 낮은 항목부터 개선
2. 예: 성능률이 70%면, 성능 개선으로 5% 향상 → OEE 5% 향상

---

### 💡 Cpk가 1.33 미만일 때
```
Cpk < 1.33 → 공정 능력 부족

원인:
1. 규격 편차가 큼     → 치수 산포 확대
2. 공정 센터 이탈     → 공정 중심 조정
3. 변동성 커짐        → 재료/환경 영향
```

**해결책**:
1. 불량 Pareto 분석 → 상위 2개 불량 80% 차지
2. 상위 2개만 집중 개선 → Cpk 1.33 달성 가능

---

### 💡 설비 건강도가 낮을 때
```
건강도 점수:
- 80+ : 정상
- 50-80 : 주의 (1-2개월 내 점검)
- <50 : 위험 (긴급 정비)
```

**대응**:
1. 온도/진동 센서 확인
2. 고장 전조 신호 분석
3. 예방 정비 스케줄 수립

---

### 💡 에너지 낭비가 클 때
```
절감 기회 상위 3가지:

1. 피크 시프팅 (효과: 30%)
   → 생산 일정 조정

2. 공정 최적화 (효과: 15%)
   → 라인별 효율 개선

3. 설비 교체 (효과: 20%)
   → 5년 이상 노후 설비 먼저
```



---

## 🎓 강의 & 연습

### 📚 lectures/ 폴더 (교육 자료)

**Python 기초** (01-05):
- 01_변수와자료형.ipynb
- 02_자료구조.ipynb
- 03_조건문.ipynb
- 05_함수.ipynb

**데이터처리** (06-12):
- 06_numpy.ipynb
- 07_pandas.ipynb
- 08_데이터분석1.ipynb
- 09_데이터분석2.ipynb
- 10_집계분석.ipynb
- 11_advanced.ipynb
- 12_advanced.ipynb

**시각화** (13-15):
- 13_matplotlib.ipynb
- 14_seaborn.ipynb
- 15_advanced_chart.ipynb

### 🏆 실습/ 폴더 (프로젝트 실습)

**기초 실습**:
- 01_pandas_basic_practice.ipynb
- 02_preprocessing_practice.ipynb
- 03_aggregation_practice.ipynb
- 04_merging_practice.ipynb
- 05_advanced_practice.ipynb

**시각화 실습**:
- 06_matplotlib_basic_practice.ipynb
- 07_seaborn_basic_practice.ipynb
- 08_advanced_visualization_practice.ipynb

**프로젝트 실습**:
- project1_oee_practice.ipynb ← OEE 분석 연습
- project2_quality_spc_practice.ipynb ← 품질/SPC 연습
- project3_predictive_maintenance_practice.ipynb ← 정비 연습
- project4_energy_analysis_practice.ipynb ← 에너지 연습

---

## 🔗 다음 단계

완료 후 다음 단계를 시도해보세요:

- [ ] **실시간 대시보드** 구축 (Streamlit)
- [ ] **자동 스케줄** 설정 (매일 자동 분석)
- [ ] **머신러닝** 추가 (이상탐지, 예측)
- [ ] **웹 배포** (Flask, Django)
- [ ] **클라우드 이전** (AWS, Azure)
- [ ] **알림 시스템** 구축 (문제 발생시 자동 알림)

---

## 📊 프로젝트 통계

| 항목 | 수치 |
|-----|------|
| **총 코드 라인** | ~2,500줄 |
| **분석 모듈** | 4개 (OEE, 품질, 정비, 에너지) |
| **시각화 차트** | 8+ 종류 |
| **설정 항목** | 50+ |
| **유틸리티 함수** | 20+ |
| **강의 노트북** | 15개 |
| **실습 노트북** | 9개 |
| **저장소 크기** | 9.4MB |
| **분석 시간** | ~1-2분 |
| **소요 학습시간** | 40-60시간 (초보→중급) |

---

## 🏗️ 기술 스택

```
언어 & 환경:
├─ Python 3.8+
├─ Jupyter Notebook
└─ Git/GitHub

데이터 처리:
├─ Pandas (DataFrame 조작)
├─ NumPy (수치 계산)
└─ SciPy (통계 분석)

시각화:
├─ Matplotlib (기본 차트)
├─ Seaborn (통계 플롯)
└─ Plotly (인터랙티브, 선택사항)

저장소:
├─ CSV (기본)
├─ Excel (openpyxl)
└─ JSON (선택사항)

배포:
├─ Docker (선택사항)
├─ AWS/Azure (선택사항)
└─ Streamlit (웹 대시보드)
```

---

## 🎯 실전 시나리오

### 시나리오 1️⃣ : 월간 경영진 보고회

**상황**: 매월 1일 경영진에게 공장 현황 보고

**해결책**:
```bash
# 1. 월말에 자동 분석 실행
python src/main.py

# 2. 결과 파일 생성
results/
├─ charts/integrated_dashboard.png ← 대시보드 1장
├─ 00_integrated_insights.md      ← 핵심 인사이트
└─ data/                          ← 상세 데이터

# 3. 파워포인트 작성 (1시간 소요 → 대폭 단축)
# 기존: 수작업 데이터 정리 (하루 이상)
# 현재: 자동화 분석 + PPT 정리 (1시간)
```

### 시나리오 2️⃣ : 설비팀 일일 회의

**상황**: 매일 아침 생산 설비 상황 회의

**해결책**:
```bash
# 1. 06시에 자동으로 분석 실행
# (cronjob으로 설정)

# 2. 08시 회의 전 결과 확인
- OEE 추이: 어제 75%, 오늘 77% ↑
- 설비 건강도: 설비A 82/100 (정상)
- 예정된 정비: 설비B 점검 필요

# 3. 따라서 조치:
- 설비A: 정상 운영 계속
- 설비B: 점심시간에 30분 점검
- 설비C: 내일 예방 정비 스케줄
```

### 시나리오 3️⃣ : 품질 문제 발생

**상황**: 오전에 불량률이 8%로 급증

**해결책**:
```python
# 1. 즉시 품질 분석만 실행
from src.main import run_quality_analysis
from src.data_loader import DataLoader

loader = DataLoader()
quality_data = loader.get_quality_data()
results = run_quality_analysis(quality_data)

# 2. 결과 확인
불량 유형:
├─ 치수 불량: 45% (A라인에서)
├─ 표면 불량: 35% (B라인에서)
└─ 기타: 20%

# 3. 즉시 조치
- A라인: 치수 설정 재점검 (5분)
- B라인: 버니시 시스템 청소 (10분)
- 결과: 1시간 내 불량률 2%로 정상화
```

---

## 📖 문서 가이드

```
📁 docs/ (상세 문서)
├─ README.md                    ← 이 파일 (🌟 여기서 시작!)
├─ STRUCTURE.md                 ← 프로젝트 구조 상세 설명
├─ API_REFERENCE.md             ← 함수/클래스 레퍼런스
├─ TUTORIAL.md                  ← 단계별 튜토리얼
└─ TROUBLESHOOTING.md           ← 문제 해결 가이드

📓 notebooks/ (분석 예제)
├─ oee_analysis_example.ipynb
├─ quality_analysis_example.ipynb
├─ maintenance_analysis_example.ipynb
└─ energy_analysis_example.ipynb

🎓 lectures/ (교육 자료)
└─ (15개 강의 노트북)

🏆 실습/ (연습용)
└─ (9개 실습 노트북)
```

---

## 🔗 관련 링크

- **상세 가이드**: [integrated_project/docs/README.md](integrated_project/docs/README.md) ← 검증 방법 포함
- **수정 히스토리**: [GitHub](https://github.com)
- **이슈 보고**: GitHub Issues
- **문의**: 팀 분석가 (이메일)

---

## 📧 연락처 & 지원

**문제 발생 시**:
1. README.md 처음부터 다시 읽기
2. [TROUBLESHOOTING.md](integrated_project/docs/TROUBLESHOOTING.md) 확인
3. 로그 파일 확인: `analysis.log`
4. 팀 분석가에게 문의

**개선 제안**:
- GitHub Issues에 제안사항 등록
- 또는 팀 회의에서 논의

---

## 📋 체크리스트

프로젝트 시작 전 확인하세요:

- [ ] Python 3.8+ 설치됨?
- [ ] integrated_project 폴더 위치 확인?
- [ ] data/raw/project1~4 폴더에 데이터 있는지 확인?
- [ ] `pip install -r requirements.txt` 완료?
- [ ] `python src/main.py` 실행 성공?
- [ ] `results/` 폴더에 파일 생성됨?
- [ ] 차트와 리포트 확인 완료?

✅ 모두 체크되면 프로젝트 준비 완료!

---

## 🎉 축하합니다!

이제 다음을 할 수 있습니다:

✅ 전사적 데이터 분석  
✅ 설비 효율성 모니터링  
✅ 품질 관리 자동화  
✅ 예지보전 시스템  
✅ 에너지 절감 기회 발굴  
✅ 데이터 기반 의사결정  

**이 모든 것이 단 하나의 명령으로:**
```bash
python src/main.py
```

---

**마지막 업데이트**: 2026년 4월 8일  
**버전**: 1.0  
**상태**: ✅ 완료 및 운영 중  
**유지보수**: 지속적 개선 중



