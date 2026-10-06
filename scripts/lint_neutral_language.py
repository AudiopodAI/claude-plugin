#!/usr/bin/env python3
"""Fail if anything shipped to OpenAI names one host. The audiopod-studio skills
and the Codex manifest are shared by Claude and OpenAI, so they must not say
"Claude", "Anthropic", "Cowork" or "artifact" (case-insensitive, whole word),
or use Claude-only commands such as /mcp, /plugin, /audiopod:... or
`claude mcp add`.

Every text file is scanned, whatever its extension; binary files are skipped.
plugins/audiopod is Claude-only (never shipped to OpenAI) and is not linted.

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
# A slash command starts a word: not part of a URL path (preceded by a word char, / or .).
NOT_IN_PATH = r"(?<![\w/.])"
PATTERNS = [
    re.compile(r"\bclaude\b", re.IGNORECASE),
    re.compile(r"\banthropic\b", re.IGNORECASE),
    re.compile(r"\bcowork\b", re.IGNORECASE),
    re.compile(r"\bartifacts?\b", re.IGNORECASE),
    re.compile(NOT_IN_PATH + r"/mcp\b"),
    re.compile(NOT_IN_PATH + r"/plugin\b"),
    re.compile(NOT_IN_PATH + r"/audiopod(?:-studio)?:"),
]


def iter_files(paths):
    for path in paths:
        if os.path.isfile(path):
            yield path
            continue
        for dirpath, dirnames, filenames in os.walk(path):
            dirnames.sort()
            for name in sorted(filenames):
                yield os.path.join(dirpath, name)


def read_text(path):
    with open(path, "rb") as fh:
        data = fh.read()
    if b"\0" in data:
        return None
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return None


def main():
    paths = sys.argv[1:] or DEFAULT_PATHS
    hits, scanned = [], 0
    for path in iter_files(paths):
        text = read_text(path)
        if text is None:
            continue
        scanned += 1
        for lineno, line in enumerate(text.splitlines(), 1):
            if any(p.search(line) for p in PATTERNS):
                hits.append(f"{os.path.relpath(path, ROOT)}:{lineno}: {line.strip()}")
    if scanned == 0:
        sys.exit("error: no text files scanned")
    if hits:
        print("Host-specific language in shared files (use provider-neutral wording such as 'the model'):", file=sys.stderr)
        for h in hits:
            print(f"  {h}", file=sys.stderr)
        sys.exit(1)
    print(f"OK: {scanned} shared text files are host-neutral")


if __name__ == "__main__":
    main()
