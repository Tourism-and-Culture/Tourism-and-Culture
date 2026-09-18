# infosys-Smart Urban Mobility and Traffic Intelligence Dashboard

### Tourism and Cultural Intelligence Use Case

An integrated data analytics and decision support platform for understanding tourism demand, cultural attractions, visitor behaviour, weather sensitivity, transport patterns, mobility access, forecasting, and operational anomalies across India.

The project was developed as a four-milestone team internship project under the official Infosys theme **Smart Urban Mobility and Traffic Intelligence Dashboard**. The team selected **tourism and culture** as the application domain and combined a Supabase data warehouse with interactive Streamlit milestone dashboards and an integrated executive dashboard.

## Project Overview

Tourism  and Cultural activity affects urban movement, public transport usage, traffic demand, congestion around popular destinations, and access to heritage locations. However, the related information is often distributed across separate datasets for attractions, arrivals, festivals, weather, bookings, and transport. This makes it difficult for tourism authorities and urban planners to obtain a unified view of visitor activity and mobility conditions.

This platform brings these datasets together to provide:

- tourism and cultural intelligence;
- geographical demand analysis;
- booking and visitor-flow analytics;
- heritage transport and modal-shift analysis;
- traffic-level and multimodal transport analysis;
- weather-sensitivity insights;
- mobility access and equity assessment;
- demand forecasting and anomaly alerts; and
- an integrated executive dashboard for decision-makers.

## Problem Statement

Tourism authorities and urban planners need a single platform that can transform fragmented tourism, cultural, environmental, mobility and traffic related data into actionable insights. The project addresses how visitor demand affects urban movement and transport around tourism and heritage destinations. It supports evidence based planning through a structured analytical database and interactive dashboards.

## Objectives

- Integrate tourism, culture, booking, weather, and transport data into a unified data model.
- Analyze tourism demand by time, location, category, and country of origin.
- Visualize high demand destinations through heatmaps and tourism flow maps.
- Study visitor bookings, queue times, cancellations, and site demand.
- Examine heritage transport supply, completed trips, and modal substitution.
- Analyze traffic levels and the effect of weather on transport-mode preferences
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
- Compared low, moderate, and high traffic conditions using the available traffic-level data.

### Milestone 4 : Executive Intelligence and Decision Support
- Developed a weighted Mobility Access Index using supply, usage, and demand components.
- Compared mobility access across heritage zones and transport stands.
- Implemented rolling demand baselines, confidence bounds, and anomaly detection.
- Generated demand-surge and demand-drop alerts.
- Added reporting and data-export features.
- Integrated the milestone insights into an executive dashboard.

The **final integrated Executive Dashboard is a separate application page** that consolidates key outputs from all four milestones; it is not treated as a part of milestone 4 alone.

## Alignment with Urban Mobility and Traffic Intelligence

Tourism and culture are the project's chosen application domain, while mobility and traffic intelligence form the core analytical theme.

| Internship requirement | Implementation in this project |
|---|---|
| Urban mobility | Heritage transport, vehicle availability, completed trips, and visitor movement |
| Traffic intelligence | Traffic-level analysis, hourly demand patterns, weather impact, and demand alerts |
| Multimodal transport | Car, bus, metro, cycling/e-bikes, shuttle, and walking shares |
| Mobility planning | Modal-substitution simulation following infrastructure improvement |
| Accessibility and equity | Mobility Access Index and connectivity classification |
| Predictive intelligence | Historical demand forecasting and anomaly detection |
| Application domain | Tourism, culture, festivals, attractions, and heritage destinations |

The present implementation provides **historical and analytical traffic intelligence**, rather than real-time road monitoring. Live traffic speeds, GPS feeds, road sensors, and real-time congestion data are proposed as future enhancements.

## Key Dashboard Modules

1. Tourism demand and cultural overview
2. Demand heatmaps and tourism flow maps
3. Attraction and geographical intelligence
4. Booking and visitor intelligence
5. Heritage transport intelligence
6. Weather sensitivity and modal substitution
7. Traffic-level and multimodal analysis
8. Mobility access and equity analysis
9. Demand forecasting and anomaly alerts
10. Executive reporting and exports

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
- Interactive analysis of booking behaviour, traffic levels transport demand, weather effects, modal distribution, mobility access, and demand anomalies.

> *Note:* Operational dashboard metrics may reflect the first 1,000 rows returned by a Supabase query. They should therefore be interpreted as the active dashboard analysis view rather than the total size of every underlying database table.

## Limitations

- Some operational dashboards analyze the first page of rows returned by Supabase unless pagination is implemented.
- Milestone 3 transport and modal-shift data include synthetic or simulated project data.
- Forecasting is based on historical rolling patterns and is not a trained machine-learning model.
- Traffic intelligence is based on historical and project-level analytical data rather than live road sensors, GPS feeds, or real-time vehicle speeds

## Future Enhancements

- Add pagination to analyze complete Supabase tables.
- Introduce trained forecasting models and model evaluation metrics.
- Integrate real-time mobility, weather, traffic, and crowd-density feeds.

## Live Application
**Access the live platform here:** [https://tourism-and-culture.streamlit.app/](https://tourism-and-culture.streamlit.app/)

## Team (Team 1)

- Padma Priya *(Team Lead)*
- Aditi Dhuria
- Madhusri Gone
- Chaithanya E V
- Raj Chandravanshi

## Academic Context

This project was developed under the Infosys internship theme **Smart Urban Mobility and Traffic Intelligence Dashboard**, using tourism and culture as the primary application domain.

## License

This project is intended for academic and internship evaluation.
