# Fuel Cost Impact — Summary

## Purpose

Was the rise in fuel prices a critical factor affecting business viability? This summary reflects `06_fuel_cost_impact.ipynb`, built on `trip_analytical_dataset` and `fuel_batches` (the sources of truth from `03_build_trip_analytical_dataset.ipynb` and the fuel purchase pipeline).

## Methodology Note

Fuel price trend, company performance, and the freight-rate comparison use the full period (Jul 2022 – Oct 2024), since this question concerns a trend over time. Client- and route-level exposure analysis are limited to 2024, consistent with `05_client_profitability.ipynb`, for a fair comparison across different client tenures. Fuel Intensity (liters per 1,000 UAH of revenue) is used for exposure analysis rather than fuel cost share, since fuel cost share is mathematically the inverse of gross margin in this dataset and would simply reproduce the ranking already established in `05_client_profitability.ipynb`.

## Key Findings

- **Diesel prices rose 14.0% from 2022 to 2024**, but followed a V-shaped pattern rather than a steady increase — falling through late 2022/early 2023, rising sharply from mid-2023 through April 2024, then easing slightly toward the end of the period.
- **Company-level gross margin did not decline alongside fuel prices** — it fluctuated between roughly 51% and 65% with no sustained downward trend. Revenue volatility far exceeds fuel cost volatility month to month, indicating seasonal demand swings, not fuel prices, are the dominant driver of business performance.
- **Freight rates rose 15.6% over the same period, slightly outpacing the 14.0% fuel price increase** — the company did not just keep up with rising fuel costs, it modestly exceeded them through repricing. Part of this increase reflects a modest shift in route composition (highway trips grew from 58% to 63% of volume), alongside genuine repricing.
- **Regular and seasonal clients responded very differently to fuel price movements.** Regular-client margin stayed resilient even at fuel price peaks (~63% in late 2023/early 2024), while seasonal-client margin was far more volatile, dropping to ~47% mid-2023.
- **Fuel exposure is concentrated in specific clients, not spread evenly.** ТОВ Нива Експорт, ТОВ Полтавські Лани, and ФГ Кукурудза Південь combine the highest fuel intensity with the lowest effective rates and lowest margins — a compounded exposure to further fuel price increases. ТОВ Соєвий Дім and ТОВ Соняшник-Агро are the best-insulated, combining low fuel intensity with the highest rates and margins.
- **Route type is a weak differentiator of fuel exposure** (highway 7.80 vs local 7.37 L per 1,000 UAH revenue) — consistent with the weak route-type effect found in `05_client_profitability.ipynb`. Exposure is driven by client-specific factors, not broad route categories.

## Business Recommendations

- Continue the current pricing discipline — proactive rate increases, not reactive adjustments, are what kept margin stable through rising fuel costs.
- Prioritize ТОВ Нива Експорт, ТОВ Полтавські Лани, and ФГ Кукурудза Південь for tariff review with fuel cost pass-through clauses, given their compounded exposure (high fuel intensity, below-market rates).
- Extend seasonal client contracts to include fuel cost escalation clauses — seasonal clients show the most fuel-price-sensitive margin and the least pricing protection.
- Monitor the route-type mix going forward, as the shift toward highway trips partially drove the recent rate increase.
- Defer further route-level fuel investigation to `07_route_analysis.ipynb`, which examines specific routes and their operational causes (delays, idle time) rather than broad route-type categories.

## Summary

Rising diesel prices (14.0%, 2022–2024) did not become critical for business viability — freight rates rose slightly faster (15.6%), holding company-level margin steady through proactive repricing rather than reactive adjustment. This resilience is uneven: seasonal clients carry more fuel-price-sensitive margin than regular clients, and a small group of clients combine high fuel intensity with underpricing, making them the most vulnerable to further fuel cost increases. Route type itself is not a meaningful risk factor — exposure is concentrated at the client level.

Output: `client_fuel_risk` (MySQL table and `data/processed/client_fuel_risk.csv`) for the Tableau Fuel Cost Analysis dashboard. Route-level causes of fuel intensity are explored further in `07_route_analysis.ipynb`.