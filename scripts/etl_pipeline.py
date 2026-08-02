import os
import re
import pandas as pd
import zipfile

# Helper function to clean text column headers
def clean_cols(df):
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('[^a-zA-Z0-9_]', '', regex=True)
    return df

file_path = "Cleaned datasets for our project-2.xlsx"
xls = pd.ExcelFile(file_path)

# ==========================================================
# 1. BUILD DIMENSIONS
# ==========================================================

# --- DIM_TIME ---
years = pd.Series(range(2000, 2031), name='year')
months = ['January', 'February', 'March', 'April', 'May', 'June', 
          'July', 'August', 'September', 'October', 'November', 'December']
time_records = []
for y in years:
    for m_idx, m in enumerate(months, 1):
        q = (m_idx - 1) // 3 + 1
        time_records.append({'year': y, 'month_name': m, 'month_num': m_idx, 'quarter': f'Q{q}'})

dim_time = pd.DataFrame(time_records)
dim_time['time_id'] = range(1, len(dim_time) + 1)

# --- DIM_LOCATION ---
df_tourist_raw = pd.read_excel(xls, 'Tourist Places')
df_tourist = clean_cols(df_tourist_raw.copy())

df_rest_raw = pd.read_excel(xls, 'Restuarants')
df_rest = clean_cols(df_rest_raw.copy())

loc_tourist = df_tourist[['state', 'city']].drop_duplicates()
loc_rest = df_rest[['city']].drop_duplicates()
loc_rest['state'] = 'Unknown'

dim_location = pd.concat([loc_tourist, loc_rest], ignore_index=True).drop_duplicates(subset=['city', 'state'])
dim_location = dim_location.dropna(subset=['city']).reset_index(drop=True)
dim_location['location_id'] = range(1, len(dim_location) + 1)

# --- DIM_COUNTRY ---
df_age_raw = pd.read_excel(xls, 'FTA_Age_Group')
df_age = clean_cols(df_age_raw.copy())
dim_country = df_age[['country_of_nationality', 'region']].drop_duplicates().reset_index(drop=True)
dim_country = dim_country.rename(columns={'country_of_nationality': 'country_name'})
dim_country['country_id'] = range(1, len(dim_country) + 1)

# ==========================================================
# 2. BUILD FACTS
# ==========================================================

# --- FACT_ATTRACTIONS ---
rating_col = [c for c in df_tourist.columns if 'rating' in c][0]
df_tourist_clean = df_tourist.merge(dim_location, on=['city', 'state'], how='left')
fact_attractions = df_tourist_clean[['location_id', 'place_name', 'category', rating_col, 'entry_fee']].copy()
fact_attractions.columns = ['location_id', 'place_name', 'category', 'google_rating', 'entry_fee']

# --- FACT_FESTIVALS ---
df_fest1 = clean_cols(pd.read_excel(xls, 'Festivals(2014-2024)'))
df_fest2 = clean_cols(pd.read_excel(xls, 'Festivals_NorthEast_2021_22'))

df_fest1 = df_fest1.rename(columns={'stateut': 'state', 'festival_name': 'festival_name'})
df_fest2 = df_fest2.rename(columns={'name_of_state': 'state', 'name_of_fairs__festivals': 'festival_name'})

fact_festivals = pd.concat([
    df_fest1[['state', 'year', 'festival_name', 'amount_sanctioned', 'amount_released']],
    df_fest2[['state', 'year', 'festival_name', 'amount_sanctioned', 'amount_released']]
], ignore_index=True)

# Map state to location_id from dim_location
loc_state_map = dim_location[['state', 'location_id']].drop_duplicates(subset=['state'])
fact_festivals = fact_festivals.merge(loc_state_map, on='state', how='left')
fact_festivals = fact_festivals[['location_id', 'state', 'year', 'festival_name', 'amount_sanctioned', 'amount_released']]

# --- FACT_MONTHLY_TOURISM ---
df_rev = clean_cols(pd.read_excel(xls, 'Tourism Revenue'))
df_fta_m = clean_cols(pd.read_excel(xls, 'Month-Wise Details of Foreign T'))

fact_monthly_tourism = pd.merge(df_rev, df_fta_m, on=['month', 'year'], how='outer')
fact_monthly_tourism = fact_monthly_tourism.merge(
    dim_time, left_on=['year', 'month'], right_on=['year', 'month_name'], how='left'
)[['time_id', 'year', 'month', 'tourism_revenue_crore_inr', 'foreign_tourist_arrivals']]

# --- FACT_COUNTRY_ARRIVALS ---
df_stay = clean_cols(pd.read_excel(xls, 'FTA_Avg_Duration_of_Stay'))
duration_col = [c for c in df_stay.columns if 'average' in c or 'stay' in c or 'days' in c][0]

df_country_fact = df_age.merge(df_stay[['country_of_nationality', duration_col]], on='country_of_nationality', how='left')
df_country_fact = df_country_fact.merge(dim_country, left_on='country_of_nationality', right_on='country_name', how='left')

age_cols = [c for c in df_age.columns if 'percentage' in c or 'in_percentage' in c]

fact_country_arrivals = df_country_fact[[
    'country_id', 'arrivals_in_numbers'
] + age_cols + [duration_col]].copy()

# ==========================================================
# SAVE ALL CSVs
# ==========================================================
csv_files = {
    'dim_time.csv': dim_time,
    'dim_location.csv': dim_location,
    'dim_country.csv': dim_country,
    'fact_attractions.csv': fact_attractions,
    'fact_festivals.csv': fact_festivals,
    'fact_monthly_tourism.csv': fact_monthly_tourism,
    'fact_country_arrivals.csv': fact_country_arrivals
}

for name, df in csv_files.items():
    df.to_csv(name, index=False)
    print(f"Saved {name} with shape {df.shape}")

# Create zip file containing all CSVs
with zipfile.ZipFile('galaxy_schema_csvs.zip', 'w') as zipf:
    for name in csv_files.keys():
        zipf.write(name)

print("Created galaxy_schema_csvs.zip")

# Write the python script etl_pipeline.py for repository upload
python_script_content = """import os
import re
import pandas as pd
from sqlalchemy import create_engine

# ==========================================================
# GALAXY SCHEMA ETL PIPELINE FOR TOURISM DATA
# ==========================================================

EXCEL_FILE = "Cleaned datasets for our project-2.xlsx"
SUPABASE_DB_URI = "postgresql://postgres.[PROJECT_REF]:[PASSWORD]@aws-0-ap-south-1.pooler.supabase.com:6543/postgres"

def clean_cols(df):
    \"\"\"Standardize column names to lowercase, remove special characters and spaces.\"\"\"
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('[^a-zA-Z0-9_]', '', regex=True)
    return df

def run_etl():
    print("Starting ETL Pipeline Execution...")
    
    xls = pd.ExcelFile(EXCEL_FILE)

    # 1. EXTRACT & TRANSFORM DIMENSIONS
    # --- dim_time ---
    years = pd.Series(range(2000, 2031), name='year')
    months = ['January', 'February', 'March', 'April', 'May', 'June', 
              'July', 'August', 'September', 'October', 'November', 'December']
    time_records = []
    for y in years:
        for m_idx, m in enumerate(months, 1):
            q = (m_idx - 1) // 3 + 1
            time_records.append({'year': y, 'month_name': m, 'month_num': m_idx, 'quarter': f'Q{q}'})

    dim_time = pd.DataFrame(time_records)
    dim_time['time_id'] = range(1, len(dim_time) + 1)

    # --- dim_location ---
    df_tourist = clean_cols(pd.read_excel(xls, 'Tourist Places'))
    df_rest = clean_cols(pd.read_excel(xls, 'Restuarants'))

    loc_tourist = df_tourist[['state', 'city']].drop_duplicates()
    loc_rest = df_rest[['city']].drop_duplicates()
    loc_rest['state'] = 'Unknown'

    dim_location = pd.concat([loc_tourist, loc_rest], ignore_index=True).drop_duplicates(subset=['city', 'state'])
    dim_location = dim_location.dropna(subset=['city']).reset_index(drop=True)
    dim_location['location_id'] = range(1, len(dim_location) + 1)

    # --- dim_country ---
    df_age = clean_cols(pd.read_excel(xls, 'FTA_Age_Group'))
    dim_country = df_age[['country_of_nationality', 'region']].drop_duplicates().reset_index(drop=True)
    dim_country = dim_country.rename(columns={'country_of_nationality': 'country_name'})
    dim_country['country_id'] = range(1, len(dim_country) + 1)

    print("Dimensions Built: dim_time, dim_location, dim_country")

    # 2. EXTRACT & TRANSFORM FACTS
    # --- fact_attractions ---
    rating_col = [c for c in df_tourist.columns if 'rating' in c][0]
    df_tourist_clean = df_tourist.merge(dim_location, on=['city', 'state'], how='left')
    fact_attractions = df_tourist_clean[['location_id', 'place_name', 'category', rating_col, 'entry_fee']].copy()
    fact_attractions.columns = ['location_id', 'place_name', 'category', 'google_rating', 'entry_fee']

    # --- fact_festivals ---
    df_fest1 = clean_cols(pd.read_excel(xls, 'Festivals(2014-2024)'))
    df_fest2 = clean_cols(pd.read_excel(xls, 'Festivals_NorthEast_2021_22'))

    df_fest1 = df_fest1.rename(columns={'stateut': 'state', 'festival_name': 'festival_name'})
    df_fest2 = df_fest2.rename(columns={'name_of_state': 'state', 'name_of_fairs__festivals': 'festival_name'})

    fact_festivals = pd.concat([
        df_fest1[['state', 'year', 'festival_name', 'amount_sanctioned', 'amount_released']],
        df_fest2[['state', 'year', 'festival_name', 'amount_sanctioned', 'amount_released']]
    ], ignore_index=True)

    loc_state_map = dim_location[['state', 'location_id']].drop_duplicates(subset=['state'])
    fact_festivals = fact_festivals.merge(loc_state_map, on='state', how='left')
    fact_festivals = fact_festivals[['location_id', 'state', 'year', 'festival_name', 'amount_sanctioned', 'amount_released']]

    # --- fact_monthly_tourism ---
    df_rev = clean_cols(pd.read_excel(xls, 'Tourism Revenue'))
    df_fta_m = clean_cols(pd.read_excel(xls, 'Month-Wise Details of Foreign T'))

    fact_monthly_tourism = pd.merge(df_rev, df_fta_m, on=['month', 'year'], how='outer')
    fact_monthly_tourism = fact_monthly_tourism.merge(
        dim_time, left_on=['year', 'month'], right_on=['year', 'month_name'], how='left'
    )[['time_id', 'year', 'month', 'tourism_revenue_crore_inr', 'foreign_tourist_arrivals']]

    # --- fact_country_arrivals ---
    df_stay = clean_cols(pd.read_excel(xls, 'FTA_Avg_Duration_of_Stay'))
    duration_col = [c for c in df_stay.columns if 'average' in c or 'stay' in c or 'days' in c][0]

    df_country_fact = df_age.merge(df_stay[['country_of_nationality', duration_col]], on='country_of_nationality', how='left')
    df_country_fact = df_country_fact.merge(dim_country, left_on='country_of_nationality', right_on='country_name', how='left')

    age_cols = [c for c in df_age.columns if 'percentage' in c or 'in_percentage' in c]

    fact_country_arrivals = df_country_fact[[
        'country_id', 'arrivals_in_numbers'
    ] + age_cols + [duration_col]].copy()

    print("Fact Tables Transformed successfully.")

    # 3. EXPORT TO CSV & LOAD TO DB
    tables = {
        'dim_time': dim_time,
        'dim_location': dim_location,
        'dim_country': dim_country,
        'fact_attractions': fact_attractions,
        'fact_festivals': fact_festivals,
        'fact_monthly_tourism': fact_monthly_tourism,
        'fact_country_arrivals': fact_country_arrivals
    }

    # Save to local CSV files
    os.makedirs('output_csvs', exist_ok=True)
    for t_name, t_df in tables.items():
        t_df.to_csv(f'output_csvs/{t_name}.csv', index=False)
        print(f"Saved output_csvs/{t_name}.csv")

    # Optional DB Load via SQLAlchemy
    if "postgres." in SUPABASE_DB_URI and "[PASSWORD]" not in SUPABASE_DB_URI:
        engine = create_engine(SUPABASE_DB_URI)
        for t_name, t_df in tables.items():
            print(f"Loading {t_name} to Supabase...")
            t_df.to_sql(t_name, con=engine, if_exists='replace', index=False)
        print("Successfully uploaded all tables to Supabase!")

if __name__ == "__main__":
    run_etl()
"""

with open("etl_pipeline.py", "w") as f:
    f.write(python_script_content)

print("Saved etl_pipeline.py successfully.")
