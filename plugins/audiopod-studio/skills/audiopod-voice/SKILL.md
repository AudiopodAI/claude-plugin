---
name: audiopod-voice
description: Use when the user wants AudioPod to create a custom voice from a recording (voice cloning) or to re-voice an existing recording so it sounds like a different speaker (voice changing). Trigger phrases include "clone my voice", "make a custom voice", "use my voice for narration", "change the voice in this recording", "re-voice this audio".
---

# Custom voices and voice changing with AudioPod

Two AudioPod tools: one creates a reusable custom voice from a sample, the
other converts a recording into a different voice while keeping the words and
timing.

## Consent first

Only clone or convert the user's own voice, or a voice whose speaker has given
the user explicit permission to use it. Decline any request to clone or
imitate a public figure, a celebrity, or any other person without that
person's consent, and explain why.

Before calling `clone_voice`, ask the user to confirm that the sample is their
own voice or that they have the speaker's permission. Pass
`consent_confirmed: true` only after the user has explicitly confirmed it in
the conversation; never assume or infer it. Without that confirmation the
tool refuses and nothing is cloned. If the user cannot confirm, do not clone.

## Tools

### `clone_voice` - create a custom voice

| Argument | Required | Notes |
|---|---|---|
| `file_url` | yes | A clean sample of one speaker, at least 10 seconds |
| `voice_name` | yes | A name the user will recognise later |
| `description` | no | Notes on the voice (tone, accent, use) |
| `consent_confirmed` | yes | `true` only after the user confirmed it is their own voice or they have the speaker's permission |

For the best result the sample should be one speaker only, little background
noise, no music, and natural speech. If the sample is noisy, run
`denoise_audio` first (see `audiopod-audio-cleanup`) and pass
`job:denoise_audio:<id>`.

The finished voice can then be used with `text_to_speech` (see
`audiopod-voiceover`) or `change_voice`.

### `change_voice` - re-voice a recording

| Argument | Required | Notes |
|---|---|---|
| `file_url` | yes | The recording to convert |
| `voice_id` | yes | Target voice: AudioPod voice UUID, catalog ID, or slug |
| `pitch_shift` | no | Semitones, -12 to +12. Default 0 |

The words, pacing, and delivery of the original stay; only the voice changes.
Leave `pitch_shift` at 0 unless the result sounds off, then try small steps.

## Supplying the file

Both tools take a URL that AudioPod's servers fetch. They cannot read a file on
the user's computer. Pass a job reference such as `job:denoise_audio:1234`, or
a public URL exactly as the user gave it. For a local file, ask for a link
AudioPod can download, or point them to https://audiopod.ai to upload it.
Never construct, guess, or edit a URL.

## The async pattern (important)

Both tools return a **job id**.

1. Call the tool and note the job id.
2. Call `check_job_status` with that `job_id` and `tool` set to `clone_voice`
   or `change_voice`.
3. While `PENDING` or `PROCESSING`, tell the user it is working and keep calling
   `check_job_status` in the same response until it finishes (see the polling
   loop in the audiopod-jobs skill); never end your reply promising to check later.
4. When `COMPLETED`: for `clone_voice`, report the new voice's name and ID so
   the user can use it; for `change_voice`, give the output URL, quoted
   exactly.
5. When `FAILED`, report the error and suggest a fix (a longer or cleaner
   sample, a different target voice).

## Errors

- **Insufficient credits (402)**: tell the user and link
  https://audiopod.ai/pricing. Do not retry.
- **Missing scope**: `clone_voice` needs `voice:clone`; `change_voice` needs
  `voice:synthesize`; both need `audio:write`. Reconnect AudioPod from the app's connector or MCP settings to grant them.
- **Consent required**: `clone_voice` was called without
  `consent_confirmed: true`. Ask the user to confirm consent, then call it
  again; if they cannot, do not clone.
- **Voice limit reached**: the account's custom voice slots are full. Link
  the account page, https://audiopod.ai/dashboard/account.
- Never quote prices or credit amounts. Link https://audiopod.ai/pricing.
