# Distributed Causality in the SDG Network

A comprehensive Panel VAR and PCMCI+ analysis exploring causal relationships among the 17 Sustainable Development Goals (SDGs) using the Sustainable Development Report 2025 data.

## Overview

This repository contains the analysis code and data for the research paper *"Distributed Causality in the Sustainable Development Goal Network: A Panel VAR and PCMCI+ Analysis"*. The study investigates dynamic causal relationships among SDGs across 166 countries from 2000-2025.

### Key Findings

- **70 significant Granger-causal links** identified among 17 SDGs
- **11 direct causal relationships** confirmed by PCMCI+ after filtering spurious correlations
- **Heterogeneous effects** by income group: Education → Inequality strongest in high-income countries
- **Growth-Climate nexus**: Decoupling in HICs, resource-intensive growth in LMICs

## Project Structure

```
SDG Time Series/
├── Data/                          # Source data files
│   └── SDR2025-data.xlsx          # Sustainable Development Report 2025
├── Scripts/                       # Analysis scripts (numbered by run order)
│   ├── config.py                  # Path configuration
│   ├── 01_granger_analysis.py     # Pairwise Granger causality
│   ├── 02_panel_var_analysis.py   # Panel VAR estimation
│   ├── 03_pcmci_causal_discovery.py  # PCMCI+ causal discovery
│   ├── 04_heterogeneity_by_income.py # Income group analysis
│   ├── 05_robustness_validation.py   # Bootstrap & robustness checks
│   ├── 06_statistical_validation.py  # FEVD & falsification tests
│   ├── 07_generate_main_figures.py   # Main manuscript figures
│   └── 08_generate_supplementary.py  # Supplementary materials
├── Figures/                       # Generated figures (PNG + SVG)
├── Result/                        # Analysis outputs (CSV files)
├── Supplementary_Figures/         # Supplementary figures and tables
└── Manuscript/                    # Manuscript files and references
```

## Installation

### Requirements

- Python 3.9+
- See `requirements.txt` for package dependencies

### Setup

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/sdg-causal-network.git
cd sdg-causal-network

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Running the Full Analysis Pipeline

Scripts are numbered in recommended execution order:

```bash
cd Scripts

# Step 1: Granger causality analysis
python 01_granger_analysis.py

# Step 2: Panel VAR estimation
python 02_panel_var_analysis.py

# Step 3: PCMCI+ causal discovery
python 03_pcmci_causal_discovery.py

# Step 4: Heterogeneity analysis
python 04_heterogeneity_by_income.py

# Step 5: Robustness checks
python 05_robustness_validation.py

# Step 6: Statistical validation
python 06_statistical_validation.py

# Step 7: Generate figures
python 07_generate_main_figures.py
python 08_generate_supplementary.py
```

### Data Requirements

The analysis requires the **Sustainable Development Report 2025** data:

1. Download from: [SDG Index](https://dashboards.sdgindex.org/)
2. Place `SDR2025-data.xlsx` in the `Data/` directory

## Methodology

### Analytical Framework

1. **Panel VAR with Fixed Effects**: Controls for country-specific heterogeneity
2. **Granger Causality Testing**: Identifies predictive relationships (p < 0.05)
3. **PCMCI+ Causal Discovery**: Filters spurious correlations, identifies direct effects
4. **Impulse Response Functions**: Quantifies dynamic effects over 10-year horizon
5. **Heterogeneity Analysis**: Stratifies by World Bank income classification

### Key Methods

| Method | Purpose | Key Package |
|--------|---------|-------------|
| Panel VAR | Dynamic interdependencies | `statsmodels` |
| Granger Causality | Predictive causation | `statsmodels` |
| PCMCI+ | Conditional independence | `tigramite` |
| Bootstrap CI | Uncertainty quantification | `numpy` |

## Results

### Main Findings

| Relationship | Effect Size | Significance |
|--------------|-------------|--------------|
| Education → Inequality | r = 0.599 | p < 0.01 |
| Consumption → Climate | r = 0.77 | p < 0.01 |
| Growth → Poverty | r = 0.45 | p < 0.01 |

### Generated Outputs

- **Figures**: 4 main figures + 5 supplementary figures
- **Tables**: Granger causality matrix, FEVD decomposition, robustness checks
- **Data**: All intermediate results saved as CSV files in `Result/`

## Citation

If you use this code or data, please cite:

```bibtex
@article{fahim2025sdg,
  title={Distributed Causality in the Sustainable Development Goal Network: 
         A Panel VAR and PCMCI+ Analysis},
  author={Fahim, Muhtasim Munif},
  journal={TBD (Under Review)},
  year={2025}
}
```

## License

Copyright © 2025 Muhtasim Munif Fahim. 
This work is licensed under a [Creative Commons Attribution 4.0 International License](LICENSE).

[![CC BY 4.0](https://licensebuttons.net/l/by/4.0/88x31.png)](https://creativecommons.org/licenses/by/4.0/)

## Acknowledgments

- Data source: [Sustainable Development Solutions Network](https://www.sdgindex.org/)
- PCMCI+ algorithm: [Tigramite](https://github.com/jakobrunge/tigramite)

## Contact

For questions or collaborations, please open an issue or contact Muhtasim Munif Fahim.
