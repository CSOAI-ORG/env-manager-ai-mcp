<div align="center">

# Env Manager Ai MCP

**Env Manager AI MCP Server — Environment variable tools.**

[![PyPI](https://img.shields.io/pypi/v/meok-env-manager-ai-mcp)](https://pypi.org/project/meok-env-manager-ai-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MEOK AI Labs](https://img.shields.io/badge/MEOK_AI_Labs-MCP_Server-purple)](https://meok.ai)

</div>

## Overview

Env Manager AI MCP Server — Environment variable tools.

## Tools

| Tool | Description |
|------|-------------|
| `parse_env_file` | Parse .env file content and analyze variables. |
| `validate_env` | Validate .env against requirements. required: comma-separated keys. type_hints:  |
| `generate_env_template` | Generate .env.example template from an existing .env file. |
| `compare_envs` | Compare two .env files and find differences. |

## Installation

```bash
pip install meok-env-manager-ai-mcp
```

## Usage with Claude Desktop

Add to your Claude Desktop MCP config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "env-manager-ai": {
      "command": "python",
      "args": ["-m", "meok_env_manager_ai_mcp.server"]
    }
  }
}
```

## Usage with FastMCP

```python
from mcp.server.fastmcp import FastMCP

# This server exposes 4 tool(s) via MCP
# See server.py for full implementation
```

## License

MIT © [MEOK AI Labs](https://meok.ai)
