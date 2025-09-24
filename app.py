# app.py
import os
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import plotly.express as px

import constants

st.set_page_config(layout="wide", page_title="Airbnb Dashboard + A/B Test")

# DB config
CONN_STR = 'postgresql://postgres:'+constants.PASSWORD+'@'+constants.DB_HOST+':'+constants.DB_PORT+'/'+constants.DB_NAME+''
engine = create_engine(CONN_STR, pool_pre_ping=True)

# Helper to read SQL into dataframe cached
@st.cache_data
def read_sql(query, params=None):
    return pd.read_sql_query(text(query), engine, params=params)

st.title("Airbnb — Aggregates Dashboard + A/B Test")
st.markdown("Precomputed aggregates power this dashboard. If you updated raw data, run `python run_pipeline.py` first.")

# Top KPIs (from listing_summary / agg tables)
col1, col2, col3, col4 = st.columns(4)
try:
    total_listings_df = read_sql("SELECT COUNT(*) AS total FROM airbnb_kaggle")
    total_listings = int(total_listings_df.total.iloc[0])
    col1.metric("Total listings (raw)", f"{total_listings:,}")
except Exception:
    col1.metric("Total listings (raw)", "n/a")

# Aggregate KPIs using agg tables
try:
    # Average price overall
    avg_price_df = read_sql("SELECT ROUND(AVG(price)::numeric,2) AS avg_price FROM airbnb_kaggle")
    col2.metric("Avg price", f"${float(avg_price_df.avg_price.iloc[0]):,.2f}")
except Exception:
    col2.metric("Avg price", "n/a")

try:
    # Avg review score and availability
    avg_review = read_sql("SELECT ROUND(AVG(review_scores_rating)::numeric,2) AS avg_review FROM airbnb_kaggle").avg_review.iloc[0]
    col3.metric("Avg review score", f"{avg_review}")
except Exception:
    col3.metric("Avg review score", "n/a")

try:
    avg_avail = read_sql("SELECT ROUND(AVG(availability_365)::numeric,2) AS avg_avail FROM airbnb_kaggle").avg_avail.iloc[0]
    col4.metric("Avg availability (365d)", f"{avg_avail}")
except Exception:
    col4.metric("Avg availability", "n/a")

st.markdown("---")

# Neighbourhood breakdown
st.header("Listings by Neighbourhood")
nb_df = read_sql("SELECT neighbourhood, total_listings, avg_price, avg_reviews FROM agg_listings_by_neighbourhood ORDER BY total_listings DESC LIMIT 200")
st.dataframe(nb_df)

fig_nb = px.bar(nb_df, x="neighbourhood", y="total_listings", hover_data=["avg_price","avg_reviews"], title="Listings by Neighbourhood")
st.plotly_chart(fig_nb, use_container_width=True)

# Room type breakdown
st.header("Listings by Room type")
rt_df = read_sql("SELECT \"room type\" as room_type, total_listings, avg_price FROM agg_listings_by_roomtype")
fig_rt = px.pie(rt_df, names="room_type", values="total_listings", title="Room Type Distribution")
st.plotly_chart(fig_rt, use_container_width=True)
st.dataframe(rt_df)

# Price distribution
st.header("Price distribution")
pd_df = read_sql("SELECT price_range, listings FROM agg_price_distribution ORDER BY price_range")
fig_pd = px.bar(pd_df, x="price_range", y="listings", title="Price Ranges")
st.plotly_chart(fig_pd, use_container_width=True)

# A/B test tab
st.header("A/B Test (precomputed groups)")
try:
    # show group counts
    ab_counts = read_sql("SELECT group as ab_group, COUNT(*) as listings FROM ab_test_groups GROUP BY group ORDER BY group")
    st.subheader("Group sizes")
    st.table(ab_counts)

    # conv proxy: use conv_rate from ab_group_summary if exists, else compute basic metrics
    try:
        ab_summary = read_sql("SELECT ab_group, n_listings, avg_price, avg_reviews, conv_rate FROM ab_group_summary ORDER BY ab_group")
        st.subheader("A/B group summary")
        st.dataframe(ab_summary)
    except Exception:
        st.info("ab_group_summary table not present; computing simple group averages.")
        fallback = read_sql("""
            SELECT group AS ab_group, COUNT(*) AS n_listings, ROUND(AVG(price),2) AS avg_price, ROUND(AVG(review_scores_rating),2) AS avg_review
            FROM ab_test_groups
            GROUP BY group
            ORDER BY group
        """)
        st.dataframe(fallback)
except Exception as e:
    st.warning(f"A/B tables not found or error: {e}")

# Data quality tab
st.header("Data Quality Metrics")
try:
    dq = read_sql("SELECT step, metric_name, metric_value, recorded_at FROM data_quality_metrics ORDER BY recorded_at DESC")
    st.dataframe(dq)
except Exception:
    st.info("data_quality_metrics table not found. Run cleaning pipeline (run_pipeline.py).")

st.markdown("---")
st.caption("Dashboard reads only precomputed tables. Re-run pipeline to refresh aggregates.")
