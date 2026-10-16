# Data Dictionary

## 📖 Dataset Overview
This platform ingests raw Zomato restaurant metadata and verified customer reviews, synthesizing an enriched analytical master dataset.

---

### 1. Master Enriched Dataset Schema (`data/processed/zomato_enriched.csv`)

| Column Name | Data Type | Nullable | Description & Transformation |
| :--- | :--- | :--- | :--- |
| `name` | String | No | Official restaurant trade name. Stripped of whitespace. |
| `cost` | Float | No | Approximate dining cost for two in INR. Stripped of currency signs and commas. |
| `avg_rating` | Float | No | Mean customer rating aggregated from verified reviews, bounded in `[1.0, 5.0]`. Defaults to 3.8 if unreviewed. |
| `votes` | Integer | No | Count of customer reviews and ratings in the dataset. |
| `rating_std` | Float | No | Standard deviation of ratings for this restaurant. Measures score consistency. |
| `pos_review_ratio` | Float | No | Ratio of reviews scoring `≥ 4.0` stars out of total reviews for this establishment. |
| `total_pictures` | Integer | No | Cumulative number of user-uploaded photos across all reviews. |
| `cuisines` | String | No | Comma-separated list of culinary styles served. |
| `cuisines_list` | List[str] | No | Parsed token array of culinary tags for fast search and filtering. |
| `primary_cuisine` | String | No | Lead culinary style (first listed tag). |
| `num_cuisines` | Integer | No | Count of culinary categories offered. |
| `locality` | String | No | Neighborhood market zone (e.g. Gachibowli, Madhapur, Hitec City). |
| `city` | String | No | Metropolitan area (e.g. Hyderabad). |
| `price_tier` | String | No | Descriptive heuristic tier: `Budget Friendly (<= 500)`, `Mid-Range (501 - 1,200)`, `Premium Dining (1,201 - 1,800)`, `Luxury & Fine Dine (> 1,800)`. |
| `value_index` | Float | No | Value for money indicator computed as `avg_rating / log(cost + 10)`. |
| `collections` | String | Yes | Editorial Zomato tags (e.g. Great Buffets, Corporate Favorites). |
| `timings` | String | Yes | Daily operating business hours. |
| `links` | String | Yes | Direct canonical link to the official Zomato restaurant web page. |

---

### 2. Raw Source Files

1. **`Zomato Restaurant names and Metadata.csv`**:
   - `Name`: String
   - `Links`: URL string
   - `Cost`: Formatted string (e.g. `"1,300"`)
   - `Collections`: Thematic categories
   - `Cuisines`: Raw culinary styles
   - `Timings`: Business hours
2. **`Zomato Restaurant reviews.csv`**:
   - `Restaurant`: Target restaurant name
   - `Reviewer`: User handle
   - `Review`: Free-text review content
   - `Rating`: String rating (`1` to `5`, `4.5`, or non-numeric entries like `'Like'`)
   - `Metadata`: Reviewer activity summary
   - `Time`: Timestamp of review publication
   - `Pictures`: Count of images uploaded with review
