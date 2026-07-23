# 🚛 Ukrainian Freight Logistics Analytics

End-to-end analytics project exploring profitability, fuel costs, client performance, and operational efficiency in a Ukrainian B2B freight transportation company.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Project Scope](#project-scope)
- [Business Questions](#business-questions)
- [Analysis by Business Question](#analysis-by-business-question)
- [Dataset](#dataset)
- [Data Model](#data-model)
- [Metric Logic](#metric-logic)
- [Data Quality](#data-quality)
- [Dashboard](#dashboard)
- [Tech Stack](#tech-stack)
- [Repository Structure](#repository-structure)
- [Key Insights](#key-insights-coming-soon)
- [Recommendations](#recommendations-coming-soon)

---

## Project Overview

This project analyzes the profitability of a Ukrainian B2B freight transportation company operating a fleet of 12 trucks between July 2022 and October 2024.

The company transports wheat, corn, sunflower, and soybeans across Ukraine.

During 2024, diesel prices increased substantially while transportation tariffs remained largely unchanged, putting pressure on profit margins.

The goal of this project is to identify which commercial and operational factors have the greatest impact on profitability and where management should focus improvement efforts.

## Project Scope

This project demonstrates an end-to-end analytics workflow:

- Business problem definition
- Synthetic dataset generation
- Relational database design
- SQL data validation
- KPI calculation
- Exploratory data analysis
- Tableau dashboard development
- Business recommendations

## Business Questions

- Which clients generate the highest profit rather than just revenue?
- How did rising fuel prices affect profitability across clients and routes?
- Which routes generate the highest operational costs due to delays and fuel consumption?
- Which trucks and drivers operate most efficiently?

## Analysis by Business Question

| Business Question | SQL | Notebook | Insights |
|---|---|---|---|
| Business Performance Overview | [`sql/05_business_overview.sql`](sql/02_business_overview.sql) | [`notebooks/02_business_overview.ipynb`](notebooks/02_business_overview.ipynb) | [`docs/03_business_overview_summary.md`](docs/03_business_overview_summary.md) |
| Which clients generate the highest profit rather than just revenue? | [`sql/06_client_profitability.sql`](sql/03_client_profitability.sql) | [`notebooks/03_client_profitability.ipynb`](notebooks/03_client_profitability.ipynb) | [`docs/04_client_profitability_summary.md`](docs/04_client_profitability_summary.md) |
| How did rising fuel prices affect profitability across clients and routes? | [`sql/07_fuel_cost_impact.sql`](sql/07_fuel_cost_impact.sql) | [`notebooks/04_fuel_cost_impact.ipynb`](notebooks/04_fuel_cost_impact.ipynb) | [`docs/05_fuel_cost_summary.md`](docs/05_fuel_cost_summary.md) |
| Which routes generate the highest operational costs due to delays and fuel consumption? | [`sql/08_route_costs.sql`](sql/08_route_costs.sql) | [`notebooks/05_route_costs.ipynb`](notebooks/05_route_costs.ipynb) | [`docs/06_route_costs_summary.md`](docs/06_route_costs_summary.md) |
| Which trucks and drivers operate most efficiently? | [`sql/09_truck_driver_performance.sql`](sql/09_truck_driver_performance.sql) | [`notebooks/06_truck_driver_performance.ipynb`](notebooks/06_truck_driver_performance.ipynb) | [`docs/07_truck_driver_summary.md`](docs/07_truck_driver_summary.md) |

## Dataset

The project uses a synthetic but business-realistic dataset generated specifically for this portfolio project.

The dataset contains realistic operational constraints, client-specific pricing, seasonal demand patterns, truck downtime, and changing fuel prices.

Generator: [`python/generate_data.py`](python/generate_data.py)

**Period:**

- July 2022 – October 2024

## Data Model

The database consists of 10 relational tables representing the operational activities of a freight transportation company.

**Main entities:**

The database consists of 10 normalized relational tables:

- Trips
- Clients
- Routes
- Trucks
- Drivers
- Client Rates
- Fuel Batches
- Truck Refuelings
- Truck Downtime
- Trip Metrics


ER Diagram:

*(Coming soon)*

## Metric Logic

Financial metrics are not stored directly in the dataset and are calculated analytically.

**Key assumptions:**

- Revenue is calculated using Trips + Client Rates.
- Cancelled trips are excluded from revenue.
- Fuel costs are allocated by Truck and Month.
- Gross Profit = Revenue − Allocated Fuel Cost.
- Delayed trips remain part of revenue but are analyzed separately.
- Trip-level profit represents an analytical estimate rather than an accounting value.

## Data Quality

The dataset was validated before performing profitability analysis.
All critical data quality issues were resolved before starting business analysis.

**Validation included:**

- Duplicate primary keys
- Missing values
- Referential integrity
- Business rule validation
- Tariff consistency
- Fuel consistency
- Route consistency

Detailed validation results are available in:

- [`docs/02_data_quality_summary.md`](docs/02_data_quality_summary.md)
- [`sql/04_data_quality.sql`](sql/04_data_quality.sql)

## Dashboard

The Tableau dashboard is currently under development.

***Dashboard will include:***

- Executive Overview
- Client Profitability
- Route Analysis
- Truck Performance
- Driver Performance
- Fuel Cost Analysis

🔗 Tableau Public link: _to be added_

## Tech Stack

- SQL (MySQL)
- Python (Pandas, NumPy)
- Tableau
- Git
- GitHub

## Repository Structure


├── data/                 # Generated CSV datasets
├── sql/                  # Database creation, data validation and analytical SQL queries
├── notebooks/            # Exploratory analysis and business question notebooks
├── python/               # Synthetic dataset generator
├── docs/                 # Data quality reports and business summaries
├── tableau/              # Tableau workbook and dashboard assets
├── .env.example          # Environment variables template
├── .gitignore
└── README.md


## Key Insights 

The business analysis is currently in progress.

Expected areas of analysis:

- Impact of fuel cost on margin in 2024
- High-revenue clients with low margins
- Seasonal clients as a source of volume but not always profitability
- Port routes as a source of delays
- Impact of older-truck downtime on operational efficiency

## Recommendations 

The business analysis is currently in progress.

Possible directions:

- Revise tariffs for low-margin clients
- Prioritize high-margin clients during peak season
- Dedicated monitoring of port routes
- Optimize fleet utilization
- Use fuel contracts to protect margin