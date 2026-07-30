# Route Analysis — Summary

## Purpose

Which routes underperform, and what operational factors explain why? This summary reflects `07_route_analysis.ipynb`, built on `trip_analytical_dataset`.

## Methodology Note

Analysis is limited to trips active in 2024, consistent with `05_client_profitability.ipynb` and `06_fuel_cost_impact.ipynb`, for a fair, current-state comparison. Routes are analyzed as origin-destination pairs (not the technical `route_id`), since the geographic pair is interpretable and already the framing used in `05_client_profitability.ipynb`.

Each client in this dataset operates exactly one fixed route, so route-level and client-level rankings are numerically identical. This notebook does not discover new low-performing routes independent of `05_client_profitability.ipynb` - it reframes the same ranking through `route_has_port`, isolating a structural driver that route-type and client-level analysis alone did not surface.

## Key Findings

- **`route_has_port`, not `route_type`, is the real structural driver of route profitability.** All 4 port-destination routes cluster at 43.8-52.5% margin with 5.6-8.5h avg delay, versus 52.7-67.5% margin and 1.1-2.1h delay for the 6 non-port routes - a much cleaner split than route_type produced (54.5% vs 56.8%, only a 2.3pp gap).
- **All four port routes peaked in 2023 and declined in 2024**, even after controlling for seasonal mix-shift (Jul-Oct common-months comparison). Three of the four (Дніпро-Одеса, Миколаїв-Одеса, Полтава-Чорноморськ) returned to roughly their 2022 baseline rather than deteriorating further - consistent with a shared external factor (plausibly Black Sea port disruption in this period, not tested directly in this dataset) rather than individual decline. Trip volume on these routes also fell ~37% in 2024 relative to 2022-2023.
- **Подільськ-Чорноморськ (ТОВ Нива Експорт) is the exception**: its 2024 margin (43.8%) fell below its own 2022 baseline (49.0%) - a genuine decline, not a return to normal.
- **For Подільськ-Чорноморськ specifically, cargo pricing, delay, and tariff were each tested and individually ruled out.** The actual driver is fuel cost per ton-km (1.10, highest of the four port routes), traced to its lowest load factor by weight among the group (85.6%) - itself linked to its 100% wheat cargo mix (versus corn/sunflower on the other three routes). This is a distinct mechanism from the delay-driven pattern affecting the other three port routes.
- **Company-wide delay benchmarking confirms port routes are delayed meaningfully more often than the network average** - consistent with the delay-driven pattern for three of the four port routes; Подільськ-Чорноморськ's delay rate is comparatively lower, consistent with its different root cause.

## Business Recommendations

- Treat port routes as a distinct risk category, not individual client issues: extend the tariff/delay review already underway for ТОВ Полтавські Лани and ПП ДніпроЗерно to include Миколаїв-Одеса, which shares the same port-delay profile even though its margin sits just above the threshold that originally flagged the other two.
- Investigate the external port-disruption hypothesis directly before assuming the 2024 decline on three of the four port routes is permanent - the shared, simultaneous pattern suggests a common external cause rather than three independent operational failures.
- For ТОВ Нива Експорт (Подільськ-Чорноморськ), the fix is operational, not commercial or delay-related: prioritize load optimization for wheat cargo specifically - by-weight loading efficiency, not pricing or delay management, is the lever that would improve this route's margin.
- Do not apply a single "port routes are delay-driven" narrative uniformly - Подільськ-Чорноморськ demonstrates that port status alone doesn't guarantee the same root cause, and a one-size-fits-all response would misdiagnose the fix.

## Summary

Route-level analysis identified `route_has_port`, not `route_type`, as the real structural driver of underperformance: all four port-destination routes show meaningfully lower margin and higher delay than the rest of the network, a pattern that holds even after controlling for seasonal mix-shift. Three of these routes share a common 2023-peak/2024-decline pattern, consistent with an external factor affecting port routes broadly rather than individual deterioration. The fourth, Подільськ-Чорноморськ, is structurally different - neither tariff nor delay explain its underperformance; the driver is fuel cost per ton-km, traced through cargo mix and load factor by weight. This distinction matters operationally: three routes need delay mitigation, one needs load optimization, and treating all four the same would misdiagnose the fix.

Output: `route_risk` (MySQL table and `data/processed/route_risk.csv`), documenting the route-level aggregation used in this analysis. The Tableau Route Analysis dashboard calculates the equivalent aggregation directly from `trip_analytical_dataset`. Truck- and driver-specific causes are explored further in `08_truck_driver_performance.ipynb`.