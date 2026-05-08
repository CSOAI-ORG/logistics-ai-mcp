[![logistics-ai-mcp MCP server](https://glama.ai/mcp/servers/CSOAI-ORG/logistics-ai-mcp/badges/score.svg)](https://glama.ai/mcp/servers/CSOAI-ORG/logistics-ai-mcp)
[![MCP Registry](https://img.shields.io/badge/MCP_Registry-Published-green)](https://registry.modelcontextprotocol.io)
[![PyPI](https://img.shields.io/pypi/v/logistics-ai-mcp)](https://pypi.org/project/logistics-ai-mcp/)

[![logistics-ai-mcp MCP server](https://glama.ai/mcp/servers/CSOAI-ORG/logistics-ai-mcp/badges/card.svg)](https://glama.ai/mcp/servers/CSOAI-ORG/logistics-ai-mcp)

<div align="center">

# Logistics Ai MCP

**Logistics AI MCP Server**

[![PyPI](https://img.shields.io/pypi/v/meok-logistics-ai-mcp)](https://pypi.org/project/meok-logistics-ai-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MEOK AI Labs](https://img.shields.io/badge/MEOK_AI_Labs-MCP_Server-purple)](https://meok.ai)

</div>

## Overview

Logistics AI MCP Server
Supply chain and shipping tools powered by MEOK AI Labs.

## Tools

| Tool | Description |
|------|-------------|
| `track_shipment` | Track a shipment and get current status with location updates. |
| `optimize_route` | Optimize shipping route between two locations with cost and time estimates. |
| `warehouse_inventory` | Manage warehouse inventory with stock levels, reorder alerts, and valuation. |
| `estimate_delivery` | Estimate delivery date and time windows for a shipment. |
| `customs_documentation` | Generate customs documentation requirements and duty estimates. |

## Installation

```bash
pip install meok-logistics-ai-mcp
```

## Usage with Claude Desktop

Add to your Claude Desktop MCP config:

```json
{
  "mcpServers": {
    "logistics-ai": {
      "command": "python",
      "args": ["-m", "meok_logistics_ai_mcp.server"]
    }
  }
}
```

## License

MIT © [MEOK AI Labs](https://meok.ai)
<!-- mcp-name: io.github.CSOAI-ORG/logistics-ai-mcp -->
