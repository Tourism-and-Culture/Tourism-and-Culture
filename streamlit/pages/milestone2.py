from datetime import date, datetime, timedelta
import io
import os
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
import streamlit as st
from supabase import create_client

# =====================================================================================
# PAGE CONFIG 
# =====================================================================================
st.set_page_config(
    page_title="Smart Tourism & Cultural Intelligence Platform - Milestone 2",
    layout="wide"
)

# =====================================================================================
# SUPABASE CREDENTIALS & CLIENT 
# =====================================================================================
try:
    if "supabase" in st.secrets:
        SUPABASE_URL = st.secrets["supabase"].get("SUPABASE_URL") or st.secrets["supabase"].get("url")
        SUPABASE_KEY = st.secrets["supabase"].get("SUPABASE_KEY") or st.secrets["supabase"].get("key")
    else:
        SUPABASE_URL = st.secrets.get("SUPABASE_URL")
        SUPABASE_KEY = st.secrets.get("SUPABASE_KEY")
        
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise KeyError("Missing Supabase URL or Key in secrets.")
except Exception as e:
    st.error("⚠️ Error loading data from Supabase: Supabase credentials not configured in Streamlit secrets.")
    st.stop()

@st.cache_resource
def init_supabase():
    try:
        client = create_client(SUPABASE_URL, SUPABASE_KEY)
        return client
    except Exception:
        return None

supabase = init_supabase()

# =====================================================================================
# HEADER BLOCK
# =====================================================================================
st.markdown(
    """
    <div style='text-align:center; padding-top: 0.5rem;'>
        <h1 style='font-family: Helvetica, Arial, sans-serif; font-weight: 700;
                    font-size: 2.6rem; margin-bottom: 0.2rem;'>
            Smart Tourism &amp; Cultural Intelligence Platform
        </h1>
        <h3 style='font-family: Helvetica, Arial, sans-serif; font-weight: 600;
                    font-size: 1.1rem; letter-spacing: 2px; color: #6b6b6b; margin: 0.2rem 0;'>
            MILESTONE 2
        </h3>
        <h4 style='font-family: Helvetica, Arial, sans-serif; font-weight: 400;
                    font-size: 1rem; color: #8a8a8a; margin-top: 0;'>
           Data Integration, Exploratory Analysis & Executive Intelligence
        </h4>
    </div>
    """,
    unsafe_allow_html=True
)
st.divider()

# =====================================================================================
# SIDEBAR FILTERS & CONTROLS
# =====================================================================================
st.sidebar.title("🎛️ Dashboard Controls")
st.sidebar.markdown("Configure global parameters and filters for the platform modules.")

st.sidebar.subheader("📅 Date Range Filter")
default_start = date(2019, 1, 1)
default_end = date(2022, 12, 31)
global_date_range = st.sidebar.date_input("Select Operating Window", value=(default_start, default_end), key="global_date_picker")

st.sidebar.subheader("📍 Regional Filter")
global_states = st.sidebar.multiselect(
    "Select States / Zones",
    options=["Delhi", "Karnataka", "Maharashtra", "Punjab", "Telangana", "Rajasthan", "Uttar Pradesh", "General"],
    default=["Delhi", "Karnataka", "Maharashtra", "Punjab", "Telangana", "General"],
    key="global_state_filter"
)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Tip:** Use the cache clear button below if datasets are updated.")
if st.sidebar.button("🧹 Clear Global Cache", key="sidebar_clear_cache"):
    st.cache_data.clear()
    st.success("Cache cleared!")


# =====================================================================================
# MODULE 1 — Mobility Access Index & Equity Analysis
# =====================================================================================
def render_module_1():
    st.title("🚍 Module 1: Mobility Access & Equity Dashboard")
    st.subheader("Mobility Access Index & Equity Analysis across Heritage Zones")

    @st.cache_data
    def load_data_m1():
        try:
            if supabase:
                transport_response = supabase.table("fact_heritage_transport").select("*").execute()
                location_response = supabase.table("dim_location").select("*").execute()
                transport_df = pd.DataFrame(transport_response.data) if transport_response and transport_response.data else pd.DataFrame()
                locations_df = pd.DataFrame(location_response.data) if location_response and location_response.data else pd.DataFrame()
                return transport_df, locations_df
        except Exception:
            pass
        return pd.DataFrame(), pd.DataFrame()

    transport, locations = load_data_m1()

    if transport.empty or locations.empty:
        transport = pd.DataFrame({
            "location_id": [1, 2, 3, 4, 5],
            "stand_name": ["Qutab Minar Metro Exit", "Red Fort Hub", "India Gate Stand", "Lotus Temple Stand", "Humayun's Tomb Hub"],
            "vehicles_available": [12, 25, 18, 10, 15],
            "trips_completed": [45, 95, 60, 30, 50],
            "demand_level": ["high", "medium", "high", "low", "medium"]
        })
        locations = pd.DataFrame({
            "location_id": [1, 2, 3, 4, 5],
            "state": ["Delhi", "Delhi", "Delhi", "Delhi", "Delhi"],
            "city": ["New Delhi", "New Delhi", "New Delhi", "New Delhi", "New Delhi"],
            "latitude": [28.5244, 28.6562, 28.6129, 28.5535, 28.5933],
            "longitude": [77.1855, 77.2410, 77.2295, 77.2588, 77.2507]
        })

    transport["vehicles_available"] = pd.to_numeric(transport.get("vehicles_available", 0), errors="coerce").fillna(0)
    transport["trips_completed"] = pd.to_numeric(transport.get("trips_completed", 0), errors="coerce").fillna(0)
    transport["demand_level"] = transport.get("demand_level", "medium").astype(str).str.lower().str.strip()

    demand_map = {"low": 30, "medium": 60, "high": 100}
    transport["demand_score"] = transport["demand_level"].map(demand_map).fillna(60)

    transport["location_id"] = transport["location_id"].astype(str)
    locations["location_id"] = locations["location_id"].astype(str)

    zone = (
        transport.groupby(["location_id", "stand_name"], as_index=False)
        .agg(
            vehicles_available=("vehicles_available", "sum"),
            trips_completed=("trips_completed", "sum"),
            demand_score=("demand_score", "mean")
        )
    )

    max_vehicle = zone["vehicles_available"].max()
    zone["supply_score"] = (zone["vehicles_available"] / max_vehicle * 100) if max_vehicle > 0 else 0

    zone["trips_per_vehicle"] = np.where(zone["vehicles_available"] > 0, zone["trips_completed"] / zone["vehicles_available"], 0)
    max_usage = zone["trips_per_vehicle"].max()
    zone["usage_score"] = (zone["trips_per_vehicle"] / max_usage * 100) if max_usage > 0 else 0

    zone["Mobility_Access_Index"] = (
        0.30 * zone["supply_score"] + 0.30 * zone["usage_score"] + 0.40 * zone["demand_score"]
    ).round(2)

    def equity_category(score):
        if score >= 70:
            return "Well Connected"
        elif score >= 40:
            return "Moderately Connected"
        else:
            return "Underserved"

    zone["Equity_Category"] = zone["Mobility_Access_Index"].apply(equity_category)

    required_location_columns = ["location_id", "state", "city", "latitude", "longitude"]
    available_location_columns = [col for col in required_location_columns if col in locations.columns]
    locations_small = locations[available_location_columns].drop_duplicates("location_id")
    zone = zone.merge(locations_small, on="location_id", how="left")

    total_zones = zone["location_id"].nunique()
    well_connected_count = zone[zone["Equity_Category"] == "Well Connected"]["location_id"].nunique()
    underserved_count = zone[zone["Equity_Category"] == "Underserved"]["location_id"].nunique()
    average_index = round(zone["Mobility_Access_Index"].mean(), 2)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Heritage Zones", total_zones)
    col2.metric("Average Access Index", average_index)
    col3.metric("Well Connected", well_connected_count)
    col4.metric("Underserved", underserved_count)

    st.divider()

    st.header("1. Monument Accessibility & Equity Index")
    index_table = zone[["location_id", "stand_name", "Mobility_Access_Index", "Equity_Category"]].sort_values("Mobility_Access_Index", ascending=False)
    st.dataframe(index_table, use_container_width=True, hide_index=True)

    fig_index = px.bar(
        zone.sort_values("Mobility_Access_Index", ascending=False),
        x="stand_name",
        y="Mobility_Access_Index",
        color="Equity_Category",
        title="Monument Accessibility & Equity Index",
        labels={"stand_name": "Heritage Zone", "Mobility_Access_Index": "Mobility Access Index", "Equity_Category": "Equity Category"}
    )
    fig_index.add_hline(y=70, line_dash="dash", annotation_text="Well Connected")
    fig_index.add_hline(y=40, line_dash="dash", annotation_text="Moderately Connected")
    fig_index.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_index, use_container_width=True, key="m1_bar_chart")

    csv_data_m1 = zone.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Mobility Access Index CSV",
        data=csv_data_m1,
        file_name="mobility_access_equity_index.csv",
        mime="text/csv",
        key="download_m1_csv"
    )
    st.caption("Module 1 - Mobility Access Index & Equity Dashboards")
    return zone


# =====================================================================================
# MODULE 2 — Executive Intelligence Dashboard
# =====================================================================================
def render_module_2():
    st.title("📈 Module 2: Executive Intelligence Dashboard")
    st.subheader("High-Level Overview & Mobility Health Analytics")

    @st.cache_data(ttl=300)
    def load_data_m2():
        try:
            if supabase:
                response = supabase.table("view_transport_tourism_summary").select("*").execute()
                if response and response.data:
                    return pd.DataFrame(response.data)
        except Exception:
            pass
        
        try:
            if supabase:
                response = supabase.table("fact_heritage_transport").select("*").execute()
                if response and response.data:
                    return pd.DataFrame(response.data)
        except Exception:
            pass

        return pd.DataFrame({
            "trip_date": pd.date_range(start="2022-01-01", periods=50),
            "state": ["Delhi", "Karnataka", "Maharashtra", "Punjab", "Telangana"] * 10,
            "city": ["New Delhi", "Bengaluru", "Mumbai", "Amritsar", "Hyderabad"] * 10,
            "stand_name": ["Qutab Minar Metro", "Mysore Palace Hub", "Gateway of India", "Golden Temple Stand", "Charminar Station"] * 10,
            "trips_completed": np.random.randint(20, 100, 50),
            "vehicles_available": np.random.randint(10, 40, 50),
            "avg_travel_time_min": np.random.uniform(25.0, 60.0, 50),
            "on_time_pct": np.random.uniform(80.0, 98.0, 50)
        })

    raw_df = load_data_m2()
    if raw_df.empty:
        st.warning("No data found in Supabase tables for Module 2.")
        return pd.DataFrame()

    df = raw_df.copy()
    
    if "trip_date" not in df.columns:
        df["trip_date"] = pd.date_range(start="2022-01-01", periods=len(df))
    df["trip_date"] = pd.to_datetime(df["trip_date"], errors="coerce")
    df = df.dropna(subset=["trip_date"])

    if "trips_completed" not in df.columns:
        df["trips_completed"] = 50
    df["trips_completed"] = pd.to_numeric(df["trips_completed"], errors="coerce").fillna(0)

    if "vehicles_available" not in df.columns:
        df["vehicles_available"] = 20
    df["vehicles_available"] = pd.to_numeric(df["vehicles_available"], errors="coerce").fillna(0)

    if "avg_travel_time_min" not in df.columns:
        df["avg_travel_time_min"] = 40.0
    df["avg_travel_time_min"] = pd.to_numeric(df["avg_travel_time_min"], errors="coerce").fillna(40.0)

    if "on_time_pct" not in df.columns:
        df["on_time_pct"] = 85.0
    df["on_time_pct"] = pd.to_numeric(df["on_time_pct"], errors="coerce").fillna(85.0)

    for col in ["state", "city", "stand_name"]:
        if col not in df.columns:
            df[col] = "General"
        df[col] = df[col].astype(str).str.strip()

    def classify_mode(name):
        n = str(name).lower()
        if "metro" in n:
            return "Metro"
        elif "bus" in n or "isbt" in n:
            return "Bus"
        else:
            return "Others"

    if "transport_mode" not in df.columns:
        df["transport_mode"] = df["stand_name"].apply(classify_mode)
    else:
        df["transport_mode"] = df["transport_mode"].astype(str).str.strip()

    if not df.empty and not df["trip_date"].isna().all():
        min_dt = df["trip_date"].min().date()
        max_dt = df["trip_date"].max().date()
    else:
        min_dt, max_dt = date(2022, 1, 1), date(2022, 12, 31)

    start_date, end_date = global_date_range if isinstance(global_date_range, tuple) and len(global_date_range) == 2 else (min_dt, max_dt)
    
    mask = (df["trip_date"].dt.date >= start_date) & (df["trip_date"].dt.date <= end_date)
    if global_states:
        mask &= df["state"].isin(global_states)

    filtered_df = df.loc[mask].copy()
    if filtered_df.empty:
        filtered_df = df.copy()

    total_trips = int(filtered_df["trips_completed"].sum())
    total_weighted_time = (filtered_df["avg_travel_time_min"] * filtered_df["trips_completed"]).sum()
    avg_travel_time = total_weighted_time / total_trips if total_trips > 0 else 0.0

    total_weighted_on_time = (filtered_df["on_time_pct"] * filtered_df["trips_completed"]).sum()
    on_time_performance = total_weighted_on_time / total_trips if total_trips > 0 else 0.0

    target_travel_time = 45.0
    travel_efficiency = min(target_travel_time / avg_travel_time * 100, 100) if avg_travel_time > 0 else 100.0
    health_score = (0.60 * on_time_performance) + (0.40 * travel_efficiency)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Trips", f"{total_trips:,}")
    k2.metric("Average Travel Time", f"{avg_travel_time:.1f} min")
    k3.metric("On-Time Performance", f"{on_time_performance:.1f}%")
    k4.metric("Mobility Health Score", f"{health_score:.1f} / 100")

    st.divider()

    col_left, col_right = st.columns(2)
    with col_left:
        st.header("Daily Trip Trends")
        daily_trend = (
            filtered_df.groupby(filtered_df["trip_date"].dt.date, as_index=False)["trips_completed"]
            .sum()
            .rename(columns={"trip_date": "Date", "trips_completed": "Completed Trips"})
        )
        fig_line = px.line(
            daily_trend, x="Date", y="Completed Trips", markers=True, title="Trip Volume Over Time", color_discrete_sequence=["#2563EB"]
        )
        fig_line.update_layout(xaxis_title="Date", yaxis_title="Trips Completed")
        st.plotly_chart(fig_line, use_container_width=True, key="m2_line_chart")

    with col_right:
        st.header("Transport Mode Share")
        mode_share = (
            filtered_df.groupby("transport_mode", as_index=False)["trips_completed"]
            .sum()
            .rename(columns={"trips_completed": "Completed Trips"})
        )
        fig_pie = px.pie(
            mode_share, names="transport_mode", values="Completed Trips", hole=0.55, title="Share of Trips by Transport Mode", color_discrete_sequence=px.colors.qualitative.Prism
        )
        fig_pie.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig_pie, use_container_width=True, key="m2_pie_chart")

    st.divider()
    st.header("Zone & City Mobility Performance")
    summary_table = (
        filtered_df.groupby(["state", "city", "transport_mode"], as_index=False)
        .agg(
            Total_Trips=("trips_completed", "sum"),
            Vehicles_Available=("vehicles_available", "sum"),
            Avg_Travel_Time_Min=("avg_travel_time_min", "mean"),
            On_Time_Pct=("on_time_pct", "mean")
        )
        .sort_values(by="Total_Trips", ascending=False)
    )
    summary_table["Avg_Travel_Time_Min"] = summary_table["Avg_Travel_Time_Min"].round(1)
    summary_table["On_Time_Pct"] = summary_table["On_Time_Pct"].round(1)
    st.dataframe(summary_table, use_container_width=True, hide_index=True)

    csv_export_m2 = summary_table.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Executive Summary CSV",
        data=csv_export_m2,
        file_name="executive_mobility_intelligence.csv",
        mime="text/csv",
        key="download_m2_csv"
    )
    st.caption("Module 2 - Executive Intelligence Dashboards & Mobility Health Analytics")
    return summary_table


# =====================================================================================
# RENDER MODULES IN SEQUENCE (MILESTONE 2 FOCUS)
# =====================================================================================
m1_data = render_module_1()
st.markdown("---")
m2_data = render_module_2()

st.caption("Smart Tourism & Cultural Intelligence Platform - Milestone 2 Final Suite")
