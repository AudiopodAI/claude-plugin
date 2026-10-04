# AudioPod plugins for Claude

This repository is a Claude Code plugin marketplace that connects Claude to
[AudioPod](https://audiopod.ai)'s audio tools through AudioPod's hosted MCP
server. Ask Claude to transcribe a recording, split a song into stems, clean up
a noisy interview, or separate a podcast by speaker, and it runs the job on
your AudioPod account and hands back the results.

## Plugins

| Plugin | What it includes |
|---|---|
| `audiopod` | The full AudioPod toolkit: transcription, stem separation, noise removal, speaker separation, format conversion, voiceover, music, and voice tools |
| `audiopod-transcribe` | Transcription and audio processing only: transcription, stem separation, noise removal, speaker separation, and format conversion |

Install one of them, not both.

## Install

In Claude Code:

```
/plugin marketplace add AudiopodAI/claude-plugin
/plugin install audiopod@audiopod
```

or, for the transcription and audio-processing plugin:

```
/plugin install audiopod-transcribe@audiopod
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

This is added separately from the plugin (use `https://mcp.audiopod.ai/core` for the transcribe plugin's tool set).

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
