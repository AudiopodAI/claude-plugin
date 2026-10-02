---
name: audiopod-audio-cleanup
description: Use when the user wants to clean up or repair audio with AudioPod - remove background noise, hiss, hum, wind, or room tone; split a conversation, interview, or podcast into one track per speaker; or convert audio or video to another format (MP3, WAV, FLAC, OGG, M4A, AAC). Trigger phrases include "remove the noise", "clean up this recording", "split by speaker", "isolate the guest", "convert to mp3", "extract the audio from this video".
---

# Clean up, separate, and convert audio

Three AudioPod tools for fixing and preparing recordings. Each one starts a
job; see "The async pattern" below.

## Tools

### `denoise_audio` - remove background noise

| Argument | Required | Notes |
|---|---|---|
| `file_url` | yes | The noisy recording |

Removes hiss, hum, wind, traffic, and room tone while keeping the voice.

### `separate_speakers` - one track per speaker

| Argument | Required | Notes |
|---|---|---|
| `file_url` | yes | A recording with several people talking |
| `num_speakers` | no | Exact speaker count, if known. Leave unset to auto-detect |

Set `num_speakers` whenever the user knows it ("me and one guest" is 2): a
known count is more accurate, especially with similar voices. Works best when
people take turns, as in interviews, meetings, and podcasts.

### `convert_media` - change format

| Argument | Required | Notes |
|---|---|---|
| `file_url` | yes | The audio or video file |
| `output_format` | yes | `mp3`, `wav`, `flac`, `ogg`, `m4a`, or `aac` |
| `quality` | no | `low`, `medium`, `high` (default), or `lossless` |

Use `flac` or `wav` with `lossless` for editing or archiving, `mp3` or `m4a`
with `high` for sharing. Converting a video to an audio format extracts its
soundtrack.

## Supplying the file

The tools take a URL that AudioPod's servers fetch. They cannot read a file on
the user's computer.

- **A previous AudioPod job's output**: pass a job reference naming the tool
  that made it, such as `job:denoise_audio:1234`. Use this to chain steps.
- **A public link**: pass the URL exactly as the user gave it.
- **A local file**: ask for a link AudioPod can download, or point them to
  https://audiopod.ai to upload it.

Never construct, guess, or edit a URL.

## Chaining

Common sequences, each step feeding the next by job reference:

- Noisy interview to clean transcript: `denoise_audio`, then
  `transcribe_audio` with `file_url: "job:denoise_audio:<id>"`.
- Podcast to per-speaker tracks: `denoise_audio`, then `separate_speakers`.
- Video to stems: `convert_media` to `wav`, then `separate_stems`.

Wait for each job to reach `COMPLETED` before starting the next one.

## The async pattern (important)

Each tool returns a **job id**, not the finished audio.

1. Call the tool and note the job id.
2. Call `check_job_status` with that `job_id` and `tool` set to the tool name
   (`denoise_audio`, `separate_speakers`, or `convert_media`).
3. While `PENDING` or `PROCESSING`, tell the user it is running and check again
   after a short wait.
4. When `COMPLETED`, give every output URL in the result, quoted exactly. For
   `separate_speakers` there is one URL per speaker.
5. When `FAILED`, report the error message and suggest a fix.

## Errors

- **Insufficient credits (402)**: tell the user and link
  https://audiopod.ai/pricing. Do not retry.
- **Missing scope**: these tools need `audio:write`, and polling needs
  `audio:read`. Keys are managed at
  https://audiopod.ai/dashboard/account/api-keys.
- Never quote prices or credit amounts. Link https://audiopod.ai/pricing.
