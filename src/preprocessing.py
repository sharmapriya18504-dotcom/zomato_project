"""
Data preprocessing, cleaning, scaling, and feature pipeline module.
"""

from typing import Dict, List, Optional, Tuple, Union
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, RobustScaler, MinMaxScaler
import joblib

from src.config import MODELS_DIR


def clean_cost_series(series: pd.Series) -> pd.Series:
    """
    Clean string cost representations into numeric values.
    Removes commas, currency signs, and strips whitespace.
    """
    cleaned = (
        series.astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("₹", "", regex=False)
        .str.replace("$", "", regex=False)
        .str.replace("INR", "", regex=False)
        .str.strip()
    )
    return pd.to_numeric(cleaned, errors="coerce")


def clean_rating_series(series: pd.Series) -> pd.Series:
    """
    Clean rating representations into float values bounded between 0 and 5.
    Coerces textual entries (e.g. 'NEW', '-', 'Like') to NaN.
    """
    cleaned = pd.to_numeric(series, errors="coerce")
    # Clamp valid ratings
    cleaned = cleaned.apply(lambda r: r if 0.0 <= r <= 5.0 else np.nan)
    return cleaned


def detect_outliers_iqr(series: pd.Series, factor: float = 1.5) -> Tuple[pd.Series, float, float]:
    """
    Identify potential statistical outliers using Interquartile Range (IQR).
    Note: In restaurant pricing, high cost points often indicate legitimate luxury dining.
    """
    valid = series.dropna()
    if valid.empty:
        return pd.Series(False, index=series.index), 0.0, 0.0
        
    q1 = valid.quantile(0.25)
    q3 = valid.quantile(0.75)
    iqr = q3 - q1
    lower_bound = max(0.0, q1 - factor * iqr)
    upper_bound = q3 + factor * iqr
    
    is_outlier = (series < lower_bound) | (series > upper_bound)
    return is_outlier, lower_bound, upper_bound


class RestaurantPreprocessor:
    """
    Reusable feature preprocessing pipeline for restaurant clustering and analytics.
    Handles scaling, imputation, and column transformations consistently.
    """
    def __init__(self, scaler_type: str = "standard"):
        self.scaler_type = scaler_type
        if scaler_type == "robust":
            self.scaler = RobustScaler()
        elif scaler_type == "minmax":
            self.scaler = MinMaxScaler()
        else:
            self.scaler = StandardScaler()
            
        self.fitted_features: List[str] = []
        self.feature_means: Dict[str, float] = {}
        
    def fit(self, df: pd.DataFrame, feature_cols: List[str]) -> "RestaurantPreprocessor":
        self.fitted_features = list(feature_cols)
        X = df[feature_cols].copy()
        
        # Calculate imputation fallbacks
        for col in feature_cols:
            self.feature_means[col] = float(X[col].median() if not X[col].dropna().empty else 0.0)
            X[col] = X[col].fillna(self.feature_means[col])
            
        self.scaler.fit(X)
        return self
        
    def transform(self, df: pd.DataFrame) -> np.ndarray:
        if not self.fitted_features:
            raise ValueError("Preprocessor has not been fitted yet.")
            
        X = df[self.fitted_features].copy()
        for col in self.fitted_features:
            fallback = self.feature_means.get(col, 0.0)
            X[col] = X[col].fillna(fallback)
            
        return self.scaler.transform(X)
        
    def fit_transform(self, df: pd.DataFrame, feature_cols: List[str]) -> np.ndarray:
        return self.fit(df, feature_cols).transform(df)
        
    def save(self, filepath: Union[str, Path]) -> None:
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, filepath)
        
    @staticmethod
    def load(filepath: Union[str, Path]) -> "RestaurantPreprocessor":
        return joblib.load(filepath)
