"""
Unit tests for data preprocessing, cleaning, scaling, and outlier diagnostics.
"""

import pytest
import pandas as pd
import numpy as np

from src.preprocessing import (
    clean_cost_series, clean_rating_series, 
    detect_outliers_iqr, RestaurantPreprocessor
)


def test_clean_cost_series():
    raw_costs = pd.Series(["₹450", "1,200", "$800", "invalid", " 2500 "])
    cleaned = clean_cost_series(raw_costs)
    assert cleaned.iloc[0] == 450.0
    assert cleaned.iloc[1] == 1200.0
    assert cleaned.iloc[2] == 800.0
    assert np.isnan(cleaned.iloc[3])
    assert cleaned.iloc[4] == 2500.0


def test_clean_rating_series():
    raw_ratings = pd.Series(["4.5", "5.0", "Like", "NEW", "-1.0", "6.2", "3.8"])
    cleaned = clean_rating_series(raw_ratings)
    assert cleaned.iloc[0] == 4.5
    assert cleaned.iloc[1] == 5.0
    assert np.isnan(cleaned.iloc[2])
    assert np.isnan(cleaned.iloc[3])
    assert np.isnan(cleaned.iloc[4])
    assert np.isnan(cleaned.iloc[5])
    assert cleaned.iloc[6] == 3.8


def test_detect_outliers_iqr():
    normal_data = [300, 400, 450, 500, 550, 600, 650, 700, 800]
    outlier_data = [5000]
    series = pd.Series(normal_data + outlier_data)
    is_outlier, lower_b, upper_b = detect_outliers_iqr(series)
    assert is_outlier.iloc[-1] is True or is_outlier.iloc[-1] == 1
    assert is_outlier.iloc[0] is False or is_outlier.iloc[0] == 0


def test_restaurant_preprocessor():
    df = pd.DataFrame({
        "cost": [300.0, 800.0, 1500.0, np.nan],
        "avg_rating": [4.1, 4.5, 3.8, 4.2]
    })
    preprocessor = RestaurantPreprocessor(scaler_type="standard")
    X_scaled = preprocessor.fit_transform(df, ["cost", "avg_rating"])
    
    assert X_scaled.shape == (4, 2)
    assert not np.isnan(X_scaled).any()
    
    # Test transform on unseen data
    unseen_df = pd.DataFrame({
        "cost": [600.0],
        "avg_rating": [4.0]
    })
    unseen_scaled = preprocessor.transform(unseen_df)
    assert unseen_scaled.shape == (1, 2)
