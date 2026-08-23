import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from supabase import create_client

def render_module_1():
    st.header("🏛️ Module 1: Visit & Booking Intelligence")
    st.write("Comprehensive analysis of hourly visitor demand, booking status, entry queue wait times, and site bottlenecks.")

    SUPABASE_URL = st.secrets.get("MODULE1_SUPABASE_URL", "https://megkqranyjwtlmfnejky.supabase.co")
    SUPABASE_KEY = st.secrets.get("MODULE1_SUPABASE_SERVICE_KEY", None)

    @st.cache_data
    def load_module1_data():
        df_visits = pd.DataFrame()

        if SUPABASE_KEY:
            try:
                supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
                response = supabase.table("view_booking_intelligence").select("*").execute()
                df_visits = pd.DataFrame(response.data)
            except Exception:
                df_visits = pd.DataFrame()

        if df_visits.empty:
            return pd.DataFrame()

        if 'place_name' not in df_visits.columns:
            df_visits['place_name'] = "Heritage Site " + df_visits['location_id'].astype(str)
        else:
            df_visits['place_name'] = df_visits['place_name'].fillna("Heritage Site " + df_visits['location_id'].astype(str))

        if 'city' not in df_visits.columns:
            df_visits['city'] = "Unknown"
        else:
            df_visits['city'] = df_visits['city'].fillna("Unknown")

        if 'hour' not in df_visits.columns:
            df_visits['hour'] = 12
        else:
            df_visits['hour'] = pd.to_numeric(df_visits['hour'], errors='coerce').fillna(12).astype(int)

        df_visits['total_bookings'] = pd.to_numeric(df_visits.get('total_bookings', 1), errors='coerce').fillna(1)
        df_visits['completed_visits'] = pd.to_numeric(df_visits.get('completed_visits', 1), errors='coerce').fillna(1)
        df_visits['cancelled_visits'] = pd.to_numeric(df_visits.get('cancelled_visits', 0), errors='coerce').fillna(0)
        df_visits['avg_wait_time_mins'] = pd.to_numeric(df_visits.get('avg_wait_time_mins', 25.0), errors='coerce').fillna(25.0)

        return df_visits

    df_visits = load_module1_data()

    st.sidebar.header("Module 1 Filters")

    if not df_visits.empty and 'city' in df_visits.columns:
        city_options = sorted(df_visits['city'].dropna().unique().tolist())
        selected_cities = st.sidebar.multiselect(
            "Select Cities / Locations (Module 1)",
            options=city_options,
            default=city_options,
            key="m1_city_filter"
        )
    else:
        selected_cities = []

    filtered_visits = df_visits[df_visits['city'].isin(selected_cities)] if selected_cities else df_visits
    if filtered_visits.empty:
        filtered_visits = df_visits

    total_bookings_count = filtered_visits['total_bookings'].sum()
    completed_count = filtered_visits['completed_visits'].sum()
    avg_wait = filtered_visits['avg_wait_time_mins'].mean()
    total_cancels = filtered_visits['cancelled_visits'].sum()
    cancellation_rate = (total_cancels / total_bookings_count * 100) if total_bookings_count > 0 else 0.0

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Total Bookings Volume", f"{int(total_bookings_count):,}")
    kpi2.metric("Completed Visits", f"{int(completed_count):,}")
    kpi3.metric("Avg Entry Queue Wait Time", f"{avg_wait:.1f} mins")
    kpi4.metric("Avg Cancellation Rate", f"{cancellation_rate:.1f}%")

    st.markdown("---")

    st.subheader("⏰ 1. Hourly Visitor Demand & Peak Arrival Windows")
    if not filtered_visits.empty and 'hour' in filtered_visits.columns:
        df_hourly = filtered_visits.groupby("hour")["total_bookings"].sum().reset_index(name="visitor_count")
        fig_hourly = px.area(
            df_hourly,
            x="hour",
            y="visitor_count",
            markers=True,
            title="Visitor Arrival Volume Across Operating Hours",
            labels={"hour": "Hour of Day (24h)", "visitor_count": "Total Bookings"}
        )
        fig_hourly.update_xaxes(type='category', dtick=1)
        st.plotly_chart(fig_hourly, use_container_width=True, key="m1_hourly")

    st.markdown("---")

    st.subheader("📊 2. Booking Completion vs. Cancellation by Monument")
    if not filtered_visits.empty and 'place_name' in filtered_visits.columns:
        df_status = filtered_visits.groupby("place_name")[['completed_visits', 'cancelled_visits']].sum().reset_index().head(20)
        df_status_melted = df_status.melt(
            id_vars=["place_name"],
            value_vars=["completed_visits", "cancelled_visits"],
            var_name="Booking_Status",
            value_name="Count"
        )
        fig_status = px.bar(
            df_status_melted,
            x="place_name",
            y="Count",
            color="Booking_Status",
            barmode="group",
            title="Completed Visits vs Cancellations Across Heritage Sites",
            labels={"place_name": "Heritage Site", "Count": "Number of Visitors"}
        )
        st.plotly_chart(fig_status, use_container_width=True, key="m1_status")

    st.markdown("---")

    st.subheader("⌛ 3. Entry Queue Congestion & Wait Times by Site")
    if not filtered_visits.empty and 'place_name' in filtered_visits.columns:
        df_queue = filtered_visits.groupby("place_name")["avg_wait_time_mins"].mean().reset_index().head(20)
        fig_queue = px.bar(
            df_queue,
            x="place_name",
            y="avg_wait_time_mins",
            color="avg_wait_time_mins",
            title="Average Queue Wait Times (Detecting Bottlenecks at Marquee Sites)",
            labels={"place_name": "Heritage Site", "avg_wait_time_mins": "Avg Wait Time (Minutes)"}
        )
        st.plotly_chart(fig_queue, use_container_width=True, key="m1_queue")

    st.markdown("---")

    st.subheader("⚠️ 4. Cancellation Rate Risk Analysis by Location")
    if not filtered_visits.empty and 'place_name' in filtered_visits.columns:
        df_loc_summary = filtered_visits.groupby(["place_name", "city"]).agg(
            total_bookings=('total_bookings', 'sum'),
            cancelled_bookings=('cancelled_visits', 'sum')
        ).reset_index()
        
        df_loc_summary['cancellation_rate'] = np.where(
            df_loc_summary['total_bookings'] > 0,
            (df_loc_summary['cancelled_bookings'] / df_loc_summary['total_bookings']) * 100,
            0.0
        )

        fig_cancel = px.scatter(
            df_loc_summary,
            x="total_bookings",
            y="cancellation_rate",
            color="city",
            size="total_bookings",
            hover_data=["place_name"],
            title="Total Bookings vs. Cancellation Rate (%)",
            labels={"total_bookings": "Total Bookings", "cancellation_rate": "Cancellation Rate (%)"}
        )
        st.plotly_chart(fig_cancel, use_container_width=True, key="m1_cancel_risk")
