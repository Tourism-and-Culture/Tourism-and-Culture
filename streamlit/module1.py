import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from supabase import create_client

# Page layout setup
st.set_page_config(page_title="Urban Pulse | Visit & Booking Intelligence", layout="wide")

st.title("🏛️ Module 1: Visit & Booking Intelligence")
st.write("Comprehensive analysis of hourly visitor demand, booking status, entry queue wait times, and site bottlenecks.")

SUPABASE_URL = st.secrets.get("MODULE1_SUPABASE_URL")
SUPABASE_KEY = st.secrets.get("MODULE1_SUPABASE_SERVICE_KEY")

# 1. Fetch and process data from Supabase with complete table joins
@st.cache_data
def load_module1_data():
    df_locations, df_bookings, df_attractions = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    if SUPABASE_URL and SUPABASE_KEY:
        try:
            supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
            df_locations = pd.DataFrame(supabase.table("dim_location").select("*").execute().data)
            df_bookings = pd.DataFrame(supabase.table("fact_tourist_bookings").select("*").execute().data)
            df_attractions = pd.DataFrame(supabase.table("fact_attractions").select("*").execute().data)
        except Exception:
            df_locations, df_bookings, df_attractions = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    # Merge bookings with location dimensions (cities, states)
    if not df_bookings.empty and not df_locations.empty:
        df_visits = pd.merge(df_bookings, df_locations, on="location_id", how="left")
    else:
        df_visits = df_bookings.copy()

    # Merge with attractions to get real monument/place names
    if not df_visits.empty and not df_attractions.empty and 'location_id' in df_attractions.columns:
        df_attr_unique = df_attractions.drop_duplicates(subset=['location_id'])
        df_visits = pd.merge(df_visits, df_attr_unique[['location_id', 'place_name']], on="location_id", how="left")

    if not df_visits.empty:
        if 'place_name' not in df_visits.columns:
            df_visits['place_name'] = "Heritage Site " + df_visits['location_id'].astype(str)
        else:
            df_visits['place_name'] = df_visits['place_name'].fillna("Heritage Site " + df_visits['location_id'].astype(str))

    # Parse hour of day cleanly as integers for Chart 1
    if not df_visits.empty and 'booking_time' in df_visits.columns:
        df_visits['hour'] = pd.to_datetime(df_visits['booking_time'], format='%H:%M:%S', errors='coerce').dt.hour.fillna(12).astype(int)
    else:
        df_visits['hour'] = 12

    # Map status fields for completion vs cancellation charts
    if not df_visits.empty and 'status' in df_visits.columns:
        df_visits['is_completed'] = (df_visits['status'] == 'Completed').astype(int)
        df_visits['is_cancelled'] = (df_visits['status'] == 'Cancelled').astype(int)
    else:
        df_visits['is_completed'] = 1
        df_visits['is_cancelled'] = 0

    if not df_visits.empty and 'wait_time_min' not in df_visits.columns:
        df_visits['wait_time_min'] = 25.0

    if not df_visits.empty and 'city' not in df_visits.columns:
        df_visits['city'] = "Unknown"

    # Guaranteed fallback for booking_id (used in Chart 4's groupby) so a missing
    # column here never crashes the app
    if not df_visits.empty and 'booking_id' not in df_visits.columns:
        df_visits['booking_id'] = df_visits.index.astype(str)

    return df_visits

df_visits = load_module1_data()

# 2. Sidebar Filters for Cities
st.sidebar.header("Module 1 Filters")

if not df_visits.empty and 'city' in df_visits.columns:
    city_options = sorted(df_visits['city'].dropna().unique().tolist())
    selected_cities = st.sidebar.multiselect(
        "Select Cities / Locations",
        options=city_options,
        default=city_options[:10]
    )
else:
    selected_cities = []

# Filter dataset
filtered_visits = df_visits[df_visits['city'].isin(selected_cities)] if selected_cities else df_visits
if filtered_visits.empty:
    filtered_visits = df_visits

# 3. Key Performance Indicators (KPIs)
total_bookings_count = len(filtered_visits)
completed_count = filtered_visits['is_completed'].sum() if 'is_completed' in filtered_visits.columns else 0
avg_wait = filtered_visits['wait_time_min'].mean() if 'wait_time_min' in filtered_visits.columns else 0.0
cancellation_rate = (filtered_visits['is_cancelled'].sum() / total_bookings_count * 100) if total_bookings_count > 0 else 0.0

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Total Bookings Volume", f"{total_bookings_count:,}")
kpi2.metric("Completed Visits", f"{completed_count:,}")
kpi3.metric("Avg Entry Queue Wait Time", f"{avg_wait:.1f} mins")
kpi4.metric("Avg Cancellation Rate", f"{cancellation_rate:.1f}%")

st.markdown("---")

# Chart 1: Hourly Visitor Demand (Fixed with categorical/discrete hour ticks)
st.subheader("⏰ 1. Hourly Visitor Demand & Peak Arrival Windows")
if not filtered_visits.empty and 'hour' in filtered_visits.columns:
    df_hourly = filtered_visits.groupby("hour").size().reset_index(name="visitor_count")
    fig_hourly = px.area(
        df_hourly,
        x="hour",
        y="visitor_count",
        markers=True,
        title="Visitor Arrival Volume Across Operating Hours",
        labels={"hour": "Hour of Day (24h)", "visitor_count": "Total Bookings"}
    )
    fig_hourly.update_xaxes(type='category', dtick=1)
    st.plotly_chart(fig_hourly, use_container_width=True)
else:
    st.info("Hourly breakdown data unavailable.")

st.markdown("---")

# Chart 2: Booking Completion vs. Cancellation Status by Monument
st.subheader("📊 2. Booking Completion vs. Cancellation by Monument")
if not filtered_visits.empty and 'place_name' in filtered_visits.columns:
    df_status = filtered_visits.groupby("place_name")[['is_completed', 'is_cancelled']].sum().reset_index().head(20)
    df_status_melted = df_status.melt(
        id_vars=["place_name"],
        value_vars=["is_completed", "is_cancelled"],
        var_name="Booking_Status",
        value_name="Count"
    )
    df_status_melted['Booking_Status'] = df_status_melted['Booking_Status'].replace({
        'is_completed': 'completed_visits',
        'is_cancelled': 'cancelled_visits'
    })
    fig_status = px.bar(
        df_status_melted,
        x="place_name",
        y="Count",
        color="Booking_Status",
        barmode="group",
        title="Completed Visits vs Cancellations Across Heritage Sites",
        labels={"place_name": "Heritage Site", "Count": "Number of Visitors"}
    )
    st.plotly_chart(fig_status, use_container_width=True)
else:
    st.info("Monument status data unavailable.")

st.markdown("---")

# Chart 3: Entry Queue Bottlenecks & Wait Times
st.subheader("⌛ 3. Entry Queue Congestion & Wait Times by Site")
if not filtered_visits.empty and 'place_name' in filtered_visits.columns and 'wait_time_min' in filtered_visits.columns:
    df_queue = filtered_visits.groupby("place_name")["wait_time_min"].mean().reset_index().head(20)
    fig_queue = px.bar(
        df_queue,
        x="place_name",
        y="wait_time_min",
        color="wait_time_min",
        title="Average Queue Wait Times (Detecting Bottlenecks at Marquee Sites)",
        labels={"place_name": "Heritage Site", "wait_time_min": "Avg Wait Time (Minutes)"}
    )
    st.plotly_chart(fig_queue, use_container_width=True)
else:
    st.info("Queue wait time data unavailable.")

st.markdown("---")

# Chart 4: Cancellation Rate Risk Analysis Scatter (Fixed X-axis scaling)
st.subheader("⚠️ 4. Cancellation Rate Risk Analysis by Location")
if not filtered_visits.empty and 'place_name' in filtered_visits.columns:
    df_loc_summary = filtered_visits.groupby(["place_name", "city"]).agg(
        total_bookings=('booking_id', 'count'),
        cancellation_rate=('is_cancelled', lambda x: (x.sum() / len(x)) * 100)
    ).reset_index()

    fig_cancel = px.scatter(
        df_loc_summary,
        x="total_bookings",
        y="cancellation_rate",
        color="city",
        hover_data=["place_name"],
        title="Total Bookings vs. Cancellation Rate (%)",
        labels={"total_bookings": "Total Bookings", "cancellation_rate": "Cancellation Rate (%)"}
    )
    fig_cancel.update_xaxes(dtick=1)
    st.plotly_chart(fig_cancel, use_container_width=True)
else:
    st.info("Cancellation rate data unavailable.")
