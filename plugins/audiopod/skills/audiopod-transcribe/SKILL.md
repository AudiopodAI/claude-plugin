---
name: audiopod-transcribe
description: Use when the user wants to transcribe audio or video with AudioPod, turn a recording into text, get a transcript of a podcast, interview, meeting, or lecture, make subtitles or captions (SRT or VTT), or find out who said what (speaker labels). Trigger phrases include "transcribe this", "get me a transcript", "make subtitles", "speech to text", "caption this video".
---

# Transcribe audio with AudioTranscribe

AudioTranscribe is AudioPod's speech-to-text engine. It handles 100+ languages,
adds timestamps, and can label each speaker.

## Tool

`transcribe_audio` on the `audiopod` MCP server.

| Argument | Required | Notes |
|---|---|---|
| `file_url` | yes | Where the audio or video lives (see "Supplying the file") |
| `language` | no | Language code such as `en`, `es`, `ja`. Leave unset to auto-detect |
| `diarize` | no | `true` to label speakers. Default `false` |
| `format` | no | `text` (default), `srt`, `vtt`, or `json` |

## Supplying the file

The tool takes a URL that AudioPod's servers fetch. It cannot read a file on
the user's computer.

- **A previous AudioPod job's output**: pass a job reference such as
  `job:denoise_audio:1234`. This is the preferred form when chaining jobs.
- **A public link**: pass the URL exactly as the user gave it, query string
  included.
- **A local file**: ask the user for a link AudioPod can download (for example
  a share link from their cloud storage), or point them to the AudioPod
  dashboard at https://audiopod.ai to upload it.

If the user hasn't given a link yet, ask for one before calling the tool.
Never construct, guess, shorten, or edit a URL. A URL that neither the user nor
an earlier tool result supplied is rejected.

## Good defaults

- Speaker labels: set `diarize: true` unless the user says there is only one
  speaker (interviews, podcasts, and meetings always need it).
- Subtitles for a video: `format: "srt"` (or `"vtt"` for web players).
- Analysis or quoting by timestamp: `format: "json"`.
- Plain reading copy: leave `format` at `text`.
- Set `language` only when the user tells you, or it is obvious from context.

## The async pattern (important)

`transcribe_audio` returns a **job id**, not the transcript. The first response
is a receipt.

1. Call `transcribe_audio` and note the job id in the result.
2. Call `check_job_status` with `job_id` set to that id and
   `tool: "transcribe_audio"`.
3. While the status is `PENDING` or `PROCESSING`, tell the user it is still
   running and keep calling
   `check_job_status` in the same response until it finishes (see the polling
   loop in the audiopod-jobs skill); never end your reply promising to check later. Longer recordings take longer.
4. When the status is `COMPLETED`, give the user the transcript text from the
   result `message`. For subtitles or a specific format, see "Getting SRT, VTT
   or TXT" below.
5. When the status is `FAILED`, report the error message from the result and
   suggest a fix (a reachable URL, a supported format, a shorter file).

Never tell the user the transcript is ready before `check_job_status` says
`COMPLETED`.

## Getting SRT, VTT or TXT

The `format` argument on `transcribe_audio` chooses how the job is produced.
`include_format` on `check_job_status` is how you read the finished result as
SRT, VTT or TXT. If the user asked for SRT up front, pass `format: "srt"` when
starting the job AND use `include_format: "srt"` when reading the result.

When the user wants subtitles or a specific format:

1. Wait until the job is `COMPLETED`.
2. Call `check_job_status` with `tool: "transcribe_audio"`, the `job_id`, and
   `include_format` set to `srt`, `vtt` or `txt`.
3. Give the user the formatted text returned in the result `message`.
4. In Claude Code, or whenever a file tool is available, offer to save it as a
   `.srt`, `.vtt` or `.txt` file named after the source (for example
   `interview.srt`).
5. If `transcript_formatted_truncated` is true, say the output was cut at
   20,000 characters and offer to transcribe in shorter pieces.

Never invent or quote API download URLs. The only link in a result is a
presigned JSON link; tell the user it expires after about an hour.

## After it finishes

- Offer a short summary, action items, or chapter markers when the user wants
  them. Work from the real transcript text, never from memory.
- To clean up a noisy recording first, see the `audiopod-audio-cleanup` skill
  and pass that job's output as `job:denoise_audio:<id>`.

## Errors

- **Insufficient credits (402)**: the account does not have enough credits for
  this job. Tell the user and link https://audiopod.ai/pricing. Do not retry.
- **Missing scope**: the AudioPod connection doesn't include the `transcribe` or `audio:read` permissions; reconnect AudioPod (/mcp, select AudioPod, then Authenticate) to grant them.
- **Unauthorized**: the AudioPod connection has expired or been disconnected; ask the user to reconnect it with /mcp, select AudioPod, then Authenticate.
- Never quote prices or credit amounts. Link https://audiopod.ai/pricing.
