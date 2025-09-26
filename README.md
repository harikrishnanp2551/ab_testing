# Airbnb Insights Dashboard

A Streamlit-based dashboard to explore Airbnb data (from Kaggle) and run analytical pipelines. The dashboard is designed to work locally with PostgreSQL, and in cloud environments (like Streamlit Cloud) using SQLite fallback.

<img width="2451" height="1303" alt="Screenshot 2025-09-26 202136" src="https://github.com/user-attachments/assets/d9246787-db2b-4612-968e-ba02566af99f" />

<img width="2022" height="1337" alt="Screenshot 2025-09-26 202116" src="https://github.com/user-attachments/assets/1af8eec3-18c3-4e0d-93cf-da8e2e2d82c4" />

<img width="2437" height="1340" alt="image" src="https://github.com/user-attachments/assets/d694780f-27d5-44f7-a1b8-29b730ce0982" />


---
Purpose
The dashboard estimates how different listing attributes relate to engagement by comparing categories within each feature, since there are no true randomized A/B experiments available in the dataset. Engagement is proxied by the outcome number_of_reviews, and all results are framed as A/B‑style comparisons between category pairs within a feature.

What is compared
The analysis runs separate comparisons for each categorical or binary feature, including Neighbourhood Group (Brooklyn vs Manhattan), Price Bucket (<100 vs >=100), Room Type (entire_home vs private_room), Instant Bookable (True vs False), Cancellation Policy (flexible vs strict), and Service Fee (below_median vs above_median). Each comparison yields group means, sample sizes, a relative lift from group1 to group2, a p‑value from Welch’s t‑test, and a significance flag based on the defined threshold.

Metric
The outcome metric is number_of_reviews, used as a proxy for guest engagement with the listing in the absence of direct conversion or session metrics. All averages, lifts, and tests are computed on this metric for the specified category pairs within each feature.

Method
Direct category comparisons are performed within each feature rather than running a global multivariate model, aligning with the “A/B Test” section’s design note that real A/B experiments are not available.

Welch’s t‑test is used for the two‑sample comparisons because it is robust to unequal variances across category groups.

Lift is defined as the relative percent change from group1 to group2, reported as lift_pct in the tables.

Statistical significance is determined at p < 0.05, and the table includes a boolean significant indicator for each comparison.

How to read the tables
For each feature, the table shows group1 and group2 with their means (mean1 and mean2), sample sizes (n1 and n2), the relative lift from group1 to group2 (lift_pct), the Welch’s t‑test p_value, and whether the result meets the significance threshold. The “Significant Findings” panel re‑lists only the comparisons that pass the p < 0.05 threshold to make interpretation quicker.

Results summary
Two comparisons meet the significance threshold in the provided snapshot: Neighbourhood Group and Price Bucket.

Feature	group1 → group2	mean1	mean2	lift_pct	p_value
Neighbourhood Group	Brooklyn → Manhattan 	28.52 	24.11 	−15.4% 	2.99e−40 
Price Bucket	<100 → >=100 	25.87 	27.57 	+6.6% 	0.0273 
Non‑significant comparisons in the snapshot include Room Type (p = 0.116, lift ≈ +1.8%), Instant Bookable (p = 0.555, lift ≈ −0.7%), Cancellation Policy (p = 0.586, lift ≈ −0.8%), and Service Fee (p = 0.589, lift ≈ +0.6%). The narrative summary further notes that Price and Neighbourhood often show significant differences, while Instant Bookable, Cancellation Policy, Room Type, and Service Fee tend not to in this view of the data.

Interpretation notes
These are observational, A/B‑style category comparisons rather than randomized experiments, so results describe associations within features rather than causal effects. Significance is assessed per comparison using Welch’s t‑test with a threshold of p < 0.05, consistent with the dashboard’s stated methodology.

Reproducing the calculations
For any chosen feature, split the data into the two category groups shown as group1 and group2, compute mean number_of_reviews and sample sizes for each, and run Welch’s two‑sample t‑test to obtain the p_value. Compute lift_pct as the relative percentage change from group1 to group2 and mark the comparison as significant when p < 0.05, as reflected in the dashboard tables and “Significant Findings” panel.

What to look for in the UI
The A/B Test section presents an “Overview of Feature Impacts” table with the full set of comparisons and a “Significant Findings” panel listing only those passing the p‑value threshold for quick scanning. Plots such as “Number of Reviews by Neighbourhood Group” and “Number of Reviews by Price Bucket” provide visual context for the tabular differences reported above.

## 🧭 Overview

This project enables:

- Downloading Airbnb dataset from Kaggle
- Cleaning and transforming data
- Loading the data into a database (PostgreSQL locally, or SQLite in restricted environments)
- Running SQL-based pipelines/analytics (e.g. quality metrics, aggregations)
- Rendering interactive visualizations via Streamlit

---

## 🚀 Features

- **Data ingestion**: Fetch data from Kaggle automatically  
- **Dynamic DB backend**: Prefer PostgreSQL if available, fall back to SQLite  
- **SQL pipelines**: Run `.sql` scripts for cleaning, aggregations, AB testing  
- **Dashboard UI**: Visualize metrics, trends, insights with Streamlit  

---

## 🛠️ Setup & Installation

### Prerequisites

- Python 3.8+  
- `kaggle` API installed  
- Local PostgreSQL instance (optional, for local development)  
- Kaggle API credentials (username & key)  
- Streamlit secrets file for deployment environments  

### Installation

1. Clone the repo:

   ```bash
   git clone <repo-url>
   cd <repo-folder>
Setup Python environment and install dependencies:

bash
Copy code
pip install -r requirements.txt
Add secrets:

Locally: create .streamlit/secrets.toml:

toml
Copy code
[postgres]
DB_USER = "your_pg_user"
PASSWORD = "your_pg_password"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "airbnb_kaggle"

[kaggle]
username = "your_kaggle_username"
key = "your_kaggle_key"
On Streamlit Cloud: set these values in Settings → Secrets.

Run the app:

bash
Copy code
streamlit run app.py
📂 File Structure
pgsql
Copy code
.
├── app.py
├── db_utils.py
├── load_data.py
├── run_pipeline.py
├── eda_cleaning.sql
├── abtest_tables.sql
├── agg_tables.sql
├── requirements.txt
└── README.md
🔮 Future Updates (Roadmap)
Here are features or improvements to consider in future versions:

Automatic fallback / hybrid mode

Support automatic switching between PostgreSQL and SQLite

Rebuild derived tables (e.g. data_quality_metrics) via Python if SQL scripts fail on SQLite

Full SQL compatibility across DB types

Adapt SQL scripts so they run both on PostgreSQL and on SQLite

Use SQLAlchemy dialects to bridge syntax differences

Testing & CI/CD

Write unit & integration tests

Automate deployment & rebuilds

Error handling & logging improvements

More informative error messages

Better logging infrastructure

Modularization & code cleanup

Move dashboard logic into reusable modules

Use blueprints/components for UI

Performance & scalability

Pagination, query optimizations

Handling larger datasets (e.g. chunking, caching)

User interface enhancements

Additional filters, drill-downs

Export options (CSV, JSON, PDF)

⚠️ Challenges & Lessons Learned
Below are some of the key challenges encountered during development, and how you might address them in future work:


| Challenge | Description | Mitigation / Lessons |
|-----------|-------------|-----------------------|
| **Secrets & credentials management** | Passwords and DB credentials can’t be committed to git. Streamlit Cloud also needs secrets without exposing them. | Use Streamlit’s secrets manager for deployment. Use `constants.py` or environment variables locally. |
| **Missing dependencies in deployment** | Some libraries (e.g. `psycopg2`) weren’t available on Streamlit Cloud, causing errors. | Add all dependencies explicitly in `requirements.txt` (use `psycopg2-binary` for Postgres). |
| **Hard-coded local paths** | Windows-specific paths like `C:/Users/...` failed on Streamlit Cloud. | Use relative paths (`os.getcwd()`) or `tempfile` for portable directories. |
| **Database connectivity assumptions** | The code assumed `localhost` Postgres was always available, which fails in the cloud. | Implement fallback to SQLite, or host Postgres in the cloud. |
| **Secrets KeyError** | `st.secrets["secrets"]` raised errors because the TOML structure didn’t match. | Keep consistent key names in `secrets.toml`, e.g. `[postgres]`, `[kaggle]`. |
| **Missing module imports** | Helper scripts needed `streamlit` to access `st.secrets` but didn’t import it. | Ensure all modules import what they need. Test imports in isolation. |
| **SQL pipeline skipped in fallback** | Skipping SQL files when falling back to SQLite meant derived tables (e.g. `data_quality_metrics`) didn’t exist. | Provide Python fallback logic to create critical tables in SQLite. |


🧪 Usage Example & Walkthrough
On local machine with Postgres, you’ll get full SQL pipeline & derived tables, visualizations enriched.

On Streamlit Cloud (or no Postgres access), app will switch to SQLite automatically. It may skip some SQL pipeline steps, or you may supply Python-based fallbacks for derived metrics.

UI continues to function using the available tables.

🏁 Conclusion
This project provides a way to build a data-driven dashboard with flexible backend options (Postgres / SQLite). The goal is to make deployment seamless while keeping local development full-featured. In upcoming versions, the fallback behavior, compatibility, and automation will be improved.
