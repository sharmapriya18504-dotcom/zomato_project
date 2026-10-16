"""
Data loader module for reading, caching, and loading datasets.
Supports local files, uploaded files, and fallbacks.
"""

from pathlib import Path
from typing import Optional, Tuple, Union
import io
import pandas as pd
import streamlit as st

from src.config import (
    RAW_META_PATH, RAW_REVIEWS_PATH, ROOT_META_PATH, ROOT_REVIEWS_PATH,
    ENRICHED_DATA_PATH
)
from src.validation import map_columns


def read_csv_safe(source: Union[str, Path, io.BytesIO, io.StringIO]) -> pd.DataFrame:
    """
    Safely load CSV with automatic fallback for various file encodings.
    """
    encodings = ["utf-8", "latin1", "cp1252", "iso-8859-1"]
    last_err = None
    
    for enc in encodings:
        try:
            if isinstance(source, (str, Path)):
                return pd.read_csv(source, encoding=enc)
            elif hasattr(source, "seek"):
                source.seek(0)
                return pd.read_csv(source, encoding=enc)
        except Exception as e:
            last_err = e
            continue
            
    raise ValueError(f"Unable to read CSV file with standard encodings: {last_err}")


def get_default_dataset_paths() -> Tuple[Optional[Path], Optional[Path]]:
    """
    Locate the raw metadata and reviews datasets in data/raw or root workspace.
    """
    meta_path = None
    reviews_path = None
    
    if RAW_META_PATH.exists():
        meta_path = RAW_META_PATH
    elif ROOT_META_PATH.exists():
        meta_path = ROOT_META_PATH
        
    if RAW_REVIEWS_PATH.exists():
        reviews_path = RAW_REVIEWS_PATH
    elif ROOT_REVIEWS_PATH.exists():
        reviews_path = ROOT_REVIEWS_PATH
        
    return meta_path, reviews_path


@st.cache_data(show_spinner=False)
def load_raw_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load raw metadata and reviews datasets.
    """
    meta_path, reviews_path = get_default_dataset_paths()
    
    if meta_path and meta_path.exists():
        df_meta = read_csv_safe(meta_path)
    else:
        df_meta = pd.DataFrame()
        
    if reviews_path and reviews_path.exists():
        df_reviews = read_csv_safe(reviews_path)
    else:
        df_reviews = pd.DataFrame()
        
    return df_meta, df_reviews


def create_demo_dataset() -> pd.DataFrame:
    """
    Generate a realistic demo dataset if no dataset is provided or uploaded.
    """
    demo_data = {
        "name": [
            "Biryani House", "Spice Symphony", "Tandoori Nights", "Urban Cafe",
            "Golden Dragon", "Pasta Fresca", "Chai Shai", "Sushi Express",
            "The Fisherman's Deck", "Baking Bad", "Green Leaf Pure Veg", "The Royal Dawat"
        ],
        "cost": [450, 850, 1100, 600, 950, 1200, 200, 1600, 1800, 500, 400, 2200],
        "rating": [4.3, 4.1, 3.9, 4.4, 4.2, 4.5, 4.0, 4.6, 4.3, 4.2, 4.1, 4.7],
        "votes": [120, 240, 95, 310, 180, 420, 65, 510, 390, 110, 140, 680],
        "cuisines": [
            "Biryani, North Indian", "North Indian, Continental", "Mughlai, Kebab", "Cafe, Fast Food",
            "Chinese, Asian", "Italian, Pizza", "Tea, Street Food", "Japanese, Sushi",
            "Seafood, Continental", "Bakery, Desserts", "South Indian, North Indian", "Mughlai, Awadhi"
        ],
        "locality": [
            "Gachibowli", "Hitec City", "Madhapur", "Jubilee Hills",
            "Banjara Hills", "Kondapur", "Gachibowli", "Jubilee Hills",
            "Gachibowli", "Madhapur", "Kondapur", "Banjara Hills"
        ],
        "city": ["Hyderabad"] * 12,
        "links": ["https://www.zomato.com"] * 12
    }
    return pd.DataFrame(demo_data)
