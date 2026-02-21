# ============================================================
# config_ferm.py
# Experiment-Specific Configuration
# ============================================================
"""
Configuration for THIS specific fermentation experiment:
Methanol feeding strategy optimization for recombinant protein production

This file contains ONLY experiment-specific settings.
Generic fermentation settings are imported from config_domain_bioprocess.py

Experiment Details:
- Organism: Komagataella phaffii (Pichia pastoris)
- Product: Recombinant β-lactoglobulin (whey protein)
- Factors: 2 strains × 3 methanol feeding strategies
- Duration: 120 hours (5 days)

Author: [Your Name]
Created: [Date]
"""

# Import generic bioprocess settings
from config_domain_bioprocess import (
    merge_with_experiment_ranges,
    merge_with_experiment_types,
    BIOREACTOR_MONITORING,
    FILE_PATTERNS
)

# ============================================================================
# EXPERIMENT INFORMATION
# ============================================================================
EXPERIMENT_INFO = {
    'title': 'Methanol Feeding Strategy Optimization',
    'organism': 'Komagataella phaffii',
    'product': 'Recombinant β-lactoglobulin',
    'duration_h': 120,
    'factors': ['Strain', 'Methanol_Strategy'],
    'levels': {
        'Strain': ['KP-B1', 'KP-B2'],
        'Methanol_Strategy': ['Continuous', 'Pulsed', 'Ramped']
    }
}

# ============================================================================
# DATA CONSOLIDATION CONFIG
# ============================================================================
CONSOLIDATION_CONFIG = {
    'base_folder': 'ferm_data',
    'run_folder_prefix': 'Run_',
    'id_extraction': lambda folder: folder.replace('Run_', ''),
    'files': {
        'offline': {
            'pattern': FILE_PATTERNS['offline'],
            'id_column': 'Run_ID'
        },
        'bioreactor': {
            'pattern': FILE_PATTERNS['bioreactor'],
            'id_column': 'Run_ID',
            'keep_all': True
        },
        'feed': {
            'pattern': FILE_PATTERNS['feed'],
            'id_column': 'Run_ID'
        }
    }
}

# ============================================================================
# EXPERIMENT-SPECIFIC VARIABLES
# These are unique to THIS experiment
# ============================================================================
EXPERIMENT_TYPES = {
    # Substrates (specific to this experiment)
    'Glucose_gL': 'numeric',           # Growth phase substrate
    'Methanol_gL': 'numeric',          # Induction phase substrate
    
    # Product (specific to this experiment)
    'Protein_mgL': 'numeric',          # Recombinant protein titer
}

EXPERIMENT_RANGES = {
    # Substrates
    'Glucose_gL': (0, 100),            # Initial 40 g/L, consumed during growth
    'Methanol_gL': (0, 20),            # In reactor (not stock concentration)
    
    # Product
    'Protein_mgL': (0, 50000),         # 0-50 g/L (optimized strain target)
}

# ============================================================================
# QUALITY CHECK CONFIG
# Combines generic bioprocess + experiment-specific
# ============================================================================
QUALITY_CONFIG = {
    'primary_file': 'offline',
    'check_column_consistency': True,
    
    # Merge generic and experiment-specific types
    'expected_types': merge_with_experiment_types(EXPERIMENT_TYPES),
    
    # Merge generic and experiment-specific ranges
    'value_ranges': merge_with_experiment_ranges(EXPERIMENT_RANGES),
    
    # Sampling
    'group_by_column': 'Run_ID',
    
    # Time continuity (use generic settings)
    'time_column': BIOREACTOR_MONITORING['time_column'],
    'expected_interval': BIOREACTOR_MONITORING['expected_log_interval'],
    'tolerance': BIOREACTOR_MONITORING['tolerance']
}

# ============================================================================
# CLEANING CONFIG
# ============================================================================
CLEANING_CONFIG = {
    'sort_by': ['Run_ID', 'Time_h'],
    'output_folder': 'ferm_data_cleaned',
    'metadata_extraction': {
        'enabled': True,
        'extract_from': 'Run_ID',
        'fields': ['Strain', 'Methanol_Strategy']  # From EXPERIMENT_INFO
    }
}

# ============================================================================
# METADATA EXTRACTION FUNCTION
# EXPERIMENT-SPECIFIC - Based on YOUR run naming convention
# ============================================================================
def extract_metadata_from_run_id(run_id):
    """
    Extract strain and methanol strategy from Run_ID.
    
    THIS IS SPECIFIC TO THIS EXPERIMENT'S NAMING CONVENTION:
    - Run IDs contain: 'B1' or 'B2' for strain
    - Run IDs contain: 'run1', 'run2', 'run3' for strategy
    
    Examples:
        'KP_B1_run1' → ('KP-B1', 'Continuous')
        'KP-B2_run2' → ('KP-B2', 'Pulsed')
        'run3_KPB1'  → ('KP-B1', 'Ramped')
    
    Args:
        run_id (str): The Run_ID to parse
    
    Returns:
        tuple: (strain, strategy)
    """
    # Extract strain
    if 'B1' in run_id:
        strain = 'KP-B1'
    elif 'B2' in run_id:
        strain = 'KP-B2'
    else:
        strain = 'Unknown'
    
    # Extract strategy
    run_lower = run_id.lower()
    if 'run1' in run_lower or run_id.endswith('1'):
        strategy = 'Continuous'
    elif 'run2' in run_lower or run_id.endswith('2') or 'run-02' in run_lower:
        strategy = 'Pulsed'
    elif 'run3' in run_lower or run_id.endswith('3'):
        strategy = 'Ramped'
    else:
        strategy = 'Unknown'
    
    return strain, strategy

# ============================================================================
# END OF EXPERIMENT CONFIGURATION
# ============================================================================