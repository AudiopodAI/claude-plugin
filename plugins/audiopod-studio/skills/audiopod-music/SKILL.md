---
name: audiopod-music
description: Use when the user wants AudioPod to create music - a song, an instrumental, a beat, a jingle, background music for a video or podcast, or a rap or hip hop track - or wants to write a song they can shape and tweak before it is recorded (melody, chords, sections, sheet music). Trigger phrases include "make a song", "compose music", "create a beat", "make a hip hop track", "background music", "write and sing these lyrics", "instrumental track", "compose a song I can tweak", "let me see the melody first", "change the chorus".
---

# Create music with AudioMusic

AudioMusic is AudioPod's music engine. It makes full songs, rap and hip hop
tracks, instrumentals, and beats from a text description. When the user does
not bring lyrics, AudioPod writes them from the description.

It works in two modes:

- **Song** (`generate_music`) is the default for everything. It honors a
  requested length and returns synced lyrics.
- **Score-first** (`compose_music` → `revise_music_score` →
  `record_music_score`) is for when the user wants to see or shape the
  composition itself before it is recorded.

## Choose the tool

| The user wants | Tool |
|---|---|
| A song from a description ("a sad indie song about rain") | `generate_music` with `prompt` only. AudioPod writes the lyrics |
| Their own (or approved) lyrics performed | `generate_music` with `prompt` + `lyrics` |
| A beat, instrumental, or background bed | `generate_music` with `instrumental: true` |
| An exact length, or synced lyrics | `generate_music` |
| "Write me a song I can tweak", "let me see the melody / chords / sections first", sheet music | `compose_music` |
| A change to a composed song in plain words ("brighter chorus", "down a key") | `revise_music_score` |
| Record the composed song | `record_music_score` |
| The same tune with a new style or new words | `record_music_score` with `style` / `lyrics` |

When in doubt, use `generate_music`.

## Song mode: `generate_music`

| Argument | Required | Notes |
|---|---|---|
| `prompt` | yes | A description of the music: genre, mood, tempo, instruments, voice, what the song is about. It is never sung |
| `lyrics` | no | Only words the user wrote or approved. They are performed word for word. Leave out and AudioPod writes the lyrics |
| `instrumental` | no | `true` for beats, instrumentals, backing tracks, and background music with no vocals |
| `vocal_language` | no | ISO 639-1 code (`en`, `es`, `hi`, `ja`...) for the sung lyrics. Set it only when the user names a language |
| `duration` | no | Seconds, 10 to 600. Leave out unless the user asked for a length |
| `task_type` | no | Usually leave out. `text2rap` only with the user's own lyrics to be rapped |

Every track uses the best quality on every plan; there is no quality setting
to choose (a `quality` value is accepted and ignored).

Rules:

- **A description is enough.** Do not write lyrics yourself just to fill the
  `lyrics` field, and never put the description into `lyrics`. Hip hop and rap
  with no user lyrics are just a description: say "hip hop" or "rap" in the
  prompt and leave `lyrics` and `task_type` out.
- **Pass `lyrics` only when the user supplied them or approved a draft.** If
  the user asks you to write the lyrics, draft them, show them, and get a yes
  before spending credits.
- **No vocals means `instrumental: true`.** Words like "beat", "instrumental",
  "backing track", "background music", or "no vocals" all mean this.
- **Language**: set `vocal_language` when the user names one ("in Spanish",
  "a Hindi song"). Otherwise leave it out.

## Score-first mode: the compose loop

Use it only when the user wants to shape the tune before it is recorded.

1. **Write** — `compose_music` with `style` plus **either** `description`
   (AudioPod writes the lyrics; optional `target_seconds` 30 to 300 and
   `language`) **or** the user's own `lyrics`. Never both. It returns a job id
   for a score with no audio yet. Takes about 10 seconds.
   Each call starts a new paid job; confirm with the user before running it again.
2. **Show** — once `check_job_status` (with `tool: "compose_music"`) says
   `COMPLETED`, call `get_music_score` (read-only) and describe the song to the
   user in plain words: key, tempo, sections, length.
3. **Revise** — for every change the user asks for, call
   `revise_music_score` with the score's `job_id` and the request as
   `instruction`, in the user's own words. Narrow it with `section`
   ("chorus") or `bars` (`{"start": 5, "end": 8}`) when the user names one.
   Each revision returns a **new** job id for the new score; use that id next.
   Each call starts a new paid job; confirm with the user before running it again.
   Repeat as often as the user likes.
4. **Record** — tell the user that recording starts a new paid job and how
   long the track will be (`get_music_score` reports the length), get a
   clear yes, then call `record_music_score` with the latest score's
   `job_id`. Takes one to three minutes.

Rules:

- **Always use `revise_music_score` for changes.** Never write or edit the
  notation yourself, and do not pass `abc` unless the user handed you a
  complete score of their own.
- **Confirm before recording.** Each call starts a new paid job; confirm with the user before running it again.
- If `revise_music_score` says plain-English changes are not available on the
  account yet, say so and offer to record the score as it is.
- If a revision is refused because it could not be made safely, nothing was
  charged: suggest rewording it or limiting it to one section or a few bars.
- `edit_music_score` is a deprecated name for `record_music_score`; do not
  use it.

## Writing a good prompt or style

Be specific and concrete. Cover:

- **Genre and era**: "90s boom-bap", "modern synthwave", "acoustic folk".
- **Mood**: "warm and hopeful", "tense", "laid-back".
- **Instruments**: "fingerpicked guitar, soft piano, brushed drums".
- **Tempo**: "slow, around 70 BPM", "upbeat 120 BPM".
- **Voice and theme** (for songs): "gravelly male rapper", "a song about
  leaving home".
- **Use**: "podcast intro bed" helps the result fit.

Avoid naming real artists or copying existing songs; describe the sound
instead.

## Lyrics the user gives you

- Mark sections with `[verse]`, `[chorus]`, `[bridge]` on their own lines.
- Keep the user's words as they wrote them.
- In Song mode, if the song must fit a length, set `duration` to match the
  lyrics.

## The async pattern (important)

Every music tool except `get_music_score` returns a **job id**, not audio.

1. Call the tool and note the job id. If the result says AudioPod is writing
   the lyrics, tell the user.
2. Call `check_job_status` with that `job_id` and `tool` set to the tool that
   made the job (`generate_music`, `compose_music`, `revise_music_score` or
   `record_music_score`).
3. While `PENDING` or `PROCESSING`, tell the user it is being made and keep
   calling `check_job_status` in the same response until it finishes (see the
   polling loop in the audiopod-jobs skill); never end your reply promising to
   check later. A recorded track usually takes one to three minutes; a score
   about ten seconds.
4. When `COMPLETED`, give every output URL from the result (audio, and lyrics
   if present), quoted exactly. A written or revised score has no audio yet.
5. When `FAILED`, report the error and suggest a fix (a simpler prompt, a
   shorter duration).

Each call makes a new job and spends credits again, so do not resubmit to
"check" a job.

## Credits

- Never quote prices or credit amounts, in either mode. Link
  https://audiopod.ai/pricing if the user asks.
- Score-first mode: each `compose_music`, `revise_music_score` and
  `record_music_score` call starts a new paid job; confirm with the user
  before running one again, and always before recording.

## Errors

- **Insufficient credits (402)**: tell the user and link
  https://audiopod.ai/pricing. Do not retry.
- **Missing scope**: the connection needs `music:generate` and `audio:write`
  (and `audio:read` to read a score). Reconnect AudioPod from the app's
  connector or MCP settings to grant them.
