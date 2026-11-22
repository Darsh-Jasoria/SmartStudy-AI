# Reel script (90 to 150 seconds, target about 125 s)

Record the screen with a voice-over (QuickTime: File, New Screen Recording, microphone on). Faces are optional. **The demo must be a real run** (Part 3). Upload to Google Drive or unlisted YouTube, set "Anyone with the link can view", and note the exact length in seconds for form Q14.

| Part | Time | Who | On screen | Say |
|---|---|---|---|---|
| 1 Problem | 0:00 to 0:12 | Darsh | Title (app About page) | "We are Team IntelliCore. Students have long lecture notes and little time. SmartStudy turns notes into a summary, key terms and practice questions, and every answer shows its quote from the notes." |
| 2 Prompt experiment | 0:12 to 0:50 | Mahak | Evaluation dashboard, Overview, then the Compare tab (v1 against v5 on the TCP notes) | "Our first prompt, v1, was one line. It wrote only short questions, and not one note met the format: constraints met were 0. With role, rules and quotes in v2, constraints went to 1 and answer support rose from 0.725 to 0.956. Our final v5 chain adds an outline, a quote check in code and a moderator, which raised coverage from 0.57 (v3) to 0.68." |
| 3 Working demo | 0:50 to 1:45 | Pradanya | Generate page, **live app**: paste the Hinglish deadlock notes (`test-data/m2_inputs/E2_hinglish_deadlock.txt`), workflow v5, Generate; show Overview (5 terms, 5 questions, 100% verified), then Questions and Show answer | "Here is a real run on Hinglish notes. The model returns a summary within the limit, key terms, and five questions. Each one is marked source verified, because code checked that the quote exists in our notes." |
| 4 Progress and next steps | 1:45 to 2:05 | Arnav | Test table (docs/test_table.md in the dashboard, Project docs) | "We ran 13 tests: 11 pass and 2 fail. A 3-sentence note and casual chat still get 5 questions with no warning. For Milestone 3 we will fix that, raise key-term recall, add human scoring and compare ChatGPT and Claude." |

Checklist before upload: length between 90 and 150 s; the demo shows the real app answering, not slides; audio clear; every member speaks or appears at least once if you want to show shared work.
