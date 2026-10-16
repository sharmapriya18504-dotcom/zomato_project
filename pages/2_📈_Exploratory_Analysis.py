"""
Page 2: Exploratory Data Analysis (EDA)
In-depth statistical distributions, outlier analysis, correlation heatmaps, and data audits.
"""

import streamlit as st
import pandas as pd

from src.eda import compute_numerical_correlations, compute_top_cuisines, compute_locality_breakdown
from src.preprocessing import detect_outliers_iqr
from src.validation import audit_data_quality
from components.sidebar_filters import render_sidebar_controls
from components.charts import (
    plot_cost_distribution, plot_rating_distribution, 
    plot_top_cuisines_chart, plot_cost_vs_rating, plot_correlation_matrix
)

st.set_page_config(
    page_title="Exploratory Analysis | Zomato Intelligence",
    page_icon="📈",
    layout="wide"
)

df, model_settings = render_sidebar_controls()

st.title("📈 Exploratory Data Analysis")
st.markdown("""
Statistical inspection of restaurant pricing, customer sentiments, ratings, and culinary distribution.
""")

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Distributions & Outliers", 
    "🍲 Culinary Landscape", 
    "🔗 Correlations & Relationships", 
    "🔍 Data Quality Audit"
])

with tab1:
    st.subheader("Cost and Rating Distributions")
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(plot_cost_distribution(df), use_container_width=True)
    with c2:
        st.plotly_chart(plot_rating_distribution(df), use_container_width=True)
        
    st.subheader("Cost Outlier Diagnostics (IQR Method)")
    if "cost" in df.columns:
        is_outlier, lower_b, upper_b = detect_outliers_iqr(df["cost"])
        num_outliers = int(is_outlier.sum())
        
        st.write(
            f"• Statistical Upper Fence (Q3 + 1.5*IQR): **INR {upper_b:,.0f}**  \n"
            f"• Detected High-Cost Points: **{num_outliers} restaurants** ({(num_outliers / len(df) * 100):.1f}% of total listings)."
        )
        st.info(
            "📌 **Analytical Note on Outliers:** High pricing points are generally legitimate fine dining and luxury venues "
            "(e.g., Jonathan's Kitchen, 10 Downing Street, Barbeque Nation), rather than data entry corruptions. "
            "They represent genuine high-end dining clusters."
        )
        if num_outliers > 0:
            st.dataframe(df[is_outlier][["name", "cost", "avg_rating", "primary_cuisine", "locality"]], use_container_width=True)

with tab2:
    st.subheader("Culinary Diversity and Frequency")
    col_c1, col_c2 = st.columns([3, 2])
    with col_c1:
        top_cuisines = compute_top_cuisines(df, top_n=12)
        st.plotly_chart(plot_top_cuisines_chart(top_cuisines), use_container_width=True)
    with col_c2:
        st.markdown("#### Top Cuisines Table")
        st.dataframe(top_cuisines, use_container_width=True)

with tab3:
    st.subheader("Feature Correlation & Associations")
    corr_df = compute_numerical_correlations(df)
    if not corr_df.empty:
        st.plotly_chart(plot_correlation_matrix(corr_df), use_container_width=True)
    else:
        st.info("Not enough numerical features available to generate a correlation heatmap.")
        
    st.subheader("Dining Cost vs Customer Rating")
    st.plotly_chart(plot_cost_vs_rating(df), use_container_width=True)

with tab4:
    st.subheader("Dataset Quality Audit")
    audit = audit_data_quality(df)
    
    a1, a2, a3, a4 = st.columns(4)
    with a1:
        st.metric("Total Rows", f"{audit['total_rows']}")
    with a2:
        st.metric("Total Columns", f"{audit['total_columns']}")
    with a3:
        st.metric("Duplicate Rows", f"{audit['duplicate_rows']}")
    with a4:
        st.metric("Invalid Cost/Ratings", f"{audit['invalid_cost_count'] + audit['invalid_rating_count']}")
        
    st.markdown("#### Missing Values per Column")
    missing_df = pd.DataFrame(list(audit["missing_summary"].items()), columns=["Column", "Missing Count"])
    missing_df["Missing (%)"] = ((missing_df["Missing Count"] / len(df)) * 100).round(1)
    st.dataframe(missing_df, use_container_width=True)
