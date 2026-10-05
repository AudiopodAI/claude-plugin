---
description: Convert a recording to MIDI with AudioPod
argument-hint: "<file-url> [general|piano|vocal]"
---

Convert this recording to MIDI with AudioPod: $ARGUMENTS

Follow the `audiopod-midi` skill. Call the `audio_to_midi` tool with the URL exactly as given and the engine named above if any (default `general`). Then poll `check_job_status` with `tool: "audio_to_midi"` until the job is `COMPLETED` or `FAILED`, and return the Multitrack MIDI link first, then each per-stem MIDI link. If no URL was given, ask for one. On an insufficient-credits error, link https://audiopod.ai/pricing.
