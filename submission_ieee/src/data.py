"""Loads the real result files of the SmartStudy repo so every number in the report/PPT comes from data."""
import glob, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code"))
VERS = ["v0", "v1", "v2", "v3", "v4", "v5"]
COLS = ["term_recall", "coverage", "term_halluc", "ungrounded_q", "answer_support", "outside_know", "constraints", "json_fail"]
NOTE_LABEL = {"01_cpu_scheduling": "CPU sched.", "02_big_o": "Big-O", "03_normalization": "Normalization", "04_tcp": "TCP",
              "05_gradient_descent": "Grad. descent", "06_prompting_basics": "Prompting", "07_memory_management": "Memory mgmt (L)",
              "08_model_evaluation": "Model eval. (L)", "09_software_engineering_slides": "SE slides (L)"}

def load(v):
    return json.load(open(sorted(glob.glob(str(ROOT / "test-data/results" / f"{v}_*.json")))[-1]))
RES = {v: load(v) for v in VERS}
TESTS = json.load(open(sorted(glob.glob(str(ROOT / "test-data/live_runs/m2_tests_*.json")))[-1]))
CASES = [c["case"] for c in RES["v5"]["detail"]]

def per_note(v, key):
    return [c["score"][key] for c in RES[v]["detail"]]
def ratio(v, a, b):
    return [c["score"][a] / c["score"][b] for c in RES[v]["detail"]]
