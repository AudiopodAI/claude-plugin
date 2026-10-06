#!/usr/bin/env python3
"""Fail if anything shipped to OpenAI names one host. The audiopod-studio skills
and the Codex manifest are shared by Claude and OpenAI, so they must not say
"Claude" or "artifact" (case-insensitive, whole word), or use Claude-only
commands such as /mcp or `claude mcp add`.

Usage: python3 scripts/lint_neutral_language.py [path ...]
Defaults to plugins/audiopod-studio/skills and the Codex manifest.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_PATHS = [
    os.path.join(ROOT, "plugins", "audiopod-studio", "skills"),
    os.path.join(ROOT, "plugins", "audiopod-studio", ".codex-plugin", "plugin.json"),
]
PATTERNS = [
    re.compile(r"\bclaude\b", re.IGNORECASE),
    re.compile(r"\bartifacts?\b", re.IGNORECASE),
    re.compile(r"(?<![\w/])/mcp\b"),
]


def iter_files(paths):
    for path in paths:
        if os.path.isfile(path):
            yield path
            continue
        for dirpath, _, filenames in os.walk(path):
            for name in sorted(filenames):
                if name.endswith((".md", ".json", ".txt")):
                    yield os.path.join(dirpath, name)


def main():
    paths = sys.argv[1:] or DEFAULT_PATHS
    hits, scanned = [], 0
    for path in iter_files(paths):
        scanned += 1
        with open(path, encoding="utf-8") as fh:
            for lineno, line in enumerate(fh, 1):
                for pat in PATTERNS:
                    if pat.search(line):
                        hits.append(f"{os.path.relpath(path, ROOT)}:{lineno}: {line.strip()}")
                        break
    if scanned == 0:
        sys.exit("error: no files scanned")
    if hits:
        print("Host-specific language in shared files (use provider-neutral wording such as 'the model'):", file=sys.stderr)
        for h in hits:
            print(f"  {h}", file=sys.stderr)
        sys.exit(1)
    print(f"OK: {scanned} shared files are host-neutral")


if __name__ == "__main__":
    main()
