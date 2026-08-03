# Truck Performance — Summary

## Purpose

Do truck-level factors (age, capacity, downtime) explain the route and cargo performance issues identified in prior notebooks, and is profitability concentrated across trucks the way it is across clients? This summary reflects `08_truck_driver_performance.ipynb`, built on `trip_analytical_dataset` and `truck_downtime`.

## Methodology Note

`driver_id` is not consistently paired with a single `truck_id` in this dataset — a data-generation limitation, not a real-world 1:1 driver-truck assignment (all 12 drivers appear across multiple trucks). This analysis therefore treats truck-level questions only, using static truck attributes (`truck_capacity_tons`, `truck_year`, `truck_brand`) rather than driver-truck combinations.

The notebook is intentionally narrower in scope than `05_client_profitability.ipynb` or `07_route_analysis.ipynb`: truck-level data doesn't support the same depth of causal analysis. It follows two specific threads already opened by prior notebooks rather than a generic truck ranking — the capacity-matching question flagged for Подільськ-Чорноморськ in `07_route_analysis.ipynb`, and the open question from `03_business_overview_summary.md` on whether profit concentrates across trucks the way revenue does not.

## Truck Profitability (2024)

Top 5 trucks by profit account for **53.1%** of total gross profit — far less concentrated than clients (84.4%, `04_client_profitability_summary.md`).

## Key Findings

- **Profit is far less concentrated across trucks than across clients.** The top 5 trucks by profit account for 53.1% of total gross profit, compared to 84.4% for the top 5 clients. This confirms the open question from `03_business_overview_summary.md`: truck-level effects are second-order compared to client- or route-level effects.
- **Truck age is not a meaningful driver of margin or fuel efficiency.** The fleet's lowest-margin truck (TRK-03, 49.0%) is a 2017 model, not the oldest; only the two oldest trucks (2015, 2017) show elevated fuel cost per ton-km (1.10, 1.12 UAH), and this doesn't extend to a fleet-wide age gradient.
- **Подільськ-Чорноморськ, not the trucks assigned to it, drives the worst outcomes.** The four bottom-margin trucks serve all 10 routes and are not concentrated on any subset — but three of them underperform even that route's already-low 2024 average (43.8%, `07_route_analysis.ipynb`). A direct test confirms the cause: the same four trucks recover to 51.0–54.7% margin on their other routes — a 12–18 pp jump — confirming the route's structural fuel-cost/load-factor issue dominates whichever truck is assigned to it, though the port-route observations themselves remain a small sample (6–7 trips per truck).
- **Downtime and margin are independent.** Total downtime in 2024 was 491 days across 15 events (breakdowns account for more days and events than scheduled maintenance), concentrated in half the fleet (top 5 trucks = 71.7% of all downtime days). The truck with the most downtime (TRK-01, 85 days) does have low margin (51.6%), but two other high-downtime trucks (TRK-02, TRK-12) are among the fleet's most profitable (56.5%, 57.1%) — downtime does not explain why the bottom-margin trucks underperform.

## Business Recommendations

- Skip fleet-wide truck replacement or age-based capex — truck age isn't a consistent driver of margin or fuel efficiency here; only the two oldest trucks (TRK-01, TRK-03) show a fuel-efficiency signal worth monitoring individually, not a fleet-wide pattern.
- Don't try to fix Подільськ-Чорноморськ's low margin by reassigning trucks — the route's structural fuel-cost/load-factor problem affects any truck placed on it. Any fix needs to happen at the route/cargo level (tariff or fuel surcharge renegotiation for wheat cargo, per `07_route_analysis.ipynb`), not through truck-level assignment changes.
- Track downtime and margin as separate operational issues, not a shared metric — two of the highest-downtime trucks are among the fleet's most profitable, and the bottom-margin trucks mostly have low or no downtime.
- Deprioritize truck-level intervention relative to the client- and route-level fixes already recommended in `05_client_profitability.ipynb` and `07_route_analysis.ipynb` — profit is evenly spread across the fleet, and this notebook found no comparable structural risk at the truck level.

## Summary

Truck-level analysis found no dominant structural pattern comparable to the client- or route-level findings in prior notebooks: profit is roughly evenly distributed across the fleet, and truck age is not a consistent driver of margin or fuel efficiency. The one confirmed causal link is on Подільськ-Чорноморськ: three of the four bottom-margin trucks underperform even that route's already-low baseline, but recover to near-normal margin (51.0–54.7%) as soon as they're on any other route — confirming that the route's structural issue, not truck assignment, drives the shortfall. Downtime, while real (491 days in 2024, concentrated in about half the fleet), does not correlate with margin and should be tracked separately.

Output: `truck_performance` (MySQL table and `data/processed/truck_performance.csv`) for the Tableau Truck Performance dashboard tab. This concludes the four business-question notebooks (05–08).