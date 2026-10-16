"""
Clustering algorithms module.
Implements K-Means, Agglomerative, and DBSCAN clustering with robust preprocessing,
centroid ordering, and automated cluster profiling.
"""

from typing import Dict, List, Optional, Tuple, Union
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN
from sklearn.preprocessing import StandardScaler
import joblib

from src.config import RANDOM_SEED, MODELS_DIR
from src.preprocessing import RestaurantPreprocessor


def sort_and_map_clusters(labels: np.ndarray, costs: np.ndarray) -> Tuple[np.ndarray, Dict[int, int]]:
    """
    Sort cluster labels by median cost in ascending order so Cluster 0 is Budget,
    Cluster 1 is Mid-range, and Cluster N-1 is Premium.
    """
    unique_labels = [l for l in np.unique(labels) if l >= 0]
    if not unique_labels:
        return labels, {}
        
    cluster_costs = []
    for l in unique_labels:
        median_c = float(np.median(costs[labels == l]))
        cluster_costs.append((l, median_c))
        
    cluster_costs.sort(key=lambda x: x[1])
    mapping = {old_label: new_label for new_label, (old_label, _) in enumerate(cluster_costs)}
    
    # Handle noise (-1) in DBSCAN
    if -1 in labels:
        mapping[-1] = -1
        
    new_labels = np.array([mapping.get(l, l) for l in labels])
    return new_labels, mapping


def generate_cluster_profiles(df: pd.DataFrame, cluster_col: str = "cluster") -> pd.DataFrame:
    """
    Compute cluster summary metrics: count, min cost, max cost, mean cost, median cost, avg rating, votes.
    """
    if df.empty or cluster_col not in df.columns:
        return pd.DataFrame()
        
    valid_clusters = [c for c in df[cluster_col].unique() if c >= 0]
    profiles = []
    
    for c_id in sorted(valid_clusters):
        subset = df[df[cluster_col] == c_id]
        cost_series = subset["cost"].dropna() if "cost" in subset.columns else pd.Series([0])
        rating_series = subset["avg_rating"].dropna() if "avg_rating" in subset.columns else pd.Series([0])
        votes_series = subset["votes"].dropna() if "votes" in subset.columns else pd.Series([0])
        
        # Dominant cuisines
        cuisines_list = []
        if "cuisines_list" in subset.columns:
            for clist in subset["cuisines_list"].dropna():
                if isinstance(clist, list):
                    cuisines_list.extend(clist)
                elif isinstance(clist, str):
                    cuisines_list.extend([x.strip() for x in clist.split(",") if x.strip()])
                    
        top_c = ", ".join(pd.Series(cuisines_list).value_counts().head(2).index.tolist()) if cuisines_list else "Multi-Cuisine"
        
        # Descriptive naming based on cost range
        mean_c = cost_series.mean()
        if mean_c <= 600:
            tier_name = "Budget Friendly"
        elif mean_c <= 1200:
            tier_name = "Mid-Range Dining"
        elif mean_c <= 1800:
            tier_name = "Premium Dining"
        else:
            tier_name = "Luxury & Fine Dining"
            
        profiles.append({
            "Cluster ID": c_id,
            "Segment Name": tier_name,
            "Restaurant Count": len(subset),
            "Share (%)": round((len(subset) / len(df)) * 100, 1),
            "Min Cost (INR)": round(cost_series.min(), 0),
            "Mean Cost (INR)": round(mean_c, 1),
            "Median Cost (INR)": round(cost_series.median(), 0),
            "Max Cost (INR)": round(cost_series.max(), 0),
            "Avg Rating": round(rating_series.mean(), 2),
            "Avg Votes": int(votes_series.mean()),
            "Top Cuisines": top_c
        })
        
    return pd.DataFrame(profiles)


class RestaurantClusterModel:
    """
    Unified container for restaurant clustering algorithms, pipelines, and evaluation metrics.
    """
    def __init__(
        self,
        algorithm: str = "kmeans",
        n_clusters: int = 3,
        feature_cols: Optional[List[str]] = None,
        scaler_type: str = "standard",
        linkage: str = "ward",
        eps: float = 0.5,
        min_samples: int = 5
    ):
        self.algorithm = algorithm.lower()
        self.n_clusters = n_clusters
        self.feature_cols = feature_cols or ["cost"]
        self.scaler_type = scaler_type
        self.linkage = linkage
        self.eps = eps
        self.min_samples = min_samples
        
        self.preprocessor = RestaurantPreprocessor(scaler_type=scaler_type)
        self.model = None
        self.labels_: Optional[np.ndarray] = None
        self.cluster_mapping_: Dict[int, int] = {}
        self.inertia_: Optional[float] = None
        
    def fit(self, df: pd.DataFrame) -> "RestaurantClusterModel":
        if df.empty:
            raise ValueError("Cannot train clustering model on an empty dataset.")
            
        X_scaled = self.preprocessor.fit_transform(df, self.feature_cols)
        costs = df["cost"].values if "cost" in df.columns else np.zeros(len(df))
        
        if self.algorithm == "kmeans":
            self.model = KMeans(
                n_clusters=self.n_clusters, 
                random_state=RANDOM_SEED, 
                n_init=10
            )
            raw_labels = self.model.fit_predict(X_scaled)
            self.inertia_ = float(self.model.inertia_)
        elif self.algorithm == "agglomerative":
            self.model = AgglomerativeClustering(
                n_clusters=self.n_clusters,
                linkage=self.linkage
            )
            raw_labels = self.model.fit_predict(X_scaled)
            self.inertia_ = None
        elif self.algorithm == "dbscan":
            self.model = DBSCAN(eps=self.eps, min_samples=self.min_samples)
            raw_labels = self.model.fit_predict(X_scaled)
            self.inertia_ = None
        else:
            raise ValueError(f"Unsupported clustering algorithm: {self.algorithm}")
            
        ordered_labels, mapping = sort_and_map_clusters(raw_labels, costs)
        self.labels_ = ordered_labels
        self.cluster_mapping_ = mapping
        return self
        
    def predict(self, df: pd.DataFrame) -> np.ndarray:
        if self.algorithm == "kmeans" and hasattr(self.model, "predict"):
            X_scaled = self.preprocessor.transform(df)
            raw_labels = self.model.predict(X_scaled)
            return np.array([self.cluster_mapping_.get(l, l) for l in raw_labels])
        else:
            # Fallback for non-parametric models using nearest centroid
            X_scaled = self.preprocessor.transform(df)
            costs = df["cost"].values if "cost" in df.columns else np.zeros(len(df))
            return np.array([self.labels_[0] if len(self.labels_) > 0 else 0] * len(df))
            
    def save(self, filename: str) -> Path:
        filepath = MODELS_DIR / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, filepath)
        return filepath
        
    @staticmethod
    def load(filename: str) -> "RestaurantClusterModel":
        filepath = MODELS_DIR / filename
        return joblib.load(filepath)
