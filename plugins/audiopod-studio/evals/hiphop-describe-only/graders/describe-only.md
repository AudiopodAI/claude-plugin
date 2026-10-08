---
type: llm
---
The user gave no lyrics. Pass only if the generate_music call describes the track in `prompt` and does not include a `lyrics` argument (the assistant must not invent lyrics, or copy the description into `lyrics`, without the user approving them). Fail if the call passes `lyrics`, or sets `task_type` to `text2rap` or `lyric2vocals`.
