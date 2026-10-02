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

Claude Code asks for your AudioPod API key when the plugin is enabled. Get one
at [audiopod.ai](https://audiopod.ai) (dashboard, then API keys, or go straight
to <https://audiopod.ai/dashboard/account/api-keys>). The key is stored in your
system's secure credential store, not in a settings file.

## What gets sent where

Audio and text you send through these plugins go to AudioPod's servers
(`mcp.audiopod.ai` and `api.audiopod.ai`) for processing. Jobs use credits from
your AudioPod account; see <https://audiopod.ai/pricing>. Outputs are stored
under AudioPod's retention policy: <https://audiopod.ai/privacy>.

## Docs and support

- Documentation: <https://docs.audiopod.ai>
- Support: <https://audiopod.ai/support> or support@audiopod.ai

## License

MIT. See [LICENSE](LICENSE).
