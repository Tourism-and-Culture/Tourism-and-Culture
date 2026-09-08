import streamlit as st

# ============================================================
# PAGE CONFIG
# ============================================================

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
# SIDEBAR MILESTONE NAVIGATION
# ============================================================

st.sidebar.title("📚 Project Navigation")

st.sidebar.write("Select a milestone to explore:")

milestone = st.sidebar.selectbox(
    "Choose Milestone",
    [
        "🏠 Home",
        "📊 Milestone 1",
        "📈 Milestone 2",
        "🔮 Milestone 3",
        "⚡ Milestone 4"
    ]
)

# ============================================================
# MILESTONE NAVIGATION
# ============================================================

if milestone == "📊 Milestone 1":
    st.switch_page("pages/milestone1.py")

elif milestone == "📈 Milestone 2":
    st.switch_page("pages/milestone2.py")

elif milestone == "🔮 Milestone 3":
    st.switch_page("pages/milestone3.py")

elif milestone == "⚡ Milestone 4":
    st.switch_page("pages/milestone4.py")

# ============================================================
# HOME PAGE HEADER
# ============================================================

st.markdown(
    """
    <div class="center-header">
        <h2>TEAM 1</h2>

        <h1>
            Smart Tourism &amp; Cultural Intelligence Platform
        </h1>

        <p>
            Tourism, Cultural Heritage, Mobility &amp;
            Intelligence Dashboard
        </p>
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

    Use the **Choose Milestone** menu in the sidebar to navigate
    between the four milestone dashboards.
    """
)

st.divider()

# ============================================================
# PROJECT MILESTONES
# ============================================================

st.subheader("Project Milestones")

# ============================================================
# MILESTONE 1 & 2
# ============================================================

col1, col2 = st.columns(2)

with col1:
    st.markdown(
        """
        ### 📊 Milestone 1

        **Global Tourism Trends, Cultural Attractions &
        Financial Analytics Overview**
        """
    )

with col2:
    st.markdown(
        """
        ### 📈 Milestone 2

        **Mobility Access, Equity & Executive Intelligence**
        """
    )

# ============================================================
# MILESTONE 3 & 4
# ============================================================

col3, col4 = st.columns(2)

with col3:
    st.markdown(
        """
        ### 🔮 Milestone 3

        **Demand Intelligence & Visitor Mobility**
        """
    )

with col4:
    st.markdown(
        """
        ### ⚡ Milestone 4

        **Equity, Forecasting & Finalization**
        """
    )

st.divider()

# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="center-footer">

        <p>
            Padma Priya • Aditi Dhuria • Madhusri Gone • Chaithanya E V
        </p>

        <p>
            Smart Tourism &amp; Cultural Intelligence Platform
            - Integrated Milestones 1-4
        </p>

    </div>
    """,
    unsafe_allow_html=True
)
