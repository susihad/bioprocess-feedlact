# ============================================================
# config_domain_bioprocess.py
# Domain Configuration for Fermentation/Bioprocess Experiments
# ============================================================
"""
Generic configuration for fermentation and bioprocess experiments.

This file contains settings that apply to ANY fermentation experiment,
regardless of organism, substrate, or product.

APPLIES TO:
- Bacterial fermentation (E. coli, Bacillus, etc.)
- Yeast fermentation (S. cerevisiae, Pichia, etc.)
- Fungal fermentation (Aspergillus, Penicillium, etc.)
- Cell culture (CHO, HEK293, hybridomas, etc.)

DO NOT MODIFY THIS FILE unless adding new generic bioprocess parameters.

For experiment-specific settings, use config_ferm.py (or your own config).

Author: [Your Name]
Created: [Date]
"""

# ============================================================================
# GENERIC BIOPROCESS VALUE RANGES
# These apply to virtually ALL fermentation/bioprocess experiments
# ============================================================================
BIOPROCESS_RANGES = {
    # -------------------------------------------------------------------
    # PROCESS VARIABLES (Always monitored in bioprocessing)
    # -------------------------------------------------------------------
    'pH': (3.0, 8.0),                  # Most fermentation pH range
    'DO_%': (0, 100),                  # Dissolved oxygen (by definition)
    'Temperature_C': (20, 45),         # Typical bioprocess temperature range
    'Agitation_rpm': (100, 1200),      # Standard bioreactor agitation range
    
    # -------------------------------------------------------------------
    # CELL MEASUREMENTS (Common to all fermentation)
    # -------------------------------------------------------------------
    'Biomass_gL': (0, 200),            # Typical max cell density (wet weight)
    'OD600': (0, 100),                 # Optical density measurement range
    'Viability_%': (0, 100),           # Cell viability (by definition)
    'VCD_cells_per_mL': (0, 1e8),      # Viable cell density (mammalian cells)
    
    # -------------------------------------------------------------------
    # GAS MEASUREMENTS (For aerobic processes)
    # -------------------------------------------------------------------
    'CO2_%': (0, 100),                 # CO2 in off-gas
    'O2_%': (0, 100),                  # O2 in off-gas
    'RQ': (0, 5),                      # Respiratory quotient (CO2/O2)
    'OUR_mmol_L_h': (0, 500),          # Oxygen uptake rate
    'CPR_mmol_L_h': (0, 500),          # Carbon dioxide production rate
}

# ============================================================================
# GENERIC BIOPROCESS DATA TYPES
# Common measurements in fermentation
# ============================================================================
BIOPROCESS_TYPES = {
    # Time
    'Time_h': 'numeric',
    'Timestamp': 'numeric',
    
    # Process variables
    'pH': 'numeric',
    'DO_%': 'numeric',
    'Temperature_C': 'numeric',
    'Agitation_rpm': 'numeric',
    'Pressure_bar': 'numeric',
    
    # Cell measurements
    'Biomass_gL': 'numeric',
    'OD600': 'numeric',
    'Viability_%': 'numeric',
    'VCD_cells_per_mL': 'numeric',
    
    # Identifiers
    'Run_ID': 'string',
    'Batch_ID': 'string',
    'Sample_ID': 'string',
}

# ============================================================================
# GENERIC BIOREACTOR MONITORING SETTINGS
# Typical sensor logging parameters
# ============================================================================
BIOREACTOR_MONITORING = {
    'expected_log_interval': 0.5,     # Hours between sensor readings (30 min)
    'tolerance': 1.5,                 # Gap detection multiplier
    'time_column': 'Timestamp',       # Standard time column name
}

# ============================================================================
# COMMON FERMENTATION FILE PATTERNS
# Standard file naming in bioprocess labs
# ============================================================================
FILE_PATTERNS = {
    'offline': 'offline_samples.csv',      # Manual lab measurements
    'bioreactor': 'bioreactor_log.csv',    # Automated sensor data
    'feed': 'feed_log.csv',                # Feeding/addition events
    'metadata': 'run_metadata.csv',        # Run information
}

# ============================================================================
# STANDARD COLUMN NAMING CONVENTIONS
# Recommended naming for bioprocess data
# ============================================================================
NAMING_CONVENTIONS = {
    'time_units': ['_h', '_min', '_s'],                    # Time should have units
    'concentration_units': ['_gL', '_mgL', '_mM', '_M'],   # Concentration units
    'percentage_units': ['_%'],                            # Percentages
    'rate_units': ['_per_h', '_h_inv'],                    # Rates
    'temperature_units': ['_C', '_K'],                     # Temperature
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================
def get_generic_ranges():
    """
    Get generic bioprocess value ranges.
    
    Returns:
        dict: Generic value ranges for fermentation
    """
    return BIOPROCESS_RANGES.copy()

def get_generic_types():
    """
    Get generic bioprocess data types.
    
    Returns:
        dict: Generic expected data types
    """
    return BIOPROCESS_TYPES.copy()

def merge_with_experiment_ranges(experiment_ranges):
    """
    Merge generic bioprocess ranges with experiment-specific ranges.
    Experiment-specific ranges override generic ones if there's overlap.
    
    Args:
        experiment_ranges (dict): Experiment-specific value ranges
    
    Returns:
        dict: Combined ranges (generic + experiment-specific)
    """
    combined = BIOPROCESS_RANGES.copy()
    combined.update(experiment_ranges)
    return combined

def merge_with_experiment_types(experiment_types):
    """
    Merge generic bioprocess types with experiment-specific types.
    
    Args:
        experiment_types (dict): Experiment-specific data types
    
    Returns:
        dict: Combined types (generic + experiment-specific)
    """
    combined = BIOPROCESS_TYPES.copy()
    combined.update(experiment_types)
    return combined

# ============================================================================
# END OF DOMAIN CONFIGURATION
# ============================================================================