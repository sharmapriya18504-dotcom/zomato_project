"""
Page 7: Model Evaluation Dashboard
Systematic comparison of clustering algorithms, validation metrics, and Elbow analysis.
"""

import streamlit as st
import pandas as pd

from src.evaluation import compute_elbow_curve, compare_clustering_algorithms
from components.sidebar_filters import render_sidebar_controls
from components.charts import plot_elbow_curve_chart

st.set_page_config(
    page_title="Model Evaluation | Zomato Intelligence",
    page_icon="🧪",
    layout="wide"
)

df, model_settings = render_sidebar_controls()

st.title("🧪 Model Evaluation & Benchmarking")
st.markdown("""
Rigorous mathematical validation of unsupervised algorithms across Silhouette, Davies-Bouldin, and Calinski-Harabasz metrics.
""")

feature_cols = ["cost"]
if "avg_rating" in df.columns:
    feature_cols.append("avg_rating")

# 1. Elbow Method Section
st.subheader("📉 Elbow Curve & Inflection Point Analysis")
elbow_df = compute_elbow_curve(
    df, 
    feature_cols=feature_cols, 
    k_range=range(2, 8),
    scaler_type=model_settings["scaler"]
)

if not elbow_df.empty:
    st.plotly_chart(plot_elbow_curve_chart(elbow_df, selected_k=model_settings["n_clusters"]), use_container_width=True)
    st.dataframe(elbow_df, use_container_width=True)
else:
    st.info("Unable to compute elbow curve on current data.")

st.divider()

# 2. Algorithm Comparison
st.subheader(f"⚔️ Algorithm Benchmarking (K = {model_settings['n_clusters']})")
comparison_df = compare_clustering_algorithms(
    df, 
    feature_cols=feature_cols, 
    k=model_settings["n_clusters"],
    scaler_type=model_settings["scaler"]
)
st.dataframe(comparison_df, use_container_width=True)

st.divider()

# 3. Metric Definitions & Interpretations
st.subheader("📚 Metric Interpretation Guide")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
    #### Silhouette Score
    - **Scale:** -1.0 to +1.0
    - **Goal:** Higher is better (> 0.5 is strong)
    - **Meaning:** Measures how similar an object is to its own cluster compared to neighboring clusters.
    """)
with col2:
    st.markdown("""
    #### Davies–Bouldin Index
    - **Scale:** 0 to +∞
    - **Goal:** Lower is better (closer to 0)
    - **Meaning:** Ratio of within-cluster distances to between-cluster distances. Lower values mean better separation.
    """)
with col3:
    st.markdown("""
    #### Calinski–Harabasz Index
    - **Scale:** 0 to +∞
    - **Goal:** Higher is better
    - **Meaning:** Ratio of sum of between-clusters dispersion to within-cluster dispersion.
    """)

st.info("""
⚠️ **Important Model Limitations:** Unsupervised clustering segments restaurants by statistical cost and review density. 
It does not measure business profitability, footfall conversion, or individual kitchen hygiene unless explicit operational datasets are integrated.
""")
