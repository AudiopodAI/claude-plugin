# AudioPod Studio for Claude

The AudioPod Studio plugin connects Claude to AudioPod's audio tools through
AudioPod's hosted MCP server. Ask in plain language and Claude picks the right
tool, starts the job, follows it until it finishes, and gives you the output
links.

## What you can do

- **Transcribe** audio or video with AudioTranscribe: speaker labels,
  timestamps, and SRT or VTT subtitles in 100+ languages.
- **Split songs into stems** with AudioStems: vocals, drums, bass, piano,
  guitar, and the rest; acapellas and instrumentals.
- **Convert audio to MIDI**: a melody, instrument, or song becomes MIDI files
  for your DAW or notation tool.
- **Clean up recordings**: remove background noise, split a conversation into
  one track per speaker, and convert between audio and video formats.
- **Create voiceovers** from text in 200+ languages.
- **Create music**: songs, instrumentals, and beats from a description, or
  compose a song you can reshape in plain words before it is recorded.
- **Custom voices**: create a voice from a sample you have the rights to, or
  re-voice a recording.

Slash commands: `/audiopod-studio:transcribe`, `/audiopod-studio:stems`, `/audiopod-studio:midi`,
`/audiopod-studio:tts`, `/audiopod-studio:status`.

Studio adds music, text to speech, and voice features on top of the
transcription and audio-processing tools in the `audiopod` plugin. Install only
one AudioPod plugin, not both: both register an MCP server named `audiopod`, so
installing both would duplicate the tools.

## Setup

Install with `/plugin install audiopod-studio@audiopod`. The first time Claude uses an AudioPod tool it asks you to
connect: choose Connect (or run /mcp, select AudioPod, then Authenticate). A
browser window opens, you sign in to your AudioPod account, review what the
connection can do, and select Allow access. No API key to copy. You can
disconnect at any time from your AudioPod account page.

### Using an API key instead (CI or headless)

Create a key at <https://audiopod.ai/dashboard/account/api-keys> and run:

```
claude mcp add --transport http audiopod https://mcp.audiopod.ai --header "X-API-Key: <your key>"
```

This is added separately from the plugin.

## How files are supplied

AudioPod's tools take a link to your audio, which AudioPod downloads. They
cannot read files on your computer directly. Share a link to the file (for
example from cloud storage), or upload it in the AudioPod dashboard. Output
from one job can be passed straight into the next.

## Data, credits, and privacy

- **Where your data goes**: audio, video, and text you send through this plugin
  are sent to AudioPod's servers at `mcp.audiopod.ai` and `api.audiopod.ai` for
  processing. Nothing runs locally.
- **Credits**: each job consumes credits from the AudioPod account you connected. Checking a job's status, or asking how many credits you have left and which plan you are on, is free. See
  <https://audiopod.ai/pricing>.
- **Retention**: outputs are stored according to AudioPod's retention policy,
  described at <https://audiopod.ai/privacy>.
- Terms of service: <https://audiopod.ai/terms>.

## Support

Docs: <https://docs.audiopod.ai> · Support: <https://audiopod.ai/support> ·
support@audiopod.ai

## License

MIT
