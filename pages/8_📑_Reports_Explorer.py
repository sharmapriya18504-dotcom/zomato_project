"""
Page 8: Reports Explorer & Data Exports
Download executive analytical PDF reports and custom filtered CSV records.
"""

import streamlit as st
import pandas as pd

from src.eda import compute_overview_kpis, generate_automated_insights
from src.clustering import RestaurantClusterModel, generate_cluster_profiles
from src.reporting import generate_pdf_report, export_dataframe_to_csv
from components.sidebar_filters import render_sidebar_controls

st.set_page_config(
    page_title="Reports & Exports | Zomato Intelligence",
    page_icon="📑",
    layout="wide"
)

df, model_settings = render_sidebar_controls()

st.title("📑 Reports Explorer & Data Export Hub")
st.markdown("""
Export full analytical datasets, filtered records, and generate executive PDF summaries.
""")

kpis = compute_overview_kpis(df)
insights = generate_automated_insights(df)

# Fit model to get current profiles
cluster_model = RestaurantClusterModel(
    algorithm=model_settings["algorithm"],
    n_clusters=model_settings["n_clusters"],
    feature_cols=["cost"],
    scaler_type=model_settings["scaler"]
)
cluster_model.fit(df)
df_clustered = df.copy()
df_clustered["cluster"] = cluster_model.labels_
profiles_df = generate_cluster_profiles(df_clustered, cluster_col="cluster")

st.subheader("📄 Automated PDF Executive Report")
st.markdown("Download a formatted executive PDF report containing project KPIs, model configurations, cluster profiles, and strategic findings.")

model_meta = {
    "Algorithm": model_settings["algorithm_name"],
    "Clusters_K": model_settings["n_clusters"],
    "Scaler": model_settings["scaler_name"],
    "Total_Records": len(df)
}

pdf_bytes = generate_pdf_report(
    summary_kpis=kpis,
    cluster_profiles=profiles_df,
    model_metadata=model_meta,
    insights=insights
)

st.download_button(
    label="📥 Download Executive PDF Report",
    data=pdf_bytes,
    file_name="Zomato_Intelligence_Report.pdf",
    mime="application/pdf"
)

st.divider()

st.subheader("💾 Raw & Processed Dataset Exports (CSV)")

c1, c2 = st.columns(2)
with c1:
    st.markdown("#### Complete Enriched Dataset")
    st.caption("Contains full metadata, aggregated review stats, locality tags, and pricing tiers.")
    csv_enriched = export_dataframe_to_csv(df)
    st.download_button(
        label="📥 Download Enriched Dataset (CSV)",
        data=csv_enriched,
        file_name="zomato_enriched_master.csv",
        mime="text/csv"
    )

with c2:
    st.markdown("#### Clustered Restaurant Records")
    st.caption("Contains fitted cluster IDs and segment names for the current model configuration.")
    csv_clustered = export_dataframe_to_csv(df_clustered)
    st.download_button(
        label="📥 Download Clustered Records (CSV)",
        data=csv_clustered,
        file_name=f"zomato_clustered_k{model_settings['n_clusters']}.csv",
        mime="text/csv"
    )

st.divider()

st.subheader("📋 In-Dashboard Report Summary Preview")
st.json({
    "Project": "Zomato Restaurant Intelligence Platform",
    "Author": "Priya Sharma",
    "Dataset_KPIs": kpis,
    "Model_Metadata": model_meta,
    "Cluster_Summary": profiles_df.to_dict(orient="records")
})
