"""
Page 4: Location & Market Geography
Spatial concentration, locality dining costs, and area-wise segment breakdowns.
"""

import streamlit as st
import pandas as pd
import plotly.express as px

from src.location_analysis import analyze_market_density, analyze_locality_price_tiers
from components.sidebar_filters import render_sidebar_controls

st.set_page_config(
    page_title="Location Intelligence | Zomato Intelligence",
    page_icon="🗺️",
    layout="wide"
)

df, model_settings = render_sidebar_controls()

st.title("🗺️ Location & Market Geography")
st.markdown("""
Locality-level density, market share, and comparative pricing patterns across tracked zones.
""")

density_df = analyze_market_density(df)

if density_df.empty:
    st.info("No locality or location columns found in current dataset.")
    st.stop()

# Locality metrics
l1, l2, l3 = st.columns(3)
with l1:
    top_loc = density_df.iloc[0]["locality"]
    top_count = density_df.iloc[0]["restaurant_count"]
    st.metric("Primary Hub", f"{top_loc}", f"{top_count} restaurants listed")
with l2:
    if "avg_cost" in density_df.columns:
        priciest_loc = density_df.sort_values(by="avg_cost", ascending=False).iloc[0]
        st.metric("Priciest Locality", f"{priciest_loc['locality']}", f"Avg INR {priciest_loc['avg_cost']:,.0f}")
with l3:
    if "avg_rating" in density_df.columns:
        highest_rated = density_df.sort_values(by="avg_rating", ascending=False).iloc[0]
        st.metric("Highest Rated Zone", f"{highest_rated['locality']}", f"Avg {highest_rated['avg_rating']:.2f}★")

st.divider()

# Charts
c1, c2 = st.columns(2)
with c1:
    fig_count = px.bar(
        density_df,
        x="locality",
        y="restaurant_count",
        title="Restaurant Density by Locality",
        labels={"locality": "Locality", "restaurant_count": "Restaurant Count"},
        color="restaurant_count",
        color_continuous_scale="Reds",
        template="plotly_dark"
    )
    fig_count.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(21, 28, 44, 0.4)", coloraxis_showscale=False)
    st.plotly_chart(fig_count, use_container_width=True)

with c2:
    if "avg_cost" in density_df.columns:
        fig_cost = px.bar(
            density_df,
            x="locality",
            y="avg_cost",
            title="Average Dining Cost for Two by Locality",
            labels={"locality": "Locality", "avg_cost": "Average Cost (INR)"},
            color="avg_cost",
            color_continuous_scale="Blues",
            template="plotly_dark"
        )
        fig_cost.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(21, 28, 44, 0.4)", coloraxis_showscale=False)
        st.plotly_chart(fig_cost, use_container_width=True)

st.divider()

# Locality Table
st.subheader("📋 Locality Comparative Summary")
st.dataframe(density_df, use_container_width=True)

# Price Tier Proportions by Area
tier_breakdown = analyze_locality_price_tiers(df)
if not tier_breakdown.empty:
    st.subheader("📊 Price Tier Mix across Localities (%)")
    st.dataframe(tier_breakdown, use_container_width=True)
