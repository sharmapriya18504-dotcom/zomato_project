"""
Location and Market Geography module.
Provides locality-level density, cost distributions, and geographic fallbacks.
"""

from typing import Dict, List, Optional
import pandas as pd
import numpy as np


def analyze_market_density(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute locality-level market concentration and dining attributes.
    """
    if df.empty or "locality" not in df.columns:
        return pd.DataFrame()
        
    rating_col = "avg_rating" if "avg_rating" in df.columns else "rating"
    cost_col = "cost" if "cost" in df.columns else None
    
    aggs = {"name": "count"}
    if cost_col:
        aggs[cost_col] = ["mean", "median", "min", "max"]
    if rating_col in df.columns:
        aggs[rating_col] = "mean"
    if "votes" in df.columns:
        aggs["votes"] = "sum"
        
    grouped = df.groupby("locality").agg(aggs)
    grouped.columns = ["_".join(c).strip("_") for c in grouped.columns.values]
    
    rename_dict = {
        "name_count": "restaurant_count",
        f"{cost_col}_mean": "avg_cost",
        f"{cost_col}_median": "median_cost",
        f"{cost_col}_min": "min_cost",
        f"{cost_col}_max": "max_cost",
        f"{rating_col}_mean": "avg_rating",
        "votes_sum": "total_market_votes"
    }
    grouped.rename(columns={k: v for k, v in rename_dict.items() if k in grouped.columns}, inplace=True)
    
    grouped["market_share_pct"] = (
        (grouped["restaurant_count"] / len(df)) * 100
    ).round(1)
    
    if "avg_cost" in grouped.columns:
        grouped["avg_cost"] = grouped["avg_cost"].round(0)
    if "avg_rating" in grouped.columns:
        grouped["avg_rating"] = grouped["avg_rating"].round(2)
        
    return grouped.reset_index().sort_values(by="restaurant_count", ascending=False)


def analyze_locality_price_tiers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate the proportion of Budget, Mid-Range, and Premium restaurants per locality.
    """
    if df.empty or "locality" not in df.columns:
        return pd.DataFrame()
        
    tier_col = "price_tier" if "price_tier" in df.columns else None
    if not tier_col:
        return pd.DataFrame()
        
    crosstab = pd.crosstab(df["locality"], df[tier_col], normalize="index") * 100
    return crosstab.round(1).reset_index()
