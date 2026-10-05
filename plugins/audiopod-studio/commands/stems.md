---
description: Split a track into stems (vocals, drums, bass, and more) with AudioPod
argument-hint: "<file-url> [4stem|6stem|2stem_vocals|2stem_other]"
---

Separate this track into stems with AudioPod: $ARGUMENTS

Follow the `audiopod-stems` skill. Call the `separate_stems` tool with the URL exactly as given and the mode named above (default `4stem`; use `2stem_vocals` for an acapella or vocal removal). Then poll `check_job_status` until the job is `COMPLETED` or `FAILED`, and list every stem link with its label. If no URL was given, ask for one. On an insufficient-credits error, link https://audiopod.ai/pricing.
