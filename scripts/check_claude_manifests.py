#!/usr/bin/env python3
"""Check the Claude marketplace: marketplace.json parses, lists both plugins,
every entry's source directory exists with a .claude-plugin/plugin.json whose
name and version match the entry, and each plugin has an MCP config with an
https URL.

Usage: python3 scripts/check_claude_manifests.py [--root DIR]
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPECTED = {"audiopod": "./plugins/audiopod", "audiopod-studio": "./plugins/audiopod-studio"}

errors = []


def check_entry(root, market, entry):
    name = entry.get("name")
    source = entry.get("source")
    if not isinstance(name, str) or not name:
        errors.append(f"marketplace.json: an entry has no name ({entry!r})")
        return
    if not isinstance(source, str) or not source:
        errors.append(f"marketplace.json: {name} has no source")
        return
    if name in EXPECTED and source != EXPECTED[name]:
        errors.append(f"marketplace.json: {name} source is {source!r}, expected {EXPECTED[name]!r}")
    src = os.path.normpath(os.path.join(root, source))
    if not os.path.isdir(src):
        errors.append(f"{name}: source directory {source} does not exist")
        return
    manifest_path = os.path.join(src, ".claude-plugin", "plugin.json")
    if not os.path.isfile(manifest_path):
        errors.append(f"{name}: missing .claude-plugin/plugin.json")
        return
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
        return
    servers = json.load(open(mcp_path)).get("mcpServers", {})
    if not servers:
        errors.append(f"{name}: .mcp.json declares no servers")
    for server, cfg in servers.items():
        if not str(cfg.get("url", "")).startswith("https://"):
            errors.append(f"{name}: .mcp.json server {server} url is not https")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=ROOT, help="repository root holding .claude-plugin/marketplace.json")
    args = parser.parse_args()

    market = json.load(open(os.path.join(args.root, ".claude-plugin", "marketplace.json")))
    entries = market.get("plugins", [])
    names = {e.get("name") for e in entries if isinstance(e, dict)}
    for name in EXPECTED:
        if name not in names:
            errors.append(f"marketplace.json: plugin {name} is not listed")
    for entry in entries:
        if not isinstance(entry, dict):
            errors.append(f"marketplace.json: entry {entry!r} is not an object")
            continue
        check_entry(args.root, market, entry)

    if errors:
        for e in errors:
            print(f"error: {e}", file=sys.stderr)
        sys.exit(1)
    print(f"OK: marketplace lists {len(entries)} plugins and every source is a valid plugin")


if __name__ == "__main__":
    main()
