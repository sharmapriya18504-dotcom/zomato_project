"""
Validation and schema verification module.
Ensures uploaded and raw datasets adhere to expected columns and valid data ranges.
"""

from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np

from src.config import COLUMN_ALIASES


def map_columns(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, str]]:
    """
    Standardize DataFrame column names using the configured aliases.
    
    Returns:
        renamed_df: DataFrame with standardized column names
        mapping_applied: Dict showing original -> canonical name
    """
    renamed = df.copy()
    col_map = {}
    
    # Lowercase and clean raw column names
    clean_raw_cols = {col: str(col).strip().lower().replace(" ", "_") for col in renamed.columns}
    
    for canonical, aliases in COLUMN_ALIASES.items():
        matched = False
        for original, clean in clean_raw_cols.items():
            if clean in aliases:
                col_map[original] = canonical
                matched = True
                break
        if not matched:
            # Check partial substring match if not directly found
            for original, clean in clean_raw_cols.items():
                for alias in aliases:
                    if alias in clean and original not in col_map:
                        col_map[original] = canonical
                        matched = True
                        break
                if matched:
                    break
                    
    renamed.rename(columns=col_map, inplace=True)
    return renamed, col_map


def validate_dataset(df: pd.DataFrame, required_fields: Optional[List[str]] = None) -> Tuple[bool, List[str]]:
    """
    Validate that required core fields exist in the DataFrame.
    
    Returns:
        is_valid: bool
        messages: List of human-readable issues or validation passes
    """
    if required_fields is None:
        required_fields = ["name", "cost"]
        
    messages = []
    if df is None or df.empty:
        return False, ["Dataset is empty or could not be loaded."]
        
    missing = [req for req in required_fields if req not in df.columns]
    if missing:
        messages.append(f"Missing mandatory columns: {', '.join(missing)}.")
        return False, messages
        
    messages.append("Required schema validation passed.")
    return True, messages


def audit_data_quality(df: pd.DataFrame) -> Dict[str, any]:
    """
    Generate an audit report of dataset quality:
    - Missing counts
    - Duplicates
    - Potential invalid values (negative costs, out-of-bounds ratings)
    """
    report = {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "columns": list(df.columns),
        "missing_summary": df.isnull().sum().to_dict(),
        "duplicate_rows": int(df.duplicated().sum()),
        "duplicate_names": int(df.duplicated(subset=["name"]).sum()) if "name" in df.columns else int(df.duplicated().sum()),
        "invalid_cost_count": 0,
        "invalid_rating_count": 0
    }
    
    if "cost" in df.columns:
        costs = pd.to_numeric(
            df["cost"].astype(str).str.replace(",", "").str.strip(), 
            errors="coerce"
        )
        report["invalid_cost_count"] = int((costs <= 0).sum() + costs.isna().sum())
        
    if "rating" in df.columns:
        ratings = pd.to_numeric(df["rating"], errors="coerce")
        report["invalid_rating_count"] = int(((ratings < 0) | (ratings > 5)).sum() + ratings.isna().sum())
        
    return report
