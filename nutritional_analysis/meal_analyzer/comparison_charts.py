"""
Comparison Visualizations for NutriScanner
Shows meal nutrition vs. recommended daily values
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
from typing import Dict, List

# Modern color palette
COLORS = {
    'primary': '#6C63FF',
    'success': '#00D4AA',
    'warning': '#FFB800',
    'danger': '#FF5757',
    'excellent': '#10B981',
    'good': '#3B82F6',
    'fair': '#F59E0B',
    'poor': '#EF4444',
}

# Recommended Daily Values (RDV)
DAILY_VALUES = {
    "Energy (kcal)": 2000.0,
    "Protein (g)": 50.0,
    "Carbohydrates digestible (g)": 275.0,
    "Total fiber (g)": 28.0,
    "Fat (g)": 78.0,
    "SFA": 20.0,
    "Sodium": 2300.0,
    "Potassium": 4700.0,
    "Calcium": 1300.0,
    "Iron": 18.0,
    "Magnesium": 420.0,
    "Zinc": 11.0,
    "Vitamin A(µg)": 900.0,
    "Vitamin C": 90.0,
    "Vitamin D(µg)": 20.0,
    "Folate(µg)": 400.0,
}

# Nutrients to maximize vs limit
MAXIMIZE_NUTRIENTS = [
    "Protein (g)", "Total fiber (g)", "Potassium", "Calcium",
    "Iron", "Magnesium", "Zinc", "Vitamin A(µg)", "Vitamin C",
    "Vitamin D(µg)", "Folate(µg)"
]

LIMIT_NUTRIENTS = ["Sodium", "SFA"]


def create_daily_value_comparison(totals: Dict) -> plt.Figure:
    """
    Beautiful percentage of daily value comparison chart
    """
    fig = plt.figure(figsize=(16, 10), facecolor='white')
    gs = GridSpec(2, 2, figure=fig, hspace=0.35, wspace=0.3)

    # ========================================================================
    # TOP LEFT: Macronutrients vs Daily Values
    # ========================================================================
    ax1 = fig.add_subplot(gs[0, 0])

    macros = ['Energy (kcal)', 'Protein (g)', 'Carbohydrates digestible (g)',
              'Total fiber (g)', 'Fat (g)']
    macro_labels = ['Energy', 'Protein', 'Carbs', 'Fiber', 'Fat']

    meal_values = []
    rdv_percentages = []
    colors = []

    for nutrient in macros:
        meal_val = totals.get(nutrient, 0.0)
        rdv = DAILY_VALUES.get(nutrient, 1.0)
        percentage = (meal_val / rdv) * 100

        meal_values.append(meal_val)
        rdv_percentages.append(min(percentage, 150))  # Cap at 150% for display

        # Color based on percentage
        if nutrient in LIMIT_NUTRIENTS:
            # For nutrients to limit: lower is better
            if percentage <= 30:
                colors.append(COLORS['excellent'])
            elif percentage <= 50:
                colors.append(COLORS['good'])
            elif percentage <= 75:
                colors.append(COLORS['warning'])
            else:
                colors.append(COLORS['danger'])
        else:
            # For nutrients to maximize: higher is better
            if percentage >= 75:
                colors.append(COLORS['excellent'])
            elif percentage >= 50:
                colors.append(COLORS['good'])
            elif percentage >= 25:
                colors.append(COLORS['warning'])
            else:
                colors.append(COLORS['poor'])

    # Create horizontal bars
    y_pos = np.arange(len(macro_labels))
    bars = ax1.barh(y_pos, rdv_percentages, color=colors, alpha=0.8,
                    edgecolor='white', linewidth=2, height=0.6)

    # Add 100% reference line
    ax1.axvline(x=100, color='gray', linestyle='--', linewidth=2,
                alpha=0.5, label='100% Daily Value')

    # Add percentage labels
    for i, (bar, pct, val) in enumerate(zip(bars, rdv_percentages, meal_values)):
        width = bar.get_width()
        label_x = width + 3

        # Show percentage and actual value
        ax1.text(label_x, bar.get_y() + bar.get_height() / 2,
                 f'{pct:.0f}% ({val:.1f})',
                 va='center', fontweight='bold', fontsize=11, color=colors[i])

    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(macro_labels, fontsize=12, fontweight='bold')
    ax1.set_xlabel('% of Daily Value', fontsize=12, fontweight='bold')
    ax1.set_title('Macronutrients vs Daily Recommendations',
                  fontsize=14, fontweight='bold', pad=15)
    ax1.set_xlim(0, max(rdv_percentages) * 1.15)
    ax1.grid(axis='x', alpha=0.3, linestyle='--')
    ax1.legend(loc='lower right', fontsize=10)

    # ========================================================================
    # TOP RIGHT: Micronutrients vs Daily Values
    # ========================================================================
    ax2 = fig.add_subplot(gs[0, 1])

    micros = ['Calcium', 'Iron', 'Magnesium', 'Zinc',
              'Vitamin A(µg)', 'Vitamin C', 'Vitamin D(µg)', 'Folate(µg)']
    micro_labels = ['Calcium', 'Iron', 'Magnesium', 'Zinc',
                    'Vit A', 'Vit C', 'Vit D', 'Folate']

    micro_percentages = []
    micro_colors = []

    for nutrient in micros:
        meal_val = totals.get(nutrient, 0.0)
        rdv = DAILY_VALUES.get(nutrient, 1.0)
        percentage = (meal_val / rdv) * 100

        micro_percentages.append(min(percentage, 150))

        # Color coding
        if percentage >= 75:
            micro_colors.append(COLORS['excellent'])
        elif percentage >= 50:
            micro_colors.append(COLORS['good'])
        elif percentage >= 25:
            micro_colors.append(COLORS['warning'])
        else:
            micro_colors.append(COLORS['poor'])

    # Create bars
    x_pos = np.arange(len(micro_labels))
    bars = ax2.bar(x_pos, micro_percentages, color=micro_colors, alpha=0.8,
                   edgecolor='white', linewidth=2, width=0.6)

    # Add 100% reference line
    ax2.axhline(y=100, color='gray', linestyle='--', linewidth=2,
                alpha=0.5, label='100% Daily Value')

    # Add percentage labels on top of bars
    for bar, pct in zip(bars, micro_percentages):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width() / 2, height + 3,
                 f'{pct:.0f}%', ha='center', va='bottom',
                 fontweight='bold', fontsize=10)

    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(micro_labels, rotation=45, ha='right', fontsize=10)
    ax2.set_ylabel('% of Daily Value', fontsize=12, fontweight='bold')
    ax2.set_title('Micronutrients vs Daily Recommendations',
                  fontsize=14, fontweight='bold', pad=15)
    ax2.set_ylim(0, max(micro_percentages) * 1.2)
    ax2.grid(axis='y', alpha=0.3, linestyle='--')
    ax2.legend(loc='upper right', fontsize=10)

    # ========================================================================
    # BOTTOM LEFT: Nutrients to Limit (Sodium & Saturated Fat)
    # ========================================================================
    ax3 = fig.add_subplot(gs[1, 0])

    limit_nutrients = ['Sodium', 'SFA']
    limit_labels = ['Sodium\n(mg)', 'Saturated Fat\n(g)']

    for i, (nutrient, label) in enumerate(zip(limit_nutrients, limit_labels)):
        meal_val = totals.get(nutrient, 0.0)
        rdv = DAILY_VALUES.get(nutrient, 1.0)
        percentage = (meal_val / rdv) * 100

        # Determine color (lower is better for these)
        if percentage <= 30:
            color = COLORS['excellent']
            status = 'Excellent'
        elif percentage <= 50:
            color = COLORS['good']
            status = 'Good'
        elif percentage <= 75:
            color = COLORS['warning']
            status = 'Moderate'
        else:
            color = COLORS['danger']
            status = 'High'

        # Create gauge-like visualization
        # Background circle
        circle_bg = mpatches.Circle((i * 2.5 + 1, 0.5), 0.8,
                                    facecolor='lightgray', alpha=0.2,
                                    edgecolor='gray', linewidth=2)
        ax3.add_patch(circle_bg)

        # Filled circle based on percentage
        wedge = mpatches.Wedge((i * 2.5 + 1, 0.5), 0.8, -90,
                               -90 + (360 * min(percentage / 100, 1.0)),
                               facecolor=color, alpha=0.7, edgecolor='white',
                               linewidth=3)
        ax3.add_patch(wedge)

        # Center text
        ax3.text(i * 2.5 + 1, 0.5, f'{percentage:.0f}%',
                 ha='center', va='center', fontsize=20,
                 fontweight='bold', color=color)

        # Label below
        ax3.text(i * 2.5 + 1, -0.5, label,
                 ha='center', va='top', fontsize=11, fontweight='bold')

        # Status below label
        ax3.text(i * 2.5 + 1, -0.8, status,
                 ha='center', va='top', fontsize=10,
                 style='italic', color=color)

        # Actual value
        ax3.text(i * 2.5 + 1, -1.1, f'{meal_val:.1f}',
                 ha='center', va='top', fontsize=9, color='gray')

    ax3.set_xlim(-0.5, 5)
    ax3.set_ylim(-1.5, 1.5)
    ax3.axis('off')
    ax3.set_title('Nutrients to Limit (% of Daily Maximum)',
                  fontsize=14, fontweight='bold', pad=10)

    # ========================================================================
    # BOTTOM RIGHT: Overall Nutrient Adequacy Summary
    # ========================================================================
    ax4 = fig.add_subplot(gs[1, 1])

    # Calculate how many nutrients meet different thresholds
    categories = {
        'Excellent (≥75%)': 0,
        'Good (50-74%)': 0,
        'Fair (25-49%)': 0,
        'Poor (<25%)': 0
    }

    for nutrient in MAXIMIZE_NUTRIENTS:
        if nutrient in totals and nutrient in DAILY_VALUES:
            meal_val = totals.get(nutrient, 0.0)
            rdv = DAILY_VALUES.get(nutrient, 1.0)
            percentage = (meal_val / rdv) * 100

            if percentage >= 75:
                categories['Excellent (≥75%)'] += 1
            elif percentage >= 50:
                categories['Good (50-74%)'] += 1
            elif percentage >= 25:
                categories['Fair (25-49%)'] += 1
            else:
                categories['Poor (<25%)'] += 1

    # Create donut chart
    sizes = list(categories.values())
    labels = list(categories.keys())
    colors_donut = [COLORS['excellent'], COLORS['good'],
                    COLORS['warning'], COLORS['poor']]

    # Only show categories with values > 0
    sizes_filtered = [s for s in sizes if s > 0]
    labels_filtered = [l for l, s in zip(labels, sizes) if s > 0]
    colors_filtered = [c for c, s in zip(colors_donut, sizes) if s > 0]

    if sizes_filtered:
        wedges, texts, autotexts = ax4.pie(
            sizes_filtered, labels=None, colors=colors_filtered,
            autopct=lambda pct: f'{int(pct / 100 * sum(sizes_filtered))}',
            startangle=90, pctdistance=0.85,
            wedgeprops=dict(width=0.4, edgecolor='white', linewidth=3)
        )

        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(14)

        # Add center circle
        centre = mpatches.Circle((0, 0), 0.70, fc='white', linewidth=0)
        ax4.add_artist(centre)

        # Add total count in center
        total_nutrients = sum(sizes_filtered)
        ax4.text(0, 0.05, f'{total_nutrients}', ha='center', va='center',
                 fontsize=32, fontweight='bold', color='#2D3436')
        ax4.text(0, -0.15, 'Nutrients\nTracked', ha='center', va='center',
                 fontsize=11, color='gray')

        # Legend
        legend_labels = [f'{label}: {count}'
                         for label, count in zip(labels_filtered, sizes_filtered)]
        ax4.legend(legend_labels, loc='upper left', bbox_to_anchor=(0.85, 1),
                   fontsize=10, frameon=True, fancybox=True, shadow=True)

    ax4.set_title('Nutrient Adequacy Distribution',
                  fontsize=14, fontweight='bold', pad=15)

    # ========================================================================
    # Main Title
    # ========================================================================
    fig.suptitle('Meal Nutrition vs Recommended Daily Values',
                 fontsize=18, fontweight='bold', y=0.98)

    return fig


def create_traffic_light_chart(totals: Dict) -> plt.Figure:
    """
    Traffic light system showing nutrient status
    """
    fig, ax = plt.subplots(figsize=(14, 10), facecolor='white')
    ax.axis('off')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    # Title
    ax.text(0.5, 0.95, 'Nutrient Status: Traffic Light System',
            ha='center', va='top', fontsize=20, fontweight='bold')

    ax.text(0.5, 0.90, 'Quick visual guide to your meal\'s nutritional profile',
            ha='center', va='top', fontsize=12, style='italic', color='gray')

    # Categories
    nutrients_to_check = {
        'Macronutrients': ['Protein (g)', 'Carbohydrates digestible (g)', 'Total fiber (g)'],
        'Minerals': ['Calcium', 'Iron', 'Magnesium', 'Zinc'],
        'Vitamins': ['Vitamin A(µg)', 'Vitamin C', 'Vitamin D(µg)', 'Folate(µg)'],
        'Limit These': ['Sodium', 'SFA']
    }

    y_start = 0.80
    section_height = 0.18

    for category, nutrients in nutrients_to_check.items():
        # Category header
        ax.text(0.05, y_start, category, fontsize=14, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.3))

        # Draw nutrient boxes
        x_pos = 0.05
        y_pos = y_start - 0.04
        box_width = 0.18

        for nutrient in nutrients:
            if nutrient in totals and nutrient in DAILY_VALUES:
                meal_val = totals.get(nutrient, 0.0)
                rdv = DAILY_VALUES.get(nutrient, 1.0)
                percentage = (meal_val / rdv) * 100

                # Determine traffic light color
                if category == 'Limit These':
                    # Lower is better
                    if percentage <= 30:
                        color = '#22C55E'  # Green
                        status = '✓'
                    elif percentage <= 60:
                        color = '#F59E0B'  # Amber
                        status = '!'
                    else:
                        color = '#EF4444'  # Red
                        status = '✗'
                else:
                    # Higher is better
                    if percentage >= 50:
                        color = '#22C55E'  # Green
                        status = '✓'
                    elif percentage >= 25:
                        color = '#F59E0B'  # Amber
                        status = '!'
                    else:
                        color = '#EF4444'  # Red
                        status = '✗'

                # Draw box
                box = mpatches.FancyBboxPatch(
                    (x_pos, y_pos - 0.08), box_width, 0.08,
                    boxstyle="round,pad=0.01",
                    facecolor=color, alpha=0.2,
                    edgecolor=color, linewidth=2
                )
                ax.add_patch(box)

                # Status symbol
                ax.text(x_pos + 0.02, y_pos - 0.04, status,
                        fontsize=16, fontweight='bold', color=color,
                        va='center')

                # Nutrient name
                nutrient_short = nutrient.replace('(g)', '').replace('(µg)', '').replace(' digestible', '').strip()
                ax.text(x_pos + 0.05, y_pos - 0.04, nutrient_short,
                        fontsize=9, va='center', fontweight='bold')

                # Percentage
                ax.text(x_pos + box_width - 0.02, y_pos - 0.04, f'{percentage:.0f}%',
                        fontsize=9, ha='right', va='center', color=color,
                        fontweight='bold')

                x_pos += box_width + 0.02
                if x_pos > 0.85:
                    x_pos = 0.05
                    y_pos -= 0.10

        y_start -= section_height

    # Legend
    legend_y = 0.08
    ax.text(0.2, legend_y, '✓ = Good', fontsize=11, color='#22C55E', fontweight='bold')
    ax.text(0.4, legend_y, '! = Fair', fontsize=11, color='#F59E0B', fontweight='bold')
    ax.text(0.6, legend_y, '✗ = Needs Attention', fontsize=11, color='#EF4444', fontweight='bold')

    return fig


def generate_comparison_visualizations(totals: Dict) -> Dict[str, plt.Figure]:
    """
    Generate all comparison visualizations
    """
    figures = {}

    figures['daily_value_comparison'] = create_daily_value_comparison(totals)
    figures['traffic_light_chart'] = create_traffic_light_chart(totals)

    return figures