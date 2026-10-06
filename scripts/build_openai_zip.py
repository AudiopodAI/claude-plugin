#!/usr/bin/env python3
"""Build dist/audiopod-openai.zip: the OpenAI (ChatGPT + Codex) upload of audiopod-studio.

The ZIP root is the plugin root of plugins/audiopod-studio, restricted to an
allowlist of what the OpenAI package format uses (Codex manifest, MCP config,
skills, assets, license). Claude-only parts (commands/, evals/, .claude-plugin/,
the Claude README) are left out.

Refuses to build if the plugin contains a symlink anywhere, a hidden file or
directory under skills/, or a file that resolves outside the plugin root.

Size limits are our own conservative ones (SKILL.md 256 KiB, skill 5 MiB,
archive 8 MiB), well under OpenAI's documented package limits (100 MB
compressed, 512 MiB extracted, 100 MiB per entry).

The repo's .codex-plugin/plugin.json is named "audiopod-studio" so that Codex
can install this repo as a marketplace (Codex requires the manifest name to
match the marketplace entry). The OpenAI directory listing is "audiopod", so
the ZIP copy of the manifest gets that name.

Usage: python3 scripts/build_openai_zip.py [--plugin DIR] [--out dist/audiopod-openai.zip]
"""
import argparse
import json
import os
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_PLUGIN = os.path.join(ROOT, "plugins", "audiopod-studio")

# Paths (relative to the plugin root) that go into the ZIP. Everything else stays out.
INCLUDE = [".codex-plugin", ".mcp.json", "skills", "assets", "LICENSE"]

KIB, MIB = 1024, 1024 * 1024
MAX_SKILL_MD = 256 * KIB
MAX_SKILL_DIR = 5 * MIB
MAX_ARCHIVE = 8 * MIB

# Package name of the OpenAI directory listing (see the module docstring).
OPENAI_NAME = "audiopod"
CODEX_MANIFEST = os.path.join(".codex-plugin", "plugin.json")

# Fixed timestamp so the same sources always produce the same ZIP.
ZIP_DATE = (2020, 1, 1, 0, 0, 0)


def safety_errors(plugin):
    """Symlinks anywhere, hidden entries under skills/, paths escaping the root."""
    errors = []
    root = os.path.realpath(plugin)
    for dirpath, dirnames, filenames in os.walk(plugin, followlinks=False):
        rel_dir = os.path.relpath(dirpath, plugin)
        for name in dirnames + filenames:
            path = os.path.join(dirpath, name)
            rel = os.path.normpath(os.path.join(rel_dir, name))
            if os.path.islink(path):
                errors.append(f"{rel}: symlinks are not allowed in the plugin")
                continue
            if rel.split(os.sep)[0] == "skills" and name.startswith("."):
                errors.append(f"{rel}: hidden files and directories are not allowed under skills/")
            real = os.path.realpath(path)
            if not real.startswith(root + os.sep):
                errors.append(f"{rel}: resolves outside the plugin root")
    return errors


def collect_files(plugin):
    files = []
    for entry in INCLUDE:
        path = os.path.join(plugin, entry)
        if not os.path.exists(path):
            sys.exit(f"error: {entry} is missing from {plugin}")
        if os.path.isfile(path):
            files.append(entry)
            continue
        for dirpath, dirnames, filenames in os.walk(path, followlinks=False):
            dirnames.sort()
            for name in sorted(filenames):
                if name == ".DS_Store":
                    continue
                files.append(os.path.relpath(os.path.join(dirpath, name), plugin))
    return files


def check_skill_limits(plugin):
    errors = []
    sizes = {}
    skills_dir = os.path.join(plugin, "skills")
    for skill in sorted(os.listdir(skills_dir)):
        sdir = os.path.join(skills_dir, skill)
        if not os.path.isdir(sdir):
            continue
        md = os.path.join(sdir, "SKILL.md")
        if not os.path.isfile(md):
            errors.append(f"skills/{skill}: missing SKILL.md")
            continue
        md_size = os.path.getsize(md)
        total = sum(
            os.path.getsize(os.path.join(dp, f))
            for dp, _, fs in os.walk(sdir)
            for f in fs
        )
        sizes[skill] = (md_size, total)
        if md_size > MAX_SKILL_MD:
            errors.append(f"skills/{skill}/SKILL.md is {md_size} bytes (limit {MAX_SKILL_MD})")
        if total > MAX_SKILL_DIR:
            errors.append(f"skills/{skill} is {total} bytes (limit {MAX_SKILL_DIR})")
    return sizes, errors


def fail(errors):
    for e in errors:
        print(f"error: {e}", file=sys.stderr)
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--plugin", default=DEFAULT_PLUGIN)
    parser.add_argument("--out", default=os.path.join(ROOT, "dist", "audiopod-openai.zip"))
    args = parser.parse_args()
    plugin = args.plugin

    unsafe = safety_errors(plugin)
    if unsafe:
        fail(unsafe)

    sizes, errors = check_skill_limits(plugin)
    files = collect_files(plugin)

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with zipfile.ZipFile(args.out, "w", zipfile.ZIP_DEFLATED) as zf:
        for rel in files:
            info = zipfile.ZipInfo(rel.replace(os.sep, "/"), ZIP_DATE)
            info.external_attr = 0o644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            with open(os.path.join(plugin, rel), "rb") as fh:
                data = fh.read()
            if rel == CODEX_MANIFEST:
                manifest = json.loads(data)
                manifest["name"] = OPENAI_NAME
                data = (json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode()
            zf.writestr(info, data)

    archive = os.path.getsize(args.out)
    if archive > MAX_ARCHIVE:
        errors.append(f"archive is {archive} bytes (limit {MAX_ARCHIVE})")

    print(f"Built {os.path.relpath(args.out, ROOT)}: {len(files)} files, {archive} bytes (limit {MAX_ARCHIVE})")
    for skill, (md_size, total) in sizes.items():
        print(f"  skills/{skill}: SKILL.md {md_size} bytes, skill total {total} bytes")
    if errors:
        fail(errors)


if __name__ == "__main__":
    main()
