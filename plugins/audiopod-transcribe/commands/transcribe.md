---
description: Transcribe an audio or video URL with AudioPod, with speaker labels and optional subtitles
argument-hint: <file-url> [srt|vtt|json] [language]
---

Transcribe this with AudioPod: $ARGUMENTS

Follow the `audiopod-transcribe` skill. Call the `transcribe_audio` tool with the URL exactly as given, `diarize: true` unless the user says there is only one speaker, and the format or language named above if any. Then poll `check_job_status` until the job is `COMPLETED` or `FAILED`, and return the transcript or output links. If no URL was given, ask for one. On an insufficient-credits error, link https://audiopod.ai/pricing.
