# Copyright (c) 2025 Muhtasim Munif Fahim
# Licensed under the CC-BY-4.0

"""
Script 02: Panel VAR Analysis
=============================
Fits a Panel Vector Autoregression (PVAR) model to the 8-SDG subset data.
Calculates Impulse Response Functions (IRFs) with 95% Asymptotic Confidence Intervals.

Outputs:
    - irf_data.csv: IRF value and CI bounds for visualization
"""

import pandas as pd
import numpy as np
from statsmodels.tsa.api import VAR
from statsmodels.tsa.stattools import adfuller
import logging
import warnings
import config

warnings.filterwarnings("ignore")

def load_panel_data(filepath: str):
    logging.info("Loading Panel Data...")
    xl = pd.ExcelFile(filepath)
    df = pd.read_excel(xl, 'Backdated SDG Index')
    
    goal_cols = config.GOAL_COLS
    id_cols = ['id', 'year']
    
    df_panel = df[id_cols + goal_cols].copy()
    df_panel['year'] = pd.to_datetime(df_panel['year'], format='%Y').dt.year
    df_panel = df_panel.set_index(['id', 'year']).sort_index()
    
    # Interpolate missing values
    df_panel[goal_cols] = df_panel.groupby(level=0)[goal_cols].transform(
        lambda x: x.interpolate(method='linear', limit_direction='both')
    )
    
    df_panel = df_panel.dropna()
    logging.info(f"Panel Data Shape: {df_panel.shape}")
    return df_panel, goal_cols

def check_panel_stationarity(df, cols):
    logging.info("Checking Panel Stationarity...")
    stationary_df = df.copy()
    diff_needed = []
    
    for col in cols:
        p_values = []
        countries = df.index.get_level_values(0).unique()
        for country in countries:
            series = df.xs(country)[col]
            if len(series) > 10 and series.nunique() > 1:
                try:
                    res = adfuller(series, autolag='AIC')
                    p_values.append(res[1])
                except:
                    pass
        
        if p_values and np.median(p_values) > 0.05:
            diff_needed.append(col)
    
    if diff_needed:
        logging.info(f"Differencing variables: {diff_needed}")
        for col in diff_needed:
            stationary_df[col] = stationary_df.groupby(level=0)[col].diff()
        stationary_df = stationary_df.dropna()
        
    return stationary_df

def remove_fixed_effects(df):
    logging.info("Removing Fixed Effects (Demeaning)...")
    return df - df.groupby(level=0).transform('mean')

def save_irf_data(results, cols: list, steps: int = 10):
    """Save IRF data with statistically rigorous Confidence Intervals."""
    logging.info(f"Generating Impulse Response Functions (Steps: {steps})...")
    
    # Generate Orthogonal IRFs
    irf = results.irf(steps)
    orth_irfs = irf.orth_irfs
    
    # Calculate 95% Confidence Intervals manually using VAR.stderr()
    # statsmodels IRF.stderr() returns a (steps+1, neqs, neqs) array of standard errors
    se_matrix = irf.stderr()
    
    # 95% CI coefficient is 1.96 for asymptotic normality
    lower_band = orth_irfs - (1.96 * se_matrix)
    upper_band = orth_irfs + (1.96 * se_matrix)
    
    irf_data = []
    
    for i, response in enumerate(cols):
        for j, impulse in enumerate(cols):
            # Impulse j -> Response i
            # Dimension indices in statsmodels are (step, response, impulse)
            point_estimates = orth_irfs[:, i, j]
            low_bounds = lower_band[:, i, j]
            high_bounds = upper_band[:, i, j]
            
            for step in range(steps + 1):
                irf_data.append({
                    'Impulse': impulse,
                    'Response': response,
                    'Step': step,
                    'Value': point_estimates[step],
                    'Lower_CI': low_bounds[step],
                    'Upper_CI': high_bounds[step]
                })
    
    df_irf = pd.DataFrame(irf_data)
    df_irf.to_csv(config.IRF_DATA_FILE, index=False)
    logging.info(f"Scientifically robust IRF data saved to {config.IRF_DATA_FILE}")

def main():
    try:
        df, cols = load_panel_data(config.SDR_DATA_FILE)
        logging.info(f"Analyzing {len(cols)} SDGs in strategic subset.")
        
        df_stat = check_panel_stationarity(df, cols)
        df_fe = remove_fixed_effects(df_stat)
        
        logging.info("Fitting PVAR model (maxlags=1, ic=AIC)...")
        model = VAR(df_fe)
        results = model.fit(maxlags=1, ic='aic')
        
        logging.info("VAR model fitted successfully.")
        
        # Save IRF Data
        save_irf_data(results, cols)
        
    except Exception as e:
        logging.critical(f"Panel VAR analysis failed: {e}")
        raise

if __name__ == "__main__":
    main()
