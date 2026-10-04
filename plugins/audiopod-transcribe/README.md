# AudioPod Transcribe & Audio Tools for Claude

This plugin connects Claude to AudioPod's transcription and audio-processing
tools through AudioPod's hosted MCP server. Ask in plain language and Claude
starts the job, follows it until it finishes, and gives you the results.

## What you can do

- **Transcribe** audio or video with AudioTranscribe: speaker labels,
  timestamps, and SRT or VTT subtitles in 100+ languages.
- **Split songs into stems** with AudioStems: vocals, drums, bass, piano,
  guitar, and the rest.
- **Remove background noise** such as hiss, hum, wind, and room tone.
- **Separate speakers**: one track per person from an interview, meeting, or
  podcast.
- **Convert formats** between MP3, WAV, FLAC, OGG, M4A, and AAC, including
  extracting the soundtrack from a video.

Slash commands: `/audiopod-transcribe:transcribe`,
`/audiopod-transcribe:stems`, `/audiopod-transcribe:status`.

## Setup

Install the plugin. The first time Claude uses an AudioPod tool it asks you to
connect: choose Connect (or run /mcp, select AudioPod, then Authenticate). A
browser window opens, you sign in to your AudioPod account, review what the
connection can do, and select Allow access. No API key to copy. You can
disconnect at any time from your AudioPod account page.

### Using an API key instead (CI or headless)

Create a key at <https://audiopod.ai/dashboard/account/api-keys> and run:

```
claude mcp add --transport http audiopod https://mcp.audiopod.ai/core --header "X-API-Key: <your key>"
```

This is added separately from the plugin.

## How files are supplied

AudioPod's tools take a link to your audio, which AudioPod downloads. They
cannot read files on your computer directly. Share a link to the file (for
example from cloud storage), or upload it in the AudioPod dashboard. Output
from one job can be passed straight into the next, for example noise removal
followed by transcription.

## Data, credits, and privacy

- **Where your data goes**: audio, video, and text you send through this plugin
  are sent to AudioPod's servers at `mcp.audiopod.ai` and `api.audiopod.ai` for
  processing. Nothing runs locally.
- **Credits**: each job consumes credits from the AudioPod account you connected. Checking a job's status is free. See
  <https://audiopod.ai/pricing>.
- **Retention**: outputs are stored according to AudioPod's retention policy,
  described at <https://audiopod.ai/privacy>.
- Terms of service: <https://audiopod.ai/terms>.

## Support

Docs: <https://docs.audiopod.ai> · Support: <https://audiopod.ai/support> ·
support@audiopod.ai

## License

MIT
