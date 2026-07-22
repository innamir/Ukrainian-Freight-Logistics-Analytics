/* ============================================================
   04_constraints_and_indexes.sql

   Project: Ukrainian Freight Logistics Analytics

   Purpose:
   Add primary keys, foreign keys and analytical indexes
   after CSV import and data type standardization.

   Author: Inna Myroshnychenko
============================================================ */

USE ukrainian_freight_logistics;

-- ============================================================
-- PRIMARY KEYS
-- ============================================================

ALTER TABLE trucks
ADD PRIMARY KEY (truck_id);

ALTER TABLE drivers
ADD PRIMARY KEY (driver_id);

ALTER TABLE clients
ADD PRIMARY KEY (client_id);

ALTER TABLE routes
ADD PRIMARY KEY (route_id);

ALTER TABLE trips
ADD PRIMARY KEY (trip_id);

ALTER TABLE client_rates
ADD PRIMARY KEY (rate_id);

ALTER TABLE fuel_batches
ADD PRIMARY KEY (batch_id);

ALTER TABLE truck_refuelings
ADD PRIMARY KEY (refuel_id);

ALTER TABLE truck_downtime
ADD PRIMARY KEY (downtime_id);

ALTER TABLE trip_metrics
ADD PRIMARY KEY (trip_id);



-- ============================================================
-- FOREIGN KEYS
-- ============================================================

ALTER TABLE routes
ADD CONSTRAINT fk_routes_client
FOREIGN KEY (client_id)
REFERENCES clients(client_id);



ALTER TABLE trips
ADD CONSTRAINT fk_trips_truck
FOREIGN KEY (truck_id)
REFERENCES trucks(truck_id);

ALTER TABLE trips
ADD CONSTRAINT fk_trips_driver
FOREIGN KEY (driver_id)
REFERENCES drivers(driver_id);

ALTER TABLE trips
ADD CONSTRAINT fk_trips_client
FOREIGN KEY (client_id)
REFERENCES clients(client_id);

ALTER TABLE trips
ADD CONSTRAINT fk_trips_route
FOREIGN KEY (route_id)
REFERENCES routes(route_id);



ALTER TABLE client_rates
ADD CONSTRAINT fk_client_rates_client
FOREIGN KEY (client_id)
REFERENCES clients(client_id);



ALTER TABLE truck_refuelings
ADD CONSTRAINT fk_refuelings_truck
FOREIGN KEY (truck_id)
REFERENCES trucks(truck_id);



ALTER TABLE truck_downtime
ADD CONSTRAINT fk_downtime_truck
FOREIGN KEY (truck_id)
REFERENCES trucks(truck_id);



ALTER TABLE trip_metrics
ADD CONSTRAINT fk_trip_metrics_trip
FOREIGN KEY (trip_id)
REFERENCES trips(trip_id);



-- ============================================================
-- INDEXES
-- ============================================================

-- Trips

CREATE INDEX idx_trips_departure_date
ON trips(date_departure);

CREATE INDEX idx_trips_truck
ON trips(truck_id);

CREATE INDEX idx_trips_driver
ON trips(driver_id);

CREATE INDEX idx_trips_client
ON trips(client_id);

CREATE INDEX idx_trips_route
ON trips(route_id);



-- Routes

CREATE INDEX idx_routes_client
ON routes(client_id);



-- Client tariff lookup

CREATE INDEX idx_client_rates_lookup
ON client_rates
(
    client_id,
    valid_from,
    valid_to,
    distance_from_km,
    distance_to_km,
    weight_from_tons,
    weight_to_tons
);



-- Truck refuelings

CREATE INDEX idx_refuelings_truck_date
ON truck_refuelings
(
    truck_id,
    refuel_date
);



-- Fuel batches

CREATE INDEX idx_fuel_batches_purchase_date
ON fuel_batches(purchase_date);



-- Truck downtime

CREATE INDEX idx_downtime_truck
ON truck_downtime(truck_id);



-- Trip metrics

CREATE INDEX idx_trip_metrics_recorded_at
ON trip_metrics(recorded_at);