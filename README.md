# 🚇 NYC MTA Subway Ridership Dashboard

An interactive data visualization dashboard built using **Dash**, **Plotly**, and **Pandas** to explore ridership patterns in the NYC MTA subway system. This project leverages open data from the New York State government to provide insights into hourly ridership trends, station-level traffic, and geographical patterns.

To start this tool, run `app.py`.

---

## 📁 About the Project

The goal of this project is to help users—commuters, analysts, city planners—visually understand:

- Hourly subway ridership patterns across time and boroughs
- Peak traffic periods
- Station-wise distribution using an interactive map
- Dynamic filtering based on date ranges

The project is modular, scalable, and designed with clean separation of concerns for better readability and maintainability.

---

## 🧩 File Descriptions

| File              | Description                                                                      |
| ----------------- | -------------------------------------------------------------------------------- |
| `app.py`          | Main entry point that starts the Dash app and assigns the layout                 |
| `app_instance.py` | Initializes the Dash app and sets up logging                                     |
| `layout.py`       | Defines the UI layout including tabs, headers, graphs, and buttons               |
| `callbacks.py`    | Contains all Dash callbacks that manage interactivity                            |
| `buttons.py`      | Provides reusable Dash UI components like date pickers and buttons               |
| `data.py`         | Responsible for loading, cleaning, filtering, and preprocessing the dataset      |
| `visualizer.py`   | Generates visualizations including time-series and geospatial plots using Plotly |
| `helper.py`       | Contains utility functions like decorators for logging function calls            |

---

## 📊 About the Data

The dataset by the Metropolitan Transportation Authority provides subway ridership estimates on an hourly basis by subway station complex and class of fare payment.
Source: [MTA Subway Hourly Ridership Dataset (2020–2024)](https://data.ny.gov/Transportation/MTA-Subway-Hourly-Ridership-2020-2024/wujg-7c2s/about_data)

Fields in the dataset:

- transit_timestamp: Timestamp of the observation
- station_complex: Subway station complex name
- borough: The borough the station belongs to
- ridership: Number of passengers at that hour
- latitude, longitude: For mapping station location

## References

- [MTA Subway Hourly Ridership Dataset (2020–2024)](https://data.ny.gov/Transportation/MTA-Subway-Hourly-Ridership-2020-2024/wujg-7c2s/about_data)
- [MTA Subway Stations](https://data.ny.gov/Transportation/MTA-Subway-Stations/39hk-dx4f/about_data)
- [New York City Subway nomenclature](https://en.wikipedia.org/wiki/New_York_City_Subway_nomenclature)
