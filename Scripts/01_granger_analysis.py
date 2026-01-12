# Copyright (c) 2025 Muhtasim Munif Fahim
# Licensed under the CC-BY-4.0

"""
Script 01: Pairwise Granger Causality Analysis
==============================================
Performs pairwise Granger causality tests on the 8-SDG subset pairs to identify
potential predictive relationships.

Outputs:
    - granger_pvalues.csv: Matrix of p-values
    - causal_graph.png: Network visualization of significant links
"""

import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller, grangercausalitytests
import logging
import warnings
from typing import Tuple

# Import project configuration
import config

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

def load_and_preprocess(filepath: str) -> Tuple[pd.DataFrame, list]:
    """
    Load data and aggregate to global time series.
    """
    logging.info(f"Loading data from {filepath}...")
    try:
        xl = pd.ExcelFile(filepath)
        df = pd.read_excel(xl, 'Backdated SDG Index')
        
        # Select Goal columns (Now defaults to 8-SDG subset from config)
        goal_cols = config.GOAL_COLS
        
        # Group by year to get Global Average
        df_global = df.groupby('year')[goal_cols].mean().dropna()
        
        logging.info(f"Data aggregation complete. Shape: {df_global.shape}")
        return df_global, goal_cols
        
    except FileNotFoundError:
        logging.error(f"Data file not found at {filepath}")
        raise
    except Exception as e:
        logging.error(f"Error loading data: {e}")
        raise

def check_stationarity(df: pd.DataFrame, cols: list) -> pd.DataFrame:
    """
    Check for stationarity using ADF test and difference if necessary.
    """
    logging.info("Checking stationarity (ADF Test)...")
    stationary_df = df.copy()
    diff_count = 0
    
    for col in cols:
        result = adfuller(df[col].dropna())
        p_value = result[1]
        
        if p_value > 0.05:
            logging.debug(f"{col} is non-stationary (p={p_value:.3f}), differencing...")
            stationary_df[col] = df[col].diff()
            diff_count += 1
    
    stationary_df = stationary_df.dropna()
    logging.info(f"Differenced {diff_count} variables to achieve stationarity.")
    return stationary_df

def run_granger_causality(df: pd.DataFrame, cols: list, maxlag: int = 2) -> Tuple[np.ndarray, np.ndarray]:
    """
    Run pairwise Granger causality tests.
    """
    logging.info(f"Running Pairwise Granger Causality (Max Lag: {maxlag})...")
    n = len(cols)
    p_matrix = np.zeros((n, n))
    adj_matrix = np.zeros((n, n))
    
    for i, target in enumerate(cols):
        for j, source in enumerate(cols):
            if i == j:
                continue
            
            data = df[[target, source]]
            
            try:
                # Run Granger test
                gc_res = grangercausalitytests(data, maxlag=maxlag, verbose=False)
                
                # Get minimum p-value across all lags
                p_values = [gc_res[lag][0]['ssr_ftest'][1] for lag in range(1, maxlag+1)]
                min_p = min(p_values)
                
                p_matrix[j, i] = min_p # Source (j) -> Target (i)
                
                if min_p < 0.05:
                    adj_matrix[j, i] = 1
                    
            except (ValueError, KeyError) as e:
                logging.warning(f"Granger test failed for {source} -> {target}: {e}")
            except Exception as e:
                logging.error(f"Unexpected error for {source} -> {target}: {e}")
                
    return adj_matrix, p_matrix

def plot_causal_graph(adj_matrix: np.ndarray, cols: list) -> None:
    """
    Visualize the causal graph.
    """
    logging.info("Generating Causal Graph visualization...")
    G = nx.DiGraph()
    
    # Add nodes using config names
    labels = {i: config.SDG_NAMES.get(col, col) for i, col in enumerate(cols)}
    for i in range(len(cols)):
        G.add_node(i, label=labels[i])
    
    # Add edges
    rows, cols_idxs = np.where(adj_matrix == 1)
    for r, c in zip(rows, cols_idxs):
        G.add_edge(r, c)
        
    plt.figure(figsize=(10, 8))
    pos = nx.circular_layout(G)
    
    # Draw graph components
    nx.draw_networkx_nodes(G, pos, node_size=2000, node_color='lightblue', alpha=0.9)
    nx.draw_networkx_edges(G, pos, width=1.5, alpha=0.6, arrowsize=20, edge_color='gray')
    nx.draw_networkx_labels(G, pos, labels, font_size=10, font_weight='bold')
    
    plt.title("Causal Architecture (8-SDG Subset)\nPairwise Granger Causality (p < 0.05)", fontsize=16)
    plt.axis('off')
    plt.tight_layout()
    
    output_path = config.FIGURES_DIR / 'causal_graph.png'
    plt.savefig(output_path, dpi=300)
    logging.info(f"Graph saved to {output_path}")

def main():
    """Main execution function."""
    try:
        # Load data
        df, cols = load_and_preprocess(config.SDR_DATA_FILE)
        logging.info(f"Analyzing {len(cols)} SDGs: {cols}")
        
        # Ensure data exists
        if df.empty:
            logging.error("DataFrame is empty. Exiting.")
            return

        # Stationarity check
        df_stationary = check_stationarity(df, cols)
        
        # Run Analysis
        adj_matrix, p_matrix = run_granger_causality(df_stationary, cols, maxlag=2)
        
        # Save results
        results_df = pd.DataFrame(p_matrix, index=cols, columns=cols)
        results_df.to_csv(config.GRANGER_PVALUES_FILE)
        logging.info(f"P-value matrix saved to {config.GRANGER_PVALUES_FILE}")
        
        # Visualization
        plot_causal_graph(adj_matrix, cols)
        
        # Summary
        edge_count = np.sum(adj_matrix)
        logging.info(f"Analysis Complete. Found {int(edge_count)} significant causal links.")
        
    except Exception as e:
        logging.critical(f"Analysis failed: {e}")
        raise

if __name__ == "__main__":
    main()
