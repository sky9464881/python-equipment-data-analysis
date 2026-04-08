"""
통합 시각화 모듈 - refined version

기존 클래스/메서드 시그니처를 유지하면서,
레이아웃 겹침과 텍스트 충돌을 줄이도록 개선한 교체형 모듈입니다.
"""

from __future__ import annotations

import textwrap
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import matplotlib.font_manager as fm
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.patches import FancyBboxPatch

from config import FONT_NAME, COLORS, PLOT_CONFIG, CHARTS_DIR, OEE_TARGETS, QUALITY_TARGETS
from utils import logger

# ============================================
# 글로벌 스타일
# ============================================
plt.rcParams['axes.linewidth'] = 1.2
plt.rcParams['grid.alpha'] = 0.25
plt.rcParams['grid.linestyle'] = '--'
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.facecolor'] = '#fafafa'
plt.rcParams['savefig.facecolor'] = 'white'
plt.rcParams['savefig.bbox'] = 'tight'
plt.rcParams['axes.unicode_minus'] = False


COLOR_PALETTE = {
    'primary': '#1f4788',
    'secondary': '#d84315',
    'success': '#388e3c',
    'warning': '#f57c00',
    'danger': '#c62828',
    'light_bg': '#f5f5f5',
    'dark_text': '#212121',
    'muted_text': '#616161',
    'border': '#d0d7de',
    'soft_blue': '#eaf2ff',
    'soft_green': '#edf7ed',
    'soft_orange': '#fff4e5',
    'soft_red': '#fdecec',
}

LINE_COLORS = {
    'A라인': '#1f4788',
    'B라인': '#d84315',
    'C라인': '#388e3c',
    'D라인': '#6a1b9a',
}


class IntegratedVisualizer:
    """프로페셔널 통합 시각화"""

    def __init__(self, output_dir: Path = CHARTS_DIR):
        self.output_dir = output_dir
        self.figures = {}
        self.font_family = self._detect_font_family()
        self._setup_style()

    # ============================================
    # 기본 설정 / 공통 유틸
    # ============================================

    def _detect_font_family(self) -> str:
        """운영체제별 한글 폰트 fallback 포함"""
        candidates = []
        if FONT_NAME:
            candidates.append(FONT_NAME)
        candidates.extend(['Malgun Gothic', 'AppleGothic', 'NanumGothic', 'DejaVu Sans'])

        available = {f.name for f in fm.fontManager.ttflist}
        for name in candidates:
            if name in available:
                return name
        return 'DejaVu Sans'

    def _setup_style(self):
        plt.rcParams['font.family'] = self.font_family
        sns.set_style('whitegrid')

    def _apply_korean_font(self, figure):
        """Figure의 모든 텍스트에 폰트 적용"""
        for text in figure.findobj(match=plt.Text):
            text.set_fontfamily(self.font_family)

    def _safe_value(self, value, default=0.0) -> float:
        try:
            if pd.isna(value):
                return float(default)
            return float(value)
        except Exception:
            return float(default)

    def _style_axes(self, ax, *, grid_axis='y'):
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(COLOR_PALETTE['border'])
        ax.spines['bottom'].set_color(COLOR_PALETTE['border'])
        ax.tick_params(axis='both', labelsize=10, colors=COLOR_PALETTE['dark_text'])
        ax.grid(axis=grid_axis, alpha=0.25, linestyle='--')
        ax.set_axisbelow(True)

    def _wrap_text(self, text: str, width: int = 14) -> str:
        text = '' if text is None else str(text)
        if len(text) <= width:
            return text
        return '\n'.join(textwrap.wrap(text, width=width, break_long_words=False))

    def _wrap_labels(self, labels: Iterable, width: int = 12) -> List[str]:
        return [self._wrap_text(str(label), width=width) for label in labels]

    def _smart_rotation(self, labels: Iterable, threshold: int = 8) -> int:
        labels = [str(x) for x in labels]
        if len(labels) > threshold or any(len(x) > 8 for x in labels):
            return 30
        return 0

    def _annotate_vertical_bars(self, ax, bars, fmt='{:.1f}%', offset=1.2, fontsize=9):
        ymin, ymax = ax.get_ylim()
        span = max(1, ymax - ymin)
        limit = ymax - span * 0.02
        for bar in bars:
            height = bar.get_height()
            if pd.isna(height):
                continue
            y = min(height + offset, limit)
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                y,
                fmt.format(height),
                ha='center',
                va='bottom',
                fontsize=fontsize,
                fontweight='bold',
                color=COLOR_PALETTE['dark_text'],
                clip_on=True,
            )

    def _annotate_horizontal_bars(self, ax, bars, values, fmt='{:.1f}%', fontsize=9):
        xmin, xmax = ax.get_xlim()
        span = max(1, xmax - xmin)
        right_margin = xmax - span * 0.03
        for bar, value in zip(bars, values):
            if pd.isna(value):
                continue
            y = bar.get_y() + bar.get_height() / 2
            if value > xmax * 0.84:
                ax.text(
                    value - span * 0.02,
                    y,
                    fmt.format(value),
                    ha='right',
                    va='center',
                    fontsize=fontsize,
                    fontweight='bold',
                    color='white',
                    clip_on=True,
                )
            else:
                x = min(value + span * 0.015, right_margin)
                ax.text(
                    x,
                    y,
                    fmt.format(value),
                    ha='left',
                    va='center',
                    fontsize=fontsize,
                    fontweight='bold',
                    color=COLOR_PALETTE['dark_text'],
                    clip_on=True,
                )

    def _format_period_labels(self, periods: Iterable, max_ticks: int = 8):
        labels = [str(p) for p in periods]
        n = len(labels)
        if n == 0:
            return [], []
        if n <= max_ticks:
            idx = list(range(n))
        else:
            idx = np.linspace(0, n - 1, max_ticks, dtype=int).tolist()
        tick_labels = []
        for i in idx:
            label = labels[i]
            tick_labels.append(label.split('/')[0][-5:] if '/' in label else label)
        return idx, tick_labels

    def _finalize_figure(self, fig, top=0.92, bottom=0.08, left=0.06, right=0.96, hspace=0.3, wspace=0.25):
        fig.subplots_adjust(top=top, bottom=bottom, left=left, right=right, hspace=hspace, wspace=wspace)
        self._apply_korean_font(fig)

    # ============================================
    # 1. OEE 게이지 차트
    # ============================================

    def plot_oee_gauge(self, metrics: Dict) -> plt.Figure:
        fig = plt.figure(figsize=(16, 9.8))
        fig.patch.set_facecolor('#f6f8fb')
        gs = fig.add_gridspec(2, 2, hspace=0.18, wspace=0.10)
        fig.suptitle('OEE 분석 현황', fontsize=21, fontweight='bold', y=0.965)
        fig.text(
            0.5, 0.935,
            '핵심 지표 4개를 동일 스케일에서 비교할 수 있도록 구성했습니다.',
            ha='center', va='center', fontsize=10.5, color=COLOR_PALETTE['muted_text']
        )

        metric_cards = [
            ('가동률 (Availability)', self._safe_value(metrics.get('availability', 0)), OEE_TARGETS['availability'], COLOR_PALETTE['primary'], '%'),
            ('성능률 (Performance)', self._safe_value(metrics.get('performance', 0)), OEE_TARGETS['performance'], COLOR_PALETTE['secondary'], '%'),
            ('양품률 (Quality)', self._safe_value(metrics.get('quality', 0)), OEE_TARGETS['quality'], COLOR_PALETTE['success'], '%'),
            ('종합 OEE', self._safe_value(metrics.get('oee', 0)), OEE_TARGETS['overall'], COLOR_PALETTE['danger'], '%'),
        ]

        for i, card in enumerate(metric_cards):
            ax = fig.add_subplot(gs[i // 2, i % 2])
            self._draw_oee_gauge_card(ax, *card)

        self._finalize_figure(fig, top=0.90, bottom=0.06, left=0.04, right=0.96, hspace=0.12, wspace=0.08)
        self.figures['oee_gauge'] = fig
        return fig

    def _draw_oee_gauge_card(self, ax, title, value, target, color, unit):
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_xlim(-1.30, 1.30)
        ax.set_ylim(-0.95, 1.38)

        card = FancyBboxPatch(
            (-1.24, -0.88), 2.48, 2.18,
            boxstyle='round,pad=0.02,rounding_size=0.08',
            facecolor='white', edgecolor=COLOR_PALETTE['border'], linewidth=1.2, zorder=0,
        )
        ax.add_patch(card)

        # 제목
        ax.text(0, 1.17, title, ha='center', va='bottom', fontsize=13, fontweight='bold', color=COLOR_PALETTE['dark_text'])

        # 게이지 아크
        start_angle = np.pi
        end_angle = 0
        theta_bg = np.linspace(start_angle, end_angle, 240)
        ax.plot(np.cos(theta_bg), np.sin(theta_bg), color='#e7ebf0', linewidth=20, solid_capstyle='round', zorder=1)

        value_ratio = np.clip(value, 0, 100) / 100
        theta_fill = np.linspace(start_angle, start_angle + (end_angle - start_angle) * value_ratio, 240)
        ax.plot(np.cos(theta_fill), np.sin(theta_fill), color=color, linewidth=20, solid_capstyle='round', zorder=2)

        # 눈금 최소화
        for tick in np.linspace(0, 1, 6):
            angle = start_angle + (end_angle - start_angle) * tick
            ax.plot(
                [0.84 * np.cos(angle), 0.95 * np.cos(angle)],
                [0.84 * np.sin(angle), 0.95 * np.sin(angle)],
                color='#a8b0bb', linewidth=1.5, zorder=3,
            )

        for tick, label in zip([0.0, 0.5, 1.0], ['0', '50', '100']):
            angle = start_angle + (end_angle - start_angle) * tick
            ax.text(
                1.08 * np.cos(angle),
                1.08 * np.sin(angle) - 0.03,
                label,
                ha='center', va='center', fontsize=8.5, color=COLOR_PALETTE['muted_text'],
            )

        # 목표선 및 목표 라벨
        target_ratio = np.clip(target, 0, 100) / 100
        target_angle = start_angle + (end_angle - start_angle) * target_ratio
        x0, y0 = 0.68 * np.cos(target_angle), 0.68 * np.sin(target_angle)
        x1, y1 = 1.03 * np.cos(target_angle), 1.03 * np.sin(target_angle)
        ax.plot([x0, x1], [y0, y1], color=COLOR_PALETTE['dark_text'], linewidth=2.0, zorder=4)
        ax.scatter([x1], [y1], s=20, color=COLOR_PALETTE['dark_text'], zorder=5)

        label_x = 0.94 if x1 >= 0 else -0.94
        label_y = 0.16 if y1 >= 0.15 else 0.22
        target_box = FancyBboxPatch(
            (label_x - 0.22, label_y - 0.055), 0.44, 0.11,
            boxstyle='round,pad=0.02,rounding_size=0.04',
            facecolor='#f3f5f7', edgecolor='none', zorder=1,
        )
        ax.add_patch(target_box)
        ax.text(label_x, label_y, f'목표 {target:.0f}{unit}', ha='center', va='center', fontsize=8.5, color=COLOR_PALETTE['dark_text'])

        # 중앙 수치
        progress_pct = (value / target * 100) if target > 0 else 0
        gap = value - target
        if value >= target:
            status = '목표 달성'
            status_color = COLOR_PALETTE['success']
            badge_bg = COLOR_PALETTE['soft_green']
        elif value >= target * 0.90:
            status = '근접'
            status_color = COLOR_PALETTE['warning']
            badge_bg = COLOR_PALETTE['soft_orange']
        else:
            status = '개선 필요'
            status_color = COLOR_PALETTE['danger']
            badge_bg = COLOR_PALETTE['soft_red']

        ax.text(0, 0.12, f'{value:.1f}{unit}', ha='center', va='center', fontsize=28, fontweight='bold', color=color)
        ax.text(0, -0.10, f'달성률 {progress_pct:.0f}%   |   차이 {gap:+.1f}{unit}', ha='center', va='center', fontsize=9.5, color=COLOR_PALETTE['muted_text'])

        badge = FancyBboxPatch(
            (-0.42, -0.36), 0.84, 0.14,
            boxstyle='round,pad=0.02,rounding_size=0.05',
            facecolor=badge_bg, edgecolor='none', zorder=1,
        )
        ax.add_patch(badge)
        ax.text(0, -0.29, status, ha='center', va='center', fontsize=10, fontweight='bold', color=status_color)

        # 하단 요약 박스
        footer = FancyBboxPatch(
            (-0.88, -0.73), 1.76, 0.18,
            boxstyle='round,pad=0.02,rounding_size=0.04',
            facecolor='#f8fafc', edgecolor='none', zorder=1,
        )
        ax.add_patch(footer)
        footer_text = f'현재 {value:.1f}{unit} / 목표 {target:.1f}{unit} / 갭 {gap:+.1f}{unit}'
        ax.text(0, -0.64, footer_text, ha='center', va='center', fontsize=8.8, color=COLOR_PALETTE['dark_text'])

    # ============================================
    # 2. 설비 비교 차트
    # ============================================

    def plot_equipment_comparison(self, oee_by_equipment: pd.DataFrame) -> plt.Figure:
        df = oee_by_equipment.copy()
        top_n = min(12, len(df))
        df = df.head(top_n).sort_values('oee', ascending=True)

        fig_height = max(7.5, 0.62 * len(df) + 3.5)
        fig, ax = plt.subplots(figsize=(15, fig_height))
        fig.suptitle('설비별 OEE 순위', fontsize=18, fontweight='bold', y=0.97)

        colors = [LINE_COLORS.get(line, COLOR_PALETTE['primary']) for line in df['line']]
        y_labels = [f"{self._wrap_text(row['equipment_id'], 14)}\n({row['line']})" for _, row in df.iterrows()]

        max_val = max([self._safe_value(v) for v in df['oee']] + [OEE_TARGETS['overall']])
        x_max = min(110, max(100, max_val + 12))

        bars = ax.barh(range(len(df)), df['oee'], color=colors, edgecolor='white', linewidth=1.2, height=0.68)
        ax.axvline(
            OEE_TARGETS['overall'], color=COLOR_PALETTE['danger'], linestyle='--', linewidth=2.2,
            alpha=0.9, label=f"목표 OEE {OEE_TARGETS['overall']}%"
        )

        ax.set_yticks(range(len(df)))
        ax.set_yticklabels(y_labels, fontsize=10)
        ax.set_xlabel('OEE (%)', fontsize=12, fontweight='bold')
        ax.set_title('상위 설비 비교', fontsize=13, fontweight='bold', loc='left', pad=12)
        ax.set_xlim(0, x_max)
        self._style_axes(ax, grid_axis='x')

        values = [self._safe_value(v) for v in df['oee']]
        self._annotate_horizontal_bars(ax, bars, values, fmt='{:.1f}%')

        present_lines = list(dict.fromkeys(df['line'].astype(str).tolist()))
        handles = [
            mpatches.Patch(facecolor=LINE_COLORS.get(line, COLOR_PALETTE['primary']), edgecolor='none', label=line)
            for line in present_lines
        ]
        if handles:
            ax.legend(
                handles=handles,
                loc='upper center', bbox_to_anchor=(0.5, -0.10),
                ncol=min(4, len(handles)), frameon=False, fontsize=10,
            )

        self._finalize_figure(fig, top=0.90, bottom=0.14, left=0.20, right=0.96)
        self.figures['equipment_comparison'] = fig
        return fig

    # ============================================
    # 3. 라인 비교 차트
    # ============================================

    def plot_line_comparison(self, oee_by_line: pd.DataFrame) -> plt.Figure:
        df = oee_by_line.copy()
        lines = df['line'].astype(str).tolist()
        colors = [LINE_COLORS.get(line, COLOR_PALETTE['primary']) for line in lines]
        rotation = self._smart_rotation(lines)

        fig, axes = plt.subplots(2, 2, figsize=(16, 10))
        fig.suptitle('라인별 성과 분석', fontsize=18, fontweight='bold', y=0.97)

        specs = [
            ('oee', '① 종합 OEE', 'OEE (%)', OEE_TARGETS['overall']),
            ('availability', '② 가동률', '가동률 (%)', OEE_TARGETS['availability']),
            ('performance', '③ 성능률', '성능률 (%)', OEE_TARGETS['performance']),
            ('quality', '④ 양품률', '양품률 (%)', OEE_TARGETS['quality']),
        ]

        for ax, (column, title, ylabel, target) in zip(axes.flatten(), specs):
            vals = [self._safe_value(v) for v in df[column]]
            local_max = max(vals + [target])
            ymax = min(110, max(100, local_max + 8))
            bars = ax.bar(lines, vals, color=colors, edgecolor='white', linewidth=1.2, width=0.62, alpha=0.92)
            ax.axhline(target, color=COLOR_PALETTE['danger'], linestyle='--', linewidth=2, label=f'목표 {target}%')
            ax.set_title(title, fontsize=12, fontweight='bold', loc='left')
            ax.set_ylabel(ylabel, fontsize=11, fontweight='bold')
            ax.set_ylim(0, ymax)
            self._style_axes(ax, grid_axis='y')
            self._annotate_vertical_bars(ax, bars, fmt='{:.1f}%')
            ax.tick_params(axis='x', rotation=rotation)
            if rotation:
                for label in ax.get_xticklabels():
                    label.set_ha('right')
            if column == 'oee':
                ax.legend(loc='upper right', frameon=False, fontsize=9)

        self._finalize_figure(fig, top=0.90, bottom=0.10, left=0.06, right=0.97, hspace=0.35, wspace=0.22)
        self.figures['line_comparison'] = fig
        return fig

    # ============================================
    # 4. OEE 추이 차트
    # ============================================

    def plot_oee_trend(self, oee_by_period: pd.DataFrame) -> plt.Figure:
        df = oee_by_period.copy().reset_index(drop=True)
        x_pos = np.arange(len(df))

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 9), sharex=True)
        fig.suptitle('OEE 시계열 분석', fontsize=18, fontweight='bold', y=0.97)

        oee_vals = df['oee'].astype(float).to_numpy()
        ax1.plot(x_pos, oee_vals, marker='o', linewidth=2.8, markersize=6.5, color=COLOR_PALETTE['primary'], label='OEE')
        ax1.fill_between(x_pos, oee_vals, alpha=0.15, color=COLOR_PALETTE['primary'])
        ax1.axhline(OEE_TARGETS['overall'], color=COLOR_PALETTE['danger'], linestyle='--', linewidth=2, label=f"목표 {OEE_TARGETS['overall']}%")
        ax1.set_ylabel('OEE (%)', fontsize=12, fontweight='bold')
        ax1.set_title('① OEE 추이', fontsize=13, fontweight='bold', loc='left')
        ax1.set_ylim(max(0, np.nanmin(oee_vals) - 8), min(105, max(100, np.nanmax(oee_vals) + 8)))
        self._style_axes(ax1, grid_axis='both')
        ax1.legend(loc='upper left', frameon=False, fontsize=10)

        annotate_idx, _ = self._format_period_labels(df['period'], max_ticks=min(8, max(4, len(df))))
        for i in annotate_idx:
            val = self._safe_value(df.loc[i, 'oee'])
            ax1.text(i, min(val + 1.5, ax1.get_ylim()[1] - 1.5), f'{val:.0f}%', ha='center', va='bottom', fontsize=8, fontweight='bold', clip_on=True)

        metric_specs = [
            ('availability', '가동률', 's', COLOR_PALETTE['primary']),
            ('performance', '성능률', '^', COLOR_PALETTE['secondary']),
            ('quality', '양품률', 'o', COLOR_PALETTE['success']),
        ]
        for col, label, marker, color in metric_specs:
            vals = df[col].astype(float).to_numpy()
            ax2.plot(x_pos, vals, marker=marker, linewidth=2.2, markersize=5.5, label=label, color=color)

        ax2.set_ylabel('비율 (%)', fontsize=12, fontweight='bold')
        ax2.set_xlabel('분석 기간', fontsize=12, fontweight='bold')
        ax2.set_title('② OEE 구성요소 추이', fontsize=13, fontweight='bold', loc='left')
        lower = max(0, min(df[['availability', 'performance', 'quality']].min().min() - 5, 70))
        upper = min(105, max(df[['availability', 'performance', 'quality']].max().max() + 4, 100))
        ax2.set_ylim(lower, upper)
        self._style_axes(ax2, grid_axis='both')
        ax2.legend(loc='upper center', bbox_to_anchor=(0.5, -0.18), ncol=3, frameon=False, fontsize=10)

        tick_idx, tick_labels = self._format_period_labels(df['period'], max_ticks=8)
        ax2.set_xticks(tick_idx)
        ax2.set_xticklabels(tick_labels, rotation=30 if len(tick_labels) > 5 else 0, ha='right' if len(tick_labels) > 5 else 'center')

        self._finalize_figure(fig, top=0.90, bottom=0.15, left=0.07, right=0.97, hspace=0.30)
        self.figures['oee_trend'] = fig
        return fig

    # ============================================
    # 5. Six Big Losses
    # ============================================

    def plot_six_big_losses(self, losses: pd.DataFrame) -> plt.Figure:
        sorted_losses = losses.sort_values('total_min', ascending=False).copy()
        values = sorted_losses['total_min'].astype(float).to_numpy()
        labels = sorted_losses.index.astype(str).tolist()

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
        fig.suptitle('OEE 손실 분석 (Six Big Losses)', fontsize=18, fontweight='bold', y=0.97)

        pareto_colors = [COLOR_PALETTE['danger'] if i < 2 else COLOR_PALETTE['secondary'] for i in range(len(sorted_losses))]
        wrapped_labels = self._wrap_labels(labels, width=10)
        bars = ax1.bar(range(len(sorted_losses)), values, color=pareto_colors, edgecolor='white', linewidth=1.2, width=0.68)
        ax1.set_xticks(range(len(sorted_losses)))
        ax1.set_xticklabels(wrapped_labels, rotation=20 if len(labels) > 4 else 0, ha='right' if len(labels) > 4 else 'center')
        ax1.set_ylabel('손실시간 (분)', fontsize=12, fontweight='bold')
        ax1.set_title('① 손실 요인별 크기', fontsize=13, fontweight='bold', loc='left')
        self._style_axes(ax1, grid_axis='y')
        self._annotate_vertical_bars(ax1, bars, fmt='{:.0f}', offset=max(1.0, np.nanmax(values) * 0.02), fontsize=9)

        total = values.sum() if values.sum() else 1
        pct = values / total * 100
        donut_colors = plt.cm.Set3(np.linspace(0.05, 0.95, len(values)))

        def _autopct(p):
            return f'{p:.1f}%' if p >= 6 else ''

        wedges, texts, autotexts = ax2.pie(
            values,
            labels=None,
            autopct=_autopct,
            startangle=90,
            counterclock=False,
            colors=donut_colors,
            pctdistance=0.78,
            wedgeprops=dict(width=0.42, edgecolor='white'),
            textprops={'fontsize': 9, 'fontweight': 'bold'},
        )
        ax2.set_title('② 손실 배분 비율', fontsize=13, fontweight='bold', loc='left')
        legend_labels = [f'{label} ({p:.1f}%)' for label, p in zip(labels, pct)]
        ax2.legend(wedges, legend_labels, loc='center left', bbox_to_anchor=(1.0, 0.5), frameon=False, fontsize=9)
        for autotext in autotexts:
            autotext.set_color(COLOR_PALETTE['dark_text'])
        ax2.text(0, 0, f'총 손실\n{int(total)}분', ha='center', va='center', fontsize=12, fontweight='bold', color=COLOR_PALETTE['dark_text'])

        self._finalize_figure(fig, top=0.90, bottom=0.10, left=0.06, right=0.87, wspace=0.28)
        self.figures['six_big_losses'] = fig
        return fig

    # ============================================
    # 6. 개선 효과
    # ============================================

    def plot_improvement(self, before_after: pd.DataFrame) -> plt.Figure:
        df = before_after.copy()
        x = np.arange(len(df))
        width = 0.34
        labels = self._wrap_labels(df['metrics'].astype(str).tolist(), width=10)
        rotation = self._smart_rotation(labels, threshold=5)

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
        fig.suptitle('개선 효과 분석', fontsize=18, fontweight='bold', y=0.97)

        pre_vals = df['pre'].astype(float).to_numpy()
        post_vals = df['post'].astype(float).to_numpy()
        ymax = min(110, max(np.nanmax(pre_vals), np.nanmax(post_vals), 100) + 8)

        bars1 = ax1.bar(x - width / 2, pre_vals, width, label='개선 전', color=COLOR_PALETTE['secondary'], edgecolor='white', linewidth=1.2, alpha=0.9)
        bars2 = ax1.bar(x + width / 2, post_vals, width, label='개선 후', color=COLOR_PALETTE['success'], edgecolor='white', linewidth=1.2, alpha=0.9)
        ax1.set_ylabel('수치 (%)', fontsize=12, fontweight='bold')
        ax1.set_title('① 개선 전/후 비교', fontsize=13, fontweight='bold', loc='left')
        ax1.set_xticks(x)
        ax1.set_xticklabels(labels, rotation=rotation, ha='right' if rotation else 'center')
        ax1.set_ylim(0, ymax)
        self._style_axes(ax1, grid_axis='y')
        ax1.legend(loc='upper left', frameon=False, fontsize=10)
        self._annotate_vertical_bars(ax1, bars1, fmt='{:.1f}%')
        self._annotate_vertical_bars(ax1, bars2, fmt='{:.1f}%')

        change_vals = df['change_pp'].astype(float).to_numpy()
        colors_imp = [COLOR_PALETTE['success'] if val >= 0 else COLOR_PALETTE['danger'] for val in change_vals]
        bars = ax2.barh(range(len(df)), change_vals, color=colors_imp, edgecolor='white', linewidth=1.2, height=0.62)
        ax2.set_yticks(range(len(df)))
        ax2.set_yticklabels(labels, fontsize=10)
        ax2.set_xlabel('개선 효과 (p.p)', fontsize=12, fontweight='bold')
        ax2.set_title('② 개선 효과 크기', fontsize=13, fontweight='bold', loc='left')
        lim = max(1.0, np.nanmax(np.abs(change_vals)) * 1.25)
        ax2.set_xlim(-lim, lim)
        ax2.axvline(x=0, color=COLOR_PALETTE['dark_text'], linewidth=1.2)
        self._style_axes(ax2, grid_axis='x')

        for bar, val in zip(bars, change_vals):
            x_pos = val + (0.04 * lim if val >= 0 else -0.04 * lim)
            ax2.text(
                x_pos,
                bar.get_y() + bar.get_height() / 2,
                f'{val:.2f}p.p',
                va='center',
                ha='left' if val >= 0 else 'right',
                fontsize=9,
                fontweight='bold',
                color=COLOR_PALETTE['dark_text'],
                clip_on=True,
            )

        self._finalize_figure(fig, top=0.90, bottom=0.12, left=0.08, right=0.97, wspace=0.28)
        self.figures['improvement'] = fig
        return fig

    # ============================================
    # 7. 통합 대시보드 (Executive Dashboard)
    # ============================================

    def _draw_kpi_card(self, ax, title, value, unit, target, icon, color):
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis('off')

        ratio = (value / target * 100) if target > 0 else 0
        gap = value - target
        if ratio >= 100:
            badge_text = '목표 달성'
            badge_color = COLOR_PALETTE['success']
            badge_bg = COLOR_PALETTE['soft_green']
        elif ratio >= 90:
            badge_text = '근접'
            badge_color = COLOR_PALETTE['warning']
            badge_bg = COLOR_PALETTE['soft_orange']
        else:
            badge_text = '관리 필요'
            badge_color = COLOR_PALETTE['danger']
            badge_bg = COLOR_PALETTE['soft_red']

        bg = FancyBboxPatch(
            (0.18, 0.42), 9.64, 9.04,
            boxstyle='round,pad=0.28,rounding_size=0.50',
            facecolor='white', edgecolor=COLOR_PALETTE['border'], linewidth=1.2,
        )
        accent = FancyBboxPatch(
            (0.18, 8.45), 9.64, 1.01,
            boxstyle='round,pad=0.0,rounding_size=0.45',
            facecolor=color, edgecolor=color, linewidth=0,
        )
        badge = FancyBboxPatch(
            (3.1, 1.10), 3.8, 0.95,
            boxstyle='round,pad=0.10,rounding_size=0.22',
            facecolor=badge_bg, edgecolor='none', linewidth=0,
        )
        ax.add_patch(bg)
        ax.add_patch(accent)
        ax.add_patch(badge)

        title_text = f'{icon}  {title}'.strip() if icon else title
        ax.text(0.7, 8.96, title_text, ha='left', va='center', fontsize=11.2, fontweight='bold', color='white')
        ax.text(5.0, 5.55, f'{value:.1f}{unit}', ha='center', va='center', fontsize=27, fontweight='bold', color=color)
        ax.text(5.0, 3.45, f'목표 {target:.1f}{unit}', ha='center', va='center', fontsize=10, color=COLOR_PALETTE['muted_text'])
        ax.text(5.0, 2.65, f'차이 {gap:+.1f}{unit} / 달성률 {ratio:.0f}%', ha='center', va='center', fontsize=9.8, color=COLOR_PALETTE['muted_text'])
        ax.text(5.0, 1.56, badge_text, ha='center', va='center', fontsize=10, fontweight='bold', color=badge_color)

    def create_integrated_dashboard(self, dashboard_data=None) -> plt.Figure:
        fig = plt.figure(figsize=(22, 14.5))
        fig.patch.set_facecolor('#f4f7fb')
        gs = fig.add_gridspec(20, 24, left=0.03, right=0.97, top=0.95, bottom=0.04, hspace=0.85, wspace=0.65)

        if dashboard_data is None or not isinstance(dashboard_data, dict):
            dashboard_data = {}

        oee_dict = dashboard_data.get('oee', {}) if isinstance(dashboard_data.get('oee', {}), dict) else {}
        oee_val = self._safe_value(oee_dict.get('oee', 0))
        availability = self._safe_value(oee_dict.get('availability', 0))
        performance = self._safe_value(oee_dict.get('performance', 0))
        quality = self._safe_value(oee_dict.get('quality', 0))

        line_df = dashboard_data.get('line_oee') if isinstance(dashboard_data.get('line_oee'), pd.DataFrame) else None
        loss_df = dashboard_data.get('six_big_losses') if isinstance(dashboard_data.get('six_big_losses'), pd.DataFrame) else None
        imp_df = dashboard_data.get('improvement_comparison') if isinstance(dashboard_data.get('improvement_comparison'), pd.DataFrame) else None

        # 헤더
        ax_header = fig.add_subplot(gs[0:2, :])
        ax_header.axis('off')
        header_bg = FancyBboxPatch((0.0, 0.05), 1.0, 0.90, boxstyle='round,pad=0.015,rounding_size=0.04',
                                   transform=ax_header.transAxes, facecolor='white', edgecolor=COLOR_PALETTE['border'], linewidth=1.0)
        ax_header.add_patch(header_bg)
        ax_header.text(0.03, 0.70, '스마트팩토리 통합 대시보드', transform=ax_header.transAxes,
                       fontsize=24, fontweight='bold', color=COLOR_PALETTE['dark_text'], ha='left', va='center')
        ax_header.text(0.03, 0.34, '핵심 KPI, 라인별 성과, 주요 손실, 개선 효과를 한 화면에서 확인할 수 있도록 재구성했습니다.',
                       transform=ax_header.transAxes, fontsize=11, color=COLOR_PALETTE['muted_text'], ha='left', va='center')
        ax_header.text(0.97, 0.66, f'현재 OEE {oee_val:.1f}%', transform=ax_header.transAxes,
                       fontsize=18, fontweight='bold', color=COLOR_PALETTE['primary'], ha='right', va='center')
        ax_header.text(0.97, 0.34, f'목표 {OEE_TARGETS["overall"]:.1f}% 대비 {oee_val - OEE_TARGETS["overall"]:+.1f}p',
                       transform=ax_header.transAxes, fontsize=10.5, color=COLOR_PALETTE['muted_text'], ha='right', va='center')

        # KPI 카드
        self._draw_kpi_card(fig.add_subplot(gs[2:5, 0:6]), 'OEE', oee_val, '%', OEE_TARGETS['overall'], 'KPI', COLOR_PALETTE['primary'])
        self._draw_kpi_card(fig.add_subplot(gs[2:5, 6:12]), '가동률', availability, '%', OEE_TARGETS['availability'], 'AV', COLOR_PALETTE['secondary'])
        self._draw_kpi_card(fig.add_subplot(gs[2:5, 12:18]), '성능률', performance, '%', OEE_TARGETS['performance'], 'PF', COLOR_PALETTE['success'])
        self._draw_kpi_card(fig.add_subplot(gs[2:5, 18:24]), '양품률', quality, '%', OEE_TARGETS['quality'], 'QL', COLOR_PALETTE['danger'])

        # 라인별 성과
        ax_line = fig.add_subplot(gs[5:12, 0:11])
        ax_line.set_facecolor('white')
        if line_df is not None and not line_df.empty:
            temp = line_df.copy()
            temp['line'] = temp['line'].astype(str)
            temp = temp.sort_values('oee', ascending=False)
            x = np.arange(len(temp))
            width = 0.34
            colors = [LINE_COLORS.get(line, COLOR_PALETTE['primary']) for line in temp['line']]
            oee_vals = temp['oee'].astype(float).to_numpy()
            bars = ax_line.bar(x, oee_vals, width=0.56, color=colors, edgecolor='white', linewidth=1.2, zorder=3)
            ax_line.axhline(OEE_TARGETS['overall'], color=COLOR_PALETTE['danger'], linestyle='--', linewidth=2, zorder=2,
                            label=f'목표 {OEE_TARGETS["overall"]}%')
            ax_line.set_xticks(x)
            ax_line.set_xticklabels(self._wrap_labels(temp['line'], 10), fontsize=10)
            ax_line.set_ylim(0, min(110, max(100, np.nanmax(oee_vals) + 10)))
            ax_line.set_title('라인별 OEE 비교', fontsize=14, fontweight='bold', loc='left', pad=12)
            ax_line.set_ylabel('OEE (%)', fontsize=11.5, fontweight='bold')
            self._style_axes(ax_line, grid_axis='y')
            self._annotate_vertical_bars(ax_line, bars, fmt='{:.1f}%')
            ax_line.legend(loc='upper right', frameon=False, fontsize=10)
        else:
            ax_line.axis('off')
            ax_line.text(0.5, 0.5, '라인별 OEE 데이터가 없습니다.', ha='center', va='center', fontsize=13, color=COLOR_PALETTE['muted_text'])

        # 목표 대비 bullet chart
        ax_bullet = fig.add_subplot(gs[5:12, 11:17])
        ax_bullet.set_facecolor('white')
        metrics_data = [
            ('가동률', availability, OEE_TARGETS['availability'], COLOR_PALETTE['secondary']),
            ('성능률', performance, OEE_TARGETS['performance'], COLOR_PALETTE['success']),
            ('양품률', quality, OEE_TARGETS['quality'], COLOR_PALETTE['danger']),
            ('OEE', oee_val, OEE_TARGETS['overall'], COLOR_PALETTE['primary']),
        ]
        y = np.arange(len(metrics_data))
        ax_bullet.barh(y, [100] * len(metrics_data), color='#edf1f5', edgecolor='none', height=0.46, zorder=1)
        for i, (label, cur, tgt, c) in enumerate(metrics_data):
            ax_bullet.barh(i, cur, color=c, edgecolor='none', height=0.46, zorder=2)
            ax_bullet.plot([tgt, tgt], [i - 0.28, i + 0.28], color=COLOR_PALETTE['dark_text'], linewidth=2, zorder=3)
            if cur >= 82:
                ax_bullet.text(cur - 2.0, i, f'{cur:.1f}%', va='center', ha='right', fontsize=9.5, color='white', fontweight='bold')
            else:
                ax_bullet.text(cur + 2.0, i, f'{cur:.1f}%', va='center', ha='left', fontsize=9.5, color=COLOR_PALETTE['dark_text'])
        ax_bullet.set_yticks(y)
        ax_bullet.set_yticklabels([m[0] for m in metrics_data], fontsize=10.5)
        ax_bullet.tick_params(axis='y', pad=2)
        ax_bullet.set_xlim(0, 100)
        ax_bullet.invert_yaxis()
        ax_bullet.set_title('목표 대비 달성 현황', fontsize=14, fontweight='bold', loc='left', pad=12)
        ax_bullet.set_xlabel('현재값 (%)', fontsize=10.5, fontweight='bold')
        self._style_axes(ax_bullet, grid_axis='x')
        ax_bullet.spines['left'].set_visible(False)
        ax_bullet.text(0.98, 1.03, '검은 표시선 = 목표값', transform=ax_bullet.transAxes,
                       ha='right', va='bottom', fontsize=9.2, color=COLOR_PALETTE['muted_text'])

        # 손실 요인
        ax_loss = fig.add_subplot(gs[5:12, 17:24])
        ax_loss.set_facecolor('white')
        if loss_df is not None and not loss_df.empty:
            temp = loss_df.sort_values('total_min', ascending=True).copy()
            labels = temp.index.astype(str).tolist()
            values = temp['total_min'].astype(float).to_numpy()
            colors_loss = [COLOR_PALETTE['warning']] * len(values)
            if len(values) >= 1:
                colors_loss[-1] = COLOR_PALETTE['danger']
            if len(values) >= 2:
                colors_loss[-2] = COLOR_PALETTE['secondary']
            bars = ax_loss.barh(np.arange(len(values)), values, color=colors_loss, edgecolor='white', linewidth=1.1, height=0.60)
            ax_loss.set_yticks(np.arange(len(values)))
            ax_loss.set_yticklabels(self._wrap_labels(labels, 12), fontsize=10)
            ax_loss.set_title('주요 손실 요인', fontsize=14, fontweight='bold', loc='left', pad=12)
            ax_loss.set_xlabel('손실 시간 (분)', fontsize=10.5, fontweight='bold')
            self._style_axes(ax_loss, grid_axis='x')
            self._annotate_horizontal_bars(ax_loss, bars, values, fmt='{:.0f}분')
        else:
            ax_loss.axis('off')
            ax_loss.text(0.5, 0.5, '손실 데이터를 확인할 수 없습니다.', ha='center', va='center', fontsize=13, color=COLOR_PALETTE['muted_text'])

        # 개선 전후 비교
        ax_imp = fig.add_subplot(gs[12:20, 0:14])
        ax_imp.set_facecolor('white')
        if imp_df is not None and not imp_df.empty and {'metrics', 'pre', 'post'}.issubset(imp_df.columns):
            temp = imp_df.copy()
            labels = self._wrap_labels(temp['metrics'].astype(str).tolist(), 10)
            x = np.arange(len(temp))
            width = 0.34
            pre_vals = temp['pre'].astype(float).to_numpy()
            post_vals = temp['post'].astype(float).to_numpy()
            bars1 = ax_imp.bar(x - width/2, pre_vals, width, color=COLOR_PALETTE['secondary'], alpha=0.88, edgecolor='white', linewidth=1.1, label='개선 전')
            bars2 = ax_imp.bar(x + width/2, post_vals, width, color=COLOR_PALETTE['success'], alpha=0.88, edgecolor='white', linewidth=1.1, label='개선 후')
            ax_imp.set_xticks(x)
            ax_imp.set_xticklabels(labels, fontsize=10)
            ax_imp.set_ylim(0, min(110, max(100, np.nanmax([pre_vals.max() if len(pre_vals) else 0, post_vals.max() if len(post_vals) else 0]) + 10)))
            ax_imp.set_title('개선 전후 비교', fontsize=14, fontweight='bold', loc='left', pad=12)
            ax_imp.set_ylabel('수치 (%)', fontsize=11.5, fontweight='bold')
            self._style_axes(ax_imp, grid_axis='y')
            self._annotate_vertical_bars(ax_imp, bars1, fmt='{:.1f}%')
            self._annotate_vertical_bars(ax_imp, bars2, fmt='{:.1f}%')
            ax_imp.legend(loc='upper right', frameon=False, fontsize=10)
        else:
            ax_imp.axis('off')
            ax_imp.text(0.5, 0.5, '개선 전후 비교 데이터가 없습니다.', ha='center', va='center', fontsize=13, color=COLOR_PALETTE['muted_text'])

        # 핵심 진단 및 실행 과제
        ax_summary = fig.add_subplot(gs[12:20, 14:24])
        ax_summary.axis('off')
        summary_bg = FancyBboxPatch((0.0, 0.0), 1.0, 1.0, boxstyle='round,pad=0.018,rounding_size=0.04',
                                    transform=ax_summary.transAxes, facecolor='white', edgecolor=COLOR_PALETTE['border'], linewidth=1.0)
        ax_summary.add_patch(summary_bg)

        if line_df is not None and not line_df.empty and 'oee' in line_df.columns:
            best_line_row = line_df.sort_values('oee', ascending=False).iloc[0]
            worst_line_row = line_df.sort_values('oee', ascending=True).iloc[0]
            best_line = f"{best_line_row['line']} ({self._safe_value(best_line_row['oee']):.1f}%)"
            worst_line = f"{worst_line_row['line']} ({self._safe_value(worst_line_row['oee']):.1f}%)"
        else:
            best_line = '데이터 없음'
            worst_line = '데이터 없음'

        if loss_df is not None and not loss_df.empty and 'total_min' in loss_df.columns:
            top_loss_row = loss_df.sort_values('total_min', ascending=False).iloc[0]
            top_loss = f"{str(top_loss_row.name)} ({self._safe_value(top_loss_row['total_min']):.0f}분)"
        else:
            top_loss = '데이터 없음'

        gap_oee = oee_val - OEE_TARGETS['overall']
        main_issue = '가동률 개선 우선' if availability < min(performance, quality) else '손실 원인 집중 관리'
        summary_lines = [
            ('현재 진단', COLOR_PALETTE['dark_text'], True),
            (f'현재 OEE는 {oee_val:.1f}%이며 목표 대비 {gap_oee:+.1f}p 차이입니다.', COLOR_PALETTE['dark_text'], False),
            (f'가장 높은 라인: {best_line}', COLOR_PALETTE['dark_text'], False),
            (f'개선이 필요한 라인: {worst_line}', COLOR_PALETTE['dark_text'], False),
            (f'가장 큰 손실 요인: {top_loss}', COLOR_PALETTE['dark_text'], False),
            ('', COLOR_PALETTE['dark_text'], False),
            ('핵심 포인트', COLOR_PALETTE['dark_text'], True),
            (f'1. 우선순위: {main_issue}', COLOR_PALETTE['primary'], False),
            ('2. 목표선 미달 항목은 운영 조건과 비가동 구간을 함께 점검해야 합니다.', COLOR_PALETTE['dark_text'], False),
            ('3. 품질이 안정적이면 생산성보다 가동 안정화가 먼저입니다.', COLOR_PALETTE['dark_text'], False),
            ('', COLOR_PALETTE['dark_text'], False),
            ('실행 과제', COLOR_PALETTE['dark_text'], True),
            ('1. 손실 상위 2개 항목의 발생 시간과 빈도를 주간 단위로 추적', COLOR_PALETTE['dark_text'], False),
            ('2. 저성과 라인의 작업 편차와 셋업 시간을 표준화', COLOR_PALETTE['dark_text'], False),
            ('3. OEE와 설비 부하를 같이 보면서 개선 효과를 검증', COLOR_PALETTE['dark_text'], False),
        ]

        y = 0.93
        for line, color, is_header in summary_lines:
            if line == '':
                y -= 0.05
                continue
            ax_summary.text(0.05, y, line, transform=ax_summary.transAxes, ha='left', va='top',
                            fontsize=12.2 if is_header else 10.6,
                            fontweight='bold' if is_header else 'normal', color=color)
            y -= 0.085 if is_header else 0.070

        self._apply_korean_font(fig)
        self.figures['integrated_dashboard'] = fig
        return fig

    # ============================================
    # 저장
    # ============================================

    def save_all(self) -> None:
        print("\n" + "=" * 60)
        print("차트 저장 중...")
        print("=" * 60)

        self.output_dir.mkdir(parents=True, exist_ok=True)

        for name, fig in self.figures.items():
            try:
                path = self.output_dir / f"{name}.png"
                fig.savefig(path, format='png', dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
                print(f"  저장 완료: {path.name}")
                plt.close(fig)
            except Exception as e:
                logger.error(f"차트 저장 실패 - {name}: {e}")
                print(f"  저장 실패 - {name}: {e}")

        print("=" * 60)
        logger.info("모든 차트 저장 완료")
