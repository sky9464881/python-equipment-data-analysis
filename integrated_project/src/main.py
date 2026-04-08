"""
통합 팩토리 분석 프로젝트 - 메인 실행 스크립트

4개 프로젝트(OEE, 품질, 설비, 에너지)의 통합 분석
"""

import sys
from pathlib import Path

# 경로 설정
PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR = PROJECT_ROOT / 'src'
sys.path.insert(0, str(SRC_DIR))

import pandas as pd
from typing import Dict

from config import *
from utils import setup_environment, initialize_project, print_section, save_dataframe, logger
from data_loader import DataLoader
from analyzers.oee_analyzer import OEEAnalyzer
from analyzers.quality_analyzer import QualityAnalyzer
from analyzers.maintenance_analyzer import MaintenanceAnalyzer
from analyzers.energy_analyzer import EnergyAnalyzer
from visualizers.integrated_visualizer import IntegratedVisualizer


# ============================================
# 메인 분석 파이프라인
# ============================================

def run_oee_analysis(data: Dict[str, pd.DataFrame]) -> Dict:
    """OEE 분석 실행"""
    
    print_section("프로젝트 1: OEE 분석", 2)
    
    try:
        equip = data.get('equipment')
        prod = data.get('production')
        downtime = data.get('downtime')
        
        if equip is None or prod is None:
            logger.error("필수 데이터 없음")
            return {}
        
        # 분석기 생성
        analyzer = OEEAnalyzer(prod, equip, downtime)
        results = analyzer.run_full_analysis()
        
        # 결과 저장
        if 'by_equipment' in results:
            save_dataframe(results['by_equipment'], '01_equipment_oee')
        if 'by_line' in results:
            save_dataframe(results['by_line'], '02_line_oee')
        if 'six_big_losses' in results:
            save_dataframe(results['six_big_losses'], '03_six_big_losses')
        if 'by_period' in results:
            save_dataframe(results['by_period'], '04_period_oee')
        
        return results
    
    except Exception as e:
        logger.error(f"OEE 분석 실패: {e}")
        import traceback
        traceback.print_exc()
        return {}


def run_quality_analysis(data: Dict[str, pd.DataFrame]) -> Dict:
    """품질 분석 - SPC 및 공정능력 분석"""
    
    print_section("프로젝트 2: 품질관리 분석 (SPC)", 2)
    
    try:
        inspection = data.get('inspection')
        defect = data.get('defect')
        product_spec = data.get('product_spec')
        
        if inspection is None or len(inspection) == 0:
            logger.warning("검사 데이터 없음")
            return {}
        
        # 품질 분석기 생성
        analyzer = QualityAnalyzer(inspection, defect, product_spec)
        results = analyzer.run_full_analysis()
        
        # 결과 저장
        if 'basic_metrics' in results:
            save_dataframe(pd.DataFrame([results['basic_metrics']]), '02_quality_metrics')
        
        if 'defect_analysis' in results and isinstance(results['defect_analysis'], pd.DataFrame):
            save_dataframe(results['defect_analysis'], '02_defect_pareto')
        
        if 'quality_trend' in results and isinstance(results['quality_trend'], pd.DataFrame):
            save_dataframe(results['quality_trend'], '02_quality_trend')
        
        return results
    
    except Exception as e:
        logger.error(f"품질 분석 실패: {e}")
        import traceback
        traceback.print_exc()
        return {}


def run_maintenance_analysis(data: Dict[str, pd.DataFrame]) -> Dict:
    """설비 분석 - 이상탐지 및 건강도"""
    
    print_section("프로젝트 3: 설비관리 및 예지보전 분석", 2)
    
    try:
        sensor = data.get('sensor')
        maintenance = data.get('maintenance')
        equipment = data.get('equipment')
        alarm = data.get('alarm')
        
        if sensor is None or len(sensor) == 0:
            logger.warning("센서 데이터 없음")
            return {}
        
        # 설비 분석기 생성
        analyzer = MaintenanceAnalyzer(sensor, maintenance, equipment, alarm)
        results = analyzer.run_full_analysis()
        
        # 결과 저장
        if 'maintenance_analysis' in results and isinstance(results['maintenance_analysis'], pd.DataFrame):
            save_dataframe(results['maintenance_analysis'], '03_maintenance_history')
        
        if 'anomalies' in results:
            anom_df = pd.DataFrame([results['anomalies']])
            save_dataframe(anom_df, '03_anomalies_detected')
        
        return results
    
    except Exception as e:
        logger.error(f"설비 분석 실패: {e}")
        import traceback
        traceback.print_exc()
        return {}


def run_energy_analysis(data: Dict[str, pd.DataFrame]) -> Dict:
    """에너지 분석 - 효율성 및 절감 기회"""
    
    print_section("프로젝트 4: 에너지관리 및 효율성 분석", 2)
    
    try:
        energy = data.get('energy')
        production = data.get('production')
        
        if energy is None or len(energy) == 0:
            logger.warning("에너지 데이터 없음")
            return {}
        
        # 에너지 분석기 생성
        analyzer = EnergyAnalyzer(energy, production)
        results = analyzer.run_full_analysis()
        
        # 결과 저장
        if 'consumption' in results:
            cons_df = pd.DataFrame([results['consumption']])
            save_dataframe(cons_df, '04_energy_consumption')
        
        if 'energy_by_process' in results and isinstance(results['energy_by_process'], pd.DataFrame):
            save_dataframe(results['energy_by_process'], '04_energy_by_process')
        
        if 'savings_opportunities' in results:
            opps_df = pd.DataFrame([results['savings_opportunities']])
            save_dataframe(opps_df, '04_savings_opportunities')
        
        return results
    
    except Exception as e:
        logger.error(f"에너지 분석 실패: {e}")
        import traceback
        traceback.print_exc()
        return {}


# ============================================
# 통합 분석
# ============================================

def create_integrated_insights(analysis_results: Dict) -> str:
    """통합 인사이트 생성"""
    
    insights = []
    
    insights.append("# 통합 분석 인사이트\n")
    
    # OEE 분석
    if 'oee_results' in analysis_results:
        oee = analysis_results['oee_results'].get('overall', {})
        if oee:
            insights.append(f"## OEE 분석\n")
            insights.append(f"- 종합 OEE: {oee.get('oee', 0):.2f}% (목표: 85%)\n")
            insights.append(f"- 가동률: {oee.get('availability', 0):.2f}%\n")
            insights.append(f"- 성능률: {oee.get('performance', 0):.2f}%\n")
            insights.append(f"- 양품률: {oee.get('quality', 0):.2f}%\n\n")
    
    # 품질 분석
    if 'quality_results' in analysis_results:
        quality = analysis_results['quality_results']
        if quality:
            insights.append(f"## 품질 분석\n")
            insights.append(f"- 합격률: {quality.get('pass_rate', 0):.2f}%\n")
            insights.append(f"- 검사 건수: {quality.get('total_inspections', 0):,}건\n\n")
    
    # 설비 분석
    if 'maintenance_results' in analysis_results:
        insights.append(f"## 설비관리 분석\n")
        insights.append(f"- 각 설비의 정비 기록 구분 분석 필요\n\n")
    
    # 에너지 분석
    if 'energy_results' in analysis_results:
        energy = analysis_results['energy_results']
        if energy:
            insights.append(f"## 에너지 분석\n")
            insights.append(f"- 총 전력 소비: {energy.get('total_kwh', 0):,.0f} kWh\n")
            insights.append(f"- 평균 전력: {energy.get('avg_power_kw', 0):.2f} kW\n")
            insights.append(f"- 최대 전력: {energy.get('peak_power_kw', 0):.2f} kW\n\n")
    
    insights.append("## 권고사항\n")
    insights.append("1. OEE 목표 달성을 위해 비가동 원인 분석 필요\n")
    insights.append("2. 품질 지표 지속 모니터링\n")
    insights.append("3. 에너지 효율 개선 방안 수립\n")
    
    return "".join(insights)


# ============================================
# 메인 실행
# ============================================

def main():
    """메인 분석 파이프라인"""
    
    print("\n" + "█" * 70)
    print("█" + " " * 68 + "█")
    print("█" + "  한국정밀산업(주) 통합 팩토리 분석 시스템".center(68) + "█")
    print("█" + " " * 68 + "█")
    print("█" * 70 + "\n")
    
    try:
        # 1. 초기화
        print_section("초기화", 1)
        setup_environment()
        
        # 2. 데이터 로더
        print_section("데이터 로드", 1)
        loader = DataLoader()
        all_data = loader.load_all()
        
        # 3. 프로젝트별 분석
        print_section("프로젝트별 분석", 1)
        
        analysis_results = {}
        
        # 프로젝트 1: OEE
        oee_data = loader.get_oee_data()
        analysis_results['oee_results'] = run_oee_analysis(oee_data)
        
        # 프로젝트 2: 품질
        quality_data = loader.get_quality_data()
        analysis_results['quality_results'] = run_quality_analysis(quality_data)
        
        # 프로젝트 3: 설비
        maintenance_data = loader.get_maintenance_data()
        analysis_results['maintenance_results'] = run_maintenance_analysis(maintenance_data)
        
        # 프로젝트 4: 에너지
        energy_data = loader.get_energy_data()
        analysis_results['energy_results'] = run_energy_analysis(energy_data)
        
        # 4. 시각화
        print_section("시각화", 1)
        
        visualizer = IntegratedVisualizer()
        
        # OEE 차트들
        if 'oee_results' in analysis_results and 'overall' in analysis_results['oee_results']:
            visualizer.plot_oee_gauge(analysis_results['oee_results']['overall'])
            
            if 'by_equipment' in analysis_results['oee_results']:
                visualizer.plot_equipment_comparison(
                    analysis_results['oee_results']['by_equipment']
                )
            
            if 'by_line' in analysis_results['oee_results']:
                visualizer.plot_line_comparison(
                    analysis_results['oee_results']['by_line']
                )
            
            if 'by_period' in analysis_results['oee_results']:
                visualizer.plot_oee_trend(
                    analysis_results['oee_results']['by_period']
                )
            
            if 'six_big_losses' in analysis_results['oee_results']:
                visualizer.plot_six_big_losses(
                    analysis_results['oee_results']['six_big_losses']
                )
            
            if 'improvement' in analysis_results['oee_results']:
                visualizer.plot_improvement(
                    analysis_results['oee_results']['improvement']
                )
        
        # 통합 대시보드
        dashboard_data = {
            'oee': analysis_results['oee_results'].get('overall', {}),
            'equipment_oee': analysis_results['oee_results'].get('by_equipment', pd.DataFrame()),
            'line_oee': analysis_results['oee_results'].get('by_line', pd.DataFrame()),
            'six_big_losses': analysis_results['oee_results'].get('six_big_losses', pd.DataFrame()),
            'improvement_comparison': analysis_results['oee_results'].get('improvement', None)
        }
        visualizer.create_integrated_dashboard(dashboard_data)
        
        # 모든 차트 저장
        print()
        visualizer.save_all()
        
        # 5. 통합 인사이트 저장
        print_section("통합 인사이트", 1)
        insights = create_integrated_insights(analysis_results)
        print(insights)
        
        from utils import save_report
        save_report(insights, '00_integrated_insights')
        
        # 완료
        print_section("분석 완료", 1)
        
        print(f"📁 결과 경로: {RESULTS_DIR}")
        print(f"📊 생성 파일:\n")
        
        # 결과 파일 나열
        chart_files = list(CHARTS_DIR.glob('*.png'))
        data_files = list(RESULTS_DATA_DIR.glob('*.csv'))
        report_files = list(REPORTS_DIR.glob('*.md'))
        
        print(f"  차트: {len(chart_files)}개")
        for f in chart_files:
            print(f"    - {f.name}")
        
        print(f"\n  데이터: {len(data_files)}개")
        for f in data_files:
            print(f"    - {f.name}")
        
        print(f"\n  리포트: {len(report_files)}개")
        for f in report_files:
            print(f"    - {f.name}")
        
        print("\n" + "█" * 70)
        print("█" + "✓ 모든 분석이 완료되었습니다!".center(68) + "█")
        print("█" * 70 + "\n")
        
        return 0
    
    except Exception as e:
        logger.error(f"분석 실패: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
