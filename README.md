# Airbnb Insights Dashboard

A Streamlit-based dashboard to explore Airbnb data (from Kaggle) and run analytical pipelines. The dashboard is designed to work locally with PostgreSQL, and in cloud environments (like Streamlit Cloud) using SQLite fallback.

---

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

Challenge	Description	Mitigation / Lessons
Secrets & credentials management	You don’t want passwords in your code or repository. Streamlit Cloud needs access to secrets without exposing them.	Use Streamlit’s secrets manager. Fallback to constants.py locally or environment variables.
Missing dependencies in deployment	On deployment, certain libraries (e.g. psycopg2) may not be installed, causing runtime errors.	Ensure dependencies are listed in requirements.txt (e.g. psycopg2-binary).
Hard-coded paths incompatible with cloud	Using local file paths (e.g. "C:/Users/...") breaks deployment.	Use relative paths or temp directories (e.g. os.getcwd(), tempfile).
Database connectivity assumptions	You assumed Postgres would always be accessible (localhost), but on cloud it isn’t.	Implement fallback to SQLite or use a cloud-hosted database.
KeyError when accessing secrets	The secrets key name didn’t match the code (e.g. st.secrets["secrets"]).	Keep secret keys consistent, or structure nested secret tables.
Missing modules / imports	Helpers (e.g. load_data.py, run_pipeline.py) needed imports (like streamlit) to access st.secrets.	Always import required modules, test module-level code paths.
SQL pipelines skipped under fallback mode	When falling back to SQLite, skipping SQL scripts meant derived tables like data_quality_metrics didn’t exist.	Provide Python-based fallback logic to build essential tables.

🧪 Usage Example & Walkthrough
On local machine with Postgres, you’ll get full SQL pipeline & derived tables, visualizations enriched.

On Streamlit Cloud (or no Postgres access), app will switch to SQLite automatically. It may skip some SQL pipeline steps, or you may supply Python-based fallbacks for derived metrics.

UI continues to function using the available tables.

🏁 Conclusion
This project provides a way to build a data-driven dashboard with flexible backend options (Postgres / SQLite). The goal is to make deployment seamless while keeping local development full-featured. In upcoming versions, the fallback behavior, compatibility, and automation will be improved.
