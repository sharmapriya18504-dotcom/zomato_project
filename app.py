"""
Zomato Restaurant Intelligence Platform — Main Application Entrypoint
Cost Clustering, Market Analytics & Smart Recommendations
Developed by Priya Sharma
"""

import streamlit as st
import pandas as pd

from components.sidebar_filters import render_sidebar_controls
from components.kpi_cards import render_kpi_card
from src.eda import compute_overview_kpis, generate_automated_insights
from src.clustering import RestaurantClusterModel, generate_cluster_profiles
from components.charts import plot_cluster_cost_boxplots, plot_cost_vs_rating

st.set_page_config(
    page_title="Zomato Restaurant Intelligence Platform | Priya Sharma",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Dark Glassmorphism Theme)
st.markdown("""
<style>
    .main {
        background-color: #0B0E14;
        color: #F8FAFC;
    }
    .stMetric {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 14px 18px;
        border-radius: 12px;
    }
    h1, h2, h3 {
        color: #FFFFFF;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    .hero-banner {
        background: linear-gradient(135deg, rgba(226, 55, 68, 0.15) 0%, rgba(59, 130, 246, 0.1) 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 30px;
        margin-bottom: 24px;
    }
    .page-nav-card {
        background: rgba(21, 28, 44, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 18px;
        height: 100%;
        transition: transform 0.2s;
    }
</style>
""", unsafe_allow_html=True)

# Render Global Sidebar
df, model_settings = render_sidebar_controls()

# Hero Banner
st.markdown("""
<div class="hero-banner">
    <div style="display: inline-block; background: rgba(226, 55, 68, 0.2); border: 1px solid #E23744; color: #FF5A66; padding: 4px 14px; border-radius: 999px; font-size: 0.82rem; font-weight: 700; margin-bottom: 12px;">
        🚀 Production-Grade Machine Learning & Market Intelligence
    </div>
    <h1 style="font-size: 2.4rem; margin: 0 0 10px 0;">
        Zomato Restaurant Intelligence Platform
    </h1>
    <p style="font-size: 1.05rem; color: #94A3B8; margin: 0 0 16px 0; max-width: 850px;">
        Cost Clustering, Market Analytics & Smart Recommendations across 105+ dining establishments in Hyderabad.
        Powered by Scikit-Learn unsupervised clustering, Plotly interactive analytics, and multi-criteria recommendation scoring.
    </p>
    <div style="font-size: 0.85rem; color: #CBD5E1;">
        Developed with ❤️ by <strong>Priya Sharma</strong> • B.Tech Student | Aspiring Data Scientist & ML Engineer
    </div>
</div>
""", unsafe_allow_html=True)

# Executive KPIs
kpis = compute_overview_kpis(df)
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    render_kpi_card("Total Restaurants", f"{kpis['total_restaurants']}", "Cataloged listings", "#E23744", "🍽️")
with col2:
    render_kpi_card("Avg Dining Cost", f"INR {kpis['avg_cost']:,.0f}", f"Median: INR {kpis['median_cost']:,.0f}", "#3B82F6", "💵")
with col3:
    render_kpi_card("Avg Customer Rating", f"{kpis['avg_rating']:.2f}★", "From 10,000+ reviews", "#10B981", "⭐")
with col4:
    render_kpi_card("Cuisines Tracked", f"{kpis['total_cuisines']}", "Diverse food styles", "#F59E0B", "🍲")
with col5:
    render_kpi_card("Active Clusters", f"K = {model_settings['n_clusters']}", f"Algorithm: {model_settings['algorithm'].upper()}", "#8B5CF6", "🤖")

st.divider()

# Multi-Page Navigation Hub
st.subheader("🧭 Platform Navigation Hub")
st.markdown("Explore dedicated analytical modules from the sidebar or click through below:")

nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)

with nav_col1:
    st.markdown("""
    <div class="page-nav-card">
        <h4>📊 1. Executive Overview</h4>
        <p style="font-size: 0.85rem; color: #94A3B8;">High-level market summary, core KPIs, and automated factual insights.</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div class="page-nav-card" style="margin-top: 14px;">
        <h4>📈 2. Exploratory Analysis</h4>
        <p style="font-size: 0.85rem; color: #94A3B8;">Detailed distributions, IQR outlier checks, and correlation heatmaps.</p>
    </div>
    """, unsafe_allow_html=True)

with nav_col2:
    st.markdown("""
    <div class="page-nav-card">
        <h4>🤖 3. Cost Clustering</h4>
        <p style="font-size: 0.85rem; color: #94A3B8;">K-Means & Agglomerative clustering, profiles, and boxplot segmentation.</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div class="page-nav-card" style="margin-top: 14px;">
        <h4>🗺️ 4. Location Intelligence</h4>
        <p style="font-size: 0.85rem; color: #94A3B8;">Locality dining density, market concentration, and geographic fallbacks.</p>
    </div>
    """, unsafe_allow_html=True)

with nav_col3:
    st.markdown("""
    <div class="page-nav-card">
        <h4>🔍 5. Restaurant Finder</h4>
        <p style="font-size: 0.85rem; color: #94A3B8;">Multi-criteria recommendation engine with relaxed filter fallbacks.</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div class="page-nav-card" style="margin-top: 14px;">
        <h4>⚔️ 6. Competitor Analysis</h4>
        <p style="font-size: 0.85rem; color: #94A3B8;">Benchmark specific restaurants against local category peers.</p>
    </div>
    """, unsafe_allow_html=True)

with nav_col4:
    st.markdown("""
    <div class="page-nav-card">
        <h4>🧪 7. Model Evaluation</h4>
        <p style="font-size: 0.85rem; color: #94A3B8;">Elbow curve, Silhouette scores, and Davies-Bouldin benchmarking.</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div class="page-nav-card" style="margin-top: 14px;">
        <h4>📑 8. Reports & Exports</h4>
        <p style="font-size: 0.85rem; color: #94A3B8;">Download executive PDF reports and custom filtered CSV records.</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# Quick Live Clustering Preview
st.subheader("⚡ Live Model Preview")
cluster_model = RestaurantClusterModel(
    algorithm=model_settings["algorithm"],
    n_clusters=model_settings["n_clusters"],
    feature_cols=["cost"],
    scaler_type=model_settings["scaler"]
)
cluster_model.fit(df)
df_clustered = df.copy()
df_clustered["cluster"] = cluster_model.labels_

c1, c2 = st.columns(2)
with c1:
    st.plotly_chart(plot_cluster_cost_boxplots(df_clustered, cluster_col="cluster"), use_container_width=True)
with c2:
    st.plotly_chart(plot_cost_vs_rating(df_clustered, cluster_col="cluster"), use_container_width=True)

st.info("💡 **Dual Deployment Note:** This repository also includes a zero-config static web UI (`index.html`) pre-configured for instant **Vercel** deployment!")