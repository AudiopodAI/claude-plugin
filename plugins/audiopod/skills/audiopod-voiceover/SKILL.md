---
name: audiopod-voiceover
description: Use when the user wants AudioPod to turn text into spoken audio - a voiceover, narration, read-aloud, explainer audio, or an audio version of an article or script, in any of 200+ languages, with a catalog voice or their own custom voice. Trigger phrases include "text to speech", "read this aloud", "make a voiceover", "narrate this", "TTS".
---

# Text to speech with AudioPod

AudioPod narrates text in 200+ languages with 380+ catalog voices, or with a
custom voice the user created (see the `audiopod-voice` skill).

## Tool

`text_to_speech` on the `audiopod` MCP server.

| Argument | Required | Notes |
|---|---|---|
| `text` | yes | Up to 20,000 characters per call |
| `voice_id` | no | AudioPod catalog ID (integer, preferred) or voice slug. Omit for the default voice |
| `language` | no | Language code such as `en`, `es`, `fr`, `ja`. Default `en` |
| `speed` | no | 0.5 to 2.0. Default 1.0 |

## Before you call

- **Length**: never silently truncate. If the text is over 20,000 characters,
  tell the user and split it at paragraph or section breaks into several calls,
  numbering the parts.
- **Voice**: use the voice the user names. If they gave none, the default voice
  is fine; mention that they can pick another at https://audiopod.ai.
- **Language**: set `language` to match the text. A Spanish script needs
  `language: "es"`.
- **Prepare the text**: write numbers, dates, and abbreviations the way they
  should be spoken when ambiguity matters ("2026" as a year, "Dr." as
  "Doctor"). Remove markdown symbols, URLs, and code that should not be read.
- **Speed**: leave at 1.0 unless asked. Use 0.9 for dense explainer content.

## The async pattern (important)

`text_to_speech` returns a **job id**, not audio.

1. Call `text_to_speech` and note the job id.
2. Call `check_job_status` with that `job_id` and `tool: "text_to_speech"`.
3. While `PENDING` or `PROCESSING`, tell the user it is rendering and keep calling
   `check_job_status` in the same response until it finishes (see the polling
   loop in the audiopod-jobs skill); never end your reply promising to check later.
4. When `COMPLETED`, give the audio URL from the result, quoted exactly.
5. When `FAILED`, report the error and suggest a fix (shorter text, a
   different voice).

For multi-part narration, submit the parts in order and report each URL with
its part number.

## Errors

- **Insufficient credits (402)**: tell the user and link
  https://audiopod.ai/pricing. Do not retry. For long scripts, suggest
  confirming the account balance before submitting every part.
- **Missing scope**: the connection needs `voice:synthesize` and `audio:write`. Reconnect AudioPod (/mcp, select AudioPod, then Authenticate) to grant them.
- **Unknown voice**: ask the user to confirm the voice, or omit `voice_id`.
- Never quote prices or credit amounts. Link https://audiopod.ai/pricing.
