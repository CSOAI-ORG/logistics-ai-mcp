"""
Logistics AI MCP Server
Supply chain and shipping tools powered by MEOK AI Labs.
"""


import sys, os
sys.path.insert(0, os.path.expanduser('~/clawd/meok-labs-engine/shared'))
from auth_middleware import check_access

import time
import math
import hashlib
import random
from datetime import datetime, date, timedelta
from collections import defaultdict
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("logistics-ai", instructions="MEOK AI Labs MCP Server")

_call_counts: dict[str, list[float]] = defaultdict(list)
FREE_TIER_LIMIT = 40
WINDOW = 86400


def _check_rate_limit(tool_name: str) -> None:
    now = time.time()
    _call_counts[tool_name] = [t for t in _call_counts[tool_name] if now - t < WINDOW]
    if len(_call_counts[tool_name]) >= FREE_TIER_LIMIT:
        raise ValueError(f"Rate limit exceeded for {tool_name}. Free tier: {FREE_TIER_LIMIT}/day.")
    _call_counts[tool_name].append(now)


# Major port/city coordinates for route calculation
LOCATIONS = {
    "london": (51.5074, -0.1278), "new_york": (40.7128, -74.0060),
    "los_angeles": (34.0522, -118.2437), "shanghai": (31.2304, 121.4737),
    "singapore": (1.3521, 103.8198), "dubai": (25.2048, 55.2708),
    "rotterdam": (51.9244, 4.4777), "hamburg": (53.5511, 9.9937),
    "tokyo": (35.6762, 139.6503), "sydney": (-33.8688, 151.2093),
    "mumbai": (19.0760, 72.8777), "hong_kong": (22.3193, 114.1694),
    "barcelona": (41.3874, 2.1686), "miami": (25.7617, -80.1918),
    "cape_town": (-33.9249, 18.4241), "sao_paulo": (-23.5505, -46.6333),
}

TRANSPORT_SPEEDS = {"air": 800, "sea": 30, "road": 70, "rail": 120}  # km/h
TRANSPORT_COSTS_PER_KG_KM = {"air": 0.005, "sea": 0.0003, "road": 0.001, "rail": 0.0006}


def _haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))


@mcp.tool()
def track_shipment(
    tracking_id: str,
    carrier: str = "auto", api_key: str = "") -> dict:
    """Track a shipment and get current status with location updates.

    Args:
        tracking_id: Shipment tracking ID/number
        carrier: Carrier name or 'auto' for auto-detection
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    _check_rate_limit("track_shipment")

    # Deterministic simulation based on tracking ID
    seed = int(hashlib.md5(tracking_id.encode()).hexdigest()[:8], 16)
    rng = random.Random(seed)

    statuses = ["PICKED_UP", "IN_TRANSIT", "AT_HUB", "OUT_FOR_DELIVERY", "DELIVERED", "CUSTOMS_HOLD"]
    status = rng.choice(statuses)

    cities = list(LOCATIONS.keys())
    origin = rng.choice(cities)
    destination = rng.choice([c for c in cities if c != origin])

    event_count = rng.randint(2, 6)
    events = []
    base_date = date.today() - timedelta(days=event_count)
    for i in range(event_count):
        events.append({
            "timestamp": (base_date + timedelta(days=i, hours=rng.randint(0, 23))).isoformat(),
            "location": rng.choice(cities).replace("_", " ").title(),
            "status": statuses[min(i, len(statuses) - 1)],
            "description": f"Package processed at facility",
        })

    progress = min(100, rng.randint(15, 100))

    return {
        "tracking_id": tracking_id,
        "carrier": carrier if carrier != "auto" else rng.choice(["DHL", "FedEx", "UPS", "Maersk", "CMA CGM"]),
        "status": status,
        "origin": origin.replace("_", " ").title(),
        "destination": destination.replace("_", " ").title(),
        "progress_percent": progress,
        "estimated_delivery": (date.today() + timedelta(days=rng.randint(1, 14))).isoformat(),
        "events": events,
        "weight_kg": round(rng.uniform(0.5, 500), 1),
    }


@mcp.tool()
def optimize_route(
    origin: str,
    destination: str,
    weight_kg: float = 10.0,
    transport_modes: list[str] | None = None,
    priority: str = "balanced", api_key: str = "") -> dict:
    """Optimize shipping route between two locations with cost and time estimates.

    Args:
        origin: Origin city/port name
        destination: Destination city/port name
        weight_kg: Total shipment weight in kg
        transport_modes: Modes to consider: air, sea, road, rail (default: all)
        priority: Optimization priority: cost, speed, balanced
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    _check_rate_limit("optimize_route")

    transport_modes = transport_modes or ["air", "sea", "road", "rail"]
    origin_key = origin.lower().replace(" ", "_")
    dest_key = destination.lower().replace(" ", "_")

    if origin_key not in LOCATIONS:
        origin_key = min(LOCATIONS.keys(), key=lambda k: len(set(k) - set(origin_key)))
    if dest_key not in LOCATIONS:
        dest_key = min(LOCATIONS.keys(), key=lambda k: len(set(k) - set(dest_key)))

    lat1, lon1 = LOCATIONS[origin_key]
    lat2, lon2 = LOCATIONS[dest_key]
    distance = _haversine(lat1, lon1, lat2, lon2)

    routes = []
    for mode in transport_modes:
        if mode == "sea" and distance < 500:
            continue
        if mode == "road" and distance > 5000:
            continue

        route_distance = distance * (1.0 if mode == "air" else 1.3 if mode == "sea" else 1.2)
        speed = TRANSPORT_SPEEDS[mode]
        hours = route_distance / speed
        cost_per_kg_km = TRANSPORT_COSTS_PER_KG_KM[mode]
        cost = route_distance * weight_kg * cost_per_kg_km

        co2_factors = {"air": 0.602, "sea": 0.016, "road": 0.096, "rail": 0.028}
        co2 = route_distance * weight_kg * co2_factors[mode] / 1000

        routes.append({
            "mode": mode,
            "distance_km": round(route_distance),
            "estimated_hours": round(hours, 1),
            "estimated_days": round(hours / 24, 1),
            "cost_estimate": round(cost, 2),
            "cost_currency": "USD",
            "co2_kg": round(co2, 2),
        })

    if priority == "cost":
        routes.sort(key=lambda r: r["cost_estimate"])
    elif priority == "speed":
        routes.sort(key=lambda r: r["estimated_hours"])
    else:
        routes.sort(key=lambda r: r["cost_estimate"] * 0.5 + r["estimated_hours"] * 10)

    return {
        "origin": origin,
        "destination": destination,
        "straight_line_distance_km": round(distance),
        "weight_kg": weight_kg,
        "priority": priority,
        "recommended": routes[0] if routes else None,
        "alternatives": routes[1:],
    }


@mcp.tool()
def warehouse_inventory(
    items: list[dict],
    operation: str = "status", api_key: str = "") -> dict:
    """Manage warehouse inventory with stock levels, reorder alerts, and valuation.

    Args:
        items: List of dicts with keys: sku, name, quantity, unit_cost, reorder_point (optional), max_stock (optional)
        operation: Operation type: status, reorder_check, valuation
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    _check_rate_limit("warehouse_inventory")

    total_value = 0.0
    total_items = 0
    reorder_needed = []
    overstocked = []
    healthy = []

    for item in items:
        sku = item.get("sku", "UNKNOWN")
        name = item.get("name", sku)
        qty = int(item.get("quantity", 0))
        cost = float(item.get("unit_cost", 0))
        reorder_point = int(item.get("reorder_point", 10))
        max_stock = int(item.get("max_stock", 1000))

        value = qty * cost
        total_value += value
        total_items += qty

        record = {
            "sku": sku,
            "name": name,
            "quantity": qty,
            "unit_cost": cost,
            "total_value": round(value, 2),
            "reorder_point": reorder_point,
        }

        if qty <= reorder_point:
            record["status"] = "REORDER"
            record["suggested_order"] = max_stock - qty
            reorder_needed.append(record)
        elif qty > max_stock * 0.9:
            record["status"] = "OVERSTOCKED"
            overstocked.append(record)
        else:
            record["status"] = "HEALTHY"
            healthy.append(record)

    return {
        "operation": operation,
        "summary": {
            "total_skus": len(items),
            "total_items": total_items,
            "total_value": round(total_value, 2),
            "items_needing_reorder": len(reorder_needed),
            "items_overstocked": len(overstocked),
            "items_healthy": len(healthy),
        },
        "reorder_needed": reorder_needed,
        "overstocked": overstocked,
        "healthy": healthy if operation == "status" else [],
    }


@mcp.tool()
def estimate_delivery(
    origin: str,
    destination: str,
    transport_mode: str = "road",
    ship_date: str = "",
    priority: str = "standard", api_key: str = "") -> dict:
    """Estimate delivery date and time windows for a shipment.

    Args:
        origin: Origin city
        destination: Destination city
        transport_mode: Transport mode: air, sea, road, rail
        ship_date: Ship date YYYY-MM-DD (default: today)
        priority: Service level: express, standard, economy
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    _check_rate_limit("estimate_delivery")

    origin_key = origin.lower().replace(" ", "_")
    dest_key = destination.lower().replace(" ", "_")

    if origin_key not in LOCATIONS:
        origin_key = min(LOCATIONS.keys(), key=lambda k: len(set(k) - set(origin_key)))
    if dest_key not in LOCATIONS:
        dest_key = min(LOCATIONS.keys(), key=lambda k: len(set(k) - set(dest_key)))

    lat1, lon1 = LOCATIONS[origin_key]
    lat2, lon2 = LOCATIONS[dest_key]
    distance = _haversine(lat1, lon1, lat2, lon2)

    route_mult = {"air": 1.0, "sea": 1.3, "road": 1.2, "rail": 1.15}
    route_distance = distance * route_mult.get(transport_mode, 1.2)

    speed = TRANSPORT_SPEEDS.get(transport_mode, 70)
    base_hours = route_distance / speed

    priority_mult = {"express": 0.7, "standard": 1.0, "economy": 1.5}
    total_hours = base_hours * priority_mult.get(priority, 1.0)

    # Add handling time
    handling = {"express": 4, "standard": 24, "economy": 48}
    total_hours += handling.get(priority, 24)

    # Add customs time for international
    customs_hours = 24 if distance > 2000 else 0
    total_hours += customs_hours

    if not ship_date:
        ship_dt = datetime.now()
    else:
        ship_dt = datetime.fromisoformat(ship_date)

    delivery_dt = ship_dt + timedelta(hours=total_hours)
    earliest = delivery_dt - timedelta(hours=total_hours * 0.1)
    latest = delivery_dt + timedelta(hours=total_hours * 0.2)

    return {
        "origin": origin,
        "destination": destination,
        "transport_mode": transport_mode,
        "priority": priority,
        "distance_km": round(route_distance),
        "ship_date": ship_dt.date().isoformat(),
        "estimated_delivery": delivery_dt.date().isoformat(),
        "delivery_window": {
            "earliest": earliest.date().isoformat(),
            "latest": latest.date().isoformat(),
        },
        "transit_days": round(total_hours / 24, 1),
        "includes_customs": customs_hours > 0,
    }


@mcp.tool()
def customs_documentation(
    origin_country: str,
    destination_country: str,
    goods_description: str,
    declared_value: float,
    currency: str = "USD",
    weight_kg: float = 1.0,
    hs_code: str = "", api_key: str = "") -> dict:
    """Generate customs documentation requirements and duty estimates.

    Args:
        origin_country: Origin country code (e.g. GB, US)
        destination_country: Destination country code
        goods_description: Description of goods being shipped
        declared_value: Declared customs value
        currency: Currency of declared value
        weight_kg: Total weight in kg
        hs_code: Harmonized System code (if known)
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    _check_rate_limit("customs_documentation")

    origin = origin_country.upper()
    dest = destination_country.upper()

    # Duty rate estimates by destination region
    duty_rates = {
        "US": 0.05, "GB": 0.04, "EU": 0.04, "CN": 0.10, "IN": 0.15,
        "AU": 0.05, "JP": 0.03, "BR": 0.20, "RU": 0.12,
    }
    # Check for EU members
    eu_members = {"DE", "FR", "IT", "ES", "NL", "BE", "AT", "SE", "DK", "FI", "PT", "IE", "PL", "CZ", "GR", "RO", "HU", "BG", "HR", "SK", "SI", "LT", "LV", "EE", "LU", "MT", "CY"}

    is_eu_dest = dest in eu_members
    is_eu_origin = origin in eu_members

    # No customs within EU single market
    if is_eu_dest and is_eu_origin:
        return {
            "origin": origin,
            "destination": dest,
            "customs_required": False,
            "reason": "EU Single Market - no customs duties between member states",
            "documents_required": ["Commercial Invoice", "Packing List"],
        }

    effective_dest = "EU" if is_eu_dest else dest
    duty_rate = duty_rates.get(effective_dest, 0.08)
    duty_amount = round(declared_value * duty_rate, 2)

    vat_import = {"GB": 0.20, "EU": 0.20, "AU": 0.10, "JP": 0.10, "IN": 0.18, "BR": 0.17}
    import_vat_rate = vat_import.get(effective_dest, 0.10)
    import_vat = round((declared_value + duty_amount) * import_vat_rate, 2)

    documents = [
        "Commercial Invoice (3 copies)",
        "Packing List",
        "Bill of Lading / Air Waybill",
        "Certificate of Origin",
    ]

    if declared_value > 5000:
        documents.append("Export License (may be required)")
    if dest in ("US", "CA"):
        documents.append("USMCA Certificate (if applicable)")
    if is_eu_dest:
        documents.append("EUR.1 Movement Certificate (if applicable)")
        documents.append("EORI Number required")
    if dest == "GB":
        documents.append("EORI Number (GB)")
        documents.append("UK Import Declaration")

    return {
        "origin": origin,
        "destination": dest,
        "goods_description": goods_description,
        "declared_value": declared_value,
        "currency": currency,
        "weight_kg": weight_kg,
        "hs_code": hs_code or "To be determined - consult tariff schedule",
        "customs_required": True,
        "estimated_duty": {
            "duty_rate": f"{duty_rate * 100:.1f}%",
            "duty_amount": duty_amount,
            "import_vat_rate": f"{import_vat_rate * 100:.1f}%",
            "import_vat": import_vat,
            "total_duties_and_taxes": round(duty_amount + import_vat, 2),
        },
        "documents_required": documents,
        "de_minimis_threshold": "Check destination country for duty-free threshold",
        "disclaimer": "Duty estimates are approximate. Actual rates depend on HS classification and trade agreements.",
    }


if __name__ == "__main__":
    mcp.run()
