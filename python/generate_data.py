from __future__ import annotations

import csv
import math
import random
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path

random.seed(42)

OUT_DIR = Path("data/raw")
START_DATE = date(2022, 7, 1)
END_DATE = date(2024, 10, 31)
DIESEL_KG_PER_LITER = 0.84

# 2-3 rare disruption events across the whole dataset: storm/port closure,
# a checkpoint delay, a road-repair closure. Trips caught in these windows
# get forced long delays (40-60h), a few even cancelled outright.
ANOMALIES = [
    {"start": date(2022, 11, 10), "end": date(2022, 11, 13), "label": "storm_port_closure", "scope": "port"},
    {"start": date(2023, 8, 21), "end": date(2023, 8, 24), "label": "checkpoint", "scope": "any"},
    {"start": date(2024, 3, 6), "end": date(2024, 3, 9), "label": "road_repair", "scope": "any"},
]

def anomaly_for(trip_day: date, route: dict) -> dict | None:
    for a in ANOMALIES:
        if a["start"] <= trip_day <= a["end"]:
            if a["scope"] == "port" and not route["has_port"]:
                continue
            return a
    return None

# Driving style shows up only as a hidden fuel-consumption multiplier, never
# as a stored column - it's meant to be *inferred* from the data, not read
# off a label. Values below 1.0 are economical drivers, above 1.0 aggressive.
DRIVER_FUEL_EFFICIENCY = {
    "DRV-01": 0.93,
    "DRV-02": 0.97,
    "DRV-03": 1.00,
    "DRV-04": 1.03,
    "DRV-05": 0.95,
    "DRV-06": 1.05,
    "DRV-07": 0.98,
    "DRV-08": 1.06,
    "DRV-09": 1.07,
    "DRV-10": 0.94,
    "DRV-11": 1.02,
    "DRV-12": 0.99,
}

# The two newest trucks join the active fleet gradually during H2 2022,
# reflecting a company that wasn't running at full fleet capacity yet.
TRUCK_ACTIVE_FROM = {
    "TRK-11": date(2022, 9, 1),
    "TRK-12": date(2022, 11, 1),
}

def daterange(start: date, end: date):
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)

def dstr(value: date | None) -> str:
    return "" if value is None else value.isoformat()

def month_start(value: date) -> date:
    return date(value.year, value.month, 1)

def add_months(value: date, months: int) -> date:
    y = value.year + (value.month - 1 + months) // 12
    m = (value.month - 1 + months) % 12 + 1
    return date(y, m, 1)

def days_in_month(value: date) -> int:
    return (add_months(month_start(value), 1) - month_start(value)).days

def season_for_day(value: date) -> str:
    if value.month in (7, 8, 9):
        return "harvest"
    if value.month in (10, 11):
        return "sunflower_peak"
    if value.month in (12, 1, 2):
        return "winter_slow"
    return "normal"

def weighted_choice(items: list[tuple]) -> str:
    total = sum(item[-1] for item in items)
    pick = random.uniform(0, total)
    upto = 0.0
    for item in items:
        weight = item[-1]
        upto += weight
        if upto >= pick:
            return item[0]
    return items[-1][0]

def write_csv(name: str, rows: list[dict], columns: list[str]) -> None:
    OUT_DIR.mkdir(exist_ok=True)
    with (OUT_DIR / name).open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

TRUCK_COLUMNS = [
    "truck_id",
    "brand",
    "model",
    "year_manufactured",
    "capacity_tons",
    "engine_volume",
    "mileage_start_km",
    "tank_capacity_liters",
]

DRIVER_COLUMNS = [
    "driver_id",
    "full_name",
    "driver_commission_rate",
    "hire_date",
    "trips_per_month_avg",
    "preferred_route_type",
]

CLIENT_COLUMNS = [
    "client_id",
    "company_name",
    "region",
    "primary_cargo",
    "payment_terms_days",
    "is_seasonal",
    "active_from",
    "active_to",
]

ROUTE_COLUMNS = [
    "route_id",
    "client_id",
    "origin_city",
    "destination_city",
    "distance_km",
    "route_type",
    "typical_cargo",
    "has_port",
]

RATE_COLUMNS = [
    "rate_id",
    "client_id",
    "distance_from_km",
    "distance_to_km",
    "weight_from_tons",
    "weight_to_tons",
    "rate_uah_per_ton_km",
    "valid_from",
    "valid_to",
]

DOWNTIME_COLUMNS = [
    "downtime_id",
    "truck_id",
    "date_from",
    "date_to",
    "reason",
]

TRIP_COLUMNS = [
    "trip_id",
    "date_departure",
    "date_arrival",
    "truck_id",
    "driver_id",
    "client_id",
    "route_id",
    "origin_city",
    "destination_city",
    "distance_km",
    "route_type",
    "cargo_type",
    "cargo_tons_actual",
    "load_factor_pct",
    "delay_hours",
    "status",
]

FUEL_BATCH_COLUMNS = [
    "batch_id",
    "purchase_date",
    "supplier",
    "liters_purchased",
    "price_per_liter_uah",
    "total_cost_uah",
]

TRIP_METRICS_COLUMNS = [
    "trip_id",
    "odometer_after_trip",
    "recorded_at",
]

REFUELING_COLUMNS = [
    "refuel_id",
    "truck_id",
    "refuel_date",
    "odometer_at_refuel",
    "liters_refueled",
]

def make_trucks() -> list[dict]:
    # tank_capacity_liters reflects realistic single-tank setups for EU long-haul
    # trucks of this class (600-800L), scaled loosely with size/generation.
    specs = [
        ("TRK-01", "DAF", "XF 105", 2015, 22.0, 12.9, 392_400, 660),
        ("TRK-02", "DAF", "XF 106", 2016, 23.0, 12.9, 365_800, 660),
        ("TRK-03", "DAF", "CF 85", 2017, 21.5, 12.9, 338_600, 600),
        ("TRK-04", "Volvo", "FH 460", 2018, 24.0, 12.8, 304_900, 700),
        ("TRK-05", "Scania", "R450", 2018, 24.5, 12.7, 287_200, 700),
        ("TRK-06", "MAN", "TGX 18.440", 2019, 23.5, 12.4, 261_500, 730),
        ("TRK-07", "Mercedes", "Actros 1845", 2019, 24.0, 12.8, 249_300, 730),
        ("TRK-08", "DAF", "XF 480", 2020, 25.0, 12.9, 221_700, 760),
        ("TRK-09", "Volvo", "FH 500", 2020, 25.0, 12.8, 204_600, 780),
        ("TRK-10", "Scania", "G450", 2021, 24.0, 12.7, 176_300, 700),
        ("TRK-11", "MAN", "TGX 18.480", 2021, 24.5, 12.4, 164_800, 730),
        ("TRK-12", "Mercedes", "Actros 1848", 2021, 25.0, 12.8, 153_900, 730),
    ]
    return [
        {
            "truck_id": truck_id,
            "brand": brand,
            "model": model,
            "year_manufactured": year,
            "capacity_tons": f"{capacity:.1f}",
            "engine_volume": f"{engine:.1f}",
            "mileage_start_km": mileage,
            "tank_capacity_liters": tank,
        }
        for truck_id, brand, model, year, capacity, engine, mileage, tank in specs
    ]

def make_drivers() -> list[dict]:
    # driver_commission_rate is a revenue-share commission (common pay model
    # in UA freight), not a fixed salary - rescaled from an early draft's
    # thin ~10-12% to a realistic ~27-34% once fuel/overhead have to come
    # out of the same rate.
    data = [
        ("DRV-01", "Олександр Ковальчук", 0.120, "2019-03-18", 9, "local"),
        ("DRV-02", "Віталій Бондаренко", 0.122, "2020-06-02", 10, "highway"),
        ("DRV-03", "Сергій Мельник", 0.123, "2018-11-14", 12, "local"),
        ("DRV-04", "Андрій Савченко", 0.126, "2021-01-22", 18, "highway"),
        ("DRV-05", "Ігор Шевченко", 0.128, "2017-07-09", 20, "local"),
        ("DRV-06", "Микола Ткаченко", 0.124, "2020-09-30", 15, "highway"),
        ("DRV-07", "Петро Романюк", 0.125, "2019-12-11", 14, "local"),
        ("DRV-08", "Юрій Дорошенко", 0.129, "2021-05-16", 19, "highway"),
        ("DRV-09", "Василь Кравець", 0.127, "2022-02-07", 18, "local"),
        ("DRV-10", "Дмитро Лисенко", 0.121, "2021-08-25", 8, "highway"),
        ("DRV-11", "Тарас Гончар", 0.130, "2022-04-19", 20, "local"),
        ("DRV-12", "Роман Мороз", 0.126, "2020-02-03", 13, "highway"),
    ]
    return [
        {
            "driver_id": driver_id,
            "full_name": name,
            "driver_commission_rate": f"{pct:.3f}",
            "hire_date": hire_date,
            "trips_per_month_avg": avg,
            "preferred_route_type": route_type,
        }
        for driver_id, name, pct, hire_date, avg, route_type in data
    ]

def make_clients() -> list[dict]:
    data = [
        ("CLT-01", "ТОВ Соняшник-Агро", "Кіровоградська", "sunflower", 45, 0, "2022-07-01", ""),
        ("CLT-02", "ПП ДніпроЗерно", "Дніпропетровська", "wheat;sunflower;corn", 30, 0, "2022-07-01", ""),
        ("CLT-03", "ТОВ Полтавські Лани", "Полтавська", "wheat;sunflower;corn", 45, 0, "2022-07-01", ""),
        ("CLT-04", "ФГ Кукурудза Південь", "Миколаївська", "sunflower;corn", 60, 0, "2022-07-01", ""),
        ("CLT-05", "ТОВ Соєвий Дім", "Черкаська", "soy", 30, 0, "2022-07-01", ""),
        ("CLT-06", "АгроЛогістика Центр", "Вінницька", "mixed grains", 45, 0, "2022-07-01", ""),
        ("CLT-07", "ФГ Жнива-Поділля", "Вінницька", "wheat", 30, 1, "2022-07-01", "2024-09-30"),
        ("CLT-08", "ТОВ Пшеничний Шлях", "Чернігівська", "wheat", 45, 1, "2022-07-01", "2024-09-30"),
        ("CLT-09", "ФГ Золоте Колосся", "Хмельницька", "wheat", 30, 1, "2022-07-01", "2024-09-30"),
        ("CLT-10", "ПП Липневий Урожай", "Сумська", "wheat", 60, 1, "2022-07-01", "2024-09-30"),
        ("CLT-11", "ТОВ Нива Експорт", "Одеська", "wheat", 45, 1, "2022-07-01", "2024-09-30"),
    ]
    return [
        {
            "client_id": client_id,
            "company_name": name,
            "region": region,
            "primary_cargo": cargo,
            "payment_terms_days": terms,
            "is_seasonal": seasonal,
            "active_from": active_from,
            "active_to": active_to,
        }
        for client_id, name, region, cargo, terms, seasonal, active_from, active_to in data
    ]

def make_routes() -> list[dict]:
    data = [
        ("RTE-01", "CLT-01", "Кропивницький", "Дніпро", 246, "highway", "sunflower", 0),
        ("RTE-02", "CLT-02", "Дніпро", "Одеса", 472, "highway", "corn", 1),
        ("RTE-03", "CLT-03", "Полтава", "Чорноморськ", 612, "highway", "wheat", 1),
        ("RTE-04", "CLT-04", "Миколаїв", "Одеса", 132, "local", "sunflower", 1),
        ("RTE-05", "CLT-05", "Черкаси", "Кременчук", 118, "local", "soy", 0),
        ("RTE-06", "CLT-06", "Вінниця", "Київ", 267, "highway", "mixed grains", 0),
        ("RTE-07", "CLT-07", "Вінниця", "Жмеринка", 52, "local", "wheat", 0),
        ("RTE-08", "CLT-08", "Чернігів", "Київ", 149, "local", "wheat", 0),
        ("RTE-09", "CLT-09", "Хмельницький", "Тернопіль", 112, "local", "wheat", 0),
        ("RTE-10", "CLT-11", "Подільськ", "Чорноморськ", 214, "highway", "wheat", 1),
    ]
    return [
        {
            "route_id": route_id,
            "client_id": client_id,
            "origin_city": origin,
            "destination_city": destination,
            "distance_km": distance,
            "route_type": route_type,
            "typical_cargo": cargo,
            "has_port": port,
        }
        for route_id, client_id, origin, destination, distance, route_type, cargo, port in data
    ]

def make_downtime(trucks: list[dict]) -> list[dict]:
    rows = []
    occupied_by_truck: dict[str, list[tuple[date, date]]] = defaultdict(list)
    total_days = (END_DATE - START_DATE).days + 1

    for truck in trucks:
        truck_id = truck["truck_id"]
        year = int(truck["year_manufactured"])
        if year <= 2016:
            target_days = random.randint(math.floor(total_days * 0.125), math.floor(total_days * 0.150))
            event_count = 4
        elif year == 2017:
            target_days = random.randint(math.floor(total_days * 0.110), math.floor(total_days * 0.135))
            event_count = 4
        elif year <= 2019:
            target_days = random.randint(math.floor(total_days * 0.090), math.floor(total_days * 0.115))
            event_count = 3
        else:
            target_days = random.randint(math.floor(total_days * 0.080), math.floor(total_days * 0.095))
            event_count = 2

        lengths = []
        remaining = target_days
        for i in range(event_count):
            if i == event_count - 1:
                length = remaining
            else:
                max_len = remaining - (event_count - i - 1) * 12
                length = random.randint(18, max(19, min(45, max_len)))
                remaining -= length
            lengths.append(length)

        for length in lengths:
            for _ in range(500):
                start_offset = random.randint(0, total_days - length)
                start = START_DATE + timedelta(days=start_offset)
                end = start + timedelta(days=length - 1)
                if start.month in (7, 8, 9, 10):
                    continue
                if any(not (end < s or start > e) for s, e in occupied_by_truck[truck_id]):
                    continue
                occupied_by_truck[truck_id].append((start, end))
                rows.append(
                    {
                        "downtime_id": f"DT-{len(rows) + 1:03d}",
                        "truck_id": truck_id,
                        "date_from": dstr(start),
                        "date_to": dstr(end),
                        "reason": "breakdown" if random.random() < (0.72 if year <= 2017 else 0.48) else "scheduled_maintenance",
                    }
                )
                break

    rows.sort(key=lambda r: (r["truck_id"], r["date_from"]))
    for i, row in enumerate(rows, 1):
        row["downtime_id"] = f"DT-{i:03d}"
    return rows

def rate_periods() -> list[tuple[date, date, float, str]]:
    return [
        (date(2022, 7, 1), date(2022, 9, 30), 1.18, "harvest"),
        (date(2022, 10, 1), date(2022, 12, 31), 1.00, "base"),
        (date(2023, 1, 1), date(2023, 6, 30), 1.12, "base"),
        (date(2023, 7, 1), date(2023, 9, 30), 1.34, "harvest"),
        (date(2023, 10, 1), date(2023, 12, 31), 1.15, "base"),
        (date(2024, 1, 1), date(2024, 6, 30), 1.19, "base"),
        (date(2024, 7, 1), date(2024, 9, 30), 1.33, "harvest"),
        (date(2024, 10, 1), date(2024, 10, 31), 1.20, "base"),
    ]

def make_client_rates(clients: list[dict]) -> list[dict]:
    client_multiplier = {
        "CLT-01": 1.14,
        "CLT-02": 1.00,
        "CLT-03": 0.98,
        "CLT-04": 0.87,
        "CLT-05": 1.18,
        "CLT-06": 1.10,
        "CLT-07": 0.78,
        "CLT-08": 0.80,
        "CLT-09": 0.79,
        "CLT-10": 0.77,
        "CLT-11": 0.82,
    }
    bands = [
        (0, 150, 15, 18, 2.16),
        (0, 150, 18, 22, 2.03),
        (0, 150, 22, 30, 1.95),

        (150, 300, 15, 18, 1.94),
        (150, 300, 18, 22, 1.82),
        (150, 300, 22, 30, 1.74),

        (300, 500, 15, 18, 1.76),
        (300, 500, 18, 22, 1.68),
        (300, 500, 22, 30, 1.60),

        (500, 9999, 15, 18, 1.67),
        (500, 9999, 18, 22, 1.58),
        (500, 9999, 22, 30, 1.50),
    ]
    rows = []
    for client in clients:
        client_id = client["client_id"]
        chosen_bands = bands[:5] if client_id in {"CLT-05", "CLT-07", "CLT-08", "CLT-09", "CLT-10"} else bands
        for start, end, period_multiplier, period_type in rate_periods():
            if client["is_seasonal"] == 1 and period_type != "harvest":
                continue
            for dist_from, dist_to, weight_from, weight_to, base_rate in chosen_bands:
                variance = random.uniform(0.95, 1.05)
                rate = base_rate * client_multiplier[client_id] * period_multiplier * variance
                rows.append(
                    {
                        "rate_id": f"RAT-{len(rows) + 1:04d}",
                        "client_id": client_id,
                        "distance_from_km": dist_from,
                        "distance_to_km": dist_to,
                        "weight_from_tons": weight_from,
                        "weight_to_tons": weight_to,
                        "rate_uah_per_ton_km": f"{rate:.3f}",
                        "valid_from": dstr(start),
                        "valid_to": dstr(end),
                    }
                )
    return rows

def allowed_cargo(client_id: str, trip_date: date) -> list[str]:
    season = season_for_day(trip_date)
    if client_id == "CLT-01":
        return ["sunflower"]
    if client_id in {"CLT-02", "CLT-03"}:
        return ["wheat", "sunflower", "corn"] if season == "harvest" else ["sunflower", "corn"]
    if client_id == "CLT-04":
        return ["sunflower", "corn"] if season != "harvest" else []
    if client_id == "CLT-05":
        return ["soy"]
    if client_id == "CLT-06":
        return ["wheat", "sunflower", "corn", "soy"] if season == "harvest" else ["sunflower", "corn", "soy"]
    return ["wheat"] if season == "harvest" else []

def target_trips_for_month(value: date) -> int:
    season = season_for_day(value)
    if value.year == 2022:
        base = {"harvest": 255, "sunflower_peak": 235, "winter_slow": 62, "normal": 150}[season]
    elif value.year == 2023:
        base = {"harvest": 285, "sunflower_peak": 240, "winter_slow": 58, "normal": 175}[season]
    else:
        base = {"harvest": 220, "sunflower_peak": 165, "winter_slow": 47, "normal": 135}[season]
    return max(25, int(random.gauss(base, base * 0.045)))

def build_downtime_calendar(downtime: list[dict]) -> dict[str, set[date]]:
    calendar: dict[str, set[date]] = defaultdict(set)
    for row in downtime:
        start = datetime.strptime(row["date_from"], "%Y-%m-%d").date()
        end = datetime.strptime(row["date_to"], "%Y-%m-%d").date()
        for day in daterange(start, end):
            calendar[row["truck_id"]].add(day)
    return calendar

def make_trips(
    trucks: list[dict],
    drivers: list[dict],
    clients: list[dict],
    routes: list[dict],
    downtime: list[dict],
) -> list[dict]:
    downtime_days = build_downtime_calendar(downtime)
    trucks_by_id = {t["truck_id"]: t for t in trucks}
    drivers_by_id = {d["driver_id"]: d for d in drivers}
    clients_by_id = {c["client_id"]: c for c in clients}
    routes_by_month: dict[date, list[dict]] = defaultdict(list)
    all_routes = {r["route_id"]: r for r in routes}
    last_trip_day_by_truck: dict[str, date] = {}
    rows = []

    route_weights_by_season = {
        "harvest": [
            ("RTE-07", 16),
            ("RTE-08", 15),
            ("RTE-09", 15),
            ("RTE-10", 12),
            ("RTE-02", 10),
            ("RTE-03", 9),
            ("RTE-06", 9),
            ("RTE-01", 8),
            ("RTE-05", 4),
            ("RTE-04", 2),
        ],
        "sunflower_peak": [
            ("RTE-01", 24),
            ("RTE-04", 18),
            ("RTE-02", 16),
            ("RTE-03", 12),
            ("RTE-06", 15),
            ("RTE-05", 8),
        ],
        "winter_slow": [
            ("RTE-01", 18),
            ("RTE-02", 14),
            ("RTE-04", 18),
            ("RTE-05", 16),
            ("RTE-06", 18),
        ],
        "normal": [
            ("RTE-01", 18),
            ("RTE-02", 15),
            ("RTE-03", 12),
            ("RTE-04", 13),
            ("RTE-05", 12),
            ("RTE-06", 15),
        ],
    }

    driver_trip_bias = {
        d["driver_id"]: 0.45 + float(d["trips_per_month_avg"]) / 20 for d in drivers
    }

    months = []
    current = START_DATE
    while current <= END_DATE:
        months.append(month_start(current))
        current = add_months(current, 1)

    for m in months:
        target = target_trips_for_month(m)
        if m == date(2024, 10, 1):
            target = 128
        month_days = [m + timedelta(days=i) for i in range(days_in_month(m)) if START_DATE <= m + timedelta(days=i) <= END_DATE]
        attempts = 0
        while len(routes_by_month[m]) < target and attempts < target * 30:
            attempts += 1
            trip_day = random.choice(month_days)
            season = season_for_day(trip_day)
            route_id = weighted_choice(route_weights_by_season[season])
            route = all_routes[route_id]
            cargo_options = allowed_cargo(route["client_id"], trip_day)
            if not cargo_options:
                continue

            candidates = []
            for truck in trucks:
                truck_id = truck["truck_id"]
                active_from = TRUCK_ACTIVE_FROM.get(truck_id)
                if active_from and trip_day < active_from:
                    continue
                driver_id = f"DRV-{int(truck_id.split('-')[1]):02d}"
                driver = drivers_by_id[driver_id]
                if trip_day in downtime_days[truck_id]:
                    continue
                if last_trip_day_by_truck.get(truck_id) == trip_day and route["route_type"] == "highway":
                    continue
                if route["route_type"] == "highway" and driver["preferred_route_type"] == "local":
                    preference = 0.82
                elif route["route_type"] == "local" and driver["preferred_route_type"] == "highway":
                    preference = 0.80
                else:
                    preference = 1.10
                if season == "winter_slow" and random.random() < 0.12:
                    preference *= 0.75
                candidates.append((truck_id, driver_id, driver_trip_bias[driver_id] * preference))

            if not candidates:
                continue
            truck_id = weighted_choice(candidates)
            driver_id = f"DRV-{int(truck_id.split('-')[1]):02d}"
            if random.random() < 0.065:
                driver_id = random.choice([d["driver_id"] for d in drivers])

            truck = trucks_by_id[truck_id]
            capacity = float(truck["capacity_tons"])
            client = clients_by_id[route["client_id"]]
            if route["route_type"] == "local":
                ceiling_pct = random.uniform(105.0, 118.0)
            else:
                ceiling_pct = random.uniform(96.0, 102.0)

            # Seasonal harvest clients run a lot of short, thin-margin trips:
            # more likely to go out partially loaded than core clients.
            underload_chance = 0.38 if (season == "harvest" and client["is_seasonal"] == 1) else 0.20
            if random.random() < underload_chance:
                target_pct = random.uniform(68.0, 87.0)
            else:
                target_pct = random.uniform(87.0, ceiling_pct)

            load = max(15.0, capacity * target_pct / 100)
            load_factor = load / capacity * 100

            base_delay_prob = random.uniform(0.15, 0.20) if route["has_port"] else random.uniform(0.05, 0.08)
            delay_multiplier = 1.38 if trip_day.year == 2024 and route["has_port"] else 1.0
            delayed = random.random() < min(0.42, base_delay_prob * delay_multiplier)
            cancelled = random.random() < (0.011 if season != "harvest" else 0.006)
            anomaly = anomaly_for(trip_day, route)
            if anomaly:
                # A storm/checkpoint/road closure overrides the normal delay
                # model: most caught trips get hit with a long delay, a small
                # share get cancelled outright.
                if random.random() < 0.15:
                    delay_hours = round(random.uniform(0.0, 2.0), 1)
                    status = "cancelled"
                else:
                    delay_hours = round(random.uniform(40.0, 60.0), 1)
                    status = "delayed"
            elif cancelled:
                delay_hours = round(random.uniform(0.0, 2.0), 1)
                status = "cancelled"
            elif delayed:
                if route["has_port"]:
                    base_hours = random.uniform(8.0, 28.0)
                    if trip_day.year == 2024:
                        base_hours *= random.uniform(1.30, 1.42)
                    delay_hours = round(base_hours, 1)
                else:
                    delay_hours = round(random.uniform(2.0, 9.0), 1)
                status = "delayed"
            else:
                delay_hours = round(random.uniform(0.0, 1.8), 1)
                status = "completed"

            travel_days = 0 if route["distance_km"] < 180 and delay_hours < 8 else 1
            if route["distance_km"] > 500 or delay_hours > 24:
                travel_days += 1

            row = {
                "trip_id": f"TRP-{len(rows) + 1:05d}",
                "date_departure": dstr(trip_day),
                "date_arrival": dstr(min(trip_day + timedelta(days=travel_days), END_DATE)),
                "truck_id": truck_id,
                "driver_id": driver_id,
                "client_id": route["client_id"],
                "route_id": route_id,
                "origin_city": route["origin_city"],
                "destination_city": route["destination_city"],
                "distance_km": route["distance_km"],
                "route_type": route["route_type"],
                "cargo_type": random.choice(cargo_options),
                "cargo_tons_actual": f"{load:.2f}",
                "load_factor_pct": f"{load_factor:.1f}",
                "delay_hours": f"{delay_hours:.1f}",
                "status": status,
            }
            rows.append(row)
            routes_by_month[m].append(row)
            last_trip_day_by_truck[truck_id] = trip_day

    rows.sort(key=lambda r: (r["date_departure"], r["truck_id"], r["trip_id"]))
    for i, row in enumerate(rows, 1):
        row["trip_id"] = f"TRP-{i:05d}"
    return rows

def make_fuel_batches() -> list[dict]:
    # Same wholesale price schedule/style as the previous fuel_contracts logic
    # (real 2022-2024 UAH diesel wholesale price movement), but volumes are
    # bumped up and no longer track per-batch consumption caps: FIFO
    # allocation across batches is left entirely to SQL, not to generation.
    starts_and_prices = [
        ("2022-07-01", 54.20),
        ("2022-08-18", 52.70),
        ("2022-10-07", 48.60),
        ("2022-12-05", 46.40),
        ("2023-02-03", 47.10),
        ("2023-04-06", 48.20),
        ("2023-06-08", 49.60),
        ("2023-07-21", 50.40),
        ("2023-09-08", 51.90),
        ("2023-11-10", 52.80),
        ("2024-01-09", 53.90),
        ("2024-03-12", 55.70),
        ("2024-05-10", 58.40),
        ("2024-06-21", 60.80),
        ("2024-08-12", 59.30),
        ("2024-09-24", 57.20),
    ]
    rows = []
    for i, (start_s, price) in enumerate(starts_and_prices, 1):
        purchase_date = datetime.strptime(start_s, "%Y-%m-%d").date()
        tons = random.uniform(21.0, 28.0)
        if purchase_date in {date(2023, 6, 8), date(2024, 5, 10), date(2024, 9, 24)}:
            tons = random.uniform(27.0, 30.0)
        liters = int(round(tons * 1000 / DIESEL_KG_PER_LITER))
        rows.append(
            {
                "batch_id": f"FB-{i:03d}",
                "purchase_date": dstr(purchase_date),
                "supplier": "ОККО Пальне",
                "liters_purchased": liters,
                "price_per_liter_uah": f"{price:.2f}",
                "total_cost_uah": f"{liters * price:.2f}",
            }
        )
    return rows

def make_trip_metrics(trucks: list[dict], trips: list[dict]) -> list[dict]:
    odometer = {t["truck_id"]: int(t["mileage_start_km"]) for t in trucks}
    trips_by_truck: dict[str, list[dict]] = defaultdict(list)
    for trip in trips:
        if trip["status"] != "cancelled":
            trips_by_truck[trip["truck_id"]].append(trip)
    for truck_id in trips_by_truck:
        trips_by_truck[truck_id].sort(key=lambda r: (r["date_departure"], r["trip_id"]))

    rows = []
    for truck_id, truck_trips in trips_by_truck.items():
        for trip in truck_trips:
            distance = int(trip["distance_km"])
            odometer[truck_id] += distance
            arrival = datetime.strptime(trip["date_arrival"], "%Y-%m-%d").date()
            recorded_at = datetime.combine(arrival, datetime.min.time()) + timedelta(
                hours=random.uniform(6, 20)
            )
            rows.append(
                {
                    "trip_id": trip["trip_id"],
                    "odometer_after_trip": odometer[truck_id],
                    "recorded_at": recorded_at.strftime("%Y-%m-%d %H:%M"),
                }
            )

    rows.sort(key=lambda r: r["trip_id"])
    return rows

def make_refuelings(
    trucks: list[dict], trips: list[dict], trip_metrics: list[dict]
) -> tuple[list[dict], list[dict]]:
    trucks_by_id = {t["truck_id"]: t for t in trucks}
    odo_after_trip = {tm["trip_id"]: tm["odometer_after_trip"] for tm in trip_metrics}

    trips_by_truck: dict[str, list[dict]] = defaultdict(list)
    for trip in trips:
        if trip["status"] != "cancelled":
            trips_by_truck[trip["truck_id"]].append(trip)
    for truck_id in trips_by_truck:
        trips_by_truck[truck_id].sort(key=lambda r: (r["date_departure"], r["trip_id"]))

    rows = []
    validation_events = []
    for truck_id, truck_trips in trips_by_truck.items():
        truck = trucks_by_id[truck_id]
        capacity = float(truck["tank_capacity_liters"])
        fuel_level = capacity  # truck starts with a full tank
        prev_odo = int(truck["mileage_start_km"])

        for trip in truck_trips:
            distance = int(trip["distance_km"])
            cargo_tons = float(trip["cargo_tons_actual"])
            age = int(trip["date_departure"][:4]) - int(truck["year_manufactured"])
            route_factor = 1.06 if trip["route_type"] == "local" else 1.00
            load_factor = 0.96 + (cargo_tons / float(truck["capacity_tons"])) * 0.08
            age_factor = 1.00 + max(0, age - 5) * 0.012
            driver_factor = DRIVER_FUEL_EFFICIENCY.get(trip["driver_id"], 1.0)
            liters_needed = (
                distance
                * random.uniform(28.0, 33.0)
                / 100
                * route_factor
                * load_factor
                * age_factor
                * driver_factor
            )
            # Idling burns fuel while the truck waits (port queues, checkpoints,
            # storms, road closures) - a real mechanism tying delay_hours to cost.
            idle_liters_per_hour = random.uniform(1.8, 3.2)
            liters_needed += float(trip["delay_hours"]) * idle_liters_per_hour
            fuel_level = max(0.0, fuel_level - liters_needed)
            current_odo = odo_after_trip[trip["trip_id"]]

            threshold = capacity * random.uniform(0.15, 0.25)
            if fuel_level <= threshold:
                liters_refueled = capacity - fuel_level

                dep = datetime.strptime(trip["date_departure"], "%Y-%m-%d").date()
                arr = datetime.strptime(trip["date_arrival"], "%Y-%m-%d").date()
                span = (arr - dep).days
                refuel_date = dep if span <= 0 else dep + timedelta(days=random.randint(0, span))

                offset_km = random.randint(0, max(0, distance - 1)) if distance > 1 else 0
                refuel_odo = min(current_odo, prev_odo + offset_km)
                refuel_odo = max(refuel_odo, prev_odo)

                rows.append(
                    {
                        "refuel_id": f"RFL-{len(rows) + 1:05d}",
                        "truck_id": truck_id,
                        "refuel_date": dstr(refuel_date),
                        "odometer_at_refuel": refuel_odo,
                        "liters_refueled": f"{liters_refueled:.2f}",
                    }
                )
                validation_events.append(
                    {
                        "truck_id": truck_id,
                        "trigger_trip_id": trip["trip_id"],
                        "odometer_at_refuel": refuel_odo,
                    }
                )
                fuel_level = capacity

            prev_odo = current_odo

    rows.sort(key=lambda r: (r["refuel_date"], r["truck_id"], r["refuel_id"]))
    for i, row in enumerate(rows, 1):
        row["refuel_id"] = f"RFL-{i:05d}"
    return rows, validation_events

def validate(
    trucks,
    downtime,
    trips,
    fuel_batches,
    trip_metrics,
    refuelings,
    refuel_validation_events,
) -> None:
    downtime_calendar = build_downtime_calendar(downtime)
    for trip in trips:
        trip_date = datetime.strptime(trip["date_departure"], "%Y-%m-%d").date()
        if trip_date in downtime_calendar[trip["truck_id"]]:
            raise ValueError(f"Trip during downtime: {trip['trip_id']}")

    # 1. Every non-cancelled trip has exactly one trip_metrics record.
    expected_trip_ids = {t["trip_id"] for t in trips if t["status"] != "cancelled"}
    actual_trip_ids = {tm["trip_id"] for tm in trip_metrics}
    if expected_trip_ids != actual_trip_ids:
        raise ValueError("trip_metrics does not cover exactly the non-cancelled trips")

    # 2. Odometer never decreases per truck, checked in the same trip sequence
    # used during generation (trips sorted by date_departure/trip_id per truck).
    # A refuel is checked right after the trip that triggered it, since a
    # refuel's odometer always falls within that trip's own distance window.
    odo_after_trip = {tm["trip_id"]: tm["odometer_after_trip"] for tm in trip_metrics}
    refuel_by_trigger_trip: dict[str, list[int]] = defaultdict(list)
    for ev in refuel_validation_events:
        refuel_by_trigger_trip[ev["trigger_trip_id"]].append(ev["odometer_at_refuel"])

    trips_by_truck: dict[str, list[dict]] = defaultdict(list)
    for trip in trips:
        if trip["status"] != "cancelled":
            trips_by_truck[trip["truck_id"]].append(trip)
    for truck_id in trips_by_truck:
        trips_by_truck[truck_id].sort(key=lambda r: (r["date_departure"], r["trip_id"]))

    for truck in trucks:
        truck_id = truck["truck_id"]
        last_odo = int(truck["mileage_start_km"])
        for trip in trips_by_truck.get(truck_id, []):
            for refuel_odo in refuel_by_trigger_trip.get(trip["trip_id"], []):
                if refuel_odo < last_odo:
                    raise ValueError(f"Odometer decreased for {truck_id} at refuel")
                last_odo = refuel_odo
            trip_odo = odo_after_trip[trip["trip_id"]]
            if trip_odo < last_odo:
                raise ValueError(f"Odometer decreased for {truck_id} at trip {trip['trip_id']}")
            last_odo = trip_odo

    # 3. Refuel date not before the earliest fuel batch purchase date.
    earliest_batch_date = min(
        datetime.strptime(b["purchase_date"], "%Y-%m-%d").date() for b in fuel_batches
    )
    for rf in refuelings:
        rf_date = datetime.strptime(rf["refuel_date"], "%Y-%m-%d").date()
        if rf_date < earliest_batch_date:
            raise ValueError(f"Refuel before first fuel batch: {rf['refuel_id']}")

    # 4. Total refueled volume must not exceed total purchased volume.
    total_purchased = sum(b["liters_purchased"] for b in fuel_batches)
    total_refueled = sum(float(rf["liters_refueled"]) for rf in refuelings)
    if total_refueled > total_purchased:
        raise ValueError(
            f"Refuelings exceed purchased fuel: {total_refueled:.0f}L > {total_purchased:.0f}L"
        )

    # 5. Downtime ratio sanity check (unchanged from original dataset).
    total_days = (END_DATE - START_DATE).days + 1
    downtime_by_truck = defaultdict(int)
    for row in downtime:
        start = datetime.strptime(row["date_from"], "%Y-%m-%d").date()
        end = datetime.strptime(row["date_to"], "%Y-%m-%d").date()
        downtime_by_truck[row["truck_id"]] += (end - start).days + 1
    for truck in trucks:
        ratio = downtime_by_truck[truck["truck_id"]] / total_days
        if not 0.079 <= ratio <= 0.151:
            raise ValueError(f"Downtime ratio out of range for {truck['truck_id']}: {ratio:.3f}")

    return total_purchased, total_refueled

def main() -> None:
    trucks = make_trucks()
    drivers = make_drivers()
    clients = make_clients()
    routes = make_routes()
    downtime = make_downtime(trucks)
    client_rates = make_client_rates(clients)
    trips = make_trips(trucks, drivers, clients, routes, downtime)
    fuel_batches = make_fuel_batches()
    trip_metrics = make_trip_metrics(trucks, trips)
    refuelings, refuel_validation_events = make_refuelings(trucks, trips, trip_metrics)

    total_purchased, total_refueled = validate(
        trucks, downtime, trips, fuel_batches, trip_metrics, refuelings, refuel_validation_events
    )

    write_csv("trucks.csv", trucks, TRUCK_COLUMNS)
    write_csv("drivers.csv", drivers, DRIVER_COLUMNS)
    write_csv("clients.csv", clients, CLIENT_COLUMNS)
    write_csv("routes.csv", routes, ROUTE_COLUMNS)
    write_csv("client_rates.csv", client_rates, RATE_COLUMNS)
    write_csv("truck_downtime.csv", downtime, DOWNTIME_COLUMNS)
    write_csv("fuel_batches.csv", fuel_batches, FUEL_BATCH_COLUMNS)
    write_csv("trips.csv", trips, TRIP_COLUMNS)
    write_csv("trip_metrics.csv", trip_metrics, TRIP_METRICS_COLUMNS)
    write_csv("truck_refuelings.csv", refuelings, REFUELING_COLUMNS)

    print(f"Wrote CSVs to {OUT_DIR.resolve()}")
    print(f"Trips: {len(trips):,}")
    print(f"Trip metrics: {len(trip_metrics):,}")
    print(f"Refuelings: {len(refuelings):,}")
    print(f"Downtime events: {len(downtime):,}")
    print(f"Fuel purchased: {total_purchased:,.0f} L | Fuel refueled: {total_refueled:,.0f} L "
          f"({total_refueled/total_purchased:.1%} utilization)")

if __name__ == "__main__":
    main()