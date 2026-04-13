# env-manager-ai-mcp

MCP server for environment variable management tools.

## Tools

- **parse_env_file** — Parse .env files with sensitivity detection
- **validate_env** — Validate against required vars and type hints
- **generate_env_template** — Generate .env.example templates
- **compare_envs** — Diff two .env files

## Usage

```bash
pip install mcp
python server.py
```

## Rate Limits

50 calls/day per tool (free tier).
