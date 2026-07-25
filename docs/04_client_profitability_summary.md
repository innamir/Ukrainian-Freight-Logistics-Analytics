# Client Profitability — Summary

## Purpose

Identify which clients generate the highest profit — not just revenue — and diagnose the root causes behind low-margin relationships. This summary reflects `05_client_profitability.ipynb`, built on `trip_analytical_dataset` (the single source of truth from `03_build_trip_analytical_dataset.ipynb`).

## Methodology Note

The analysis focuses on clients active during 2024. Comparing clients across incomplete business periods (partial 2022 or 2024 activity, different tenure lengths) would produce misleading conclusions — a fixed calendar window makes the comparison fair. All 10 clients in the portfolio were active in 2024; none were excluded.

## Client Profitability (2024)

Ranked by gross profit, not revenue — the direct answer to "who generates the most profit."

| Client | Trips | Revenue (UAH) | Gross Profit (UAH) | Margin |
|---|---|---|---|---|
| ТОВ Полтавські Лани | 167 | 4,141,124 | 2,084,856 | 50.3% |
| ПП ДніпроЗерно | 192 | 3,889,903 | 2,034,546 | 52.3% |
| ТОВ Соняшник-Агро | 227 | 3,064,563 | 1,887,739 | 61.6% |
| АгроЛогістика Центр | 184 | 2,537,897 | 1,501,809 | 59.2% |
| ТОВ Соєвий Дім | 94 | 728,171 | 491,528 | 67.5% |

All 10 clients exceed the 15-trip reliability threshold — no client required exclusion due to insufficient sample size.

## Key Findings

- **Regular clients significantly outperform seasonal ones, even within the same season.** Comparing both groups only during the peak months (Jul-Sep) — to avoid the bias of regular clients' annual average including slower off-peak months — regular clients still operate at a meaningfully higher margin (58.1%) than seasonal clients (50.3%), a 7.8 percentage point gap. This is wider than the naive full-year comparison (55.6% vs 50.3%), confirming the lower margin is a genuine characteristic of seasonal client relationships, not a measurement artifact.
- **Scale drives the top profit rank, not efficiency.** ТОВ Полтавські Лани generates the most profit but has the lowest margin among the top 5 (50.3%). ТОВ Соєвий Дім has the highest margin (67.5%) but ranks only 5th by profit — its low trip volume limits total contribution despite being the most efficient client per trip.
- **Moderate customer concentration.** The top 3 clients generate 63.4% of total 2024 gross profit; the top 5 generate 84.4% — softer than a classic 80/20 Pareto split, but still a meaningful dependency on a small group of clients.
- **Two structural-risk clients share the same root cause: underpriced tariffs and port-side delays.** ТОВ Полтавські Лани and ПП ДніпроЗерно are both low-margin, high-profit-share clients. Both pay below-market tariffs (1.87 and 1.98 UAH/ton-km respectively, versus 2.40–2.95 for other top clients) and both have delays 100% concentrated on a single port-destination route — Полтава → Чорноморськ (51/51 delayed trips, avg. 26.1h) and Дніпро → Одеса (56/56 delayed trips, avg. 28.4h).
- **ТОВ Нива Експорт's low margin is a 2024-specific decline, consistent with the seasonal pattern above.** This client is seasonal (`is_seasonal=1`), with the lowest margin overall (43.8%) but contributing only 7.5% of total profit. It is not new — active since 2022-07-03, with a margin history of 49.0% (2022) → 51.2% (2023, peak) → 43.8% (2024). The 2024 drop is consistent with both this year's elevated delay rate and the confirmed seasonal-client underperformance pattern.

## Business Recommendations

- **ТОВ Полтавські Лани:** renegotiate tariff toward the 2.0–2.5 UAH/ton-km range paid by comparable clients; investigate port-side delays on the Полтава → Чорноморськ route specifically.
- **ПП ДніпроЗерно:** same two-step review — moderate tariff adjustment plus investigation of delays on the Дніпро → Одеса route.
- **ТОВ Нива Експорт:** investigate what changed operationally in 2024 before considering tariff or relationship changes — the 2022–2023 track record suggests the relationship is recoverable.
- Seasonal clients operate at a structurally lower margin than regular clients even during the same peak season (50.3% vs 58.1%, a 7.8 pp gap) — review whether seasonal contracts should carry a premium to offset this.
- Increase business volume with high-margin, lower-volume clients (e.g. ТОВ Соєвий Дім) to reduce dependency on less efficient top-revenue relationships and diversify profit sources.
- Monitor cancellation/delay rates across all clients, as reliability risk erodes profitability over time even where margin currently looks acceptable.

## Next Steps

Port-route delays affecting two independent clients point to a broader operational pattern worth investigating at the route level — this will be explored in `07_route_analysis.ipynb`.

Output: `client_profitability_2024` (MySQL table and `data/processed/client_profitability_2024.csv`) for the Tableau Client Profitability dashboard.