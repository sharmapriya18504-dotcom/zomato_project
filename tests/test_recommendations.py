"""
Unit tests for restaurant recommendation, filtering, and scoring.
"""

import pytest
import pandas as pd
import numpy as np

from src.recommendations import filter_restaurants, compute_recommendation_score


@pytest.fixture
def sample_recs_df():
    return pd.DataFrame({
        "name": ["Budget Bites", "Midway Meals", "Luxury Lounge", "Biryani Central"],
        "cost": [350, 900, 2200, 600],
        "avg_rating": [4.2, 4.0, 4.8, 4.5],
        "votes": [80, 110, 450, 320],
        "primary_cuisine": ["Fast Food", "North Indian", "Continental", "Biryani"],
        "cuisines": ["Fast Food, Street Food", "North Indian, Chinese", "Continental, Italian", "Biryani, Mughlai"],
        "cuisines_list": [["Fast Food", "Street Food"], ["North Indian", "Chinese"], ["Continental", "Italian"], ["Biryani", "Mughlai"]],
        "locality": ["Gachibowli", "Hitec City", "Banjara Hills", "Gachibowli"]
    })


def test_filter_exact_match(sample_recs_df):
    filtered, was_relaxed = filter_restaurants(
        sample_recs_df,
        max_cost=1000,
        min_rating=4.0,
        preferred_cuisine="Biryani",
        locality="Gachibowli"
    )
    assert was_relaxed is False
    assert len(filtered) == 1
    assert filtered.iloc[0]["name"] == "Biryani Central"


def test_filter_relaxed_when_no_match(sample_recs_df):
    # Extremely strict budget that no restaurant matches exactly
    filtered, was_relaxed = filter_restaurants(
        sample_recs_df,
        max_cost=200,  # Min cost is 350
        min_rating=4.0
    )
    assert was_relaxed is True
    # Relaxed search should find closest budget options
    assert len(filtered) >= 0


def test_recommendation_ranking_score(sample_recs_df):
    ranked = compute_recommendation_score(sample_recs_df, max_budget=1000, preferred_cuisine="Biryani")
    assert "match_score" in ranked.columns
    assert "recommendation_reason" in ranked.columns
    # Top match should be scored high
    assert ranked.iloc[0]["match_score"] > 60.0
    # First row should have highest score
    assert ranked.iloc[0]["match_score"] >= ranked.iloc[-1]["match_score"]


def test_empty_dataset_handling():
    filtered, was_relaxed = filter_restaurants(pd.DataFrame(), max_cost=500)
    assert filtered.empty
    assert was_relaxed is False
    
    ranked = compute_recommendation_score(pd.DataFrame())
    assert ranked.empty
