# Experiment log (live runs, 22 November 2026)

## How the results were produced
Real runs of the workflows on **gemini-3.1-flash-lite** through the Gemini API (temperature 0.0, thinking level minimal), one run per version, on the 9 notes in `test-data/notes/` scored against `test-data/gold/` by `code/smartstudy/evaluate.py`. Raw outputs: `test-data/live_runs/` (copied to `test-data/results/` for the dashboard). Free-tier request limits differ by model (one model we tried allowed only 20 requests per day), which limited repeated runs, so each version was run once. The earlier simulated answers (Claude Haiku via helper agents, October) are in `test-data/replay_simulated_oct28/` and are **not** used for any claim.

## Hypotheses (written in October, before any run; re-tested here on live data)
| # | Hypothesis | Result on live data |
|---|---|---|
| H1 | v2 beats v1 (fewer outside terms, format followed) | **Supported on format, not on recall.** constraints 0.0 to 1.0; flagged terms 0.091 to 0.0; answer_support 0.725 to 0.956; term_recall fell 0.358 to 0.22. |
| H2 | v3 (one example) beats v2 | **Not supported.** recall 0.22 to 0.237, coverage 0.622 to 0.568, and 2 questions had a quote not in the notes (ungrounded 0.044). |
| H3 | v4 (chain) beats v3 | **Mixed.** coverage 0.568 to 0.676 and ungrounded 0.044 to 0.0, but flagged terms 0.0 to 0.053 and answer_support 0.956 to 0.867, at 3x the calls. The quote guard dropped 1 item in 9 notes. |
| H5 | v5 length guard fixes word-limit failures | **Could not be tested on packs.** Every summary was already within 100 words, so the guard never fired. Verified separately in test 7 (real over-long summary shortened by P4). |

## Scores, all 9 notes
| Version | term_recall | coverage | term_halluc | ungrounded_q | answer_support | outside_know | constraints | json_fail |
|---|---|---|---|---|---|---|---|---|
| v0 | 0.191 | 0.568 | 0.0 | 0.0 | 1.0 | 0 | 0.0 | 0 |
| v1 | 0.358 | 0.649 | 0.091 | n/a | 0.725 | 0 | 0.0 | 0 |
| v2 | 0.22 | 0.622 | 0.0 | 0.0 | 0.956 | 0 | 1.0 | 0 |
| v3 | 0.237 | 0.568 | 0.0 | 0.044 | 0.956 | 0 | 1.0 | 0 |
| v4 | 0.254 | 0.676 | 0.053 | 0.0 | 0.867 | 0 | 1.0 | 0 |
| v5 | 0.254 | 0.676 | 0.053 | 0.0 | 0.867 | 0 | 1.0 | 0 |

## Short notes (6)
| Version | term_recall | coverage | term_halluc | ungrounded_q | answer_support | outside_know | constraints | json_fail |
|---|---|---|---|---|---|---|---|---|
| v0 | 0.276 | 0.789 | 0.0 | 0.0 | 1.0 | 0 | 0.0 | 0 |
| v1 | 0.526 | 0.842 | 0.083 | n/a | 0.76 | 0 | 0.0 | 0 |
| v2 | 0.342 | 0.789 | 0.0 | 0.0 | 0.933 | 0 | 1.0 | 0 |
| v3 | 0.368 | 0.763 | 0.0 | 0.033 | 0.933 | 0 | 1.0 | 0 |
| v4 | 0.421 | 0.842 | 0.077 | 0.0 | 0.833 | 0 | 1.0 | 0 |
| v5 | 0.421 | 0.842 | 0.077 | 0.0 | 0.833 | 0 | 1.0 | 0 |

## Long notes (3)
| Version | term_recall | coverage | term_halluc | ungrounded_q | answer_support | outside_know | constraints | json_fail |
|---|---|---|---|---|---|---|---|---|
| v0 | 0.124 | 0.333 | 0.0 | 0.0 | 1.0 | 0 | 0.0 | 0 |
| v1 | 0.227 | 0.444 | 0.105 | n/a | 0.667 | 0 | 0.0 | 0 |
| v2 | 0.124 | 0.444 | 0.0 | 0.0 | 1.0 | 0 | 1.0 | 0 |
| v3 | 0.134 | 0.361 | 0.0 | 0.067 | 1.0 | 0 | 1.0 | 0 |
| v4 | 0.124 | 0.5 | 0.0 | 0.0 | 0.933 | 0 | 1.0 | 0 |
| v5 | 0.124 | 0.5 | 0.0 | 0.0 | 0.933 | 0 | 1.0 | 0 |

## Error analysis (real failures)
| Where | Failure | Likely cause | Next step |
|---|---|---|---|
| v1, all notes | Only short-answer questions, 4 or 5 per note, no required mix; no source quotes | Prompt gives no counts, types or evidence rule | Fixed by v2 (constraints 0.0 to 1.0) |
| v1, 5 notes | One term per note not found in the notes (for example AUC-ROC, CI/CD) | No "use only the notes" rule | Fixed by v2 (flagged terms 0.0) |
| v2 to v5, all notes | Only 3 to 6 key terms where the gold list has 10 to 15 (recall 0.22 to 0.25) | Prompt never says how many terms or to be exhaustive | **Open.** v6: "list every defined term" with a minimum count |
| v3, TCP and memory notes | A question's evidence is not contiguous text from the notes (it joins two parts with "...") | The model broke the "one exact contiguous quote, no ellipses" rule | v4 quote guard removes such items |
| v4, 2 notes | A term flagged as not in the notes ("Big-O Notation", "Boyce-Codd Normal Form (BCNF)") | Naming variants; exact-phrase check is strict | Use fuzzy matching in the scorer |
| Test 8 and 12 | 5 questions from a 3-sentence note and from casual chat, no warning | Model ignores the "return fewer and warn" rule | **Open.** Cap N by note length in code; add an "is this lecture content?" check |

## Validity caveats
One run per version, one model, nine computer-science notes. Differences of a few points are not strong evidence. term_recall uses lenient containment matching and rewards long term lists. answer_support is a word-overlap proxy, not a correctness check. There is no human scoring yet (planned for Milestone 3, rubric in `docs/human_eval_rubric.md`). Prompts v1 to v5 were written before the live runs. Test inputs 8 to 12 were designed to probe known risks (thin input, injection, missing information, non-lecture text), so failures there are informative rather than surprising.

Keep failures and losing versions in this log; do not delete them.
