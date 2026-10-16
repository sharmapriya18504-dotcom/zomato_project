# Model Card: Restaurant Clustering & Intelligence Models

## 📌 Model Details
- **Model Name:** Zomato Restaurant Segmentation Pipeline
- **Model Version:** 2.0.0
- **Authors:** Priya Sharma
- **Frameworks:** Python 3.10+, Scikit-Learn 1.7+, Pandas, NumPy

---

## 🎯 Intended Use
- **Primary Use Case:** Segmenting dining establishments into mathematical pricing clusters (Budget-Friendly, Mid-Range Dining, Premium & Fine Dine).
- **Secondary Use Case:** Supporting transparent recommendation ranking, neighborhood competitor benchmarking, and promotional targeting.
- **Out-of-Scope Uses:** The models **do not** predict business profitability, kitchen hygiene standards, food freshness, or customer footfall volume.

---

## ⚙️ Algorithms & Preprocessing
1. **K-Means Clustering:**
   - Minimizes within-cluster sum-of-squares (Inertia).
   - Tunable $K \in [2, 7]$ (Elbow inflection observed at $K = 3$).
   - Random state: 42, $n\_init = 10$.
2. **Agglomerative Hierarchical Clustering:**
   - Bottom-up hierarchical merging.
   - Linkage options: `ward` (minimizes variance) and `average` (average pairwise distance).
3. **Feature Preprocessing:**
   - Feature scaling via `StandardScaler` ($Z = \frac{X - \mu}{\sigma}$).
   - Median imputation for missing values.
   - Centroid sorting to ensure intuitive ascending ordering by cost.

---

## 📊 Evaluation & Benchmarks (At $K=3$)
- **Silhouette Coefficient:** **0.590** (Indicates well-separated, distinct clusters).
- **Davies–Bouldin Index:** **0.536** (Low ratio of within-cluster scatter to separation).
- **Calinski–Harabasz Index:** **243.8** (Strong variance ratio criterion).
- **Inertia:** **18.29** (Sharp reduction from $K=2$ at 31.83).

---

## ⚠️ Caveats & Ethical Considerations
- Statistical outliers with high costs (e.g. > INR 2,000) reflect legitimate luxury experiences rather than corrupted records.
- Customer reviews can exhibit voluntary-response bias (users with very positive or negative experiences are more likely to submit reviews).
