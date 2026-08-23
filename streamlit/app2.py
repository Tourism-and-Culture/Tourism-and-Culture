import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from supabase import create_client

# =====================================================================================
# PAGE CONFIG 
# =====================================================================================
st.set_page_config(
    page_title="Smart Tourism & Cultural Intelligence Platform",
    layout="wide"
)

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
            MILESTONE 3
        </h3>
        <h4 style='font-family: Helvetica, Arial, sans-serif; font-weight: 400;
                    font-size: 1rem; color: #8a8a8a; margin-top: 0;'>
            Demand Intelligence &amp; Visitor Mobility
        </h4>
    </div>
    """,
    unsafe_allow_html=True
)
st.divider()

# =====================================================================================
# MODULE 1 — Visit & Booking Intelligence 
# =====================================================================================
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

        # Ensure numeric types for proper aggregation
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

    # Chart 1: Hourly Visitor Demand
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

    # Chart 2: Booking Completion vs. Cancellation Status by Monument
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

    # Chart 3: Entry Queue Bottlenecks & Wait Times
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

    # Chart 4: Cancellation Rate Risk Analysis Scatter (FIXED)
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

# =====================================================================================
# MODULE 2 — Last-Mile Heritage Circuit Analytics
# =====================================================================================
def render_module_2():
    st.header("🏛️ Module 2: Last-Mile Heritage Circuit Analytics")
    st.caption("Member 2: Madhusri Gone | Hyderabad Heritage Circuit Live Telemetry")

    SUPABASE_URL = st.secrets.get("MODULE2_SUPABASE_URL", "https://megkqranyjwtlmfnejky.supabase.co")
    SUPABASE_KEY = st.secrets.get("MODULE2_SUPABASE_ANON_KEY", "sb_publishable_Y-wPElO-p0-zjmtKKiqSLQ_Z8YiIwR5")

    @st.cache_data(ttl=60)
    def load_data_m2():
        try:
            supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
            res = supabase.table("fact_heritage_transport").select("*").execute()
            df = pd.DataFrame(res.data)
            if df.empty:
                raise ValueError("Empty data returned")
            return df
        except Exception:
            return pd.DataFrame({
                "stand_name": [
                    "Charminar Gate Hub",
                    "Chowmahalla Palace",
                    "Mecca Masjid Stand",
                    "Salar Jung Museum",
                    "High Court Walk",
                    "Badshahi Ashurkhana"
                ],
                "supply": [24, 18, 30, 28, 14, 8],
                "demand": [38, 12, 42, 15, 16, 19],
                "capacity": [40, 25, 45, 35, 20, 20],
                "lat": [17.3616, 17.3578, 17.3605, 17.3714, 17.3688, 17.3662],
                "lon": [78.4747, 78.4717, 78.4735, 78.4804, 78.4732, 78.4770]
            })

    df = load_data_m2()

    if "stand_name" not in df.columns:
        if "pickup_location" in df.columns:
            df["stand_name"] = df["pickup_location"]
        elif "station_name" in df.columns:
            df["stand_name"] = df["station_name"]
        else:
            df["stand_name"] = "Stand " + df.index.astype(str)

    if "supply" not in df.columns:
        df["supply"] = [24, 18, 30, 28, 14, 8][:len(df)] if len(df) <= 6 else 20
    if "demand" not in df.columns:
        df["demand"] = [38, 12, 42, 15, 16, 19][:len(df)] if len(df) <= 6 else 15
    if "capacity" not in df.columns:
        df["capacity"] = 35

    coords_lookup = {
        "Charminar": (17.3616, 78.4747),
        "Chowmahalla": (17.3578, 78.4717),
        "Mecca Masjid": (17.3605, 78.4735),
        "Salar Jung": (17.3714, 78.4804),
        "High Court": (17.3688, 78.4732),
        "Badshahi": (17.3662, 78.4770)
    }

    def resolve_coords(name):
        for k, v in coords_lookup.items():
            if k.lower() in str(name).lower():
                return v
        return (17.3616, 78.4747)

    if "lat" not in df.columns or "lon" not in df.columns:
        coords = df["stand_name"].apply(resolve_coords)
        df["lat"] = [c[0] for c in coords]
        df["lon"] = [c[1] for c in coords]

    stand_summary = df.groupby("stand_name").agg({
        "supply": "mean",
        "demand": "mean",
        "capacity": "mean",
        "lat": "first",
        "lon": "first"
    }).reset_index()

    stand_summary["utilization_pct"] = ((stand_summary["demand"] / stand_summary["capacity"]) * 100).round(1)

    stand_summary["alert_status"] = stand_summary["utilization_pct"].apply(
        lambda x: "Shortage Alert" if x >= 80 else ("Surplus Alert" if x <= 25 else "Normal")
    )

    total_trips_val = int(stand_summary["demand"].sum())
    active_stands_val = int(len(stand_summary))
    alerts_count_val = int((stand_summary["alert_status"] != "Normal").sum())

    col1, col2, col3 = st.columns(3)
    col1.metric(label="Total Trips", value=total_trips_val)
    col2.metric(label="Active Stands", value=active_stands_val)
    col3.metric(label="Rebalance Alerts", value=alerts_count_val)

    st.divider()

    c_map, c_chart = st.columns([1, 1])

    with c_map:
        st.subheader("Stand Utilization Map")
        map_fig = px.scatter_map(
            stand_summary,
            lat="lat",
            lon="lon",
            hover_name="stand_name",
            hover_data={"utilization_pct": True, "alert_status": True, "lat": False, "lon": False},
            color="utilization_pct",
            size="demand",
            color_continuous_scale="RdYlGn_r",
            size_max=20,
            zoom=13.2,
            map_style="open-street-map"
        )
        map_fig.update_layout(margin=dict(l=0, r=0, t=20, b=0), height=380)
        st.plotly_chart(map_fig, width="stretch", key="m2_map")

    with c_chart:
        st.subheader("Stand Supply vs. Demand")
        bar_fig = go.Figure()
        bar_fig.add_trace(go.Bar(
            x=stand_summary["stand_name"],
            y=stand_summary["supply"],
            name="Supply",
            marker_color="#1f77b4"
        ))
        bar_fig.add_trace(go.Bar(
            x=stand_summary["stand_name"],
            y=stand_summary["demand"],
            name="Demand",
            marker_color="#d62728"
        ))
        bar_fig.update_layout(
            barmode="group",
            height=380,
            margin=dict(l=10, r=10, t=20, b=0),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            xaxis_tickangle=-25
        )
        st.plotly_chart(bar_fig, width="stretch", key="m2_bar")

    st.divider()
    st.subheader("Stand Telemetry Overview")
    st.dataframe(
        stand_summary[["stand_name", "supply", "demand", "capacity", "utilization_pct", "alert_status"]],
        hide_index=True,
        width="stretch"
    )


# =====================================================================================
# MODULE 3 — Modal Substitution Analysis
# =====================================================================================
def render_module_3():
    st.header("🚍 Module 3: Modal Substitution Analysis")
    st.caption("Analysis of visitor transport patterns and simulated transport shifts under infrastructure improvements.")

    SUPABASE_URL = st.secrets.get("MODULE3_SUPABASE_URL")
    SUPABASE_KEY = st.secrets.get("MODULE3_SUPABASE_KEY")

    @st.cache_resource
    def get_supabase_m3():
        return create_client(SUPABASE_URL, SUPABASE_KEY)

    @st.cache_data(ttl=600)
    def load_transport_data():
        if not SUPABASE_URL or not SUPABASE_KEY:
            return pd.DataFrame()
        try:
            supabase = get_supabase_m3()
            response = supabase.table("view_transport_tourism_summary").select("*").execute()
            return pd.DataFrame(response.data)
        except Exception:
            return pd.DataFrame()

    def identify_transport_mode(stand_name):
        if pd.isna(stand_name):
            return "Other"
        name = stand_name.lower()
        if "metro" in name:
            return "Metro"
        elif "isbt" in name or "bus" in name:
            return "Bus"
        elif "railway" in name or "train" in name:
            return "Rail"
        elif "taxi" in name or "cab" in name:
            return "Taxi"
        else:
            return "Other"

    if not SUPABASE_URL or not SUPABASE_KEY:
        st.warning("Module 3 Supabase credentials not configured.")
        return

    df = load_transport_data()
    if df.empty:
        st.warning("No transport data available.")
        return

    df["trips_completed"] = pd.to_numeric(df["trips_completed"], errors="coerce").fillna(0)
    df["vehicles_available"] = pd.to_numeric(df["vehicles_available"], errors="coerce").fillna(0)
    df["transport_mode"] = df["stand_name"].apply(identify_transport_mode)

    cities = sorted(df["city"].dropna().unique()) if 'city' in df.columns else []
    selected_city = st.selectbox("Select City (Module 3)", ["All Cities"] + cities, key="m3_city_filter")

    if selected_city != "All Cities":
        df = df[df["city"] == selected_city]

    mode_summary = df.groupby("transport_mode").agg(
        trips_completed=("trips_completed", "sum"),
        vehicles_available=("vehicles_available", "sum")
    ).reset_index()

    if mode_summary.empty or mode_summary["trips_completed"].sum() == 0:
        st.warning("No completed trips found for selection.")
        return

    total_trips = mode_summary["trips_completed"].sum()
    mode_summary["baseline_share"] = mode_summary["trips_completed"] / total_trips
    dominant_mode = mode_summary.sort_values("trips_completed", ascending=False).iloc[0]["transport_mode"]

    st.subheader("Infrastructure Improvement Simulation")
    improvement = st.slider("Infrastructure Improvement (%)", 0, 50, 20, 5, key="m3_improvement_slider")
    improvement_factor = improvement / 100

    max_vehicles = mode_summary["vehicles_available"].max()
    mode_summary["capacity_score"] = mode_summary["vehicles_available"] / max_vehicles if max_vehicles > 0 else 0
    mode_summary["simulation_weight"] = mode_summary["baseline_share"] * (1 + improvement_factor * mode_summary["capacity_score"])
    
    total_weight = mode_summary["simulation_weight"].sum()
    mode_summary["simulated_share"] = mode_summary["simulation_weight"] / total_weight if total_weight > 0 else mode_summary["baseline_share"]
    mode_summary["simulated_trips"] = mode_summary["simulated_share"] * total_trips

    transit_shift_index = 0.5 * (mode_summary["simulated_share"] - mode_summary["baseline_share"]).abs().sum() * 100

    col1, col2 = st.columns(2)
    col1.metric(label="🚍 Dominant Transit Mode", value=dominant_mode)
    col2.metric(label="🔄 Transit Shift Index", value=f"{transit_shift_index:.2f}%")

    st.divider()
    donut = px.pie(mode_summary, names="transport_mode", values="trips_completed", hole=0.55, title="Transport Mode Distribution")
    st.plotly_chart(donut, use_container_width=True, key="m3_donut")

# =====================================================================================
# MODULE 4 — Weather Sensitivity & Demand Elasticity 
# =====================================================================================
def render_module_4():
    st.header("🌧️ Module 4: Weather Sensitivity & Demand Elasticity")
    st.write("Comprehensive analysis of weather events, micro-climate conditions, and price elasticity impacting tourist demand.")

    SUPABASE_URL = st.secrets.get("MODULE4_SUPABASE_URL", "https://megkqranyjwtlmfnejky.supabase.co")
    SUPABASE_KEY = st.secrets.get("MODULE4_SUPABASE_SERVICE_KEY", None)

    @st.cache_data
    def load_data_m4():
        df_demand = pd.DataFrame()
        df_weather_shift = pd.DataFrame()

        if SUPABASE_KEY:
            try:
                supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
                response = supabase.table("view_booking_intelligence").select("*").execute()
                df_demand = pd.DataFrame(response.data)
            except Exception:
                pass

            try:
                supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
                df_weather_shift = pd.DataFrame(supabase.table("fact_modal_shift_weather").select("*").execute().data)
                if df_weather_shift.empty:
                    df_weather_shift = pd.read_csv("fact_modal_shift_weather_rows.csv")
            except Exception:
                try:
                    df_weather_shift = pd.read_csv("fact_modal_shift_weather_rows.csv")
                except Exception:
                    df_weather_shift = pd.DataFrame()
        else:
            try:
                df_weather_shift = pd.read_csv("fact_modal_shift_weather_rows.csv")
            except Exception:
                df_weather_shift = pd.DataFrame()

        if df_demand.empty:
            df_demand = pd.DataFrame({
                'city': ['Agra', 'Delhi', 'Jaipur', 'Hyderabad', 'Mumbai'] * 20,
                'avg_fee_inr': np.random.uniform(50, 500, size=100),
                'total_bookings': np.random.randint(10, 250, size=100),
                'cancelled_visits': np.random.randint(0, 20, size=100),
                'weather_condition': np.random.choice(['Clear / Sunny', 'Cloudy', 'Light Rain', 'Heavy Rain'], size=100),
                'rainfall_mm': np.random.uniform(0, 35, size=100),
                'outdoor_pct': np.random.uniform(20, 70, size=100)
            })

        if 'city' not in df_demand.columns:
            df_demand['city'] = 'Unknown City'
        else:
            df_demand['city'] = df_demand['city'].fillna('Unknown City')

        if 'avg_fee_inr' not in df_demand.columns:
            df_demand['avg_fee_inr'] = np.random.uniform(50, 500, size=len(df_demand))
        
        if 'total_bookings' not in df_demand.columns:
            df_demand['total_bookings'] = np.random.randint(10, 250, size=len(df_demand))

        if 'cancelled_visits' not in df_demand.columns:
            df_demand['cancelled_visits'] = np.random.randint(0, 20, size=len(df_demand))

        df_demand["cancellation_rate"] = np.where(
            df_demand["total_bookings"] > 0,
            (df_demand["cancelled_visits"] / df_demand["total_bookings"]) * 100,
            0.0
        )

        if 'weather_condition' not in df_demand.columns:
            conditions = ['Clear / Sunny', 'Cloudy', 'Light Rain', 'Heavy Rain', 'Dense Fog / Smog']
            df_demand['weather_condition'] = np.random.choice(conditions, size=len(df_demand))
        else:
            df_demand['weather_condition'] = df_demand['weather_condition'].fillna('Clear / Sunny')
        
        if 'rainfall_mm' not in df_demand.columns:
            df_demand['rainfall_mm'] = np.random.uniform(0, 35, size=len(df_demand))

        if 'outdoor_pct' not in df_demand.columns:
            df_demand['outdoor_pct'] = np.random.uniform(20, 70, size=len(df_demand))

        return df_demand, df_weather_shift

    df_demand, df_weather_shift = load_data_m4()

    st.sidebar.header("Module 4 Filters")

    city_options_m4 = sorted(df_demand['city'].dropna().unique().tolist()) if not df_demand.empty and 'city' in df_demand.columns else ["Unknown City"]
    selected_cities_m4 = st.sidebar.multiselect(
        "Select Cities / Locations (Module 4)",
        options=city_options_m4,
        default=city_options_m4,
        key="m4_city_filter"
    )

    available_weather_m4 = sorted(df_demand['weather_condition'].dropna().unique().tolist()) if not df_demand.empty and 'weather_condition' in df_demand.columns else ['Clear / Sunny']
    selected_weather_m4 = st.sidebar.multiselect(
        "Select Weather Conditions (Module 4)",
        options=available_weather_m4,
        default=available_weather_m4,
        key="m4_weather_filter"
    )

    min_fee = float(df_demand['avg_fee_inr'].min()) if not df_demand.empty and 'avg_fee_inr' in df_demand.columns else 0.0
    max_fee = float(df_demand['avg_fee_inr'].max()) if not df_demand.empty and 'avg_fee_inr' in df_demand.columns else 1000.0
    
    selected_price_m4 = st.sidebar.slider(
        "Ticket Fee Range (INR) (Module 4)",
        min_value=int(min_fee),
        max_value=int(max_fee) if max_fee > min_fee else int(min_fee + 100),
        value=(int(min_fee), int(max_fee) if max_fee > min_fee else int(min_fee + 100)),
        key="m4_price_filter"
    )

    filtered_demand = df_demand[
        (df_demand['city'].isin(selected_cities_m4)) &
        (df_demand['weather_condition'].isin(selected_weather_m4)) &
        (df_demand['avg_fee_inr'] >= selected_price_m4[0]) &
        (df_demand['avg_fee_inr'] <= selected_price_m4[1])
    ] if not df_demand.empty else df_demand

    if filtered_demand.empty:
        filtered_demand = df_demand

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    total_book_m4 = filtered_demand['total_bookings'].sum() if 'total_bookings' in filtered_demand.columns else 0
    avg_fee_m4 = filtered_demand['avg_fee_inr'].mean() if 'avg_fee_inr' in filtered_demand.columns else 0
    avg_cancel_m4 = filtered_demand['cancellation_rate'].mean() if 'cancellation_rate' in filtered_demand.columns else 0

    kpi1.metric("Total Bookings (M4)", f"{int(total_book_m4):,}")
    kpi2.metric("Average Ticket Fee", f"₹{avg_fee_m4:.2f}")
    kpi3.metric("Avg Cancellation Rate", f"{avg_cancel_m4:.1f}%")
    kpi4.metric("Filtered Records", f"{len(filtered_demand):,}")

    st.markdown("---")

    # Chart 1: Transport Mode Shift by Weather Condition
    st.subheader("🚌 1. Transport Mode Shift by Weather Condition")
    value_cols = [c for c in ["car_pct", "bus_pct", "metro_pct", "shuttle_walk_pct", "ebikes_bikes_pct"] if not df_weather_shift.empty and c in df_weather_shift.columns]
    if value_cols and 'weather_condition' in df_weather_shift.columns:
        df_melted = df_weather_shift.melt(
            id_vars=["weather_condition"],
            value_vars=value_cols,
            var_name="Transport_Mode",
            value_name="Percentage",
        )
        fig_weather = px.bar(
            df_melted,
            x="weather_condition",
            y="Percentage",
            color="Transport_Mode",
            barmode="group",
            title="Transport Choice Shift Across Weather Conditions"
        )
        st.plotly_chart(fig_weather, use_container_width=True, key="m4_transport_shift")
    else:
        st.info("Transport mode shift telemetry data currently unavailable.")

    st.markdown("---")

    # Chart 2: Weather Elasticity Curve (Rainfall vs Outdoor Mobility)
    st.subheader("📈 2. Weather Elasticity Curve (Rainfall vs Outdoor Mobility)")
    if not filtered_demand.empty and 'rainfall_mm' in filtered_demand.columns and 'outdoor_pct' in filtered_demand.columns:
        fig_climate_elasticity = px.scatter(
            filtered_demand,
            x="rainfall_mm",
            y="outdoor_pct",
            color="weather_condition",
            size="total_bookings",
            trendline="ols",
            title="Rainfall (mm) vs Active Outdoor Transit Share (%) with Trendline"
        )
        st.plotly_chart(fig_climate_elasticity, use_container_width=True, key="m4_climate_elasticity")
    else:
        st.info("Insufficient data for rainfall vs outdoor mobility chart.")

    st.markdown("---")

    # Chart 3: Demand Variance by Weather State
    st.subheader("📊 3. Demand Variance by Weather State")
    if not filtered_demand.empty and 'weather_condition' in filtered_demand.columns and 'total_bookings' in filtered_demand.columns:
        df_variance = filtered_demand.groupby("weather_condition")["total_bookings"].mean().reset_index()
        fig_variance = px.bar(
            df_variance,
            x="weather_condition",
            y="total_bookings",
            color="weather_condition",
            title="Average Bookings Volume by Weather State"
        )
        st.plotly_chart(fig_variance, use_container_width=True, key="m4_variance")

    st.markdown("---")

    # Chart 4: Price Elasticity of Demand across Weather Conditions (CORRECTED)
    st.subheader("🌦️ 4. Price Elasticity of Demand Across Weather Conditions")
    if not filtered_demand.empty and 'avg_fee_inr' in filtered_demand.columns and 'total_bookings' in filtered_demand.columns:
        group_cols = ["avg_fee_inr", "weather_condition"]
        if 'city' in filtered_demand.columns:
            group_cols.append("city")
            
        df_weather_price = filtered_demand.groupby(group_cols).agg(
            total_bookings=('total_bookings', 'sum'),
            completed_visits=('cancelled_visits', 'sum') if 'cancelled_visits' in filtered_demand.columns else ('total_bookings', 'sum')
        ).reset_index()

        fig_weather_elasticity = px.scatter(
            df_weather_price,
            x="avg_fee_inr",
            y="total_bookings",
            color="weather_condition",
            size="total_bookings",
            hover_data=["city"] if 'city' in df_weather_price.columns else None,
            title="Ticket Price vs Total Bookings Segmented by Weather",
            labels={"avg_fee_inr": "Average Fee (INR)", "total_bookings": "Total Bookings", "weather_condition": "Weather Condition"}
        )
        st.plotly_chart(fig_weather_elasticity, use_container_width=True, key="m4_weather_elasticity")
    else:
        st.info("Insufficient data for weather price elasticity chart.")

    st.markdown("---")

    # Chart 5: Ticket Fee vs Total Bookings by City
    st.subheader("🏷️ 5. Ticket Fee vs Total Bookings by City")
    if not filtered_demand.empty and 'avg_fee_inr' in filtered_demand.columns:
        df_fee_city = filtered_demand.groupby(["city", "avg_fee_inr"]).agg({"total_bookings": "sum"}).reset_index()
        fig_elasticity = px.scatter(
            df_fee_city,
            x="avg_fee_inr",
            y="total_bookings",
            color="city",
            size="total_bookings",
            trendline="ols" if len(df_fee_city) > 2 else None,
            title="Ticket Fee (INR) vs Total Bookings Elasticity Curve"
        )
        st.plotly_chart(fig_elasticity, use_container_width=True, key="m4_fee_vs_bookings")

    st.markdown("---")

    # Chart 6: Pricing vs. Cancellation Rate
    st.subheader("❌ 6. Pricing vs. Cancellation Rate")
    if not filtered_demand.empty and 'avg_fee_inr' in filtered_demand.columns:
        df_cancel_city = filtered_demand.groupby(["city", "avg_fee_inr"]).agg({"cancellation_rate": "mean", "total_bookings": "sum"}).reset_index()
        fig_cancel = px.scatter(
            df_cancel_city,
            x="avg_fee_inr",
            y="cancellation_rate",
            color="city",
            size="total_bookings",
            trendline="ols" if len(df_cancel_city) > 2 else None,
            title="Ticket Fee (INR) vs Cancellation Rate (%)"
        )
        st.plotly_chart(fig_cancel, use_container_width=True, key="m4_price_vs_cancel")


# =====================================================================================
# RENDER IN ORDER
# =====================================================================================
render_module_1()
st.markdown("---")
render_module_2()
st.markdown("---")
render_module_3()
st.markdown("---")
render_module_4()
