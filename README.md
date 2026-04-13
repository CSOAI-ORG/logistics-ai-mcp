# Logistics AI MCP

> Supply chain and shipping tools - shipment tracking, route optimization, warehouse inventory, delivery ETA, customs docs

Built by **MEOK AI Labs** | [meok.ai](https://meok.ai)

## Features

| Tool | Description |
|------|-------------|
| `track_shipment` | See tool docstring for details |
| `optimize_route` | See tool docstring for details |
| `warehouse_inventory` | See tool docstring for details |
| `estimate_delivery` | See tool docstring for details |
| `customs_documentation` | See tool docstring for details |

## Installation

```bash
pip install mcp
```

## Usage

### As an MCP Server

```bash
python server.py
```

### Claude Desktop Configuration

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "logistics-ai-mcp": {
      "command": "python",
      "args": ["/path/to/logistics-ai-mcp/server.py"]
    }
  }
}
```

## Rate Limits

Free tier includes **30-50 calls per tool per day**. Upgrade at [meok.ai/pricing](https://meok.ai/pricing) for unlimited access.

## License

MIT License - see [LICENSE](LICENSE) for details.

---

Built with FastMCP by MEOK AI Labs
