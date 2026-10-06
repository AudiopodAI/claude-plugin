# AudioPod plugins for Claude, ChatGPT, and Codex

This repository is a Claude Code plugin marketplace, and also the source of
AudioPod's OpenAI plugin for ChatGPT and Codex (see
[Use with ChatGPT / Codex](#use-with-chatgpt--codex)). It connects Claude to
[AudioPod](https://audiopod.ai)'s audio tools through AudioPod's hosted MCP
server. Ask Claude to transcribe a recording, split a song into stems, clean up
a noisy interview, or separate a podcast by speaker, and it runs the job on
your AudioPod account and hands back the results.

## Plugins

| Plugin | What it includes |
|---|---|
| `audiopod` | Transcription and audio processing: transcription, stem separation, noise removal, speaker separation, format conversion, and audio-to-MIDI conversion |
| `audiopod-studio` | Everything in `audiopod` (including audio-to-MIDI conversion), plus music, text to speech, and voice features |

Install ONE of them, not both: both register an MCP server named `audiopod`, so installing both would duplicate the tools.

## Install

In Claude Code:

```
/plugin marketplace add AudiopodAI/claude-plugin
/plugin install audiopod@audiopod
```

or, for the full plugin with music, text to speech, and voice features:

```
/plugin install audiopod-studio@audiopod
```

Install the plugin. The first time Claude uses an AudioPod tool it asks you to
connect: choose Connect (or run /mcp, select AudioPod, then Authenticate). A
browser window opens, you sign in to your AudioPod account, review what the
connection can do, and select Allow access. No API key to copy. You can
disconnect at any time from your AudioPod account page.

#### Using an API key instead (CI or headless)

Create a key at <https://audiopod.ai/dashboard/account/api-keys> and run:

```
claude mcp add --transport http audiopod https://mcp.audiopod.ai --header "X-API-Key: <your key>"
```

This is added separately from the plugin (use `https://mcp.audiopod.ai/core` for the `audiopod` plugin's tool set).

## Use with ChatGPT / Codex

The same skills ship to OpenAI as the **AudioPod** plugin, built from
`plugins/audiopod-studio` (the full tool set). It connects to the same hosted
MCP server, `https://mcp.audiopod.ai`, and you sign in with your AudioPod
account the same way.

- **ChatGPT**: install AudioPod from the plugin directory once it is listed.
  Until then, go to <https://chatgpt.com/plugins>, select the plus button, then
  **Add custom MCP server**, and enter `https://mcp.audiopod.ai`.
- **Codex**: add the server and sign in:

  ```
  codex mcp add audiopod --url https://mcp.audiopod.ai
  codex mcp login audiopod
  ```

### How the OpenAI package is laid out

`plugins/audiopod-studio` serves both hosts, so one set of skills can't drift:

| File | Used by |
|---|---|
| `.claude-plugin/plugin.json` | Claude |
| `.codex-plugin/plugin.json` | OpenAI (listing metadata; points at `./.mcp.json` and `./skills/`). Named `audiopod-studio` here to match the marketplace entry; the ZIP build names it `audiopod` for the OpenAI listing |
| `.mcp.json` | Both |
| `skills/` | Both (kept host-neutral; CI fails on host-specific wording) |
| `commands/`, `evals/`, `README.md` | Claude only, left out of the OpenAI ZIP |

Build the upload for the OpenAI plugin portal with:

```
scripts/build-openai-zip.sh
```

It writes `dist/audiopod-openai.zip` (git-ignored). It refuses symlinks, hidden
files under `skills/`, and anything that resolves outside the plugin. It also
fails if a `SKILL.md` is over 256 KiB, a skill is over 5 MiB, or the archive is
over 8 MiB. These size limits are our own conservative ones, not OpenAI's.
OpenAI documents 100 MB compressed, 512 MiB extracted, and 100 MiB per archive
entry ([submission error reference](https://developers.openai.com/plugins/deploy/submission-errors)).

On every pull request, CI (`.github/workflows/ci.yml`) validates both Claude
plugins, checks the OpenAI manifest's fields, limits, and URLs in the source
tree and in the built ZIP, and runs negative tests for those checks
(`tests/test_ci_checks.py`).

## What gets sent where

Audio and text you send through these plugins go to AudioPod's servers
(`mcp.audiopod.ai` and `api.audiopod.ai`) for processing. Jobs use credits from
the AudioPod account you connected; see <https://audiopod.ai/pricing>. Outputs are stored
under AudioPod's retention policy: <https://audiopod.ai/privacy>.

## Docs and support

- Documentation: <https://docs.audiopod.ai>
- Support: <https://audiopod.ai/support> or support@audiopod.ai

## License

MIT. See [LICENSE](LICENSE).
