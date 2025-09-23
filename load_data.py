import os
import zipfile
import pandas as pd
from sqlalchemy import create_engine
from kaggle.api.kaggle_api_extended import KaggleApi

import constants


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

#clean price and service price column
    if "price" in df.columns:
        df["price"] = (
            df["price"]
            .astype(str)
            .str.replace("[$,]", "", regex=True)
            .astype(float)
        )  
    if "service fee" in df.columns:
        df["service fee"] = (
            df["service fee"]
            .astype(str)
            .str.replace("[$,]", "", regex=True)
            .astype(float)
        ) 

    print(f"Loaded {len(df):,} rows from CSV.")

    #connect to postgres
    conn_str = 'postgresql://postgres:'+constants.PASSWORD+'@localhost:5432/airbnb_kaggle'
    engine = create_engine(conn_str)
    

    df.to_sql('airbnb_kaggle', engine, if_exists="replace", index=False, chunksize=1000)
    print("Data successfully loaded into Postgres.")

# RUN 
if __name__ == "__main__":
    download_dataset()
    load_to_postgres()