"""
Unit tests for clustering algorithms, centroid ordering, and evaluation metrics.
"""

import pytest
import pandas as pd
import numpy as np

from src.clustering import RestaurantClusterModel, generate_cluster_profiles
from src.evaluation import evaluate_clustering, compute_elbow_curve


@pytest.fixture
def sample_clustered_df():
    return pd.DataFrame({
        "name": [f"Rest_{i}" for i in range(12)],
        "cost": [250, 300, 350, 400, 750, 800, 850, 900, 1600, 1800, 2000, 2400],
        "avg_rating": [3.8, 4.0, 4.1, 3.9, 4.2, 4.3, 4.0, 4.4, 4.6, 4.7, 4.5, 4.8],
        "votes": [40, 55, 60, 45, 120, 150, 130, 160, 300, 350, 400, 500],
        "cuisines": ["Fast Food", "North Indian", "Biryani", "South Indian"] * 3
    })


def test_kmeans_clustering(sample_clustered_df):
    model = RestaurantClusterModel(algorithm="kmeans", n_clusters=3, feature_cols=["cost"])
    model.fit(sample_clustered_df)
    
    assert len(model.labels_) == len(sample_clustered_df)
    assert set(model.labels_) == {0, 1, 2}
    
    # Check that Cluster 0 has lower mean cost than Cluster 2 (ordered)
    mean_c0 = sample_clustered_df["cost"][model.labels_ == 0].mean()
    mean_c2 = sample_clustered_df["cost"][model.labels_ == 2].mean()
    assert mean_c0 < mean_c2


def test_agglomerative_clustering(sample_clustered_df):
    model = RestaurantClusterModel(algorithm="agglomerative", n_clusters=3, feature_cols=["cost"])
    model.fit(sample_clustered_df)
    
    assert len(model.labels_) == len(sample_clustered_df)
    assert len(set(model.labels_)) == 3


def test_cluster_profiles_generation(sample_clustered_df):
    model = RestaurantClusterModel(algorithm="kmeans", n_clusters=3, feature_cols=["cost"])
    model.fit(sample_clustered_df)
    df_clustered = sample_clustered_df.copy()
    df_clustered["cluster"] = model.labels_
    
    profiles = generate_cluster_profiles(df_clustered, cluster_col="cluster")
    assert len(profiles) == 3
    assert "Segment Name" in profiles.columns
    assert "Mean Cost (INR)" in profiles.columns


def test_evaluation_metrics(sample_clustered_df):
    X = sample_clustered_df[["cost"]].values
    labels = np.array([0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2])
    metrics = evaluate_clustering(X, labels)
    
    assert metrics["silhouette_score"] is not None
    assert metrics["silhouette_score"] > 0.4
    assert metrics["davies_bouldin_index"] is not None
