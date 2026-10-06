#!/usr/bin/env python3
"""Check the Claude marketplace: marketplace.json parses, lists both plugins, each
source directory exists with a .claude-plugin/plugin.json whose name and version
match the marketplace entry, and each plugin has an MCP config with an https URL.

Usage: python3 scripts/check_claude_manifests.py
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MARKETPLACE = os.path.join(ROOT, ".claude-plugin", "marketplace.json")
EXPECTED = {"audiopod": "./plugins/audiopod", "audiopod-studio": "./plugins/audiopod-studio"}

errors = []


def main():
    market = json.load(open(MARKETPLACE))
    entries = {p.get("name"): p for p in market.get("plugins", [])}
    for name, source in EXPECTED.items():
        entry = entries.get(name)
        if not entry:
            errors.append(f"marketplace.json: plugin {name} is not listed")
            continue
        if entry.get("source") != source:
            errors.append(f"marketplace.json: {name} source is {entry.get('source')!r}, expected {source!r}")
        src = os.path.normpath(os.path.join(ROOT, entry.get("source", "")))
        if not os.path.isdir(src):
            errors.append(f"{name}: source directory {entry.get('source')} does not exist")
            continue
        manifest_path = os.path.join(src, ".claude-plugin", "plugin.json")
        if not os.path.isfile(manifest_path):
            errors.append(f"{name}: missing .claude-plugin/plugin.json")
            continue
        manifest = json.load(open(manifest_path))
        if manifest.get("name") != name:
            errors.append(f"{name}: plugin.json name is {manifest.get('name')!r}")
        for field in ("version", "description"):
            if not manifest.get(field):
                errors.append(f"{name}: plugin.json {field} is missing")
        if manifest.get("version") != entry.get("version"):
            errors.append(f"{name}: plugin.json version {manifest.get('version')} != marketplace {entry.get('version')}")
        if entry.get("version") != market.get("metadata", {}).get("version"):
            errors.append(f"{name}: marketplace entry version differs from metadata.version")
        mcp_path = os.path.join(src, ".mcp.json")
        if not os.path.isfile(mcp_path):
            errors.append(f"{name}: missing .mcp.json")
            continue
        servers = json.load(open(mcp_path)).get("mcpServers", {})
        for server, cfg in servers.items():
            if not str(cfg.get("url", "")).startswith("https://"):
                errors.append(f"{name}: .mcp.json server {server} url is not https")
        if not servers:
            errors.append(f"{name}: .mcp.json declares no servers")

    if errors:
        for e in errors:
            print(f"error: {e}", file=sys.stderr)
        sys.exit(1)
    print(f"OK: marketplace lists {', '.join(EXPECTED)} and each source is a valid plugin")


if __name__ == "__main__":
    main()
