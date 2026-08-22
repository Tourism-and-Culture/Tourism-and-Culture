import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client


# --------------------------------------------------
# SUPABASE CONNECTION
# --------------------------------------------------

@st.cache_resource
def get_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]

    return create_client(url, key)


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

@st.cache_data(ttl=600)
def load_transport_data():

    supabase = get_supabase()

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

    df = pd.DataFrame(response.data)

    return df


# --------------------------------------------------
# CREATE TRANSPORT MODE
# --------------------------------------------------

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


# --------------------------------------------------
# MODULE 3
# --------------------------------------------------

def render_module3():

    st.title("🚍 Module 3 – Modal Substitution Analysis")

    st.caption(
        "Analysis of visitor transport patterns and simulated "
        "transport shifts under infrastructure improvements."
    )

    # -----------------------------
    # LOAD SUPABASE DATA
    # -----------------------------

    df = load_transport_data()

    if df.empty:
        st.warning("No transport data available.")
        return

    # Ensure numbers are numeric
    df["trips_completed"] = pd.to_numeric(
        df["trips_completed"],
        errors="coerce"
    ).fillna(0)

    df["vehicles_available"] = pd.to_numeric(
        df["vehicles_available"],
        errors="coerce"
    ).fillna(0)

    # -----------------------------
    # DERIVE TRANSPORT MODE
    # -----------------------------

    df["transport_mode"] = df["stand_name"].apply(
        identify_transport_mode
    )

    # -----------------------------
    # CITY FILTER
    # -----------------------------

    cities = sorted(df["city"].dropna().unique())

    selected_city = st.selectbox(
        "Select City",
        ["All Cities"] + cities
    )

    if selected_city != "All Cities":
        df = df[df["city"] == selected_city]

    # -----------------------------
    # MODE SUMMARY
    # -----------------------------

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

    # -----------------------------
    # BASELINE SHARE
    # -----------------------------

    mode_summary["baseline_share"] = (
        mode_summary["trips_completed"] / total_trips
    )

    # -----------------------------
    # DOMINANT TRANSIT MODE
    # -----------------------------

    dominant_mode = (
        mode_summary
        .sort_values("trips_completed", ascending=False)
        .iloc[0]["transport_mode"]
    )

    # --------------------------------------------------
    # INFRASTRUCTURE SIMULATION
    # --------------------------------------------------

    st.subheader("Infrastructure Improvement Simulation")

    improvement = st.slider(
        "Infrastructure Improvement (%)",
        min_value=0,
        max_value=50,
        value=20,
        step=5
    )

    improvement_factor = improvement / 100

    max_vehicles = mode_summary["vehicles_available"].max()

    if max_vehicles > 0:

        mode_summary["capacity_score"] = (
            mode_summary["vehicles_available"]
            / max_vehicles
        )

    else:

        mode_summary["capacity_score"] = 0

    # Increase attractiveness based on infrastructure capacity
    mode_summary["simulation_weight"] = (
        mode_summary["baseline_share"]
        *
        (
            1
            +
            improvement_factor
            *
            mode_summary["capacity_score"]
        )
    )

    # Re-normalise so transport shares equal 100%
    total_weight = mode_summary["simulation_weight"].sum()

    mode_summary["simulated_share"] = (
        mode_summary["simulation_weight"]
        / total_weight
    )

    mode_summary["simulated_trips"] = (
        mode_summary["simulated_share"]
        * total_trips
    )

    # --------------------------------------------------
    # TRANSIT SHIFT INDEX
    # --------------------------------------------------

    transit_shift_index = (
        0.5
        *
        (
            mode_summary["simulated_share"]
            -
            mode_summary["baseline_share"]
        ).abs().sum()
        *
        100
    )

    # --------------------------------------------------
    # KPI CARDS
    # --------------------------------------------------

    st.subheader("Key Performance Indicators")

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            label="🚍 Dominant Transit Mode",
            value=dominant_mode
        )

    with col2:

        st.metric(
            label="🔄 Transit Shift Index",
            value=f"{transit_shift_index:.2f}%"
        )

    st.divider()

    # --------------------------------------------------
    # TRANSPORT MODE DONUT
    # --------------------------------------------------

    st.subheader("Transport Mode Distribution")

    donut = px.pie(
        mode_summary,
        names="transport_mode",
        values="trips_completed",
        hole=0.55
    )

    donut.update_layout(
        legend_title_text="Transport Mode"
    )

    st.plotly_chart(
        donut,
        use_container_width=True
    )

    # --------------------------------------------------
    # INFRASTRUCTURE SHIFT CHART
    # --------------------------------------------------

    st.subheader("Infrastructure Shift Simulation")

    simulation_df = mode_summary[
        [
            "transport_mode",
            "trips_completed",
            "simulated_trips"
        ]
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
        labels={
            "transport_mode": "Transport Mode",
            "Trips": "Completed / Estimated Trips"
        }
    )

    st.plotly_chart(
        shift_chart,
        use_container_width=True
    )

    # --------------------------------------------------
    # DETAILS
    # --------------------------------------------------

    with st.expander("View Transport Analysis Data"):

        display_df = mode_summary[
            [
                "transport_mode",
                "trips_completed",
                "vehicles_available",
                "baseline_share",
                "simulated_share"
            ]
        ].copy()

        display_df["Baseline Share"] = (
            display_df["baseline_share"] * 100
        ).round(2)

        display_df["Simulated Share"] = (
            display_df["simulated_share"] * 100
        ).round(2)

        st.dataframe(
            display_df[
                [
                    "transport_mode",
                    "trips_completed",
                    "vehicles_available",
                    "Baseline Share",
                    "Simulated Share"
                ]
            ],
            use_container_width=True
        )