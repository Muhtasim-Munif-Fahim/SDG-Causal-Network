"""
Script 03: PCMCI+ Causal Discovery
==================================
Runs PCMCI+ algorithm to identify direct causal links and filter spurious correlations.
Uses a relaxed significance threshold (alpha=0.20) suitable for this small subset exploratory analysis.

Outputs:
    - pcmci_links.csv: Significant causal links found by PCMCI+
"""

import pandas as pd
import numpy as np
import logging
import warnings
import config

# Import tigramite
try:
    from tigramite import data_processing as pp
    from tigramite.pcmci import PCMCI
    from tigramite.independence_tests.parcorr_wls import ParCorrWLS
except ImportError:
    logging.warning("Tigramite not installed. PCMCI+ analysis will be skipped.")
    pp = None

warnings.filterwarnings("ignore")

def run_pcmci(df: pd.DataFrame, cols: list) -> pd.DataFrame:
    """Run PCMCI+ and return significant links."""
    if pp is None:
        return pd.DataFrame()

    logging.info("Initializing PCMCI+...")
    data = df[cols].values
    var_names = cols
    
    dataframe = pp.DataFrame(data, var_names=var_names)
    parcorr = ParCorrWLS(significance='analytic')
    pcmci = PCMCI(dataframe=dataframe, cond_ind_test=parcorr, verbosity=0)
    
    # Relaxed threshold for small sample / subset analysis
    alpha = 0.20 
    logging.info(f"Running PCMCI+ algorithm (alpha={alpha})...")
    results = pcmci.run_pcmciplus(tau_max=3, pc_alpha=alpha)
    
    # Extract links
    p_matrix = results['p_matrix']
    val_matrix = results['val_matrix']
    links = []
    
    for j in range(len(var_names)):
        for i in range(len(var_names)):
            for tau in range(p_matrix.shape[2]):
                # Filter out p-values > alpha
                # tau > 0 ensures we get lagged effects
                if p_matrix[i, j, tau] < alpha and tau > 0:
                    links.append({
                        'Source': var_names[i],
                        'Target': var_names[j],
                        'Lag': tau,
                        'Strength': val_matrix[i, j, tau],
                        'P_Value': p_matrix[i, j, tau]
                    })
    
    return pd.DataFrame(links)

def main():
    try:
        # Load and aggregate data
        xl = pd.ExcelFile(config.SDR_DATA_FILE)
        df_raw = pd.read_excel(xl, 'Backdated SDG Index')
        df_global = df_raw.groupby('year')[config.GOAL_COLS].mean().dropna()
        
        # Run PCMCI+
        links_df = run_pcmci(df_global, config.GOAL_COLS)
        
        # Save
        output_path = config.RESULTS_DIR / 'pcmci_links.csv'
        links_df.to_csv(output_path, index=False)
        logging.info(f"PCMCI+ links saved to {output_path}")
        logging.info(f"Found {len(links_df)} significant links.")
        
    except Exception as e:
        logging.error(f"PCMCI+ analysis failed: {e}")

if __name__ == "__main__":
    main()
