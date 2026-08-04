# Business Recommendations — Summary

## Purpose

Consolidate the business recommendations from all four business-question notebooks (`05_client_profitability.ipynb`, `06_fuel_cost_impact.ipynb`, `07_route_analysis.ipynb`, `08_truck_driver_performance.ipynb`) into a single, priority-ordered action list. Individual notebooks investigate in the order questions were raised; this document reorders by expected business impact.

## How Priority Was Assigned

**High** — structural risk confirmed causally, with a clear fix and meaningful profit exposure. **Medium** — real risk, but smaller in scale, less certain, or requiring further investigation before acting. **Low** — monitoring/hygiene items, or risks the analysis explicitly ruled out (framed as "don't do X").

## High Priority

1. **Renegotiate tariffs for all four port routes.** ТОВ Полтавські Лани (Полтава-Чорноморськ) and ПП ДніпроЗерно (Дніпро-Одеса) were flagged first at the client level (`04_client_profitability_summary.md`). Route-level analysis (`06_route_analysis_summary.md`) confirms this is a category-wide gap, not two isolated cases: comparing tariff across the full 10-route network, not just among port routes, three of the four port routes — including Подільськ-Чорноморськ — are priced below every non-port route (1.87-1.98 vs. 2.07-2.95 UAH/ton-km); the fourth, Миколаїв-Одеса (2.11), sits at the low end of the non-port range too. Extend the tariff review already underway for the first two clients to all four port routes.
2. **Additionally fix Подільськ-Чорноморськ's (ТОВ Нива Експорт) load factor.** Beyond the shared tariff gap above, this route has a second, independent problem: a low load factor by weight (85.6%) tied to its 100% wheat cargo mix, which pushes it below even its own port-route peers — tariff and delay were tested specifically against those peers and don't explain that extra gap. Reassigning a different truck to this route was also tested and ruled out (`08_truck_driver_performance_summary.md`) — the fix is tariff review (shared with item 1) plus loading practice, not truck assignment.

## Medium Priority

3. **Investigate the external port-disruption hypothesis** before treating the 2024 decline on three port routes (Дніпро-Одеса, Миколаїв-Одеса, Полтава-Чорноморськ) as permanent. All three show the same 2023-peak/2024-decline pattern and returned to roughly their 2022 baseline — consistent with a shared external cause (e.g. Black Sea port disruption, not tested directly) rather than three independent failures (`06_route_analysis_summary.md`).
4. **Add fuel-cost pass-through clauses for ФГ Кукурудза Південь.** `04_client_profitability_summary.md` found this client's profit share too small (2.4-3.1%) to warrant the tariff/delay investigation given to the two structural-risk clients above. But `05_fuel_cost_summary.md` flags it separately for compounded fuel exposure (high fuel intensity + low rate and margin) — a forward-looking risk that's independent of current profit contribution.
5. **Protect seasonal clients contractually.** Two independent notebooks converge on the same client segment: seasonal clients run a structurally lower margin even within the same season (50.3% vs. 58.1%, `04_client_profitability_summary.md`) and show wider, less predictable margin swings under fuel-price pressure (`05_fuel_cost_summary.md`). Add a seasonal premium and a fuel-cost escalation clause.
6. **Grow volume with high-margin, lower-volume clients** (e.g. ТОВ Соєвий Дім, 67.5% margin) to reduce dependency on less-efficient top-revenue relationships (`04_client_profitability_summary.md`).

## Low Priority / Monitoring

7. **Don't rely on bulk fuel purchasing as a permanent buffer.** It currently cushions the realized-rate/fuel-cost gap, but any reduction in how far ahead the company buys would expose this more sharply than the historical trend suggests (`05_fuel_cost_summary.md`).
8. **Track truck downtime and margin as separate metrics.** Two of the highest-downtime trucks are among the fleet's most profitable — downtime is not a valid proxy for truck inefficiency (`08_truck_driver_performance_summary.md`).
9. **Skip fleet-wide truck replacement or age-based capex.** Truck age is not a consistent driver of margin or fuel efficiency; monitor only the two oldest trucks individually (`08_truck_driver_performance_summary.md`).
10. **Monitor cancellation/delay rates across all clients** as ongoing hygiene — reliability risk erodes profitability over time even where margin currently looks acceptable (`04_client_profitability_summary.md`).
11. **Deprioritize `route_type` and truck-level factors as analytical lenses.** Neither explains meaningful variance anywhere in this analysis (`route_has_port` and cargo mix dominate `route_type`; client- and route-level effects dominate truck-level ones) — further investigation along either lens has low expected return (`05_fuel_cost_summary.md`, `08_truck_driver_performance_summary.md`).

## Cross-Notebook Convergence

Two patterns are worth calling out because they only become visible once all four notebooks are read together, not from any single one:

- **ТОВ Полтавські Лани and ПП ДніпроЗерно are the same risk, found twice.** Client-level analysis (`04_client_profitability_summary.md`) and route-level analysis (`06_route_analysis_summary.md`) independently flagged the same two accounts — because each client operates exactly one fixed route, "high-risk client" and "high-risk route" are the same fact here, not corroborating but distinct evidence. Two different analytical framings converging without either being designed to reproduce the other is a meaningfully stronger signal than either alone.
- **Подільськ-Чорноморськ turned out to have two independent, additive causes, not one that replaced another.** `04_client_profitability_summary.md` first flagged it for operational investigation. `05_fuel_cost_summary.md` flagged a tariff/fuel-pass-through angle — confirmed, not overturned, once `06_route_analysis_summary.md` compared its tariff against the full 10-route network rather than just the other three port routes: all four port routes, including this one, are priced below the rest of the network. `06_route_analysis_summary.md` additionally uncovered a second, independent mechanism specific to this route — a wheat-cargo-driven load factor issue explaining why it underperforms even its own port-route peers, on top of the shared tariff gap. `08_truck_driver_performance_summary.md` then confirmed this second mechanism is route-specific, not a truck-assignment issue. The lesson here is the opposite of the client/route convergence above: two analyses can each be right about a different, compounding cause — the fix is to add findings together, not assume a later, more granular analysis overturns an earlier one just because it adds nuance.

## Summary

Across all four business-question notebooks, two structural risks account for the majority of concrete, actionable findings: underpriced, delay-prone port routes — all four, not just the two originally flagged at the client level — and an additional, cargo-mix-driven load-factor problem specific to Подільськ-Чорноморськ, compounding rather than replacing the shared tariff issue. Both have clear commercial and operational fixes. Fuel price risk is real but concentrated in specific clients rather than fleet-wide, and neither truck age, truck assignment, nor downtime explain any of the profitability patterns found elsewhere in the analysis — truck- and route-type-level intervention are consistently the lowest-priority levers across all four notebooks.

This document draws on outputs already published by notebooks 05-08 (`client_profitability_2024`, `client_fuel_risk`, `route_risk`, `truck_performance`) and does not introduce new calculations.