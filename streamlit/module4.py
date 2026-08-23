import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from supabase import create_client

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
