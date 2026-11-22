=== SYSTEM PROMPT ===
You edit revision summaries. Rewrite the given summary so that it has AT MOST the stated number of words (count carefully; aim for about 10 percent under the limit). Keep every topic that the summary currently covers, keep technical terms, and add nothing that is not already in the summary. Output ONLY valid JSON, no fences: {"summary": string}


=== USER MESSAGE ===
Word limit: 100
Current length: 105 words

SUMMARY TO SHORTEN
The scheduler picks the next ready process and the dispatcher switches the CPU to it via a context switch. Preemptive scheduling can take the CPU from a running process; non-preemptive scheduling does not. FCFS runs processes in arrival order but suffers the convoy effect. SJF gives minimum average waiting time but needs burst prediction and can starve long processes. Round Robin gives each process a fixed quantum and sends it to the back of the ready queue; large quanta act like FCFS and tiny ones add overhead. Priority scheduling runs the highest priority first, and aging solves starvation. Metrics are turnaround, waiting and response time.

Return the JSON now.

