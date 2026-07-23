"""
fuel_cost_allocation.py

Pure business logic: FIFO (First-In, First-Out) allocation of
company-wide diesel purchase costs to individual trips.

Contains only allocate_fifo_fuel_cost(). No file I/O, no database
connections -- callers (notebooks) are responsible for loading
input DataFrames and persisting the result.
"""

import pandas as pd


def allocate_fifo_fuel_cost(
    trips_df: pd.DataFrame,
    fuel_batches_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Allocate fuel cost to each trip using FIFO consumption against
    a single, company-wide diesel purchase queue.

    The fleet draws from one shared pool of purchased fuel (all 12
    trucks are refueled from the same supplier deliveries recorded
    in fuel_batches). Consumption is therefore modeled as one
    chronological stream across all trucks combined: trips are
    processed in order of date_departure, and each trip's estimated
    fuel volume is drawn from the oldest available purchase batch
    first. If a batch runs out mid-trip, the remaining volume is
    drawn from the next batch and the trip's cost is split
    accordingly across both batches' prices.

    Parameters
    ----------
    trips_df : pd.DataFrame
        Must contain columns: trip_id, date_departure,
        estimated_fuel_liters. Rows with a null or zero
        estimated_fuel_liters are passed through with a null
        fuel_cost_uah (e.g. cancelled trips, or trailing trips not
        yet closed out by a subsequent refuel).
    fuel_batches_df : pd.DataFrame
        Must contain columns: batch_id, purchase_date,
        liters_purchased, price_per_liter_uah.

    Returns
    -------
    pd.DataFrame
        Columns: trip_id, fuel_cost_uah, fuel_liters_allocated,
        batches_used. fuel_liters_allocated should match
        estimated_fuel_liters for every trip that was fully
        allocated -- useful as a QA check downstream.
        batches_used is a comma-separated list of batch_id values
        the trip drew from (mostly 1, occasionally 2+ when a trip
        straddles a batch boundary).
    """
    # Chronological order across the whole fleet -- this is what
    # makes the allocation genuinely FIFO at the company level,
    # not per truck. trip_id is a stable tie-breaker for trips
    # sharing the same date_departure.
    trips_sorted = trips_df.sort_values(
        ["date_departure", "trip_id"]
    ).reset_index(drop=True)

    # FIFO queue of purchase batches, oldest first. Each entry
    # tracks how many liters remain unconsumed from that batch.
    batches_sorted = fuel_batches_df.sort_values("purchase_date").reset_index(drop=True)
    queue = [
        {
            "batch_id": row.batch_id,
            "remaining_liters": float(row.liters_purchased),
            "price_per_liter_uah": float(row.price_per_liter_uah),
        }
        for row in batches_sorted.itertuples(index=False)
    ]
    queue_position = 0  # index of the current (oldest, not-yet-exhausted) batch

    results = []

    for trip in trips_sorted.itertuples(index=False):
        liters_needed = trip.estimated_fuel_liters

        if pd.isna(liters_needed) or liters_needed <= 0:
            results.append(
                {
                    "trip_id": trip.trip_id,
                    "fuel_cost_uah": None,
                    "fuel_liters_allocated": None,
                    "batches_used": None,
                }
            )
            continue

        remaining = float(liters_needed)
        cost = 0.0
        batches_used = []

        while remaining > 0:
            if queue_position >= len(queue):
                # Ran out of purchased fuel to allocate against --
                # a data inconsistency (more fuel consumed than
                # ever purchased). Surface it loudly rather than
                # silently guessing a price.
                raise ValueError(
                    f"trip_id={trip.trip_id}: fuel_batches queue exhausted "
                    f"with {remaining:.2f} L still unallocated. "
                    "Check that total liters_purchased covers total "
                    "estimated_fuel_liters across the dataset."
                )

            batch = queue[queue_position]
            take = min(remaining, batch["remaining_liters"])

            cost += take * batch["price_per_liter_uah"]
            batch["remaining_liters"] -= take
            remaining -= take
            batches_used.append(batch["batch_id"])

            if batch["remaining_liters"] <= 0:
                queue_position += 1

        results.append(
            {
                "trip_id": trip.trip_id,
                "fuel_cost_uah": round(cost, 2),
                "fuel_liters_allocated": round(float(liters_needed), 2),
                "batches_used": ",".join(str(b) for b in dict.fromkeys(batches_used)),
            }
        )

    return pd.DataFrame(results)