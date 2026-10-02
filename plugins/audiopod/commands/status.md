---
description: Check the status of an AudioPod job and get its output links
argument-hint: [job-id] [tool]
---

Check the status of my AudioPod job: $ARGUMENTS

Follow the `audiopod-jobs` skill. Call `check_job_status` with the job id and tool named above. Job ids are only unique per tool. If a job id was given without a tool, use the tool that started that job earlier in this conversation; if you don't know it, ask the user what kind of job it was (for example transcription or stems) before calling. If nothing was given, call it with no arguments so AudioPod finds the most recent job. Report the status, and every output link if the job is `COMPLETED`. Never guess a job id.
