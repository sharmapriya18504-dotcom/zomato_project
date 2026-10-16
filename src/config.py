"""
Configuration module for Zomato Restaurant Intelligence Platform.
Handles directory paths, column normalization schemas, and model parameters.
"""

from pathlib import Path
from typing import Dict, List

# Base Directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = BASE_DIR / "models"
REPORTS_DIR = BASE_DIR / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"

# Default Dataset File Names
DEFAULT_META_FILENAME = "Zomato Restaurant names and Metadata.csv"
DEFAULT_REVIEWS_FILENAME = "Zomato Restaurant reviews.csv"
PROCESSED_DATASET_FILENAME = "zomato_enriched.csv"

# Pre-packaged File Paths
RAW_META_PATH = RAW_DATA_DIR / DEFAULT_META_FILENAME
RAW_REVIEWS_PATH = RAW_DATA_DIR / DEFAULT_REVIEWS_FILENAME
ROOT_META_PATH = BASE_DIR / DEFAULT_META_FILENAME
ROOT_REVIEWS_PATH = BASE_DIR / DEFAULT_REVIEWS_FILENAME
ENRICHED_DATA_PATH = PROCESSED_DATA_DIR / PROCESSED_DATASET_FILENAME

# Column Name Aliases for Dynamic Validation & Upload
COLUMN_ALIASES: Dict[str, List[str]] = {
    "name": ["name", "restaurant_name", "restaurant", "res_name"],
    "cost": [
        "cost", "approx_cost_for_two", "approx_cost(for two people)", 
        "average_cost_for_two", "price", "cost_for_two"
    ],
    "cuisines": ["cuisines", "cuisine", "food_type", "cuisine_type"],
    "links": ["links", "link", "url", "zomato_url"],
    "collections": ["collections", "collection", "tags"],
    "timings": ["timings", "timing", "hours", "opening_hours"],
    "rating": ["rating", "rate", "aggregate_rating", "avg_rating", "score"],
    "votes": ["votes", "review_count", "reviews", "num_reviews", "ratings_count"],
    "locality": ["locality", "address", "area", "subzone"],
    "city": ["city", "town", "region"]
}

# Machine Learning Parameters
RANDOM_SEED = 42
DEFAULT_K_CLUSTERS = 3
MIN_K_CLUSTERS = 2
MAX_K_CLUSTERS = 7

# Visual & Clustering Palette
CLUSTER_COLORS = [
    "#10B981",  # Cluster 0 - Emerald (Budget)
    "#3B82F6",  # Cluster 1 - Blue (Mid-Range)
    "#F59E0B",  # Cluster 2 - Amber (Premium)
    "#8B5CF6",  # Cluster 3 - Purple (Luxury)
    "#EC4899",  # Cluster 4 - Pink (Fine Dining)
    "#06B6D4",  # Cluster 5 - Cyan (Signature)
    "#14B8A6"   # Cluster 6 - Teal (Elite)
]

# Theme Settings
THEME_CONFIG = {
    "primaryColor": "#E23744",
    "backgroundColor": "#0B0E14",
    "secondaryBackgroundColor": "#151C2C",
    "textColor": "#F8FAFC",
    "font": "sans-serif"
}
