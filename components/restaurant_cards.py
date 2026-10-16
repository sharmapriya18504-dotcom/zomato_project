"""
Restaurant Card rendering component.
"""

from typing import Dict, List
import streamlit as st


def render_restaurant_card(row: Dict[str, any], cluster_color: str = "#E23744") -> None:
    """
    Render a restaurant listing card.
    """
    name = row.get("name", "Restaurant")
    cost = row.get("cost", 800)
    rating = row.get("avg_rating", row.get("rating", 4.0))
    votes = row.get("votes", 25)
    cuisines = row.get("cuisines", "Multi-Cuisine")
    locality = row.get("locality", "Central")
    link = row.get("links", "https://www.zomato.com")
    tier = row.get("price_tier", "Mid-Range")
    reason = row.get("recommendation_reason", "")
    score = row.get("match_score", None)
    
    score_badge_html = f"""
    <span style="background: rgba(226, 55, 68, 0.2); border: 1px solid #E23744; color: #FF5A66; padding: 3px 10px; border-radius: 999px; font-size: 0.75rem; font-weight: 700;">
        Match Score: {score}%
    </span>
    """ if score is not None else ""
    
    card_html = f"""
    <div style="
        background: rgba(21, 28, 44, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 12px;
        border-left: 4px solid {cluster_color};
    ">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
            <div>
                <h4 style="margin: 0; color: #F8FAFC; font-size: 1.15rem; font-weight: 700;">{name}</h4>
                <div style="font-size: 0.8rem; color: #94A3B8; margin-top: 2px;">📍 {locality} • {tier}</div>
            </div>
            <div>{score_badge_html}</div>
        </div>
        
        <div style="display: flex; align-items: center; gap: 14px; margin-bottom: 8px; flex-wrap: wrap;">
            <span style="font-size: 1.1rem; font-weight: 800; color: #FFFFFF;">INR {cost:,.0f} <small style='font-size: 0.75rem; color: #64748B; font-weight: 400;'>for two</small></span>
            <span style="background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.3); color: #10B981; padding: 2px 8px; border-radius: 6px; font-size: 0.82rem; font-weight: 700;">
                ★ {rating:.1f}
            </span>
            <span style="font-size: 0.8rem; color: #64748B;">{votes} reviews</span>
        </div>
        
        <div style="font-size: 0.82rem; color: #CBD5E1; margin-bottom: 8px;">
            🍽️ <strong>Cuisines:</strong> {cuisines}
        </div>
        
        {"<div style='font-size: 0.8rem; color: #F59E0B; margin-bottom: 8px;'>💡 <em>" + str(reason) + "</em></div>" if reason else ""}
        
        <div style="text-align: right;">
            <a href="{link}" target="_blank" style="color: #FF5A66; text-decoration: none; font-size: 0.85rem; font-weight: 600;">
                View on Zomato ↗
            </a>
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)
