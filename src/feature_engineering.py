"""
Feature engineering module.
Extracts rich signals from raw metadata, review text, ratings, timings, and URLs.
"""

from pathlib import Path
from typing import Optional, Tuple
import pandas as pd
import numpy as np

from src.config import ENRICHED_DATA_PATH
from src.preprocessing import clean_cost_series, clean_rating_series


def extract_location_from_url(url: str) -> Tuple[str, str]:
    """
    Extract city and locality from standard Zomato restaurant URLs.
    Example: https://www.zomato.com/hyderabad/beyond-flavours-gachibowli -> ('Hyderabad', 'Gachibowli')
    """
    if not isinstance(url, str) or not url.startswith("http"):
        return "Hyderabad", "Gachibowli"
        
    parts = url.strip().split("/")
    city = "Hyderabad"
    locality = "Gachibowli"
    
    if len(parts) >= 4 and parts[3].strip():
        city_raw = parts[3].replace("-", " ").title()
        if len(city_raw) < 20 and not city_raw.lower().startswith("thetilt"):
            city = city_raw
            
    if len(parts) >= 5 and parts[4].strip():
        slug = parts[4].strip()
        if "-" in slug:
            sub = slug.split("-")[-1].replace("_", " ").title()
            if len(sub) > 2 and not sub.isdigit():
                locality = sub
                
    return city, locality


def aggregate_reviews_data(df_reviews: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate user reviews per restaurant:
    - Average Rating
    - Total Votes / Review Count
    - Rating Standard Deviation (consistency)
    - Positive Review Ratio (ratings >= 4.0)
    - Total pictures uploaded
    """
    if df_reviews.empty or "Restaurant" not in df_reviews.columns:
        return pd.DataFrame()
        
    rev_copy = df_reviews.copy()
    
    # Normalize Restaurant Name
    rev_copy["Restaurant"] = rev_copy["Restaurant"].astype(str).str.strip()
    
    # Clean numeric rating
    if "Rating" in rev_copy.columns:
        rev_copy["rating_clean"] = clean_rating_series(rev_copy["Rating"])
    else:
        rev_copy["rating_clean"] = 3.8
        
    # Pictures column
    if "Pictures" not in rev_copy.columns:
        rev_copy["Pictures"] = 0
    else:
        rev_copy["Pictures"] = pd.to_numeric(rev_copy["Pictures"], errors="coerce").fillna(0)
        
    grouped = rev_copy.groupby("Restaurant")
    
    stats = grouped.agg(
        avg_rating=("rating_clean", "mean"),
        votes=("rating_clean", "count"),
        rating_std=("rating_clean", "std"),
        total_pictures=("Pictures", "sum")
    ).reset_index()
    
    # Positive review ratio (% of reviews >= 4.0)
    pos_reviews = rev_copy[rev_copy["rating_clean"] >= 4.0].groupby("Restaurant")["rating_clean"].count()
    stats["pos_review_ratio"] = (
        stats["Restaurant"].map(pos_reviews).fillna(0) / stats["votes"].replace(0, 1)
    ).round(2)
    
    stats["avg_rating"] = stats["avg_rating"].round(1)
    stats["rating_std"] = stats["rating_std"].fillna(0.0).round(2)
    stats["votes"] = stats["votes"].astype(int)
    stats["total_pictures"] = stats["total_pictures"].astype(int)
    
    return stats


def build_enriched_dataset(
    df_meta: pd.DataFrame, 
    df_reviews: Optional[pd.DataFrame] = None,
    save_to_disk: bool = True
) -> pd.DataFrame:
    """
    Combine metadata, aggregate review features, parse location, extract cuisines,
    and build a unified master dataset for analytics and ML models.
    """
    if df_meta.empty:
        return pd.DataFrame()
        
    df = df_meta.copy()
    
    # Ensure standard names
    col_mapping = {col: col.lower().strip() for col in df.columns}
    df.rename(columns=col_mapping, inplace=True)
    
    # Standardize cost
    if "cost" in df.columns:
        df["cost"] = clean_cost_series(df["cost"])
    else:
        df["cost"] = 800.0
        
    # Drop rows without valid cost
    df = df.dropna(subset=["cost"]).reset_index(drop=True)
    
    # Standardize name
    name_col = "name" if "name" in df.columns else df.columns[0]
    df["name"] = df[name_col].astype(str).str.strip()
    
    # Aggregate Reviews if provided
    if df_reviews is not None and not df_reviews.empty:
        rev_stats = aggregate_reviews_data(df_reviews)
        if not rev_stats.empty:
            df = pd.merge(df, rev_stats, left_on="name", right_on="Restaurant", how="left")
            if "Restaurant" in df.columns:
                df.drop(columns=["Restaurant"], inplace=True)
                
    # Fill defaults for missing ratings/votes if no reviews matched
    if "avg_rating" not in df.columns:
        df["avg_rating"] = 3.8
    else:
        df["avg_rating"] = df["avg_rating"].fillna(3.8).round(1)
        
    if "votes" not in df.columns:
        df["votes"] = 45
    else:
        df["votes"] = df["votes"].fillna(25).astype(int)
        
    if "pos_review_ratio" not in df.columns:
        df["pos_review_ratio"] = 0.65
    else:
        df["pos_review_ratio"] = df["pos_review_ratio"].fillna(0.60)
        
    if "total_pictures" not in df.columns:
        df["total_pictures"] = 5
    else:
        df["total_pictures"] = df["total_pictures"].fillna(0).astype(int)
        
    # Parse Locations from Links
    if "links" in df.columns:
        locations = df["links"].apply(extract_location_from_url)
        df["city"] = [loc[0] for loc in locations]
        df["locality"] = [loc[1] for loc in locations]
    else:
        df["city"] = "Hyderabad"
        df["locality"] = "Gachibowli"
        
    # Parse Cuisines
    if "cuisines" in df.columns:
        df["cuisines_list"] = df["cuisines"].astype(str).apply(
            lambda x: [c.strip() for c in x.split(",") if c.strip() and c.strip().lower() != "nan"]
        )
        df["primary_cuisine"] = df["cuisines_list"].apply(lambda x: x[0] if len(x) > 0 else "North Indian")
        df["num_cuisines"] = df["cuisines_list"].apply(len)
    else:
        df["cuisines"] = "North Indian, Chinese"
        df["cuisines_list"] = [["North Indian", "Chinese"]] * len(df)
        df["primary_cuisine"] = "North Indian"
        df["num_cuisines"] = 2
        
    # Cost segment tags (heuristic baseline)
    def assign_price_tier(cost: float) -> str:
        if cost <= 500:
            return "Budget Friendly (<= 500)"
        elif cost <= 1200:
            return "Mid-Range (501 - 1,200)"
        elif cost <= 1800:
            return "Premium Dining (1,201 - 1,800)"
        else:
            return "Luxury & Fine Dine (> 1,800)"
            
    df["price_tier"] = df["cost"].apply(assign_price_tier)
    
    # Value for Money index: rating / (log(cost + 1))
    df["value_index"] = (df["avg_rating"] / np.log(df["cost"] + 10)).round(2)
    
    if save_to_disk:
        ENRICHED_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(ENRICHED_DATA_PATH, index=False, encoding="utf-8")
        
    return df
