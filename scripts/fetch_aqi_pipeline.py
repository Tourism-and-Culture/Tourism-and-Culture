import random
import pandas as pd
from supabase import create_client

# 1. Supabase Credentials (Use environment variables or placeholders for security)
SUPABASE_URL = "YOUR_SUPABASE_URL"
SUPABASE_KEY = "YOUR_SUPABASE_KEY"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 2. Fetch distinct dates from dim_weather table
res = supabase.table("dim_weather").select("date").execute()
df = pd.DataFrame(res.data)
unique_dates = df["date"].unique()

# 3. Seasonal AQI generator (Higher in winter, lower during monsoon)
def calculate_realistic_aqi(date_str):
    try:
        month = int(str(date_str).split("-")[1])
    except Exception:
        return 150.0

    monthly_base = {
        1: 280, 2: 210, 3: 160, 4: 140,
        5: 130, 6: 110, 7: 75,  8: 65,
        9: 85, 10: 190, 11: 340, 12: 310
    }
    base = monthly_base.get(month, 150)
    return round(base + random.uniform(-15, 15), 1)

# 4. Push AQI updates to dim_weather
total_updated = 0
for date_val in unique_dates:
    aqi_value = calculate_realistic_aqi(date_val)
    update_res = supabase.table("dim_weather").update({"aqi": aqi_value}).eq("date", str(date_val)).execute()
    total_updated += len(update_res.data)

print(f"Successfully populated AQI data across {total_updated} rows in dim_weather!")