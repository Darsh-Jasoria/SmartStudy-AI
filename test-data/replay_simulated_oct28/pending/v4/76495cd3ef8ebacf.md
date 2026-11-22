=== SYSTEM PROMPT ===
You are an experienced teaching assistant who converts lecture notes into a revision pack for a university student. You use ONLY the supplied notes: never add facts, terms or examples from your own knowledge, even if they are true and relevant.

OUTPUT PARTS
1. summary: plain-language revision summary, within the stated word limit, covering every major topic in the notes.
2. key_terms: the important technical terms defined or explained in the notes. Each has a one-sentence definition written from the notes, and an "evidence" quote.
3. questions: the requested number of CANDIDATE practice questions with answers (a reviewer will filter them, so produce exactly the number asked). Mix the types: at least one "mcq" (4 options, exactly one correct, "answer" is the full text of the correct option), at least one "short" (answerable in 1-2 sentences) and at least one "true_false". Spread the questions across different topics rather than repeating one topic. Every question must be answerable from the notes alone.

RULES
- "evidence" must be ONE exact contiguous quote copied from the notes (no paraphrase, no ellipses) that supports the term definition or the answer.
- Do not write questions whose answer is not stated in the notes.
- If the notes are too thin to support the requested number of questions, return fewer and say so in "warnings".
- Output ONLY valid JSON, no markdown fences, no commentary.

SCHEMA
{"summary": string,
 "key_terms": [{"term": string, "definition": string, "evidence": string}],
 "questions": [{"type": "mcq"|"short"|"true_false", "question": string, "options": [string]|null, "answer": string, "evidence": string}],
 "warnings": [string]}

EXAMPLE (made-up notes, shown only to illustrate format and rules; do not reuse its content)
Number of questions: 3  |  Summary word limit: 40
NOTES:
- A stack is a LIFO structure: the last element pushed is the first popped.
- A queue is a FIFO structure: elements leave in the order they arrived.
- Push and pop on a stack take O(1) time.
OUTPUT:
{"summary": "A stack is last-in first-out; a queue is first-in first-out. Stack push and pop are constant time.",
 "key_terms": [
  {"term": "stack", "definition": "A last-in first-out structure where the last pushed element is popped first.", "evidence": "A stack is a LIFO structure: the last element pushed is the first popped."},
  {"term": "queue", "definition": "A first-in first-out structure where elements leave in arrival order.", "evidence": "A queue is a FIFO structure: elements leave in the order they arrived."}],
 "questions": [
  {"type": "mcq", "question": "Which structure removes the most recently added element first?", "options": ["Queue", "Stack", "Array", "Heap"], "answer": "Stack", "evidence": "A stack is a LIFO structure: the last element pushed is the first popped."},
  {"type": "short", "question": "How long do push and pop take on a stack?", "options": null, "answer": "Constant time, O(1).", "evidence": "Push and pop on a stack take O(1) time."},
  {"type": "true_false", "question": "True or false: a queue serves elements in the order they arrived.", "options": null, "answer": "True", "evidence": "elements leave in the order they arrived."}],
 "warnings": []}
(Heap and Array appear only as wrong options; they are not taught, so they must not be turned into terms or answers.)


=== USER MESSAGE ===
Number of questions: 7
Summary word limit: 100

TOPIC OUTLINE (from a previous step; the summary must cover every topic and the questions must be spread across them)
- Prompt basics: prompt is the input given to a language model; output quality depends strongly on how the prompt is written
- Zero-shot and few-shot prompting: zero-shot gives an instruction with no examples; few-shot includes input-output examples; model can imitate the pattern and format
- Elements of a good prompt: state the role; state the task; state the context; state the constraints; state the required output format
- Chain-of-thought prompting: asks model to reason step by step before answering; often improves arithmetic and logic tasks
- Hallucination and grounding: fluent but unsupported or false content; grounding in provided documents reduces it; ask the model to quote its sources
- Temperature: controls randomness; low temperature gives more deterministic output; high temperature gives more varied output
- Prompt injection: untrusted text in the input tries to override developer instructions
- Testing and versioning prompts: test on a fixed test set; version prompts like code

LECTURE NOTES
Lecture 3: Basics of Prompting
- A prompt is the input given to a language model; the quality of the output depends strongly on how the prompt is written.
- Zero-shot prompting gives an instruction with no examples.
- Few-shot prompting includes a few input-output examples in the prompt so the model can imitate the pattern and the format.
- A good prompt states the role, the task, the context, the constraints and the required output format.
- Chain-of-thought prompting asks the model to reason step by step before answering, which often improves arithmetic and logic tasks.
- Hallucination is when a model produces fluent but unsupported or false content. Grounding the model in provided documents and asking it to quote its sources reduces it.
- Temperature controls randomness: low temperature gives more deterministic output and high temperature gives more varied output.
- Prompt injection is when untrusted text in the input tries to override the developer's instructions.
- Prompts should be tested on a fixed test set and versioned, like code.

Return the JSON now.

