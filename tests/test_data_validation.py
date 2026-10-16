"""
Unit tests for data validation, schema verification, and column mapping.
"""

import pytest
import pandas as pd
import numpy as np

from src.validation import map_columns, validate_dataset, audit_data_quality


@pytest.fixture
def sample_raw_df():
    return pd.DataFrame({
        "Restaurant Name": ["Alpha Cafe", "Beta Biryani", "Gamma Grills"],
        "Approx Cost(for two people)": ["400", "1,200", "1,800"],
        "Rate": ["4.2", "3.9", "4.6"],
        "Cuisines": ["Cafe, Fast Food", "Biryani, North Indian", "Barbecue, Continental"]
    })


def test_column_mapping(sample_raw_df):
    renamed, mapping = map_columns(sample_raw_df)
    assert "name" in renamed.columns
    assert "cost" in renamed.columns
    assert "rating" in renamed.columns
    assert "cuisines" in renamed.columns


def test_validate_dataset_success(sample_raw_df):
    renamed, _ = map_columns(sample_raw_df)
    is_valid, msgs = validate_dataset(renamed, required_fields=["name", "cost"])
    assert is_valid is True
    assert "passed" in msgs[0].lower()


def test_validate_dataset_missing_columns():
    invalid_df = pd.DataFrame({"some_random_col": [1, 2, 3]})
    is_valid, msgs = validate_dataset(invalid_df, required_fields=["name", "cost"])
    assert is_valid is False
    assert "missing" in msgs[0].lower()


def test_validate_dataset_empty():
    is_valid, msgs = validate_dataset(pd.DataFrame())
    assert is_valid is False


def test_audit_data_quality():
    test_df = pd.DataFrame({
        "name": ["A", "B", "A"],  # 1 duplicate name
        "cost": ["-100", "800", "invalid"],
        "rating": ["5.5", "4.2", "-1.0"]  # 2 invalid ratings
    })
    audit = audit_data_quality(test_df)
    assert audit["total_rows"] == 3
    assert audit["duplicate_names"] == 1
    assert audit["invalid_cost_count"] >= 2
    assert audit["invalid_rating_count"] >= 2
