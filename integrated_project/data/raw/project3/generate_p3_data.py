"""
프로젝트 3: 설비관리 - 예지보전 & 센서 이상탐지 데이터 생성
4개 CSV:
  1. p3_equipment.csv     - 설비 마스터 (12대, 누적가동시간·정비주기)
  2. p3_sensor_log.csv    - 센서 시계열 (~12,000건, 시간별)
  3. p3_maintenance_log.csv - 정비/고장 이력 (~350건)
  4. p3_alarm_log.csv     - 알람 기록 (~250건)

스토리:
  - EQ-A03: 3월부터 진동이 서서히 증가 → 4/15 베어링 고장 → 교체 후 정상
  - EQ-C02: 5월 냉각계통 이상 → 온도 상승 패턴 → 5/20 과열 정지
  - EQ-B01: 모범 설비, 예방정비 잘 지켜서 고장 없음
  - 고장 전 7일간 센서 이상 징후가 존재 (vibration↑, temperature↑)
  - 예방정비 후 센서값 정상화 패턴
  - 야간에 냉각 효율 저하 → 온도 약간 높음
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

np.random.seed(2025)
random.seed(2025)

# =============================================
# 1. 설비 마스터
# =============================================
equipment_data = {
    'equipment_id': [f'EQ-{line}{str(i).zfill(2)}' for line in ['A','B','C'] for i in range(1,5)],
    'equipment_name': [
        'CNC선반-A1','CNC선반-A2','밀링머신-A3','드릴프레스-A4',
        'CNC선반-B1','CNC선반-B2','밀링머신-B3','드릴프레스-B4',
        'CNC선반-C1','CNC선반-C2','밀링머신-C3','드릴프레스-C4'
    ],
    'line': ['A라인']*4 + ['B라인']*4 + ['C라인']*4,
    'equipment_type': ['CNC선반','CNC선반','밀링머신','드릴프레스']*3,
    'install_date': [
        '2018-03-15','2018-06-20','2019-01-10','2019-04-05',
        '2021-07-01','2021-09-15','2022-02-10','2022-05-20',
        '2020-01-15','2020-04-10','2020-08-25','2020-11-30'
    ],
    'cumulative_hours': [
        12500, 12100, 10800, 10200,
        5800, 5500, 4200, 3900,
        8500, 8200, 7100, 6800
    ],
    'pm_cycle_days': [90, 90, 60, 120, 90, 90, 60, 120, 90, 90, 60, 120],
    'last_pm_date': [
        '2024-01-15','2024-02-01','2024-01-20','2023-12-10',
        '2024-02-15','2024-02-20','2024-03-01','2024-01-25',
        '2024-01-10','2024-02-05','2024-02-10','2024-01-05'
    ],
    'criticality': ['A','B','A','C','B','B','A','C','B','A','B','C'],
}
equipment = pd.DataFrame(equipment_data)

# =============================================
# 2. 센서 시계열 데이터
# =============================================
# 시간별 데이터, 2024-01-01 ~ 2024-06-30, 매 2시간
date_range = pd.date_range('2024-01-01', '2024-06-30 23:00', freq='2H')
equip_ids = equipment['equipment_id'].tolist()

sensor_records = []
sensor_id = 1

# 설비별 기본 센서 프로파일
base_profiles = {
    'EQ-A01': {'temp': 42, 'vib': 2.5, 'current': 15, 'pressure': 5.0},
    'EQ-A02': {'temp': 41, 'vib': 2.3, 'current': 14.5, 'pressure': 5.0},
    'EQ-A03': {'temp': 44, 'vib': 3.0, 'current': 16, 'pressure': 4.8},  # 노후
    'EQ-A04': {'temp': 40, 'vib': 1.8, 'current': 12, 'pressure': 5.2},
    'EQ-B01': {'temp': 36, 'vib': 1.2, 'current': 13, 'pressure': 5.5},  # 모범
    'EQ-B02': {'temp': 37, 'vib': 1.3, 'current': 13.5, 'pressure': 5.4},
    'EQ-B03': {'temp': 38, 'vib': 1.5, 'current': 14, 'pressure': 5.3},
    'EQ-B04': {'temp': 36, 'vib': 1.1, 'current': 11, 'pressure': 5.5},
    'EQ-C01': {'temp': 39, 'vib': 1.8, 'current': 14, 'pressure': 5.1},
    'EQ-C02': {'temp': 40, 'vib': 2.0, 'current': 14.5, 'pressure': 5.0},  # 5월 이상
    'EQ-C03': {'temp': 39, 'vib': 1.7, 'current': 14, 'pressure': 5.2},
    'EQ-C04': {'temp': 38, 'vib': 1.5, 'current': 12, 'pressure': 5.3},
}

# 고장 이벤트 정의 (설비별 날짜)
failure_events = {
    'EQ-A03': [
        {'failure_date': pd.Timestamp('2024-04-15'), 'ramp_days': 10,
         'sensor': 'vibration', 'ramp_amount': 4.0, 'temp_ramp': 8},
    ],
    'EQ-C02': [
        {'failure_date': pd.Timestamp('2024-05-20'), 'ramp_days': 7,
         'sensor': 'temperature', 'ramp_amount': 15, 'vib_ramp': 1.5},
    ],
    'EQ-A01': [
        {'failure_date': pd.Timestamp('2024-03-10'), 'ramp_days': 5,
         'sensor': 'current', 'ramp_amount': 8, 'temp_ramp': 5},
    ],
}

# 예방정비 이벤트 (정비 후 센서값 개선)
pm_events = {
    'EQ-A03': [pd.Timestamp('2024-01-20'), pd.Timestamp('2024-04-18')],  # 고장 후 수리
    'EQ-B01': [pd.Timestamp('2024-02-15'), pd.Timestamp('2024-05-15')],
    'EQ-C02': [pd.Timestamp('2024-02-10'), pd.Timestamp('2024-05-22')],  # 고장 후 수리
    'EQ-A01': [pd.Timestamp('2024-01-15'), pd.Timestamp('2024-03-12')],  # 고장 후 수리
}

for ts in date_range:
    hour = ts.hour
    month = ts.month
    day_of_year = ts.dayofyear

    # 야간(22~06) 온도 보정
    night_temp_adj = 1.5 if (hour >= 22 or hour <= 6) else 0

    # 일요일 비가동 (센서값 없음 → 건너뜀)
    if ts.weekday() == 6:
        continue

    for eq_id in equip_ids:
        profile = base_profiles[eq_id]

        # 10% 확률로 미가동 (센서 기록 없음)
        if np.random.random() < 0.03:
            continue

        base_temp = profile['temp']
        base_vib = profile['vib']
        base_current = profile['current']
        base_pressure = profile['pressure']

        # 계절 효과: 여름(6월) 온도 +2
        seasonal_temp = 2.0 if month >= 5 else 0

        # 노후 설비 트렌드: 누적가동시간에 따른 점진적 열화
        line = eq_id.split('-')[1][0]
        if line == 'A':
            aging_vib = 0.001 * day_of_year  # 서서히 증가
            aging_temp = 0.003 * day_of_year
        elif line == 'C':
            aging_vib = 0.0005 * day_of_year
            aging_temp = 0.002 * day_of_year
        else:
            aging_vib = 0.0001 * day_of_year
            aging_temp = 0.001 * day_of_year

        # 고장 전 램프업 패턴
        failure_vib_add = 0
        failure_temp_add = 0
        failure_current_add = 0
        is_down = False

        if eq_id in failure_events:
            for event in failure_events[eq_id]:
                fd = event['failure_date']
                ramp_days = event['ramp_days']
                ramp_start = fd - timedelta(days=ramp_days)

                # 고장 당일~+2일: 설비 정지 (데이터 없음)
                if fd <= ts <= fd + timedelta(days=2):
                    is_down = True
                    break

                # 램프업 구간: 서서히 악화
                if ramp_start <= ts < fd:
                    progress = (ts - ramp_start).total_seconds() / (ramp_days * 86400)
                    progress = min(progress, 1.0)
                    # 지수적 증가
                    ramp_factor = progress ** 2

                    if event['sensor'] == 'vibration':
                        failure_vib_add = event['ramp_amount'] * ramp_factor
                        failure_temp_add = event.get('temp_ramp', 0) * ramp_factor * 0.5
                    elif event['sensor'] == 'temperature':
                        failure_temp_add = event['ramp_amount'] * ramp_factor
                        failure_vib_add = event.get('vib_ramp', 0) * ramp_factor * 0.5
                    elif event['sensor'] == 'current':
                        failure_current_add = event['ramp_amount'] * ramp_factor
                        failure_temp_add = event.get('temp_ramp', 0) * ramp_factor * 0.5

        if is_down:
            continue

        # 예방정비 후 개선 효과 (정비 후 2주간 센서값 개선)
        pm_improve_vib = 0
        pm_improve_temp = 0
        if eq_id in pm_events:
            for pm_date in pm_events[eq_id]:
                if pm_date <= ts <= pm_date + timedelta(days=14):
                    days_after = (ts - pm_date).days
                    improve = max(0, 1 - days_after / 14)
                    pm_improve_vib = -0.5 * improve
                    pm_improve_temp = -2 * improve

        # 최종 센서값 계산
        temperature = (base_temp + seasonal_temp + night_temp_adj + aging_temp
                      + failure_temp_add + pm_improve_temp
                      + np.random.normal(0, 1.5))

        vibration = max(0.1, base_vib + aging_vib + failure_vib_add + pm_improve_vib
                       + np.random.normal(0, 0.3))

        current = max(5, base_current + failure_current_add + np.random.normal(0, 1.0))

        pressure = max(2, base_pressure + np.random.normal(0, 0.2))

        # 이상치 (0.5%)
        if np.random.random() < 0.005:
            vibration += np.random.uniform(3, 8)
        if np.random.random() < 0.005:
            temperature += np.random.uniform(10, 20)

        # NaN (2% 온도, 3% 진동, 1% 전류)
        temp_val = round(temperature, 1) if np.random.random() > 0.02 else np.nan
        vib_val = round(vibration, 2) if np.random.random() > 0.03 else np.nan
        curr_val = round(current, 1) if np.random.random() > 0.01 else np.nan
        press_val = round(pressure, 2) if np.random.random() > 0.01 else np.nan

        sensor_records.append({
            'sensor_id': f'S-{sensor_id:06d}',
            'timestamp': ts.strftime('%Y-%m-%d %H:%M'),
            'equipment_id': eq_id,
            'temperature_c': temp_val,
            'vibration_mms': vib_val,
            'current_a': curr_val,
            'pressure_bar': press_val,
        })
        sensor_id += 1

sensor_log = pd.DataFrame(sensor_records)

# =============================================
# 3. 정비/고장 이력
# =============================================
maint_types = {
    'PM': {'desc': '예방정비', 'duration_range': (2, 8), 'cost_range': (50, 300)},
    'CM': {'desc': '고장수리', 'duration_range': (4, 48), 'cost_range': (200, 2000)},
    'BM': {'desc': '사후보전', 'duration_range': (1, 4), 'cost_range': (30, 150)},
    'INS': {'desc': '점검', 'duration_range': (1, 2), 'cost_range': (10, 50)},
}

maint_causes = {
    'CM': ['베어링마모', '모터과열', '유압누유', '기어손상', '센서고장', '전기접촉불량', '스핀들이상', '냉각계통이상'],
    'PM': ['정기점검', '오일교환', '필터교환', '벨트교환', '베어링교환', '냉각수교환'],
    'BM': ['소모품교체', '볼트조임', '청소', '윤활'],
    'INS': ['일상점검', '진동측정', '온도측정', '전류측정'],
}

maint_records = []
maint_id = 1
date_range_days = pd.date_range('2024-01-01', '2024-06-30', freq='D')

for date in date_range_days:
    if date.weekday() == 6:
        continue

    for eq_id in equip_ids:
        line = eq_id.split('-')[1][0]

        # 고장 수리 (failure_events와 연동)
        if eq_id in failure_events:
            for event in failure_events[eq_id]:
                if date.date() == event['failure_date'].date():
                    cause = random.choice(['베어링마모', '모터과열', '스핀들이상', '냉각계통이상'])
                    duration = np.random.randint(8, 48)
                    cost = np.random.randint(500, 2500)
                    maint_records.append({
                        'maintenance_id': f'MT-{maint_id:05d}',
                        'date': date.strftime('%Y-%m-%d'),
                        'equipment_id': eq_id,
                        'maintenance_type': 'CM',
                        'description': f'고장수리 - {cause}',
                        'cause': cause,
                        'duration_hours': duration,
                        'cost_won': cost * 1000,
                        'parts_replaced': random.choice(['베어링', '모터', '씰', '기어', '센서', '냉각펌프']),
                        'technician_id': f'TECH-{random.randint(1,8):02d}',
                    })
                    maint_id += 1

        # 예방정비
        if eq_id in pm_events:
            for pm_date in pm_events[eq_id]:
                if date.date() == pm_date.date():
                    cause = random.choice(maint_causes['PM'])
                    duration = np.random.randint(2, 8)
                    cost = np.random.randint(50, 400)
                    maint_records.append({
                        'maintenance_id': f'MT-{maint_id:05d}',
                        'date': date.strftime('%Y-%m-%d'),
                        'equipment_id': eq_id,
                        'maintenance_type': 'PM',
                        'description': f'예방정비 - {cause}',
                        'cause': cause,
                        'duration_hours': duration,
                        'cost_won': cost * 1000,
                        'parts_replaced': random.choice(['오일', '필터', '벨트', '베어링', '냉각수', np.nan]),
                        'technician_id': f'TECH-{random.randint(1,8):02d}',
                    })
                    maint_id += 1

        # 주기적 PM (pm_cycle_days 기준)
        eq_row = equipment[equipment['equipment_id'] == eq_id].iloc[0]
        pm_cycle = eq_row['pm_cycle_days']
        last_pm = pd.Timestamp(eq_row['last_pm_date'])
        days_since = (date - last_pm).days
        if days_since > 0 and days_since % pm_cycle == 0:
            cause = random.choice(maint_causes['PM'])
            duration = np.random.randint(2, 8)
            cost = np.random.randint(80, 400)
            maint_records.append({
                'maintenance_id': f'MT-{maint_id:05d}',
                'date': date.strftime('%Y-%m-%d'),
                'equipment_id': eq_id,
                'maintenance_type': 'PM',
                'description': f'정기 예방정비 - {cause}',
                'cause': cause,
                'duration_hours': duration,
                'cost_won': cost * 1000,
                'parts_replaced': random.choice(['오일', '필터', '벨트', '베어링', '냉각수']),
                'technician_id': f'TECH-{random.randint(1,8):02d}',
            })
            maint_id += 1

        # 주간 점검 (매주 월요일)
        if date.weekday() == 0 and np.random.random() < 0.5:
            cause = random.choice(maint_causes['INS'])
            maint_records.append({
                'maintenance_id': f'MT-{maint_id:05d}',
                'date': date.strftime('%Y-%m-%d'),
                'equipment_id': eq_id,
                'maintenance_type': 'INS',
                'description': f'주간점검 - {cause}',
                'cause': cause,
                'duration_hours': np.random.randint(1, 3),
                'cost_won': np.random.randint(10, 50) * 1000,
                'parts_replaced': np.nan,
                'technician_id': f'TECH-{random.randint(1,8):02d}',
            })
            maint_id += 1

        # 랜덤 정비 이벤트 (고장/사후보전)
        rand = np.random.random()
        if line == 'A' and rand < 0.03:
            mtype = random.choices(['CM', 'BM'], weights=[0.4, 0.6], k=1)[0]
        elif line == 'B' and rand < 0.012:
            mtype = random.choices(['CM', 'BM'], weights=[0.2, 0.8], k=1)[0]
        elif line == 'C' and rand < 0.02:
            mtype = random.choices(['CM', 'BM'], weights=[0.3, 0.7], k=1)[0]
        else:
            continue

        info = maint_types[mtype]
        cause = random.choice(maint_causes[mtype])
        duration = np.random.randint(*info['duration_range'])
        cost = np.random.randint(*info['cost_range'])

        # NaN (cause 5%, parts 10%)
        cause_val = cause if np.random.random() > 0.05 else np.nan
        parts = random.choice(['오일', '필터', '벨트', '베어링', '볼트', '씰', np.nan])

        maint_records.append({
            'maintenance_id': f'MT-{maint_id:05d}',
            'date': date.strftime('%Y-%m-%d'),
            'equipment_id': eq_id,
            'maintenance_type': mtype,
            'description': f'{info["desc"]} - {cause}',
            'cause': cause_val,
            'duration_hours': duration if np.random.random() > 0.03 else np.nan,
            'cost_won': cost * 1000,
            'parts_replaced': parts,
            'technician_id': f'TECH-{random.randint(1,8):02d}',
        })
        maint_id += 1

maintenance_log = pd.DataFrame(maint_records)

# =============================================
# 4. 알람 기록
# =============================================
alarm_types = {
    'HIGH_TEMP': {'threshold': 55, 'severity': '경고'},
    'HIGH_VIBRATION': {'threshold': 5.0, 'severity': '경고'},
    'HIGH_CURRENT': {'threshold': 22, 'severity': '경고'},
    'CRITICAL_TEMP': {'threshold': 65, 'severity': '위험'},
    'CRITICAL_VIBRATION': {'threshold': 8.0, 'severity': '위험'},
    'LOW_PRESSURE': {'threshold': 3.5, 'severity': '경고'},
    'EMERGENCY_STOP': {'threshold': None, 'severity': '긴급'},
}

alarm_records = []
alarm_id = 1

# 센서 데이터에서 알람 조건 체크
for _, row in sensor_log.iterrows():
    eq_id = row['equipment_id']

    # 온도 알람
    if pd.notna(row['temperature_c']):
        if row['temperature_c'] >= 65:
            alarm_records.append({
                'alarm_id': f'ALM-{alarm_id:05d}',
                'timestamp': row['timestamp'],
                'equipment_id': eq_id,
                'alarm_type': 'CRITICAL_TEMP',
                'alarm_value': row['temperature_c'],
                'threshold': 65,
                'severity': '위험',
                'acknowledged': random.choice([True, True, False]),
                'resolved': random.choice([True, True, False]),
            })
            alarm_id += 1
        elif row['temperature_c'] >= 55:
            if np.random.random() < 0.8:  # 80% 기록
                alarm_records.append({
                    'alarm_id': f'ALM-{alarm_id:05d}',
                    'timestamp': row['timestamp'],
                    'equipment_id': eq_id,
                    'alarm_type': 'HIGH_TEMP',
                    'alarm_value': row['temperature_c'],
                    'threshold': 55,
                    'severity': '경고',
                    'acknowledged': random.choice([True, True, True, False]),
                    'resolved': random.choice([True, True, False]),
                })
                alarm_id += 1

    # 진동 알람
    if pd.notna(row['vibration_mms']):
        if row['vibration_mms'] >= 8.0:
            alarm_records.append({
                'alarm_id': f'ALM-{alarm_id:05d}',
                'timestamp': row['timestamp'],
                'equipment_id': eq_id,
                'alarm_type': 'CRITICAL_VIBRATION',
                'alarm_value': row['vibration_mms'],
                'threshold': 8.0,
                'severity': '위험',
                'acknowledged': random.choice([True, False]),
                'resolved': random.choice([True, False]),
            })
            alarm_id += 1
        elif row['vibration_mms'] >= 5.0:
            if np.random.random() < 0.7:
                alarm_records.append({
                    'alarm_id': f'ALM-{alarm_id:05d}',
                    'timestamp': row['timestamp'],
                    'equipment_id': eq_id,
                    'alarm_type': 'HIGH_VIBRATION',
                    'alarm_value': row['vibration_mms'],
                    'threshold': 5.0,
                    'severity': '경고',
                    'acknowledged': random.choice([True, True, False]),
                    'resolved': random.choice([True, True, False]),
                })
                alarm_id += 1

    # 전류 알람
    if pd.notna(row['current_a']) and row['current_a'] >= 22:
        if np.random.random() < 0.7:
            alarm_records.append({
                'alarm_id': f'ALM-{alarm_id:05d}',
                'timestamp': row['timestamp'],
                'equipment_id': eq_id,
                'alarm_type': 'HIGH_CURRENT',
                'alarm_value': row['current_a'],
                'threshold': 22,
                'severity': '경고',
                'acknowledged': True,
                'resolved': random.choice([True, False]),
            })
            alarm_id += 1

alarm_log = pd.DataFrame(alarm_records)

# 알람 NaN (acknowledged 3%)
if len(alarm_log) > 0:
    nan_mask = np.random.random(len(alarm_log)) < 0.03
    alarm_log.loc[nan_mask, 'acknowledged'] = np.nan

# =============================================
# 저장
# =============================================
out = '/Users/macro/Documents/GitHub/smart-factory2/data/project3/'
equipment.to_csv(out + 'p3_equipment.csv', index=False, encoding='utf-8-sig')
sensor_log.to_csv(out + 'p3_sensor_log.csv', index=False, encoding='utf-8-sig')
maintenance_log.to_csv(out + 'p3_maintenance_log.csv', index=False, encoding='utf-8-sig')
alarm_log.to_csv(out + 'p3_alarm_log.csv', index=False, encoding='utf-8-sig')

print("="*60)
print("프로젝트 3 데이터 생성 완료!")
print("="*60)
print(f"\n설비 마스터: {len(equipment)}건")
print(f"센서 로그: {len(sensor_log):,}건")
print(f"정비 이력: {len(maintenance_log)}건")
print(f"알람 기록: {len(alarm_log)}건")

print(f"\n--- 센서 NaN ---")
print(sensor_log.isnull().sum()[sensor_log.isnull().sum()>0])
print(f"\n--- 정비 NaN ---")
print(maintenance_log.isnull().sum()[maintenance_log.isnull().sum()>0])

print(f"\n--- 정비 유형별 건수 ---")
print(maintenance_log['maintenance_type'].value_counts())
print(f"\n--- 알람 유형별 건수 ---")
print(alarm_log['alarm_type'].value_counts() if len(alarm_log) > 0 else 'None')

# 스토리 검증: EQ-A03 진동 추이
eq_a03 = sensor_log[sensor_log['equipment_id']=='EQ-A03'].copy()
eq_a03['ts'] = pd.to_datetime(eq_a03['timestamp'])
eq_a03['month'] = eq_a03['ts'].dt.month
print(f"\n--- EQ-A03 월별 평균 진동 (고장 전 증가 확인) ---")
print(eq_a03.groupby('month')['vibration_mms'].mean())

# EQ-C02 온도 추이
eq_c02 = sensor_log[sensor_log['equipment_id']=='EQ-C02'].copy()
eq_c02['ts'] = pd.to_datetime(eq_c02['timestamp'])
eq_c02['month'] = eq_c02['ts'].dt.month
print(f"\n--- EQ-C02 월별 평균 온도 (5월 이상 확인) ---")
print(eq_c02.groupby('month')['temperature_c'].mean())
