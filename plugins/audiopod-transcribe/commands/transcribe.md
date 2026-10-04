---
description: Transcribe an audio or video URL with AudioPod, with speaker labels and optional subtitles
argument-hint: <file-url> [srt|vtt|json] [language]
---

Transcribe this with AudioPod: $ARGUMENTS

Follow the `audiopod-transcribe` skill. Call the `transcribe_audio` tool with the URL exactly as given, `diarize: true` unless the user says there is only one speaker, and the format or language named above if any. Then poll `check_job_status` until the job is `COMPLETED` or `FAILED`. If a format (srt, vtt) was named, pass it as `format` when starting the job, and once the job is `COMPLETED` call `check_job_status` again with `tool: "transcribe_audio"`, the `job_id`, and `include_format` set to `srt`, `vtt` or `txt`, then return the formatted text from the result `message` (offer to save it as a file named after the source, such as interview.srt, when a file tool is available). If `transcript_formatted_truncated` is true, say the output was cut at 20,000 characters and offer to transcribe in shorter pieces. Never invent download URLs; the only link is a presigned JSON link that expires after about an hour. If no URL was given, ask for one. On an insufficient-credits error, link https://audiopod.ai/pricing.
