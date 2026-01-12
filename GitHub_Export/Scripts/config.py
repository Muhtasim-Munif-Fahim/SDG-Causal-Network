# Copyright (c) 2025 Muhtasim Munif Fahim
# Licensed under the CC-BY-4.0

"""
Configuration module for SDG Time Series Analysis.
Handles path definitions and common constants.
"""

from pathlib import Path
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Project root directory (parent of the Scripts folder)
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Directory paths
DATA_DIR = PROJECT_ROOT / 'Data'
FIGURES_DIR = PROJECT_ROOT / 'Figures'
RESULTS_DIR = PROJECT_ROOT / 'Results'
SUPPLEMENTARY_DIR = PROJECT_ROOT / 'Supplementary_Figures'
MANUSCRIPT_DIR = PROJECT_ROOT / 'Manuscript'
SCRIPTS_DIR = PROJECT_ROOT / 'Scripts'

# Ensure directories exist
for directory in [FIGURES_DIR, RESULTS_DIR, SUPPLEMENTARY_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# File paths
SDR_DATA_FILE = DATA_DIR / 'SDR2025-data.xlsx'
GRANGER_PVALUES_FILE = RESULTS_DIR / 'granger_pvalues.csv'
IRF_DATA_FILE = RESULTS_DIR / 'irf_data.csv'

# Strategic 8-SDG Subset (Matching manuscript focus)
# Original full list: [f'goal{i}' for i in range(1, 18)]
GOAL_COLS = ['goal1', 'goal3', 'goal4', 'goal7', 'goal8', 'goal10', 'goal13', 'goal16']

# SDG Names Map
SDG_NAMES = {
    'goal1': 'Poverty',
    'goal2': 'Hunger',
    'goal3': 'Health',
    'goal4': 'Education',
    'goal5': 'Gender',
    'goal6': 'Water',
    'goal7': 'Energy',
    'goal8': 'Growth',
    'goal9': 'Industry',
    'goal10': 'Inequality',
    'goal11': 'Cities',
    'goal12': 'Consumption',
    'goal13': 'Climate',
    'goal14': 'Oceans',
    'goal15': 'Biodiversity',
    'goal16': 'Institutions',
    'goal17': 'Partnerships'
}

# World Bank Income Group Mapping 
INCOME_MAPPING = {
    'USA': 'HIC', 'CAN': 'HIC', 'GBR': 'HIC', 'FRA': 'HIC', 'DEU': 'HIC', 
    'JPN': 'HIC', 'AUS': 'HIC', 'NZL': 'HIC', 'SWE': 'HIC', 'NOR': 'HIC',
    'DNK': 'HIC', 'FIN': 'HIC', 'CHE': 'HIC', 'NLD': 'HIC', 'BEL': 'HIC',
    'AUT': 'HIC', 'ITA': 'HIC', 'ESP': 'HIC', 'PRT': 'HIC', 'IRL': 'HIC',
    'CHN': 'UMIC', 'BRA': 'UMIC', 'MEX': 'UMIC', 'RUS': 'UMIC', 'TUR': 'UMIC',
    'ZAF': 'UMIC', 'IND': 'LMIC', 'IDN': 'LMIC', 'PAK': 'LMIC', 'NGA': 'LMIC',
    'ETH': 'LIC', 'TZA': 'LIC', 'COD': 'LIC', 'MOZ': 'LIC', 'UGA': 'LIC'
}
