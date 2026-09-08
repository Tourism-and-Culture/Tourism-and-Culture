import streamlit as st
from supabase import create_client

# =========================================================
# STREAMLIT PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Heritage Circuit Analytics",
    page_icon="🏛️",
    layout="wide"
)


# =========================================================
# SUPABASE CONFIGURATION
# =========================================================

# -------------------------
# Module 1
# -------------------------

MODULE1_SUPABASE_URL = st.secrets["MODULE1_SUPABASE_URL"]
MODULE1_SUPABASE_SERVICE_KEY = st.secrets["MODULE1_SUPABASE_SERVICE_KEY"]

module1_supabase = create_client(
    MODULE1_SUPABASE_URL,
    MODULE1_SUPABASE_SERVICE_KEY
)


# -------------------------
# Module 2
# -------------------------

MODULE2_SUPABASE_URL = st.secrets["MODULE2_SUPABASE_URL"]
MODULE2_SUPABASE_ANON_KEY = st.secrets["MODULE2_SUPABASE_ANON_KEY"]

module2_supabase = create_client(
    MODULE2_SUPABASE_URL,
    MODULE2_SUPABASE_ANON_KEY
)


# -------------------------
# Module 3
# -------------------------

MODULE3_SUPABASE_URL = st.secrets["MODULE3_SUPABASE_URL"]
MODULE3_SUPABASE_KEY = st.secrets["MODULE3_SUPABASE_KEY"]

module3_supabase = create_client(
    MODULE3_SUPABASE_URL,
    MODULE3_SUPABASE_KEY
)


# -------------------------
# Module 4
# -------------------------

MODULE4_SUPABASE_URL = st.secrets["MODULE4_SUPABASE_URL"]
MODULE4_SUPABASE_SERVICE_KEY = st.secrets["MODULE4_SUPABASE_SERVICE_KEY"]

module4_supabase = create_client(
    MODULE4_SUPABASE_URL,
    MODULE4_SUPABASE_SERVICE_KEY
)


# =========================================================
# APP
# =========================================================

st.title("🏛️ Heritage Circuit Analytics")

st.success("All Supabase connections initialized successfully.")


# =========================================================
# MODULE SELECTION
# =========================================================

module = st.sidebar.selectbox(
    "Select Module",
    [
        "Module 1",
        "Module 2",
        "Module 3",
        "Module 4"
    ]
)


# =========================================================
# MODULE 1
# =========================================================

if module == "Module 1":

    st.header("Module 1")

    st.info("Module 1 Supabase connection is ready.")


# =========================================================
# MODULE 2
# =========================================================

elif module == "Module 2":

    st.header("Module 2 - Last-Mile Heritage Circuit Analytics")

    st.info("Module 2 Supabase connection is ready.")


# =========================================================
# MODULE 3
# =========================================================

elif module == "Module 3":

    st.header("Module 3")

    st.info("Module 3 Supabase connection is ready.")


# =========================================================
# MODULE 4
# =========================================================

elif module == "Module 4":

    st.header("Module 4")

    st.info("Module 4 Supabase connection is ready.")
