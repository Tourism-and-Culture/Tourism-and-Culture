import streamlit as st
from supabase import create_client, Client

st.set_page_config(
    page_title="Supabase Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Supabase Dashboard")

# Get Supabase credentials from Streamlit Secrets
SUPABASE_URL = st.secrets["db.megkqranyjwtlmfnejky.supabase.co"]
SUPABASE_KEY = st.secrets["sb_publishable_Y-wPElO-p0-zjmtKKiqSLQ_Z8YiIwR5"]

# Connect to Supabase
supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

st.success("Connected to Supabase successfully!")

# Example: read data from a table
table_name = "your_table_name"

try:
    response = supabase.table(table_name).select("*").execute()

    data = response.data

    if data:
        st.subheader("Data")
        st.dataframe(data, use_container_width=True)
    else:
        st.info("No data found in the table.")

except Exception as e:
    st.error(f"Error loading data: {e}")
