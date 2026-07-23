"""
test_fuel_cost_allocation.py

Unit tests for allocate_fifo_fuel_cost(). Run with:

    pytest python/test_fuel_cost_allocation.py -v

These tests use small, hand-verifiable inputs -- the goal is to
prove the FIFO algorithm itself is correct before trusting it on
the full ~4,800-row trip dataset, where manual verification isn't
feasible.
"""

import pandas as pd
import pytest

from fuel_cost_allocation import allocate_fifo_fuel_cost


def test_single_batch_simple_consumption():
    """A trip that fits entirely within one batch should be priced
    at that batch's price, with no split."""
    trips = pd.DataFrame({
        "trip_id": [1],
        "date_departure": ["2022-07-01"],
        "estimated_fuel_liters": [100.0],
    })
    batches = pd.DataFrame({
        "batch_id": ["B1"],
        "purchase_date": ["2022-06-30"],
        "liters_purchased": [500.0],
        "price_per_liter_uah": [50.0],
    })

    result = allocate_fifo_fuel_cost(trips, batches)
    row = result.iloc[0]

    assert row["fuel_cost_uah"] == pytest.approx(100 * 50.0)
    assert row["fuel_liters_allocated"] == pytest.approx(100.0)
    assert row["batches_used"] == "B1"


def test_batch_boundary_split():
    """A trip that straddles two batches should be priced using
    both prices, proportionally to liters drawn from each."""
    trips = pd.DataFrame({
        "trip_id": [1, 2],
        "date_departure": ["2022-07-01", "2022-07-02"],
        "estimated_fuel_liters": [80.0, 50.0],
    })
    batches = pd.DataFrame({
        "batch_id": ["B1", "B2"],
        "purchase_date": ["2022-06-30", "2022-07-01"],
        "liters_purchased": [100.0, 500.0],
        "price_per_liter_uah": [50.0, 55.0],
    })

    result = allocate_fifo_fuel_cost(trips, batches).set_index("trip_id")

    # Trip 1: 80 L, fully from B1 (100 L available) -> 80 * 50
    assert result.loc[1, "fuel_cost_uah"] == pytest.approx(80 * 50.0)
    assert result.loc[1, "batches_used"] == "B1"

    # Trip 2: 50 L needed, only 20 L left in B1, rest (30 L) from B2
    expected_cost = 20 * 50.0 + 30 * 55.0
    assert result.loc[2, "fuel_cost_uah"] == pytest.approx(expected_cost)
    assert result.loc[2, "fuel_liters_allocated"] == pytest.approx(50.0)
    assert result.loc[2, "batches_used"] == "B1,B2"


def test_trips_processed_in_chronological_order_not_input_order():
    """Trips must be consumed in date_departure order, regardless
    of the order they appear in the input DataFrame."""
    trips = pd.DataFrame({
        "trip_id": [2, 1],  # deliberately out of chronological order
        "date_departure": ["2022-07-02", "2022-07-01"],
        "estimated_fuel_liters": [50.0, 80.0],
    })
    batches = pd.DataFrame({
        "batch_id": ["B1", "B2"],
        "purchase_date": ["2022-06-30", "2022-07-01"],
        "liters_purchased": [100.0, 500.0],
        "price_per_liter_uah": [50.0, 55.0],
    })

    result = allocate_fifo_fuel_cost(trips, batches).set_index("trip_id")

    # Same expected outcome as test_batch_boundary_split, proving
    # date order -- not row order -- drives the allocation.
    assert result.loc[1, "fuel_cost_uah"] == pytest.approx(80 * 50.0)
    assert result.loc[2, "fuel_cost_uah"] == pytest.approx(20 * 50.0 + 30 * 55.0)


def test_null_and_zero_liters_pass_through_as_null_cost():
    """Cancelled trips (or trailing trips with no closing refuel)
    have null/zero estimated_fuel_liters and should get a null
    fuel_cost_uah, not an error or a zero cost."""
    trips = pd.DataFrame({
        "trip_id": [1, 2],
        "date_departure": ["2022-07-01", "2022-07-02"],
        "estimated_fuel_liters": [None, 0.0],
    })
    batches = pd.DataFrame({
        "batch_id": ["B1"],
        "purchase_date": ["2022-06-30"],
        "liters_purchased": [500.0],
        "price_per_liter_uah": [50.0],
    })

    result = allocate_fifo_fuel_cost(trips, batches).set_index("trip_id")

    assert pd.isna(result.loc[1, "fuel_cost_uah"])
    assert pd.isna(result.loc[2, "fuel_cost_uah"])


def test_queue_exhausted_raises_value_error():
    """If total demand exceeds total purchased fuel, the function
    should fail loudly rather than guess a price."""
    trips = pd.DataFrame({
        "trip_id": [1],
        "date_departure": ["2022-07-01"],
        "estimated_fuel_liters": [1000.0],
    })
    batches = pd.DataFrame({
        "batch_id": ["B1"],
        "purchase_date": ["2022-06-30"],
        "liters_purchased": [100.0],
        "price_per_liter_uah": [50.0],
    })

    with pytest.raises(ValueError, match="queue exhausted"):
        allocate_fifo_fuel_cost(trips, batches)


def test_multiple_batches_fully_consumed_in_sequence():
    """Several small trips draining exactly through 3 batches in
    order -- checks the queue advances correctly batch by batch."""
    trips = pd.DataFrame({
        "trip_id": [1, 2, 3],
        "date_departure": ["2022-07-01", "2022-07-02", "2022-07-03"],
        "estimated_fuel_liters": [100.0, 100.0, 100.0],
    })
    batches = pd.DataFrame({
        "batch_id": ["B1", "B2", "B3"],
        "purchase_date": ["2022-06-29", "2022-06-30", "2022-07-01"],
        "liters_purchased": [100.0, 100.0, 100.0],
        "price_per_liter_uah": [50.0, 55.0, 60.0],
    })

    result = allocate_fifo_fuel_cost(trips, batches).set_index("trip_id")

    assert result.loc[1, "fuel_cost_uah"] == pytest.approx(100 * 50.0)
    assert result.loc[1, "batches_used"] == "B1"
    assert result.loc[2, "fuel_cost_uah"] == pytest.approx(100 * 55.0)
    assert result.loc[2, "batches_used"] == "B2"
    assert result.loc[3, "fuel_cost_uah"] == pytest.approx(100 * 60.0)
    assert result.loc[3, "batches_used"] == "B3"