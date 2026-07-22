/* ============================================================
   Project : Ukrainian Freight Logistics Analytics
   File    : 04_data_quality.sql
   Author  : Inna Myroshnychenko

   Purpose:
   Validate source data before calculating KPIs,
   profitability metrics and business insights.

   SQL Dialect: MySQL 8.0
============================================================ */

USE ukrainian_freight_logistics;

-- ============================================================
-- 1. DATASET OVERVIEW
-- Verify that all tables were imported successfully.
-- ============================================================

SELECT 'trucks' AS table_name, COUNT(*) AS row_count FROM trucks
UNION ALL
SELECT 'drivers', COUNT(*) FROM drivers
UNION ALL
SELECT 'clients', COUNT(*) FROM clients
UNION ALL
SELECT 'routes', COUNT(*) FROM routes
UNION ALL
SELECT 'client_rates', COUNT(*) FROM client_rates
UNION ALL
SELECT 'fuel_batches', COUNT(*) FROM fuel_batches
UNION ALL
SELECT 'truck_refuelings', COUNT(*) FROM truck_refuelings
UNION ALL
SELECT 'truck_downtime', COUNT(*) FROM truck_downtime
UNION ALL
SELECT 'trips', COUNT(*) FROM trips
UNION ALL
SELECT 'trip_metrics', COUNT(*) FROM trip_metrics;

-- ============================================================
-- 2. DATE COVERAGE
-- Check that the imported data covers the expected period.
-- ============================================================

SELECT
    'trips' AS table_name,
    MIN(date_departure) AS first_date,
    MAX(date_departure) AS last_date,
    COUNT(*) AS total_records
FROM trips

UNION ALL

SELECT
    'truck_refuelings',
    MIN(refuel_date),
    MAX(refuel_date),
    COUNT(*)
FROM truck_refuelings

UNION ALL

SELECT
    'fuel_batches',
    MIN(purchase_date),
    MAX(purchase_date),
    COUNT(*)
FROM fuel_batches

UNION ALL

SELECT
    'trip_metrics',
    MIN(recorded_at),
    MAX(recorded_at),
    COUNT(*)
FROM trip_metrics;

-- ============================================================
-- 3. MISSING VALUES
-- Check critical fields required for further analysis.
-- ============================================================

SELECT
    'Trips' AS table_name,
    COUNT(*) AS failed_records
FROM trips
WHERE trip_id IS NULL
   OR truck_id IS NULL
   OR driver_id IS NULL
   OR client_id IS NULL
   OR route_id IS NULL
   OR date_departure IS NULL
   OR date_arrival IS NULL
   OR distance_km IS NULL
   OR cargo_tons_actual IS NULL
   OR load_factor_pct IS NULL
   OR status IS NULL

UNION ALL

SELECT
    'Truck Refuelings',
    COUNT(*)
FROM truck_refuelings
WHERE refuel_id IS NULL
   OR truck_id IS NULL
   OR refuel_date IS NULL
   OR liters_refueled IS NULL
   OR odometer_at_refuel IS NULL

UNION ALL

SELECT
    'Fuel Batches',
    COUNT(*)
FROM fuel_batches
WHERE batch_id IS NULL
   OR purchase_date IS NULL
   OR liters_purchased IS NULL
   OR price_per_liter_uah IS NULL
   OR total_cost_uah IS NULL

UNION ALL

SELECT
    'Trip Metrics',
    COUNT(*)
FROM trip_metrics
WHERE trip_id IS NULL
   OR odometer_after_trip IS NULL
   OR recorded_at IS NULL

UNION ALL

SELECT
    'Client Rates',
    COUNT(*)
FROM client_rates
WHERE rate_id IS NULL
   OR client_id IS NULL
   OR distance_from_km IS NULL
   OR distance_to_km IS NULL
   OR weight_from_tons IS NULL
   OR weight_to_tons IS NULL
   OR rate_uah_per_ton_km IS NULL
   OR valid_from IS NULL
   OR valid_to IS NULL;


-- ============================================================
-- 4. REFERENTIAL INTEGRITY
-- Check for orphan records (missing parent records).
-- ============================================================

SELECT
    'Trips -> Trucks' AS relationship_name,
    COUNT(*) AS invalid_records
FROM trips t
LEFT JOIN trucks tr
    ON t.truck_id = tr.truck_id
WHERE tr.truck_id IS NULL

UNION ALL

SELECT
    'Trips -> Drivers',
    COUNT(*)
FROM trips t
LEFT JOIN drivers d
    ON t.driver_id = d.driver_id
WHERE d.driver_id IS NULL

UNION ALL

SELECT
    'Trips -> Clients',
    COUNT(*)
FROM trips t
LEFT JOIN clients c
    ON t.client_id = c.client_id
WHERE c.client_id IS NULL

UNION ALL

SELECT
    'Trips -> Routes',
    COUNT(*)
FROM trips t
LEFT JOIN routes r
    ON t.route_id = r.route_id
WHERE r.route_id IS NULL

UNION ALL

SELECT
    'Routes -> Clients',
    COUNT(*)
FROM routes r
LEFT JOIN clients c
    ON r.client_id = c.client_id
WHERE c.client_id IS NULL

UNION ALL

SELECT
    'Truck Refuelings -> Trucks',
    COUNT(*)
FROM truck_refuelings rf
LEFT JOIN trucks tr
    ON rf.truck_id = tr.truck_id
WHERE tr.truck_id IS NULL

UNION ALL

SELECT
    'Truck Downtime -> Trucks',
    COUNT(*)
FROM truck_downtime td
LEFT JOIN trucks tr
    ON td.truck_id = tr.truck_id
WHERE tr.truck_id IS NULL

UNION ALL

SELECT
    'Trip Metrics -> Trips',
    COUNT(*)
FROM trip_metrics tm
LEFT JOIN trips t
    ON tm.trip_id = t.trip_id
WHERE t.trip_id IS NULL

UNION ALL

SELECT
    'Client Rates -> Clients',
    COUNT(*)
FROM client_rates cr
LEFT JOIN clients c
    ON cr.client_id = c.client_id
WHERE c.client_id IS NULL;

/*
Expected result:
All relationships should return 0 invalid records.
Any non-zero value indicates orphan records that require investigation.
*/


-- ============================================================
-- 5. BUSINESS RULE VALIDATION
-- Validate business logic and domain-specific rules.
-- ============================================================

SELECT
    'Trips' AS category,
    'Arrival before departure' AS check_name,
    COUNT(*) AS failed_records
FROM trips
WHERE date_arrival < date_departure

UNION ALL

SELECT
    'Trips',
    'Non-positive trip distance',
    COUNT(*)
FROM trips
WHERE distance_km <= 0

UNION ALL

SELECT
    'Trips',
    'Non-positive cargo weight',
    COUNT(*)
FROM trips
WHERE cargo_tons_actual <= 0

UNION ALL

SELECT
    'Trips' AS category,
    'Load factor exceeds 115%' AS check_name,
    COUNT(*) AS failed_records
FROM trips t
JOIN trucks tr
ON t.truck_id = tr.truck_id
WHERE (t.cargo_tons_actual / tr.capacity_tons) > 1.15

UNION ALL

SELECT
    'Trips',
    'Negative delay',
    COUNT(*)
FROM trips
WHERE delay_hours < 0

UNION ALL

SELECT
    'Fuel',
    'Fuel batch cost mismatch',
    COUNT(*)
FROM fuel_batches
WHERE ABS(total_cost_uah - (liters_purchased * price_per_liter_uah)) > 1

UNION ALL

SELECT
    'Fuel',
    'Invalid refueling volume',
    COUNT(*)
FROM truck_refuelings
WHERE liters_refueled <= 0

UNION ALL

SELECT
    'Fuel',
    'Refueling exceeds tank capacity',
    COUNT(*)
FROM truck_refuelings rf
JOIN trucks t
    ON rf.truck_id = t.truck_id
WHERE rf.liters_refueled > t.tank_capacity_liters

UNION ALL

SELECT
    'Fleet',
    'Cargo exceeds truck capacity',
    COUNT(*)
FROM trips tr
JOIN trucks t
    ON tr.truck_id = t.truck_id
WHERE tr.cargo_tons_actual > t.capacity_tons

UNION ALL

SELECT
    'Fleet',
    'Trips during truck downtime',
    COUNT(*)
FROM trips tr
JOIN truck_downtime td
    ON tr.truck_id = td.truck_id
   AND tr.date_departure BETWEEN td.date_from AND td.date_to;
-- ============================================================
-- 6. CLIENT RATE VALIDATION
-- Validate tariff structure and validity periods.
-- ============================================================

SELECT
    'Tariff Structure' AS category,
    'Distance range start >= end' AS check_name,
    COUNT(*) AS failed_records
FROM client_rates
WHERE distance_from_km >= distance_to_km

UNION ALL

SELECT
    'Tariff Structure',
    'Weight range start >= end',
    COUNT(*)
FROM client_rates
WHERE weight_from_tons >= weight_to_tons

UNION ALL

SELECT
    'Tariff Structure',
    'Invalid tariff validity period',
    COUNT(*)
FROM client_rates
WHERE valid_from >= valid_to

UNION ALL

SELECT
    'Tariff Structure',
    'Negative tariff rate',
    COUNT(*)
FROM client_rates
WHERE rate_uah_per_ton_km <= 0

UNION ALL

SELECT
    'Tariff Coverage',
    'Trips without matching tariff',
    COUNT(*)
FROM (
    SELECT
        t.trip_id
    FROM trips t
    LEFT JOIN client_rates cr
        ON t.client_id = cr.client_id
       AND t.date_departure BETWEEN cr.valid_from AND cr.valid_to
       AND t.distance_km >= cr.distance_from_km
       AND t.distance_km < cr.distance_to_km
       AND t.cargo_tons_actual >= cr.weight_from_tons
       AND t.cargo_tons_actual < cr.weight_to_tons
    WHERE cr.rate_id IS NULL
) x;


-- ============================================================
-- 7. ROUTE CONSISTENCY
-- Validate route-related business logic.
-- ============================================================

SELECT
    'Routes' AS category,
    'Trip distance differs from route distance by more than 10%',
    COUNT(*) AS failed_records
FROM trips t
JOIN routes r
    ON t.route_id = r.route_id
WHERE ABS(t.distance_km - r.distance_km) > r.distance_km * 0.10

UNION ALL

SELECT
    'Routes',
    'Origin city differs from route',
    COUNT(*)
FROM trips t
JOIN routes r
    ON t.route_id = r.route_id
WHERE t.origin_city <> r.origin_city

UNION ALL

SELECT
    'Routes',
    'Destination city differs from route',
    COUNT(*)
FROM trips t
JOIN routes r
    ON t.route_id = r.route_id
WHERE t.destination_city <> r.destination_city

UNION ALL

SELECT
    'Routes',
    'Route type differs',
    COUNT(*)
FROM trips t
JOIN routes r
    ON t.route_id = r.route_id
WHERE t.route_type <> r.route_type;