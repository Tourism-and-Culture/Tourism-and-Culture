import streamlit as st


st.set_page_config(
    page_title="Smart Urban Mobility and Traffic Intelligence",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# file path
milestone1_page = "pages/milestone1.py"
milestone2_page = "pages/milestone2.py"
milestone3_page = "pages/milestone3.py"
milestone4_page = "pages/milestone4.py"
executive_page = "pages/Executive Dashboard.py"



st.markdown(
    """
    <style>
    :root {
        color-scheme: dark;
    }

    html,
    body,
    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"] {
        background-color: #00172B !important;
        color: #f0f6fc !important;
    }

    [data-testid="stHeader"] {
        background-color: #0e1117 !important;
        color: #f0f6fc !important;
    }

    [data-testid="stToolbar"] button,
    [data-testid="stToolbar"] svg,
    [data-testid="stHeaderActionElements"] button,
    [data-testid="stHeaderActionElements"] svg {
        color: #f0f6fc !important;
        fill: currentColor !important;
    }

    .block-container {
        max-width: 1150px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    [data-testid="stSidebar"] {
        display: none;
    }

    .home-header {
        text-align: center;
        padding: 1rem 0 1.5rem 0;
    }

    .team-name {
        color: #58a6ff;
        font-size: 0.9rem;
        font-weight: 700;
        letter-spacing: 3px;
    }

    .home-header h1 {
        color: #f0f6fc;
        font-size: 3rem;
        margin: 0.7rem 0 0.5rem 0;
    }

    .home-header h3 {
        color: #79c0ff;
        font-size: 1.25rem;
        margin-bottom: 1rem;
    }

    .home-header p {
        max-width: 780px;
        margin: auto;
        color: #a5afba;
        line-height: 1.6;
    }

    .section-title {
        color: #f0f6fc;
        font-size: 1.5rem;
        font-weight: 700;
        margin: 1.5rem 0 0.7rem 0;
    }

    .card-heading {
        color: #f0f6fc;
        font-size: 1.15rem;
        font-weight: 700;
        margin-bottom: 0.4rem;
    }

    .card-text {
        color: #b8c3ce !important;
        line-height: 1.5;
        min-height: 65px;
    }

    /* Keep bordered containers identical in Streamlit's light and dark themes. */
    div[data-testid="stVerticalBlockBorderWrapper"],
    [data-testid="stVerticalBlockBorderWrapper"] > div {
        background-color: #07343d !important;
        border: 1px solid #58737a !important;
        border-color: #58737a !important;
        border-radius: 12px !important;
        box-shadow: none !important;
    }

    .section-title,
    .card-heading,
    [data-testid="stMarkdownContainer"] h1,
    [data-testid="stMarkdownContainer"] h2,
    [data-testid="stMarkdownContainer"] h3 {
        color: #f0f6fc !important;
    }

    [data-testid="stCaptionContainer"],
    [data-testid="stCaptionContainer"] p,
    [data-testid="stCaptionContainer"] span {
        color: #b8c3ce !important;
        opacity: 1 !important;
    }

    [data-testid="stPageLink"] a,
    [data-testid="stPageLink"] a:link,
    [data-testid="stPageLink"] a:visited {
        justify-content: center;
        background-color: #1f6feb !important;
        color: #ffffff !important;
        border: 1px solid #58a6ff !important;
        border-radius: 8px !important;
        font-weight: 600;
        text-decoration: none;
        opacity: 1 !important;
    }

    [data-testid="stPageLink"] a p,
    [data-testid="stPageLink"] a span,
    [data-testid="stPageLink"] a svg {
        color: #ffffff !important;
        fill: currentColor !important;
        opacity: 1 !important;
    }

    [data-testid="stPageLink"] a:hover {
        background-color: #388bfd !important;
        border-color: #79c0ff !important;
    }

    .footer {
        text-align: center;
        color: #8b949e;
        border-top: 1px solid #30363d;
        margin-top: 2rem;
        padding-top: 1.4rem;
        line-height: 1.8;
    }

    .footer strong {
        color: #f0f6fc;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# Main heading
st.markdown(
    """
    <div class="home-header">
        <div class="team-name">TEAM 1</div>
        <h1>Smart Urban Mobility and Traffic Intelligence Dashboard</h1>
        <h3>Tourism and Cultural Intelligence Use Case</h3>
        <p>
            This platform brings together tourism demand, cultural destinations,
            visitor mobility, traffic behaviour, weather analysis, forecasting
            and mobility access in one Streamlit application.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# The final combined dashboard 
st.markdown('<div class="section-title">Executive Dashboard</div>', unsafe_allow_html=True)

with st.container(border=True):
    info_col, button_col = st.columns([3, 1])

    with info_col:
        st.markdown(
            """
            <div class="card-heading">Integrated Executive View</div>
            <div class="card-text">
                Combined KPIs, demand maps, traffic intelligence, weather impact,
                mobility access, forecasts and alerts from all four milestones.
            </div>
            """,
            unsafe_allow_html=True,
        )

    with button_col:
        st.page_link(
            executive_page,
            label="Open Executive Dashboard",
            icon="📊",
        )


# Individual milestone pages
st.markdown('<div class="section-title">Explore the Project Milestones</div>', unsafe_allow_html=True)
st.caption("Open a milestone to view its detailed analysis and implementation.")


def show_milestone(title, description, page, icon):
    with st.container(border=True):
        st.markdown(f'<div class="card-heading">{title}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="card-text">{description}</div>', unsafe_allow_html=True)
        st.page_link(page, label=f"Open {title}", icon=icon)


col1, col2 = st.columns(2)

with col1:
    show_milestone(
        "Milestone 1",
        "Supabase data foundation, validated tourism KPIs and the original Power BI prototype.",
        milestone1_page,
        "🗄️",
    )

with col2:
    show_milestone(
        "Milestone 2",
        "Tourism heatmaps, flow maps, destination performance, weather overlays and the Looker Studio prototype.",
        milestone2_page,
        "🗺️",
    )


col3, col4 = st.columns(2)

with col3:
    show_milestone(
        "Milestone 3",
        "Booking behaviour, transport demand, traffic pressure, seasonal patterns and modal substitution.",
        milestone3_page,
        "🚦",
    )

with col4:
    show_milestone(
        "Milestone 4",
        "Mobility Access Index, equity analysis, demand forecasting, anomaly detection and reports.",
        milestone4_page,
        "📈",
    )


# Team details
st.markdown(
    """
    <div class="footer">
        <strong>Team 1</strong><br>
        Padma Priya &nbsp;•&nbsp; Aditi Dhuria &nbsp;•&nbsp;
        Madhusri Gone &nbsp;•&nbsp; Chaithanya E V &nbsp;•&nbsp; Raj Chandravanshi<br>
        Infosys Internship Project · Integrated Milestones 1–4
    </div>
    """,
    unsafe_allow_html=True,
)
