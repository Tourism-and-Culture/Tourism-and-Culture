import streamlit as st
from supabase import create_client

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Heritage Circuit Analytics",
    page_icon="🏛️",
    layout="wide"
)


# =========================================================
# SUPABASE CONNECTIONS
# =========================================================

# Module 1
module1_supabase = create_client(
    st.secrets["MODULE1_SUPABASE_URL"],
    st.secrets["MODULE1_SUPABASE_SERVICE_KEY"]
)

# Module 2
module2_supabase = create_client(
    st.secrets["MODULE2_SUPABASE_URL"],
    st.secrets["MODULE2_SUPABASE_ANON_KEY"]
)

# Module 3
module3_supabase = create_client(
    st.secrets["MODULE3_SUPABASE_URL"],
    st.secrets["MODULE3_SUPABASE_KEY"]
)

# Module 4
module4_supabase = create_client(
    st.secrets["MODULE4_SUPABASE_URL"],
    st.secrets["MODULE4_SUPABASE_SERVICE_KEY"]
)


# =========================================================
# APP
# =========================================================

st.title("🏛️ Heritage Circuit Analytics")

st.success("Supabase connections initialized successfully!")


# =========================================================
# SIDEBAR
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
    st.write("Module 1 Supabase connection is ready.")

    # To read data later:
    # response = module1_supabase.table("YOUR_TABLE_NAME").select("*").execute()
    # st.dataframe(response.data)


# =========================================================
# MODULE 2
# =========================================================

elif module == "Module 2":

    st.header("Module 2 - Last-Mile Heritage Circuit Analytics")
    st.write("Module 2 Supabase connection is ready.")

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
    st.write("Module 3 Supabase connection is ready.")

    # Example:
    # response = module3_supabase.table("YOUR_TABLE_NAME").select("*").execute()
    # st.dataframe(response.data)


# =========================================================
# MODULE 4
# =========================================================

elif module == "Module 4":

    st.header("Module 4")
    st.write("Module 4 Supabase connection is ready.")

    # Example:
    # response = module4_supabase.table("YOUR_TABLE_NAME").select("*").execute()
    # st.dataframe(response.data)
