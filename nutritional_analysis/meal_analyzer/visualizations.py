# -*- coding: utf-8 -*-
"""
NutriScanner Visualizations
============================
Two clean, mobile-friendly charts:

  1. health_scorecard     — 5 health index scores as colour-coded cards
  2. macronutrient_donut  — carbs / protein / fat calorie split donut

Both returned from generate_visualizations() as a dict of matplotlib Figures.
"""

from __future__ import annotations
import warnings
from typing import Dict, List

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np

warnings.filterwarnings('ignore')

# ── Palette ───────────────────────────────────────────────────────────────
C = {
    'excellent':   '#16A34A',
    'good':        '#2563EB',
    'attention':   '#DC2626',
    'carbs':       '#F97316',
    'protein':     '#22C55E',
    'fat':         '#FACC15',
    'bg':          '#FFFFFF',
    'card_border': '#E5E7EB',
    'text_dark':   '#111827',
    'text_mid':    '#6B7280',
}

def _col(s):   return C['excellent'] if s >= 75 else C['good'] if s >= 50 else C['attention']
def _lbl(s):   return 'Excellent'    if s >= 75 else 'Good'    if s >= 50 else 'Needs Attention'
def _bg(s):    return '#F0FDF4'      if s >= 75 else '#EFF6FF'  if s >= 50 else '#FEF2F2'


# ═══════════════════════════════════════════════════════════════════════════
# CHART 1 — Health Scorecard
# ═══════════════════════════════════════════════════════════════════════════

def create_health_scorecard(indexes: Dict[str, float]) -> plt.Figure:
    """5 index scores as colour-coded cards with progress bars."""
    n   = len(indexes)
    fig, ax = plt.subplots(figsize=(9, 1.2 + n * 0.9), facecolor=C['bg'])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    ax.text(0.5, 0.97, 'Health Index Scores',
            ha='center', va='top', fontsize=15, fontweight='bold',
            color=C['text_dark'], transform=ax.transAxes)

    card_h = 0.80 / n
    y_top  = 0.88

    for i, (name, score) in enumerate(indexes.items()):
        y0    = y_top - i * (card_h + 0.018)
        y_mid = y0 - card_h / 2
        col   = _col(score)

        # Card
        ax.add_patch(FancyBboxPatch(
            (0.03, y0 - card_h), 0.94, card_h - 0.006,
            boxstyle='round,pad=0.01',
            facecolor=_bg(score), edgecolor=C['card_border'],
            linewidth=1.2, transform=ax.transAxes, clip_on=False))
        # Colour stripe
        ax.add_patch(FancyBboxPatch(
            (0.03, y0 - card_h), 0.012, card_h - 0.006,
            boxstyle='round,pad=0.0',
            facecolor=col, edgecolor='none',
            transform=ax.transAxes, clip_on=False))

        # Name
        short = name.replace(' Score', '').replace('Carbohydrate', 'Carb')
        ax.text(0.07, y_mid, short,
                ha='left', va='center', fontsize=10.5, fontweight='bold',
                color=C['text_dark'], transform=ax.transAxes)

        # Progress bar
        bx, bw, by, bh = 0.46, 0.28, y_mid - 0.015, 0.030
        ax.add_patch(FancyBboxPatch((bx, by), bw, bh,
            boxstyle='round,pad=0.005', facecolor='#E5E7EB', edgecolor='none',
            transform=ax.transAxes, clip_on=False))
        ax.add_patch(FancyBboxPatch((bx, by), max(0.005, bw * score / 100), bh,
            boxstyle='round,pad=0.005', facecolor=col, edgecolor='none',
            transform=ax.transAxes, clip_on=False))

        # Score & rating
        ax.text(0.78, y_mid, f'{score:.1f}/100',
                ha='center', va='center', fontsize=12, fontweight='bold',
                color=col, transform=ax.transAxes)
        ax.text(0.96, y_mid, _lbl(score),
                ha='right', va='center', fontsize=9, style='italic',
                color=col, transform=ax.transAxes)

    ax.text(0.5, 0.01,
            'Scores are interpretive indicators, not medical diagnoses.',
            ha='center', va='bottom', fontsize=8,
            color=C['text_mid'], style='italic', transform=ax.transAxes)

    fig.tight_layout(pad=0.4)
    return fig


# ═══════════════════════════════════════════════════════════════════════════
# CHART 2 — Macronutrient Donut
# ═══════════════════════════════════════════════════════════════════════════

def create_macronutrient_donut(totals: Dict) -> plt.Figure:
    """Donut: calorie split Carbs / Protein / Fat. Total kcal in centre."""
    carbs_g   = max(0, totals.get('Carbohydrates digestible (g)', 0))
    protein_g = max(0, totals.get('Protein (g)', 0))
    fat_g     = max(0, totals.get('Fat (g)', 0))
    fiber_g   = max(0, totals.get('Total fiber (g)', 0))

    cal_c  = carbs_g   * 4
    cal_p  = protein_g * 4
    cal_f  = fat_g     * 9
    total  = cal_c + cal_p + cal_f

    fig, ax = plt.subplots(figsize=(7, 6.2), facecolor=C['bg'])
    ax.set_aspect('equal')

    if total < 1:
        ax.text(0.5, 0.5, 'No macronutrient data available',
                ha='center', va='center', fontsize=12, color=C['text_mid'],
                transform=ax.transAxes)
        ax.axis('off')
        fig.tight_layout()
        return fig

    sizes  = [cal_c, cal_p, cal_f]
    colors = [C['carbs'], C['protein'], C['fat']]
    labels = ['Carbohydrates', 'Protein', 'Fat']
    grams  = [carbs_g, protein_g, fat_g]

    ax.pie(sizes, colors=colors, startangle=90, counterclock=False,
           wedgeprops=dict(width=0.46, edgecolor='white', linewidth=3))

    ax.text(0,  0.13, f'{total:.0f}',
            ha='center', va='center', fontsize=32, fontweight='bold',
            color=C['text_dark'])
    ax.text(0, -0.14, 'kcal',
            ha='center', va='center', fontsize=13, color=C['text_mid'])

    handles = [
        mpatches.Patch(
            facecolor=colors[i], edgecolor='white', linewidth=1.5,
            label=f'{labels[i]}:  {grams[i]:.1f} g  '
                  f'({sizes[i]:.0f} kcal,  {sizes[i]/total*100:.0f}%)')
        for i in range(3)
    ]
    ax.legend(handles=handles, loc='lower center',
              bbox_to_anchor=(0.5, -0.20), ncol=1,
              fontsize=10.5, frameon=False,
              handlelength=1.4, handleheight=1.0)

    ax.set_title('Macronutrient Breakdown', fontsize=14, fontweight='bold',
                 color=C['text_dark'], pad=16)

    if fiber_g > 0:
        ax.text(0, -1.62, f'Dietary Fiber: {fiber_g:.1f} g',
                ha='center', va='center', fontsize=9.5,
                color=C['text_mid'], style='italic')

    ax.axis('off')
    fig.tight_layout(pad=0.6)
    return fig


# ═══════════════════════════════════════════════════════════════════════════
# MAIN ENTRY POINT — called by analyzer.py
# ═══════════════════════════════════════════════════════════════════════════

def generate_visualizations(totals: Dict, indexes: Dict, items: List) -> Dict:
    """Return {'health_scorecard': Figure, 'macronutrient_donut': Figure}."""
    return {
        'health_scorecard':    create_health_scorecard(indexes),
        'macronutrient_donut': create_macronutrient_donut(totals),
    }


# ── Backwards-compat wrappers ─────────────────────────────────────────────

def generate_beautiful_visualizations(totals, indexes, items):
    """Legacy wrapper used by analyzer.py."""
    return generate_visualizations(totals, indexes, items)

def generate_comparison_visualizations(totals):
    """Legacy wrapper — now a no-op, comparison_charts.py can be deleted."""
    return {}