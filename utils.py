# ============================================================
# utils.py - Universal Reusable Functions
# ============================================================
"""
Universal data processing functions for laboratory experiments.

Works for ANY experiment type - no domain knowledge required.
All functions are config-driven and require no modification
for different experiment types (fermentation, cell culture, genomics, etc.)

Functions:
- Consolidation: consolidate_files()
- Quality Checks: check_missing_values(), check_duplicates(), 
                  check_data_types(), check_sampling_consistency(),
                  check_value_ranges(), check_time_continuity(),
                  check_column_consistency()
- Cleaning: remove_duplicates(), sort_dataframe(), apply_unit_conversions()
- Reporting: generate_report()
- Utility: list_available_checks()

Author: [Your Name]
Created: [Date]
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime
from collections import Counter

# ============================================================================
# CONSOLIDATION FUNCTIONS
# ============================================================================
def consolidate_files(config):
    """
    Consolidate files from multiple folders into master DataFrames.
    
    Args:
        config (dict): Configuration dictionary with:
            - base_folder (str): Root folder containing run folders
            - run_folder_prefix (str): Prefix for run folders (e.g., 'Run_')
            - id_extraction (function): Lambda to extract ID from folder name
            - files (dict): File patterns and ID columns
    
    Returns:
        tuple: (consolidated_data dict, run_folders list)
    
    Example:
        consolidated, folders = consolidate_files(CONSOLIDATION_CONFIG)
    """
    base_folder = config['base_folder']
    prefix = config['run_folder_prefix']
    id_extractor = config['id_extraction']
    
    # Find all run folders
    run_folders = [f for f in os.listdir(base_folder) 
                   if os.path.isdir(os.path.join(base_folder, f)) and f.startswith(prefix)]
    
    consolidated = {}
    
    for file_key, file_config in config['files'].items():
        dfs = []
        pattern = file_config['pattern']
        id_col = file_config['id_column']
        
        for folder in run_folders:
            file_path = os.path.join(base_folder, folder, pattern)
            
            if os.path.exists(file_path):
                df = pd.read_csv(file_path)
                
                # Add ID column if not present
                if id_col not in df.columns:
                    df.insert(0, id_col, id_extractor(folder))
                
                dfs.append(df)
        
        # Combine all runs
        if dfs:
            consolidated[file_key] = pd.concat(dfs, ignore_index=True)
        else:
            consolidated[file_key] = pd.DataFrame()
    
    return consolidated, run_folders

# ============================================================================
# QUALITY CHECK FUNCTIONS
# ============================================================================
def check_column_consistency(df, group_by_col, file_name):
    """
    Check if all groups (e.g., runs) have the same columns.
    Flags groups with different column sets.
    
    Universal - works for any grouped data.
    
    Args:
        df (DataFrame): Data to check
        group_by_col (str): Column to group by (e.g., 'Run_ID')
        file_name (str): Name of file for reporting
    
    Returns:
        dict: Check result with status and details
    """
    issues = []
    column_sets = {}
    
    for group_id in df[group_by_col].unique():
        group_data = df[df[group_by_col] == group_id]
        # Get non-null columns for this group
        group_cols = set(group_data.columns[group_data.notna().any()])
        column_sets[group_id] = group_cols
    
    # Find the most common column set (reference)
    all_column_sets = [frozenset(cols) for cols in column_sets.values()]
    if not all_column_sets:
        return {
            "check": "Column Consistency",
            "status": "PASS",
            "file": file_name,
            "details": "No groups to compare"
        }
    
    most_common_cols = set(Counter(all_column_sets).most_common(1)[0][0])
    
    # Compare each group to reference
    for group_id, group_cols in column_sets.items():
        missing = most_common_cols - group_cols
        extra = group_cols - most_common_cols
        
        if missing or extra:
            issue = {"group": group_id, "file": file_name}
            if missing:
                issue["missing_columns"] = list(missing)
            if extra:
                issue["extra_columns"] = list(extra)
            issues.append(issue)
    
    if issues:
        return {
            "check": "Column Consistency",
            "status": "FAIL",
            "file": file_name,
            "details": issues
        }
    
    return {
        "check": "Column Consistency",
        "status": "PASS",
        "file": file_name,
        "details": "All groups have same columns"
    }

def check_missing_values(df, file_name):
    """
    Check for missing (NaN) values in DataFrame.
    
    Universal - works for any dataset.
    
    Args:
        df (DataFrame): Data to check
        file_name (str): Name of file for reporting
    
    Returns:
        dict: Check result with status and details
    """
    missing = df.isnull().sum()
    missing_cols = missing[missing > 0]
    
    if len(missing_cols) > 0:
        details = {col: {"count": int(count), "percent": f"{(count/len(df)*100):.1f}%"} 
                   for col, count in missing_cols.items()}
        return {
            "check": "Missing Values",
            "status": "FAIL",
            "file": file_name,
            "details": details
        }
    
    return {
        "check": "Missing Values",
        "status": "PASS",
        "file": file_name,
        "details": "No missing values"
    }

def check_duplicates(df, file_name):
    """
    Check for duplicate rows in DataFrame.
    
    Universal - works for any dataset.
    
    Args:
        df (DataFrame): Data to check
        file_name (str): Name of file for reporting
    
    Returns:
        dict: Check result with status and details
    """
    dup_count = df.duplicated().sum()
    
    if dup_count > 0:
        return {
            "check": "Duplicate Rows",
            "status": "FAIL",
            "file": file_name,
            "details": f"{dup_count} duplicate rows found"
        }
    
    return {
        "check": "Duplicate Rows",
        "status": "PASS",
        "file": file_name,
        "details": "No duplicates"
    }

def check_data_types(df, file_name, expected_types):
    """
    Verify columns have expected data types.
    
    Universal with config.
    
    Args:
        df (DataFrame): Data to check
        file_name (str): Name of file for reporting
        expected_types (dict): Expected types {'col_name': 'numeric' or 'string'}
    
    Returns:
        dict: Check result with status and details
    """
    issues = []
    
    for col, expected_type in expected_types.items():
        if col not in df.columns:
            continue
            
        if expected_type == 'numeric':
            if not pd.api.types.is_numeric_dtype(df[col]):
                issues.append(f"{col} should be numeric, got {df[col].dtype}")
        elif expected_type == 'string':
            if not pd.api.types.is_string_dtype(df[col]) and not pd.api.types.is_object_dtype(df[col]):
                issues.append(f"{col} should be string, got {df[col].dtype}")
    
    if issues:
        return {
            "check": "Data Types",
            "status": "FAIL",
            "file": file_name,
            "details": issues
        }
    
    return {
        "check": "Data Types",
        "status": "PASS",
        "file": file_name,
        "details": "All types correct"
    }

def check_sampling_consistency(df, group_by_col):
    """
    Check if all groups have the same number of samples.
    
    Universal - just needs grouping column.
    
    Args:
        df (DataFrame): Data to check
        group_by_col (str): Column to group by (e.g., 'Run_ID', 'Patient_ID')
    
    Returns:
        dict: Check result with status and details
    """
    counts = df.groupby(group_by_col).size()
    min_count = counts.min()
    max_count = counts.max()
    
    if min_count != max_count:
        details = counts.to_dict()
        return {
            "check": "Sampling Consistency",
            "status": "FAIL",
            "details": f"Count range: {min_count}-{max_count}",
            "breakdown": details
        }
    
    return {
        "check": "Sampling Consistency",
        "status": "PASS",
        "details": f"All groups: {max_count} samples"
    }

def check_value_ranges(df, file_name, range_rules):
    """
    Check if values are within expected ranges.
    
    Universal with config.
    
    Args:
        df (DataFrame): Data to check
        file_name (str): Name of file for reporting
        range_rules (dict): Expected ranges {'col_name': (min_val, max_val)}
    
    Returns:
        dict: Check result with status and details
    """
    issues = []
    
    for col, (min_val, max_val) in range_rules.items():
        if col not in df.columns:
            continue
            
        if (df[col] < min_val).any():
            count = (df[col] < min_val).sum()
            issues.append(f"{col}: {count} values below {min_val}")
        
        if (df[col] > max_val).any():
            count = (df[col] > max_val).sum()
            issues.append(f"{col}: {count} values above {max_val}")
    
    if issues:
        return {
            "check": "Value Ranges",
            "status": "FAIL",
            "file": file_name,
            "details": issues
        }
    
    return {
        "check": "Value Ranges",
        "status": "PASS",
        "file": file_name,
        "details": "All values in valid ranges"
    }

def check_time_continuity(df, time_col, expected_interval, tolerance=1.5):
    """
    Check for gaps in time-series data.
    
    Universal for time-series data.
    
    Args:
        df (DataFrame): Data to check
        time_col (str): Name of time column
        expected_interval (float): Expected time between readings
        tolerance (float): Multiplier for gap detection (default 1.5)
    
    Returns:
        dict: Check result with status and details
    """
    df_sorted = df.sort_values(time_col)
    time_diffs = df_sorted[time_col].diff()
    
    large_gaps = time_diffs[time_diffs > expected_interval * tolerance]
    
    if len(large_gaps) > 0:
        gap_details = []
        for idx in large_gaps.index:
            t_before = df_sorted.loc[idx-1, time_col]
            t_after = df_sorted.loc[idx, time_col]
            gap = large_gaps.loc[idx]
            gap_details.append(f"Gap from {t_before} to {t_after} ({gap:.1f} units)")
        
        return {
            "check": "Time Continuity",
            "status": "FAIL",
            "details": gap_details
        }
    
    return {
        "check": "Time Continuity",
        "status": "PASS",
        "details": "No significant gaps"
    }

# ============================================================================
# CLEANING FUNCTIONS
# ============================================================================
def remove_duplicates(df):
    """
    Remove duplicate rows from DataFrame.
    
    Universal.
    
    Args:
        df (DataFrame): Data to clean
    
    Returns:
        tuple: (cleaned DataFrame, number of rows removed)
    """
    initial = len(df)
    df_clean = df.drop_duplicates()
    removed = initial - len(df_clean)
    return df_clean, removed

def sort_dataframe(df, sort_columns):
    """
    Sort DataFrame by specified columns.
    
    Universal.
    
    Args:
        df (DataFrame): Data to sort
        sort_columns (list): List of column names to sort by
    
    Returns:
        DataFrame: Sorted DataFrame with reset index
    """
    return df.sort_values(sort_columns).reset_index(drop=True)

def apply_unit_conversions(df, conversions_config):
    """
    Apply unit conversions based on config.
    
    Universal with config.
    
    Args:
        df (DataFrame): Data to convert
        conversions_config (dict): Conversion rules with format:
            {'source_col': {'target_column': str, 
                           'conversion_factor': float,
                           'description': str}}
    
    Returns:
        tuple: (converted DataFrame, list of change descriptions)
    """
    changes = []
    
    for source_col, config in conversions_config.items():
        if source_col in df.columns:
            target_col = config['target_column']
            factor = config['conversion_factor']
            
            df[target_col] = df[source_col] * factor
            df = df.drop(source_col, axis=1)
            
            changes.append(config['description'])
    
    return df, changes

# ============================================================================
# REPORTING FUNCTIONS
# ============================================================================
def generate_report(all_checks, run_folders=None, consolidation_config=None, output_path='data_quality_report.txt'):
    """
    Generate comprehensive text report from quality check results.
    
    Universal - works for any experiment type.
    
    Args:
        all_checks (list): List of check result dictionaries
        run_folders (list): Optional list of run folder names
        consolidation_config (dict): Optional config for folder structure info
        output_path (str): Path to save report (default: 'data_quality_report.txt')
    
    Returns:
        str: Path to generated report file
    """
    passed = sum(1 for c in all_checks if c.get('status') == "PASS")
    failed = sum(1 for c in all_checks if c.get('status') == "FAIL")
    
    report = f"""{'='*70}
DATA QUALITY ASSESSMENT REPORT
{'='*70}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

"""
    
    # ========================================================================
    # DATA STRUCTURE SECTION
    # ========================================================================

    if run_folders and consolidation_config:
        base_folder = consolidation_config['base_folder']
        
        # Get unique file patterns
        file_patterns = [config['pattern'] for config in consolidation_config['files'].values()]
        total_files = len(run_folders) * len(file_patterns)
        
        report += f"""{'='*70}
DATA STRUCTURE
{'='*70}
Base folder: {base_folder}
Total run folders: {len(run_folders)} (Total files: {total_files})

"""
        
        # List run folders
        report += "Run Folders:\n"
        for i, folder in enumerate(sorted(run_folders), 1):
            # Strip the prefix for cleaner display
            folder_clean = folder.replace(consolidation_config.get('run_folder_prefix', 'Run_'), '')
            report += f"  {i}. {folder_clean}\n"
        
        # Analyze all files to get row/column ranges
        report += "\nFile Analysis:\n"
        
        all_rows = {}  # {pattern: [list of row counts]}
        all_cols = {}  # {pattern: [list of col counts]}
        
        for file_key, file_config in consolidation_config['files'].items():
            pattern = file_config['pattern']
            all_rows[pattern] = []
            all_cols[pattern] = []
            
            for folder in run_folders:
                file_path = os.path.join(base_folder, folder, pattern)
                if os.path.exists(file_path):
                    try:
                        df = pd.read_csv(file_path)
                        all_rows[pattern].append(len(df))
                        all_cols[pattern].append(len(df.columns))
                    except:
                        pass
        
        # Print summary statistics
        if all_rows:
            report += "\n  Number of rows per file:\n"
            for pattern in file_patterns:
                if pattern in all_rows and all_rows[pattern]:
                    min_rows = min(all_rows[pattern])
                    max_rows = max(all_rows[pattern])
                    report += f"    {pattern:30s}: {min_rows}-{max_rows} rows\n"
        
        if all_cols:
            report += "\n  Number of columns per file:\n"
            for pattern in file_patterns:
                if pattern in all_cols and all_cols[pattern]:
                    min_cols = min(all_cols[pattern])
                    max_cols = max(all_cols[pattern])
                    report += f"    {pattern:30s}: {min_cols}-{max_cols} columns\n"
        
        report += "\n"
    
    # ========================================================================
    # QUALITY CHECKS SUMMARY
    # ========================================================================
    report += f"""{'='*70}
QUALITY CHECKS SUMMARY
{'='*70}
Total quality parameters checked: {len(all_checks)}
Passed: {passed}
Failed: {failed}

DETAILED RESULTS:
"""
    
    # ========================================================================
    # DETAILED CHECK RESULTS - CONSISTENT FORMAT
    # ========================================================================
    for check in all_checks:
        status = "[PASS]" if check.get('status') == "PASS" else "[FAIL]"
        report += f"\n{status} {check.get('check', 'Unknown')}: {check.get('status', 'Unknown')}\n"
        
        details = check.get('details', 'No details')
        file_name = check.get('file', 'Unknown')
        
        # Helper to get clean folder name (without prefix)
        def get_clean_folder(run_id):
            if run_folders and consolidation_config:
                folder_prefix = consolidation_config.get('run_folder_prefix', 'Run_')
                source_folder = f"{folder_prefix}{run_id}"
                if source_folder in run_folders:
                    return run_id  # Already clean (without prefix)
            return None
        
        # ====================================================================
        # HANDLE DIFFERENT CHECK TYPES WITH CONSISTENT FORMAT
        # ====================================================================
        
        # --------------------------------------------------------------------
        # CHECK 1: Column Consistency
        # Format:
        #   Extra/Missing columns found
        #   File: xxx.csv
        #   Folder: run_id
        #   Extra columns: col1, col2
        # --------------------------------------------------------------------
        if isinstance(details, list) and check.get('check') == 'Column Consistency':
            for item in details:
                if isinstance(item, dict) and 'group' in item:
                    if 'extra_columns' in item and 'missing_columns' in item:
                        report += f"  Extra and missing columns found\n"
                    elif 'extra_columns' in item:
                        report += f"  Extra columns found\n"
                    elif 'missing_columns' in item:
                        report += f"  Missing columns found\n"
                    
                    report += f"  File: {item.get('file', 'Unknown')}\n"
                    folder = get_clean_folder(item['group'])
                    if folder:
                        report += f"  Folder: {folder}\n"
                    
                    if 'extra_columns' in item:
                        report += f"  Extra columns: {', '.join(item['extra_columns'])}\n"
                    if 'missing_columns' in item:
                        report += f"  Missing columns: {', '.join(item['missing_columns'])}\n"
        
        # --------------------------------------------------------------------
        # CHECK 2: Missing Values
        # Format:
        #   Missing data detected in X columns
        #   File: xxx.csv
        #   Column 'col1': X missing (Y%) in folders: folder1, folder2
        # --------------------------------------------------------------------
        elif isinstance(details, dict) and check.get('check') == 'Missing Values':
            num_cols = len(details)
            report += f"  Missing data detected in {num_cols} column(s)\n"
            report += f"  File: {file_name}\n"
            
            # Load file to get run-specific info
            try:
                df = pd.read_csv(file_name) if os.path.exists(file_name) else None
                if df is not None and 'Run_ID' in df.columns:
                    for col, info in details.items():
                        count = info.get('count', 0)
                        percent = info.get('percent', '0')
                        
                        # Get affected runs
                        runs_with_missing = df[df[col].isna()]['Run_ID'].unique()
                        folders_str = ', '.join(sorted(runs_with_missing)) if len(runs_with_missing) > 0 else 'None'
                        
                        report += f"  Column '{col}': {count} missing ({percent}) in folders: {folders_str}\n"
                else:
                    # Fallback
                    for col, info in details.items():
                        count = info.get('count', 0)
                        percent = info.get('percent', '0')
                        report += f"  Column '{col}': {count} missing ({percent})\n"
            except:
                # Fallback
                for col, info in details.items():
                    count = info.get('count', 0)
                    percent = info.get('percent', '0')
                    report += f"  Column '{col}': {count} missing ({percent})\n"
        
        # --------------------------------------------------------------------
        # CHECK 3: Duplicate Rows
        # Format:
        #   X duplicate rows found
        #   File: xxx.csv
        #   Folder: folder1, folder2
        # --------------------------------------------------------------------
        elif check.get('check') == 'Duplicate Rows' and check.get('status') == 'FAIL':
            report += f"  {details}\n"
            report += f"  File: {file_name}\n"
            
            # Try to identify which runs have duplicates
            try:
                df = pd.read_csv(file_name) if os.path.exists(file_name) else None
                if df is not None and 'Run_ID' in df.columns:
                    dup_runs = df[df.duplicated(keep=False)]['Run_ID'].unique()
                    if len(dup_runs) > 0:
                        folders_str = ', '.join(sorted(dup_runs))
                        report += f"  Folder: {folders_str}\n"
            except:
                pass
        
        # --------------------------------------------------------------------
        # CHECK 4: Data Types
        # Format:
        #   Data type issues found
        #   File: xxx.csv
        #   col1 should be numeric, got object
        # --------------------------------------------------------------------
        elif isinstance(details, list) and check.get('check') == 'Data Types':
            report += f"  Data type issues found\n"
            report += f"  File: {file_name}\n"
            for issue in details:
                report += f"  {issue}\n"
        
        # --------------------------------------------------------------------
        # CHECK 5: Sampling Consistency
        # Format:
        #   Inconsistent sample counts
        #   File: xxx.csv
        #   Expected: X samples, but some runs have Y samples
        #   folder1: X samples, folder2: Y samples
        # --------------------------------------------------------------------
        elif 'breakdown' in details if isinstance(details, dict) else False:
            report += f"  Inconsistent sample counts\n"
            report += f"  File: {file_name}\n"
            
            # Get min/max from breakdown
            counts = list(details['breakdown'].values())
            min_c = min(counts)
            max_c = max(counts)
            report += f"  Sample count range: {min_c}-{max_c} samples\n"
            
            for run, count in details['breakdown'].items():
                if count != max_c:
                    missing = max_c - count
                    report += f"  Folder '{run}': {count} samples (missing {missing})\n"
        
        # --------------------------------------------------------------------
        # CHECK 6: Value Ranges
        # Format:
        #   Out-of-range values detected
        #   File: xxx.csv
        #   Column 'Protein_mgL': 38 values exceed maximum (50000 mg/L) in folders: folder1, folder2
        # --------------------------------------------------------------------
        elif isinstance(details, list) and check.get('check') == 'Value Ranges':
            report += f"  Out-of-range values detected\n"
            report += f"  File: {file_name}\n"
            
            # Try to identify which runs have range violations
            try:
                df = pd.read_csv(file_name) if os.path.exists(file_name) else None
                if df is not None and 'Run_ID' in df.columns:
                    for issue in details:
                        # Parse issue: "Protein_mgL: 38 values above 50000"
                        parts = issue.split(':')
                        col_name = parts[0].strip()
                        
                        if 'below' in issue:
                            threshold = issue.split('below')[1].strip()
                            condition = f"below minimum ({threshold})"
                            violating_runs = df[df[col_name] < float(threshold)]['Run_ID'].unique()
                        elif 'above' in issue:
                            threshold = issue.split('above')[1].strip()
                            condition = f"exceed maximum ({threshold})"
                            violating_runs = df[df[col_name] > float(threshold)]['Run_ID'].unique()
                        else:
                            condition = "out of range"
                            violating_runs = []
                        
                        count = parts[1].split()[0].strip() if len(parts) > 1 else "some"
                        
                        if len(violating_runs) > 0:
                            folders_str = ', '.join(sorted(violating_runs))
                            report += f"  Column '{col_name}': {count} values {condition} in folders: {folders_str}\n"
                        else:
                            report += f"  {issue}\n"
                else:
                    # Fallback
                    for issue in details:
                        report += f"  {issue}\n"
            except:
                # Fallback
                for issue in details:
                    report += f"  {issue}\n"
        
        # --------------------------------------------------------------------
        # CHECK 7: Time Continuity
        # Format:
        #   Time gaps detected
        #   File: xxx.csv
        #   Gap from X to Y (Z hours)
        # --------------------------------------------------------------------
        elif isinstance(details, list) and check.get('check') == 'Time Continuity':
            report += f"  Time gaps detected\n"
            report += f"  File: {file_name}\n"
            for gap in details:
                report += f"  {gap}\n"
        
        # --------------------------------------------------------------------
        # FALLBACK for PASS or unknown formats
        # --------------------------------------------------------------------
        else:
            if isinstance(details, str):
                report += f"  {details}\n"
            elif isinstance(details, dict):
                for key, value in details.items():
                    report += f"  {key}: {value}\n"
            else:
                report += f"  {details}\n"
    
    report += f"\n{'='*70}\nEND OF REPORT\n{'='*70}\n"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    return output_path
# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================
def list_available_checks():
    """
    List all available quality check functions.
    
    Useful for documentation and troubleshooting.
    
    Returns:
        dict: Dictionary of function names and descriptions
    """
    checks = {
        'check_column_consistency': 'Verify all groups have same columns',
        'check_missing_values': 'Detect missing/NaN values',
        'check_duplicates': 'Find duplicate rows',
        'check_data_types': 'Verify column data types',
        'check_sampling_consistency': 'Check sample counts across groups',
        'check_value_ranges': 'Validate values within expected ranges',
        'check_time_continuity': 'Detect gaps in time-series data'
    }
    
    print("Available Quality Checks:")
    print("="*50)
    for func, desc in checks.items():
        print(f"  {func:30s} - {desc}")
    
    return checks

# ============================================================================
# END OF MODULE
# ============================================================================