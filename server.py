"""Env Manager AI MCP Server — Environment variable tools."""

import sys, os
sys.path.insert(0, os.path.expanduser('~/clawd/meok-labs-engine/shared'))
from auth_middleware import check_access

import re
import time
from typing import Any
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("env-manager-ai", instructions="MEOK AI Labs MCP Server")
_calls: dict[str, list[float]] = {}
DAILY_LIMIT = 50

def _rate_check(tool: str) -> bool:
    now = time.time()
    _calls.setdefault(tool, [])
    _calls[tool] = [t for t in _calls[tool] if t > now - 86400]
    if len(_calls[tool]) >= DAILY_LIMIT:
        return False
    _calls[tool].append(now)
    return True

def _parse_env(content: str) -> dict[str, str]:
    """Parse .env file content into key-value pairs."""
    result = {}
    for line in content.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, val = line.split("=", 1)
            key = key.strip()
            val = val.strip().strip("'\"")
            result[key] = val
    return result

@mcp.tool()
def parse_env_file(content: str, api_key: str = "") -> dict[str, Any]:
    """Parse .env file content and analyze variables."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    if not _rate_check("parse_env_file"):
        return {"error": "Rate limit exceeded (50/day)"}
    parsed = _parse_env(content)
    comments = [l.strip() for l in content.split("\n") if l.strip().startswith("#")]
    sensitive_patterns = ["password", "secret", "key", "token", "api_key", "auth", "credential", "private"]
    sensitive = [k for k in parsed if any(p in k.lower() for p in sensitive_patterns)]
    empty = [k for k, v in parsed.items() if not v]
    categories: dict[str, list[str]] = {}
    for k in parsed:
        prefix = k.split("_")[0] if "_" in k else "general"
        categories.setdefault(prefix, []).append(k)
    return {
        "variables": parsed, "count": len(parsed), "comments": len(comments),
        "sensitive_vars": sensitive, "empty_vars": empty,
        "categories": categories
    }

@mcp.tool()
def validate_env(content: str, required: str = "", type_hints: str = "", api_key: str = "") -> dict[str, Any]:
    """Validate .env against requirements. required: comma-separated keys. type_hints: KEY:type pairs (int,url,email,bool)."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    if not _rate_check("validate_env"):
        return {"error": "Rate limit exceeded (50/day)"}
    parsed = _parse_env(content)
    issues = []
    # Check required
    if required:
        for key in required.split(","):
            key = key.strip()
            if key and key not in parsed:
                issues.append({"key": key, "issue": "missing", "severity": "error"})
            elif key and not parsed.get(key):
                issues.append({"key": key, "issue": "empty", "severity": "warning"})
    # Type validation
    if type_hints:
        for hint in type_hints.split(","):
            if ":" not in hint:
                continue
            key, expected = hint.strip().split(":", 1)
            key, expected = key.strip(), expected.strip()
            val = parsed.get(key, "")
            if not val:
                continue
            if expected == "int" and not val.isdigit():
                issues.append({"key": key, "issue": f"Expected integer, got '{val}'", "severity": "error"})
            elif expected == "bool" and val.lower() not in ("true", "false", "1", "0", "yes", "no"):
                issues.append({"key": key, "issue": f"Expected boolean, got '{val}'", "severity": "error"})
            elif expected == "url" and not re.match(r'https?://', val):
                issues.append({"key": key, "issue": f"Expected URL, got '{val}'", "severity": "error"})
            elif expected == "email" and not re.match(r'[^@]+@[^@]+\.[^@]+', val):
                issues.append({"key": key, "issue": f"Expected email, got '{val}'", "severity": "error"})
    # Check for common issues
    for key, val in parsed.items():
        if val and val[0] in ("'", '"') and val[-1] != val[0]:
            issues.append({"key": key, "issue": "Mismatched quotes", "severity": "warning"})
        if " " in key:
            issues.append({"key": key, "issue": "Key contains spaces", "severity": "error"})
    valid = not any(i["severity"] == "error" for i in issues)
    return {"valid": valid, "issues": issues, "issue_count": len(issues), "variable_count": len(parsed)}

@mcp.tool()
def generate_env_template(content: str, include_comments: bool = True, mask_values: bool = True, api_key: str = "") -> dict[str, Any]:
    """Generate .env.example template from an existing .env file."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    if not _rate_check("generate_env_template"):
        return {"error": "Rate limit exceeded (50/day)"}
    parsed = _parse_env(content)
    sensitive_patterns = ["password", "secret", "key", "token", "api_key", "auth", "credential", "private"]
    lines = []
    if include_comments:
        lines.append("# Environment Configuration Template")
        lines.append("# Copy to .env and fill in values")
        lines.append("")
    current_prefix = ""
    for key, val in parsed.items():
        prefix = key.split("_")[0] if "_" in key else ""
        if prefix != current_prefix and include_comments:
            lines.append("")
            lines.append(f"# {prefix} Configuration")
            current_prefix = prefix
        is_sensitive = any(p in key.lower() for p in sensitive_patterns)
        if mask_values and is_sensitive:
            lines.append(f"{key}=")
        elif mask_values:
            if val.isdigit():
                lines.append(f"{key}={val}")
            elif val.lower() in ("true", "false"):
                lines.append(f"{key}={val}")
            elif re.match(r'https?://', val):
                lines.append(f"{key}=https://example.com")
            else:
                lines.append(f"{key}=")
        else:
            lines.append(f"{key}={val}")
    template = "\n".join(lines)
    return {"template": template, "variable_count": len(parsed), "masked_count": sum(1 for k in parsed if any(p in k.lower() for p in sensitive_patterns))}

@mcp.tool()
def compare_envs(env_a: str, env_b: str, label_a: str = "env_a", label_b: str = "env_b", api_key: str = "") -> dict[str, Any]:
    """Compare two .env files and find differences."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    if not _rate_check("compare_envs"):
        return {"error": "Rate limit exceeded (50/day)"}
    a = _parse_env(env_a)
    b = _parse_env(env_b)
    all_keys = sorted(set(list(a.keys()) + list(b.keys())))
    only_a = [k for k in all_keys if k in a and k not in b]
    only_b = [k for k in all_keys if k in b and k not in a]
    different = [{"key": k, label_a: a[k], label_b: b[k]} for k in all_keys if k in a and k in b and a[k] != b[k]]
    same = [k for k in all_keys if k in a and k in b and a[k] == b[k]]
    return {
        f"only_in_{label_a}": only_a, f"only_in_{label_b}": only_b,
        "different_values": different, "identical": same,
        "total_a": len(a), "total_b": len(b), "identical_count": len(same)
    }

if __name__ == "__main__":
    mcp.run()
