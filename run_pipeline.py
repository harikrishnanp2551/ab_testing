# run_pipeline.py
import os
from sqlalchemy import create_engine, text
import sys

import constants


  #connect to postgres
conn_str = 'postgresql://postgres:'+constants.PASSWORD+'@'+constants.DB_HOST+':'+constants.DB_PORT+'/'+constants.DB_NAME+''
engine = create_engine(conn_str)

# SQL files (adjust names/paths if different)
SQL_FILES = [
    "eda_cleaning.sql",     # your EDA + cleaning (should create/replace data_quality_metrics etc)
    "abtest_tables.sql",    # A/B test simulation tables
    "agg_tables.sql",       # aggregate tables for dashboard (you uploaded this)
]

def load_sql_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def run_sql_script(engine, script):
    # Split on semicolons but keep simple; run each statement separately to surface errors
    # Note: multi-line functions/queries with semicolons may be split incorrectly; if that happens,
    # keep scripts simple or use a more robust parser. This works for typical DDL/DML files.
    statements = [s.strip() for s in script.split(";") if s.strip()]
    with engine.begin() as conn:
        for stmt in statements:
            try:
                conn.execute(text(stmt))
            except Exception as e:
                print("Error executing statement:")
                print(stmt[:400])
                raise

def main():
    print("Connecting to Postgres...")
    engine = create_engine(conn_str, pool_pre_ping=True)
    

    for sql_file in SQL_FILES:
        if not os.path.exists(sql_file):
            print(f"SQL file not found: {sql_file} — skipping")
            continue
        print(f"\n--- Running {sql_file} ---")
        script = load_sql_file(sql_file)
        try:
            run_sql_script(engine, script)
            print(f"✔ {sql_file} completed")
        except Exception as e:
            print(f"✖ Error while running {sql_file}: {e}")
            raise

    print("\nAll SQL scripts executed. Aggregate tables created/updated.")

if __name__ == "__main__":
    main()
