# 스마트팩토리 통합 데이터 분석 시스템

> **OEE, 품질, 예지보전, 에너지 데이터를 통합 분석하여 공장 운영 상태를 한눈에 파악할 수 있도록 설계한 스마트팩토리 데이터 분석 포트폴리오 프로젝트**

---

## 프로젝트 소개
<img width="6427" height="4145" alt="integrated_dashboard" src="https://github.com/user-attachments/assets/1cdd52e8-8d70-407c-a0fd-0079d15df5d0" />

제조 현장에서는 생산, 품질, 정비, 에너지 데이터가 각각 분리되어 관리되는 경우가 많습니다.  
이 프로젝트는 이러한 데이터를 **하나의 분석 흐름으로 통합**하여, 공장 운영 상태를 더 빠르고 직관적으로 파악할 수 있도록 구성했습니다.

단순히 개별 지표를 보여주는 것이 아니라,

- 설비 효율이 어느 수준인지
- 어떤 설비와 라인이 병목인지
- 품질 저하와 이상 징후가 어디서 발생하는지
- 에너지 사용이 어디서 비효율적인지

를 **통합 대시보드**와 분석 차트로 확인할 수 있도록 설계했습니다.

---

## 핵심 목표

- **설비 효율 극대화**: OEE 85% 이상 달성 지원
- **품질 관리 고도화**: Cpk 1.33 이상 목표
- **예지보전 강화**: 이상 징후 조기 탐지
- **에너지 비용 절감**: 원단위 및 피크 사용 분석

---

## 주요 기능

### OEE 분석
- 가동률(Availability), 성능률(Performance), 양품률(Quality) 계산
- 종합 OEE 산출
- 설비별 / 라인별 OEE 비교
- OEE 추이 분석
- Six Big Losses 분석
- 개선 전후 비교

### 품질 분석
- 제품 규격 대비 측정값 분석
- 합격률 및 불량 유형 집계
- Cpk 기반 공정능력 분석
- 파레토 및 SPC 시각화

### 예지보전 분석
- 센서 데이터 기반 이상 징후 탐지
- 건강도(Health Index) 산출
- 고장 전조 신호 탐지
- 정비 우선순위 제안

### 에너지 분석
- 설비별 / 시간대별 전력 사용량 분석
- 생산량 대비 에너지 원단위 분석
- 피크 사용 구간 파악
- 절감 포인트 도출

### 통합 대시보드
- 핵심 KPI 요약
- 라인별 성과 비교
- 손실 요인 시각화
- 개선 효과 및 실행 과제 정리

---

## 문제 정의

스마트팩토리 환경에서는 생산, 품질, 정비, 에너지 데이터가 서로 분리되어 관리되는 경우가 많아 전체 운영 상태를 한 번에 파악하기 어렵습니다.

예를 들어,

- 생산 데이터는 생산 데이터대로
- 품질 데이터는 품질 데이터대로
- 설비 상태 및 센서 데이터는 별도로
- 에너지 데이터도 따로

관리되면 실제로 중요한 질문인

- 지금 공장이 어떤 상태인지
- 어디가 병목인지
- 어떤 설비를 먼저 점검해야 하는지
- 에너지가 어디서 비효율적으로 사용되는지

에 빠르게 답하기 어렵습니다.

이 프로젝트는 이러한 문제를 해결하기 위해 **여러 종류의 운영 데이터를 공통된 분석 구조로 통합하고 시각화하는 것**에 초점을 맞췄습니다.

---

## 시스템 흐름

```text
생산 / 품질 / 센서 / 에너지 데이터
                ↓
          데이터 로딩 및 전처리
                ↓
 OEE / 품질 / 예지보전 / 에너지 모듈별 분석
                ↓
     차트, CSV, 리포트 결과 자동 생성
                ↓
          통합 대시보드로 결과 통합
```

---

## 분석 모듈 구성

| 모듈 | 목적 | 핵심 지표 | 주요 산출물 |
|---|---|---|---|
| OEE | 설비 효율 분석 | OEE, 가동률, 성능률, 양품률 | 설비별 순위, 라인별 비교, 추이 분석 |
| 품질 | 공정 품질 분석 | Cpk, 합격률, 불량 유형 | 파레토 차트, SPC 차트 |
| 예지보전 | 설비 상태 진단 | 건강도, 이상 징후, MTBF | 점검 우선순위, 이상 탐지 결과 |
| 에너지 | 전력 효율 분석 | 원단위, 피크 전력, 사용 패턴 | 절감 포인트, 에너지 리포트 |

---

## 프로젝트 구조

```text
integrated_project/
├── data/
│   ├── raw/
│   │   ├── project1/           # OEE 데이터
│   │   ├── project2/           # 품질 데이터
│   │   ├── project3/           # 정비/센서 데이터
│   │   └── project4/           # 에너지 데이터
│   └── processed/              # 전처리/가공 데이터
│
├── src/
│   ├── config.py
│   ├── data_loader.py
│   ├── main.py                 # 메인 실행 파일
│   ├── utils.py
│   ├── analyzers/
│   │   ├── oee_analyzer.py
│   │   ├── quality_analyzer.py
│   │   ├── maintenance_analyzer.py
│   │   └── energy_analyzer.py
│   └── visualizers/
│
├── results/
│   ├── charts/                 # 시각화 결과
│   ├── data/                   # CSV 결과
│   └── reports/                # Markdown 리포트
│
├── requirements.txt
└── docs/
```

---

## 주요 결과물

- **차트 이미지**: `results/charts/`
- **분석 데이터**: `results/data/`
- **리포트**: `results/reports/`

예시 이미지:


![integrated_dashboard](results/charts/integrated_dashboard.png)
![oee_gauge](results/charts/oee_gauge.png)
![oee_trend](results/charts/oee_trend.png)


---

## 데이터 구성

### Project 1: OEE 분석
필수 파일
- `p1_equipment.csv`
- `p1_production_log.csv`
- `p1_downtime_log.csv`

예시:

```csv
equipment_id,equipment_name,line_id,rated_capacity
1,설비A,1,100
2,설비B,1,120
```

```csv
timestamp,equipment_id,product_id,quantity,production_time
2024-01-01 09:00,1,101,50,120
```

```csv
date,equipment_id,downtime_reason,duration_minutes,downtime_type
2024-01-01,1,부품 교체,15,계획정지
```

### Project 2: 품질 분석
필수 파일
- `p2_product_spec.csv`
- `p2_inspection_log.csv`

예시:

```csv
product_id,parameter,lower_spec,upper_spec,unit
101,길이,95,105,mm
101,두께,4.8,5.2,mm
```

```csv
timestamp,product_id,parameter,measured_value,result
2024-01-01 10:00,101,길이,100.2,Pass
```

### Project 3: 예지보전 분석
필수 파일
- `p3_equipment.csv`
- `p3_sensor_log.csv`
- `p3_maintenance_log.csv`

예시:

```csv
timestamp,equipment_id,temperature_celsius,vibration_mms,motor_current_amps
2024-01-01 08:00,1,65.3,4.5,15.2
```

### Project 4: 에너지 분석
필수 파일
- `p4_energy_log.csv`
- `p4_tariff.csv`

예시:

```csv
timestamp,equipment_id,power_kw,production_quantity
2024-01-01 09:00,1,5.2,100
```

### 데이터 입력 규칙
- 인코딩: `UTF-8`
- 파일명: `pX_*.csv`
- 날짜 형식: `YYYY-MM-DD HH:MM:SS`
- 숫자 형식: 소수점 `.` 사용
- 결측치 / 이상치 사전 점검 권장

---

## 실행 방법

### 1. 환경 설정

```bash
cd integrated_project
python --version
pip install -r requirements.txt
```

### 2. 데이터 확인

```bash
ls -la data/raw/
```

### 3. 실행

```bash
# Windows
chcp 65001
python src/main.py

# Mac / Linux
python src/main.py
```

### 4. 결과 확인

실행 후 아래 경로에 결과가 생성됩니다.

- `results/charts/`
- `results/data/`
- `results/reports/`

---

## 설정 예시

`src/config.py`

```python
QUALITY_CPK_THRESHOLD = 1.33
MAINTENANCE_HEALTH_THRESHOLD = 70
ENERGY_TARGET_UNIT = 0.50

OUTPUT_CHART_DIR = "results/charts/"
OUTPUT_DATA_DIR = "results/data/"
OUTPUT_REPORT_DIR = "results/reports/"

FONT_NAME = "Malgun Gothic"
DPI = 100
```

---

## 기술 스택

- **Language**: Python 3.8+
- **Libraries**: pandas, numpy, scipy, matplotlib, seaborn
- **Output**: CSV, PNG, Markdown

---

## 프로젝트 특징

- **모듈 분리 구조**: OEE, 품질, 예지보전, 에너지 분석을 독립 모듈로 구성
- **재사용 가능한 분석 구조**: 로딩, 분석, 시각화, 저장 단계 분리
- **시각화 중심 결과 전달**: 현업 해석에 적합한 대시보드 및 차트 구성
- **통합 관점 분석**: 개별 지표가 아닌 공장 전체 상태를 함께 해석할 수 있도록 설계

---

## 기대 효과

- 병목 설비 및 손실 요인 빠른 식별
- 품질 저하 및 이상 징후 조기 대응
- 에너지 낭비 구간 파악
- 데이터 기반 운영 개선 지원

---

## 향후 개선 방향

- Streamlit 기반 실시간 대시보드 구축
- 이상 탐지 머신러닝 모델 추가
- 웹 기반 리포트 자동화
- 실시간 데이터 연동
- 클라우드 배포

---

## 프로젝트 정보

- 분석 모듈: 4개
- 차트 종류: 8종 이상
- 결과 산출물: PNG, CSV, Markdown
- 평균 분석 시간: 약 1~2분

---

## 한 줄 요약

**스마트팩토리 데이터를 OEE, 품질, 예지보전, 에너지 관점에서 통합 분석하고, 이를 대시보드와 리포트로 시각화한 데이터 분석 포트폴리오 프로젝트입니다.**
