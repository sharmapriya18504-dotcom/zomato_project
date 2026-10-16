"""
KPI Metric cards component for Streamlit dashboard.
"""

from typing import Optional
import streamlit as st


def render_kpi_card(
    title: str, 
    value: str, 
    subtext: Optional[str] = None, 
    border_color: str = "#E23744",
    icon: str = "📊"
) -> None:
    """
    Render a clean glassmorphism KPI card.
    """
    card_html = f"""
    <div style="
        background: rgba(21, 28, 44, 0.75);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-top: 3px solid {border_color};
        border-radius: 12px;
        padding: 18px 20px;
        margin-bottom: 14px;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25);
    ">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
            <span style="font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.5px; color: #94A3B8; font-weight: 600;">{title}</span>
            <span style="font-size: 1.1rem;">{icon}</span>
        </div>
        <div style="font-size: 1.85rem; font-weight: 800; color: #F8FAFC; letter-spacing: -0.5px;">{value}</div>
        {"<div style='font-size: 0.78rem; color: #64748B; margin-top: 4px;'>" + subtext + "</div>" if subtext else ""}
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)
