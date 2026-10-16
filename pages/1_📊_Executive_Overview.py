"""
Page 1: Executive Overview Dashboard
High-level market overview, responsive KPI cards, core distributions, and automated insights.
"""

import streamlit as st
import pandas as pd

from src.eda import compute_overview_kpis, compute_top_cuisines, compute_locality_breakdown, generate_automated_insights
from components.sidebar_filters import render_sidebar_controls
from components.kpi_cards import render_kpi_card
from components.charts import (
    plot_cost_distribution, plot_rating_distribution, 
    plot_top_cuisines_chart, plot_cost_vs_rating
)

st.set_page_config(
    page_title="Executive Overview | Zomato Intelligence",
    page_icon="📊",
    layout="wide"
)

# Render Sidebar
df, model_settings = render_sidebar_controls()

# Header
st.title("📊 Executive Overview Dashboard")
st.markdown("""
High-level restaurant intelligence, market aggregates, and pricing benchmarks across Hyderabad.
""")

# Compute KPIs
kpis = compute_overview_kpis(df)

# Render KPI Cards in Columns
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    render_kpi_card("Total Restaurants", f"{kpis['total_restaurants']}", "Active listings in dataset", "#E23744", "🍽️")
with col2:
    render_kpi_card("Avg Dining Cost", f"INR {kpis['avg_cost']:,.0f}", f"Median: INR {kpis['median_cost']:,.0f}", "#3B82F6", "💵")
with col3:
    render_kpi_card("Avg Customer Rating", f"{kpis['avg_rating']:.2f} / 5.0", "Based on 10k reviews", "#10B981", "⭐")
with col4:
    render_kpi_card("Cuisine Diversity", f"{kpis['total_cuisines']}", "Distinct culinary styles", "#F59E0B", "🍲")
with col5:
    render_kpi_card("Market Zones", f"{kpis['total_localities']}", "Tracked localities", "#8B5CF6", "📍")

st.divider()

# Charts Section (2 Columns)
c1, c2 = st.columns(2)
with c1:
    st.plotly_chart(plot_cost_distribution(df), use_container_width=True)
with c2:
    st.plotly_chart(plot_rating_distribution(df), use_container_width=True)

c3, c4 = st.columns(2)
with c3:
    top_c_df = compute_top_cuisines(df, top_n=10)
    st.plotly_chart(plot_top_cuisines_chart(top_c_df), use_container_width=True)
with c4:
    st.plotly_chart(plot_cost_vs_rating(df), use_container_width=True)

st.divider()

# Automated Insights Section
st.subheader("💡 Automated Data-Driven Findings")
insights = generate_automated_insights(df)
for item in insights:
    st.info(item)

st.divider()

# Dataset Preview
with st.expander("📋 Inspect Cleaned Dataset Sample (First 15 Rows)"):
    display_cols = [c for c in ["name", "cost", "avg_rating", "votes", "primary_cuisine", "locality", "price_tier"] if c in df.columns]
    st.dataframe(df[display_cols].head(15), use_container_width=True)
