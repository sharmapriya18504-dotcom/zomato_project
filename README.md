# 🍽️ Zomato Restaurant Cost Clustering & Data Intelligence

[![Vercel Deployment](https://img.shields.io/badge/Deploy-Vercel-black?style=for-the-badge&logo=vercel)](https://vercel.com)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

> **Developed by [Priya Sharma](https://github.com/sharmapriya18504-dotcom)**  
> *B.Tech Student | Aspiring Data Scientist & Machine Learning Engineer*

An end-to-end Data Science & Unsupervised Machine Learning project analyzing and clustering 105+ restaurants across Hyderabad listed on Zomato. The application segments dining places into intelligent pricing tiers (**Budget-Friendly**, **Mid-Range**, and **Premium / Luxury**) using K-Means clustering, Silhouette evaluation, and comprehensive review analytics.

---

## 🌟 Key Highlights & Features

- **🤖 Interactive K-Means Playground**: Real-time slider to test $K \in [2, 6]$, dynamically updating cluster centroids, inertia, and silhouette scores.
- **📉 Mathematical Validation**:
  - **Elbow Method Curve**: Pinpoints the optimal inflection point ($K = 3$).
  - **Silhouette Coefficient**: Achieves **0.590** at $K=3$, demonstrating distinct separation between budget and premium dining.
- **📊 Exploratory Data Analysis (EDA) Hub**:
  - Dining Cost Histogram & Density Distribution.
  - Top 10 Most Popular Cuisines (North Indian, Chinese, Continental, Biryani, etc.).
  - Customer Rating breakdown across **10,000+ verified reviews**.
  - Most Reviewed Restaurants ranking.
- **🍽️ Smart Restaurant Explorer**:
  - Live search by restaurant name, cuisine, or collection.
  - Filter by dynamic pricing tiers.
  - Direct links to official Zomato restaurant profiles.
- **🔮 Interactive Pricing Predictor**:
  - Enter hypothetical restaurant cost & cuisine to predict which tier it belongs to, along with marketing recommendations.
- **⚡ Dual Deployment Architecture**:
  1. **Standalone Web UI (`index.html`)**: Instant 1-click deployment on **Vercel** with zero build configuration!
  2. **Python Streamlit App (`app.py`)**: Local development and Streamlit Community Cloud support.

---

## 🗂️ Project Structure

```bash
zomato_project/
├── index.html                           # Main entry point for Vercel deployment
├── vercel.json                          # Vercel configuration & header caching
├── css/
│   └── style.css                        # Modern dark glassmorphism design system
├── js/
│   ├── app.js                           # Clustering engine, Chart.js logic, search & filters
│   └── data.js                          # Embedded JSON dataset & precomputed ML metrics
├── app.py                               # Enhanced Python Streamlit dashboard
├── zomato.ipynb                         # Jupyter Notebook with complete EDA & model training
├── requirements.txt                     # Python dependencies
├── .gitignore                           # Git ignore rules (excludes virtualenvs & caches)
├── Zomato Restaurant names and Metadata.csv # Metadata dataset (105 restaurants)
├── Zomato Restaurant reviews.csv        # Reviews dataset (10,000+ reviews)
└── README.md                            # Comprehensive documentation
```

---

## 🚀 How to Deploy on Vercel (1-Click)

1. **Push this repository to your GitHub account**:
   ```bash
   git add .
   git commit -m "Add professional UI, clean repository, and Vercel configuration"
   git push origin main
   ```

2. **Deploy on Vercel**:
   - Go to [vercel.com](https://vercel.com) and sign in with GitHub.
   - Click **"Add New Project"** -> **"Import"** `zomato_project`.
   - Leave the Framework Preset as **"Other"** (Root Directory: `./`).
   - Click **Deploy**! 🚀
   - Your project will be live in **15 seconds** with a free SSL `.vercel.app` URL!

---

## 💻 How to Run Locally

### Option 1: Open the Web UI directly (No installation needed!)
Simply double-click `index.html` in your file explorer, or serve it locally with:
```bash
python -m http.server 3000
```
Then visit `http://localhost:3000` in your web browser.

### Option 2: Run the Streamlit Dashboard
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the Streamlit app
streamlit run app.py
```

---

## 📊 Machine Learning Methodology

1. **Data Cleaning & Preprocessing**:
   - Stripped currency symbols, commas, and coerced cost values to numeric integers.
   - Handled missing values and eliminated invalid rows.
2. **Feature Normalization**:
   - Applied `StandardScaler` from Scikit-Learn to normalize restaurant costs ($Z = \frac{X - \mu}{\sigma}$).
3. **K-Means Clustering**:
   - Iterated through $K = 2$ to $K = 7$ with `random_state=42`.
   - Calculated Within-Cluster Sum of Squares (Inertia) to generate the Elbow plot.
4. **Performance Evaluation**:
   - Evaluated clusters using the **Silhouette Score** ($s = \frac{b - a}{\max(a, b)}$).
   - $K = 3$ produced the optimal elbow inflection with a Silhouette Score of **0.590**.

---

## 👩‍💻 Author

**Priya Sharma**  
- B.Tech Student | Aspiring Data Scientist  
- GitHub: [@sharmapriya18504-dotcom](https://github.com/sharmapriya18504-dotcom)  
- Email: sharmapriya18504@gmail.com  

*Contributions, stars, and feedback are always welcome!*
