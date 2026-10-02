---
name: audiopod-music
description: Use when the user wants AudioPod to create music - a song with lyrics, an instrumental, a beat, a jingle, background music for a video or podcast, or a rap track. Trigger phrases include "make a song", "compose music", "create a beat", "background music", "write and sing these lyrics", "instrumental track".
---

# Create music with AudioMusic

AudioMusic is AudioPod's music engine. It makes full songs, instrumentals, and
rap from a text description, with optional lyrics.

## Tool

`generate_music` on the `audiopod` MCP server.

| Argument | Required | Notes |
|---|---|---|
| `prompt` | yes | Genre, mood, instruments, tempo, era, use case |
| `lyrics` | no | The words to sing. Omit for an instrumental or AudioPod-written lyrics |
| `duration` | no | Seconds, 30 to 300. Default 120 |
| `task_type` | no | `text2music` (default), `lyric2vocals`, `text2rap`, `text2instrumental` |

## Choosing `task_type`

| The user wants | `task_type` |
|---|---|
| A general song or track | `text2music` |
| Their lyrics sung, vocals front and centre | `lyric2vocals` |
| Rap or hip-hop vocals | `text2rap` |
| No vocals at all (beds, beats, underscore) | `text2instrumental` |

## Writing a good prompt

Be specific and concrete. Cover:

- **Genre and era**: "90s boom-bap", "modern synthwave", "acoustic folk".
- **Mood**: "warm and hopeful", "tense", "laid-back".
- **Instruments**: "fingerpicked guitar, soft piano, brushed drums".
- **Tempo**: "slow, around 70 BPM", "upbeat 120 BPM".
- **Use**: "podcast intro bed, no vocals" helps the result fit.

Avoid naming real artists or copying existing songs; describe the sound
instead.

## Lyrics

- Mark sections with `[verse]`, `[chorus]`, `[bridge]` on their own lines.
- Keep lines short and singable. Match the lyric length to `duration`.
- If the user asks you to write lyrics, draft them, show them, and get a yes
  before spending credits.

## The async pattern (important)

`generate_music` returns a **job id**, not audio.

1. Call `generate_music` and note the job id.
2. Call `check_job_status` with that `job_id` and `tool: "generate_music"`.
3. While `PENDING` or `PROCESSING`, tell the user it is being made and check
   again after a short wait. A track usually takes one to three minutes.
4. When `COMPLETED`, give every output URL from the result (audio, and lyrics
   if present), quoted exactly.
5. When `FAILED`, report the error and suggest a fix (a simpler prompt, a
   shorter duration).

Each call makes a new track and spends credits again, so do not resubmit to
"check" a job.

## Errors

- **Insufficient credits (402)**: tell the user and link
  https://audiopod.ai/pricing. Do not retry.
- **Missing scope**: the key needs `music:generate` and `audio:write`. Keys are
  managed at https://audiopod.ai/dashboard/account/api-keys.
- Never quote prices or credit amounts. Link https://audiopod.ai/pricing.
