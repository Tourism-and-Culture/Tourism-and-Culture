from pathlib import Path

import pandas as pd
import streamlit as st
from supabase import create_client


st.set_page_config(
    page_title="Milestone 1 | Smart Urban Mobility and Traffic Intelligence",
    page_icon="🏙️",
    layout="wide",
)


def read_supabase_secrets():
    """Support both secret formats used across the milestone applications."""
    try:
        return st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"]
    except (KeyError, TypeError):
        try:
            return st.secrets["supabase"]["url"], st.secrets["supabase"]["key"]
        except (KeyError, TypeError):
            st.error(
                "Supabase secrets are missing. Add SUPABASE_URL and SUPABASE_KEY "
                "to `.streamlit/secrets.toml`."
            )
            st.stop()


SUPABASE_URL, SUPABASE_KEY = read_supabase_secrets()


@st.cache_resource
def get_supabase_client():
    return create_client(SUPABASE_URL, SUPABASE_KEY)


@st.cache_data(ttl=300, show_spinner=False)
def fetch_table(table_name):
    response = get_supabase_client().table(table_name).select("*").execute()
    return pd.DataFrame(response.data or [])


def numeric_sum(frame, column):
    if frame.empty or column not in frame.columns:
        return 0
    return pd.to_numeric(frame[column], errors="coerce").fillna(0).sum()


def option_list(frame, column):
    if frame.empty or column not in frame.columns:
        return ["All"]
    values = sorted(frame[column].dropna().astype(str).unique().tolist())
    return ["All", *values]


def filter_equals(frame, column, value):
    if value == "All" or frame.empty or column not in frame.columns:
        return frame
    return frame[frame[column].astype(str) == str(value)]


st.markdown(
    """
    <div style="text-align:center; padding:0.4rem 0 0.6rem 0">
      <h1 style="margin-bottom:0.2rem">Smart Urban Mobility and Traffic Intelligence Dashboard</h1>
      <div style="font-size:1.15rem; color:#64748b; font-weight:600">
        Tourism and Cultural Intelligence Use Case
      </div>
      <div style="margin-top:0.45rem; letter-spacing:0.16rem; color:#2563eb; font-weight:700">
        MILESTONE 1 · DATA FOUNDATION
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.info(
    "Milestone 1 establishes the Supabase data foundation and the original Power BI "
    "prototype used for tourism and cultural analysis."
)


try:
    with st.spinner("Loading validated project data from Supabase..."):
        attractions = fetch_table("fact_attractions")
        monthly = fetch_table("fact_monthly_tourism")
        festivals = fetch_table("fact_festivals")
        locations = fetch_table("dim_location")
except Exception as error:
    st.error(f"Unable to load Milestone 1 data from Supabase: {error}")
    st.caption(
        "Check the URL/key in `.streamlit/secrets.toml`, confirm the four tables exist, "
        "and ensure their Supabase read policies allow access. No CSV or synthetic fallback is used."
    )
    st.stop()


if attractions.empty or monthly.empty or festivals.empty:
    st.error(
        "Supabase connected successfully, but one or more required tables returned no rows: "
        "fact_attractions, fact_monthly_tourism, fact_festivals."
    )
    st.stop()


# Remove impossible ratings before calculating attraction metrics.
if "google_rating" in attractions.columns:
    attractions["google_rating"] = pd.to_numeric(
        attractions["google_rating"], errors="coerce"
    )
    attractions = attractions[
        attractions["google_rating"].between(0, 5, inclusive="both")
    ].copy()

if (
    not locations.empty
    and "location_id" in attractions.columns
    and "location_id" in locations.columns
):
    location_columns = [
        column
        for column in ["location_id", "state", "city"]
        if column in locations.columns
    ]
    attractions = attractions.merge(
        locations[location_columns].drop_duplicates("location_id"),
        on="location_id",
        how="left",
        suffixes=("", "_location"),
    )
    for column in ["state", "city"]:
        location_column = f"{column}_location"
        if location_column in attractions.columns:
            if column in attractions.columns:
                attractions[column] = attractions[column].fillna(attractions[location_column])
            else:
                attractions[column] = attractions[location_column]
            attractions.drop(columns=location_column, inplace=True)


st.sidebar.header("Filters")
year_values = set()
for frame in (monthly, festivals):
    if "year" in frame.columns:
        year_values.update(frame["year"].dropna().astype(str).tolist())
selected_year = st.sidebar.selectbox("Year", ["All", *sorted(year_values)])
selected_state = st.sidebar.selectbox("State", option_list(attractions, "state"))
city_source = filter_equals(attractions, "state", selected_state)
selected_city = st.sidebar.selectbox("City", option_list(city_source, "city"))
selected_category = st.sidebar.selectbox("Attraction category", option_list(attractions, "category"))

if st.sidebar.button("Refresh Supabase data", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

st.sidebar.caption(
    "Year filters tourism and festival records. State, city and category filter attraction metrics."
)


filtered_attractions = filter_equals(attractions, "state", selected_state)
filtered_attractions = filter_equals(filtered_attractions, "city", selected_city)
filtered_attractions = filter_equals(filtered_attractions, "category", selected_category)
filtered_monthly = filter_equals(monthly, "year", selected_year)
filtered_festivals = filter_equals(festivals, "year", selected_year)

total_attractions = len(filtered_attractions)
total_arrivals = int(numeric_sum(filtered_monthly, "foreign_tourist_arrivals"))
total_revenue = numeric_sum(filtered_monthly, "tourism_revenue_crore_inr")
festival_records = len(filtered_festivals)
average_rating = (
    filtered_attractions["google_rating"].mean()
    if "google_rating" in filtered_attractions.columns and not filtered_attractions.empty
    else float("nan")
)
average_entry_fee = (
    pd.to_numeric(filtered_attractions["entry_fee"], errors="coerce").mean()
    if "entry_fee" in filtered_attractions.columns and not filtered_attractions.empty
    else float("nan")
)

st.subheader("Validated Supabase KPIs")
k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Tourist Places", f"{total_attractions:,}")
k2.metric("Foreign Tourist Arrivals", f"{total_arrivals / 1_000_000:.1f}M")
k3.metric("Tourism Revenue", f"₹{total_revenue:,.0f} Cr")
k4.metric("Festival Records", f"{festival_records:,}")
k5.metric("Average Rating", "—" if pd.isna(average_rating) else f"{average_rating:.2f}")
k6.metric(
    "Average Entry Fee",
    "—" if pd.isna(average_entry_fee) else f"₹{average_entry_fee:,.0f}",
)
st.caption(
    "These cards are calculated directly from the current Supabase tables. Attraction "
    "ratings are validated to the 0–5 range before aggregation."
)


st.divider()
st.subheader("Original Power BI Prototype")
st.caption(
    "This is the original Milestone 1 implementation and is retained as project evidence. "
    "Its snapshot values reflect the earlier prototype; the KPI cards above show the current "
    "validated Supabase results."
)

base_dir = Path(__file__).resolve().parent
project_root = base_dir.parent if base_dir.name == "pages" else base_dir
image_candidates = [
    project_root / "images" / "milestone1_powerbi_dashboard.png",
    project_root / "MicrosoftTeams-image.png",
    base_dir / "milestone1_powerbi_dashboard.png",
    base_dir / "MicrosoftTeams-image.png",
]
power_bi_image = next((path for path in image_candidates if path.exists()), None)

if power_bi_image:
    st.image(
        str(power_bi_image),
        caption="Milestone 1 — Tourism and Cultural Analysis Dashboard built in Power BI",
        use_container_width=True,
    )
else:
    st.warning(
        "Power BI image not found. Save the supplied image as "
        "`images/milestone1_powerbi_dashboard.png` in the project repository."
    )


st.divider()
st.subheader("Data Foundation")
c1, c2, c3, c4 = st.columns(4)
c1.markdown("**Database**  \nSupabase PostgreSQL")
c2.markdown("**Model**  \nGalaxy schema")
c3.markdown("**Core facts**  \nTourism · Attractions · Festivals")
c4.markdown("**Shared dimensions**  \nTime · Location · Country · Weather")

with st.expander("How Milestone 1 connects to the rest of the project"):
    st.markdown(
        """
        - **Milestone 2:** geospatial tourism, demand heatmaps and weather overlays
        - **Milestone 3:** booking, transport, modal substitution and traffic intelligence
        - **Milestone 4:** mobility access, forecasting, anomaly detection and reporting
        - **Executive Dashboard:** integrated decision-support view across all milestones
        """
    )

st.success(
    "Milestone 1 complete: a validated Supabase data foundation with the original Power BI prototype."
)
st.caption(
    "Team 1 · Padma Priya · Aditi Dhuria · Madhusri Gone · Chaithanya E V · Raj Chandravanshi"
)
