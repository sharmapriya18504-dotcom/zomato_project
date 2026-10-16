"""
Interactive Plotly charts component for Streamlit dashboard.
"""

from typing import List, Optional
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from src.config import CLUSTER_COLORS


def plot_cost_distribution(df: pd.DataFrame) -> go.Figure:
    """
    Plot restaurant cost for two distribution with box margin.
    """
    if df.empty or "cost" not in df.columns:
        return go.Figure()
        
    fig = px.histogram(
        df,
        x="cost",
        nbins=25,
        marginal="box",
        title="Dining Cost for Two Distribution (INR)",
        labels={"cost": "Cost for Two (INR)"},
        color_discrete_sequence=["#E23744"],
        template="plotly_dark"
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(21, 28, 44, 0.4)",
        font=dict(family="Plus Jakarta Sans, sans-serif", color="#CBD5E1"),
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig


def plot_rating_distribution(df: pd.DataFrame) -> go.Figure:
    """
    Plot restaurant ratings distribution.
    """
    rating_col = "avg_rating" if "avg_rating" in df.columns else ("rating" if "rating" in df.columns else None)
    if df.empty or not rating_col:
        return go.Figure()
        
    fig = px.histogram(
        df,
        x=rating_col,
        nbins=15,
        title="Customer Rating Distribution (1.0 to 5.0)",
        labels={rating_col: "Average Rating"},
        color_discrete_sequence=["#F59E0B"],
        template="plotly_dark"
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(21, 28, 44, 0.4)",
        font=dict(family="Plus Jakarta Sans, sans-serif", color="#CBD5E1"),
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig


def plot_top_cuisines_chart(top_cuisines_df: pd.DataFrame) -> go.Figure:
    """
    Horizontal bar chart for most popular cuisines.
    """
    if top_cuisines_df.empty:
        return go.Figure()
        
    fig = px.bar(
        top_cuisines_df.sort_values(by="count", ascending=True),
        x="count",
        y="cuisine",
        orientation="h",
        title="Top 10 Most Common Cuisines",
        labels={"count": "Number of Restaurants", "cuisine": "Cuisine"},
        color="count",
        color_continuous_scale=["#3B82F6", "#E23744"],
        template="plotly_dark"
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(21, 28, 44, 0.4)",
        font=dict(family="Plus Jakarta Sans, sans-serif", color="#CBD5E1"),
        margin=dict(l=20, r=20, t=50, b=20),
        coloraxis_showscale=False
    )
    return fig


def plot_cost_vs_rating(df: pd.DataFrame, cluster_col: Optional[str] = None) -> go.Figure:
    """
    Interactive scatter plot of Cost for Two vs Customer Rating with hover details.
    """
    if df.empty or "cost" not in df.columns:
        return go.Figure()
        
    rating_col = "avg_rating" if "avg_rating" in df.columns else "rating"
    color_arg = cluster_col if cluster_col and cluster_col in df.columns else None
    
    hover_cols = ["primary_cuisine", "locality", "votes"] if "primary_cuisine" in df.columns else ["name"]
    
    fig = px.scatter(
        df,
        x="cost",
        y=rating_col,
        color=color_arg,
        hover_name="name",
        hover_data=hover_cols,
        title="Dining Cost vs Customer Rating",
        labels={"cost": "Cost for Two (INR)", rating_col: "Rating (1-5)"},
        color_discrete_sequence=CLUSTER_COLORS,
        template="plotly_dark"
    )
    fig.update_traces(marker=dict(size=9, opacity=0.85, line=dict(width=1, color="white")))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(21, 28, 44, 0.4)",
        font=dict(family="Plus Jakarta Sans, sans-serif", color="#CBD5E1"),
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig


def plot_elbow_curve_chart(elbow_df: pd.DataFrame, selected_k: int = 3) -> go.Figure:
    """
    Line chart showing the Elbow curve (Inertia vs K) and Silhouette scores.
    """
    if elbow_df.empty:
        return go.Figure()
        
    fig = go.Figure()
    
    # Inertia line
    fig.add_trace(go.Scatter(
        x=elbow_df["k"],
        y=elbow_df["inertia"],
        mode="lines+markers",
        name="Inertia (Within-Cluster Sum of Squares)",
        line=dict(color="#E23744", width=3),
        marker=dict(size=8)
    ))
    
    # Highlight selected K
    sel_point = elbow_df[elbow_df["k"] == selected_k]
    if not sel_point.empty:
        fig.add_trace(go.Scatter(
            x=sel_point["k"],
            y=sel_point["inertia"],
            mode="markers",
            name=f"Selected K={selected_k}",
            marker=dict(color="#FFD700", size=14, symbol="star")
        ))
        
    fig.update_layout(
        title="Elbow Method Curve (Inertia vs Number of Clusters)",
        xaxis=dict(title="Number of Clusters (K)", tickmode="linear", gridcolor="rgba(255,255,255,0.06)"),
        yaxis=dict(title="Inertia (Error)", gridcolor="rgba(255,255,255,0.06)"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(21, 28, 44, 0.4)",
        font=dict(family="Plus Jakarta Sans, sans-serif", color="#CBD5E1"),
        template="plotly_dark",
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig


def plot_cluster_cost_boxplots(df: pd.DataFrame, cluster_col: str = "cluster") -> go.Figure:
    """
    Boxplot showing cost distribution separated across clusters.
    """
    if df.empty or cluster_col not in df.columns or "cost" not in df.columns:
        return go.Figure()
        
    fig = px.box(
        df,
        x=cluster_col,
        y="cost",
        color=cluster_col,
        title="Cost Distribution by Cluster Segment",
        labels={cluster_col: "Cluster ID", "cost": "Cost for Two (INR)"},
        color_discrete_sequence=CLUSTER_COLORS,
        template="plotly_dark"
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(21, 28, 44, 0.4)",
        font=dict(family="Plus Jakarta Sans, sans-serif", color="#CBD5E1"),
        margin=dict(l=20, r=20, t=50, b=20),
        showlegend=False
    )
    return fig


def plot_correlation_matrix(corr_df: pd.DataFrame) -> go.Figure:
    """
    Annotated heatmap of numerical correlations.
    """
    if corr_df.empty:
        return go.Figure()
        
    fig = px.imshow(
        corr_df,
        text_auto=True,
        aspect="auto",
        title="Numerical Features Correlation Heatmap",
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        template="plotly_dark"
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(21, 28, 44, 0.4)",
        font=dict(family="Plus Jakarta Sans, sans-serif", color="#CBD5E1"),
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig
