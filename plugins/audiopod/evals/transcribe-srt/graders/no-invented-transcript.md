---
type: llm
focus: trace
---
The assistant must not invent transcript content. Any transcript text or subtitle lines it shows must come from the check_job_status tool result (which contains "ZEBRA-MARKER welcome to the mock talk") or it should give the output URL from the result. Fail if it presents transcript text that does not appear in any tool result, or claims a transcript is ready before check_job_status reported COMPLETED.
