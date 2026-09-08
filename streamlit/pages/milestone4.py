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
    page_title="Smart Tourism & Cultural Intelligence Platform",
    layout="wide"
)

# =====================================================================================
# SUPABASE CREDENTIALS & CLIENT
# =====================================================================================
SUPABASE_URL = st.secrets.get("SUPABASE_URL")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY")

@st.cache_resource
def init_supabase():
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
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
            MILESTONE 4
        </h3>
        <h4 style='font-family: Helvetica, Arial, sans-serif; font-weight: 400;
                    font-size: 1rem; color: #8a8a8a; margin-top: 0;'>
           Equity, Forecasting & Finalization
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
                transport_df = pd.DataFrame(transport_response.data)
                locations_df = pd.DataFrame(location_response.data)
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
                if response.data:
                    return pd.DataFrame(response.data)
        except Exception:
            pass
        
        try:
            if supabase:
                response = supabase.table("fact_heritage_transport").select("*").execute()
                if response.data:
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

    df = df.dropna(subset=["trip_date"])

    start_date, end_date = global_date_range if isinstance(global_date_range, tuple) and len(global_date_range) == 2 else (df["trip_date"].min().date(), df["trip_date"].max().date())
    
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
# MODULE 3 — Demand Forecasting, Anomaly Detection & Live Alerts
# =====================================================================================
def render_module_3():
    st.title("📊 Module 3: Demand Forecasting, Anomaly Detection & Live Alerts")
    st.markdown("Predicting future visitor footfall, catching weather/crowd anomalies, and tracking live system alerts.")

    @st.cache_data
    def load_data_m3():
        try:
            if supabase:
                response = supabase.table("view_booking_intelligence").select("*").execute()
                if response.data:
                    df = pd.DataFrame(response.data)
                    if not df.empty:
                        return df
        except Exception:
            pass

        dates = pd.date_range(start="2021-01-01", periods=60)
        np.random.seed(42)
        return pd.DataFrame({
            "booking_date": dates,
            "total_bookings": np.random.poisson(lam=1200, size=60),
            "avg_wait_time_mins": np.random.uniform(10.0, 35.0, size=60)
        })

    df = load_data_m3()
    if df.empty or "booking_date" not in df.columns:
        st.error("⚠️ No booking data available.")
        return pd.DataFrame()

    df["booking_date"] = pd.to_datetime(df["booking_date"])
    daily_demand = (
        df.groupby("booking_date")
        .agg(
            total_bookings=("total_bookings", "sum"),
            avg_wait_time=("avg_wait_time_mins", "mean") if "avg_wait_time_mins" in df.columns else ("total_bookings", "count"),
        )
        .reset_index()
        .sort_values("booking_date")
    )

    st.subheader("🚨 Live System & Weather Alerts")
    daily_demand["rolling_mean"] = daily_demand["total_bookings"].rolling(window=7, min_periods=1).mean()
    daily_demand["rolling_std"] = daily_demand["total_bookings"].rolling(window=7, min_periods=1).std().fillna(1)
    daily_demand["z_score"] = (daily_demand["total_bookings"] - daily_demand["rolling_mean"]) / daily_demand["rolling_std"]

    latest_row = daily_demand.iloc[-1]
    if latest_row["z_score"] < -1.5:
        st.error(f"⚠️ **Demand Drop Alert:** Significant visitor drop detected on {latest_row['booking_date'].strftime('%Y-%m-%d')} (Possible weather/rain disruption).")
    elif latest_row["z_score"] > 1.5:
        st.warning(f"🔥 **Surge Alert:** High visitor spike detected on {latest_row['booking_date'].strftime('%Y-%m-%d')}! Ensure transport stand readiness.")
    else:
        st.success("✅ **System Status Normal:** Visitor footfall and transport demand are within stable operating ranges.")

    st.markdown("---")
    st.subheader("📈 Visitor Footfall & Demand Forecasting")
    daily_demand["forecast"] = daily_demand["rolling_mean"] * 1.05
    daily_demand["upper_bound"] = daily_demand["rolling_mean"] + (1.5 * daily_demand["rolling_std"])
    daily_demand["lower_bound"] = daily_demand["rolling_mean"] - (1.5 * daily_demand["rolling_std"])

    fig_m3 = px.line(
        daily_demand,
        x="booking_date",
        y=["total_bookings", "forecast", "upper_bound", "lower_bound"],
        labels={"value": "Visitor Demand / Bookings", "booking_date": "Date", "variable": "Metric Type"},
        title="Demand Forecast with Upper & Lower Confidence Bounds",
    )
    fig_m3.update_layout(template="plotly_dark", legend_title_text="Legend", hovermode="x unified")
    st.plotly_chart(fig_m3, use_container_width=True, key="m3_forecast_chart")

    st.markdown("---")
    st.subheader("🔍 Anomaly Log & Statistical Flags")
    st.markdown("Dates flagged with unusual booking spikes or drops beyond standard deviation boundaries.")

    anomalies = daily_demand[abs(daily_demand["z_score"]) > 1.2].copy()
    anomalies["Anomaly Type"] = anomalies["z_score"].apply(lambda x: "🚨 Demand Drop" if x < 0 else "🔥 Surge Spike")
    anomalies["Date"] = anomalies["booking_date"].dt.strftime("%Y-%m-%d")

    if not anomalies.empty:
        st.dataframe(
            anomalies[["Date", "total_bookings", "rolling_mean", "Anomaly Type"]].rename(
                columns={"total_bookings": "Actual Bookings", "rolling_mean": "Expected Baseline"}
            ),
            use_container_width=True,
        )
    else:
        st.info("No major anomalies recorded in the active dataset window.")

    export_df = daily_demand.copy()
    export_df["booking_date"] = export_df["booking_date"].dt.strftime("%Y-%m-%d")

    csv_data_m3 = export_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Demand Forecast Summary CSV",
        data=csv_data_m3,
        file_name="demand_forecast_anomaly_summary.csv",
        mime="text/csv",
        key="download_m3_csv"
    )
    st.caption("Module 3 - Demand Forecasting, Anomaly Detection & Live System Alerts")
    return daily_demand


# =====================================================================================
# MODULE 4 — Performance Optimization & Reporting Suite
# =====================================================================================
def render_module_4():
    st.title("📊 Module 4: Performance Optimization & Reporting Suite")
    st.markdown("Review live transport datasets, monitor query caching performance, and download executive reports.")

    st.markdown("---")
    st.subheader("⚙️ System & Database Performance Optimization")
    col_opt1, col_opt2 = st.columns(2)
    with col_opt1:
        st.info("**Query Caching Status:** Active (@st.cache_data)")
        st.write("Database and file queries are cached with a 10-minute TTL to ensure zero lag and high-speed execution.")
    with col_opt2:
        if st.button("🧹 Clear App & Query Cache", key="m4_clear_cache"):
            st.cache_data.clear()
            st.success("Cache cleared successfully! Data reloaded.")

    @st.cache_data(ttl=600)
    def load_project_data_m4():
        try:
            if supabase:
                response = supabase.table("fact_heritage_transport").select("*").execute()
                if response.data:
                    return pd.DataFrame(response.data)
        except Exception:
            pass

        return pd.DataFrame({
            "trip_id": [1, 2, 3, 4, 5],
            "stand_name": ["Qutab Minar Metro Exit", "Red Fort Hub", "India Gate Stand", "Lotus Temple Stand", "Humayun's Tomb Hub"],
            "vehicles_available": [4, 23, 15, 8, 12],
            "trips_completed": [13, 45, 30, 22, 19],
            "demand_level": ["Balanced", "High", "Balanced", "Low", "Balanced"],
        })

    df_summary = load_project_data_m4()

    st.markdown("---")
    st.subheader("🚌 Heritage Transport & Mobility Performance Summary")
    st.write(f"Displaying {len(df_summary)} records from your project dataset.")
    st.dataframe(df_summary, use_container_width=True)

    st.markdown("---")
    st.subheader("📥 Automated Reporting Suite")
    col_csv, col_pdf = st.columns(2)

    with col_csv:
        st.markdown("### **CSV Data Export**")
        st.write("Export your exact project dataset records into a clean CSV spreadsheet.")
        csv_data_m4 = df_summary.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Heritage Transport CSV",
            data=csv_data_m4,
            file_name="heritage_transport_performance_report.csv",
            mime="text/csv",
            key="download_m4_csv"
        )

    with col_pdf:
        st.markdown("### **Executive PDF Report**")
        st.write("Generate a professionally formatted PDF document from your loaded records.")

        def generate_executive_pdf(dataframe):
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
            styles = getSampleStyleSheet()

            title_style = ParagraphStyle("ExecutiveTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=16, textColor=colors.HexColor("#1e293b"), spaceAfter=10)
            body_style = ParagraphStyle("ExecutiveBody", parent=styles["Normal"], fontName="Helvetica", fontSize=9, textColor=colors.HexColor("#334155"), spaceAfter=6)

            story = []
            story.append(Paragraph("Smart City Tourism Mobility - Executive Summary Report", title_style))
            story.append(Paragraph("Milestone 4: Heritage Transport Efficiency & Mobility Optimization", body_style))
            story.append(Spacer(1, 8))

            df_to_render = dataframe.head(15)
            table_data = [list(df_to_render.columns)] + df_to_render.values.tolist()
            num_cols = len(df_to_render.columns)
            col_width = 500 / num_cols if num_cols > 0 else 80
            col_widths = [col_width] * num_cols

            t = Table(table_data, colWidths=col_widths)
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 8),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 5),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f8fafc")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -1), 7),
                ("TOPPADDING", (0, 1), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 1), (-1, -1), 4),
            ]))
            story.append(t)
            doc.build(story)
            buffer.seek(0)
            return buffer.getvalue()

        try:
            pdf_text_data = generate_executive_pdf(df_summary)
            st.download_button(
                label="📑 Download Executive PDF",
                data=pdf_text_data,
                file_name="heritage_transport_executive_report.pdf",
                mime="application/pdf",
                key="download_m4_pdf"
            )
        except Exception as e:
            st.error(f"Error generating PDF: {e}")

    st.caption("Module 4 - Performance Optimization & Reporting Suite")
    return df_summary


# =====================================================================================
# RENDER ALL MODULES IN SEQUENCE
# =====================================================================================
m1_data = render_module_1()
st.markdown("---")
m2_data = render_module_2()
st.markdown("---")
m3_data = render_module_3()
st.markdown("---")
m4_data = render_module_4()

# =====================================================================================
# ENTIRE DASHBOARD REPORT SUITE (ALL MODULES CSV & PDF)
# =====================================================================================
st.markdown("---")
st.header("📦 Entire Dashboard Report Suite (Global Export)")
st.markdown("Download a consolidated master CSV or a multi-section executive PDF report covering **all four modules**.")

col_full_csv, col_full_pdf = st.columns(2)

with col_full_csv:
    st.markdown("### **Master Dashboard CSV Export**")
    st.write("Package summaries across Modules 1, 2, 3, and 4 into a single downloadable master CSV file.")

    def generate_master_csv(df_m1, df_m2, df_m3, df_m4):
        output = io.StringIO()
        output.write("=== MODULE 1: MOBILITY ACCESS & EQUITY SUMMARY ===\n")
        if isinstance(df_m1, pd.DataFrame) and not df_m1.empty:
            df_m1.to_csv(output, index=False)
        else:
            output.write("No data available\n")
        
        output.write("\n=== MODULE 2: EXECUTIVE INTELLIGENCE SUMMARY ===\n")
        if isinstance(df_m2, pd.DataFrame) and not df_m2.empty:
            df_m2.to_csv(output, index=False)
        else:
            output.write("No data available\n")

        output.write("\n=== MODULE 3: DEMAND FORECASTING SUMMARY ===\n")
        if isinstance(df_m3, pd.DataFrame) and not df_m3.empty:
            df_m3_copy = df_m3.copy()
            if "booking_date" in df_m3_copy.columns:
                df_m3_copy["booking_date"] = pd.to_datetime(df_m3_copy["booking_date"]).dt.strftime("%Y-%m-%d")
            df_m3_copy.to_csv(output, index=False)
        else:
            output.write("No data available\n")

        output.write("\n=== MODULE 4: PERFORMANCE OPTIMIZATION SUMMARY ===\n")
        if isinstance(df_m4, pd.DataFrame) and not df_m4.empty:
            df_m4.to_csv(output, index=False)
        else:
            output.write("No data available\n")

        return output.getvalue().encode("utf-8")

    try:
        master_csv_bytes = generate_master_csv(m1_data, m2_data, m3_data, m4_data)
        st.download_button(
            label="📥 Download Master Dashboard CSV (All Modules)",
            data=master_csv_bytes,
            file_name="smart_tourism_entire_dashboard_master.csv",
            mime="text/csv",
            key="download_entire_dashboard_csv"
        )
    except Exception as e:
        st.error(f"Error generating master CSV: {e}")

with col_full_pdf:
    st.markdown("### **Entire Dashboard PDF Report (All Modules)**")
    st.write("Generate a comprehensive multi-section PDF report capturing summaries across Modules 1, 2, 3, and 4.")
