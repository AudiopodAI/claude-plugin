---
name: audiopod-music
description: Use when the user wants AudioPod to create music - a song, an instrumental, a beat, a jingle, background music for a video or podcast, or a rap or hip hop track. Trigger phrases include "make a song", "compose music", "create a beat", "make a hip hop track", "background music", "write and sing these lyrics", "instrumental track".
---

# Create music with AudioMusic

AudioMusic is AudioPod's music engine. It makes full songs, rap and hip hop
tracks, instrumentals, and beats from a text description. When the user does
not bring lyrics, AudioPod writes them from the description.

## Tool

`generate_music` on the `audiopod` MCP server.

| Argument | Required | Notes |
|---|---|---|
| `prompt` | yes | A description of the music: genre, mood, tempo, instruments, voice, what the song is about. It is never sung |
| `lyrics` | no | Only words the user wrote or approved. They are performed word for word. Leave out and AudioPod writes the lyrics |
| `instrumental` | no | `true` for beats, instrumentals, backing tracks, and background music with no vocals |
| `vocal_language` | no | ISO 639-1 code (`en`, `es`, `hi`, `ja`...) for the sung lyrics. Set it only when the user names a language |
| `duration` | no | Seconds, 10 to 600. Leave out unless the user asked for a length |
| `quality` | no | `standard` (default) or `premium`. Use `premium` only when the user asks for it |
| `task_type` | no | Usually leave out. See below |

## Pick the request shape

| The user wants | Call |
|---|---|
| A song from a description only ("a hip hop track about late-night drives") | `prompt` only. AudioPod writes the lyrics |
| A song in a particular language | `prompt` + `vocal_language` |
| Their own (or approved) lyrics performed | `prompt` + `lyrics` |
| Their own lyrics rapped | `prompt` + `lyrics` + `task_type: "text2rap"` |
| A beat, instrumental, or background bed | `prompt` + `instrumental: true` |

Rules:

- **A description is enough.** Do not write lyrics yourself just to fill the
  `lyrics` field, and never put the description into `lyrics`. Hip hop and rap
  with no user lyrics are just a description: say "hip hop" or "rap" in the
  prompt and leave `lyrics` and `task_type` out.
- **Pass `lyrics` only when the user supplied them or approved a draft.** If
  the user asks you to write the lyrics, draft them, show them, and get a yes
  before spending credits.
- **No vocals means `instrumental: true`.** Words like "beat", "instrumental",
  "backing track", "background music", or "no vocals" all mean this.
- **Language**: set `vocal_language` when the user names one ("in Spanish",
  "a Hindi song"). Otherwise leave it out.

## Writing a good prompt

Be specific and concrete. Cover:

- **Genre and era**: "90s boom-bap", "modern synthwave", "acoustic folk".
- **Mood**: "warm and hopeful", "tense", "laid-back".
- **Instruments**: "fingerpicked guitar, soft piano, brushed drums".
- **Tempo**: "slow, around 70 BPM", "upbeat 120 BPM".
- **Voice and theme** (for songs): "gravelly male rapper", "a song about
  leaving home".
- **Use**: "podcast intro bed" helps the result fit.

Avoid naming real artists or copying existing songs; describe the sound
instead.

## Lyrics the user gives you

- Mark sections with `[verse]`, `[chorus]`, `[bridge]` on their own lines.
- Keep the user's words as they wrote them.
- If the song must fit a length, set `duration` to match the lyrics.

## The async pattern (important)

`generate_music` returns a **job id**, not audio.

1. Call `generate_music` and note the job id. If the result says AudioPod is
   writing the lyrics, tell the user.
2. Call `check_job_status` with that `job_id` and `tool: "generate_music"`.
3. While `PENDING` or `PROCESSING`, tell the user it is being made and keep calling
   `check_job_status` in the same response until it finishes (see the polling
   loop in the audiopod-jobs skill); never end your reply promising to check later. A track usually takes one to three minutes.
4. When `COMPLETED`, give every output URL from the result (audio, and lyrics
   if present), quoted exactly.
5. When `FAILED`, report the error and suggest a fix (a simpler prompt, a
   shorter duration).

Each call makes a new track and spends credits again, so do not resubmit to
"check" a job.

## Errors

- **Insufficient credits (402)**: tell the user and link
  https://audiopod.ai/pricing. Do not retry.
- **Premium not available on the plan**: tell the user premium needs a paid
  plan (link https://audiopod.ai/pricing) and offer to make it at standard
  quality instead.
- **Missing scope**: the connection needs `music:generate` and `audio:write`. Reconnect AudioPod from the app's connector or MCP settings to grant them.
- Never quote prices or credit amounts. Link https://audiopod.ai/pricing.
