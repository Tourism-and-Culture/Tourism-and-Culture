import streamlit as st
from supabase import create_client

# =========================================================
# SUPABASE CONFIGURATION
# =========================================================

# Module 1
MODULE1_SUPABASE_URL = st.secrets["https://megkqranyjwtlmfnejky.supabase.co"]
MODULE1_SUPABASE_SERVICE_KEY = st.secrets["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1lZ2txcmFueWp3dGxtZm5lamt5Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4NTY1ODQ2MSwiZXhwIjoyMTAxMjM0NDYxfQ.RblsukLFblvPf72nVb4Hp_g5s0PPgsKL-RPSNiKwn-w"]

module1_supabase = create_client(
    MODULE1_SUPABASE_URL,
    MODULE1_SUPABASE_SERVICE_KEY
)


# Module 2
MODULE2_SUPABASE_URL = st.secrets["https://megkqranyjwtlmfnejky.supabase.co"]
MODULE2_SUPABASE_ANON_KEY = st.secrets["sb_publishable_Y-wPElO-p0-zjmtKKiqSLQ_Z8YiIwR5"]

module2_supabase = create_client(
    MODULE2_SUPABASE_URL,
    MODULE2_SUPABASE_ANON_KEY
)


# Module 3
MODULE3_SUPABASE_URL = st.secrets["https://megkqranyjwtlmfnejky.supabase.co"]
MODULE3_SUPABASE_KEY = st.secrets["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1lZ2txcmFueWp3dGxtZm5lamt5Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4NTY1ODQ2MSwiZXhwIjoyMTAxMjM0NDYxfQ.RblsukLFblvPf72nVb4Hp_g5s0PPgsKL-RPSNiKwn-w"]

module3_supabase = create_client(
    MODULE3_SUPABASE_URL,
    MODULE3_SUPABASE_KEY
)


# Module 4
MODULE4_SUPABASE_URL = st.secrets["https://megkqranyjwtlmfnejky.supabase.co"]
MODULE4_SUPABASE_SERVICE_KEY = st.secrets["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1lZ2txcmFueWp3dGxtZm5lamt5Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4NTY1ODQ2MSwiZXhwIjoyMTAxMjM0NDYxfQ.RblsukLFblvPf72nVb4Hp_g5s0PPgsKL-RPSNiKwn-w"]

module4_supabase = create_client(
    MODULE4_SUPABASE_URL,
    MODULE4_SUPABASE_SERVICE_KEY
)


# =========================================================
# STREAMLIT APP
# =========================================================

st.set_page_config(
    page_title="Heritage Circuit Analytics",
    page_icon="🏛️",
    layout="wide"
)

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

    # Example:
    # response = module1_supabase.table("your_table_name").select("*").execute()
    # st.dataframe(response.data)


# =========================================================
# MODULE 2
# =========================================================

elif module == "Module 2":

    st.header("Module 2 - Last-Mile Heritage Circuit Analytics")

    st.info("Module 2 Supabase connection is ready.")

    # Example:
    # response = module2_supabase.table(
    #     "fact_heritage_transport_rows"
    # ).select("*").execute()
    #
    # st.dataframe(response.data)


# =========================================================
# MODULE 3
# =========================================================

elif module == "Module 3":

    st.header("Module 3")

    st.info("Module 3 Supabase connection is ready.")

    # Example:
    # response = module3_supabase.table("your_table_name").select("*").execute()
    # st.dataframe(response.data)


# =========================================================
# MODULE 4
# =========================================================

elif module == "Module 4":

    st.header("Module 4")

    st.info("Module 4 Supabase connection is ready.")

    # Example:
    # response = module4_supabase.table("your_table_name").select("*").execute()
    # st.dataframe(response.data)
