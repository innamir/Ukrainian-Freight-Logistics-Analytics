/* ============================================================
   File: 03_change_data_types.sql

   Project: Ukrainian Freight Logistics Analytics

   Description:
   Standardizes data types after CSV import.

   Author: Inna Myroshnychenko
   ============================================================ */

USE ukrainian_freight_logistics;

-- ============================================================
-- TRIPS
-- ============================================================

ALTER TABLE trips
MODIFY trip_id VARCHAR(50) NOT NULL,
MODIFY date_departure DATETIME,
MODIFY distance_km DECIMAL(10,2),
MODIFY cargo_tons_actual DECIMAL(10,2),
MODIFY load_factor_pct DECIMAL(5,2),
MODIFY delay_hours DECIMAL(5,2);


-- ============================================================
-- TRUCKS
-- ============================================================

ALTER TABLE trucks
MODIFY truck_id VARCHAR(50) NOT NULL,
MODIFY year_manufactured SMALLINT,
MODIFY capacity_tons DECIMAL(10,2),
MODIFY engine_volume DECIMAL(10,2),
MODIFY mileage_start_km INT,
MODIFY tank_capacity_liters SMALLINT;

-- ============================================================
-- DRIVERS
-- ============================================================

ALTER TABLE drivers
MODIFY driver_id VARCHAR(50) NOT NULL,
MODIFY driver_commission_rate DECIMAL(5,2),
MODIFY hire_date DATETIME,
MODIFY trips_per_month_avg TINYINT;

-- ============================================================
-- CLIENTS
-- ============================================================
UPDATE clients
SET
    active_from = NULLIF(active_from, ''),
    active_to   = NULLIF(active_to, '');

ALTER TABLE clients
MODIFY client_id VARCHAR(50) NOT NULL,
MODIFY payment_terms_days TINYINT,
MODIFY is_seasonal BOOLEAN,
MODIFY active_from DATETIME,
MODIFY active_to DATETIME;

-- ============================================================
-- ROUTES
-- ============================================================

ALTER TABLE routes
MODIFY route_id VARCHAR(50) NOT NULL,
MODIFY distance_km SMALLINT,
MODIFY has_port BOOLEAN;

-- ============================================================
-- CLIENT RATES
-- ============================================================

ALTER TABLE client_rates
MODIFY rate_id VARCHAR(50) NOT NULL,
MODIFY distance_from_km DECIMAL(10,2),
MODIFY distance_to_km DECIMAL(10,2),
MODIFY weight_from_tons DECIMAL(10,2),
MODIFY weight_to_tons DECIMAL(10,2),
MODIFY rate_uah_per_ton_km DECIMAL(10,2),
MODIFY valid_from DATETIME,
MODIFY valid_to DATETIME;

-- ============================================================
-- FUEL BATCHES
-- ============================================================

ALTER TABLE fuel_batches
MODIFY batch_id VARCHAR(50) NOT NULL,
MODIFY purchase_date DATETIME,
MODIFY liters_purchased DECIMAL(10,2),
MODIFY price_per_liter_uah DECIMAL(10,2),
MODIFY total_cost_uah DECIMAL(12,2);

-- ============================================================
-- TRUCK REFUELINGS
-- ============================================================

ALTER TABLE truck_refuelings
MODIFY refuel_id VARCHAR(50) NOT NULL,
MODIFY refuel_date DATETIME,
MODIFY odometer_at_refuel INT,
MODIFY liters_refueled DECIMAL(10,2);

-- ============================================================
-- TRUCK DOWNTIME
-- ============================================================

ALTER TABLE truck_downtime
MODIFY downtime_id VARCHAR(50) NOT NULL,
MODIFY date_from DATETIME,
MODIFY date_to DATETIME;

-- ============================================================
-- TRIP METRICS
-- ============================================================

ALTER TABLE trip_metrics
MODIFY trip_id VARCHAR(50) NOT NULL,
MODIFY odometer_after_trip INT,
MODIFY recorded_at DATETIME;