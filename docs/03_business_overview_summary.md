# Business Overview — Summary

## Purpose

Establish a company-level understanding of the business before analyzing individual business questions. This summary reflects `04_business_overview.ipynb`, built on `trip_analytical_dataset` (the single source of truth from `03_build_trip_analytical_dataset.ipynb`).

## Overall Performance (Jul 2022 – Oct 2024)

Based on 4,827 of 4,925 trips (cancelled trips and trips with unresolved fuel cost are excluded — see Data Quality).

| Metric | Value |
|---|---|
| Total Revenue | 58,202,763 UAH |
| Total Fuel Cost | 24,398,793 UAH |
| Total Gross Profit | 33,803,970 UAH |
| Gross Margin | 58.1% |

The business operates at a healthy overall margin across the full observation period.

## Key Findings

**1. Strong seasonality in revenue**

Revenue peaks during the harvest months (roughly July–October) and drops sharply in winter, consistent with the client base's seasonal grain-shipping demand. Gross margin rises during the winter dip, since fuel cost falls faster than revenue when volume is low.

**2. Revenue is heavily concentrated among top clients**

The largest client generates roughly 10x the revenue of the smallest client in the top 10. This motivates a closer look at client-level profitability, not just revenue, in the next analysis (Business Question 1).

**3. Revenue is more evenly distributed across the fleet**

Unlike clients, revenue across trucks does not show the same degree of concentration — suggesting fleet utilization is not the primary driver of the revenue concentration seen at the client level. Business Question 4 will confirm whether this holds for profitability as well.

**4. Delays materially erode profitability**

| Status | Mean Margin | Median Margin | Trip Count |
|---|---|---|---|
| Completed | 58.8% | 60.1% | 4,186 |
| Delayed | 51.8% | 54.3% | 641 |

Delayed trips are consistently less profitable than completed trips, driven by idle fuel consumption during delays (trucks continue burning diesel while waiting, independent of distance travelled). This motivates a closer look at delay-heavy routes in Business Question 3.

## Next Steps

These baseline figures are the reference point for all four business-question notebooks that follow:

- `05_client_profitability.ipynb`
- `06_fuel_cost_impact.ipynb`
- `07_route_analysis.ipynb`
- `08_truck_driver_performance.ipynb`