from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components
from supabase import create_client

# page setup
st.set_page_config(
    page_title="Executive Dashboard | Smart Urban Mobility & Traffic Intelligence",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).resolve().parent
MAPS_DIR = BASE_DIR / "maps"

TABLES = {
    "attractions": "fact_attractions",
    "monthly": "fact_monthly_tourism",
    "festivals": "fact_festivals",
    "bookings": "view_booking_intelligence",
    "transport": "view_transport_tourism_summary",
    "modal": "fact_modal_shift_weather",
    "locations": "dim_location",
}

DEMAND_MAPS = {
    "Overall demand": "01_demand_heatmap_overall.html",
    "High demand": "02_demand_heatmap_high_demand.html",
    "Top destinations": "03_demand_heatmap_top_destinations.html",
    "Medium / high demand": "04_demand_heatmap_medium_high.html",
    "All destinations": "05_demand_heatmap_all_destinations.html",
}

FLOW_MAPS = {
    "All origin countries": "06_tourism_flow_all_countries.html",
    "Top 10 origins": "07_tourism_flow_top_10.html",
    "Top 15 origins": "08_tourism_flow_top_15.html",
    "Top 20 origins": "09_tourism_flow_top_20.html",
    "Major markets": "10_tourism_flow_major_markets.html",
}


st.markdown(
    """
    <style>
        .block-container {
            max-width: 1500px;
            padding-top: 1.5rem;
        }

        h1, h2, h3 {
            color: #173154;
        }

        div[data-testid="stMetric"] {
            background: #f3f7fc;
            border: 1px solid #dce6f2;
            border-radius: 12px;
            padding: 14px;
        }

        div[data-testid="stMetricLabel"] {
            color: #536985;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# connect to supabase
def secret_value(name):
    """Read a secret without crashing when secrets.toml is absent."""
    try:
        return st.secrets.get(name)
    except Exception:
        return None


def credentials_for(dataset_name):
    """
    Prefer the shared Supabase credentials used by Milestone 4.
    Also recognize the module-specific names used in Milestone 3.
    """

    url = secret_value("SUPABASE_URL")
    key = secret_value("SUPABASE_KEY")

    # Also support the [supabase] format used in Milestone 2.
    try:
        nested = st.secrets.get("supabase", {})
        url = url or nested.get("url")
        key = key or nested.get("key")
    except Exception:
        pass

    if url and key:
        return url, key

    if dataset_name == "bookings":
        alternatives = [
            ("MODULE1_SUPABASE_URL", "MODULE1_SUPABASE_SERVICE_KEY"),
            ("MODULE4_SUPABASE_URL", "MODULE4_SUPABASE_SERVICE_KEY"),
        ]

    elif dataset_name == "transport":
        alternatives = [
            ("MODULE3_SUPABASE_URL", "MODULE3_SUPABASE_KEY"),
        ]

    elif dataset_name == "modal":
        alternatives = [
            ("MODULE4_SUPABASE_URL", "MODULE4_SUPABASE_SERVICE_KEY"),
        ]

    else:
        alternatives = []

    for url_name, key_name in alternatives:
        module_url = secret_value(url_name)
        module_key = secret_value(key_name)

        if module_url and module_key:
            return module_url, module_key

    return None, None


@st.cache_resource
def get_supabase_client(url, key):
    return create_client(url, key)


@st.cache_data(ttl=300, show_spinner=False)
def load_table(dataset_name):
    """
    Fetch directly from Supabase. No CSV files or generated data are used.

    The first 1,000 rows are loaded to match the current milestone
    dashboard's single-query analysis scope.
    """

    table_name = TABLES[dataset_name]
    url, key = credentials_for(dataset_name)

    if not url or not key:
        return pd.DataFrame(), (
            f"No matching Supabase URL/key pair configured for {table_name}."
        )

    try:
        response = (
            get_supabase_client(url, key)
            .table(table_name)
            .select("*")
            .range(0, 999)
            .execute()
        )

        if not response.data:
            return pd.DataFrame(), (
                f"{table_name} returned no rows. Check the table, "
                "its permissions, and its data."
            )

        return pd.DataFrame(response.data), None

    except Exception as exc:
        return pd.DataFrame(), (
            f"{table_name}: {type(exc).__name__}: {str(exc)[:200]}"
        )


# helpers
def numeric(df, column):
    if column not in df.columns:
        return pd.Series(0.0, index=df.index)

    return pd.to_numeric(df[column], errors="coerce").fillna(0)


def show_chart(fig, height=320):
    fig.update_layout(
        height=height,
        margin=dict(l=8, r=8, t=25, b=8),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(color="#233d5d"),
    )
    st.plotly_chart(fig, use_container_width=True)


def show_map(filename):
    path = MAPS_DIR / filename

    if not path.is_file():
        st.warning(
            f"Map file missing: maps/{filename}. "
            "Place your original HTML maps in a maps folder beside this script."
        )
        return

    components.html(
        path.read_text(encoding="utf-8"),
        height=430,
        scrolling=False,
    )


def show_section(title, description=None):
    st.subheader(title)

    if description:
        st.caption(description)


# sidebar filters and cache
with st.sidebar:
    st.title("🇮🇳 Executive view")
    st.caption("Smart Urban Mobility and Traffic Intelligence · Team 1")

    st.info(
        "The saved HTML maps retain their original appearance. "
        "Year and state filters apply to the Supabase charts, "
        "but do not redraw the saved maps."
    )

    if st.button("Refresh Supabase data"):
        st.cache_data.clear()
        st.rerun()


with st.spinner("Loading executive dashboard data from Supabase..."):
    loaded = {
        dataset_name: load_table(dataset_name)
        for dataset_name in TABLES
    }

failures = {
    dataset_name: error
    for dataset_name, (data, error) in loaded.items()
    if data.empty
}

if failures:
    st.error(
        "The executive dashboard could not load all required "
        "Supabase tables."
    )

    for dataset_name, error in failures.items():
        st.write(f"**{TABLES[dataset_name]}:** {error}")

    st.info(
        "For all dashboard sections, set SUPABASE_URL and SUPABASE_KEY "
        "in .streamlit/secrets.toml or in your Streamlit Cloud app secrets. "
        "This dashboard does not load CSV data."
    )
    st.stop()


attractions = loaded["attractions"][0].copy()
monthly = loaded["monthly"][0].copy()
festivals = loaded["festivals"][0].copy()
bookings = loaded["bookings"][0].copy()
transport = loaded["transport"][0].copy()
modal = loaded["modal"][0].copy()
locations = loaded["locations"][0].copy()

bookings["booking_date"] = pd.to_datetime(
    bookings["booking_date"], errors="coerce"
)
transport["trip_date"] = pd.to_datetime(
    transport["trip_date"], errors="coerce"
)
modal["date"] = pd.to_datetime(
    modal["date"], errors="coerce"
)

modal["Season"] = modal["date"].dt.month.map(
    lambda month: (
        "Peak Season"
        if month in [10, 11, 12, 1, 2, 3]
        else "Off-Peak Season"
    )
)

if "location_id" in modal.columns and "location_id" in locations.columns:
    traffic_locations = locations[["location_id", "city", "state"]].copy()
    traffic_locations["state"] = (
        traffic_locations["state"].astype(str).str.strip().replace(
            {"Maharahtra": "Maharashtra", "Maharastra": "Maharashtra"}
        )
    )
    modal["location_id"] = modal["location_id"].astype(str)
    traffic_locations["location_id"] = traffic_locations["location_id"].astype(str)
    modal = modal.merge(
        traffic_locations.drop_duplicates("location_id"),
        on="location_id",
        how="left",
        suffixes=("", "_location"),
    )

monthly["year"] = pd.to_numeric(
    monthly["year"], errors="coerce"
)

years = sorted(
    {
        int(value)
        for value in pd.concat(
            [
                monthly["year"],
                bookings["booking_date"].dt.year,
                transport["trip_date"].dt.year,
            ],
            ignore_index=True,
        ).dropna()
    }
)

states = sorted(
    set(bookings["state"].dropna().astype(str))
    | set(transport["state"].dropna().astype(str))
)

with st.sidebar:
    selected_year = st.selectbox("Year", ["All"] + years)
    selected_state = st.selectbox("State", ["All"] + states)

    st.caption("Data source: Supabase only")
    st.caption("Query scope: first 1,000 rows per table or view")
    st.caption("Tourism seasons: Peak = Oct–Mar · Off-Peak = Apr–Sep")


# filters
if selected_year != "All":
    monthly = monthly[monthly["year"] == selected_year]

    if "year" in festivals.columns:
        festivals = festivals[
            numeric(festivals, "year") == selected_year
        ]

    bookings = bookings[
        bookings["booking_date"].dt.year == selected_year
    ]
    transport = transport[
        transport["trip_date"].dt.year == selected_year
    ]
    modal = modal[
        modal["date"].dt.year == selected_year
    ]

if selected_state != "All":
    bookings = bookings[
        bookings["state"] == selected_state
    ]
    transport = transport[
        transport["state"] == selected_state
    ]

    location_ids = set(
        locations.loc[
            locations["state"] == selected_state,
            "location_id",
        ]
    )

    attractions = attractions[
        attractions["location_id"].isin(location_ids)
    ]
    modal = modal[
        modal["location_id"].isin(location_ids)
    ]

    if "state" in festivals.columns:
        festivals = festivals[
            festivals["state"] == selected_state
        ]


# KPI Calculations
st.title("Smart Urban Mobility and Traffic Intelligence Dashboard")
st.caption("TOURISM AND CULTURAL INTELLIGENCE USE CASE")
st.caption("MASTER EXECUTIVE DASHBOARD · MILESTONES 1–4")

st.caption(
    "Operational figures reflect the Supabase rows loaded into the "
    "dashboard. The maps are original saved visualizations."
)

valid_attractions = attractions[
    numeric(attractions, "google_rating").between(0, 5)
]

k1, k2, k3, k4, k5, k6 = st.columns(6)

k1.metric(
    "Tourist places",
    f"{len(valid_attractions):,}",
)

k2.metric(
    "Foreign arrivals",
    f"{numeric(monthly, 'foreign_tourist_arrivals').sum():,.0f}",
)

k3.metric(
    "Tourism revenue",
    f"₹{numeric(monthly, 'tourism_revenue_crore_inr').sum():,.0f} Cr",
)

k4.metric(
    "Bookings in view",
    f"{numeric(bookings, 'total_bookings').sum():,.0f}",
)

k5.metric(
    "Completed visits",
    f"{numeric(bookings, 'completed_visits').sum():,.0f}",
)

k6.metric(
    "Trips in view",
    f"{numeric(transport, 'trips_completed').sum():,.0f}",
)

# 1. TOURISM DEMAND AND CULTURE
show_section("1 · Tourism demand & cultural overview")

left, right = st.columns(2)

with left:
    st.markdown("**Monthly foreign tourist arrivals**")

    if not monthly.empty:
        month_numbers = {
            month: index
            for index, month in enumerate(
                [
                    "January", "February", "March",
                    "April", "May", "June",
                    "July", "August", "September",
                    "October", "November", "December",
                ],
                start=1,
            )
        }

        trend = monthly.copy()
        trend["month_num"] = trend["month"].map(month_numbers)

        trend = trend.dropna(
            subset=["year", "month_num"]
        ).sort_values(
            ["year", "month_num"]
        )

        if not trend.empty:
            trend["period"] = pd.to_datetime(
                {
                    "year": trend["year"].astype(int),
                    "month": trend["month_num"].astype(int),
                    "day": 1,
                }
            )

            fig = px.line(
                trend,
                x="period",
                y="foreign_tourist_arrivals",
                markers=True,
                labels={
                    "period": "Month",
                    "foreign_tourist_arrivals": "Foreign arrivals",
                },
            )
            show_chart(fig)

with right:
    st.markdown("**Valid attractions by category**")

    if not valid_attractions.empty:
        categories = (
            valid_attractions["category"]
            .value_counts()
            .reset_index()
        )

        fig = px.bar(
            categories,
            x="count",
            y="category",
            orientation="h",
            color="count",
            color_continuous_scale="Blues",
            labels={
                "count": "Attractions",
                "category": "",
            },
        )
        show_chart(fig)


# 2 ORIGINAL DEMAND HEATMAPS AND FLOW MAPS
show_section(
    "2 · Demand heatmaps & tourism flows",
    "These are our original HTML maps. They are saved map views, "
    "so the dashboard filters do not change their plotted data.",
)

left, right = st.columns(2)

with left:
    demand_choice = st.selectbox(
        "Demand heatmap",
        list(DEMAND_MAPS),
    )
    show_map(DEMAND_MAPS[demand_choice])

with right:
    flow_choice = st.selectbox(
        "Tourism flow map",
        list(FLOW_MAPS),
    )
    show_map(FLOW_MAPS[flow_choice])


# 3 BOOKING AND TRANSPORT
show_section("3 · Booking & transport intelligence")

left, right = st.columns(2)

with left:
    if not bookings.empty:
        hourly = (
            bookings.groupby("hour", as_index=False)[
                "total_bookings"
            ]
            .sum()
        )

        fig = px.bar(
            hourly,
            x="hour",
            y="total_bookings",
            title="Bookings by hour",
            labels={
                "hour": "Hour of day",
                "total_bookings": "Bookings",
            },
        )
        show_chart(fig)

        avg_wait = numeric(
            bookings, "avg_wait_time_mins"
        ).mean()

        total_bookings = numeric(
            bookings, "total_bookings"
        ).sum()

        cancellation_rate = (
            numeric(
                bookings, "cancelled_visits"
            ).sum()
            / max(total_bookings, 1)
            * 100
        )

        st.caption(
            f"Average queue wait: {avg_wait:.1f} min · "
            f"Cancellation rate: {cancellation_rate:.1f}%"
        )

with right:
    if not transport.empty:
        stands = (
            transport.groupby(
                "stand_name", as_index=False
            )["trips_completed"]
            .sum()
            .nlargest(10, "trips_completed")
        )

        fig = px.bar(
            stands,
            x="trips_completed",
            y="stand_name",
            orientation="h",
            title="Top stands by completed trips",
            labels={
                "stand_name": "",
                "trips_completed": "Completed trips",
            },
        )
        show_chart(fig)

# 4 WEATHER AND MODAL SUBSTITUTION
show_section("4 · Weather sensitivity & modal substitution")

mode_columns = [
    "car_pct",
    "bus_pct",
    "metro_pct",
    "ebikes_bikes_pct",
    "shuttle_walk_pct",
]

left, right = st.columns(2)

if not modal.empty:
    for column in mode_columns:
        modal[column] = numeric(modal, column)

    with left:
        weather_shares = (
            modal.groupby(
                "weather_condition",
                as_index=False,
            )[mode_columns]
            .mean()
        )

        weather_long = weather_shares.melt(
            id_vars="weather_condition",
            var_name="Mode",
            value_name="Mean share (%)",
        )

        fig = px.bar(
            weather_long,
            x="weather_condition",
            y="Mean share (%)",
            color="Mode",
            barmode="stack",
            title="Average mode share by weather",
        )
        show_chart(fig, height=360)

    with right:
        shares = modal[mode_columns].mean()

        fig = px.pie(
            names=[
                "Car",
                "Bus",
                "Metro",
                "E-bike / bike",
                "Shuttle / walk",
            ],
            values=shares.values,
            hole=0.55,
            title="Mean modal share in loaded view",
        )
        show_chart(fig)

# 5 TRAFFIC INTELLIGENCE
show_section(
    "5 · Traffic intelligence overview",
    "Historical traffic-state analysis from Supabase fact_modal_shift_weather. "
    "This is analytical traffic intelligence, not real-time road-sensor monitoring.",
)

traffic_required = {
    "traffic_level", "weather_condition", "aqi", "rainfall_mm",
    "car_pct", "bus_pct", "metro_pct", "ebikes_bikes_pct", "shuttle_walk_pct"
}

if traffic_required.issubset(modal.columns):
    traffic = modal.copy()
    traffic["traffic_level"] = traffic["traffic_level"].astype(str).str.strip()
    traffic = traffic[traffic["traffic_level"].ne("")]

    traffic_order = ["Low Traffic", "Moderate Traffic", "Heavy Congestion"]
    available_traffic = [level for level in traffic_order if level in traffic["traffic_level"].unique()]
    available_traffic += sorted(set(traffic["traffic_level"].dropna().unique()) - set(available_traffic))

    selected_traffic = st.multiselect(
        "Traffic conditions included in the overview",
        available_traffic,
        default=available_traffic,
        key="executive_traffic_filter",
    )
    traffic = traffic[traffic["traffic_level"].isin(selected_traffic)].copy()

    if traffic.empty:
        st.info("Select at least one traffic condition to view the analysis.")
    else:
        for column in ["aqi", "rainfall_mm", *mode_columns]:
            traffic[column] = numeric(traffic, column)

        heavy_share = traffic["traffic_level"].eq("Heavy Congestion").mean() * 100
        dominant_traffic = traffic["traffic_level"].mode().iloc[0]

        ti1, ti2, ti3, ti4 = st.columns(4)
        ti1.metric("Dominant traffic state", dominant_traffic)
        ti2.metric("Heavy congestion share", f"{heavy_share:.1f}%")
        ti3.metric("Average AQI", f"{traffic['aqi'].mean():.0f}")
        ti4.metric("Average rainfall", f"{traffic['rainfall_mm'].mean():.1f} mm")

        traffic_counts = (
            traffic["traffic_level"].value_counts()
            .rename_axis("traffic_level")
            .reset_index(name="records")
        )
        traffic_counts["traffic_level"] = pd.Categorical(
            traffic_counts["traffic_level"], categories=traffic_order, ordered=True
        )
        traffic_counts = traffic_counts.sort_values("traffic_level")

        left, right = st.columns(2)
        with left:
            fig = px.bar(
                traffic_counts,
                x="traffic_level",
                y="records",
                color="traffic_level",
                title="Traffic condition distribution",
                labels={"traffic_level": "Traffic condition", "records": "Observations"},
            )
            show_chart(fig, height=360)

        with right:
            traffic_modes = traffic.groupby("traffic_level", as_index=False)[mode_columns].mean()
            traffic_modes = traffic_modes.melt(
                id_vars="traffic_level",
                value_vars=mode_columns,
                var_name="Mode",
                value_name="Mean share (%)",
            )
            fig = px.bar(
                traffic_modes,
                x="traffic_level",
                y="Mean share (%)",
                color="Mode",
                barmode="stack",
                title="Modal share by traffic condition",
            )
            show_chart(fig, height=360)

        weather_traffic = pd.crosstab(traffic["weather_condition"], traffic["traffic_level"])
        fig = px.imshow(
            weather_traffic,
            text_auto=True,
            aspect="auto",
            color_continuous_scale="YlOrRd",
            title="Weather–traffic interaction matrix",
            labels={"x": "Traffic condition", "y": "Weather condition", "color": "Observations"},
        )
        show_chart(fig, height=390)

        st.markdown("#### Place and Tourism-Season Congestion")
        st.caption(
            "Peak Season follows the Milestone 2 calendar rule (October–March); "
            "Off-Peak Season covers April–September."
        )

        place_col, season_col = st.columns(2)
        with place_col:
            if {"city", "state"}.issubset(traffic.columns):
                place_summary = (
                    traffic.dropna(subset=["city"])
                    .assign(heavy_record=traffic["traffic_level"].eq("Heavy Congestion").astype(int))
                    .groupby(["city", "state"], as_index=False)
                    .agg(records=("traffic_level", "size"), heavy_records=("heavy_record", "sum"))
                )
                place_summary["Heavy congestion (%)"] = (
                    place_summary["heavy_records"] / place_summary["records"] * 100
                )
                place_summary["Place"] = place_summary["city"] + ", " + place_summary["state"]
                top_places = place_summary.nlargest(10, ["Heavy congestion (%)", "records"])
                fig = px.bar(
                    top_places.sort_values("Heavy congestion (%)"),
                    x="Heavy congestion (%)",
                    y="Place",
                    orientation="h",
                    color="Heavy congestion (%)",
                    color_continuous_scale="Reds",
                    hover_data={"records": True},
                    title="Top Places by Heavy-Congestion Rate",
                )
                show_chart(fig, height=410)
            else:
                st.info("Location fields are unavailable for place-level traffic analysis.")

        with season_col:
            season_summary = (
                traffic.assign(heavy_record=traffic["traffic_level"].eq("Heavy Congestion").astype(int))
                .groupby("Season", as_index=False)
                .agg(records=("traffic_level", "size"), heavy_records=("heavy_record", "sum"))
            )
            season_summary["Heavy congestion (%)"] = (
                season_summary["heavy_records"] / season_summary["records"] * 100
            )
            fig = px.bar(
                season_summary,
                x="Season",
                y="Heavy congestion (%)",
                color="Season",
                text_auto=".1f",
                hover_data={"records": True},
                title="Peak vs Off-Peak Congestion",
            )
            show_chart(fig, height=410)

        if {"city", "Season"}.issubset(traffic.columns):
            top_cities = traffic.dropna(subset=["city"])["city"].value_counts().head(12).index
            city_season = (
                traffic[traffic["city"].isin(top_cities)]
                .assign(heavy_record=lambda frame: frame["traffic_level"].eq("Heavy Congestion").astype(int))
                .groupby(["city", "Season"], as_index=False)["heavy_record"].mean()
            )
            city_season["Heavy congestion (%)"] = city_season["heavy_record"] * 100
            matrix = city_season.pivot(
                index="city", columns="Season", values="Heavy congestion (%)"
            )
            fig = px.imshow(
                matrix,
                text_auto=".1f",
                aspect="auto",
                color_continuous_scale="YlOrRd",
                title="City × Tourism Season Heavy-Congestion Rate (%)",
                labels={"x": "Tourism season", "y": "City", "color": "Heavy congestion (%)"},
            )
            show_chart(fig, height=430)
else:
    st.warning("Traffic intelligence fields are unavailable from fact_modal_shift_weather.")


# 6 MOBILITY ACCESS AND EQUITY
show_section(
    "6 · Mobility access & equity",
    "Index formula from Milestone 4: "
    "30% supply + 30% usage + 40% demand score.",
)

if not transport.empty:
    equity = transport.copy()

    equity["vehicles_available"] = numeric(
        equity, "vehicles_available"
    )
    equity["trips_completed"] = numeric(
        equity, "trips_completed"
    )

    demand_scores = {
        "low": 30,
        "medium": 60,
        "high": 100,
    }

    equity["demand_score"] = (
        equity["demand_level"]
        .astype(str)
        .str.lower()
        .str.strip()
        .map(demand_scores)
        .fillna(60)
    )

    zones = (
        equity.groupby(
            ["location_id", "city", "stand_name"],
            as_index=False,
        )
        .agg(
            vehicles_available=(
                "vehicles_available", "sum"
            ),
            trips_completed=(
                "trips_completed", "sum"
            ),
            demand_score=(
                "demand_score", "mean"
            ),
        )
    )

    zones["trips_per_vehicle"] = (
        zones["trips_completed"]
        / zones["vehicles_available"].clip(lower=1)
    )

    max_vehicles = max(
        zones["vehicles_available"].max(), 1
    )
    max_usage = max(
        zones["trips_per_vehicle"].max(), 1
    )

    zones["supply_score"] = (
        zones["vehicles_available"]
        / max_vehicles
        * 100
    )

    zones["usage_score"] = (
        zones["trips_per_vehicle"]
        / max_usage
        * 100
    )

    zones["access_index"] = (
        0.30 * zones["supply_score"]
        + 0.30 * zones["usage_score"]
        + 0.40 * zones["demand_score"]
    )

    zones["label"] = (
        zones["city"].astype(str)
        + " · "
        + zones["stand_name"].astype(str)
    )

    st.metric(
        "Average mobility access index",
        f"{zones['access_index'].mean():.1f} / 100",
    )

    top_zones = zones.nlargest(
        15, "access_index"
    )

    fig = px.bar(
        top_zones,
        x="access_index",
        y="label",
        orientation="h",
        color="access_index",
        color_continuous_scale="Blues",
        labels={
            "access_index": "Access index",
            "label": "",
        },
    )
    show_chart(fig, height=410)


# 7 FORECAST AND ANOMALIES
show_section(
    "7 · Demand forecasting & anomaly alerts",
    "Historical seven-day rolling projection × 1.05, "
    "with bounds based on ±1.5 rolling standard deviations. "
    "This is not a trained machine-learning forecast.",
)

daily = pd.DataFrame()

if not bookings.empty:
    daily = (
        bookings.dropna(
            subset=["booking_date"]
        )
        .groupby(
            "booking_date", as_index=False
        )["total_bookings"]
        .sum()
        .sort_values("booking_date")
    )

    if not daily.empty:
        daily["baseline"] = (
            daily["total_bookings"]
            .rolling(7, min_periods=1)
            .mean()
        )

        daily["rolling_std"] = (
            daily["total_bookings"]
            .rolling(7, min_periods=2)
            .std()
            .fillna(0)
        )

        daily["forecast"] = (
            daily["baseline"] * 1.05
        )

        daily["upper_bound"] = (
            daily["baseline"]
            + 1.5 * daily["rolling_std"]
        )

        daily["lower_bound"] = (
            daily["baseline"]
            - 1.5 * daily["rolling_std"]
        ).clip(lower=0)

        daily["z_score"] = (
            (
                daily["total_bookings"]
                - daily["baseline"]
            )
            / daily["rolling_std"].replace(
                0, float("nan")
            )
        )

        anomalies = daily[
            daily["z_score"].abs() > 1.2
        ].copy()

        left, right = st.columns([2, 1])

        with left:
            fig = go.Figure()

            for field, label, line_style in [
                (
                    "total_bookings",
                    "Actual",
                    "solid",
                ),
                (
                    "forecast",
                    "Projection",
                    "dash",
                ),
                (
                    "upper_bound",
                    "Upper bound",
                    "dot",
                ),
                (
                    "lower_bound",
                    "Lower bound",
                    "dot",
                ),
            ]:
                fig.add_trace(
                    go.Scatter(
                        x=daily["booking_date"],
                        y=daily[field],
                        name=label,
                        mode="lines",
                        line=dict(
                            dash=line_style
                        ),
                    )
                )

            show_chart(fig, height=350)

        with right:
            st.metric(
                "Detected deviations",
                len(anomalies),
            )

            if anomalies.empty:
                st.success(
                    "No deviations above the "
                    "selected threshold."
                )
            else:
                anomalies["Alert"] = (
                    anomalies["z_score"]
                    .apply(
                        lambda score: (
                            "Demand surge"
                            if score > 0
                            else "Demand drop"
                        )
                    )
                )

                st.dataframe(
                    anomalies[
                        [
                            "booking_date",
                            "total_bookings",
                            "forecast",
                            "Alert",
                        ]
                    ]
                    .sort_values(
                        "booking_date",
                        ascending=False,
                    )
                    .head(12),
                    hide_index=True,
                    use_container_width=True,
                )


# 8 REPORT EXPORTS
show_section("8 · Reports & exports")

export_columns = st.columns(3)

exports = [
    (
        "Download bookings view",
        bookings,
        "bookings_view.csv",
    ),
    (
        "Download transport view",
        transport,
        "transport_view.csv",
    ),
    (
        "Download forecast",
        daily,
        "demand_forecast.csv",
    ),
]

for column, (label, dataframe, filename) in zip(
    export_columns, exports
):
    column.download_button(
        label=label,
        data=dataframe.to_csv(
            index=False
        ).encode("utf-8"),
        file_name=filename,
        mime="text/csv",
        disabled=dataframe.empty,
    )


st.divider()

st.markdown(
    """
    <div style="text-align: center;">
        <strong>Team 1</strong><br>
        Padma Priya · Aditi Dhuria ·
        Madhusri Gone · Chaithanya E V · Raj Chandravanshi
    </div>
    """,
    unsafe_allow_html=True,
)
