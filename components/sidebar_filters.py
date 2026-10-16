"""
Sidebar filters and dataset loading controls component.
"""

from typing import Dict, Tuple
import streamlit as st
import pandas as pd

from src.data_loader import load_raw_data, create_demo_dataset, read_csv_safe
from src.feature_engineering import build_enriched_dataset
from src.validation import map_columns, validate_dataset
from src.config import DEFAULT_K_CLUSTERS, MIN_K_CLUSTERS, MAX_K_CLUSTERS


def render_sidebar_controls() -> Tuple[pd.DataFrame, Dict[str, any]]:
    """
    Render standard sidebar controls:
    - Dataset source picker (Default / Upload / Demo)
    - File upload handling with validation
    - Clustering parameter sliders
    
    Returns:
        df: Enriched master DataFrame
        model_settings: Dict containing user-selected ML settings
    """
    with st.sidebar:
        st.markdown(
            """
            <div style="text-align: center; margin-bottom: 16px;">
                <h2 style="color: #E23744; margin: 0; font-weight: 800; letter-spacing: -1px;">
                    Zomato Intelligence
                </h2>
                <div style="font-size: 0.8rem; color: #94A3B8;">Market Analytics & ML Clustering</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        st.divider()
        st.markdown("### 📂 Dataset Source")
        
        data_source = st.radio(
            "Select Data Origin:",
            ["Default Zomato Hyderabad Dataset", "Upload Custom CSV", "Demo Dataset (12 Places)"],
            index=0
        )
        
        df = pd.DataFrame()
        
        if data_source == "Default Zomato Hyderabad Dataset":
            df_meta, df_rev = load_raw_data()
            if not df_meta.empty:
                df = build_enriched_dataset(df_meta, df_rev, save_to_disk=False)
                st.success(f"Loaded {len(df)} restaurants & 10k reviews.")
            else:
                st.warning("Default dataset not found. Switching to demo data.")
                df = create_demo_dataset()
                
        elif data_source == "Upload Custom CSV":
            uploaded_file = st.file_uploader(
                "Upload Restaurant CSV:",
                type=["csv"],
                help="CSV should have restaurant names and cost for two."
            )
            if uploaded_file is not None:
                try:
                    raw_df = read_csv_safe(uploaded_file)
                    renamed_df, mapping = map_columns(raw_df)
                    is_valid, msgs = validate_dataset(renamed_df, required_fields=["name", "cost"])
                    
                    if is_valid:
                        df = build_enriched_dataset(renamed_df, None, save_to_disk=False)
                        st.success(f"Custom CSV loaded ({len(df)} rows).")
                    else:
                        st.error(f"Invalid dataset: {msgs[0]}")
                        df = create_demo_dataset()
                except Exception as e:
                    st.error(f"Error parsing uploaded file: {e}")
                    df = create_demo_dataset()
            else:
                st.info("Awaiting file upload. Displaying demo dataset in the meantime.")
                df = create_demo_dataset()
                
        else:
            df = create_demo_dataset()
            st.info("Using built-in synthetic demo dataset.")
            
        st.divider()
        st.markdown("### 🤖 Clustering Parameters")
        
        algorithm = st.selectbox(
            "Algorithm:",
            ["K-Means", "Agglomerative (Ward)", "Agglomerative (Average)"],
            index=0
        )
        
        n_clusters = st.slider(
            "Number of Clusters (K):",
            min_value=MIN_K_CLUSTERS,
            max_value=min(MAX_K_CLUSTERS, len(df) - 1 if len(df) > 2 else 3),
            value=DEFAULT_K_CLUSTERS,
            step=1
        )
        
        scaler_choice = st.selectbox(
            "Feature Scaling:",
            ["StandardScaler", "RobustScaler", "MinMaxScaler"],
            index=0
        )
        
        # Map algorithm string
        algo_code = "kmeans"
        linkage_code = "ward"
        if "Agglomerative" in algorithm:
            algo_code = "agglomerative"
            linkage_code = "average" if "Average" in algorithm else "ward"
            
        scaler_code = "standard"
        if scaler_choice == "RobustScaler":
            scaler_code = "robust"
        elif scaler_choice == "MinMaxScaler":
            scaler_code = "minmax"
            
        model_settings = {
            "algorithm": algo_code,
            "linkage": linkage_code,
            "n_clusters": n_clusters,
            "scaler": scaler_code,
            "scaler_name": scaler_choice,
            "algorithm_name": algorithm
        }
        
        st.divider()
        st.markdown(
            """
            <div style="font-size: 0.75rem; color: #64748B; text-align: center;">
                Developed by <strong>Priya Sharma</strong><br>
                B.Tech Student & ML Engineer
            </div>
            """, 
            unsafe_allow_html=True
        )
        
    return df, model_settings
