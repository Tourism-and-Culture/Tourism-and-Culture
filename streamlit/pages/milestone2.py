from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
from supabase import create_client, Client


# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="Smart Tourism & Cultural Intelligence Platform",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# 3. SUPABASE CONNECTION & CONFIGURATION
# ============================================================
SUPABASE_URL = st.secrets.get("SUPABASE_URL")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY")

@st.cache_resource
def init_supabase() -> Client:
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()


# ============================================================
# 4. LOAD DATA DIRECTLY FROM SUPABASE TABLES
# ============================================================
@st.cache_data(ttl=600)
def load_data():
    if not supabase:
        raise ValueError("Supabase credentials not configured in Streamlit secrets.")
        
    def fetch_table(table_name):
        response = supabase.table(table_name).select("*").execute()
        return pd.DataFrame(response.data)

    dim_country = fetch_table("dim_country")
    dim_location = fetch_table("dim_location")
    dim_time = fetch_table("dim_time")
    dim_weather = fetch_table("dim_weather")
    attractions = fetch_table("fact_attractions")
    country_arrivals = fetch_table("fact_country_arrivals")
    festivals = fetch_table("fact_festivals")
    monthly = fetch_table("fact_monthly_tourism")
    galaxy = fetch_table("view_galaxy_monthly_tourism")
    weather_tourism = fetch_table("view_weather_tourism_analysis")

    # Numeric cleanup
    for df, cols in [
        (dim_location, ["latitude", "longitude"]),
        (attractions, ["google_rating", "entry_fee"]),
        (country_arrivals, ["arrivals_in_numbers", "average_duration_of_stay_in_days"]),
        (festivals, ["amount_sanctioned", "amount_released"]),
        (monthly, ["tourism_revenue_crore_inr", "foreign_tourist_arrivals"]),
        (galaxy, ["tourism_revenue_crore_inr", "foreign_tourist_arrivals"]),
        (
            weather_tourism,
            [
                "tourism_revenue_crore_inr",
                "foreign_tourist_arrivals",
                "temp_c",
                "rainfall_mm",
                "humidity_pct",
            ],
        ),
        (
            dim_weather,
            ["temp_c", "rainfall_mm", "humidity_pct"],
        ),
    ]:
        for col in cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

    if "google_rating" in attractions.columns:
        attractions = attractions[
            attractions["google_rating"].between(0, 5, inclusive="both")
        ].copy()

    # Join attraction + location.
    attr = attractions.merge(
        dim_location,
        on="location_id",
        how="left",
        suffixes=("", "_location"),
    )

    # Join country arrivals + country dimension.
    countries = country_arrivals.merge(
        dim_country,
        on="country_id",
        how="left",
    )

    # Time enrichment.
    time = dim_time.copy()
    if "month_name" in time.columns:
        time["Season"] = time["month_name"].apply(
            lambda m: (
                "Peak Season"
                if m in [
                    "October", "November", "December",
                    "January", "February", "March",
                ]
                else "Off-Peak Season"
            )
        )

    time_lookup = time[[
        "time_id", "year", "month_name", "month_num", "quarter", "Season"
    ]].copy() if all(c in time.columns for c in ["time_id", "year", "month_name", "month_num", "quarter", "Season"]) else time

    monthly_enriched = monthly.merge(
        time_lookup,
        on="time_id",
        how="left",
        suffixes=("", "_time"),
    ) if "time_id" in monthly.columns and "time_id" in time_lookup.columns else monthly

    for col in ["year", "month_name", "month_num", "quarter", "Season"]:
        dim_col = f"{col}_time"
        if col not in monthly_enriched.columns and dim_col in monthly_enriched.columns:
            monthly_enriched.rename(columns={dim_col: col}, inplace=True)
        elif col in monthly_enriched.columns and dim_col in monthly_enriched.columns:
            monthly_enriched[col] = monthly_enriched[col].combine_first(
                monthly_enriched[dim_col]
            )
            monthly_enriched.drop(columns=[dim_col], inplace=True)

    if "year" in monthly_enriched.columns:
        monthly_enriched["year"] = pd.to_numeric(
            monthly_enriched["year"], errors="coerce"
        )

    galaxy_enriched = galaxy.copy()
    if "month_name" in galaxy_enriched.columns:
        galaxy_enriched["Season"] = galaxy_enriched["month_name"].apply(
            lambda m: (
                "Peak Season"
                if m in [
                    "October", "November", "December",
                    "January", "February", "March",
                ]
                else "Off-Peak Season"
            )
        )

    weather_geo = weather_tourism.merge(
        dim_location[["city", "state", "latitude", "longitude"]],
        left_on="location_name",
        right_on="city",
        how="left",
    ) if "location_name" in weather_tourism.columns and "city" in dim_location.columns else weather_tourism

    return {
        "dim_country": dim_country,
        "dim_location": dim_location,
        "dim_time": time,
        "dim_weather": dim_weather,
        "attractions": attr,
        "countries": countries,
        "festivals": festivals,
        "monthly": monthly_enriched,
        "galaxy": galaxy_enriched,
        "weather": weather_geo,
    }


try:
    data = load_data()
except Exception as exc:
    st.error(f"Error loading data from Supabase: {exc}")
    st.stop()


attr = data["attractions"]
countries = data["countries"]
festivals = data["festivals"]
monthly = data["monthly"]
weather = data["weather"]
dim_time = data["dim_time"]


# ============================================================
# 5. HELPER FUNCTIONS
# ============================================================
COLORS = {
    "cyan": "#58A6FF", "blue": "#1F6FEB", "teal": "#3FB950",
    "gold": "#D29922", "green": "#238636", "red": "#DA3633",
    "purple": "#8957E5", "orange": "#F0883E", "text": "#FAFAFA",
    "muted": "#8B949E", "grid": "#30363D", "panel": "#161B22",
    "bg": "#0E1117",
}


def format_number(value):
    if pd.isna(value):
        return "—"
    value = float(value)
    if abs(value) >= 1_000_000_000:
        return f"{value / 1_000_000_000:.2f}B"
    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    if abs(value) >= 1_000:
        return f"{value / 1_000:.1f}K"
    return f"{value:,.0f}"


MONTH_ORDER = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]


def month_sort(df, col="month_name"):
    out = df.copy()
    if col in out.columns:
        out[col] = pd.Categorical(out[col], categories=MONTH_ORDER, ordered=True)
        out = out.sort_values(col)
    return out


def chart_layout(fig, height=330, title=None):
    fig.update_layout(
        title=dict(text=title or "", x=0.02, xanchor="left", font=dict(size=14, color=COLORS["text"], family="Helvetica, Arial, sans-serif")),
        height=height, paper_bgcolor=COLORS["panel"], plot_bgcolor=COLORS["panel"],
        font=dict(color=COLORS["text"], size=11, family="Helvetica, Arial, sans-serif"),
        margin=dict(l=65, r=35, t=65 if title else 20, b=55),
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0, bgcolor="rgba(0,0,0,0)", font=dict(color=COLORS["muted"], size=10)),
        hoverlabel=dict(bgcolor="#21262D", bordercolor="#30363D", font_color="#FFFFFF"),
        xaxis=dict(gridcolor=COLORS["grid"], zeroline=False, automargin=True, tickfont=dict(color=COLORS["muted"]), title_font=dict(color=COLORS["text"]), linecolor="#30363D"),
        yaxis=dict(gridcolor=COLORS["grid"], zeroline=False, automargin=True, tickfont=dict(color=COLORS["muted"]), title_font=dict(color=COLORS["text"]), linecolor="#30363D"),
    )
    return fig


def empty_chart(message="No data available for the selected filters."):
    fig = go.Figure()
    fig.add_annotation(
        text=message, x=0.5, y=0.5, xref="paper", yref="paper",
        showarrow=False, font=dict(color=COLORS["muted"], size=12, family="Helvetica, Arial, sans-serif"),
    )
    chart_layout(fig, height=300)
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return fig


# ============================================================
# 6. SIDEBAR FILTERS
# ============================================================
st.sidebar.title("🔍 Filters")
st.sidebar.markdown("Configure global parameters to filter tourism & cultural metrics.")

st.sidebar.subheader("Year")
years = sorted(monthly["year"].dropna().unique().astype(int).tolist()) if "year" in monthly.columns else []
selected_year = st.sidebar.selectbox("Select Year", ["All"] + years)

st.sidebar.subheader("Quarter")
quarters = ["All", "Q1", "Q2", "Q3", "Q4"]
selected_quarter = st.sidebar.selectbox("Select Quarter", quarters)

st.sidebar.subheader("Month")
months = ["All"] + MONTH_ORDER
selected_month = st.sidebar.selectbox("Select Month", months)

st.sidebar.subheader("Season")
selected_season = st.sidebar.selectbox(
    "Select Season",
    ["All", "Peak Season", "Off-Peak Season"],
)

st.sidebar.subheader("State")
states = ["All"] + sorted(attr["state"].dropna().astype(str).unique()) if "state" in attr.columns else ["All"]
selected_state = st.sidebar.selectbox("Select State", states)

if selected_state != "All" and "state" in attr.columns and "city" in attr.columns:
    city_values = sorted(
        attr.loc[attr["state"] == selected_state, "city"]
        .dropna().astype(str).unique()
    )
else:
    city_values = sorted(attr["city"].dropna().astype(str).unique()) if "city" in attr.columns else []

st.sidebar.subheader("City")
selected_city = st.sidebar.selectbox("Select City", ["All"] + city_values)

st.sidebar.subheader("Category")
categories = ["All"] + sorted(
    attr["category"].dropna().astype(str).unique()
) if "category" in attr.columns else ["All"]
selected_category = st.sidebar.selectbox("Select Category", categories)

st.sidebar.subheader("Country")
country_values = sorted(
    countries.loc[
        ~countries["country_name"].astype(str).str.strip().isin(["Total", "Others"]),
        "country_name",
    ].dropna().astype(str).unique()
) if "country_name" in countries.columns else []
selected_country = st.sidebar.selectbox("Select Country", ["All"] + country_values)

st.sidebar.markdown("---")
st.sidebar.caption("Source: Live Supabase database integration.")


# ============================================================
# 7. APPLY FILTERS
# ============================================================
filtered_attr = attr.copy()
if selected_state != "All" and "state" in filtered_attr.columns:
    filtered_attr = filtered_attr[filtered_attr["state"] == selected_state]
if selected_city != "All" and "city" in filtered_attr.columns:
    filtered_attr = filtered_attr[filtered_attr["city"] == selected_city]
if selected_category != "All" and "category" in filtered_attr.columns:
    filtered_attr = filtered_attr[filtered_attr["category"] == selected_category]


filtered_monthly = monthly.copy()
if selected_year != "All" and "year" in filtered_monthly.columns:
    filtered_monthly = filtered_monthly[filtered_monthly["year"] == int(selected_year)]
if selected_quarter != "All" and "quarter" in filtered_monthly.columns:
    filtered_monthly = filtered_monthly[filtered_monthly["quarter"] == selected_quarter]
if selected_month != "All" and "month_name" in filtered_monthly.columns:
    filtered_monthly = filtered_monthly[filtered_monthly["month_name"] == selected_month]
if selected_season != "All" and "Season" in filtered_monthly.columns:
    filtered_monthly = filtered_monthly[filtered_monthly["Season"] == selected_season]


filtered_country = countries.copy()
if "country_name" in filtered_country.columns:
    filtered_country = filtered_country[
        ~filtered_country["country_name"].astype(str).str.strip().isin(["Total", "Others"])
    ].copy()
    if selected_country != "All":
        filtered_country = filtered_country[filtered_country["country_name"] == selected_country]


filtered_festivals = festivals.copy()
if selected_state != "All" and "state" in filtered_festivals.columns:
    filtered_festivals = filtered_festivals[
        filtered_festivals["state"].astype(str).str.contains(selected_state, na=False)
    ]
if selected_year != "All" and "year" in filtered_festivals.columns:
    filtered_festivals = filtered_festivals[
        filtered_festivals["year"].astype(str).str.startswith(str(selected_year))
    ]


filtered_weather = weather.copy()
if selected_year != "All" and "year" in filtered_weather.columns:
    filtered_weather = filtered_weather[filtered_weather["year"] == int(selected_year)]
if selected_month != "All" and "month" in filtered_weather.columns:
    filtered_weather = filtered_weather[filtered_weather["month"] == selected_month]
if selected_state != "All" and "state" in filtered_weather.columns:
    filtered_weather = filtered_weather[
        filtered_weather["state"].astype(str).str.contains(selected_state, na=False)
    ]
if selected_city != "All" and "city" in filtered_weather.columns:
    filtered_weather = filtered_weather[
        filtered_weather["city"].astype(str).str.contains(selected_city, na=False)
    ]


# ============================================================
# 8. HEADER BLOCK
# ============================================================
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
            Geospatial, Weather &amp; Transit Analytics
        </h4>
    </div>
    """,
    unsafe_allow_html=True
)
st.divider()


# ============================================================
# 9. KPI CARDS
# ============================================================
total_places = len(filtered_attr)
avg_rating = filtered_attr["google_rating"].mean() if not filtered_attr.empty and "google_rating" in filtered_attr.columns else 0
avg_fee = filtered_attr["entry_fee"].mean() if not filtered_attr.empty and "entry_fee" in filtered_attr.columns else 0
foreign_arrivals = (
    filtered_monthly["foreign_tourist_arrivals"].sum()
    if not filtered_monthly.empty and "foreign_tourist_arrivals" in filtered_monthly.columns
    else 0
)
revenue = (
    filtered_monthly["tourism_revenue_crore_inr"].sum()
    if not filtered_monthly.empty and "tourism_revenue_crore_inr" in filtered_monthly.columns
    else 0
)
festival_count = len(filtered_festivals)

k1, k2, k3, k4, k5, k6 = st.columns(6)

k1.metric("Tourist Places", format_number(total_places))
k2.metric("Average Rating", f"{avg_rating:.2f} / 5")
k3.metric("Average Entry Fee", f"₹{avg_fee:,.0f}")
k4.metric("Foreign Arrivals", format_number(foreign_arrivals))
k5.metric("Tourism Revenue", f"₹{revenue:,.0f} Cr")
k6.metric("Festival Records", format_number(festival_count))


# ============================================================
# 10. MAIN DEMAND & GEOGRAPHY
# ============================================================
st.markdown(
    '<div class="section-title">Demand & Geographic Intelligence</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="section-note">Attraction density, location distribution and geographic drill-down.</div>',
    unsafe_allow_html=True,
)

map_col, cat_col = st.columns([1.55, 1])

with map_col:
    st.markdown("**Tourist Attraction Density Map**")
    if not filtered_attr.empty and {"latitude", "longitude"}.issubset(filtered_attr.columns):
        map_df = filtered_attr.dropna(subset=["latitude", "longitude"]).copy()

        if not map_df.empty:
            m = folium.Map(
                location=[map_df["latitude"].mean(), map_df["longitude"].mean()],
                zoom_start=5,
                tiles="CartoDB positron",
            )

            location_density = (
                map_df.groupby(["latitude", "longitude"])
                .size()
                .reset_index(name="attraction_count")
            )

            heat_data = [
                [r.latitude, r.longitude, r.attraction_count]
                for r in location_density.itertuples()
            ]

            HeatMap(heat_data, radius=20, blur=18, min_opacity=0.35, max_zoom=8).add_to(m)

            for row in (
                map_df.groupby(["location_id", "state", "city", "latitude", "longitude"])
                .agg(attractions=("place_name", "count"), avg_rating=("google_rating", "mean"))
                .reset_index()
                .itertuples()
            ):
                folium.CircleMarker(
                    location=[row.latitude, row.longitude],
                    radius=max(4, min(10, row.attractions)),
                    tooltip=f"{row.city}, {row.state}",
                    popup=f"<b>{row.city}</b><br>{row.state}<br>Attractions: {row.attractions}<br>Avg rating: {row.avg_rating:.2f}",
                    color=COLORS["cyan"],
                    fill=True,
                    fill_opacity=0.75,
                ).add_to(m)

            st_folium(m, width=None, height=430, use_container_width=True)
        else:
            st.info("No geographic attraction coordinates found.")
    else:
        st.info("No geographic records match the selected filters.")


with cat_col:
    if not filtered_attr.empty and "category" in filtered_attr.columns:
        category_counts = (
            filtered_attr["category"]
            .value_counts()
            .reset_index()
        )
        category_counts.columns = ["Category", "Places"]
        category_counts = category_counts.head(10).sort_values("Places")

        if not category_counts.empty:
            fig = px.bar(category_counts, x="Places", y="Category", orientation="h", text="Places")
            fig.update_traces(marker_color=COLORS["teal"], texttemplate="%{text:,}", textposition="outside", cliponaxis=False)
            fig.update_xaxes(title="Number of Places", rangemode="tozero")
            fig.update_yaxes(title="", automargin=True)
            chart_layout(fig, height=430, title="Top Tourism Categories")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.plotly_chart(empty_chart(), use_container_width=True)
    else:
        st.plotly_chart(empty_chart(), use_container_width=True)


# ============================================================
# 11. TOP PLACES + VALUE ANALYSIS
# ============================================================
st.markdown('<div class="section-title">Attraction Performance</div>', unsafe_allow_html=True)
left, right = st.columns([1, 1])

with left:
    if not filtered_attr.empty and {"google_rating", "place_name"}.issubset(filtered_attr.columns):
        top_places = (
            filtered_attr.sort_values(["google_rating", "place_name"], ascending=[False, True])
            .head(10)
            .sort_values("google_rating")
        )
        if not top_places.empty:
            fig = px.bar(top_places, x="google_rating", y="place_name", orientation="h", text="google_rating")
            fig.update_traces(marker_color=COLORS["cyan"], texttemplate="%{text:.1f}", textposition="outside")
            fig.update_xaxes(range=[0, 5.2], title="Google Rating")
            fig.update_yaxes(title="")
            chart_layout(fig, height=420, title="Top 10 Highest-Rated Tourist Places")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.plotly_chart(empty_chart(), use_container_width=True)
    else:
        st.plotly_chart(empty_chart(), use_container_width=True)

with right:
    if not filtered_attr.empty:
        value_df = filtered_attr[["place_name", "city", "state", "category", "entry_fee", "google_rating"]].copy() if all(c in filtered_attr.columns for c in ["place_name", "city", "state", "category", "entry_fee", "google_rating"]) else pd.DataFrame()

        if not value_df.empty:
            value_df["entry_fee"] = pd.to_numeric(value_df["entry_fee"], errors="coerce")
            value_df["google_rating"] = pd.to_numeric(value_df["google_rating"], errors="coerce")
            value_df = value_df.dropna(subset=["entry_fee", "google_rating"])

            if not value_df.empty:
                fig_value = go.Figure()
                fee_plot = value_df["entry_fee"].where(value_df["entry_fee"] > 0, 1)

                fig_value.add_trace(
                    go.Scatter(
                        x=fee_plot, y=value_df["google_rating"],
                        mode="markers",
                        marker=dict(size=8, color="#58A6FF", opacity=0.75, line=dict(width=0.8, color="#8B949E")),
                        name="Tourist Places",
                    )
                )
                fig_value.update_layout(
                    height=420, margin=dict(l=65, r=30, t=35, b=65),
                    title=dict(text="Entry Fee vs Google Rating", x=0.02, xanchor="left", font=dict(size=14, family="Helvetica, Arial, sans-serif")),
                    xaxis=dict(title="Entry Fee (₹)", type="log", tickformat="~s", showgrid=True),
                    yaxis=dict(title="Google Rating (out of 5)", range=[0, 5.2], dtick=1, showgrid=True),
                    paper_bgcolor=COLORS["panel"], plot_bgcolor=COLORS["panel"], font=dict(color=COLORS["text"], size=11, family="Helvetica, Arial, sans-serif"),
                )
                st.plotly_chart(fig_value, use_container_width=True, config={"displayModeBar": False})
            else:
                st.info("No valid value data.")
        else:
            st.info("Columns missing for value chart.")
    else:
        st.info("No records available.")


# ============================================================
# 12. TOURISM ARRIVALS + REVENUE
# ============================================================
st.markdown('<div class="section-title">Tourism Demand & Economic Trends</div>', unsafe_allow_html=True)
trend1, trend2 = st.columns(2)

if not filtered_monthly.empty and {"year", "month_name", "foreign_tourist_arrivals", "tourism_revenue_crore_inr"}.issubset(filtered_monthly.columns):
    trend_monthly = (
        filtered_monthly.groupby(["year", "month_name"], as_index=False)
        .agg(
            foreign_tourist_arrivals=("foreign_tourist_arrivals", "sum"),
            tourism_revenue_crore_inr=("tourism_revenue_crore_inr", "sum"),
        )
    )
    trend_monthly = month_sort(trend_monthly, "month_name")

    with trend1:
        fig = px.line(trend_monthly, x="month_name", y="foreign_tourist_arrivals", color="year", markers=True)
        chart_layout(fig, height=350, title="Foreign Tourist Arrivals")
        st.plotly_chart(fig, use_container_width=True)

    with trend2:
        fig = px.line(trend_monthly, x="month_name", y="tourism_revenue_crore_inr", color="year", markers=True)
        chart_layout(fig, height=350, title="Tourism Revenue")
        st.plotly_chart(fig, use_container_width=True)
else:
    with trend1:
        st.plotly_chart(empty_chart(), use_container_width=True)
    with trend2:
        st.plotly_chart(empty_chart(), use_container_width=True)


# ============================================================
# 13. FOOTER
# ============================================================
st.markdown(
    """
    <div style="margin-top:26px;padding:16px 0 4px 0;border-top:1px solid #30363D;color:#8B949E;font-size:11px;text-align:center;font-family:Helvetica, Arial, sans-serif;">
        Smart Tourism &amp; Cultural Intelligence Platform • Milestone 2 (Powered by Supabase)
    </div>
    """,
    unsafe_allow_html=True,
)
