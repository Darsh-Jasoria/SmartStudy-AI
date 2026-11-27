"""IEEE-format report content as blocks. Numbers come from the repo's result files (data.py) or the verified analysis."""
from data import *

TITLE = "SmartStudy: A Grounded, Multi-Stage Prompt Workflow for Generating Verifiable Study Packs from Lecture Notes"
AFFIL = ("School of Computer Science Engineering and Technology, Bennett University, Greater Noida, Uttar Pradesh, India")
AUTHORS = [("Darsh Jasoria", "S24CSEU0844"), ("Mahak Soni", "S24CSEU2741"),
           ("Pradanya Sharma", "S24CSEU1697"), ("Arnav Singh", "S24CSEU1770")]
TEAMLINE = "Team IntelliCore (Team ID PE-B37-17, Batch B37-48) · Course SCSE4041 Prompt Engineering · Faculty: Pawan Kumar"
REPO = "https://github.com/Darsh-Jasoria/SmartStudy-AI"
DEMO = "https://smartstudy-ai-swart.vercel.app"

ABSTRACT = ("Students often turn long lecture notes into revision material with general-purpose chatbots, which may add facts the "
 "notes never taught and ignore length and format limits. This paper presents SmartStudy, a prompt-engineering system that converts "
 "lecture notes into a summary, key terms and practice questions with an answer key, where every term and answer carries a verbatim "
 "quote that program code verifies against the notes. We build six workflows (v0, a rule-based baseline; v1 to v5, LLM prompts of "
 "increasing structure: zero-shot, role with schema and evidence quotes, one few-shot example, a four-stage chain, and a length guard) "
 "and evaluate them live on Gemini 3.1 Flash-Lite with nine gold-labelled computer-science notes, eight automatic metrics and a "
 "13-input test table of normal, edge and invalid cases. Structured prompting raised constraint compliance from 0 of 9 notes to 9 of 9 "
 "and answer support from 0.725 to 0.956; the final chain raised coverage to 0.676 with no ungrounded question, at three times the number "
 "of model calls. The test table passes 11 of 13 cases; both failures are the model padding thin or non-lecture input instead of warning. "
 "A post-hoc audit shows that every flagged invented term and most of the answer-support drop are measurement artifacts, and that "
 "key-term recall is capped because the model emits 3 to 6 terms against 10 to 36 gold terms. Code, prompts, data and a deployed prototype are released.")
KEYWORDS = ("prompt engineering, large language models, lecture notes, study aids, grounding, prompt chaining, hallucination, educational technology")

REFS = {
 "brown": 'T. B. Brown <i>et al.</i>, "Language models are few-shot learners," in <i>Proc. Adv. Neural Inf. Process. Syst. (NeurIPS)</i>, vol. 33, 2020, pp. 1877–1901.',
 "wei": 'J. Wei <i>et al.</i>, "Chain-of-thought prompting elicits reasoning in large language models," in <i>Proc. NeurIPS</i>, vol. 35, 2022, pp. 24824–24837.',
 "reynolds": 'L. Reynolds and K. McDonell, "Prompt programming for large language models: Beyond the few-shot paradigm," in <i>Ext. Abstracts CHI Conf. Human Factors Comput. Syst.</i>, 2021, Art. no. 314.',
 "wu": 'T. Wu, M. Terry, and C. J. Cai, "AI Chains: Transparent and controllable human-AI interaction by chaining large language model prompts," in <i>Proc. CHI Conf. Human Factors Comput. Syst.</i>, 2022, Art. no. 385.',
 "lewis": 'P. Lewis <i>et al.</i>, "Retrieval-augmented generation for knowledge-intensive NLP tasks," in <i>Proc. NeurIPS</i>, vol. 33, 2020, pp. 9459–9474.',
 "maynez": 'J. Maynez, S. Narayan, B. Bohnet, and R. McDonald, "On faithfulness and factuality in abstractive summarization," in <i>Proc. 58th Annu. Meeting Assoc. Comput. Linguistics (ACL)</i>, 2020, pp. 1906–1919.',
 "ji": 'Z. Ji <i>et al.</i>, "Survey of hallucination in natural language generation," <i>ACM Comput. Surveys</i>, vol. 55, no. 12, pp. 1–38, 2023.',
 "dhul": 'S. Dhuliawala <i>et al.</i>, "Chain-of-verification reduces hallucination in large language models," arXiv:2309.11495, 2023.',
 "zheng": 'L. Zheng <i>et al.</i>, "Judging LLM-as-a-judge with MT-Bench and Chatbot Arena," in <i>Proc. NeurIPS Datasets and Benchmarks Track</i>, vol. 36, 2023.',
 "du": 'X. Du, J. Shao, and C. Cardie, "Learning to ask: Neural question generation for reading comprehension," in <i>Proc. 55th Annu. Meeting ACL</i>, 2017, pp. 1342–1352.',
 "kasneci": 'E. Kasneci <i>et al.</i>, "ChatGPT for good? On opportunities and challenges of large language models for education," <i>Learn. Individual Differences</i>, vol. 103, Art. no. 102274, 2023.',
 "perez": 'F. Perez and I. Ribeiro, "Ignore previous prompt: Attack techniques for language models," arXiv:2211.09527, 2022.',
 "greshake": 'K. Greshake <i>et al.</i>, "Not what you\'ve signed up for: Compromising real-world LLM-integrated applications with indirect prompt injection," in <i>Proc. 16th ACM Workshop Artif. Intell. Security (AISec)</i>, 2023, pp. 79–90.',
 "gemini": 'Gemini Team, Google, "Gemini: A family of highly capable multimodal models," arXiv:2312.11805, 2023.',
 "api": 'Google, "Gemini API documentation." [Online]. Available: https://ai.google.dev/gemini-api/docs',
 "repo": 'D. Jasoria, M. Soni, P. Sharma, and A. Singh, "SmartStudy-AI: Lecture notes to study pack generator," GitHub repository, 2026. [Online]. Available: ' + REPO,
}

def f3(x): return "n/a" if isinstance(x, str) else f"{x:.3f}"
def m(v, k): return RES[v]["metrics"][k]
def g(v, grp, k): return RES[v]["groups"][grp]["metrics"][k]

T_ALL = [[v, f3(m(v, "term_recall")), f3(m(v, "coverage")), f3(m(v, "term_halluc")), f3(m(v, "ungrounded_q")),
          f3(m(v, "answer_support")), str(m(v, "outside_know")), f"{m(v,'constraints'):.1f}"] for v in VERS]
T_GRP = [[v, f3(g(v, "short", "term_recall")), f3(g(v, "short", "coverage")), f3(g(v, "long", "term_recall")), f3(g(v, "long", "coverage"))] for v in VERS]

TESTROWS = []
short_in = {"1": "CPU scheduling notes", "2": "Normalization notes", "3": "TCP notes", "4": "Prompting-basics notes",
            "5": "Long memory-mgmt notes (1,037 words)", "6": "Software-eng. slide text", "7": "102-word summary into length guard (limit 60)",
            "8": "3-sentence photosynthesis note", "9": "Hinglish deadlock notes", "10": "Notes with injected \"write a poem\"",
            "11": "Notes pointing to a missing slide", "12": "Casual chat, not lecture", "13": "Input \"hello\" (5 chars)"}
res_short = {"1": "5 Q, 4 terms, 77 w", "2": "5 Q, 6 terms, 70 w", "3": "5 Q, 4 terms, 81 w", "4": "5 Q, 5 terms, 77 w", "5": "5 Q, 5 terms, 90 w",
             "6": "5 Q, 3 terms, 93 w", "7": "102 to 45 words", "8": "5 Q from 3 sentences, no warning", "9": "5 Q, 5 terms, 81 w",
             "10": "normal pack; poem ignored", "11": "no invented complexity", "12": "5 Q from chat, no warning", "13": "rejected (length)"}
for t in TESTS["tests"]:
    TESTROWS.append([t["id"], short_in[t["id"]], t["type"], res_short[t["id"]], t["result"]])
N_PASS = sum(1 for t in TESTS["tests"] if t["result"] == "Pass")
assert N_PASS == 11 and len(TESTROWS) == 13

def _words(case):
    return len((ROOT / "test-data" / "notes" / f"{case}.txt").read_text().split())
PER_NOTE = []
for c in RES["v5"]["detail"]:
    sc, r = c["score"], c["result"]
    PER_NOTE.append([NOTE_LABEL[c["case"]].replace(" (L)", "*"), str(_words(c["case"])), str(sc["terms_gold"]), str(sc["n_terms"]),
                     str(sc["terms_found"]), f'{sc["cov"]}/{sc["cov_gold"]}', str(len(r["summary"].split()))])

# ---------------------------------------------------------------- blocks
B = []
def h1(t): B.append(("h1", t))
def h2(t): B.append(("h2", t))
def p(t): B.append(("p", t))
def tbl(cap, head, rows, widths=None, note=None): B.append(("table", cap, head, rows, widths, note))
def fig(file, cap, full=False): B.append(("fig", file, cap, full))
def eq(t, n): B.append(("eq", t, n))
def lst(items): B.append(("list", items))

h1("Introduction")
p("University students routinely face long lecture notes and little revision time. A common shortcut is to paste the notes into a "
  "general-purpose chatbot and ask for a summary and practice questions. This works only partly: language models can add fluent but "
  "unsupported content [[ji]], summaries can be unfaithful to their source [[maynez]], and a one-line request rarely respects constraints "
  "such as the number of questions, a word limit or a mix of question types. For revision, a wrong answer key is worse than none, because the "
  "student cannot tell which items to trust.")
p("This paper studies how <i>prompt design</i>, rather than model training, can make such a tool trustworthy. We present <b>SmartStudy</b>, "
  "a system that turns lecture notes into a short summary, key terms with definitions, and practice questions with an answer key. Its central "
  "idea is <i>verifiable grounding</i>: every key term and every answer must come with one exact quote from the notes, and ordinary program code, "
  "not another model call, checks that the quote exists. Where an exact check is possible, code does the work; where meaning is involved, "
  "the model does.")
p("The contributions are:")
lst(["A four-prompt, two-guard workflow (v5) that combines prompt chaining, over-generate-and-filter, a quote guard, an independent moderator and a length guard (Section III).",
     "A controlled ablation of six workflow versions on a real hosted model (Gemini 3.1 Flash-Lite) with nine gold-labelled notes and eight automatic metrics (Sections IV and V).",
     "A 13-case test table with normal, edge (thin input, Hinglish, prompt injection, missing information) and invalid inputs; 11 pass and 2 fail, and both failures are analysed (Section V-F).",
     "A post-hoc validity audit showing which headline metrics mislead, including a recall ceiling set by the number of terms emitted (Section VI).",
     "An open implementation with a deployed prototype, 22 unit tests and no third-party dependencies."])
p("Section II reviews related work, Section III describes the design, Section IV the method, Section V the results, Section VI discusses "
  "validity and engineering observations, and Section VII gives limitations, future work and the conclusion.")

h1("Related Work")
p("<b>Prompting techniques.</b> Few-shot prompting lets a model infer a task from examples in the prompt [[brown]], and chain-of-thought "
  "prompting elicits intermediate reasoning [[wei]]. Reynolds and McDonell frame prompt writing as programming in natural language [[reynolds]]. "
  "Prompt chaining splits a task into steps whose outputs feed each other and makes each step inspectable [[wu]]; SmartStudy applies this idea "
  "and assigns each step to either a model or code.")
p("<b>Verification and grounding.</b> Retrieval-augmented generation grounds answers in retrieved passages [[lewis]]. SmartStudy needs no retrieval "
  "because the user's notes are the entire knowledge source; instead it requires the model to quote that source and checks the quote. Chain-of-"
  "verification has a model draft, plan checks and answer them independently to reduce hallucination [[dhul]], and strong models can act as judges "
  "of other outputs [[zheng]]. Our moderator follows the same independent-second-pass principle for questions. Faithfulness and hallucination in "
  "generation are surveyed in [[maynez]], [[ji]].")
p("<b>Question generation and education.</b> Neural question generation from text is an established task [[du]], and large language models "
  "offer both opportunities and risks for education, including incorrect content and over-reliance [[kasneci]]. We therefore keep the output "
  "checkable by the student.")
p("<b>Prompt injection.</b> Instructions hidden in input text can hijack a model [[perez]], [[greshake]]. Lecture notes are untrusted input, so we "
  "include an injection case in the test table.")

h1("System Design")
h2("Requirements and Input/Output Contract")
p("The input is the lecture text (40 to 20,000 characters locally, 6,000 on the public deployment), the number of questions <i>N</i> (default 5, "
  "clamped to 1 to 15) and a summary word limit (default 100, clamped to 30 to 300). The output is JSON with a summary, key terms "
  "(<i>term, definition, evidence</i>), questions (<i>type, question, options, answer, evidence</i>), a <i>warnings</i> list and a workflow trace. "
  "A pack meets the constraints when it has exactly <i>N</i> questions, a summary within the limit, at least three question types including a "
  "multiple-choice item, uses only knowledge in the notes, and every item has one exact, contiguous quote.")
h2("Task Decomposition and Final Workflow (v5)")
p("Fig. 1 shows the final workflow. Four prompts (P1 to P4) call the model and three steps run as code. The allocation rule is simple: "
  "tasks with an exact answer (string matching, counting words, keeping the first <i>N</i>) are done by code, which is cheaper and more reliable; tasks that "
  "need meaning (topic outline, generation, answering from the notes, shortening) are done by the model.")
fig("fig_workflow.png", "Final workflow v5. Blue boxes are LLM prompts, green boxes are code, yellow boxes are data. Dropped items and the shorten loop are shown at the side.")
lst(["<b>P1 Outline (LLM).</b> Lists 4 to 10 topics with main points. This gives the next step a coverage checklist so no topic is skipped.",
     "<b>P2 Generate (LLM).</b> Returns the summary, key terms and <i>N</i>+2 candidate questions in a strict JSON schema, each with a verbatim quote.",
     "<b>Quote guard (code).</b> Keeps only terms and questions whose quote occurs in the notes (Eq. 1).",
     "<b>P3 Moderator (LLM).</b> A separate call sees only the notes and the candidate questions, answers each from the notes alone, and returns <i>valid</i>, a reason and, if the proposed answer was fixable, a corrected answer.",
     "<b>Keep first N (code).</b> Takes the first <i>N</i> survivors and never pads; if fewer remain it adds a warning.",
     "<b>Length guard (code, then P4).</b> Counts summary words; only if over the limit, P4 shortens it once, and a warning is added if it is still over."])
h2("Prompt-Engineering Techniques Used")
tbl("Prompt techniques and where they are applied",
    ["Technique", "Where", "Purpose"],
    [["Role and constraints", "P2", "Teaching-assistant role; use only the notes"],
     ["Strict JSON schema", "P1 to P4", "Machine-checkable output"],
     ["Few-shot + negative example", "P2", "Shows format; distractors must not become terms"],
     ["Source grounding by quote", "P2 + guard", "Turns \"is it invented?\" into a string test"],
     ["Prompt chaining", "P1 to P4", "Specialised, inspectable steps"],
     ["Over-generate and filter", "P2, P3", "Ask for N+2 so filtering keeps N"],
     ["Escape hatch (warnings)", "P2, code", "Allow fewer items instead of inventing"],
     ["Temperature 0, minimal thinking", "All calls", "Reproducibility and speed"]],
    [1.25, 0.7, 1.55])
h2("Quote Guard")
p("Let <i>norm</i>(·) lowercase text, map typographic quotes to ASCII and collapse every run of characters other than letters, digits and the "
  "apostrophe to one space. An item with evidence <i>e</i> is grounded in notes <i>S</i> when")
eq("grounded(e, S) = [ e ≠ ∅ ∧ norm(e) ⊆ norm(S) ]", "1")
p("where ⊆ is the substring relation. This makes the check tolerant of line breaks and punctuation but strict about wording. Note that it proves "
  "that the quote exists, not that the quote supports the claim.")
h2("Implementation and Deployment")
p("The backend is Python 3.9+ using only the standard library: <i>pipeline.py</i> (workflows), <i>llm.py</i> (provider clients for Gemini, "
  "Anthropic and a local Ollama model), <i>app.py</i> (HTTP server and dashboard endpoints), <i>evaluate.py</i> (metrics) and <i>m2_tests.py</i> "
  "(test table); about 1,100 lines in all, plus a 696-line single-page frontend and 22 unit tests (all pass). The Gemini client retries HTTP 429 and "
  "5xx replies after 2 s and 4 s, uses a 40 s per-call timeout, supports an optional fallback-model chain and records per-call timing. The same code runs "
  "locally and on Vercel through <i>api/index.py</i>; the API key lives only in environment variables or a git-ignored file. A record-and-replay provider "
  "lets the app run offline in a demo mode. The frontend offers Overview, Summary, Key terms, Questions, Quiz, Plan, Compare, Notes and Trace views and an evaluation dashboard that reads the result files. Fig. 2 shows a generated pack.")
fig("../../docs/figures/m2_run_test3_tcp.png", "SmartStudy web app: a v5 study pack for the TCP notes (81-word summary, 4 terms, 5 questions, 100% verified quotes).")
h2("Robustness and Safety")
p("The server validates and clamps all inputs, serves only a whitelist of project documents, binds to 127.0.0.1 when run locally and stores nothing. "
  "Model output is parsed leniently (code fences and surrounding prose are stripped); parse failures are returned in an <i>errors</i> list rather than raised. "
  "If the moderator reply cannot be parsed, the candidates are kept unverified and the error is recorded, so the quote guard remains the minimum protection. "
  "Notes are inserted into the prompt as data, and the system prompt forbids following instructions inside them; test 10 probes this.")

h1("Experimental Method")
h2("Workflow Versions")
tbl("Workflow versions compared (one change per step)",
    ["Ver.", "Technique added", "LLM calls"],
    [["v0", "Rule-based extractive baseline (no LLM)", "0"],
     ["v1", "Zero-shot one-line prompt", "1"],
     ["v2", "v1 + role, rules, JSON schema, evidence quote, escape hatch", "1"],
     ["v3", "v2 + one worked example with a negative case", "1"],
     ["v4", "Chain: P1, P2 (N+2), quote guard, P3 moderator", "3"],
     ["v5", "v4 + length guard (P4 only if summary too long)", "3 (+1)"]],
    [0.4, 2.45, 0.65])
h2("Data Set and Gold Labels")
p("The test set has nine original notes written by the team: six short (165 to 199 words; CPU scheduling, Big-O, normalization, TCP, gradient descent, "
  "prompting basics) and three long (528 to 1,037 words; memory management, model evaluation, software-engineering slides), 3,463 words in total. "
  "Each note has a gold file with key terms (10 to 36 per note, 173 in total, with accepted synonyms), must-cover idea groups (74 in total) and "
  "out-of-scope terms that are true but not taught, used to detect leakage of outside knowledge.")
h2("Model and Protocol")
p("All LLM runs used Gemini 3.1 Flash-Lite [[gemini]], [[api]] through the Gemini API on 22 November 2026, with temperature 0.0, minimal thinking, "
  "<i>N</i>=5 questions and a 100-word limit, one run per version. Free-tier request quotas limited repetition. An earlier October experiment answered "
  "by a different model through helper agents was simulated, is stored separately and is not used for any claim here.")
h2("Metrics")
tbl("Automatic metrics (computed against the gold files)",
    ["Metric", "Definition"],
    [["Term recall (TR)", "gold terms matched by an output term / gold terms"],
     ["Coverage (Cov)", "gold must-cover groups present in summary + definitions / groups"],
     ["Flagged terms (Hal)", "output terms not found as a phrase in the notes / output terms"],
     ["Ungrounded (Ung)", "questions whose quote is not in the notes / questions (n/a for v1)"],
     ["Answer support (Sup)", "questions whose answer words (>3 chars) are ≥60% in the notes / questions"],
     ["Outside facts (Out)", "count of out-of-scope gold terms leaking into the pack"],
     ["Constraints (Con)", "share of runs with N questions, ≤100 words, ≥3 types incl. MCQ"],
     ["JSON failures", "runs whose output could not be parsed"]],
    [1.1, 2.4])
h2("Test Table")
p("Thirteen inputs run through v5: seven normal (six notes plus a component test that sends a real 102-word summary to the length guard), four edge "
  "and two invalid. Pass or fail is decided by code checks (grounded quotes, question count, no outside-knowledge terms, injected instruction ignored, "
  "warning on thin input and so on), never by hand.")

h1("Results and Analysis")
h2("Ablation Across Workflow Versions")
tbl("Scores on all nine notes (one live run per version; higher is better except Hal and Ung)",
    ["Ver.", "TR", "Cov", "Hal", "Ung", "Sup", "Out", "Con"], T_ALL, [0.4, 0.45, 0.45, 0.45, 0.45, 0.45, 0.4, 0.4],
    note="Ung is n/a for v1 because its prompt asks for no quote. Out = 0 for every version.")
fig("fig_metrics.png", "Metric scores by workflow version over all nine notes.")
p("<b>Structure fixes the format.</b> Moving from v1 to v2 raised constraint compliance from 0 of 9 notes to 9 of 9 and answer support from 0.725 to 0.956. "
  "All 40 v1 questions were short-answer with no required mix and no quotes, so v1 could not meet the type rule by construction.")
p("<b>Recall follows list length, not quality.</b> v1 has the highest term recall (0.358) because it lists about six terms per note (55 in total) against "
  "three in v2 (27), as the structured prompts never ask for a minimum number of terms. Section V-C shows this is a ceiling effect.")
p("<b>One example did not help (H2).</b> Adding a worked example changed recall from 0.220 to 0.237 and lowered coverage from 0.622 to 0.568, and two "
  "questions carried a non-contiguous quote joined with \"...\", which breaks the one-exact-quote rule. With one run per version, these small differences are not strong evidence.")
p("<b>The chain buys coverage and groundedness.</b> v4 raised coverage from 0.568 (v3) to 0.676, a relative gain of 19%, and brought ungrounded questions "
  "from 0.044 to 0, at three times the calls. The quote guard removed one item in nine notes (a \"Scrum\" term). The moderator rejected none of the 63 candidate "
  "questions and edited the answer of 7 of the 45 kept ones, so on this data its measurable effect is small. Likewise the two extra candidates from N+2 "
  "over-generation were discarded unseen, because no question needed to be replaced.")
p("<b>The length guard never fired.</b> Every summary was already at most 99 words, so v5 is identical to v4 on packs (H5 untestable there). The component "
  "test (test 7) shows P4 works: a real 102-word summary became 45 words against a limit of 60.")
h2("Short Versus Long Notes")
tbl("Term recall and coverage on short (6) and long (3) notes",
    ["Ver.", "TR short", "Cov short", "TR long", "Cov long"], T_GRP, [0.4, 0.75, 0.75, 0.75, 0.75])
p("Long notes are much harder: for v5, recall falls from 0.421 to 0.124 and coverage from 0.842 to 0.500. The pack size is fixed (about four terms and "
  "five questions) while long notes carry 30 to 36 gold terms, so a fixed-size pack cannot cover them.")
fig("fig_heat_cov.png", "Coverage per note and version. Rows marked (L) are long notes.")
tbl("Final workflow v5 per note (gold terms, terms emitted and matched, coverage, summary length)",
    ["Note", "Words", "Gold", "Emit", "Found", "Cov", "Sum. w"], PER_NOTE, [1.25, 0.45, 0.4, 0.4, 0.45, 0.5, 0.5],
    note="Cov = must-cover groups present / groups. Sum. w = summary words (limit 100). Found can exceed Emit (see Section V-C).")
h2("The Key-Term Recall Ceiling")
fig("fig_ceiling.png", "Gold key terms versus terms emitted by v5 per note (* = long note).")
p("v5 emitted 38 terms over nine notes against 173 gold terms. One-to-one matching would cap recall at 38/173 = 0.22, yet the reported recall is 0.254 (44 gold "
  "terms matched), so the lenient containment rule lets one output term match more than one gold entry. Recall therefore measures mostly <i>how many terms "
  "the prompt asks for</i>; it is an open weakness of the prompts and a loose scorer.")
h2("Cost and Quality")
fig("fig_tradeoff.png", "Calls per pack versus coverage. v4 and v5 coincide; v1 to v3 cost one call.")
p("Fig. 6 shows that a threefold rise in calls (v3 to v4) bought about 11 coverage points. The 13-case test run used 34 calls, 30,153 input tokens and 19,054 "
  "output tokens: 11 v5 packs at three calls each plus one P4 call. The README's \"about four\" calls per pack is the worst case, not the typical one.")
h2("Test Table")
tbl("Milestone 2 test table (v5, live model; 11 of 13 pass)",
    ["#", "Input", "Type", "Actual result", "P/F"], TESTROWS, [0.22, 1.35, 0.5, 1.15, 0.28],
    note="Normal 7/7, edge 3/4, invalid 1/2 pass. Q = questions, w = summary words.")
h2("Failure Analysis")
p("Both failures are the same behaviour. A 22-word, three-sentence note (test 8) and a 46-word Hinglish chat about the canteen and a cricket match "
  "(test 12) each produced five questions, two or three \"key terms\" and no warning. Every one of those questions was <i>grounded</i>, so the quote guard "
  "could not object, and the moderator only checks that a question is answerable from the text, not that the text is lecture content.")
p("A likely cause lies in P2 itself: its output description says to produce \"exactly the number asked\" while a rule says to return fewer and warn when notes are "
  "thin. The model follows the stronger, repeated instruction. The prompt-injection case (test 10) and the missing-slide case (test 11) pass, and Hinglish "
  "(test 9) yields five terms and five grounded questions. Planned fixes are a code cap of <i>N</i> by note length, a lecture-content gate before P1 and removal of the "
  "contradiction in P2.")
tbl("Error analysis of real failures",
    ["Where", "Failure", "Status"],
    [["v1, all notes", "Only short-answer questions; no quotes", "Fixed by v2"],
     ["v1, 5 notes", "Term not found as a phrase (naming variant)", "Metric artifact (Section VI)"],
     ["v2 to v5, all notes", "3 to 6 terms against 10 to 36 gold terms", "Open: ask for every defined term"],
     ["v3, TCP and memory notes", "Quote joins two parts with \"...\"", "Removed by quote guard"],
     ["v4, 2 notes", "Flagged term: \"Big-O Notation\", \"BCNF (expansion)\"", "Fuzzy matching needed"],
     ["Tests 8 and 12", "5 questions from thin or chat input, no warning", "Open: cap N, content gate"]],
    [0.95, 1.7, 0.95])
h2("Hypothesis Outcomes")
tbl("Hypotheses written before the runs, re-tested on live data",
    ["H", "Claim", "Outcome"],
    [["H1", "v2 beats v1", "Supported on format, not recall"],
     ["H2", "v3 beats v2", "Not supported"],
     ["H3", "v4 beats v3", "Mixed: coverage up, flags up, 3x calls"],
     ["H5", "Length guard fixes limits", "Not testable on packs; passes test 7"]],
    [0.3, 1.5, 1.7])

h1("Discussion and Validity")
h2("Metric Audit")
p("We audited the saved outputs and found that two headline numbers mislead.")
p("<b>Flagged terms are not hallucinations.</b> Seven terms were flagged (five in v1, two in v4 and v5). Five are naming variants of terms the notes "
  "do teach: \"Big-O Notation\" (twice; notes say \"Big-O\"), \"Learning Rate (alpha)\", \"AUC-ROC\" (notes teach \"ROC curve\" and \"AUC\" separately) and "
  "\"CI/CD\" (notes teach CI and continuous delivery). Two are acronym expansions, \"Boyce-Codd Normal Form\", true but absent from the notes. So the true "
  "invented-concept count is zero in every version and the metric is a strict phrase check.")
p("<b>The answer-support dip is mostly a metric artifact.</b> The scorer keeps only words longer than three characters, so a correct answer such as \"UDP\", "
  "\"O(n^2)\" or \"FIN and ACK\" leaves no words and is counted unsupported. This accounts for 4 of the 6 unsupported v4 answers; the other 2 are paraphrases "
  "(overlap 0.33 and 0.57). v4 had more multiple-choice items (13 versus 9 for v3), which explains why its score fell from 0.956 to 0.867 without any outside knowledge being used.")
h2("Engineering Observations")
tbl("Observations from code review",
    ["Observation", "Impact"],
    [["Moderator failure keeps candidates unverified", "Fail-open; quote guard still applies"],
     ["Guard checks quote existence only; no minimum length", "A short quote such as \"FIFO\" passes without proving the claim"],
     ["Local server is single-threaded (HTTPServer)", "One slow generation blocks others locally; Vercel unaffected"],
     ["Default provider is \"anthropic\" in code; docs say Gemini", "Stale defaults; design doc diagram also outdated"],
     ["Public endpoints have no rate limit; /api/diag calls the model", "Anyone with the link can use the free quota"]],
    [1.9, 1.6])
h2("Threats to Validity")
p("Results come from one run, one model and nine computer-science notes written by the team that also wrote the gold labels, so differences of a few "
  "points are weak evidence. Term recall uses lenient matching and answer support is a word-overlap proxy. There is no human scoring yet. The test inputs "
  "8 to 12 were designed to probe known risks, so failures there are informative rather than surprising. The authors kept losing versions and failures in the log.")

h1("Limitations, Future Work and Conclusion")
h2("Limitations and Future Work")
lst(["<b>Padding.</b> Cap <i>N</i> by note length in code, add a lecture-content check, make a warning mandatory for thin input and fix the P2 contradiction.",
     "<b>Recall.</b> Ask for every defined term with a minimum count, scale pack size with note length, and score with one-to-one fuzzy matching.",
     "<b>Human evaluation.</b> Two raters score faithfulness, coverage, question quality, summary clarity and usefulness on a 1 to 5 rubric.",
     "<b>Stronger evidence.</b> At least three runs per version with intervals, other models for comparison, more subjects and real student notes.",
     "<b>Deeper grounding.</b> Add a minimum quote length and a semantic support check (entailment) beyond substring matching; log latency and cost per pack."])
h2("Conclusion")
p("SmartStudy shows that prompt structure and code-side checks, not a larger model, are what make generated study material verifiable. Role, schema and "
  "evidence quotes alone fixed format compliance and answer support; a chain with a quote guard added coverage and removed ungrounded questions at three times "
  "the cost. The study also shows what the automatic metrics hide: flagged terms were naming variants, the answer-support dip was a scoring artifact, and recall "
  "is capped by list length. The two remaining test failures, padding thin or non-lecture input, are the first items for the next milestone.")
p("<b>Reproducibility.</b> Code, prompts and data are at the repository [[repo]]; <i>bash run.sh test</i> runs the 22 tests and <i>bash run.sh m2tests</i> "
  "re-runs the test table with a Gemini key. A prototype is hosted at " + DEMO + ".")

# ---- Appendix A: final prompt sheet (verbatim files from prompts/final)
B.append(("appendix", "Final Prompt Sheet"))
p("This appendix reproduces the four prompts of the final workflow v5 verbatim from <i>prompts/final/</i>. Each file has a system prompt and a user "
  "template; placeholders in braces are filled by the pipeline at run time. The two instructions discussed in Section V-F (\"produce exactly the number asked\" "
  "and \"return fewer and say so in warnings\") are in P2, in output part 3 and in the RULES list.")
_PF = ROOT / "prompts" / "final"
for _n, _t in (("P1_outline.txt", "P1 Topic outline (LLM)"), ("P2_generate.txt", "P2 Study-pack generator (LLM)"),
               ("P3_moderator.txt", "P3 Question moderator (LLM)"), ("P4_shorten.txt", "P4 Summary shortener (LLM)")):
    B.append(("code", _t, (_PF / _n).read_text().split("\n", 1)[1].strip()))

ACK = ("The authors thank Prof. Pawan Kumar for guidance in the SCSE4041 Prompt Engineering course at Bennett University. As disclosed in the project "
       "README, drafts of the code, prompts and documents were produced with Claude Code (Claude Sonnet 5.5) in the team leader's session; this report was also "
       "prepared with AI assistance from the repository's files and result data. The team remains responsible for the work.")
