"""
Smart Restaurant Recommendation Engine.
Provides transparent multi-criteria filtering, ranking, explanation generation,
and graceful filter relaxation for edge-case queries.
"""

from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np


def filter_restaurants(
    df: pd.DataFrame,
    max_cost: Optional[float] = None,
    min_rating: Optional[float] = None,
    preferred_cuisine: Optional[str] = None,
    locality: Optional[str] = None,
    cluster_id: Optional[int] = None
) -> Tuple[pd.DataFrame, bool]:
    """
    Filter restaurants based on user constraints.
    If no restaurants match, returns relaxed results and a boolean flag indicating relaxation.
    """
    if df.empty:
        return pd.DataFrame(), False
        
    filtered = df.copy()
    
    # 1. Cost filter
    if max_cost is not None and "cost" in filtered.columns:
        filtered = filtered[filtered["cost"] <= max_cost]
        
    # 2. Rating filter
    rating_col = "avg_rating" if "avg_rating" in filtered.columns else "rating"
    if min_rating is not None and rating_col in filtered.columns:
        filtered = filtered[filtered[rating_col] >= min_rating]
        
    # 3. Cuisine filter
    if preferred_cuisine and preferred_cuisine.upper() != "ALL":
        cuisine_query = preferred_cuisine.lower().strip()
        
        def match_cuisine(row) -> bool:
            if "cuisines_list" in row and isinstance(row["cuisines_list"], list):
                return any(cuisine_query in c.lower() for c in row["cuisines_list"])
            elif "cuisines" in row:
                return cuisine_query in str(row["cuisines"]).lower()
            return False
            
        filtered = filtered[filtered.apply(match_cuisine, axis=1)]
        
    # 4. Locality filter
    if locality and locality.upper() != "ALL" and "locality" in filtered.columns:
        filtered = filtered[filtered["locality"].str.lower() == locality.lower().strip()]
        
    # 5. Cluster filter
    if cluster_id is not None and cluster_id >= 0 and "cluster" in filtered.columns:
        filtered = filtered[filtered["cluster"] == cluster_id]
        
    # Check if empty -> Relax constraints gracefully
    if filtered.empty:
        relaxed = df.copy()
        if preferred_cuisine and preferred_cuisine.upper() != "ALL":
            cuisine_query = preferred_cuisine.lower().strip()
            matched_cuisine = relaxed[relaxed["cuisines"].astype(str).str.lower().str.contains(cuisine_query, na=False)]
            if not matched_cuisine.empty:
                relaxed = matched_cuisine
                
        # If budget was strict, relax budget boundary up to min available or 1.5x
        if max_cost is not None and "cost" in relaxed.columns:
            min_avail = relaxed["cost"].min() if not relaxed["cost"].empty else max_cost
            relaxed = relaxed[relaxed["cost"] <= max(max_cost * 1.5, min_avail + 100)]
            
        if min_rating is not None and rating_col in relaxed.columns:
            relaxed = relaxed[relaxed[rating_col] >= max(1.0, min_rating - 0.5)]
            
        if not relaxed.empty:
            return relaxed, True
            
        # Ultimate fallback: return lowest cost available options
        return df.sort_values(by="cost").head(5), True
            
    return filtered, False


def compute_recommendation_score(
    df: pd.DataFrame,
    max_budget: Optional[float] = None,
    preferred_cuisine: Optional[str] = None
) -> pd.DataFrame:
    """
    Rank restaurants using transparent composite multi-criteria scoring (0 - 100):
    - Rating Score (40%)
    - Engagement / Votes Score (25%)
    - Budget Efficiency (20%)
    - Cuisine Alignment (15%)
    """
    if df.empty:
        return pd.DataFrame()
        
    ranked = df.copy()
    rating_col = "avg_rating" if "avg_rating" in ranked.columns else "rating"
    
    # 1. Rating component (0 to 1)
    ratings = ranked[rating_col].fillna(3.5).clip(1.0, 5.0)
    score_rating = ratings / 5.0
    
    # 2. Votes / Popularity component (log scale)
    votes = ranked["votes"].fillna(10).clip(lower=1) if "votes" in ranked.columns else pd.Series(10, index=ranked.index)
    log_votes = np.log1p(votes)
    max_log_votes = log_votes.max() if log_votes.max() > 0 else 1.0
    score_votes = log_votes / max_log_votes
    
    # 3. Budget / Affordability component
    if max_budget and "cost" in ranked.columns:
        costs = ranked["cost"].clip(lower=100)
        # Closer to budget without exceeding is ideal
        budget_ratio = (costs / max_budget).clip(0.1, 1.5)
        score_budget = 1.0 - (budget_ratio - 1.0).abs() * 0.5
        score_budget = score_budget.clip(0.1, 1.0)
    else:
        score_budget = pd.Series(0.8, index=ranked.index)
        
    # 4. Cuisine alignment
    if preferred_cuisine and preferred_cuisine.upper() != "ALL":
        target = preferred_cuisine.lower().strip()
        def calc_cuisine_match(row) -> float:
            primary = str(row.get("primary_cuisine", "")).lower()
            cuisines = str(row.get("cuisines", "")).lower()
            if target == primary:
                return 1.0
            elif target in cuisines:
                return 0.8
            return 0.4
        score_cuisine = ranked.apply(calc_cuisine_match, axis=1)
    else:
        score_cuisine = pd.Series(0.8, index=ranked.index)
        
    # Weighted Composite Score (Scale 0 to 100)
    final_score = (
        (score_rating * 40.0) +
        (score_votes * 25.0) +
        (score_budget * 20.0) +
        (score_cuisine * 15.0)
    ).round(1)
    
    ranked["match_score"] = final_score
    
    # Generate human-readable recommendation reasons
    def build_reason(row) -> str:
        r_val = row.get(rating_col, 4.0)
        c_val = row.get("cost", 800)
        v_val = row.get("votes", 50)
        
        reasons = []
        if r_val >= 4.3:
            reasons.append(f"Exceptional {r_val:.1f}★ rating")
        elif r_val >= 4.0:
            reasons.append(f"Highly rated ({r_val:.1f}★)")
            
        if max_budget and c_val <= max_budget * 0.85:
            reasons.append(f"Budget-friendly (INR {c_val:,.0f} for two)")
            
        if v_val >= 80:
            reasons.append(f"Popular choice ({v_val}+ reviews)")
            
        if not reasons:
            reasons.append(f"Balanced value at INR {c_val:,.0f}")
            
        return " • ".join(reasons)
        
    ranked["recommendation_reason"] = ranked.apply(build_reason, axis=1)
    
    return ranked.sort_values(by="match_score", ascending=False).reset_index(drop=True)
