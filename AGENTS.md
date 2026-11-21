# AGENTS.md

Instructions for AI coding agents (Claude Code, Codex, Cursor, and others) working in this repository.

## What this repo is

AudioPod's agent plugins. They all connect to AudioPod's hosted MCP server:

- `https://mcp.audiopod.ai`: the full tool set
- `https://mcp.audiopod.ai/core`: transcription, stems, noise removal, speaker separation, conversion and audio-to-MIDI

This repo holds no server code: the tools live behind those endpoints. To change what a tool does, change the AudioPod API, not this repo.

| Path | What it is | Ships to |
|---|---|---|
| `.claude-plugin/marketplace.json` | Claude Code marketplace listing both plugins | Claude |
| `plugins/audiopod/` | Core plugin: transcription and audio processing | Claude only |
| `plugins/audiopod-studio/` | Full plugin: adds music, text to speech and voice | Claude **and** OpenAI (ChatGPT / Codex) |
| `plugins/*/skills/*/SKILL.md` | Agent skills: when and how to call each MCP tool | per plugin |
| `plugins/*/commands/` | Claude Code slash commands | Claude only |
| `plugins/*/evals/` | Prompt evals (and graders) for the skills | not shipped |
| `scripts/` | CI checks and the OpenAI ZIP build | — |

## Rules

- **Keep `plugins/audiopod-studio/skills/` and its `.codex-plugin/plugin.json` host-neutral.** They ship to OpenAI too. Don't write "Claude", "Anthropic", "Cowork" or "artifact" there, or Claude-only commands (`/mcp`, `/plugin`, `/audiopod:…`, `claude mcp add`). `scripts/lint_neutral_language.py` enforces this.
- `plugins/audiopod/` is Claude-only and may use Claude wording.
- The two plugins' skills overlap but are maintained separately. When you fix a skill that exists in both, fix both copies.
- Both plugins register an MCP server named `audiopod`. Never tell users to install both.
- Don't name the AI models or vendors behind AudioPod's tools in any user-facing text: skills, READMEs, listing copy. Describe capabilities ("AudioPod's transcription"), not engines.
- Never invent prices, credit costs or limits. Link to https://audiopod.ai/pricing or https://audiopod.ai/pricing.md instead.
- Skills must never make up results: no invented transcripts, stems or job outcomes. The evals check this (e.g. `no-invented-transcript`).
- Don't commit API keys. Users authenticate with OAuth when the plugin first connects, or pass an `X-API-Key` header. Keys are created at https://audiopod.ai/dashboard/account/api-keys.

## Checks to run before you open a PR

These mirror `.github/workflows/ci.yml`:

```bash
python3 scripts/check_claude_manifests.py
claude plugin validate --strict .
claude plugin validate --strict plugins/audiopod
claude plugin validate --strict plugins/audiopod-studio
python3 tests/test_ci_checks.py
python3 scripts/check_codex_manifest.py
python3 scripts/lint_neutral_language.py
scripts/build-openai-zip.sh
```

## Learn more

- AudioPod developer docs: https://docs.audiopod.ai (MCP setup: https://docs.audiopod.ai/sdks/mcp)
- MCP server card: https://audiopod.ai/.well-known/mcp/server-card.json
- Site guide for agents: https://audiopod.ai/llms.txt
