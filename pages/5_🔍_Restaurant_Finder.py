"""
Page 5: Smart Restaurant Finder & Recommendations
Constraint filtering, transparent composite scoring, and recommendation explanations.
"""

import streamlit as st
import pandas as pd

from src.recommendations import filter_restaurants, compute_recommendation_score
from src.reporting import export_dataframe_to_csv
from components.sidebar_filters import render_sidebar_controls
from components.restaurant_cards import render_restaurant_card

st.set_page_config(
    page_title="Restaurant Finder | Zomato Intelligence",
    page_icon="🔍",
    layout="wide"
)

df, model_settings = render_sidebar_controls()

st.title("🔍 Smart Restaurant Recommendation Engine")
st.markdown("""
Discover restaurants tailored to your budget, desired rating, culinary taste, and location.
""")

# User Controls
c1, c2, c3, c4 = st.columns(4)

with c1:
    max_cost_val = float(df["cost"].max()) if "cost" in df.columns else 2000.0
    budget = st.slider("Maximum Budget for Two (INR):", 150, int(max_cost_val), int(min(1200, max_cost_val)), step=50)
with c2:
    min_rating = st.slider("Minimum Customer Rating:", 1.0, 5.0, 3.8, step=0.1)
with c3:
    # Get unique cuisines
    cuisines_opts = ["ALL"]
    if "cuisines_list" in df.columns:
        all_c = set()
        for cl in df["cuisines_list"].dropna():
            if isinstance(cl, list):
                all_c.update(cl)
        cuisines_opts.extend(sorted(list(all_c)))
    pref_cuisine = st.selectbox("Preferred Cuisine:", cuisines_opts)
with c4:
    localities_opts = ["ALL"]
    if "locality" in df.columns:
        localities_opts.extend(sorted(df["locality"].dropna().unique().tolist()))
    pref_locality = st.selectbox("Locality / Zone:", localities_opts)

# Filter & Rank
filtered_df, was_relaxed = filter_restaurants(
    df,
    max_cost=budget,
    min_rating=min_rating,
    preferred_cuisine=pref_cuisine,
    locality=pref_locality
)

if was_relaxed:
    st.warning("⚠️ No exact matches found for your strict criteria. Showing relaxed recommendations with extended budget / flexible ratings.")

if filtered_df.empty:
    st.error("No restaurants match even with relaxed filters. Please broaden your selections.")
else:
    ranked_df = compute_recommendation_score(filtered_df, max_budget=budget, preferred_cuisine=pref_cuisine)
    
    st.subheader(f"✨ Top Recommended Restaurants ({len(ranked_df)} matches)")
    
    # Download Button
    csv_data = export_dataframe_to_csv(ranked_df)
    st.download_button(
        label="📥 Download Recommendations (CSV)",
        data=csv_data,
        file_name="recommended_restaurants.csv",
        mime="text/csv"
    )
    
    # Render cards
    for _, row in ranked_df.head(15).iterrows():
        render_restaurant_card(row.to_dict())
