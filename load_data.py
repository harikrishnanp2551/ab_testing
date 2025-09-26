import os
import pandas as pd
from sqlalchemy import create_engine
from kaggle.api.kaggle_api_extended import KaggleApi
import streamlit as st
import json

secrets = st.secrets["postgres"]

# Set up Kaggle API credentials from Streamlit secrets
kaggle_secrets = st.secrets["kaggle"]
os.environ["KAGGLE_USERNAME"] = kaggle_secrets["username"]
os.environ["KAGGLE_KEY"] = kaggle_secrets["key"]

# ---- SETTINGS ----
KAGGLE_DATASET = "arianazmoudeh/airbnbopendata"
DOWNLOAD_DIR = "C:/Users/asus/Documents/Projects/ab_testing"
CSV_FILE = "Airbnb_Open_Data.csv"

# download data from kaggle
def download_dataset():
    api = KaggleApi()
    api.authenticate()
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    print("Downloading dataset from kaggle ")
    api.dataset_download_files(KAGGLE_DATASET, path=DOWNLOAD_DIR, unzip=True)
    print("Download complete.")

# load csv into postgres
def load_to_postgres():
    csv_path = os.path.join(DOWNLOAD_DIR, CSV_FILE)
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"{csv_path} not found. Check file name inside {DOWNLOAD_DIR}")

    print("CSV conversion to dataframe")
    df = pd.read_csv(csv_path)

    # --- Clean column names to snake_case lowercase ---
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    # set id as index if exists
    if "id" in df.columns:
        df.set_index("id", inplace=True)

    # clean price and service_fee columns
    if "price" in df.columns:
        df["price"] = (
            df["price"]
            .astype(str)
            .str.replace("[$,]", "", regex=True)
            .astype(float)
        )

    if "service_fee" in df.columns:
        df["service_fee"] = (
            df["service_fee"]
            .astype(str)
            .str.replace("[$,]", "", regex=True)
            .astype(float)
        )

    print(f"Loaded {len(df):,} rows from CSV.")

    # connect to postgres
    conn_str = f'postgresql://postgres:{secrets["PASSWORD"]}@localhost:5432/airbnb_kaggle'
    engine = create_engine(conn_str)

    df.to_sql('airbnb_kaggle', engine, if_exists="replace", index=True, chunksize=1000)
    print("Data successfully loaded into Postgres.")

# RUN
if __name__ == "__main__":
    download_dataset()
    load_to_postgres()
