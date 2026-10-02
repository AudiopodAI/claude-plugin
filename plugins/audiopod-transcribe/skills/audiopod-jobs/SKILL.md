---
name: audiopod-jobs
description: Use when the user asks about an AudioPod job - whether it is done, where the output is, "any update?", "is it finished?", "what happened to my transcript or stems?" - or when any AudioPod tool has just returned a job id that needs following up. Also use for questions about how AudioPod jobs, credits, and API keys work.
---

# AudioPod jobs, polling, and credits

Every AudioPod tool except `check_job_status` starts a **job** and returns a
job id straight away. The work happens on AudioPod's servers; the finished
output appears later. This skill is how to follow a job to the end.

## Tool

`check_job_status` on the `audiopod` MCP server. Free to call; it only reads.

| Argument | Required | Notes |
|---|---|---|
| `job_id` | no | The exact id an earlier tool result printed in this conversation |
| `tool` | no | The tool that started the job (see list below) |

`tool` is one of: `transcribe_audio`, `separate_stems`, `denoise_audio`,
`separate_speakers`, `convert_media`.

- Know the id: pass `job_id` and `tool`.
- Vague follow-up ("any update?"): call with **no arguments**, or with only
  `tool`. AudioPod resolves the user's most recent job. Do not ask the user for
  an id they do not have.
- **Never guess, invent, or increment a job id.**

## The polling loop

1. Submit the job; note the id and the tool name.
2. Call `check_job_status`.
3. Read `status`:
   - `PENDING` or `PROCESSING`: call `check_job_status` again **in the same
     response**. You cannot come back later on your own, so never end your
     reply with "I'll check again in a moment". Keep checking until the job
     finishes, up to about 15 checks (most jobs finish within a few minutes).
     If it is still running after that, give the user the job id and tool name
     and tell them to ask "any update on my AudioPod job?". The job keeps
     running without you.
   - `COMPLETED`: report every output URL in the result with its label, quoted
     exactly. These links are safe to share with the user.
   - `FAILED`: report the error message and suggest a fix. Failed jobs do not
     keep the credits reserved for them.
4. Never tell the user a job is done before step 3 says `COMPLETED`, and never
   resubmit a job just to check on it: that starts and charges a second job.

## Chaining jobs

To feed one job's output into another tool, pass `file_url` as a job reference:
`job:<tool>:<id>`, for example `job:denoise_audio:1234`. AudioPod substitutes
the real output. Wait for the first job to be `COMPLETED` first.

## Credits

- Each job is paid in advance from the AudioPod account linked to the API key.
  If a job fails, its credits are returned.
- `check_job_status` costs nothing.
- **Insufficient credits (402)**: tell the user plainly and link
  https://audiopod.ai/pricing. Do not retry in a loop.
- Never state prices, rates, or credit amounts. Always link
  https://audiopod.ai/pricing.

## API keys and scopes

- Keys start with `ap_` and are created at
  https://audiopod.ai/dashboard/account/api-keys. The key is entered once in
  the plugin settings; never ask the user to paste it into the chat.
- A "missing required scope" error names the scope the key lacks. Polling
  needs `audio:read`. The user can create a new key with that scope.
- An unauthorized error means the key is missing, revoked, or mistyped.

## Help

Docs: https://docs.audiopod.ai. Support: https://audiopod.ai/support.
