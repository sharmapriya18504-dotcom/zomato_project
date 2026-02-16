import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

st.set_page_config(page_title="Zomato Clustering", layout="wide")

# =============================
# TITLE
# =============================
st.title("🍽️ Zomato Restaurant Cost Clustering")

# =============================
# INTRODUCTION
# =============================
st.header("📌 Project Introduction")
st.markdown("""
Zomato is one of India's leading restaurant discovery platforms.  
This project focuses on segmenting restaurants based on their cost 
using Machine Learning clustering techniques.
""")

# =============================
# PROBLEM STATEMENT
# =============================
st.header("🎯 Problem Statement")
st.markdown("""
- Segment restaurants into pricing categories  
- Identify Budget, Mid-Range, and Premium restaurants  
- Help improve recommendation systems  
- Provide business insights for marketing strategies  
""")

# =============================
# LOAD DATA
# =============================
@st.cache_data
def load_data():
    df = pd.read_csv("Zomato Restaurant names and Metadata.csv")
    return df

df = load_data()

# =============================
# DATA CLEANING
# =============================
df['Cost'] = df['Cost'].astype(str)
df['Cost'] = df['Cost'].str.replace(',', '')
df['Cost'] = pd.to_numeric(df['Cost'], errors='coerce')
df = df.dropna(subset=['Cost'])

# =============================
# RAW DATA
# =============================
st.header("📊 Raw Data Preview")
st.dataframe(df.head())

# =============================
# ELBOW METHOD
# =============================
st.header("📉 Elbow Method")

features = df[['Cost']]
scaler = StandardScaler()
scaled = scaler.fit_transform(features)

inertia = []
K_range = range(2, 8)

for k in K_range:
    model = KMeans(n_clusters=k, random_state=42)
    model.fit(scaled)
    inertia.append(model.inertia_)

fig1, ax1 = plt.subplots()
ax1.plot(K_range, inertia, marker='o')
ax1.set_xlabel("Number of Clusters")
ax1.set_ylabel("Inertia")
ax1.set_title("Elbow Method")
st.pyplot(fig1)

# =============================
# CLUSTERING
# =============================
st.header("🔍 K-Means Clustering")

k = st.slider("Select number of clusters", 2, 6, 3)

kmeans = KMeans(n_clusters=k, random_state=42)
df['Cluster'] = kmeans.fit_predict(scaled)

# Silhouette Score
score = silhouette_score(scaled, df['Cluster'])
st.write("✅ Silhouette Score:", round(score, 3))

# =============================
# CLUSTER VISUALIZATION
# =============================
st.header("📈 Cluster Visualization")

fig2, ax2 = plt.subplots()
sns.boxplot(x='Cluster', y='Cost', data=df, ax=ax2)
st.pyplot(fig2)

# =============================
# CLUSTER SUMMARY
# =============================
st.header("📋 Cluster Summary")

summary = df.groupby('Cluster')['Cost'].agg(['mean', 'min', 'max', 'count'])
st.dataframe(summary)

# =============================
# CONCLUSION
# =============================
st.header("📊 Conclusion")

st.markdown(f"""
The clustering model successfully segmented restaurants into **{k} pricing groups**.

Silhouette Score of **{round(score,3)}** indicates good cluster separation.

Key Insights:
- Restaurants are grouped based on pricing patterns.
- Budget restaurants form a significant portion.
- Premium restaurants represent high-end dining.
- This segmentation can help Zomato in targeted marketing and recommendations.
""")

# =============================
# ABOUT ME
# =============================
st.header("👩‍💻 About Me")

st.markdown("""
Hi, I am **Priya Sharma**, a B.Tech student passionate about Data Science and Machine Learning.

This project demonstrates my ability to:

- Perform Data Cleaning and EDA  
- Apply Machine Learning (K-Means Clustering)  
- Evaluate models using Silhouette Score  
- Deploy ML applications using Streamlit  

I am continuously building real-world projects to strengthen my analytical skills.
""")

st.success("🚀 Project Successfully Deployed Using Streamlit!")