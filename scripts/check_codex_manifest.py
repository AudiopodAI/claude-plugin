#!/usr/bin/env python3
"""Check the Codex manifest (.codex-plugin/plugin.json) against OpenAI's plugin
submission rules: required fields, character and one-line limits, the category
list, HTTPS URLs, referenced files, icon shape, the MCP config it points at,
and (unless --offline) that the four listing URLs answer HTTP 200.

Rules follow developers.openai.com/plugins/deploy/submission and
developers.openai.com/plugins/deploy/submission-errors.

Usage:
  python3 scripts/check_codex_manifest.py [--offline]           # source tree
  python3 scripts/check_codex_manifest.py --zip dist/x.zip       # built ZIP
  python3 scripts/check_codex_manifest.py --plugin DIR           # any plugin dir
"""
import argparse
import json
import os
import re
import struct
import sys
import tempfile
import urllib.request
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_PLUGIN = os.path.join(ROOT, "plugins", "audiopod-studio")

SEMVER = re.compile(r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")
NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LISTING_URLS = ["websiteURL", "supportURL", "privacyPolicyURL", "termsOfServiceURL"]
# plugin_category_unknown, submission-errors reference.
CATEGORIES = {
    "Productivity", "Creativity", "Developer Tools", "Business & Operations",
    "Data & Analytics", "Communication", "Education & Research", "Security",
    "Finance", "Healthcare", "Travel", "Entertainment", "Other",
}
# Name the OpenAI listing uses; the ZIP build sets it (see build_openai_zip.py).
OPENAI_NAME = "audiopod"
MULTILINE = re.compile(r"[\r\n  ]")

errors = []


def err(msg):
    errors.append(msg)


def check_str(obj, key, limit, where, one_line=False):
    value = obj.get(key)
    if not isinstance(value, str) or not value.strip():
        err(f"{where}{key}: required non-empty string")
        return None
    if len(value) > limit:
        err(f"{where}{key}: {len(value)} chars (limit {limit})")
    if one_line and MULTILINE.search(value):
        err(f"{where}{key}: must be a single line")
    return value


def check_https(value, where):
    if not isinstance(value, str) or not value.startswith("https://"):
        err(f"{where}: must be an https URL (got {value!r})")
        return
    host = value[len("https://"):].split("/")[0]
    if not host or "@" in host:
        err(f"{where}: https URL needs a host and no embedded credentials (got {value!r})")


def resolve_rel(plugin, value, where):
    """Return the absolute path for a ./-relative manifest path, or None after an error."""
    if not isinstance(value, str) or not value.startswith("./"):
        err(f"{where}: must be a ./-prefixed relative path (got {value!r})")
        return None
    root = os.path.realpath(plugin)
    path = os.path.realpath(os.path.join(root, value))
    if path != root and not path.startswith(root + os.sep):
        err(f"{where}: {value} points outside the plugin")
        return None
    if not os.path.exists(path):
        err(f"{where}: {value} does not exist in the plugin")
        return None
    return path


def png_size(path):
    with open(path, "rb") as fh:
        head = fh.read(24)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return struct.unpack(">II", head[16:24])


def check_icon(plugin, value, where):
    path = resolve_rel(plugin, value, where)
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


def check_mcp(plugin, value):
    path = resolve_rel(plugin, value, "mcpServers")
    if not path:
        return
    try:
        cfg = json.load(open(path))
    except ValueError as e:
        err(f"mcpServers: {value} is not valid JSON ({e})")
        return
    servers = cfg.get("mcpServers") if isinstance(cfg, dict) else None
    if not isinstance(servers, dict) or len(servers) != 1:
        err(f"mcpServers: {value} must declare exactly one server under mcpServers")
        return
    for name, server in servers.items():
        url = server.get("url") if isinstance(server, dict) else None
        check_https(url, f"mcpServers.{name}.url")


def check_string_list(values, where, max_items, limit, unique=False):
    if not isinstance(values, list) or len(values) > max_items:
        err(f"{where}: must be a list of at most {max_items} items")
        return
    seen = set()
    for i, v in enumerate(values):
        if not isinstance(v, str) or not v.strip():
            err(f"{where}[{i}]: must be a non-empty string (got {type(v).__name__})")
            continue
        if len(v) > limit:
            err(f"{where}[{i}]: {len(v)} chars (limit {limit})")
        if MULTILINE.search(v):
            err(f"{where}[{i}]: must be a single line")
        key = " ".join(v.split()).casefold()
        if unique and key in seen:
            err(f"{where}[{i}]: duplicate")
        seen.add(key)


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


def validate(plugin, in_zip, offline):
    manifest_path = os.path.join(plugin, ".codex-plugin", "plugin.json")
    try:
        m = json.load(open(manifest_path))
    except (OSError, ValueError) as e:
        err(f".codex-plugin/plugin.json: cannot read ({e})")
        return
    if not isinstance(m, dict):
        err(".codex-plugin/plugin.json: must be a JSON object")
        return

    name = check_str(m, "name", 64, "")
    if name and not NAME.match(name):
        err("name: use lowercase letters, numbers, and single hyphens")
    version = check_str(m, "version", 64, "")
    if version and not SEMVER.match(version):
        err(f"version: {version!r} is not semver")

    claude_path = os.path.join(plugin, ".claude-plugin", "plugin.json")
    if in_zip:
        if name != OPENAI_NAME:
            err(f"name: ZIP manifest is named {name!r}, expected {OPENAI_NAME!r}")
        if os.path.exists(claude_path):
            err("ZIP must not contain .claude-plugin/")
    elif os.path.exists(claude_path):
        claude = json.load(open(claude_path))
        if name != claude.get("name"):
            err(f"name: {name!r} must match .claude-plugin/plugin.json ({claude.get('name')!r}) so Codex can"
                " install this repo as a marketplace; the ZIP build renames it for the OpenAI listing")
        if version != claude.get("version"):
            err(f"version: {version} does not match .claude-plugin/plugin.json ({claude.get('version')})")
    check_str(m, "description", 4000, "")

    author = m.get("author")
    if not isinstance(author, dict):
        err("author: required object")
    else:
        check_str(author, "name", 120, "author.", one_line=True)
        if "email" in author and (not isinstance(author["email"], str) or len(author["email"]) > 320):
            err("author.email: string of at most 320 chars")
        if "url" in author:
            check_https(author["url"], "author.url")
    if "homepage" in m:
        check_https(m["homepage"], "homepage")

    if m.get("skills") is not None:
        resolve_rel(plugin, m["skills"], "skills")
    if m.get("mcpServers") is not None:
        check_mcp(plugin, m["mcpServers"])

    ui = m.get("interface")
    if not isinstance(ui, dict):
        err("interface: required object")
        ui = {}
    check_str(ui, "displayName", 30, "interface.", one_line=True)
    check_str(ui, "shortDescription", 30, "interface.", one_line=True)
    check_str(ui, "longDescription", 4000, "interface.")
    check_str(ui, "developerName", 80, "interface.", one_line=True)
    category = check_str(ui, "category", 80, "interface.", one_line=True)
    if category and category not in CATEGORIES:
        err(f"interface.category: {category!r} is not one of {sorted(CATEGORIES)}")

    check_string_list(ui.get("capabilities"), "interface.capabilities", 20, 120)
    prompts = ui.get("defaultPrompt")
    if prompts is not None:
        check_string_list([prompts] if isinstance(prompts, str) else prompts,
                          "interface.defaultPrompt", 3, 128, unique=True)

    for key in ("logo", "composerIcon"):
        check_icon(plugin, ui.get(key), f"interface.{key}")
    for key in ("logoDark", "composerIconDark"):
        if key in ui:
            check_icon(plugin, ui[key], f"interface.{key}")
    shots = ui.get("screenshots") or []
    if not isinstance(shots, list):
        err("interface.screenshots: must be a list")
        shots = []
    for i, shot in enumerate(shots):
        resolve_rel(plugin, shot, f"interface.screenshots[{i}]")

    urls = []
    for key in LISTING_URLS:
        value = ui.get(key)
        check_https(value, f"interface.{key}")
        if isinstance(value, str) and len(value) > 1024:
            err(f"interface.{key}: longer than 1024 chars")
        urls.append((key, value))

    if not offline and not errors:
        live_check(urls)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--offline", action="store_true", help="skip the live GET on listing URLs")
    parser.add_argument("--plugin", default=DEFAULT_PLUGIN, help="plugin root to check")
    parser.add_argument("--zip", help="check a built ZIP instead (its root is the plugin root)")
    args = parser.parse_args()

    if args.zip:
        with tempfile.TemporaryDirectory() as tmp:
            with zipfile.ZipFile(args.zip) as zf:
                for info in zf.infolist():
                    parts = info.filename.split("/")
                    if info.filename.startswith("/") or ".." in parts:
                        sys.exit(f"error: unsafe ZIP entry {info.filename!r}")
                zf.extractall(tmp)
            validate(tmp, in_zip=True, offline=args.offline)
        label = args.zip
    else:
        validate(args.plugin, in_zip=False, offline=args.offline)
        label = os.path.join(os.path.relpath(args.plugin, ROOT), ".codex-plugin", "plugin.json")

    if errors:
        for e in errors:
            print(f"error: {e}", file=sys.stderr)
        sys.exit(1)
    print(f"OK: {label}" + (" (offline)" if args.offline else ""))


if __name__ == "__main__":
    main()
