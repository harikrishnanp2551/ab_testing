import os
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import plotly.express as px

import constants
import load_data
import run_pipeline

# ---------- Streamlit Config ----------
st.set_page_config(layout="wide", page_title="Airbnb Dashboard")
st.markdown("<div class='dashboard-title'>Airbnb Insights Dashboard</div>", unsafe_allow_html=True)

# Airbnb theme
AIRBNB_RED = "#FF5A5F"
AIRBNB_WHITE = "#FFFFFF"

st.markdown(f"""
<style>
    body {{
        background-color: #F7B7B7;
    }}
    /* Dashboard Title */
    .dashboard-title {{
        text-align: left;
        font-size: 36px;
        font-weight: bold;
        color: {AIRBNB_RED};
        margin-bottom: 5px;
    }}
    /* Metric cards */
    .metric-card {{
        background-color: {AIRBNB_RED};
        color: {AIRBNB_WHITE};
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        margin-bottom: 10px;
        box-shadow: 0px 2px 6px rgba(0,0,0,0.2);
    }}
    .metric-card h4 {{
        margin: 0;
        font-size: 20px;
    }}
    .metric-card h2 {{
        margin: 0;
        font-size: 40px;
        font-weight: bold;
    }}
    /* Tabs */
    .stTabs [role="tab"] {{
        background-color: {AIRBNB_RED};
        color: white;
        font-weight: bold;
        border-radius: 6px 6px 0px 0px;
        padding: 8px 16px;
    }}
    .stTabs [role="tab"]:hover {{
        background-color: #e0484c;
        color: white;
    }}
    .stTabs [role="tab"][aria-selected="true"] {{
        background-color: #d53c43;
        color: white;
    }}
</style>
""", unsafe_allow_html=True)

# ---------- Database Setup ----------
CONN_STR = f'postgresql://postgres:{constants.PASSWORD}@{constants.DB_HOST}:{constants.DB_PORT}/{constants.DB_NAME}'
engine = create_engine(CONN_STR, pool_pre_ping=True)

# ---------- Data Loader & Pipeline ----------
@st.cache_resource
def initialize_data():
    """Runs data load and pipeline once, stores results in Postgres."""
    load_data.download_dataset()
    load_data.load_to_postgres()
    run_pipeline.main()
    return True

# ---------- Refresh Logic ----------
if st.sidebar.button("🔄 Refresh Data & Pipeline"):
    st.cache_data.clear()
    st.cache_resource.clear()
    initialize_data()
    st.success("Data & pipeline refreshed successfully!")

# Initialize on first run
initialize_data()

# ---------- Helper to read SQL ----------
@st.cache_data
def read_sql(query):
    return pd.read_sql_query(text(query), engine)

# ---------- Sidebar Filters ----------
st.sidebar.header("Filters")
room_types = st.sidebar.multiselect(
    "Room Type",
    read_sql("SELECT DISTINCT room_type FROM airbnb_kaggle").room_type.tolist()
)
price_range = st.sidebar.slider("Price range", 0, 10000, (0, 1000))

def apply_filters(df):
    if room_types and "room_type" in df.columns:
        df = df[df["room_type"].isin(room_types)]
    if "price" in df.columns:
        df = df[(df["price"] >= price_range[0]) & (df["price"] <= price_range[1])]
    return df

# ---------- Tabs ----------
tab1, tab2, tab3 = st.tabs(["Overview", "A/B Test", "Data Quality"])

# ---- Overview Tab ----
with tab1:

    # Create layout: left (stacked bar) | right (metrics + scatter)
    left_col, right_col = st.columns([7, 6])

    # ----- LEFT: Stacked Bar -----
    with left_col:
        stacked_raw = read_sql("""
            SELECT neighbourhood, room_type, price
            FROM airbnb_kaggle
        """)
        stacked_raw = apply_filters(stacked_raw)

        stacked_df = (
            stacked_raw
            .groupby(["neighbourhood", "room_type"])
            .size()
            .reset_index(name="total")
            .sort_values("total", ascending=False)
        )

        fig_stacked = px.bar(
            stacked_df, y="neighbourhood", x="total", color="room_type",
            orientation="h",
            title="Listings by Neighborhood and Room Type",
            color_discrete_sequence=px.colors.sequential.Reds,
            # Optional: auto labels (may be busy for stacked)
            # text_auto=True,
        )

        # Broader bars and tighter spacing
        fig_stacked.update_traces(width=0.9)  # widen across the categorical axis
        fig_stacked.update_layout(bargap=0.05, bargroupgap=0.5)

        # Scale height to keep bars thick
        bar_count = stacked_df["neighbourhood"].nunique()
        fig_stacked.update_layout(height=min(5000, 30 * bar_count + 120))

        # Clean look and optional rounded corners
        fig_stacked.update_traces(marker_line_width=0)
        fig_stacked.update_layout(barcornerradius="25%")

        # Keep ordering and theme
        fig_stacked.update_layout(
            yaxis={"categoryorder": "total ascending"},
            bargap=0.05, barmode="stack",
            plot_bgcolor=AIRBNB_RED, paper_bgcolor=AIRBNB_RED, font_color="white"
        )


        container = st.container(height=780, border=True)  # fixed-height scroll area
        with container:
            st.plotly_chart(fig_stacked, use_container_width=True, config={"displayModeBar": False})
        

    # ----- RIGHT: KPIs + Scatter -----
    with right_col:
    # KPIs
        kpi_df = read_sql("SELECT host_name, number_of_reviews, price FROM airbnb_kaggle")
        kpi_df = apply_filters(kpi_df)

        total_hosts = kpi_df["host_name"].nunique()
        total_listings = len(kpi_df)
        avg_reviews = round(kpi_df["number_of_reviews"].mean(), 2)
        avg_price = round(kpi_df["price"].mean(), 2)

        # Row 1
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"<div class='metric-card'><h4>Total Hosts</h4><h2>{total_hosts:,}</h2></div>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<div class='metric-card'><h4>Total Listings</h4><h2>{total_listings:,}</h2></div>", unsafe_allow_html=True)

        # Row 2
        c3, c4 = st.columns(2)
        with c3:
            st.markdown(f"<div class='metric-card'><h4>Avg Reviews</h4><h2>{avg_reviews}</h2></div>", unsafe_allow_html=True)
        with c4:
            st.markdown(f"<div class='metric-card'><h4>Avg Price</h4><h2>${avg_price}</h2></div>", unsafe_allow_html=True)

       


        # Scatter plot
        scatter_df = read_sql("SELECT price, number_of_reviews, room_type FROM airbnb_kaggle LIMIT 10000")
        scatter_df = apply_filters(scatter_df)

        fig_scatter = px.scatter(
            scatter_df, x="number_of_reviews", y="price",
            opacity=0.6, color="room_type",
            title="Price vs Number of Reviews",
            color_discrete_sequence=px.colors.sequential.Reds
        )
        fig_scatter.update_xaxes(range=[0, 1200])
        fig_scatter.update_yaxes(range=[0, 1200])
        fig_scatter.update_layout(height=500, plot_bgcolor=AIRBNB_RED, paper_bgcolor=AIRBNB_RED, font_color="white")

        avg_price_val = scatter_df["price"].mean()
        fig_scatter.add_hline(y=avg_price_val, line_dash="dot", line_color="white",
                              annotation_text=f"Avg Price: {avg_price_val:.0f}",
                              annotation_position="bottom right")

        st.plotly_chart(fig_scatter, use_container_width=True)



# ---- A/B Test Tab ----
with tab2:
    st.subheader("A/B Test Results")
    ab_summary = read_sql("SELECT * FROM ab_group_summary")
    st.dataframe(ab_summary)

    ab_lift = read_sql("SELECT * FROM ab_group_lift")
    st.dataframe(ab_lift)

    ab_neigh = read_sql("SELECT * FROM ab_neighborhood_summary")
    st.dataframe(ab_neigh)

# ---- Data Quality Tab ----
with tab3:
    st.subheader("Data Quality Metrics")
    dq = read_sql("SELECT * FROM data_quality_metrics")
    st.dataframe(dq)

    # Data Preview 
    st.subheader("Data Preview")
    df = read_sql("""
        SELECT id, host_name, name, number_of_reviews, price, reviews_per_month,
               minimum_nights, last_review, availability_365, room_type, neighbourhood
        FROM airbnb_kaggle LIMIT 200
    """)
    df = apply_filters(df)
    st.dataframe(df, use_container_width=True)