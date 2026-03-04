"""
Enhanced Visualizations for NutriScanner
Beautiful, modern, eye-catching charts
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
from matplotlib.patches import Circle, Rectangle, FancyBboxPatch, Wedge
import matplotlib.patheffects as path_effects
from typing import Dict, List, Any

# Modern color palettes
MODERN_COLORS = {
    'primary': '#6C63FF',  # Vibrant purple
    'secondary': '#FF6584',  # Coral pink
    'success': '#00D4AA',  # Mint green
    'warning': '#FFB800',  # Golden yellow
    'danger': '#FF5757',  # Red
    'info': '#4FC3F7',  # Sky blue
    'dark': '#2D3436',  # Dark gray
    'light': '#F8F9FA',  # Off white
}

GRADIENT_COLORS = {
    'excellent': ['#00F260', '#0575E6'],  # Green to blue
    'good': ['#FFB75E', '#ED8F03'],  # Orange gradient
    'fair': ['#FFA07A', '#FF6347'],  # Light to dark orange
    'poor': ['#FF512F', '#DD2476'],  # Red gradient
}

MACRO_COLORS = {
    'carbs': '#FF6B9D',  # Pink
    'protein': '#4ECDC4',  # Teal
    'fat': '#FFE66D',  # Yellow
}


def set_modern_style():
    """Set modern, beautiful matplotlib style"""
    plt.style.use('seaborn-v0_8-whitegrid')

    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.sans-serif': ['Inter', 'Arial', 'Helvetica', 'DejaVu Sans'],
        'font.size': 11,
        'axes.labelsize': 12,
        'axes.titlesize': 14,
        'axes.titleweight': 'bold',
        'axes.labelweight': 'bold',
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'legend.fontsize': 10,
        'figure.titlesize': 18,
        'figure.titleweight': 'bold',
        'axes.spines.top': False,
        'axes.spines.right': False,
        'axes.grid': True,
        'grid.alpha': 0.3,
        'grid.linestyle': '--',
    })


def create_gradient_bar(ax, x, y, width, height, color_start, color_end, orientation='vertical'):
    """Create a beautiful gradient-filled bar"""
    if orientation == 'vertical':
        gradient = np.linspace(0, 1, 256).reshape(256, 1)
    else:
        gradient = np.linspace(0, 1, 256).reshape(1, 256)

    from matplotlib.colors import LinearSegmentedColormap
    cmap = LinearSegmentedColormap.from_list('custom', [color_start, color_end])

    if orientation == 'vertical':
        ax.imshow(gradient, extent=[x, x + width, y, y + height],
                  aspect='auto', cmap=cmap, zorder=1)
    else:
        ax.imshow(gradient.T, extent=[x, x + width, y, y + height],
                  aspect='auto', cmap=cmap, zorder=1)


def create_modern_dashboard(totals: Dict, indexes: Dict, items: List) -> plt.Figure:
    """
    Create a stunning modern dashboard
    """
    set_modern_style()

    fig = plt.figure(figsize=(20, 12), facecolor='#F8F9FA')
    gs = GridSpec(3, 4, figure=fig, hspace=0.4, wspace=0.4,
                  left=0.08, right=0.95, top=0.93, bottom=0.05)

    # ========================================================================
    # TOP LEFT: Beautiful Macronutrient Donut Chart
    # ========================================================================
    ax1 = fig.add_subplot(gs[0, :2])

    carbs_g = totals.get("Carbohydrates digestible (g)", 0.0)
    protein_g = totals.get("Protein (g)", 0.0)
    fat_g = totals.get("Fat (g)", 0.0)

    cal_carbs = max(0, carbs_g) * 4.0
    cal_protein = max(0, protein_g) * 4.0
    cal_fat = max(0, fat_g) * 9.0
    total_cal = cal_carbs + cal_protein + cal_fat

    if total_cal > 0:
        sizes = [cal_carbs, cal_protein, cal_fat]
        labels = ['Carbs', 'Protein', 'Fat']
        colors = [MACRO_COLORS['carbs'], MACRO_COLORS['protein'], MACRO_COLORS['fat']]

        # Create donut chart
        wedges, texts, autotexts = ax1.pie(
            sizes, labels=None, colors=colors,
            autopct='%1.1f%%', startangle=90,
            pctdistance=0.85, wedgeprops=dict(width=0.4, edgecolor='white', linewidth=3)
        )

        # Style percentage text
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(13)
            autotext.set_path_effects([path_effects.withStroke(linewidth=3, foreground='black', alpha=0.3)])

        # Add center circle for donut effect
        centre_circle = Circle((0, 0), 0.70, fc='#F8F9FA', linewidth=0)
        ax1.add_artist(centre_circle)

        # Add total calories in center
        ax1.text(0, 0.05, f'{total_cal:.0f}', ha='center', va='center',
                 fontsize=36, fontweight='bold', color=MODERN_COLORS['dark'])
        ax1.text(0, -0.15, 'kcal', ha='center', va='center',
                 fontsize=14, color=MODERN_COLORS['dark'], alpha=0.7)

        # Add legend with custom styling
        legend_elements = [
            mpatches.Patch(facecolor=colors[i],
                           label=f'{labels[i]}: {sizes[i]:.0f} cal ({sizes[i] / total_cal * 100:.1f}%)',
                           edgecolor='white', linewidth=2)
            for i in range(len(labels))
        ]
        ax1.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(0.85, 1),
                   frameon=True, fancybox=True, shadow=True, fontsize=11)

    ax1.set_title('💪 Macronutrient Distribution', fontsize=16, fontweight='bold',
                  color=MODERN_COLORS['dark'], pad=20)

    # ========================================================================
    # TOP RIGHT: Modern Health Score Gauge
    # ========================================================================
    ax2 = fig.add_subplot(gs[0, 2:])

    # Calculate overall health score (average of all indexes)
    overall_score = np.mean(list(indexes.values()))

    # Create semi-circular gauge
    theta = np.linspace(0, np.pi, 100)

    # Background arc
    r_outer = 1.0
    r_inner = 0.7

    # Determine color based on score
    if overall_score >= 75:
        score_color = MODERN_COLORS['success']
        score_label = 'Excellent'
    elif overall_score >= 60:
        score_color = MODERN_COLORS['info']
        score_label = 'Good'
    elif overall_score >= 40:
        score_color = MODERN_COLORS['warning']
        score_label = 'Fair'
    else:
        score_color = MODERN_COLORS['danger']
        score_label = 'Needs Attention'

    # Draw background gauge segments
    segments = [(0, 40, MODERN_COLORS['danger']),
                (40, 60, MODERN_COLORS['warning']),
                (60, 75, MODERN_COLORS['info']),
                (75, 100, MODERN_COLORS['success'])]

    for start, end, color in segments:
        theta_seg = np.linspace(np.pi * (1 - start / 100), np.pi * (1 - end / 100), 50)
        x_outer = r_outer * np.cos(theta_seg)
        y_outer = r_outer * np.sin(theta_seg)
        x_inner = r_inner * np.cos(theta_seg)
        y_inner = r_inner * np.sin(theta_seg)

        verts = list(zip(x_outer, y_outer)) + list(zip(x_inner[::-1], y_inner[::-1]))
        poly = mpatches.Polygon(verts, facecolor=color, alpha=0.2, edgecolor='none')
        ax2.add_patch(poly)

    # Draw score indicator
    score_angle = np.pi * (1 - overall_score / 100)
    indicator_length = 0.85
    ax2.plot([0, indicator_length * np.cos(score_angle)],
             [0, indicator_length * np.sin(score_angle)],
             color=score_color, linewidth=6, solid_capstyle='round', zorder=10)

    # Add center dot
    center_dot = Circle((0, 0), 0.08, fc=score_color, ec='white', linewidth=3, zorder=11)
    ax2.add_patch(center_dot)

    # Add score text
    ax2.text(0, -0.3, f'{overall_score:.0f}', ha='center', va='center',
             fontsize=48, fontweight='bold', color=score_color)
    ax2.text(0, -0.5, score_label, ha='center', va='center',
             fontsize=16, color=MODERN_COLORS['dark'], style='italic')

    # Add score labels
    score_positions = [(0, '0'), (40, '40'), (60, '60'), (75, '75'), (100, '100')]
    for score_val, label in score_positions:
        angle = np.pi * (1 - score_val / 100)
        x = 1.15 * np.cos(angle)
        y = 1.15 * np.sin(angle)
        ax2.text(x, y, label, ha='center', va='center', fontsize=10, color=MODERN_COLORS['dark'], alpha=0.6)

    ax2.set_xlim(-1.3, 1.3)
    ax2.set_ylim(-0.7, 1.3)
    ax2.axis('off')
    ax2.set_title('🎯 Overall Health Score', fontsize=16, fontweight='bold',
                  color=MODERN_COLORS['dark'], pad=10)

    # ========================================================================
    # MIDDLE: Beautiful Index Cards with Gradients
    # ========================================================================
    ax3 = fig.add_subplot(gs[1, :])
    ax3.axis('off')
    ax3.set_xlim(0, 5)
    ax3.set_ylim(0, 1.5)

    index_names_short = {
        'Carbohydrate Impact Score': '🍞 Carb Impact',
        'Sodium Density Score': '🧂 Sodium',
        'Energy Density Score': '⚡ Energy',
        'Nutrient Density Score': '🥗 Nutrients',
        'Fat Quality Score': '🥑 Fat Quality'
    }

    x_positions = np.linspace(0.5, 4.5, 5)

    for i, (idx_name, idx_value) in enumerate(indexes.items()):
        x = x_positions[i]

        # Determine color
        if idx_value >= 75:
            colors = GRADIENT_COLORS['excellent']
        elif idx_value >= 60:
            colors = GRADIENT_COLORS['good']
        elif idx_value >= 40:
            colors = GRADIENT_COLORS['fair']
        else:
            colors = GRADIENT_COLORS['poor']

        # Create card background
        card = FancyBboxPatch((x - 0.35, 0.1), 0.7, 1.2,
                              boxstyle="round,pad=0.05",
                              facecolor='white', edgecolor=colors[0],
                              linewidth=3, zorder=1)
        ax3.add_patch(card)

        # Add gradient bar for score
        bar_height = (idx_value / 100) * 0.7
        gradient_rect = Rectangle((x - 0.25, 0.3), 0.5, bar_height,
                                  facecolor=colors[0], edgecolor='none', zorder=2)
        ax3.add_patch(gradient_rect)

        # Add score value
        ax3.text(x, 0.3 + bar_height + 0.15, f'{idx_value:.0f}',
                 ha='center', va='center', fontsize=24, fontweight='bold',
                 color=colors[0], zorder=3)

        # Add label
        short_name = index_names_short.get(idx_name, idx_name)
        ax3.text(x, 1.35, short_name, ha='center', va='center',
                 fontsize=11, fontweight='bold', color=MODERN_COLORS['dark'],
                 wrap=True, zorder=3)

    ax3.text(2.5, 0.05, 'Health Index Scores', ha='center', va='bottom',
             fontsize=16, fontweight='bold', color=MODERN_COLORS['dark'])

    # ========================================================================
    # BOTTOM LEFT: Modern Nutrient Bars
    # ========================================================================
    ax4 = fig.add_subplot(gs[2, :2])

    nutrients = ['Fiber', 'Protein', 'Sodium', 'Sat. Fat']
    values = [
        totals.get('Total fiber (g)', 0),
        totals.get('Protein (g)', 0),
        totals.get('Sodium', 0) / 10,  # Scale down for visualization
        totals.get('SFA', 0)
    ]

    colors_nutrients = [MODERN_COLORS['success'], MODERN_COLORS['info'],
                        MODERN_COLORS['warning'], MODERN_COLORS['danger']]

    y_pos = np.arange(len(nutrients))

    # Create horizontal bars with rounded edges
    for i, (value, color) in enumerate(zip(values, colors_nutrients)):
        # Background bar
        bg_bar = FancyBboxPatch((0, i - 0.3), max(values) * 1.1, 0.6,
                                boxstyle="round,pad=0.02",
                                facecolor=color, alpha=0.1,
                                edgecolor='none', zorder=1)
        ax4.add_patch(bg_bar)

        # Value bar with gradient effect
        val_bar = FancyBboxPatch((0, i - 0.3), value, 0.6,
                                 boxstyle="round,pad=0.02",
                                 facecolor=color, alpha=0.8,
                                 edgecolor='white', linewidth=2, zorder=2)
        ax4.add_patch(val_bar)

        # Add value label
        ax4.text(value + max(values) * 0.02, i, f'{value:.1f}',
                 va='center', fontsize=12, fontweight='bold', color=color)

    ax4.set_yticks(y_pos)
    ax4.set_yticklabels(nutrients, fontsize=12, fontweight='bold')
    ax4.set_xlim(0, max(values) * 1.2)
    ax4.set_ylim(-0.5, len(nutrients) - 0.5)
    ax4.spines['left'].set_visible(False)
    ax4.spines['bottom'].set_visible(False)
    ax4.set_xticks([])
    ax4.set_title('📊 Key Nutrients', fontsize=16, fontweight='bold',
                  color=MODERN_COLORS['dark'], pad=15)
    ax4.grid(False)

    # ========================================================================
    # BOTTOM RIGHT: Micronutrient Radar
    # ========================================================================
    ax5 = fig.add_subplot(gs[2, 2:], projection='polar')

    micronutrients = ['Calcium', 'Iron', 'Zinc', 'Vitamin A(µg)', 'Vitamin C', 'Folate(µg)']
    micro_values = []

    daily_values = {
        'Calcium': 1300, 'Iron': 18, 'Zinc': 11,
        'Vitamin A(µg)': 900, 'Vitamin C': 90, 'Folate(µg)': 400
    }

    for nutrient in micronutrients:
        if nutrient in totals and nutrient in daily_values:
            percent_dv = min((totals[nutrient] / daily_values[nutrient]) * 100, 100)
            micro_values.append(percent_dv)
        else:
            micro_values.append(0)

    # Create radar chart
    angles = np.linspace(0, 2 * np.pi, len(micronutrients), endpoint=False).tolist()
    micro_values_plot = micro_values + micro_values[:1]
    angles_plot = angles + angles[:1]

    # Fill area with gradient effect
    ax5.fill(angles_plot, micro_values_plot, color=MODERN_COLORS['primary'],
             alpha=0.25, zorder=2)

    # Plot line
    ax5.plot(angles_plot, micro_values_plot, 'o-', linewidth=3,
             color=MODERN_COLORS['primary'], markersize=8,
             markerfacecolor='white', markeredgewidth=2, zorder=3)

    # Customize radar
    ax5.set_xticks(angles)
    labels = ['Ca', 'Fe', 'Zn', 'Vit A', 'Vit C', 'Folate']
    ax5.set_xticklabels(labels, fontsize=11, fontweight='bold')
    ax5.set_ylim(0, 100)
    ax5.set_yticks([25, 50, 75, 100])
    ax5.set_yticklabels(['25%', '50%', '75%', '100%'], fontsize=9, color='gray')
    ax5.grid(True, linestyle='--', alpha=0.4, color='gray')
    ax5.set_facecolor('#F8F9FA')
    ax5.spines['polar'].set_color('gray')
    ax5.spines['polar'].set_linewidth(2)

    # Add title
    ax5.set_title('🧬 Micronutrients (% DV)', fontsize=16, fontweight='bold',
                  color=MODERN_COLORS['dark'], pad=25)

    # ========================================================================
    # Main Title with Emoji
    # ========================================================================
    fig.suptitle('🍽️ NutriScanner - Premium Nutritional Analysis Dashboard',
                 fontsize=22, fontweight='bold', color=MODERN_COLORS['dark'], y=0.98)

    return fig


def create_minimal_scorecard(indexes: Dict) -> plt.Figure:
    """
    Create a minimal, elegant scorecard
    """
    set_modern_style()

    fig, ax = plt.subplots(figsize=(14, 10), facecolor='white')
    ax.axis('off')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    # Title
    title_text = ax.text(0.5, 0.92, '✨ Health Score Report',
                         ha='center', va='top', fontsize=28,
                         fontweight='bold', color=MODERN_COLORS['dark'])

    # Score cards
    y_start = 0.80
    card_height = 0.12
    spacing = 0.02

    index_info = [
        ('Carbohydrate Impact Score', '🍞'),
        ('Sodium Density Score', '🧂'),
        ('Energy Density Score', '⚡'),
        ('Nutrient Density Score', '🥗'),
        ('Fat Quality Score', '🥑')
    ]

    for i, ((idx_name, idx_value), (name, emoji)) in enumerate(zip(indexes.items(), index_info)):
        y = y_start - i * (card_height + spacing)

        # Determine color and label
        if idx_value >= 75:
            color = MODERN_COLORS['success']
            bg_color = '#E8F5E9'
            rating = 'Excellent ⭐⭐⭐'
        elif idx_value >= 60:
            color = MODERN_COLORS['info']
            bg_color = '#E3F2FD'
            rating = 'Good ⭐⭐'
        elif idx_value >= 40:
            color = MODERN_COLORS['warning']
            bg_color = '#FFF3E0'
            rating = 'Fair ⭐'
        else:
            color = MODERN_COLORS['danger']
            bg_color = '#FFEBEE'
            rating = 'Needs Work'

        # Card background
        card = FancyBboxPatch((0.05, y - card_height), 0.9, card_height,
                              boxstyle="round,pad=0.015",
                              facecolor=bg_color, edgecolor=color,
                              linewidth=3, zorder=1)
        ax.add_patch(card)

        # Emoji
        ax.text(0.08, y - card_height / 2, emoji, ha='center', va='center',
                fontsize=32, zorder=3)

        # Index name
        ax.text(0.15, y - card_height / 2, name, ha='left', va='center',
                fontsize=14, fontweight='bold', color=MODERN_COLORS['dark'], zorder=3)

        # Score with progress bar
        bar_width = 0.25
        bar_x = 0.55

        # Background bar
        bg_bar = Rectangle((bar_x, y - card_height / 2 - 0.015), bar_width, 0.03,
                           facecolor='#E0E0E0', edgecolor='none', zorder=2)
        ax.add_patch(bg_bar)

        # Value bar
        val_bar = Rectangle((bar_x, y - card_height / 2 - 0.015),
                            bar_width * (idx_value / 100), 0.03,
                            facecolor=color, edgecolor='none', zorder=3)
        ax.add_patch(val_bar)

        # Score number
        ax.text(0.85, y - card_height / 2, f'{idx_value:.0f}',
                ha='right', va='center', fontsize=28,
                fontweight='bold', color=color, zorder=3)

        # Rating
        ax.text(0.92, y - card_height / 2, rating,
                ha='right', va='center', fontsize=11,
                style='italic', color=color, zorder=3)

    # Footer
    ax.text(0.5, 0.03, '💡 Tip: Scores above 75 are excellent, 60-75 good, 40-60 fair',
            ha='center', va='bottom', fontsize=10, style='italic',
            color='gray', bbox=dict(boxstyle='round', facecolor='#F5F5F5', alpha=0.8))

    return fig


# Export function for your analyzer
def generate_beautiful_visualizations(totals: Dict, indexes: Dict, items: List) -> Dict[str, plt.Figure]:
    """
    Generate all beautiful visualizations

    Returns:
        Dictionary of figure names to matplotlib figures
    """
    figures = {}

    # Modern dashboard
    figures['modern_dashboard'] = create_modern_dashboard(totals, indexes, items)

    # Minimal scorecard
    figures['scorecard'] = create_minimal_scorecard(indexes)

    return figures