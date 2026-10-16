"""
Clustering evaluation metrics module.
Calculates Silhouette Score, Davies-Bouldin Index, Calinski-Harabasz Score,
and computes Elbow curve comparisons.
"""

from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score
from sklearn.cluster import KMeans, AgglomerativeClustering

from src.config import RANDOM_SEED
from src.preprocessing import RestaurantPreprocessor


def evaluate_clustering(
    X_scaled: np.ndarray, 
    labels: np.ndarray
) -> Dict[str, Optional[float]]:
    """
    Compute standard unsupervised clustering evaluation metrics.
    Handles edge cases (all identical labels or single point clusters) gracefully.
    """
    valid_labels = np.unique(labels[labels >= 0])
    num_clusters = len(valid_labels)
    
    if num_clusters < 2 or len(labels) <= num_clusters:
        return {
            "silhouette_score": None,
            "davies_bouldin_index": None,
            "calinski_harabasz_score": None,
            "num_clusters": num_clusters
        }
        
    try:
        sil = float(silhouette_score(X_scaled, labels))
    except Exception:
        sil = None
        
    try:
        db = float(davies_bouldin_score(X_scaled, labels))
    except Exception:
        db = None
        
    try:
        ch = float(calinski_harabasz_score(X_scaled, labels))
    except Exception:
        ch = None
        
    return {
        "silhouette_score": round(sil, 3) if sil is not None else None,
        "davies_bouldin_index": round(db, 3) if db is not None else None,
        "calinski_harabasz_score": round(ch, 1) if ch is not None else None,
        "num_clusters": num_clusters
    }


def compute_elbow_curve(
    df: pd.DataFrame, 
    feature_cols: List[str], 
    k_range: range = range(2, 8),
    scaler_type: str = "standard"
) -> pd.DataFrame:
    """
    Iterate over candidate K values, computing Inertia, Silhouette, and Davies-Bouldin.
    """
    if df.empty or not feature_cols:
        return pd.DataFrame()
        
    preprocessor = RestaurantPreprocessor(scaler_type=scaler_type)
    X_scaled = preprocessor.fit_transform(df, feature_cols)
    
    records = []
    for k in k_range:
        if k >= len(df):
            continue
            
        km = KMeans(n_clusters=k, random_state=RANDOM_SEED, n_init=10)
        labels = km.fit_predict(X_scaled)
        metrics = evaluate_clustering(X_scaled, labels)
        
        records.append({
            "k": k,
            "inertia": round(float(km.inertia_), 2),
            "silhouette_score": metrics["silhouette_score"],
            "davies_bouldin_index": metrics["davies_bouldin_index"],
            "calinski_harabasz_score": metrics["calinski_harabasz_score"]
        })
        
    return pd.DataFrame(records)


def compare_clustering_algorithms(
    df: pd.DataFrame, 
    feature_cols: List[str], 
    k: int = 3,
    scaler_type: str = "standard"
) -> pd.DataFrame:
    """
    Evaluate multiple algorithms on the exact same preprocessed feature space.
    """
    if df.empty or not feature_cols:
        return pd.DataFrame()
        
    preprocessor = RestaurantPreprocessor(scaler_type=scaler_type)
    X_scaled = preprocessor.fit_transform(df, feature_cols)
    
    # 1. K-Means
    km = KMeans(n_clusters=k, random_state=RANDOM_SEED, n_init=10)
    km_labels = km.fit_predict(X_scaled)
    km_metrics = evaluate_clustering(X_scaled, km_labels)
    
    # 2. Agglomerative (Ward)
    agg_ward = AgglomerativeClustering(n_clusters=k, linkage="ward")
    agg_ward_labels = agg_ward.fit_predict(X_scaled)
    agg_ward_metrics = evaluate_clustering(X_scaled, agg_ward_labels)
    
    # 3. Agglomerative (Average)
    agg_avg = AgglomerativeClustering(n_clusters=k, linkage="average")
    agg_avg_labels = agg_avg.fit_predict(X_scaled)
    agg_avg_metrics = evaluate_clustering(X_scaled, agg_avg_labels)
    
    comparison = [
        {
            "Algorithm": "K-Means",
            "Clusters": k,
            "Silhouette Score": km_metrics["silhouette_score"],
            "Davies-Bouldin": km_metrics["davies_bouldin_index"],
            "Calinski-Harabasz": km_metrics["calinski_harabasz_score"],
            "Inertia": round(float(km.inertia_), 1)
        },
        {
            "Algorithm": "Agglomerative (Ward)",
            "Clusters": k,
            "Silhouette Score": agg_ward_metrics["silhouette_score"],
            "Davies-Bouldin": agg_ward_metrics["davies_bouldin_index"],
            "Calinski-Harabasz": agg_ward_metrics["calinski_harabasz_score"],
            "Inertia": None
        },
        {
            "Algorithm": "Agglomerative (Average)",
            "Clusters": k,
            "Silhouette Score": agg_avg_metrics["silhouette_score"],
            "Davies-Bouldin": agg_avg_metrics["davies_bouldin_index"],
            "Calinski-Harabasz": agg_avg_metrics["calinski_harabasz_score"],
            "Inertia": None
        }
    ]
    return pd.DataFrame(comparison)
