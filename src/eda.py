"""
Exploratory Data Analysis (EDA) module.
Calculates statistical distributions, top frequencies, correlations, and automated data-driven insights.
"""

from typing import Dict, List, Tuple
import pandas as pd
import numpy as np


def compute_overview_kpis(df: pd.DataFrame) -> Dict[str, any]:
    """
    Calculate executive KPI metrics from the dataset.
    """
    if df.empty:
        return {
            "total_restaurants": 0,
            "avg_cost": 0,
            "median_cost": 0,
            "avg_rating": 0.0,
            "total_cuisines": 0,
            "total_localities": 0
        }
        
    cost_col = "cost" if "cost" in df.columns else None
    rating_col = "avg_rating" if "avg_rating" in df.columns else ("rating" if "rating" in df.columns else None)
    
    avg_cost = float(df[cost_col].mean()) if cost_col else 0.0
    median_cost = float(df[cost_col].median()) if cost_col else 0.0
    avg_rating = float(df[rating_col].mean()) if rating_col else 0.0
    
    # Cuisines count
    if "cuisines_list" in df.columns:
        all_c = set()
        for clist in df["cuisines_list"].dropna():
            if isinstance(clist, list):
                all_c.update(clist)
            elif isinstance(clist, str):
                all_c.update([x.strip() for x in clist.split(",")])
        num_cuisines = len(all_c)
    elif "cuisines" in df.columns:
        num_cuisines = len(df["cuisines"].dropna().unique())
    else:
        num_cuisines = 0
        
    num_localities = len(df["locality"].dropna().unique()) if "locality" in df.columns else 1
    
    return {
        "total_restaurants": len(df),
        "avg_cost": round(avg_cost, 1),
        "median_cost": round(median_cost, 1),
        "avg_rating": round(avg_rating, 2),
        "total_cuisines": num_cuisines,
        "total_localities": num_localities
    }


def compute_top_cuisines(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    Compute most frequent cuisines across all restaurants.
    """
    if df.empty:
        return pd.DataFrame(columns=["cuisine", "count"])
        
    all_cuisines = []
    if "cuisines_list" in df.columns:
        for clist in df["cuisines_list"].dropna():
            if isinstance(clist, list):
                all_cuisines.extend(clist)
            elif isinstance(clist, str):
                all_cuisines.extend([c.strip() for c in clist.split(",") if c.strip()])
    elif "cuisines" in df.columns:
        for cstr in df["cuisines"].dropna():
            all_cuisines.extend([c.strip() for c in str(cstr).split(",") if c.strip()])
            
    if not all_cuisines:
        return pd.DataFrame(columns=["cuisine", "count"])
        
    counts = pd.Series(all_cuisines).value_counts().head(top_n).reset_index()
    counts.columns = ["cuisine", "count"]
    return counts


def compute_locality_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute restaurant counts and cost statistics grouped by locality.
    """
    if df.empty or "locality" not in df.columns:
        return pd.DataFrame()
        
    cost_col = "cost" if "cost" in df.columns else None
    rating_col = "avg_rating" if "avg_rating" in df.columns else "rating"
    
    agg_dict = {"name": "count"}
    if cost_col:
        agg_dict[cost_col] = ["mean", "median"]
    if rating_col in df.columns:
        agg_dict[rating_col] = "mean"
        
    grouped = df.groupby("locality").agg(agg_dict)
    # Flatten multi-level columns
    grouped.columns = ["_".join(c).strip("_") for c in grouped.columns.values]
    grouped.rename(columns={"name_count": "restaurant_count"}, inplace=True)
    return grouped.reset_index().sort_values(by="restaurant_count", ascending=False)


def compute_numerical_correlations(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute pairwise Pearson correlation matrix for numeric columns.
    """
    candidates = ["cost", "avg_rating", "votes", "rating_std", "pos_review_ratio", "num_cuisines", "value_index"]
    valid_cols = [c for c in candidates if c in df.columns and pd.api.types.is_numeric_dtype(df[c])]
    
    if len(valid_cols) < 2:
        return pd.DataFrame()
        
    return df[valid_cols].corr().round(2)


def generate_automated_insights(df: pd.DataFrame) -> List[str]:
    """
    Generate factual, data-driven analytical takeaways based on computed statistics.
    """
    if df.empty:
        return ["No restaurant records available to extract insights."]
        
    insights = []
    kpis = compute_overview_kpis(df)
    
    # 1. Cost Distribution
    if "cost" in df.columns:
        min_cost = df["cost"].min()
        max_cost = df["cost"].max()
        median_cost = df["cost"].median()
        iqr_val = df["cost"].quantile(0.75) - df["cost"].quantile(0.25)
        insights.append(
            f"Cost for two ranges from INR {min_cost:,.0f} to INR {max_cost:,.0f}, "
            f"with a median pricing of INR {median_cost:,.0f} and an IQR spread of INR {iqr_val:,.0f}."
        )
        
    # 2. Rating & Sentiment
    rating_col = "avg_rating" if "avg_rating" in df.columns else "rating"
    if rating_col in df.columns:
        mean_r = df[rating_col].mean()
        high_rated_count = (df[rating_col] >= 4.0).sum()
        pct_high = round((high_rated_count / len(df)) * 100, 1)
        insights.append(
            f"Average customer rating stands at {mean_r:.2f} / 5.0, with {pct_high}% of dining places "
            f"maintaining a solid rating of 4.0 or higher."
        )
        
    # 3. Top Cuisines
    top_c = compute_top_cuisines(df, top_n=3)
    if not top_c.empty:
        c_names = ", ".join(top_c["cuisine"].tolist())
        insights.append(f"Top 3 dominant culinary offerings across the dataset are {c_names}.")
        
    # 4. Correlation Note
    corr_df = compute_numerical_correlations(df)
    if not corr_df.empty and "cost" in corr_df.columns and rating_col in corr_df.columns:
        cost_rating_corr = corr_df.loc["cost", rating_col]
        trend = "positive" if cost_rating_corr > 0.1 else ("negative" if cost_rating_corr < -0.1 else "negligible")
        insights.append(
            f"Correlation between dining cost and average customer rating is {cost_rating_corr:+.2f} ({trend} association), "
            f"indicating higher price points do not guarantee superior user satisfaction alone."
        )
        
    return insights
