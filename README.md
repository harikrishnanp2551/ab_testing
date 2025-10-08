# Airbnb Insights Dashboard

A Streamlit-based dashboard to explore Airbnb data (from Kaggle) and run analytical pipelines. The dashboard is designed to work locally with PostgreSQL, and in cloud environments (like Streamlit Cloud) using SQLite fallback.

<img width="2451" height="1303" alt="Screenshot 2025-09-26 202136" src="https://github.com/user-attachments/assets/d9246787-db2b-4612-968e-ba02566af99f" />

<img width="2022" height="1337" alt="Screenshot 2025-09-26 202116" src="https://github.com/user-attachments/assets/1af8eec3-18c3-4e0d-93cf-da8e2e2d82c4" />

<img width="2437" height="1340" alt="image" src="https://github.com/user-attachments/assets/d694780f-27d5-44f7-a1b8-29b730ce0982" />


# Airbnb Insights Dashboard

This project offers an interactive dashboard built in Streamlit that explores Airbnb listing data, runs feature-level “A/B tests”, and monitors data quality.

---

## What It Does

- Downloads Airbnb data from Kaggle  
- Cleans and transforms the data  
- Loads into a database — PostgreSQL (when available) or SQLite fallback  
- Runs analytics pipelines, including derived tables and comparisons  
- Visualizes insights via a web dashboard

---

## How to Set Up

### Requirements

- Python 3.8+  
- `kaggle` library  
- (Optional) PostgreSQL server for local development  
- Kaggle API credentials  
- Streamlit

### Installation Steps

1. Clone this repo.  
2. Install dependencies:

   ```bash
   pip install -r requirements.txt


Locally, create ./.streamlit/secrets.toml (or other secret file) with contents like:

[postgres]
DB_USER = "your_pg_user"
PASSWORD = "your_pg_password"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "airbnb_kaggle"

[kaggle]
username = "your_kaggle_username"
key = "your_kaggle_key"


On Streamlit Cloud, one can set the same keys via the Secrets UI.

Run:

streamlit run app.py

File Layout
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


db_utils.py — logic to choose PostgreSQL or SQLite

load_data.py — download + ingest data

run_pipeline.py — run SQL scripts or fallback logic

.sql files — cleaning, aggregation, tests

app.py — main dashboard interface



##Challenges & Lessons Learned
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


Future Enhancements

Better fallback logic: run SQL scripts (or Python equivalents) even under SQLite

Harmonize SQL scripts so they run both on Postgres and SQLite

Automate testing, deployment, and error logging

Add more visualizations, filters, and export options

Support incremental data updates instead of full reloads

Add user authentication, dynamic queries, and performance tuning

A/B Test Summary

This dashboard includes a kind of “A/B test” simulation: comparing different feature categories (e.g. high price vs low price, different neighborhoods) on the outcome number_of_reviews (as a proxy for engagement). We use Welch’s t-test to see if differences are statistically significant. The goal is to find which features are likely to drive engagement.

How to Use & Explore

Launch the dashboard.

Data will download (if not already present), cleaned, and loaded.

Navigate through tabs: data quality, analytics, feature comparisons, etc.

In the “A/B Test” tab, see comparisons across features and significance tests.

Optionally refresh the pipeline to re-download or re-run logic.

Limitations & Notes

SQLite fallback may not support all SQL features used in the pipeline

The A/B comparisons are observational — not true randomized experiments

The size of dataset and memory constraints may limit performance

Edge cases in data types or missing columns might throw errors
