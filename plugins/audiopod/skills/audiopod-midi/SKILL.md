---
name: audiopod-midi
description: Use when the user wants to convert a recording of a melody, instrument, or song into MIDI with AudioPod. Trigger phrases include "audio to MIDI", "convert this to MIDI", "transcribe to notation", "get the notes of this track", "MIDI of the piano part".
---

# Convert audio to MIDI

Audio to MIDI turns a recording the user already has into MIDI files: one
multitrack MIDI plus one per transcribed part. The result is MIDI, not audio.

## Tool

`audio_to_midi` on the `audiopod` MCP server.

| Argument | Required | Notes |
|---|---|---|
| `file_url` | yes | Where the recording lives (see "Supplying the file") |
| `stems` | no | Array of `vocals`, `bass`, `guitar`, `piano`: which separated parts to transcribe |
| `engine` | no | `general` (default), `piano`, or `vocal` |
| `tempo_bpm` | no | Tempo in beats per minute, 30 to 300, if the user knows it |

The `piano` and `vocal` specialist engines require a higher plan. If the
account does not have it, the tool says so: relay that plainly, link the
account page (https://audiopod.ai/dashboard/account), and suggest the
`general` engine instead.

## Supplying the file

The tool takes a URL that AudioPod's servers fetch. It cannot read a file on
the user's computer.

- **A previous AudioPod job's output**: pass a job reference such as
  `job:separate_stems:1234`.
- **A public link**: pass the URL exactly as the user gave it, query string
  included.
- **A local file**: ask for a link AudioPod can download (for example a share
  link from cloud storage), or point them to https://audiopod.ai to upload it.

If the user hasn't given a link yet, ask for one before calling the tool.
Never construct, guess, or edit a URL.

Only process audio the user has the rights to use.

## The async pattern (important)

`audio_to_midi` returns a **job id**, not the MIDI.

1. Call `audio_to_midi` and note the job id.
2. Call `check_job_status` with that `job_id` and `tool: "audio_to_midi"`.
3. While the status is `PENDING` or `PROCESSING`, keep calling
   `check_job_status` in the same response until it finishes (see the polling
   loop in the audiopod-jobs skill); never end your reply promising to check
   later.
4. When `COMPLETED`, hand back the "Multitrack MIDI" link first, then each
   "MIDI (<stem>)" link, quoted exactly. Say the links expire after about an
   hour. They are files to download and open in a DAW or notation tool.
5. When `FAILED`, report the error from the result and suggest a fix.

Never invent a URL, and never say the MIDI is ready before `check_job_status`
reports `COMPLETED`.

## Errors

- **Insufficient credits (402)**: tell the user the account needs more credits
  and link https://audiopod.ai/pricing. Do not retry.
- **Unauthorized**: the AudioPod connection has expired or been disconnected; ask the user to reconnect it with /mcp, select AudioPod, then Authenticate.
- Never quote prices or credit amounts. Link https://audiopod.ai/pricing.
