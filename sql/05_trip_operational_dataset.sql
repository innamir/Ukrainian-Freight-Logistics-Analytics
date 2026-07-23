-- =============================================================
-- 02_trip_operational_dataset.sql
-- One row per trip: all base trip attributes, enriched with
-- business-readable dimensions (client, driver, truck, route),
-- plus revenue (via ranked rate matching) and estimated fuel
-- volume consumed (via odometer-interval proportional split).
--
-- Deliberately NOT included here: fuel cost / gross profit.
-- Pricing requires FIFO allocation against the company-wide
-- fuel_batches purchase queue, which is sequential/stateful
-- logic handled in Python, not SQL. This query only produces
-- the inputs Python needs: liters per trip + a date to place
-- each trip in the consumption timeline.
-- =============================================================

WITH ranked_rates AS (
    SELECT
        t.trip_id,
        cr.rate_uah_per_ton_km,
        ROW_NUMBER() OVER (
            PARTITION BY t.trip_id
            ORDER BY
                CASE
                    WHEN t.cargo_tons_actual BETWEEN cr.weight_from_tons AND cr.weight_to_tons THEN 1
                    ELSE 2
                END,
                cr.weight_to_tons DESC
        ) AS rate_rank
    FROM trips t
    JOIN client_rates cr
        ON cr.client_id = t.client_id
        AND t.distance_km BETWEEN cr.distance_from_km AND cr.distance_to_km
        AND t.date_departure BETWEEN cr.valid_from AND cr.valid_to
),

trip_revenue AS (
    SELECT
        t.trip_id,
        CASE
            WHEN t.status <> 'cancelled'
                THEN t.distance_km * t.cargo_tons_actual * rr.rate_uah_per_ton_km
            ELSE NULL
        END AS revenue_uah
    FROM trips t
    LEFT JOIN ranked_rates rr
        ON rr.trip_id = t.trip_id
        AND rr.rate_rank = 1
),

-- -------------------------------------------------------------
-- Fuel volume per trip. A refuel always tops the tank to full,
-- so liters consumed since the previous refuel (or since the
-- truck's starting mileage, for the first refuel) equals that
-- refuel's liters_refueled. Split proportionally across trips
-- in that odometer interval by distance_km.
-- -------------------------------------------------------------
refuel_ordered AS (
    SELECT
        r.truck_id,
        r.refuel_id,
        r.odometer_at_refuel,
        r.liters_refueled,
        LAG(r.odometer_at_refuel) OVER (
            PARTITION BY r.truck_id ORDER BY r.odometer_at_refuel
        ) AS prev_refuel_odometer
    FROM truck_refuelings r
),

refuel_intervals AS (
    SELECT
        ro.truck_id,
        ro.refuel_id,
        COALESCE(ro.prev_refuel_odometer, tr.mileage_start_km) AS interval_start_odo,
        ro.odometer_at_refuel AS interval_end_odo,
        ro.liters_refueled AS consumed_liters
    FROM refuel_ordered ro
    JOIN trucks tr
        ON tr.truck_id = ro.truck_id
),

trip_odo AS (
    SELECT
        t.trip_id,
        t.truck_id,
        t.distance_km,
        tm.odometer_after_trip
    FROM trips t
    JOIN trip_metrics tm
        ON tm.trip_id = t.trip_id
    WHERE t.status <> 'cancelled'
),

trip_interval_map AS (
    SELECT
        ti.trip_id,
        ti.distance_km,
        ri.refuel_id,
        ri.consumed_liters
    FROM trip_odo ti
    JOIN refuel_intervals ri
        ON ri.truck_id = ti.truck_id
        AND ti.odometer_after_trip > ri.interval_start_odo
        AND ti.odometer_after_trip <= ri.interval_end_odo
),

interval_totals AS (
    SELECT refuel_id, SUM(distance_km) AS interval_total_distance
    FROM trip_interval_map
    GROUP BY refuel_id
),

trip_fuel_liters AS (
    SELECT
        tim.trip_id,
        ROUND(
            tim.consumed_liters * (tim.distance_km / it.interval_total_distance), 2
        ) AS estimated_fuel_liters
    FROM trip_interval_map tim
    JOIN interval_totals it
        ON it.refuel_id = tim.refuel_id
)

-- -------------------------------------------------------------
-- FINAL: one row per trip, enriched with business-readable
-- dimensions. estimated_fuel_liters is NULL for trailing trips
-- after a truck's last recorded refuel, and for cancelled trips
-- (no trip_metrics record). revenue_uah is NULL for cancelled
-- trips.
-- -------------------------------------------------------------
SELECT
    t.trip_id,
    t.date_departure,
    t.date_arrival,
    t.status,

    -- Client
    t.client_id,
    c.company_name AS client_name,
    c.region AS client_region,

    -- Route
    t.route_id,
    t.origin_city,
    t.destination_city,
    t.route_type,
    t.cargo_type,
    t.distance_km AS trip_distance_km,
    r.distance_km AS route_distance_km,
    r.has_port AS route_has_port,

    -- Truck
    t.truck_id,
    tr.brand AS truck_brand,
    tr.model AS truck_model,
    tr.capacity_tons AS truck_capacity_tons,
    tr.year_manufactured AS truck_year,

    -- Driver
    t.driver_id,
    d.full_name AS driver_name,
    d.driver_commission_rate,

    -- Trip metrics
    t.cargo_tons_actual,
    t.load_factor_pct,
    t.delay_hours,

    -- Financials (revenue only -- fuel cost computed in Python)
    tvr.revenue_uah,
    tfl.estimated_fuel_liters

FROM trips t
JOIN clients c
    ON c.client_id = t.client_id
JOIN routes r
    ON r.route_id = t.route_id
JOIN trucks tr
    ON tr.truck_id = t.truck_id
JOIN drivers d
    ON d.driver_id = t.driver_id
LEFT JOIN trip_revenue tvr
    ON tvr.trip_id = t.trip_id
LEFT JOIN trip_fuel_liters tfl
    ON tfl.trip_id = t.trip_id
ORDER BY t.date_departure, t.trip_id;