---
name: audiopod-stems
description: Use when the user wants to split a song into stems with AudioPod, isolate or remove vocals, make an acapella or an instrumental (karaoke) version, or extract the drums, bass, guitar, or piano from a track. Trigger phrases include "separate stems", "remove the vocals", "isolate the drums", "make an acapella", "split this track".
---

# Separate stems with AudioStems

AudioStems is AudioPod's stem separation engine. It splits a mixed track into
its parts: vocals, drums, bass, piano, guitar, and the rest.

## Tool

`separate_stems` on the `audiopod` MCP server.

| Argument | Required | Notes |
|---|---|---|
| `file_url` | yes | Where the track lives (see "Supplying the file") |
| `mode` | no | `4stem` (default), `6stem`, `2stem_vocals`, or `2stem_other` |

## Picking a mode

| The user wants | Mode |
|---|---|
| Vocals, drums, bass, everything else | `4stem` |
| The same plus piano and guitar | `6stem` |
| An acapella (vocals only) or to remove the vocals | `2stem_vocals` |
| Just the instrumental bed | `2stem_other` |

When unsure, use `4stem`: it covers the most common requests.

## Supplying the file

The tool takes a URL that AudioPod's servers fetch. It cannot read a file on
the user's computer.

- **A previous AudioPod job's output**: pass a job reference such as
  `job:convert_media:1234`.
- **A public link**: pass the URL exactly as the user gave it, query string
  included.
- **A local file**: ask for a link AudioPod can download (for example a share
  link from cloud storage), or point them to https://audiopod.ai to upload it.

Never construct, guess, or edit a URL.

Only process audio the user has the rights to use.

## The async pattern (important)

`separate_stems` returns a **job id**, not the stems.

1. Call `separate_stems` and note the job id.
2. Call `check_job_status` with that `job_id` and `tool: "separate_stems"`.
3. While the status is `PENDING` or `PROCESSING`, tell the user it is still
   working and check again after a short wait. A full song usually takes a
   few minutes.
4. When `COMPLETED`, list every stem URL in the result with its label (vocals,
   drums, and so on), quoted exactly.
5. When `FAILED`, report the error from the result and suggest a fix.

Never say the stems are ready before `check_job_status` reports `COMPLETED`.

## Errors

- **Insufficient credits (402)**: tell the user the account needs more credits
  and link https://audiopod.ai/pricing. Do not retry.
- **Missing scope**: the key needs `stems:separate` and `audio:write`. Keys are
  managed at https://audiopod.ai/dashboard/account/api-keys.
- **Unauthorized**: ask the user to check the API key in the plugin settings.
- Never quote prices or credit amounts. Link https://audiopod.ai/pricing.
