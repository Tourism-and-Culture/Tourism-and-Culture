# 🇮🇳 Smart Urban: Tourism & Cultural Intelligence Platform

An integrated data analytics and decision support platform for understanding tourism demand, cultural attractions, visitor behaviour, weather sensitivity, transport patterns, mobility access, forecasting, and operational anomalies across India.

The project was developed as a four-milestone team internship project. It combines a Supabase data warehouse with interactive Streamlit dashboards and an integrated executive dashboard.

## Project Overview

Tourism information is often distributed across separate datasets for attractions, arrivals, festivals, weather, bookings, and transport. This makes it difficult for tourism authorities and urban planners to obtain a unified view of visitor activity and mobility conditions.

This platform brings these datasets together to provide:

- tourism and cultural intelligence;
- geographical demand analysis;
- booking and visitor-flow analytics;
- heritage transport and modal-shift analysis;
- weather-sensitivity insights;
- mobility access and equity assessment;
- demand forecasting and anomaly alerts; and
- an integrated executive dashboard for decision-makers.

## Problem Statement

Tourism and urban mobility needs a single platform that can transform fragmented tourism, cultural, environmental, and transport data into actionable insights. The project addresses this requirement through a structured analytical database and interactive dashboards that support evidence-based planning.

## Objectives

- Integrate tourism, culture, booking, weather, and transport data into a unified data model.
- Analyze tourism demand by time, location, category, and country of origin.
- Visualize high demand destinations through heatmaps and tourism flow maps.
- Study visitor bookings, queue times, cancellations, and site demand.
- Examine heritage transport supply, completed trips, and modal substitution.
- Measure mobility access and identify relatively underserved locations.
- Detect unusual changes in demand and provide short term historical projections.
- Present milestone outputs through a consolidated executive dashboard.

## Project Milestones

### Milestone 1 : Data Foundation and Integration
- Designed a galaxy schema based analytical data model.
- Integrated tourism, attraction, festival, booking, weather, and transport datasets.
- Created fact tables, dimension tables, and analytical views in Supabase.
- Performed data preparation, validation, and exploratory analysis.

### Milestone 2 : Tourism, Cultural and Geospatial Intelligence
- Analyzed foreign tourist arrivals and tourism revenue.
- Explored tourist attractions by state, city, category, rating, and entry fee.
- Examined festival funding and cultural activity.
- Created tourism-demand heatmaps and origin to destination flow maps.
- Studied weather and temporal relationships with tourism indicators.

### Milestone 3 : Demand and Mobility Intelligence
- Analyzed bookings, completed visits, cancellations, queue waiting time, and visit duration.
- Identified hourly visitor-demand patterns and attraction bottlenecks.
- Evaluated heritage transport stands, vehicle availability, and completed trips.
- Examined modal shares across car, bus, metro, cycling/e-bikes, shuttle, and walking.
- Simulated modal substitution following infrastructure improvement.
- Studied the effect of weather conditions on travel-mode preferences.

### Milestone 4 : Executive Intelligence and Decision Support
- Developed a weighted Mobility Access Index using supply, usage, and demand components.
- Compared mobility access across heritage zones and transport stands.
- Implemented rolling demand baselines, confidence bounds, and anomaly detection.
- Generated demand-surge and demand-drop alerts.
- Added reporting and data-export features.
- Integrated the milestone insights into an executive dashboard.

## Key Dashboard Modules

1. Tourism demand and cultural overview
2. Demand heatmaps and tourism flow maps
3. Attraction and geographical intelligence
4. Booking and visitor intelligence
5. Heritage transport intelligence
6. Weather sensitivity and modal substitution
7. Mobility access and equity analysis
8. Demand forecasting and anomaly alerts
9. Executive reporting and exports

## Data Architecture

The platform uses a galaxy schema containing shared dimensions and multiple fact tables.

### Dimension tables
- `dim_time`
- `dim_location`
- `dim_country`
- `dim_weather`

### Fact tables
- `fact_monthly_tourism`
- `fact_attractions`
- `fact_festivals`
- `fact_country_arrivals`
- `fact_tourist_bookings`
- `fact_heritage_transport`
- `fact_modal_shift_weather`

### Analytical views
- `view_galaxy_monthly_tourism`
- `view_booking_intelligence`
- `view_transport_tourism_summary`
- `view_weather_tourism_analysis`

## Technology Stack

| Component | Technology |
|---|---|
| Programming | Python |
| Dashboard | Streamlit |
| Database and backend | Supabase / PostgreSQL |
| Data analysis | Pandas, NumPy |
| Charts | Plotly |
| Maps | Folium, Leaflet |
| Version control | Git and GitHub |

## Selected Project Results

- **999 valid tourist attractions** after removing one invalid rating record.
- **15.2 million foreign tourist arrivals** represented in the tourism dataset.
- **₹326,867 crore tourism revenue** represented in the monthly tourism data.
- **279 festival records** included in the cultural dataset.
- Interactive analysis of booking behaviour, transport demand, weather effects, modal distribution, mobility access, and demand anomalies.

> *Note:* Operational dashboard metrics may reflect the first 1,000 rows returned by a Supabase query. They should therefore be interpreted as the active dashboard analysis view rather than the total size of every underlying database table.

## Limitations

- Some operational dashboards analyze the first page of rows returned by Supabase unless pagination is implemented[cite: 12].
- Milestone 3 transport and modal-shift data include synthetic or simulated project data[cite: 12].
- Forecasting is based on historical rolling patterns and is not a trained machine-learning model[cite: 12].

## Future Enhancements

- Add pagination to analyze complete Supabase tables[cite: 12].
- Introduce trained forecasting models and model evaluation metrics[cite: 12].
- Integrate real-time mobility, weather, traffic, and crowd-density feeds[cite: 12].

## Team (Team 1)

- Padma Priya[cite: 3, 10, 12]
- Aditi Dhuria[cite: 3, 10, 12]
- Madhusri Gone[cite: 3, 10, 12]
- Chaithanya E V[cite: 3, 10, 12]
- Raj Chandravanshi[cite: 6, 12]

## Academic Context

This project was developed as a team internship project on smart urban tourism and cultural intelligence[cite: 12].

## License

This project is intended for academic and internship evaluation[cite: 12].
