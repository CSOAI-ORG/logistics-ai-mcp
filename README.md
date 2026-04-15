# Logistics AI

> By [MEOK AI Labs](https://meok.ai) — Supply chain and shipping tools

## Installation

```bash
pip install logistics-ai-mcp
```

## Usage

```bash
# Run standalone
python server.py

# Or via MCP
mcp install logistics-ai-mcp
```

## Tools

### `track_shipment`
Track a shipment and get current status with location updates.

**Parameters:**
- `tracking_id` (str): Shipment tracking ID/number
- `carrier` (str): Carrier name or 'auto' for auto-detection

### `optimize_route`
Optimize shipping route between two locations with cost and time estimates.

**Parameters:**
- `origin` (str): Origin city/port name
- `destination` (str): Destination city/port name
- `weight_kg` (float): Total shipment weight in kg (default: 10.0)
- `transport_modes` (list[str]): Modes to consider: air, sea, road, rail
- `priority` (str): Optimization priority: cost, speed, balanced

### `warehouse_inventory`
Manage warehouse inventory with stock levels, reorder alerts, and valuation.

**Parameters:**
- `items` (list[dict]): Items with sku, name, quantity, unit_cost, reorder_point, max_stock
- `operation` (str): Operation: status, reorder_check, valuation

### `estimate_delivery`
Estimate delivery date and time windows for a shipment.

**Parameters:**
- `origin` (str): Origin city
- `destination` (str): Destination city
- `transport_mode` (str): air, sea, road, rail (default: road)
- `ship_date` (str): Ship date YYYY-MM-DD
- `priority` (str): express, standard, economy

### `customs_documentation`
Generate customs documentation requirements and duty estimates.

**Parameters:**
- `origin_country` (str): Origin country code
- `destination_country` (str): Destination country code
- `goods_description` (str): Description of goods
- `declared_value` (float): Declared customs value
- `currency` (str): Currency (default: USD)
- `weight_kg` (float): Total weight
- `hs_code` (str): Harmonized System code

## Authentication

Free tier: 15 calls/day. Upgrade at [meok.ai/pricing](https://meok.ai/pricing) for unlimited access.

## License

MIT — MEOK AI Labs
