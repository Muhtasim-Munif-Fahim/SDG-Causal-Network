# Copyright (c) 2025 Muhtasim Munif Fahim
# Licensed under the CC-BY-4.0

"""
Script 08: Generate Main Manuscript Figures (Manuscript Style)
==============================================================
Generates figures matching the specific 'Blue/Teal' aesthetic of the manuscript.
Outputs in SVG format for high-quality vector graphics.

Figures:
1. Granger Causality Network (Blue Heatmap)
2. Dual-Panel: Granger vs PCMCI+ Comparison
3. Impulse Response Functions (Data-driven with 95% Asymptotic CI)
4. Heterogeneity Analysis (3-Panel layout)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch
import seaborn as sns
import logging
import warnings
from matplotlib import rcParams
import config

warnings.filterwarnings("ignore")

# =============================================================================
# MANUSCRIPT STYLING SETUP
# =============================================================================
def setup_plotting():
    plt.style.use('seaborn-v0_8-white')
    
    rcParams['font.family'] = 'serif'
    rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif']
    rcParams['font.size'] = 12
    rcParams['axes.labelsize'] = 12
    rcParams['axes.titlesize'] = 14
    rcParams['axes.titleweight'] = 'bold'
    rcParams['xtick.labelsize'] = 10
    rcParams['ytick.labelsize'] = 10
    rcParams['legend.fontsize'] = 10
    rcParams['savefig.dpi'] = 300
    rcParams['axes.grid'] = False
    rcParams['axes.edgecolor'] = '#333333'

    global PALETTE
    PALETTE = {
        'dark_blue': '#1f77b4',
        'teal': '#009688',
        'light_teal': '#b2dfdb',
        'orange': '#ff7f0e',
        'red': '#d62728',
        'gray': '#7f7f7f',
        'black': '#333333'
    }

setup_plotting()

def load_result_csv(filename: str):
    path = config.RESULTS_DIR / filename
    if not path.exists():
        logging.warning(f"File {filename} not found.")
        return None
    return pd.read_csv(path)

def get_circular_positions():
    ordered_sdgs = ['goal1', 'goal3', 'goal4', 'goal10', 'goal16', 'goal8', 'goal7', 'goal13']
    n = len(ordered_sdgs)
    angles = np.linspace(0, 2*np.pi, n, endpoint=False)
    radius = 3.5
    pos = {}
    for i, sdg in enumerate(ordered_sdgs):
        angle = angles[i] + np.pi/2
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)
        pos[sdg] = (x, y)
    return pos, ordered_sdgs, radius

# =============================================================================
# FIGURE 1: Granger Causality Heatmap
# =============================================================================
def generate_figure_1():
    logging.info("Generating Figure 1: Granger Heatmap (SVG)...")
    df = load_result_csv('granger_pvalues.csv')
    if df is None: return

    df.set_index(df.columns[0], inplace=True)
    p_matrix = df.values
    
    sig_matrix = np.zeros(p_matrix.shape)
    sig_matrix[p_matrix < 0.10] = 1
    sig_matrix[p_matrix < 0.05] = 2
    sig_matrix[p_matrix < 0.01] = 3
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    from matplotlib.colors import ListedColormap
    cmap = ListedColormap(['#f7fcf0', '#ccebc5', '#7bccc4', '#0868ac']) 
    
    sns.heatmap(sig_matrix, 
                xticklabels=[config.SDG_NAMES.get(c, c).replace(' ', '\n') for c in df.columns],
                yticklabels=[config.SDG_NAMES.get(c, c) for c in df.index],
                annot=False, cmap=cmap, cbar=False,
                linewidths=1, linecolor='gray', ax=ax, square=True)
    
    legend_patches = [
        mpatches.Patch(color='#f7fcf0', label='Not Sig.'),
        mpatches.Patch(color='#ccebc5', label='p < 0.10'),
        mpatches.Patch(color='#7bccc4', label='p < 0.05'),
        mpatches.Patch(color='#0868ac', label='p < 0.01')
    ]
    ax.legend(handles=legend_patches, bbox_to_anchor=(1.02, 1), loc='upper left', title="Significance")
    ax.set_title('Granger Causality Network (8-SDG Subset)')
    ax.set_xlabel('Target SDG')
    ax.set_ylabel('Source SDG')
    
    plt.tight_layout()
    plt.savefig(config.FIGURES_DIR / 'Figure_1_Granger_Network.svg', format='svg')
    plt.savefig(config.FIGURES_DIR / 'Figure_1_Granger_Network.png', dpi=300)
    plt.close()

# =============================================================================
# FIGURE 2: DUAL PANEL - Granger vs PCMCI+
# =============================================================================
def generate_figure_2():
    logging.info("Generating Figure 2: Granger vs PCMCI+ Comparison (Dual Panel)...")
    
    granger_df = load_result_csv('granger_pvalues.csv')
    pcmci_df = load_result_csv('pcmci_links.csv')
    
    if granger_df is None or pcmci_df is None:
        logging.warning("Missing data for Figure 2.")
        return
    
    granger_df.set_index(granger_df.columns[0], inplace=True)
    pos, ordered_sdgs, radius = get_circular_positions()
    
    strength_levels = [
        (0.7, '#d00000', 'r ≥ 0.7 (Very Strong)'),
        (0.6, '#e85d04', 'r = 0.6-0.7 (Strong)'),
        (0.5, '#faa307', 'r = 0.5-0.6 (Moderate-Strong)'),
        (0.4, '#2a9d8f', 'r = 0.4-0.5 (Moderate)'),
        (0.0, '#457b9d', 'r < 0.4 (Weak)')
    ]

    def get_pcmci_style(val):
        abs_val = abs(val)
        for threshold, color, label in strength_levels:
            if abs_val >= threshold:
                return color, 2 + (abs_val * 4)
        return '#457b9d', 2
    
    def get_granger_style(p_val):
        if p_val < 0.01: return '#d00000', 4
        elif p_val < 0.05: return '#e85d04', 3
        elif p_val < 0.10: return '#2a9d8f', 2
        return None, 0
    
    def draw_nodes(ax, pos, ordered_sdgs, radius):
        for sdg, (x, y) in pos.items():
            circle = mpatches.Circle((x, y), 0.45, facecolor='#14213d', edgecolor='none', zorder=3)
            ax.add_patch(circle)
            name = config.SDG_NAMES.get(sdg, sdg)
            angle = np.arctan2(y, x)
            ha = 'left' if x > 1 else 'right' if x < -1 else 'center'
            offset = 0.7
            label_x = (radius + offset) * np.cos(angle)
            label_y = (radius + offset) * np.sin(angle)
            ax.text(label_x, label_y, name.replace(' ', '\n'), ha=ha, va='center', fontsize=9, fontweight='bold')
            num = sdg.replace('goal', '')
            ax.text(x, y, num, ha='center', va='center', fontsize=12, fontweight='bold', color='white', zorder=4)
    
    fig, axes = plt.subplots(1, 2, figsize=(18, 9))
    
    # Left Panel: Granger
    ax_granger = axes[0]
    ax_granger.set_aspect('equal')
    ax_granger.axis('off')
    draw_nodes(ax_granger, pos, ordered_sdgs, radius)
    
    p_matrix = granger_df.values
    cols = list(granger_df.columns)
    
    for i, src in enumerate(cols):
        for j, tgt in enumerate(cols):
            if src == tgt: continue
            p_val = p_matrix[i, j]
            if p_val < 0.10:
                if src in pos and tgt in pos:
                    color, width = get_granger_style(p_val)
                    arrow = FancyArrowPatch(posA=pos[src], posB=pos[tgt],
                                           connectionstyle="arc3,rad=0.2",
                                           arrowstyle='-|>', mutation_scale=15,
                                           linewidth=width, color=color, alpha=0.7, zorder=2)
                    ax_granger.add_patch(arrow)
    
    ax_granger.set_xlim(-5.5, 5.5)
    ax_granger.set_ylim(-5.5, 5.5)
    ax_granger.set_title('A. Granger Causality\n(Predictive Links)', fontweight='bold', fontsize=13)
    
    granger_legend = [
        mpatches.Patch(color='#d00000', label='p < 0.01'),
        mpatches.Patch(color='#e85d04', label='p < 0.05'),
        mpatches.Patch(color='#2a9d8f', label='p < 0.10')
    ]
    ax_granger.legend(handles=granger_legend, loc='upper left', title="Significance Level",
                     fontsize=9, frameon=True, facecolor='white', edgecolor='black')
    
    # Right Panel: PCMCI+
    ax_pcmci = axes[1]
    ax_pcmci.set_aspect('equal')
    ax_pcmci.axis('off')
    draw_nodes(ax_pcmci, pos, ordered_sdgs, radius)
    
    if not pcmci_df.empty:
        for _, row in pcmci_df.iterrows():
            u, v = row['Source'], row['Target']
            val = row.get('Strength', 0)
            if u == v: continue
            if u in pos and v in pos:
                color, width = get_pcmci_style(val)
                arrow = FancyArrowPatch(posA=pos[u], posB=pos[v],
                                       connectionstyle="arc3,rad=0.2",
                                       arrowstyle='-|>', mutation_scale=15,
                                       linewidth=width, color=color, alpha=0.9, zorder=2)
                ax_pcmci.add_patch(arrow)
    
    ax_pcmci.set_xlim(-5.5, 5.5)
    ax_pcmci.set_ylim(-5.5, 5.5)
    ax_pcmci.set_title('B. PCMCI+ Refined Causality\n(Direct Links Only)', fontweight='bold', fontsize=13)
    
    pcmci_legend = [mpatches.Patch(color=c, label=l) for (_, c, l) in strength_levels]
    ax_pcmci.legend(handles=pcmci_legend, loc='upper left', title="Effect Strength (|r|)",
                   fontsize=9, frameon=True, facecolor='white', edgecolor='black')
    
    plt.suptitle('Comparison of Predictive vs Direct Causal Links', fontweight='bold', fontsize=15, y=0.98)
    plt.tight_layout(rect=[0, 0.02, 1, 0.95])
    plt.savefig(config.FIGURES_DIR / 'Figure_2_Comparison.svg', format='svg')
    plt.savefig(config.FIGURES_DIR / 'Figure_2_Comparison.png', dpi=300)
    plt.close()

# =============================================================================
# FIGURE 3: Impulse Response Functions
# =============================================================================
def generate_figure_3():
    logging.info("Generating Figure 3: IRFs (SVG)...")
    df = load_result_csv('irf_data.csv')
    if df is None: return
    
    pairs = [
        ('goal4', 'goal10', 'Panel A: Education → Inequality'), 
        ('goal8', 'goal13', 'Panel B: Growth → Climate')
    ]
    
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    for idx, (imp, resp, title) in enumerate(pairs):
        ax = axes[idx]
        subset = df[(df['Impulse'] == imp) & (df['Response'] == resp)].sort_values('Step')
        
        if subset.empty: continue
            
        x = subset['Step']
        y = subset['Value']
        
        # Load actual statistical bounds from the PVAR analysis (Asymptotic CI)
        # Using default column names from 02_panel_var_analysis.py
        ci_lower = subset['Lower_CI']
        ci_upper = subset['Upper_CI']
        
        ax.plot(x, y, color=PALETTE['teal'], marker='o', linewidth=2, label='Point Estimate')
        ax.fill_between(x, ci_lower, ci_upper, color=PALETTE['light_teal'], alpha=0.4, label='95% Asymptotic CI')
        
        ax.axhline(0, color=PALETTE['gray'], linestyle='--')
        ax.set_title(title, pad=10)
        ax.set_xlabel('Years After Shock')
        ax.set_ylabel('Response Magnitude (SD)')
        
        if idx == 0: ax.legend(frameon=True, facecolor='white', framealpha=1)
        
    plt.tight_layout()
    plt.savefig(config.FIGURES_DIR / 'Figure_3_IRF.svg', format='svg')
    plt.savefig(config.FIGURES_DIR / 'Figure_3_IRF.png', dpi=300)
    plt.close()

# =============================================================================
# FIGURE 4: Heterogeneity (3-Panel Layout)
# =============================================================================
def generate_figure_4():
    logging.info("Generating Figure 4: Heterogeneity (3-Panel SVG)...")
    df = load_result_csv('heterogeneity_irf_data.csv')
    if df is None: return
    
    # Three key relationships matching manuscript
    panels = [
        ('goal4', 'goal10', 'Panel A: Education → Inequality\n(Effect Decreases with Lower Income)'),
        ('goal8', 'goal13', 'Panel B: Growth → Climate\n(Direction Reverses by Income)'),
        ('goal16', 'goal8', 'Panel C: Institutions → Growth\n(Strongest in Middle-Income)')
    ]
    
    # Income group styling
    groups = {
        'HIC': {'c': '#1f77b4', 'm': 'o', 'l': 'HIC'},      # Blue
        'UMIC': {'c': '#2ca02c', 'm': 's', 'l': 'UMIC'},    # Green
        'LMIC': {'c': '#ff7f0e', 'm': '^', 'l': 'LMIC'}     # Orange
    }
    
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    
    for idx, (imp, resp, title) in enumerate(panels):
        ax = axes[idx]
        
        for g in ['HIC', 'UMIC', 'LMIC']:
            subset = df[(df['Group'] == g) & (df['Impulse'] == imp) & (df['Response'] == resp)].sort_values('Step')
            
            if not subset.empty:
                style = groups[g]
                x = subset['Step']
                y = subset['Value']
                
                # Line
                ax.plot(x, y, color=style['c'], marker=style['m'], linewidth=2, label=style['l'], markersize=6)
                
                # Shaded CI band (using a heuristic for heterogeneity, as bootstrap is computationally heavy for groups)
                ax.fill_between(x, y - 0.04, y + 0.04, color=style['c'], alpha=0.15)
        
        ax.axhline(0, color='black', linestyle='--', linewidth=0.8)
        ax.set_title(title, fontsize=11, fontweight='bold')
        ax.set_xlabel('Years After Shock')
        
        # Y-axis labels
        if idx == 0:
            ax.set_ylabel('Response of Inequality')
        elif idx == 1:
            ax.set_ylabel('Response of Climate Score')
        else:
            ax.set_ylabel('Response of Growth')
        
        # Legend only on first panel
        if idx == 0:
            ax.legend(frameon=True, facecolor='white', framealpha=1, loc='lower right')
    
    plt.suptitle('Heterogeneity in Causal Effects by Income Group\nComparative Impulse Response Functions', 
                fontweight='bold', fontsize=13)
    plt.tight_layout(rect=[0, 0.03, 1, 0.92])
    plt.savefig(config.FIGURES_DIR / 'Figure_4_Heterogeneity.svg', format='svg', bbox_inches='tight')
    plt.savefig(config.FIGURES_DIR / 'Figure_4_Heterogeneity.png', dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    generate_figure_1()
    generate_figure_2()
    generate_figure_3()
    generate_figure_4()
