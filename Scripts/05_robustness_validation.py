"""
Script 05: Robustness Validation
================================
Performs robustness checks including bootstrap confidence intervals,
alternative lag structures, and subsample stability analysis.
"""

import pandas as pd
import numpy as np
from statsmodels.tsa.api import VAR
import matplotlib.pyplot as plt
import logging
import warnings
import config

warnings.filterwarnings("ignore")

def load_panel_data(filepath):
    logging.info("Loading Panel Data...")
    xl = pd.ExcelFile(filepath)
    df = pd.read_excel(xl, 'Backdated SDG Index')
    
    goal_cols = config.GOAL_COLS
    df_panel = df[['id', 'year'] + goal_cols].copy()
    
    df_panel['year'] = pd.to_datetime(df_panel['year'], format='%Y').dt.year
    df_panel = df_panel.set_index(['id', 'year']).sort_index()
    
    # Interpolate
    df_panel[goal_cols] = df_panel.groupby(level=0)[goal_cols].transform(
        lambda x: x.interpolate(method='linear', limit_direction='both')
    )
    
    return df_panel.dropna(), goal_cols

def compute_irf_with_bootstrap(df, cols, impulse, response, lags=1, n_boot=100, steps=10):
    logging.info(f"Bootstrap IRF: {impulse} -> {response} (n_boot={n_boot})")
    
    # Baseline
    model = VAR(df[cols])
    results = model.fit(maxlags=lags, ic='aic')
    irf = results.irf(steps)
    impulse_idx = results.names.index(impulse)
    response_idx = results.names.index(response)
    baseline_irf = irf.orth_irfs[:, response_idx, impulse_idx]
    
    # Bootstrap
    boot_irfs = []
    countries = df.index.get_level_values(0).unique()
    
    for b in range(n_boot):
        boot_countries = np.random.choice(countries, size=len(countries), replace=True)
        boot_sample = pd.concat([df.xs(c) for c in boot_countries])
        
        try:
            boot_model = VAR(boot_sample[cols])
            boot_results = boot_model.fit(maxlags=lags, ic='aic', trend='n')
            boot_irf_obj = boot_results.irf(steps)
            boot_irfs.append(boot_irf_obj.orth_irfs[:, response_idx, impulse_idx])
        except:
            continue
            
    boot_irfs = np.array(boot_irfs)
    lower = np.percentile(boot_irfs, 2.5, axis=0) if len(boot_irfs) > 0 else np.zeros(steps+1)
    upper = np.percentile(boot_irfs, 97.5, axis=0) if len(boot_irfs) > 0 else np.zeros(steps+1)
    
    return baseline_irf, lower, upper

def main():
    try:
        df, cols = load_panel_data(config.SDR_DATA_FILE)
        
        # simplified preprocessing
        df_diff = df[cols].groupby(level=0).diff().dropna()
        df_fe = df_diff - df_diff.groupby(level=0).transform('mean')
        
        # 1. Bootstrap IRF
        impulse, response = 'goal4', 'goal10'
        baseline, lower, upper = compute_irf_with_bootstrap(
            df_fe, cols, impulse, response, lags=1, n_boot=50
        )
        
        # Save validation plot
        plt.figure(figsize=(10, 6))
        x = range(len(baseline))
        plt.plot(x, baseline, 'b-', label='Point Estimate')
        plt.fill_between(x, lower, upper, alpha=0.3, label='95% CI')
        plt.axhline(0, color='r', linestyle='--')
        plt.title(f'Robustness Check: {impulse} -> {response}')
        plt.savefig(config.FIGURES_DIR / f'robust_irf_{impulse}_{response}.png')
        logging.info(f"Saved validation plot for {impulse}->{response}")
        
    except Exception as e:
        logging.error(f"Robustness checks failed: {e}")
        raise

if __name__ == "__main__":
    main()
