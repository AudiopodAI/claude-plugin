---
description: Turn text into a spoken voiceover with AudioPod
argument-hint: "<text to speak> [voice or language]"
---

Create a voiceover with AudioPod for: $ARGUMENTS

Follow the `audiopod-voiceover` skill. Call the `text_to_speech` tool with the text (split it into parts if it is over 20,000 characters), plus any voice or language the user named. Then poll `check_job_status` until the job is `COMPLETED` or `FAILED`, and return the audio link. If no text was given, ask for it. On an insufficient-credits error, link https://audiopod.ai/pricing.
