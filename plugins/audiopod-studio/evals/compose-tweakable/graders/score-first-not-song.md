---
type: llm
---
The user wants a song they can tweak before it is recorded. Pass only if the assistant calls compose_music with a `style` and a `description` (the user gave no lyrics, so it must not pass `lyrics` or invent them), and does not call generate_music. Fail if it calls generate_music, passes `lyrics`, or writes notation itself.
