import streamlit as st

st.set_page_config(
    page_title="Smart Tourism & Cultural Intelligence Platform",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CENTER ALIGNMENT
# ============================================================

st.markdown(
    """
    <style>
    .center-header {
        text-align: center;
    }

    .center-header h1 {
        font-family: Helvetica, Arial, sans-serif;
        font-weight: 700;
        font-size: 2.8rem;
        margin-bottom: 0.4rem;
    }

    .center-header h2 {
        font-family: Helvetica, Arial, sans-serif;
        font-weight: 700;
        font-size: 1.5rem;
        margin-bottom: 1rem;
    }

    .center-header p {
        font-family: Helvetica, Arial, sans-serif;
        font-size: 1.15rem;
        color: #888888;
        margin-top: 0;
    }

    .center-footer {
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="center-header">
        <h2>TEAM 1</h2>
        <h1>Smart Tourism &amp; Cultural Intelligence Platform</h1>
        <p>Tourism, Cultural Heritage, Mobility &amp; Intelligence Dashboard</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.divider()

# ============================================================
# WELCOME
# ============================================================

st.header("Welcome")

st.write(
    """
    This platform brings together all four milestones of the
    Tourism & Cultural Analysis project into one Streamlit application.

    Use the **sidebar** to navigate between the four milestone dashboards.
    """
)

st.divider()

# ============================================================
# MILESTONE 1 & 2
# ============================================================

col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Milestone 1")

    st.write(
        """
        **Global Tourism Trends, Cultural Attractions &
        Financial Analytics Overview**
        """
    )

    st.page_link(
        "pages/milestone1.py",
        label="Open Milestone 1",
        icon="📊"
    )

with col2:
    st.subheader("📈 Milestone 2")

    st.write(
        """
        **Mobility Access, Equity & Executive Intelligence**
        """
    )

    st.page_link(
        "pages/milestone2.py",
        label="Open Milestone 2",
        icon="📈"
    )

# ============================================================
# MILESTONE 3 & 4
# ============================================================

col3, col4 = st.columns(2)

with col3:
    st.subheader("🔮 Milestone 3")

    st.write(
        """
        **Demand Intelligence & Visitor Mobility**
        """
    )

    st.page_link(
        "pages/milestone3.py",
        label="Open Milestone 3",
        icon="🔮"
    )

with col4:
    st.subheader("⚡ Milestone 4")

    st.write(
        """
        **Equity, Forecasting & Finalization**
        """
    )

    st.page_link(
        "pages/milestone4.py",
        label="Open Milestone 4",
        icon="⚡"
    )

st.divider()

# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="center-footer">
        <p>Padma Priya • Aditi Dhuria • Madhusri Gone • Chaithanya E V</p>
        <p>Smart Tourism &amp; Cultural Intelligence Platform - Integrated Milestones 1-4</p>
    </div>
    """,
    unsafe_allow_html=True
)
