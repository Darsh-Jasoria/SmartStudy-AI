"""Offline tests: plumbing, guards and scoring. A scripted fake LLM stands in for the API (test double only;
it is never used to produce reported evaluation results)."""
from __future__ import annotations
import json
import unittest
from pathlib import Path

from smartstudy import pipeline
from smartstudy.evaluate import load_cases, score, term_match
from smartstudy.llm import LLM

NOTES = "Lecture 1\n- A stack is a LIFO structure: the last element pushed is the first popped.\n- A queue is a FIFO structure: elements leave in the order they arrived."


class Scripted(LLM):
    def __init__(self, *replies):
        self.replies, self.calls = list(replies), []

    def complete(self, system, user, max_tokens=2000, temperature=0.0):
        self.calls.append(user)
        return self.replies.pop(0)


GOOD = {"summary": "Stack is LIFO.", "warnings": [],
        "key_terms": [{"term": "stack", "definition": "LIFO.", "evidence": "A stack is a LIFO structure"},
                      {"term": "heap", "definition": "invented", "evidence": "A heap is a tree"}],
        "questions": [{"type": "short", "question": "What is a stack?", "options": None, "answer": "LIFO", "evidence": "A stack is a LIFO structure"},
                      {"type": "short", "question": "Invented?", "options": None, "answer": "x", "evidence": "not in notes at all"},
                      {"type": "short", "question": "What is a queue?", "options": None, "answer": "FIFO", "evidence": "A queue is a FIFO structure"}]}


class Tests(unittest.TestCase):
    def test_parse_json_fenced(self):
        self.assertEqual(pipeline.parse_json('```json\n{"a": 1}\n```')[0], {"a": 1})
        self.assertIsNotNone(pipeline.parse_json("nope")[1])

    def test_grounding(self):
        self.assertTrue(pipeline.is_grounded("a stack is a LIFO structure", NOTES))
        self.assertFalse(pipeline.is_grounded("a heap is a tree", NOTES))
        self.assertFalse(pipeline.is_grounded("", NOTES))

    def test_v2_reports_ungrounded_but_keeps(self):
        r = pipeline.run(NOTES, "v2", Scripted(json.dumps(GOOD)), 3, 50)
        self.assertEqual(len(r["questions"]), 3)
        self.assertEqual(sum(q["grounded"] is False for q in r["questions"]), 1)

    def test_v4_chain_drops_ungrounded_and_rejected(self):
        outline = json.dumps({"topics": [{"title": "Stack", "main_points": ["LIFO"]}]})
        review = json.dumps({"reviews": [{"id": 0, "valid": True, "reason": "", "answer": "Last-in first-out"},
                                         {"id": 1, "valid": False, "reason": "outside knowledge", "answer": ""}]})
        llm = Scripted(outline, json.dumps(GOOD), review)
        r = pipeline.run(NOTES, "v4", llm, 5, 50)
        self.assertEqual([q["question"] for q in r["questions"]], ["What is a stack?"])
        self.assertEqual(r["questions"][0]["answer"], "Last-in first-out")
        self.assertTrue(any("not in notes" in d["reason"] for d in r["trace"]["dropped"]))
        self.assertEqual([t["term"] for t in r["key_terms"]], ["stack"])
        self.assertTrue(r["warnings"])  # fewer than requested -> warned, not padded
        self.assertIn("Number of questions: 7", llm.calls[1])  # over-generation N+2

    def test_bad_json_is_reported_not_raised(self):
        r = pipeline.run(NOTES, "v1", Scripted("sorry, I cannot"), 3, 50)
        self.assertTrue(r["errors"])

    def test_term_match_synonyms(self):
        self.assertTrue(term_match("Round Robin", "round robin|RR"))
        self.assertFalse(term_match("Heap", "stack"))

    def test_v0_runs_and_scores(self):
        data = Path(__file__).resolve().parent.parent.parent / "test-data"
        for c in load_cases(data):
            s = score(pipeline.run(c["notes"], "v0"), c)
            self.assertEqual(s["ungrounded"], 0)  # extractive output is always a quote

    def test_every_gold_term_is_in_its_notes(self):
        data = Path(__file__).resolve().parent.parent.parent / "test-data"
        for c in load_cases(data):
            n = pipeline.norm(c["notes"])
            for grp in c["gold"]["must_cover"]:
                self.assertTrue(any(pipeline.norm(k) in n for k in grp), (c["id"], grp))
            for o in c["gold"]["out_of_scope"]:
                self.assertNotIn(pipeline.norm(o), n, (c["id"], o))  # out-of-scope really is out of the notes


class RobustnessTests(unittest.TestCase):
    """Malformed model replies must produce a warning, never an exception."""
    def test_top_level_list_reply(self):
        r = pipeline.run(NOTES, "v2", Scripted("[1, 2, 3]"), 3, 50)
        self.assertTrue(r["errors"])

    def test_outline_that_is_not_an_object(self):
        gen = json.dumps({"summary": "x", "key_terms": [], "questions": []})
        r = pipeline.run(NOTES, "v5", Scripted("[]", gen, json.dumps({"summary": "x"})), 3, 50)
        self.assertTrue(r["errors"])

    def test_moderator_reviews_not_a_list(self):
        gen = json.dumps({"summary": "s", "key_terms": [], "questions": [
            {"type": "short", "question": "q", "answer": "a", "evidence": "A stack is a LIFO structure"}]})
        r = pipeline.run(NOTES, "v4", Scripted(json.dumps({"topics": []}), gen, '{"reviews": 5}'), 3, 50)
        self.assertEqual(len(r["questions"]), 1)             # kept unverified, with an error recorded
        self.assertTrue(any("verify" in e for e in r["errors"]))


class AppTests(unittest.TestCase):
    def test_dashboard_data_helpers(self):
        from smartstudy import app
        res = app.latest_results()
        self.assertEqual(set(res), set(pipeline.VERSIONS))
        mx = app.results_matrix()
        self.assertEqual({len(v) for v in mx.values()}, {9})            # nine notes per version
        ts = app.testset()
        self.assertEqual([t["group"] for t in ts].count("long"), 3)
        self.assertIn("changelog", app.prompts())
        self.assertTrue(app.prompts()["files"])

    def test_document_whitelist_blocks_other_files(self):
        from smartstudy import app
        self.assertNotIn("../README.md", app.DOCS)
        for rel in app.DOCS.values():
            self.assertTrue((app.ROOT / rel).exists(), rel)

    def test_input_clamping(self):
        from smartstudy import app
        self.assertEqual(app._clamp("99", 1, 15, 5), 15)
        self.assertEqual(app._clamp("x", 1, 15, 5), 5)
        self.assertEqual(app._clamp(-4, 1, 15, 5), 1)


class GroupTests(unittest.TestCase):
    def test_short_and_long_groups_exist_and_notes_are_long_enough(self):
        from smartstudy.evaluate import is_long, evaluate
        data = Path(__file__).resolve().parent.parent.parent / "test-data"
        cases = load_cases(data)
        flags = [is_long(c) for c in cases]
        self.assertEqual(sum(flags), 3)           # three long notes
        self.assertEqual(len(flags) - sum(flags), 6)
        s = evaluate("v0", cases, None)
        self.assertEqual(s["groups"]["short"]["n_notes"], 6)
        self.assertEqual(s["groups"]["long"]["n_notes"], 3)


class ContextTests(unittest.TestCase):
    def test_default_adds_nothing_so_saved_answers_stay_valid(self):
        self.assertEqual(pipeline.context_line("", ""), "")
        self.assertEqual(pipeline.context_line("  ", "unknown"), "")

    def test_subject_and_difficulty_are_prepended(self):
        c = pipeline.context_line("Computer Networks", "Hard")
        self.assertIn("Subject: Computer Networks", c)
        self.assertIn("Difficulty level: hard", c)
        llm = Scripted(json.dumps(GOOD))
        pipeline.run(NOTES, "v2", llm, 3, 50, subject="OS", difficulty="easy")
        self.assertTrue(llm.calls[0].startswith("Subject: OS\nDifficulty level: easy"))


class V5Tests(unittest.TestCase):
    def _run(self, shorten_reply):
        long_summary = " ".join(["word"] * 30)
        gen = dict(GOOD, summary=long_summary)
        outline = json.dumps({"topics": [{"title": "Stack", "main_points": ["LIFO"]}]})
        review = json.dumps({"reviews": [{"id": 0, "valid": True, "reason": "", "answer": "LIFO"},
                                         {"id": 1, "valid": True, "reason": "", "answer": "FIFO"}]})
        return pipeline.run(NOTES, "v5", Scripted(outline, json.dumps(gen), review, shorten_reply), 5, 10)

    def test_v5_shortens_long_summary(self):
        r = self._run(json.dumps({"summary": "Stack is LIFO."}))
        self.assertEqual(r["summary"], "Stack is LIFO.")
        self.assertEqual(r["trace"]["summary_words_before"], 30)

    def test_v5_keeps_original_and_warns_on_bad_reply(self):
        r = self._run("not json")
        self.assertEqual(len(r["summary"].split()), 30)
        self.assertTrue(r["errors"])
        self.assertTrue(any("still over" in w for w in r["warnings"]))

    def test_v5_skips_llm_when_within_limit(self):
        outline = json.dumps({"topics": []})
        review = json.dumps({"reviews": []})
        llm = Scripted(outline, json.dumps(dict(GOOD, summary="short one")), review)
        r = pipeline.run(NOTES, "v5", llm, 5, 10)   # a 4th call would pop from an empty list and raise
        self.assertIn("length guard: ok", r["trace"]["stages"])


class MetricTests(unittest.TestCase):
    def test_v1_groundedness_is_na_not_failure(self):
        from smartstudy.evaluate import aggregate
        data = Path(__file__).resolve().parent.parent.parent / "test-data"
        c = load_cases(data)[0]
        v1 = {"version": "v1", "summary": "x", "key_terms": [], "warnings": [], "errors": [],
              "questions": [{"type": "short", "question": "q", "options": None, "answer": "a", "evidence": "", "grounded": None}]}
        self.assertEqual(aggregate([score(v1, c)])["ungrounded_q"], "n/a")
        v2 = {**v1, "version": "v2"}
        self.assertEqual(aggregate([score(v2, c)])["ungrounded_q"], 1.0)


class OllamaStub(unittest.TestCase):
    def test_ollama_request_and_parse(self):
        import threading
        from http.server import BaseHTTPRequestHandler, HTTPServer
        seen = {}

        class H(BaseHTTPRequestHandler):
            def do_POST(self):
                seen["body"] = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                out = json.dumps({"message": {"content": "hi"}, "prompt_eval_count": 3, "eval_count": 2}).encode()
                self.send_response(200); self.send_header("Content-Length", str(len(out))); self.end_headers(); self.wfile.write(out)

            def log_message(self, *a):
                pass
        srv = HTTPServer(("127.0.0.1", 0), H)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        from smartstudy.llm import OllamaLLM
        llm = OllamaLLM("m", f"http://127.0.0.1:{srv.server_port}")
        self.assertEqual(llm.complete("sys", "usr"), "hi")
        srv.shutdown()
        self.assertEqual(seen["body"]["messages"][0]["role"], "system")
        self.assertFalse(seen["body"]["stream"])
        self.assertEqual((llm.input_tokens, llm.output_tokens), (3, 2))


if __name__ == "__main__":
    unittest.main()
