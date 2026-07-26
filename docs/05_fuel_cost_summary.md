# Fuel Cost Impact — Summary

## Purpose

Was the rise in fuel prices a critical factor affecting business viability? This summary reflects `06_fuel_cost_impact.ipynb`, built on `trip_analytical_dataset` and `fuel_batches`.

## Methodology Note

Fuel price trend, company performance, and the freight-rate comparison use the full period (Jul 2022 – Oct 2024). Client- and route-level exposure analysis are limited to 2024, consistent with `05_client_profitability.ipynb`.

Realized rate is compared against **actual fuel cost per unit of work** (`fuel_cost_uah`), not the external market price of diesel. Fuel is purchased in bulk batches and consumed via FIFO, so trips run on fuel paid for earlier, not at today's market price — comparing tariffs to market price directly would understate how closely pricing tracks the company's real cost base.

## Key Findings

- **Diesel prices rose 14.0% from 2022 to 2024** on average, following a V-shaped pattern rather than a steady increase — falling through early 2023, rising sharply to a peak around April 2024, then easing slightly.
- **Company-level gross margin held steady** (51–65% range, no sustained decline) despite this. Revenue volatility far exceeds fuel cost volatility month to month, pointing to seasonal demand, not fuel prices, as the main driver of performance swings.
- **Realized rate rose 15.6% over the period, slightly trailing the 17.1% rise in actual fuel cost per unit of work** — a modest 1.5-point gap, not a dramatic shortfall. This likely understates the real pricing pressure: bulk fuel purchasing locks in prices below current market rates during spikes, cushioning `fuel_cost_uah` from the full market impact.
- The route-type mix shifted slightly (highway 58%→63%) but doesn't meaningfully explain the rate-cost gap. In H2 2024, the gap narrowed (rate +1.8% vs fuel cost +1.2%) — pricing is catching up, not falling further behind.
- **Regular and seasonal clients diverge sharply**: regular-client margin stayed within a stable 55–65% band throughout, while seasonal-client margin swung much wider, dropping to ~47% at times — seasonal clients absorb fuel cost pressure less consistently.
- **Fuel exposure concentrates in specific clients, not evenly**: ТОВ Нива Експорт, ТОВ Полтавські Лани, and ФГ Кукурудза Південь combine the highest fuel intensity with the lowest rates and margins — a compounded, forward-looking risk. ТОВ Соєвий Дім and ТОВ Соняшник-Агро are the best-insulated (low intensity, high rates and margins).
- **Route type is a weak differentiator** (highway 7.80 vs local 7.37 L/1,000 UAH, 5.5% difference) — client-specific factors, not route category, drive fuel exposure.

## Business Recommendations

- Close the pricing gap: realized rate has slightly trailed actual fuel cost (15.6% vs 17.1%), and this gap is likely wider once bulk-purchasing discounts are accounted for. Treat pricing as proactive, not reactive.
- Prioritize ТОВ Нива Експорт, ТОВ Полтавські Лани, and ФГ Кукурудза Південь for tariff review with fuel cost pass-through clauses — these three carry compounded exposure and are most vulnerable to further fuel price increases.
- Extend seasonal client contracts to include fuel cost escalation clauses — seasonal clients show the widest margin swings and the least built-in pricing protection.
- Don't rely on bulk fuel purchasing as a permanent buffer — any reduction in how far ahead the company can buy would expose the rate-cost gap more sharply than the historical trend suggests.
- Route type is not a useful lens for fuel risk management — defer further investigation to specific routes in `07_route_analysis.ipynb`.

## Summary

Rising diesel prices (14.0%, 2022–2024, V-shaped) did not threaten business viability. Margin held steady overall, though realized rate (15.6%) slightly trailed the rise in actual fuel cost per unit of work (17.1%) — a gap likely understated by bulk fuel purchasing, which cushions the company from current market rates but isn't a permanent buffer.

Resilience is uneven: seasonal clients show more fuel-price-sensitive margin than regular clients, and three clients (ТОВ Нива Експорт, ТОВ Полтавські Лани, ФГ Кукурудза Південь) carry compounded exposure, making them most vulnerable. Route type is not a meaningful risk factor; exposure concentrates at the client level.

Output: `client_fuel_risk` (MySQL table and `data/processed/client_fuel_risk.csv`) for the Tableau Fuel Cost Analysis dashboard. Route-level causes are explored in `07_route_analysis.ipynb`.