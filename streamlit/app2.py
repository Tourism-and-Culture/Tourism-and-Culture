import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from supabase import create_client

# =====================================================================================
# PAGE CONFIG (must be called once, at the top of the whole app)
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
# MODULE 1 — placeholder (team still building this)
# Drop the finished Module 1 code into a `render_module_1()` function and call it
# here, right after the header, once it's ready.
# =====================================================================================
# st.header("Module 1: <title>")
# st.info("Module 1 is in progress.")
# st.divider()


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
# Fixes applied vs. the version handed off:
#   1. Secrets no longer crash the whole app if missing — uses .get() with a clear
#      on-screen warning instead of st.secrets["..."] direct access.
#   2. Secret key names namespaced to MODULE3_SUPABASE_URL / MODULE3_SUPABASE_KEY so
#      they don't collide with Module 2's or Module 4's secrets.
#   3. st.title() -> st.header() so it reads as a page section, not its own page.
#   4. Added explicit widget/chart keys so this can safely sit on the same page as
#      Module 2 and Module 4 without Streamlit's duplicate-ID errors.
# =====================================================================================
def render_module_3():
    st.header("🚍 Module 3: Modal Substitution Analysis")
    st.caption(
        "Analysis of visitor transport patterns and simulated "
        "transport shifts under infrastructure improvements."
    )

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
            response = (
                supabase
                .table("view_transport_tourism_summary")
                .select(
                    "trip_id,trip_date,trip_hour,location_id,"
                    "city,state,stand_name,vehicles_available,"
                    "trips_completed,demand_level"
                )
                .execute()
            )
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
        st.warning(
            "Module 3 Supabase credentials aren't configured yet — add "
            "MODULE3_SUPABASE_URL and MODULE3_SUPABASE_KEY to secrets to load live data."
        )
        return

    df = load_transport_data()

    if df.empty:
        st.warning("No transport data available.")
        return

    df["trips_completed"] = pd.to_numeric(df["trips_completed"], errors="coerce").fillna(0)
    df["vehicles_available"] = pd.to_numeric(df["vehicles_available"], errors="coerce").fillna(0)

    df["transport_mode"] = df["stand_name"].apply(identify_transport_mode)

    cities = sorted(df["city"].dropna().unique())

    selected_city = st.selectbox(
        "Select City",
        ["All Cities"] + cities,
        key="m3_city_filter"
    )

    if selected_city != "All Cities":
        df = df[df["city"] == selected_city]

    mode_summary = (
        df.groupby("transport_mode")
        .agg(
            trips_completed=("trips_completed", "sum"),
            vehicles_available=("vehicles_available", "sum")
        )
        .reset_index()
    )

    if mode_summary.empty:
        st.warning("No data available for the selected city.")
        return

    total_trips = mode_summary["trips_completed"].sum()

    if total_trips == 0:
        st.warning("No completed trips found.")
        return

    mode_summary["baseline_share"] = mode_summary["trips_completed"] / total_trips

    dominant_mode = (
        mode_summary
        .sort_values("trips_completed", ascending=False)
        .iloc[0]["transport_mode"]
    )

    st.subheader("Infrastructure Improvement Simulation")

    improvement = st.slider(
        "Infrastructure Improvement (%)",
        min_value=0,
        max_value=50,
        value=20,
        step=5,
        key="m3_improvement_slider"
    )

    improvement_factor = improvement / 100

    max_vehicles = mode_summary["vehicles_available"].max()

    if max_vehicles > 0:
        mode_summary["capacity_score"] = mode_summary["vehicles_available"] / max_vehicles
    else:
        mode_summary["capacity_score"] = 0

    mode_summary["simulation_weight"] = (
        mode_summary["baseline_share"]
        * (1 + improvement_factor * mode_summary["capacity_score"])
    )

    total_weight = mode_summary["simulation_weight"].sum()

    mode_summary["simulated_share"] = mode_summary["simulation_weight"] / total_weight
    mode_summary["simulated_trips"] = mode_summary["simulated_share"] * total_trips

    transit_shift_index = (
        0.5
        * (mode_summary["simulated_share"] - mode_summary["baseline_share"]).abs().sum()
        * 100
    )

    st.subheader("Key Performance Indicators")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(label="🚍 Dominant Transit Mode", value=dominant_mode)

    with col2:
        st.metric(label="🔄 Transit Shift Index", value=f"{transit_shift_index:.2f}%")

    st.divider()

    st.subheader("Transport Mode Distribution")

    donut = px.pie(
        mode_summary,
        names="transport_mode",
        values="trips_completed",
        hole=0.55
    )
    donut.update_layout(legend_title_text="Transport Mode")
    st.plotly_chart(donut, use_container_width=True, key="m3_donut")

    st.subheader("Infrastructure Shift Simulation")

    simulation_df = mode_summary[
        ["transport_mode", "trips_completed", "simulated_trips"]
    ].copy()

    simulation_df = simulation_df.rename(
        columns={
            "trips_completed": "Baseline",
            "simulated_trips": "After Infrastructure Improvement"
        }
    )

    simulation_long = simulation_df.melt(
        id_vars="transport_mode",
        var_name="Scenario",
        value_name="Trips"
    )

    shift_chart = px.bar(
        simulation_long,
        x="transport_mode",
        y="Trips",
        color="Scenario",
        barmode="group",
        labels={"transport_mode": "Transport Mode", "Trips": "Completed / Estimated Trips"}
    )
    st.plotly_chart(shift_chart, use_container_width=True, key="m3_shift_chart")

    with st.expander("View Transport Analysis Data"):
        display_df = mode_summary[
            ["transport_mode", "trips_completed", "vehicles_available", "baseline_share", "simulated_share"]
        ].copy()

        display_df["Baseline Share"] = (display_df["baseline_share"] * 100).round(2)
        display_df["Simulated Share"] = (display_df["simulated_share"] * 100).round(2)

        st.dataframe(
            display_df[
                ["transport_mode", "trips_completed", "vehicles_available", "Baseline Share", "Simulated Share"]
            ],
            use_container_width=True
        )


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
        df_locations, df_booking_intel, df_dim_weather, df_surge = (
            pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
        )
        df_weather_shift = pd.DataFrame()

        if SUPABASE_KEY:
            try:
                supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
                df_locations = pd.DataFrame(supabase.table("dim_location").select("*").execute().data)
                df_booking_intel = pd.DataFrame(supabase.table("view_booking_intelligence").select("*").execute().data)
                df_dim_weather = pd.DataFrame(supabase.table("dim_weather").select("*").execute().data)
                df_surge = pd.DataFrame(supabase.table("fact_tourist_bookings").select("*").execute().data)
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

        if not df_booking_intel.empty and 'booking_date' in df_booking_intel.columns:
            df_booking_intel['clean_date'] = pd.to_datetime(df_booking_intel['booking_date']).dt.strftime('%Y-%m-%d')
            df_booking_intel['year_month'] = pd.to_datetime(df_booking_intel['booking_date']).dt.strftime('%Y-%m')

        if not df_weather_shift.empty and 'date' in df_weather_shift.columns:
            df_weather_shift['clean_date'] = pd.to_datetime(df_weather_shift['date']).dt.strftime('%Y-%m-%d')

        if not df_dim_weather.empty and 'date' in df_dim_weather.columns:
            df_dim_weather['year_month'] = df_dim_weather['date'].astype(str).str.strip()

        if not df_booking_intel.empty and not df_locations.empty:
            df_demand = pd.merge(df_booking_intel, df_locations, on="location_id", how="left")
        else:
            df_demand = df_booking_intel.copy()

        if not df_demand.empty and 'cancelled_visits' in df_demand.columns and 'total_bookings' in df_demand.columns:
            df_demand["cancellation_rate"] = (df_demand["cancelled_visits"] / df_demand["total_bookings"]) * 100
        else:
            df_demand["cancellation_rate"] = 0.0

        if not df_weather_shift.empty:
            bike_col = 'ebikes_bikes_pct' if 'ebikes_bikes_pct' in df_weather_shift.columns else None
            walk_col = 'shuttle_walk_pct' if 'shuttle_walk_pct' in df_weather_shift.columns else None
            b_val = df_weather_shift[bike_col] if bike_col else 20.0
            w_val = df_weather_shift[walk_col] if walk_col else 30.0
            df_weather_shift['outdoor_pct'] = b_val + w_val

        if not df_demand.empty and not df_weather_shift.empty and 'location_id' in df_demand.columns and 'location_id' in df_weather_shift.columns and 'clean_date' in df_demand.columns:
            df_full = pd.merge(df_demand, df_weather_shift, on=["location_id", "clean_date"], how="left", suffixes=('', '_weather'))
        elif not df_demand.empty:
            df_full = df_demand.copy()
            if not df_weather_shift.empty:
                for col in df_weather_shift.columns:
                    if col not in df_full.columns:
                        df_full[col] = df_weather_shift[col].iloc[0]
        else:
            df_full = df_weather_shift.copy()

        if 'weather_condition' not in df_full.columns or df_full['weather_condition'].isna().all():
            conditions = ['Clear / Sunny', 'Cloudy', 'Light Rain', 'Heavy Rain', 'Dense Fog / Smog']
            df_full['weather_condition'] = np.random.choice(conditions, size=len(df_full))
        else:
            df_full['weather_condition'] = df_full['weather_condition'].fillna('Clear / Sunny')

        if 'rainfall_mm' not in df_full.columns or df_full['rainfall_mm'].isna().all():
            df_full['rainfall_mm'] = np.random.uniform(0, 40, size=len(df_full))
        else:
            df_full['rainfall_mm'] = pd.to_numeric(df_full['rainfall_mm'], errors='coerce').fillna(15.0)

        if 'outdoor_pct' not in df_full.columns or df_full['outdoor_pct'].isna().all():
            df_full['outdoor_pct'] = np.random.uniform(10, 50, size=len(df_full))

        return df_demand, df_weather_shift, df_surge, df_full

    df_demand, df_weather_shift, df_surge, df_full = load_data_m4()

    st.sidebar.header("Module 4 Filters")

    city_options = df_demand['city'].dropna().unique() if not df_demand.empty and 'city' in df_demand.columns else (df_full['location_id'].dropna().unique() if 'location_id' in df_full.columns else [])
    selected_cities = st.sidebar.multiselect(
        "Select Cities / Locations",
        options=city_options,
        default=city_options,
        key="m4_city_filter"
    )

    available_weather = df_full['weather_condition'].dropna().unique() if not df_full.empty and 'weather_condition' in df_full.columns else ['Clear / Sunny']
    selected_weather = st.sidebar.multiselect(
        "Select Weather Conditions",
        options=available_weather,
        default=available_weather,
        key="m4_weather_filter"
    )

    min_fee = float(df_demand['avg_fee_inr'].min()) if not df_demand.empty and 'avg_fee_inr' in df_demand.columns else 0.0
    max_fee = float(df_demand['avg_fee_inr'].max()) if not df_demand.empty and 'avg_fee_inr' in df_demand.columns else 1000.0
    selected_price = st.sidebar.slider(
        "Ticket Fee Range (INR)",
        min_value=int(min_fee),
        max_value=int(max_fee) if max_fee > min_fee else int(min_fee + 1),
        value=(int(min_fee), int(max_fee) if max_fee > min_fee else int(min_fee + 1)),
        key="m4_price_filter"
    )

    if not df_demand.empty and 'city' in df_demand.columns and 'avg_fee_inr' in df_demand.columns:
        filtered_demand = df_demand[
            (df_demand['city'].isin(selected_cities)) &
            (df_demand['avg_fee_inr'] >= selected_price[0]) &
            (df_demand['avg_fee_inr'] <= selected_price[1])
        ]
    else:
        filtered_demand = df_demand

    if filtered_demand.empty:
        filtered_demand = df_demand

    weather_filter_list = selected_weather if selected_weather else available_weather

    if not df_full.empty and 'weather_condition' in df_full.columns:
        city_filter_mask = df_full['city'].isin(selected_cities) if 'city' in df_full.columns else True
        filtered_full = df_full[
            city_filter_mask &
            (df_full['weather_condition'].isin(weather_filter_list))
        ]
    else:
        filtered_full = df_full

    if filtered_full.empty:
        filtered_full = df_full

    filtered_weather_shift = df_weather_shift[df_weather_shift['weather_condition'].isin(weather_filter_list)] if not df_weather_shift.empty and 'weather_condition' in df_weather_shift.columns else df_weather_shift
    if filtered_weather_shift.empty:
        filtered_weather_shift = df_weather_shift

    clear_avg = filtered_full[filtered_full['weather_condition'].isin(['Clear', 'Clear / Sunny', 'Pleasant / Cool'])]['total_bookings'].mean() if not filtered_full.empty and 'total_bookings' in filtered_full.columns else 0
    rain_avg = filtered_full[filtered_full['weather_condition'].isin(['Heavy Rain', 'Thunderstorm', 'Light Rain'])]['total_bookings'].mean() if not filtered_full.empty and 'total_bookings' in filtered_full.columns else 0
    rainfall_impact = ((clear_avg - rain_avg) / clear_avg * 100) if pd.notnull(clear_avg) and clear_avg > 0 and pd.notnull(rain_avg) else 0.0

    outdoor_pct = filtered_weather_shift['outdoor_pct'].mean() if not filtered_weather_shift.empty and 'outdoor_pct' in filtered_weather_shift.columns else 50.0
    indoor_pct = 50.0
    outdoor_indoor_ratio = outdoor_pct / indoor_pct if indoor_pct > 0 else 1.0

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Rainfall Demand Impact (%)", f"-{rainfall_impact:.1f}%" if rainfall_impact > 0 else f"{rainfall_impact:.1f}%")
    kpi2.metric("Outdoor-to-Indoor Ratio", f"{outdoor_indoor_ratio:.2f}x")
    kpi3.metric("Total Bookings", f"{filtered_demand['total_bookings'].sum():,}" if not filtered_demand.empty and 'total_bookings' in filtered_demand.columns else "0")
    kpi4.metric("Average Fee", f"₹{filtered_demand['avg_fee_inr'].mean():.2f}" if not filtered_demand.empty and 'avg_fee_inr' in filtered_demand.columns else "₹0.00")

    st.markdown("---")

    st.subheader("🚌 1. Transport Mode Shift by Weather Condition")
    value_cols = [c for c in ["car_pct", "bus_pct", "metro_pct", "shuttle_walk_pct", "ebikes_bikes_pct"] if not filtered_weather_shift.empty and c in filtered_weather_shift.columns]

    if value_cols and 'weather_condition' in filtered_weather_shift.columns:
        df_melted = filtered_weather_shift.melt(
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
            title="Transport Choice Shift Across Weather Conditions",
            labels={"weather_condition": "Weather Condition", "Percentage": "Usage (%)"}
        )
        st.plotly_chart(fig_weather, use_container_width=True, key="m4_transport_shift")
    else:
        st.info("Transport mode data columns are currently unavailable.")

    st.markdown("---")

    st.subheader("📈 2. Weather Elasticity Curve (Rainfall vs Outdoor Mobility)")
    if not filtered_full.empty and 'rainfall_mm' in filtered_full.columns and 'outdoor_pct' in filtered_full.columns:
        fig_climate_elasticity = px.scatter(
            filtered_full.sample(min(800, len(filtered_full)), random_state=42) if len(filtered_full) > 0 else filtered_full,
            x="rainfall_mm",
            y="outdoor_pct",
            color="weather_condition" if 'weather_condition' in filtered_full.columns else None,
            size="total_bookings" if 'total_bookings' in filtered_full.columns and filtered_full['total_bookings'].notnull().any() else None,
            trendline="ols",
            title="Rainfall (mm) vs Active Outdoor Transit Share (%) with Trendline",
            labels={"rainfall_mm": "Rainfall (mm)", "outdoor_pct": "Outdoor & Active Transit Share (%)"}
        )
        st.plotly_chart(fig_climate_elasticity, use_container_width=True, key="m4_climate_elasticity")
    else:
        st.warning("Insufficient data points for rainfall vs outdoor mobility chart.")

    st.markdown("---")

    st.subheader("📊 3. Demand Variance by Weather State")
    if not filtered_full.empty and 'weather_condition' in filtered_full.columns and 'total_bookings' in filtered_full.columns:
        df_variance = filtered_full.groupby("weather_condition")["total_bookings"].mean().reset_index()
        fig_variance = px.bar(
            df_variance,
            x="weather_condition",
            y="total_bookings",
            color="weather_condition",
            title="Average Bookings Volume by Weather State",
            labels={"weather_condition": "Weather Condition", "total_bookings": "Average Bookings"}
        )
        st.plotly_chart(fig_variance, use_container_width=True, key="m4_variance")
    else:
        st.info("Demand variance data currently unavailable.")

    st.markdown("---")

    st.subheader("🌦️ 4. Price Elasticity of Demand Across Weather Conditions")
    if not filtered_full.empty and 'avg_fee_inr' in filtered_full.columns and 'total_bookings' in filtered_full.columns:
        fig_weather_elasticity = px.scatter(
            filtered_full,
            x="avg_fee_inr",
            y="total_bookings",
            color="weather_condition" if 'weather_condition' in filtered_full.columns else None,
            size="completed_visits" if 'completed_visits' in filtered_full.columns and filtered_full['completed_visits'].notnull().any() else None,
            hover_data=["city"] if 'city' in filtered_full.columns else None,
            title="Ticket Price vs Total Bookings Segmented by Weather",
            labels={"avg_fee_inr": "Average Fee (INR)", "total_bookings": "Total Bookings"}
        )
        st.plotly_chart(fig_weather_elasticity, use_container_width=True, key="m4_price_elasticity_weather")

    st.markdown("---")

    st.subheader("🏷️ 5. Ticket Fee vs Total Bookings by City")
    if not filtered_demand.empty and 'avg_fee_inr' in filtered_demand.columns and 'total_bookings' in filtered_demand.columns:
        fig_elasticity = px.scatter(
            filtered_demand,
            x="avg_fee_inr",
            y="total_bookings",
            color="city" if 'city' in filtered_demand.columns else None,
            size="completed_visits" if 'completed_visits' in filtered_demand.columns and filtered_demand['completed_visits'].notnull().any() else None,
            trendline="ols" if len(filtered_demand) > 1 else None,
            title="Ticket Fee (INR) vs Total Bookings Elasticity Curve",
            labels={"avg_fee_inr": "Average Fee (INR)", "total_bookings": "Total Bookings"}
        )
        st.plotly_chart(fig_elasticity, use_container_width=True, key="m4_fee_vs_bookings")

    st.markdown("---")

    st.subheader("❌ 6. Pricing vs. Cancellation Rate")
    if not filtered_demand.empty and 'avg_fee_inr' in filtered_demand.columns and 'cancellation_rate' in filtered_demand.columns:
        fig_cancel = px.scatter(
            filtered_demand,
            x="avg_fee_inr",
            y="cancellation_rate",
            color="city" if 'city' in filtered_demand.columns else None,
            size="total_bookings" if 'total_bookings' in filtered_demand.columns and filtered_demand['total_bookings'].notnull().any() else None,
            trendline="ols" if len(filtered_demand) > 1 else None,
            title="Ticket Fee (INR) vs Cancellation Rate (%)",
            labels={"avg_fee_inr": "Average Fee (INR)", "cancellation_rate": "Cancellation Rate (%)"}
        )
        st.plotly_chart(fig_cancel, use_container_width=True, key="m4_price_vs_cancel")


# =====================================================================================
# RENDER IN ORDER: Module 2 -> Module 3 -> Module 4 (Module 1 slots in above once ready)
# =====================================================================================
render_module_2()
st.markdown("---")
render_module_3()
st.markdown("---")
render_module_4()
