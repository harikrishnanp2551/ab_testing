import os
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import plotly.express as px
import numpy as np
from scipy import stats

import load_data
import run_pipeline

import streamlit as st
from sqlalchemy import create_engine

# Get credentials from Streamlit secrets
secrets = st.secrets["postgres"]


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
CONN_STR = f'postgresql://{secrets["DB_USER"]}:{secrets["PASSWORD"]}@{secrets["DB_HOST"]}:{secrets["DB_PORT"]}/{secrets["DB_NAME"]}'
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
    st.title("Feature Impact on Number of Reviews")

    st.markdown(
        """
        Since we don’t have real A/B experiments, we compare **categories of each feature directly**.  
        Outcome: **number_of_reviews** (proxy for engagement).  
        For binary/categorical features, we run Welch’s t-tests to see if differences are significant.  
        """
    )

    # Load data with engineered features
    df_feat = read_sql("""
        SELECT id, number_of_reviews,
               instant_bookable_flag, room_type_flag, cancellation_flag,
               price_bucket, service_fee_bucket, neighbourhood_group_flag
        FROM airbnb_kaggle
        WHERE number_of_reviews IS NOT NULL
    """)

    if df_feat.empty:
        st.warning("No data found. Please refresh pipeline and ensure abtest_tables.sql ran.")
    else:
        overview_rows = []

        def compare_groups(series, outcome, labels, feature_name):
            mask1, mask2 = (series == labels[0]), (series == labels[1])
            g1, g2 = outcome[mask1], outcome[mask2]
            mean1, mean2 = g1.mean(), g2.mean()
            lift = (mean2 - mean1) / mean1 * 100 if mean1 else np.nan
            p_val = np.nan
            if len(g1) >= 2 and len(g2) >= 2:
                _, p_val = stats.ttest_ind(g2, g1, equal_var=False, nan_policy="omit")
            return {
                "feature": feature_name,
                "group1": labels[0], "mean1": mean1, "n1": len(g1),
                "group2": labels[1], "mean2": mean2, "n2": len(g2),
                "lift_pct": lift,
                "p_value": p_val,
                "significant": p_val < 0.05 if not np.isnan(p_val) else False
            }

        # Features to test
        tests = [
            ("instant_bookable_flag", [True, False], "Instant Bookable"),
            ("room_type_flag", ["entire_home", "private_room"], "Room Type"),
            ("cancellation_flag", ["flexible", "strict"], "Cancellation Policy"),
            ("price_bucket", ["<100", ">=100"], "Price Bucket"),
            ("service_fee_bucket", ["below_median", "above_median"], "Service Fee"),
            ("neighbourhood_group_flag", ["Brooklyn", "Manhattan"], "Neighbourhood Group")
        ]

        for col, labels, name in tests:
            if all(lbl in df_feat[col].unique() for lbl in labels):
                overview_rows.append(compare_groups(df_feat[col], df_feat["number_of_reviews"], labels, name))

        overview_df = pd.DataFrame(overview_rows).sort_values(by="p_value")

        st.subheader("Overview of Feature Impacts")
        st.dataframe(
            overview_df.style.format({
                "mean1": "{:.2f}", "mean2": "{:.2f}",
                "lift_pct": "{:.1f}", "p_value": "{:.3g}"
            }),
            use_container_width=True
        )

        st.markdown(
            """
            ### Methodology  
            * **Direct comparisons** between feature categories  
            * **Outcome**: number_of_reviews  
            * **Test**: Welch’s t-test (robust to unequal variances)  
            * **Lift**: relative % change from group1 → group2  
            * **Significance**: p < 0.05  
            """
        )

        sig_df = overview_df[overview_df["significant"]]
        if not sig_df.empty:
            st.subheader("Significant Findings")
            st.write(sig_df[["feature", "group1", "mean1", "group2", "mean2", "lift_pct", "p_value"]])

            for _, row in sig_df.head(2).iterrows():
                col_name = tests[[t[2] for t in tests].index(row["feature"])][0]
                labels = [row["group1"], row["group2"]]
                subset = df_feat[df_feat[col_name].isin(labels)]
                fig = px.box(
                    subset, x=col_name, y="number_of_reviews", points="all",
                    title=f"Number of Reviews by {row['feature']}"
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No statistically significant differences at p < 0.05.")

                # Narrative summary
        st.markdown("### Narrative Summary")
        if not sig_df.empty:
            insights = []
            for _, row in sig_df.iterrows():
                direction = "more" if row["lift_pct"] > 0 else "fewer"
                insights.append(
                    f"- **{row['feature']}**: {row['group2']} listings have "
                    f"{abs(row['lift_pct']):.1f}% {direction} reviews than {row['group1']} (p={row['p_value']:.3g})."
                )
            st.markdown("\n".join(insights))
            st.markdown(
                "👉 Overall: Price and Neighbourhood often show significant differences, "
                "while Instant Bookable, Cancellation Policy, Room Type, and Service Fee tend not to."
            )
        else:
            st.markdown("No feature shows statistically significant differences. Many effects may be too small to detect.")


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