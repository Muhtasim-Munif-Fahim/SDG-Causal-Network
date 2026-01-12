"""
Script 04: Heterogeneity Analysis by Income Group
=================================================
Analyzes causal dynamics stratified by World Bank income classification.

Outputs:
    - heterogeneity_irf_data.csv: IRF data for different income groups
"""

import pandas as pd
import numpy as np
from statsmodels.tsa.api import VAR
import logging
import warnings
import config

warnings.filterwarnings("ignore")

def load_panel_data_with_income(filepath: str) -> pd.DataFrame:
    """Load panel data and map income groups."""
    logging.info("Loading Panel Data...")
    xl = pd.ExcelFile(filepath)
    df = pd.read_excel(xl, 'Backdated SDG Index')
    
    goal_cols = config.GOAL_COLS
    df_panel = df[['id', 'year'] + goal_cols].copy()
    
    # Map income groups
    df_panel['income_group'] = df_panel['id'].map(config.INCOME_MAPPING)
    df_panel = df_panel.dropna(subset=['income_group'])
    
    df_panel['year'] = pd.to_datetime(df_panel['year'], format='%Y').dt.year
    df_panel = df_panel.set_index(['id', 'year']).sort_index()
    
    # Interpolate
    df_panel[goal_cols] = df_panel.groupby(level=0)[goal_cols].transform(
        lambda x: x.interpolate(method='linear', limit_direction='both')
    )
    
    return df_panel.dropna()

def save_heterogeneity_results(results_dict: dict, steps: int = 10):
    """Save IRF results from all groups to a single CSV."""
    logging.info("Saving heterogeneity IRF data...")
    all_data = []
    
    for group, result in results_dict.items():
        irf = result.irf(steps)
        orth_irfs = irf.orth_irfs
        cols = result.names
        
        for i, response in enumerate(cols):
            for j, impulse in enumerate(cols):
                series = orth_irfs[:, i, j]
                for step, value in enumerate(series):
                    all_data.append({
                        'Group': group,
                        'Impulse': impulse,
                        'Response': response,
                        'Step': step,
                        'Value': value
                    })
    
    df_out = pd.DataFrame(all_data)
    output_path = config.RESULTS_DIR / 'heterogeneity_irf_data.csv'
    df_out.to_csv(output_path, index=False)
    logging.info(f"Saved to {output_path}")

def main():
    try:
        df = load_panel_data_with_income(config.SDR_DATA_FILE)
        cols = config.GOAL_COLS
        
        results_dict = {}
        for group, group_df in df.groupby('income_group'):
            logging.info(f"Processing group: {group} (N={len(group_df)})")
            
            # Simplified processing: difference & demean
            df_diff = group_df[cols].groupby(level=0).diff().dropna()
            df_fe = df_diff - df_diff.groupby(level=0).transform('mean')
            
            try:
                model = VAR(df_fe)
                results = model.fit(maxlags=1)
                results_dict[group] = results
            except Exception as e:
                logging.warning(f"Could not fit VAR for {group}: {e}")
        
        save_heterogeneity_results(results_dict)
        
    except Exception as e:
        logging.error(f"Heterogeneity analysis failed: {e}")
        raise

if __name__ == "__main__":
    main()
