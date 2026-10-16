import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

# =============================
# PAGE CONFIGURATION
# =============================
st.set_page_config(
    page_title="Zomato Restaurant Clustering | Priya Sharma",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Dark Glassmorphism Theme)
st.markdown("""
<style>
    .main {
        background-color: #0b0e14;
        color: #f8fafc;
    }
    .stMetric {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 14px 18px;
        border-radius: 12px;
    }
    h1, h2, h3 {
        color: #ffffff;
        font-weight: 700;
    }
    .badge-primary {
        background: linear-gradient(135deg, #e23744 0%, #ff5260 100%);
        color: white;
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 0.85rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# =============================
# SIDEBAR
# =============================
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/b/bd/Zomato_Logo.svg", width=180)
    st.markdown("### 📊 Project Intelligence")
    st.markdown("**Author:** Priya Sharma")
    st.markdown("**Role:** B.Tech Student | Aspiring Data Scientist")
    st.divider()
    
    st.markdown("### ⚙️ Clustering Parameters")
    k = st.slider("Select Number of Clusters (K):", min_value=2, max_value=6, value=3, step=1)
    
    st.divider()
    st.markdown("🌐 **Web UI Deployment:**")
    st.info("Check out the standalone interactive web UI deployed on Vercel at root (`index.html`)!")

# =============================
# HEADER & HERO
# =============================
st.title("🍽️ Zomato Restaurant Cost Clustering & Analytics")
st.markdown("""
Segmenting restaurants into intelligent pricing tiers (**Budget, Mid-Range, Premium**) 
using Machine Learning (K-Means Clustering) and Exploratory Data Analysis.
""")

# =============================
# LOAD & CLEAN DATA
# =============================
@st.cache_data
def load_data():
    df_raw = pd.read_csv("Zomato Restaurant names and Metadata.csv")
    df_raw['Cost'] = df_raw['Cost'].astype(str).str.replace(',', '').str.strip()
    df_raw['Cost'] = pd.to_numeric(df_raw['Cost'], errors='coerce')
    df_raw = df_raw.dropna(subset=['Cost'])
    return df_raw

df = load_data()

# KPI Metric Cards
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Restaurants", f"{len(df)}")
with col2:
    st.metric("Average Cost", f"₹{round(df['Cost'].mean(), 0):,.0f}")
with col3:
    st.metric("Min - Max Cost", f"₹{int(df['Cost'].min())} - ₹{int(df['Cost'].max())}")
with col4:
    st.metric("Optimal Clusters", "K = 3")

st.divider()

# =============================
# TABS INTERFACE
# =============================
tab1, tab2, tab3, tab4 = st.tabs([
    "🤖 K-Means Clustering", 
    "📉 Elbow Method & Silhouette", 
    "📊 Raw Data & Exploration", 
    "👩‍💻 About Priya Sharma"
])

# Scale Features
features = df[['Cost']]
scaler = StandardScaler()
scaled = scaler.fit_transform(features)

kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
df['Cluster'] = kmeans.fit_predict(scaled)
score = silhouette_score(scaled, df['Cluster'])

# TAB 1: Clustering
with tab1:
    st.subheader(f"🔍 Cluster Segmentation (K = {k})")
    st.write(f"Evaluating K-Means with **Silhouette Score:** `{round(score, 3)}`")
    
    fig2, ax2 = plt.subplots(figsize=(8, 4))
    sns.set_theme(style="darkgrid")
    sns.boxplot(x='Cluster', y='Cost', data=df, palette='Set2', ax=ax2)
    ax2.set_title("Cost Distribution across Clusters", fontsize=12)
    ax2.set_ylabel("Cost for Two (₹)")
    ax2.set_xlabel("Assigned Cluster")
    st.pyplot(fig2)
    
    st.subheader("📋 Cluster Breakdown Summary")
    summary = df.groupby('Cluster')['Cost'].agg(
        Count='count',
        Mean='mean',
        Min='min',
        Max='max'
    ).reset_index()
    summary['Mean'] = summary['Mean'].round(1)
    st.dataframe(summary, use_container_width=True)

# TAB 2: Elbow Method & Evaluation
with tab2:
    st.subheader("📉 Elbow Method for Optimal K")
    st.markdown("The elbow method helps determine the optimal number of clusters by finding the inflection point where inertia decreases sharply.")
    
    inertia = []
    K_range = range(2, 8)
    for num_k in K_range:
        model = KMeans(n_clusters=num_k, random_state=42, n_init=10)
        model.fit(scaled)
        inertia.append(model.inertia_)
    
    fig1, ax1 = plt.subplots(figsize=(8, 4))
    ax1.plot(K_range, inertia, marker='o', color='#e23744', linewidth=2.5, markersize=7)
    ax1.axvline(x=3, color='#3b82f6', linestyle='--', label='Elbow Point (K=3)')
    ax1.set_xlabel("Number of Clusters (K)")
    ax1.set_ylabel("Inertia (Within-Cluster Sum of Squares)")
    ax1.set_title("Elbow Method Analysis")
    ax1.legend()
    st.pyplot(fig1)

# TAB 3: Raw Data Exploration
with tab3:
    st.subheader("📊 Dataset Preview")
    search_term = st.text_input("Filter restaurant by name:", "")
    if search_term:
        filtered_df = df[df['Name'].str.contains(search_term, case=False, na=False)]
    else:
        filtered_df = df
    st.dataframe(filtered_df, use_container_width=True)

# TAB 4: About Author
with tab4:
    st.subheader("👩‍💻 About the Author")
    st.markdown("""
    Hi, I am **Priya Sharma**, a B.Tech student passionate about Data Science and Machine Learning.
    
    **Project Highlights:**
    - Performed Data Cleaning, Feature Engineering & Scaling
    - Unsupervised K-Means clustering with Scikit-Learn
    - Evaluated clustering performance using Silhouette Scores & Elbow method
    - Built dual deployment: interactive web application for Vercel & Streamlit dashboard
    
    **Tech Stack:** Python, Pandas, Scikit-Learn, Streamlit, HTML5/CSS3, Vercel
    """)
    st.success("🚀 Ready for GitHub push and instant Vercel deployment!")