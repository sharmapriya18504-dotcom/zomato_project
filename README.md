# 🍽️ Zomato Restaurant Cost Clustering & Market Intelligence Platform

[![Vercel Deployment](https://img.shields.io/badge/Deploy-Vercel-black?style=for-the-badge&logo=vercel)](https://vercel.com)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org)
[![JavaScript](https://img.shields.io/badge/JavaScript-ES6+-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)](https://developer.mozilla.org)
[![Chart.js](https://img.shields.io/badge/Chart.js-4.4+-FF6384?style=for-the-badge&logo=chartdotjs&logoColor=white)](https://www.chartjs.org)

> **Developed by [Priya Sharma](https://github.com/sharmapriya18504-dotcom)**  
> *B.Tech Student | Aspiring Data Scientist & Machine Learning Engineer*  
> *Email: [sharmapriya18504@gmail.com](mailto:sharmapriya18504@gmail.com)*

---

## 📌 Executive Summary

This project performs **Unsupervised Machine Learning (K-Means Clustering)** and **Exploratory Data Analysis (EDA)** on real-world Zomato restaurant records and customer reviews across Hyderabad (Gachibowli, Banjara Hills, Jubilee Hills, Madhapur, Kondapur, etc.).

By segmenting 105+ restaurants into mathematically separated pricing tiers (**Budget-Friendly**, **Mid-Range Dining**, and **Premium / Luxury**), the platform provides actionable intelligence for:
- **Consumers**: Finding top-rated dining spots tailored to budget preferences.
- **Restaurant Owners**: Benchmarking pricing, cuisine competition, and rating performance against peers.
- **Zomato Marketing**: Personalizing targeted promotions, lunch combo discounts, and Zomato Gold fine dining curation.

---

## 📊 Dataset Overview (Real Hyderabad Data)

The analysis is conducted strictly on real data provided in the repository:

| Dataset File | Records | Key Attributes |
| :--- | :---: | :--- |
| **`Zomato Restaurant names and Metadata.csv`** | **105 Restaurants** | `Name`, `Links`, `Cost` (₹150 to ₹2,800 for two), `Collections`, `Cuisines`, `Timings` |
| **`Zomato Restaurant reviews.csv`** | **10,000+ Reviews** | `Restaurant`, `Reviewer`, `Review` text, `Rating` (1★ to 5★), `Metadata`, `Time`, `Pictures` |
| **`zomato.ipynb`** | **Jupyter Analysis** | End-to-end data cleaning, EDA, feature scaling, and initial K-Means clustering |

---

## 🧠 Machine Learning: Cost Clustering & Evaluation

The clustering pipeline scales the restaurant dining cost using **StandardScaler** ($Z = \frac{x - \mu}{\sigma}$) and applies **K-Means Clustering** with $K \in [2, 6]$.

### Model Evaluation Metrics:

| Number of Clusters ($K$) | Inertia (WCSS) | Silhouette Score | Interpretation |
| :---: | :---: | :---: | :--- |
| $K = 2$ | 31.83 | 0.651 | High cohesion, but too coarse for business use |
| **$K = 3$ (Optimal Elbow)** | **18.29** | **0.590** | **Best balance: Budget, Mid-Range, and Premium** |
| $K = 4$ | 9.42 | 0.548 | Subdivides mid-range tier |
| $K = 5$ | 4.88 | 0.536 | Creates granular luxury splits |
| $K = 6$ | 3.12 | 0.530 | Diminishing returns |

---

## 💻 Web Platform Features

1. **KPI Overview**:
   - 105 Hyderabad Restaurants Analyzed
   - 10,000+ Verified Customer Reviews
   - ₹861 Average Dining Cost (Min ₹150 • Max ₹2,800)
   - 0.590 Optimal Silhouette Score ($K=3$)

2. **Interactive K-Means Playground**:
   - Real-time $K$ slider ($K=2$ to $K=6$)
   - Dynamic Elbow Method Inertia Chart
   - Cluster Cost Distribution Chart
   - Real-time Silhouette status updates

3. **Exploratory Data Analysis (EDA) Hub**:
   - Dining Cost Distribution Histogram
   - Top 10 Most Popular Cuisines (North Indian, Chinese, Continental, Biryani, Asian, Fast Food, etc.)
   - 1★ to 5★ Customer Rating Breakdown
   - Top 10 Most Reviewed Restaurants

4. **Restaurant Directory Explorer**:
   - Live instantaneous search by Restaurant Name or Cuisine
   - Cuisine filter dropdown
   - Sort by Price (Low to High / High to Low), Rating, or Review count
   - Cluster tier filter pills
   - Restaurant cards featuring opening timings, collections, direct Zomato URLs, and real customer review quotes

5. **Pricing Tier Predictor**:
   - Input any restaurant name, estimated cost, and cuisine style
   - Predicts exact cluster tier with centroid distance and confetti celebration

---

## 🗂️ Project File Structure

```bash
zomato_project/
├── index.html                                  # Modern Semantic Responsive Web Dashboard
├── css/
│   └── style.css                               # Custom Dark Glassmorphism Design System (#E23744 Crimson)
├── js/
│   ├── app.js                                  # Interactive UI logic, Chart.js graphs, filter engine
│   └── data.js                                 # Precomputed JSON payload of all 105 restaurants & reviews
├── app.py                                      # Python WSGI Entrypoint & Local Dev Server
├── wsgi.py                                     # Vercel Serverless Function WSGI Handler
├── index.py                                    # Entrypoint fallback
├── pyproject.toml                              # PEP 621 metadata for Vercel uv builder
├── vercel.json                                 # Security headers & Vercel deployment configuration
├── .vercelignore                               # Build optimization ignore rules
├── .gitignore                                  # Git ignore rules
├── README.md                                   # Documentation
├── zomato.ipynb                                # Original Jupyter Data Science notebook
├── Zomato Restaurant names and Metadata.csv    # 105 Hyderabad restaurants dataset
└── Zomato Restaurant reviews.csv               # 10,000 reviews dataset
```

---

## 🚀 Running Locally

### Option 1: Double-click or open in any Browser
Simply open [`index.html`](file:///c:/Users/Priya%20Sharma/Downloads/zomato_project/index.html) in Chrome, Edge, Safari, or Firefox. Everything works with zero installations!

### Option 2: Python Local Server
```bash
python app.py
```
Visit: `http://localhost:8501`

---

## 🌐 Deploy to Vercel

1. Push the code to GitHub:
   ```bash
   git add .
   git commit -m "feat: complete professional Zomato clustering UI"
   git push origin main
   ```
2. Import the repository in [Vercel](https://vercel.com).
3. Click **Deploy** — Vercel builds and deploys the platform in seconds!

---

## 👩‍💻 Author

**Priya Sharma**  
- **GitHub**: [@sharmapriya18504-dotcom](https://github.com/sharmapriya18504-dotcom)  
- **Email**: sharmapriya18504@gmail.com  
- **Focus**: Data Science, Machine Learning, Python & Web UI
