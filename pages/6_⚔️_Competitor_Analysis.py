"""
Page 6: Competitor & Peer Analysis
Compare individual restaurants against neighborhood and category peers.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from components.sidebar_filters import render_sidebar_controls

st.set_page_config(
    page_title="Competitor Analysis | Zomato Intelligence",
    page_icon="⚔️",
    layout="wide"
)

df, model_settings = render_sidebar_controls()

st.title("⚔️ Competitor & Market Peer Analysis")
st.markdown("""
Benchmarking individual restaurants against local peers in the same cuisine and pricing tier.
""")

if df.empty or "name" not in df.columns:
    st.info("No restaurant records available for competitor comparison.")
    st.stop()

# Restaurant Selector
restaurant_names = sorted(df["name"].dropna().unique().tolist())
target_name = st.selectbox("Select Restaurant to Analyze:", restaurant_names, index=0)

target_row = df[df["name"] == target_name].iloc[0]

# Identify Peers: same locality or same price tier
locality_val = target_row.get("locality", "Central")
tier_val = target_row.get("price_tier", "Mid-Range")

peers = df[(df["locality"] == locality_val) & (df["name"] != target_name)]
if peers.empty:
    peers = df[(df["price_tier"] == tier_val) & (df["name"] != target_name)]
    peer_group_name = f"Price Tier ({tier_val})"
else:
    peer_group_name = f"Neighborhood ({locality_val})"

st.subheader(f"📍 Benchmarking: {target_name} vs {len(peers)} Peers in {peer_group_name}")

# Metrics Delta
t_cost = float(target_row.get("cost", 800))
p_avg_cost = float(peers["cost"].mean()) if not peers.empty else t_cost
cost_delta = t_cost - p_avg_cost

t_rating = float(target_row.get("avg_rating", 4.0))
p_avg_rating = float(peers["avg_rating"].mean()) if not peers.empty else t_rating
rating_delta = t_rating - p_avg_rating

t_votes = int(target_row.get("votes", 25))
p_med_votes = int(peers["votes"].median()) if not peers.empty else t_votes
votes_delta = t_votes - p_med_votes

c1, c2, c3 = st.columns(3)
with c1:
    st.metric(
        "Cost for Two",
        f"INR {t_cost:,.0f}",
        f"{cost_delta:+,.0f} vs Peer Avg (INR {p_avg_cost:,.0f})",
        delta_color="inverse"
    )
with c2:
    st.metric(
        "Customer Rating",
        f"{t_rating:.2f}★",
        f"{rating_delta:+.2f}★ vs Peer Avg ({p_avg_rating:.2f}★)"
    )
with c3:
    st.metric(
        "Review Engagement",
        f"{t_votes} reviews",
        f"{votes_delta:+d} vs Peer Median ({p_med_votes})"
    )

st.divider()

# Comparative Chart
st.subheader("📊 Relative Performance Comparison")
categories = ["Cost for Two (INR)", "Rating (x100)", "Votes / Reviews"]
target_values = [t_cost, t_rating * 100, t_votes]
peer_values = [p_avg_cost, p_avg_rating * 100, p_med_votes]

fig = go.Figure(data=[
    go.Bar(name=target_name, x=categories, y=target_values, marker_color="#E23744"),
    go.Bar(name=f"Peer Average / Median", x=categories, y=peer_values, marker_color="#3B82F6")
])
fig.update_layout(
    barmode="group",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(21, 28, 44, 0.4)",
    font=dict(family="Plus Jakarta Sans, sans-serif", color="#CBD5E1"),
    template="plotly_dark",
    margin=dict(l=20, r=20, t=40, b=20)
)
st.plotly_chart(fig, use_container_width=True)

# Peer Table
st.subheader(f"👥 Top Competitor Listings in {peer_group_name}")
display_cols = [c for c in ["name", "cost", "avg_rating", "votes", "primary_cuisine"] if c in peers.columns]
st.dataframe(peers[display_cols].sort_values(by="avg_rating", ascending=False).head(10), use_container_width=True)
