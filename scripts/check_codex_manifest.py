#!/usr/bin/env python3
"""Check plugins/audiopod-studio/.codex-plugin/plugin.json against OpenAI's plugin
submission rules: required fields, character limits, HTTPS URLs, referenced
files, icon shape, the MCP config it points at, and (unless --offline) that the
four listing URLs answer HTTP 200.

Usage: python3 scripts/check_codex_manifest.py [--offline]
"""
import argparse
import json
import os
import re
import struct
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN = os.path.join(ROOT, "plugins", "audiopod-studio")
MANIFEST = os.path.join(PLUGIN, ".codex-plugin", "plugin.json")
CLAUDE_MANIFEST = os.path.join(PLUGIN, ".claude-plugin", "plugin.json")

SEMVER = re.compile(r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")
NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LISTING_URLS = ["websiteURL", "supportURL", "privacyPolicyURL", "termsOfServiceURL"]

errors = []


def err(msg):
    errors.append(msg)


def check_str(obj, key, limit, where):
    value = obj.get(key)
    if not isinstance(value, str) or not value.strip():
        err(f"{where}{key}: required non-empty string")
        return None
    if len(value) > limit:
        err(f"{where}{key}: {len(value)} chars (limit {limit})")
    return value


def check_https(value, where):
    if not isinstance(value, str) or not value.startswith("https://") or "@" in value.split("/")[2]:
        err(f"{where}: must be an https URL without credentials (got {value!r})")


def check_rel_path(value, where):
    if not isinstance(value, str) or not value.startswith("./"):
        err(f"{where}: must be a ./-prefixed relative path (got {value!r})")
        return None
    path = os.path.normpath(os.path.join(PLUGIN, value))
    if not path.startswith(PLUGIN) or not os.path.exists(path):
        err(f"{where}: {value} does not exist in the plugin")
        return None
    return path


def png_size(path):
    with open(path, "rb") as fh:
        head = fh.read(24)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return struct.unpack(">II", head[16:24])


def check_icon(value, where):
    path = check_rel_path(value, where)
    if not path:
        return
    if os.path.getsize(path) > 5 * 1024 * 1024:
        err(f"{where}: larger than 5 MiB")
    if path.lower().endswith(".png"):
        size = png_size(path)
        if not size:
            err(f"{where}: not a valid PNG")
            return
        w, h = size
        if w != h or w < 48 or w > 4096:
            err(f"{where}: must be square, 48 to 4096 px (got {w}x{h})")
    elif not path.lower().endswith((".jpg", ".jpeg", ".webp", ".svg")):
        err(f"{where}: unsupported image format")


def check_mcp(value):
    path = check_rel_path(value, "mcpServers")
    if not path:
        return
    try:
        cfg = json.load(open(path))
    except ValueError as e:
        err(f"mcpServers: {value} is not valid JSON ({e})")
        return
    servers = cfg.get("mcpServers")
    if not isinstance(servers, dict) or len(servers) != 1:
        err(f"mcpServers: {value} must declare exactly one server under mcpServers")
        return
    for name, server in servers.items():
        check_https(server.get("url"), f"mcpServers.{name}.url")


def live_check(urls):
    for key, url in urls:
        req = urllib.request.Request(url, headers={"User-Agent": "audiopod-plugin-ci/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                status = resp.status
        except Exception as e:  # noqa: BLE001 - report any network failure
            err(f"interface.{key}: GET {url} failed ({e})")
            continue
        if status != 200:
            err(f"interface.{key}: GET {url} returned {status}")
        else:
            print(f"  GET {url} -> 200")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--offline", action="store_true", help="skip the live GET on listing URLs")
    args = parser.parse_args()

    m = json.load(open(MANIFEST))

    name = check_str(m, "name", 64, "")
    if name and not NAME.match(name):
        err("name: use lowercase letters, numbers, and single hyphens")
    version = check_str(m, "version", 64, "")
    if version and not SEMVER.match(version):
        err(f"version: {version!r} is not semver")
    claude = json.load(open(CLAUDE_MANIFEST))
    if name != claude.get("name"):
        err(f"name: {name!r} must match .claude-plugin/plugin.json ({claude.get('name')!r}) so Codex can"
            " install this repo as a marketplace; the ZIP build renames it for the OpenAI listing")
    claude_version = claude.get("version")
    if version != claude_version:
        err(f"version: {version} does not match .claude-plugin/plugin.json ({claude_version})")
    check_str(m, "description", 4000, "")

    author = m.get("author")
    if not isinstance(author, dict):
        err("author: required object")
    else:
        check_str(author, "name", 120, "author.")
        if "email" in author and len(author["email"]) > 320:
            err("author.email: longer than 320 chars")
        if "url" in author:
            check_https(author["url"], "author.url")
    if "homepage" in m:
        check_https(m["homepage"], "homepage")

    if m.get("skills") is not None:
        check_rel_path(m["skills"], "skills")
    if m.get("mcpServers") is not None:
        check_mcp(m["mcpServers"])

    ui = m.get("interface")
    if not isinstance(ui, dict):
        err("interface: required object")
        ui = {}
    check_str(ui, "displayName", 30, "interface.")
    check_str(ui, "shortDescription", 30, "interface.")
    check_str(ui, "longDescription", 4000, "interface.")
    check_str(ui, "developerName", 80, "interface.")
    check_str(ui, "category", 80, "interface.")

    caps = ui.get("capabilities")
    if not isinstance(caps, list) or len(caps) > 20:
        err("interface.capabilities: required list of at most 20 items")
    else:
        for i, cap in enumerate(caps):
            if not isinstance(cap, str) or not cap.strip() or len(cap) > 120:
                err(f"interface.capabilities[{i}]: non-empty string of at most 120 chars")

    prompts = ui.get("defaultPrompt")
    if prompts is not None:
        prompts = [prompts] if isinstance(prompts, str) else prompts
        if len(prompts) > 3 or len(set(prompts)) != len(prompts):
            err("interface.defaultPrompt: at most 3 unique prompts")
        for i, p in enumerate(prompts):
            if len(p) > 128:
                err(f"interface.defaultPrompt[{i}]: {len(p)} chars (limit 128)")

    for key in ("logo", "composerIcon"):
        check_icon(ui.get(key), f"interface.{key}")
    for key in ("logoDark", "composerIconDark"):
        if key in ui:
            check_icon(ui[key], f"interface.{key}")
    for i, shot in enumerate(ui.get("screenshots") or []):
        check_rel_path(shot, f"interface.screenshots[{i}]")

    urls = []
    for key in LISTING_URLS:
        value = ui.get(key)
        check_https(value, f"interface.{key}")
        if isinstance(value, str) and len(value) > 1024:
            err(f"interface.{key}: longer than 1024 chars")
        urls.append((key, value))

    if not args.offline and not errors:
        live_check(urls)

    if errors:
        for e in errors:
            print(f"error: {e}", file=sys.stderr)
        sys.exit(1)
    print(f"OK: {os.path.relpath(MANIFEST, ROOT)}" + (" (offline)" if args.offline else ""))


if __name__ == "__main__":
    main()
