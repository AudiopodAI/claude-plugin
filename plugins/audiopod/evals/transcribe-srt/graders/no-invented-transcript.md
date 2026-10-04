---
type: llm
focus: trace
---
The assistant must not invent transcript content or URLs. Any transcript text or subtitle lines it shows must come from the check_job_status tool result (which contains "ZEBRA-MARKER welcome to the mock talk"). Fail if it presents transcript text that does not appear in any tool result, quotes a download URL (for example a .srt link) that is not in a tool result, or claims a transcript is ready before check_job_status reported COMPLETED.
