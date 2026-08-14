-- ==========================================================
-- 1. GALAXY SCHEMA VIEW
-- ==========================================================
CREATE OR REPLACE VIEW view_galaxy_monthly_tourism AS
SELECT 
    t.time_id,
    t.year,
    t.month_name,
    t.month_num,
    t.quarter,
    f.foreign_tourist_arrivals,
    f.tourism_revenue_crore_inr
FROM fact_monthly_tourism f
JOIN dim_time t
  ON LOWER(f.month) = LOWER(t.month_name)
 AND f.year = t.year;


-- ==========================================================
-- 2. MISSING MONTHS QUERY
-- ==========================================================
-- --missing months (Apr-Dec) into dim_time 
INSERT INTO dim_time (year, month_num, month_name, quarter, time_id)
SELECT 
    d.year,
    d.month_num,
    d.month_name,
    d.quarter,
    ((d.year - 2000) * 12 + d.month_num) AS time_id
FROM (
    SELECT 
        EXTRACT(YEAR FROM g)::INT AS year,
        EXTRACT(MONTH FROM g)::INT AS month_num,
        TRIM(TO_CHAR(g, 'Month')) AS month_name,
        'Q' || EXTRACT(QUARTER FROM g)::INT AS quarter
    FROM generate_series(
        '2000-01-01'::date, 
        '2025-12-01'::date, 
        '1 month'::interval
    ) g
) d
WHERE NOT EXISTS (
    SELECT 1 FROM dim_time dt 
    WHERE dt.year = d.year AND dt.month_num = d.month_num
);


-- ==========================================================
-- 3. DELHI NCR STATE NAMES QUERY
-- ==========================================================
-- --'Unknown' states for Delhi NCR cities in dim_location
UPDATE dim_location
SET state = CASE 
    WHEN city = 'New Delhi' THEN 'Delhi'
    WHEN city IN ('Gurgaon', 'Faridabad') THEN 'Haryana'
    WHEN city IN ('Noida', 'Ghaziabad') THEN 'Uttar Pradesh'
    ELSE state
END
WHERE state = 'Unknown';


-- ===================================================
-- 3. MILESTONE 2: ADD AQI COLUMN TO DIM_WEATHER
-- ===================================================
ALTER TABLE "dim_weather" ADD COLUMN IF NOT EXISTS aqi NUMERIC;



-- ===================================================
-- 4. MILESTONE 2: WEATHER & TOURISM ANALYSIS VIEW
-- ===================================================
CREATE OR REPLACE VIEW view_weather_tourism_analysis AS
SELECT 
  w.location_name,
  fmt.time_id,
  fmt.year,
  fmt.month,
  fmt.tourism_revenue_crore_inr,
  fmt.foreign_tourist_arrivals,
  w.temp_c,
  w.rainfall_mm,
  w.humidity_pct,
  w.aqi,
  -- Formatted string columns with units included:
  ROUND(w.temp_c::numeric, 1)::text || ' °C' AS temp_c_formatted,
  ROUND(w.rainfall_mm::numeric, 1)::text || ' mm' AS rainfall_formatted,
  ROUND(w.humidity_pct::numeric, 1)::text || ' %' AS humidity_formatted
FROM fact_monthly_tourism fmt
LEFT JOIN dim_weather w 
  ON w.date = TO_CHAR(TO_DATE(fmt.year::text || ' ' || fmt.month, 'YYYY Month'), 'YYYY-MM');
