"""
Page 3: Advanced Restaurant Cost Clustering
Interactive K-Means and Agglomerative clustering with custom feature spaces,
automated cluster profiling, and cluster metrics.
"""

import streamlit as st
import pandas as pd

from src.clustering import RestaurantClusterModel, generate_cluster_profiles
from src.evaluation import evaluate_clustering, compute_elbow_curve
from src.reporting import export_dataframe_to_csv
from components.sidebar_filters import render_sidebar_controls
from components.charts import plot_cluster_cost_boxplots, plot_cost_vs_rating, plot_elbow_curve_chart
from src.config import CLUSTER_COLORS

st.set_page_config(
    page_title="Cost Clustering | Zomato Intelligence",
    page_icon="🤖",
    layout="wide"
)

df, model_settings = render_sidebar_controls()

st.title("🤖 Advanced Restaurant Cost Clustering")
st.markdown("""
Segmenting restaurants into data-driven pricing and experience tiers using unsupervised Machine Learning.
""")

# Feature selection controls
available_features = [c for c in ["cost", "avg_rating", "votes", "num_cuisines"] if c in df.columns]
selected_features = st.multiselect(
    "Select Features for Clustering Pipeline:",
    options=available_features,
    default=["cost"] if "cost" in available_features else available_features[:1]
)

if not selected_features:
    st.warning("Please select at least one feature to run the clustering model.")
    st.stop()

# Train Model
cluster_model = RestaurantClusterModel(
    algorithm=model_settings["algorithm"],
    n_clusters=model_settings["n_clusters"],
    feature_cols=selected_features,
    scaler_type=model_settings["scaler"],
    linkage=model_settings["linkage"]
)

with st.spinner("Fitting unsupervised clustering model..."):
    cluster_model.fit(df)
    
df_clustered = df.copy()
df_clustered["cluster"] = cluster_model.labels_

# Evaluate Model
X_scaled = cluster_model.preprocessor.transform(df)
metrics = evaluate_clustering(X_scaled, cluster_model.labels_)

# Metric Badges
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("Clusters Fitted (K)", f"{model_settings['n_clusters']}")
with m2:
    sil_str = f"{metrics['silhouette_score']:.3f}" if metrics['silhouette_score'] is not None else "N/A"
    st.metric("Silhouette Score", sil_str, help="Higher is better ([-1, 1])")
with m3:
    db_str = f"{metrics['davies_bouldin_index']:.3f}" if metrics['davies_bouldin_index'] is not None else "N/A"
    st.metric("Davies-Bouldin Index", db_str, help="Lower is better")
with m4:
    ch_str = f"{metrics['calinski_harabasz_score']:.1f}" if metrics['calinski_harabasz_score'] is not None else "N/A"
    st.metric("Calinski-Harabasz", ch_str, help="Higher is better")

st.divider()

# Cluster Profiles Table
st.subheader("📋 Data-Driven Cluster Profiles")
profiles_df = generate_cluster_profiles(df_clustered, cluster_col="cluster")
st.dataframe(profiles_df, use_container_width=True)

# Visualizations
c1, c2 = st.columns(2)
with c1:
    st.plotly_chart(plot_cluster_cost_boxplots(df_clustered, cluster_col="cluster"), use_container_width=True)
with c2:
    st.plotly_chart(plot_cost_vs_rating(df_clustered, cluster_col="cluster"), use_container_width=True)

st.divider()

# Download Clustered Data
csv_bytes = export_dataframe_to_csv(df_clustered)
st.download_button(
    label="📥 Download Dataset with Cluster Labels (CSV)",
    data=csv_bytes,
    file_name=f"zomato_clustered_k{model_settings['n_clusters']}.csv",
    mime="text/csv"
)
