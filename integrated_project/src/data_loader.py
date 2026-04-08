"""
데이터 로더 모듈

4개 프로젝트의 모든 데이터를 로드하고 통합
"""

import pandas as pd
import sys
from pathlib import Path
from typing import Dict

from config import DATA_FILES, ENCODING
from utils import logger, validate_data, preprocess_datetime_columns


class DataLoader:
    """통합 데이터 로더"""
    
    def __init__(self):
        """데이터 로더 초기화"""
        self.data = {}
        self.metadata = {}
    
    def load_all(self) -> Dict[str, pd.DataFrame]:
        """모든 데이터 로드"""
        
        print("\n" + "=" * 70)
        print("데이터 로딩 중...".center(70))
        print("=" * 70)
        
        for key, path in DATA_FILES.items():
            try:
                if not path.exists():
                    logger.warning(f"  × {key:25s} | 파일 없음: {path}")
                    continue
                
                df = pd.read_csv(path, encoding=ENCODING)
                self.data[key] = df
                
                print(f"  ✓ {key:25s} | {len(df):7,} rows × {len(df.columns):2} cols")
            
            except Exception as e:
                logger.error(f"  × {key}: {e}")
        
        print("=" * 70)
        print(f"\n✓ 총 {len(self.data)}개 데이터셋 로드 완료\n")
        
        # 날짜 전처리
        self.data = preprocess_datetime_columns(self.data)
        
        return self.data
    
    def get_data(self, key: str) -> pd.DataFrame:
        """특정 데이터 조회"""
        return self.data.get(key, pd.DataFrame())
    
    def get_oee_data(self) -> Dict[str, pd.DataFrame]:
        """OEE 분석용 데이터"""
        return {
            'equipment': self.get_data('equipment'),
            'production': self.get_data('production'),
            'downtime': self.get_data('downtime')
        }
    
    def get_quality_data(self) -> Dict[str, pd.DataFrame]:
        """품질 분석용 데이터"""
        return {
            'product_spec': self.get_data('product_spec'),
            'inspection': self.get_data('inspection'),
            'defect': self.get_data('defect'),
            'process_params': self.get_data('process_params')
        }
    
    def get_maintenance_data(self) -> Dict[str, pd.DataFrame]:
        """설비 분석용 데이터"""
        return {
            'equipment': self.get_data('equipment_pm'),
            'sensor': self.get_data('sensor'),
            'maintenance': self.get_data('maintenance'),
            'alarm': self.get_data('alarm')
        }
    
    def get_energy_data(self) -> Dict[str, pd.DataFrame]:
        """에너지 분석용 데이터"""
        return {
            'equipment': self.get_data('equipment_energy'),
            'energy': self.get_data('energy'),
            'production': self.get_data('production_energy'),
            'tariff': self.get_data('tariff')
        }
    
    def get_summary_stats(self) -> Dict:
        """데이터 요약 통계"""
        
        stats = {}
        for key, df in self.data.items():
            stats[key] = {
                'rows': len(df),
                'cols': len(df.columns),
                'memory_mb': df.memory_usage(deep=True).sum() / 1024 / 1024
            }
        
        return stats


if __name__ == "__main__":
    loader = DataLoader()
    data = loader.load_all()
    print(f"✓ 로더 준비 완료 ({len(data)}개 데이터)")
