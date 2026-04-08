"""
프로젝트 4: 에너지관리 - 에너지 원단위 & 효율 분석 데이터 생성
4개 CSV:
  1. p4_equipment.csv     - 설비 에너지 프로파일 (12대)
  2. p4_energy_log.csv    - 시간별 전력 사용 로그 (~15,000건)
  3. p4_production_log.csv - 일별 생산 실적 (~2,000건)
  4. p4_tariff.csv        - 전기 요금 단가표 (TOU: Time of Use)

스토리:
  - A라인: 노후 설비, 인버터 없음, 대기전력 높음 → 에너지 비효율
  - B라인: 신규 설비, 인버터 있음, 절전모드 → 에너지 효율적
  - C라인: 중간, 3월에 인버터 도입 → 에너지 효율 개선 확인
  - 여름(5~6월): 냉방 부하로 전력 사용 증가
  - 피크 시간대(10~12, 13~17시): 전력 사용 최대
  - 주말/야간: 대기전력 낭비 → 절감 포인트
  - EQ-A03: 에너지 낭비 최악 (대기전력 높음, 가동 효율 낮음)
"""

import pandas as pd
import numpy as np
import random

np.random.seed(2025)
random.seed(2025)

OUT_DIR = '/Users/macro/Documents/GitHub/smart-factory2/data/project4/'

# =============================================
# 1. 설비 에너지 프로파일
# =============================================
equipment_data = {
    'equipment_id': [f'EQ-{line}{str(i).zfill(2)}' for line in ['A','B','C'] for i in range(1,5)],
    'equipment_name': [
        'CNC선반-A1','CNC선반-A2','밀링머신-A3','컴프레서-A4',
        'CNC선반-B1','CNC선반-B2','밀링머신-B3','컴프레서-B4',
        'CNC선반-C1','CNC선반-C2','밀링머신-C3','컴프레서-C4'
    ],
    'line': ['A라인']*4 + ['B라인']*4 + ['C라인']*4,
    'equipment_type': ['CNC선반','CNC선반','밀링머신','컴프레서']*3,
    'rated_power_kw': [
        22, 22, 30, 15,     # A라인: 높은 정격전력
        18, 18, 25, 11,     # B라인: 최적화된 정격전력
        20, 20, 28, 13,     # C라인: 중간
    ],
    'has_inverter': [
        False, False, False, False,  # A라인: 인버터 없음
        True, True, True, True,      # B라인: 인버터 있음
        False, False, False, False,  # C라인: 3월에 도입 (데이터에서 반영)
    ],
    'standby_power_kw': [
        3.5, 3.2, 4.5, 2.8,   # A라인: 대기전력 높음
        0.8, 0.7, 1.2, 0.5,   # B라인: 절전모드
        2.2, 2.0, 3.0, 1.8,   # C라인: 중간 → 3월 이후 감소
    ],
    'energy_grade': [4, 4, 5, 3, 1, 1, 2, 1, 3, 3, 3, 2],  # 1=최고효율, 5=최저
    'install_year': [2016, 2017, 2016, 2018, 2022, 2022, 2023, 2023, 2019, 2019, 2020, 2020],
}

equipment = pd.DataFrame(equipment_data)

# =============================================
# 2. 전기 요금 단가표 (TOU - Time of Use)
# =============================================
# 한전 산업용(을) 기준 간소화
tariff_data = {
    'season': ['춘추계','춘추계','춘추계','하계','하계','하계'],
    'season_months': ['3~5,9~10월','3~5,9~10월','3~5,9~10월','6~8월','6~8월','6~8월'],
    'time_zone': ['경부하','중간부하','최대부하','경부하','중간부하','최대부하'],
    'time_zone_en': ['off-peak','mid-peak','on-peak','off-peak','mid-peak','on-peak'],
    'hours_description': ['23:00~09:00','09:00~10:00,12:00~13:00,17:00~23:00','10:00~12:00,13:00~17:00',
                          '23:00~09:00','09:00~10:00,12:00~13:00,17:00~23:00','10:00~12:00,13:00~17:00'],
    'rate_won_kwh': [60, 85, 120, 65, 105, 150],
}
tariff = pd.DataFrame(tariff_data)

# 시간대별 요금 매핑 함수
def get_tariff_rate(month, hour):
    """월과 시간으로 요금 단가 반환"""
    if month in [6, 7, 8]:  # 하계
        if 23 <= hour or hour < 9:
            return 65   # 경부하
        elif (9 <= hour < 10) or (12 <= hour < 13) or (17 <= hour < 23):
            return 105  # 중간부하
        else:  # 10~12, 13~17
            return 150  # 최대부하
    else:  # 춘추계 (1~5, 9~12)
        if 23 <= hour or hour < 9:
            return 60
        elif (9 <= hour < 10) or (12 <= hour < 13) or (17 <= hour < 23):
            return 85
        else:
            return 120

# =============================================
# 3. 시간별 에너지 사용 로그
# =============================================
date_range = pd.date_range('2024-01-01', '2024-06-30 23:00', freq='h')
equip_ids = equipment['equipment_id'].tolist()

energy_records = []
energy_id = 1

for ts in date_range:
    hour = ts.hour
    month = ts.month
    weekday = ts.weekday()  # 0=월, 6=일
    day_of_year = ts.dayofyear

    # 외기온도 (계절 + 시간 패턴)
    base_temp = 2 + month * 3.5  # 1월 5.5°C → 6월 23.5°C
    daily_variation = 5 * np.sin(np.pi * (hour - 6) / 12) if 6 <= hour <= 18 else -3
    ambient_temp = base_temp + daily_variation + np.random.normal(0, 2)

    for eq_id in equip_ids:
        eq_row = equipment[equipment['equipment_id'] == eq_id].iloc[0]
        rated_power = eq_row['rated_power_kw']
        standby_power = eq_row['standby_power_kw']
        has_inv = eq_row['has_inverter']
        line = eq_row['line']

        # C라인 3월 이후 인버터 도입 효과
        c_inverter_effect = False
        if line == 'C라인' and month >= 3:
            c_inverter_effect = True

        # 가동 여부 결정
        if weekday == 6:  # 일요일: 비가동
            is_operating = False
        elif weekday == 5:  # 토요일: 30% 확률 가동
            is_operating = np.random.random() < 0.30
        elif hour < 6 or hour >= 22:  # 야간(22~06): 20% 확률 가동
            is_operating = np.random.random() < 0.20
        else:  # 주간: 높은 가동률
            if line == 'A라인':
                is_operating = np.random.random() < 0.82
            elif line == 'B라인':
                is_operating = np.random.random() < 0.90
            else:
                is_operating = np.random.random() < 0.85

        # 전력 사용량 계산
        if is_operating:
            # 기본 가동 전력 (정격의 60~85%)
            if has_inv or c_inverter_effect:
                # 인버터 있으면 부하 최적화 → 정격의 55~75%
                load_factor = np.random.uniform(0.55, 0.75)
            else:
                # 인버터 없으면 일정 부하 → 정격의 65~90%
                load_factor = np.random.uniform(0.65, 0.90)

            # 피크 시간대 부하 증가
            if 10 <= hour <= 11 or 13 <= hour <= 16:
                load_factor += 0.05

            # 노후 효율 손실 (A라인)
            if line == 'A라인':
                load_factor += 0.05  # 노후 설비 비효율

            power_kwh = rated_power * load_factor

        else:
            # 비가동 시: 대기전력
            if c_inverter_effect:
                # C라인 3월 이후 절전모드 → 대기전력 50% 감소
                power_kwh = standby_power * 0.5 + np.random.normal(0, 0.1)
            elif has_inv:
                # B라인: 절전모드
                power_kwh = standby_power + np.random.normal(0, 0.05)
            else:
                # A라인: 대기전력 그대로
                power_kwh = standby_power + np.random.normal(0, 0.15)

        # 냉방 부하 (여름, 외기온도 25°C 이상)
        if ambient_temp > 25:
            cooling_load = (ambient_temp - 25) * 0.3  # 온도 1°C당 0.3kWh
            power_kwh += cooling_load

        # EQ-A03 특별 비효율 (밀링머신, 에너지등급 5)
        if eq_id == 'EQ-A03':
            power_kwh *= 1.10  # 10% 추가 비효율

        # 노이즈
        power_kwh += np.random.normal(0, 0.5)
        power_kwh = max(0.1, power_kwh)

        # 이상치 (0.5%)
        if np.random.random() < 0.005:
            power_kwh *= np.random.uniform(1.5, 2.5)

        # NaN (3%)
        power_val = round(power_kwh, 2) if np.random.random() > 0.03 else np.nan
        temp_val = round(ambient_temp, 1) if np.random.random() > 0.02 else np.nan

        energy_records.append({
            'energy_id': f'E-{energy_id:06d}',
            'timestamp': ts.strftime('%Y-%m-%d %H:%M'),
            'equipment_id': eq_id,
            'power_kwh': power_val,
            'is_operating': is_operating,
            'ambient_temp_c': temp_val,
        })
        energy_id += 1

energy_log = pd.DataFrame(energy_records)

# =============================================
# 4. 일별 생산 실적
# =============================================
products = ['PRD-001', 'PRD-002', 'PRD-003', 'PRD-004', 'PRD-005', 'PRD-006']
product_cycle_times = {
    'PRD-001': 180, 'PRD-002': 240, 'PRD-003': 120,
    'PRD-004': 300, 'PRD-005': 150, 'PRD-006': 200,
}

prod_records = []
prod_id = 1
date_range_days = pd.date_range('2024-01-01', '2024-06-30', freq='D')

for date in date_range_days:
    weekday = date.weekday()
    month = date.month

    if weekday == 6:  # 일요일 비가동
        continue

    for eq_id in equip_ids:
        eq_row = equipment[equipment['equipment_id'] == eq_id].iloc[0]
        line = eq_row['line']
        eq_type = eq_row['equipment_type']

        # 컴프레서는 생산 직접 안 함 (지원 설비)
        if eq_type == '컴프레서':
            continue

        # 토요일 50% 확률 비가동
        if weekday == 5 and np.random.random() < 0.50:
            continue

        # 제품 배정 (설비 타입에 따라)
        if eq_type == 'CNC선반':
            product = random.choice(['PRD-001', 'PRD-002', 'PRD-004'])
        else:  # 밀링머신
            product = random.choice(['PRD-003', 'PRD-005', 'PRD-006'])

        cycle_time = product_cycle_times[product]

        # 가동 시간 (라인별 차이)
        if line == 'A라인':
            operating_hours = np.random.uniform(12, 16)
        elif line == 'B라인':
            operating_hours = np.random.uniform(14, 18)
        else:
            operating_hours = np.random.uniform(13, 17)

        # 토요일 가동시간 감소
        if weekday == 5:
            operating_hours *= 0.5

        # 생산량 = 가동시간(초) / 사이클타임
        production_qty = int(operating_hours * 3600 / cycle_time * np.random.uniform(0.85, 1.0))
        production_qty = max(1, production_qty)

        # 불량
        if line == 'A라인':
            defect_rate = np.random.uniform(0.02, 0.06)
        elif line == 'B라인':
            defect_rate = np.random.uniform(0.005, 0.02)
        else:
            defect_rate = np.random.uniform(0.01, 0.035)

        defect_qty = int(production_qty * defect_rate)

        # NaN (operating_hours 2%, production_qty 1%)
        op_hours_val = round(operating_hours, 1) if np.random.random() > 0.02 else np.nan
        prod_qty_val = production_qty if np.random.random() > 0.01 else np.nan

        prod_records.append({
            'prod_id': f'P-{prod_id:05d}',
            'date': date.strftime('%Y-%m-%d'),
            'equipment_id': eq_id,
            'product_code': product,
            'production_qty': prod_qty_val,
            'operating_hours': op_hours_val,
            'defect_qty': defect_qty,
        })
        prod_id += 1

production_log = pd.DataFrame(prod_records)

# =============================================
# 저장
# =============================================
equipment.to_csv(OUT_DIR + 'p4_equipment.csv', index=False, encoding='utf-8-sig')
energy_log.to_csv(OUT_DIR + 'p4_energy_log.csv', index=False, encoding='utf-8-sig')
production_log.to_csv(OUT_DIR + 'p4_production_log.csv', index=False, encoding='utf-8-sig')
tariff.to_csv(OUT_DIR + 'p4_tariff.csv', index=False, encoding='utf-8-sig')

print("="*60)
print("프로젝트 4 데이터 생성 완료!")
print("="*60)
print(f"\n설비 프로파일: {len(equipment)}건")
print(f"에너지 로그: {len(energy_log):,}건")
print(f"생산 실적: {len(production_log):,}건")
print(f"요금 단가: {len(tariff)}건")

print(f"\n--- 에너지 로그 NaN ---")
print(energy_log.isnull().sum()[energy_log.isnull().sum()>0])
print(f"\n--- 생산 실적 NaN ---")
print(production_log.isnull().sum()[production_log.isnull().sum()>0])

# 검증: 라인별 평균 전력
energy_log['power_kwh_num'] = pd.to_numeric(energy_log['power_kwh'], errors='coerce')
energy_log['line'] = energy_log['equipment_id'].str.extract(r'EQ-(\w)')[0].map(
    {'A': 'A라인', 'B': 'B라인', 'C': 'C라인'}
)
print(f"\n--- 라인별 평균 전력 (kWh/h) ---")
print(energy_log.groupby('line')['power_kwh_num'].mean().round(2))

# 검증: 가동 vs 비가동 전력 비교
print(f"\n--- 가동/비가동 평균 전력 ---")
print(energy_log.groupby(['line', 'is_operating'])['power_kwh_num'].mean().round(2))

# 검증: C라인 월별 전력 (3월 이후 개선 확인)
c_line = energy_log[energy_log['line'] == 'C라인'].copy()
c_line['month'] = pd.to_datetime(c_line['timestamp']).dt.month
print(f"\n--- C라인 월별 평균 전력 (3월 이후 개선 확인) ---")
print(c_line.groupby('month')['power_kwh_num'].mean().round(2))

# 검증: 설비별 비가동 대기전력
standby = energy_log[energy_log['is_operating'] == False]
print(f"\n--- 설비별 비가동 시 평균 전력 (대기전력) ---")
print(standby.groupby('equipment_id')['power_kwh_num'].mean().round(2))
