"""Exports the task bank, subject settings and parity fixtures from the Python desktop app to web/.

The desktop (nmt_tutor/) is frozen; this script moves its data to web/src/core/data/ once and
writes reference answers (web/tests/fixtures/) that the TypeScript port is tested against.

    python3 tools/export_web_data.py            # data + fixtures
"""

import json
import os
import random
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from nmt_tutor import cabinet, engine, hints  # noqa: E402
from nmt_tutor.config import CONVERSION_TABLES, SUBJECTS_CONFIG, SUBJECTS_ORDER, score_to_nmt200  # noqa: E402
from nmt_tutor.data import get_bank  # noqa: E402
from nmt_tutor.generators import SUBJECT_GENERATORS  # noqa: E402

DATA = os.path.join(ROOT, "web", "src", "core", "data")
FIXTURES = os.path.join(ROOT, "web", "tests", "fixtures")


def write(folder, name, obj):
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"wrote {os.path.relpath(path, ROOT)}")


def export_data():
    write(DATA, "subjects.json", {
        "order": SUBJECTS_ORDER,
        "config": SUBJECTS_CONFIG,
        "conversion": {sid: {str(k): v for k, v in table.items()} for sid, table in CONVERSION_TABLES.items()},
        "generators": SUBJECT_GENERATORS,
    })
    write(DATA, "bank.json", get_bank())
    write(DATA, "language_cases.json", language_cases())


def language_cases():
    """The A–D case tables of generators/languages.py, read from its source (they are plain literals)."""
    import ast

    path = os.path.join(ROOT, "nmt_tutor", "generators", "languages.py")
    tree = ast.parse(open(path, encoding="utf-8").read())
    tables = {}
    out = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            if isinstance(node.value, ast.List):
                tables[name] = ast.literal_eval(node.value)
            elif isinstance(node.value, ast.Call):
                args = node.value.args
                key, subject, section, head = (ast.literal_eval(a) for a in args[:4])
                out[key] = {"subject": subject, "section": section, "prompt_head": head,
                            "cases": [list(c) for c in tables[args[4].id]]}
        elif isinstance(node, ast.FunctionDef) and node.name == "gen_eng_reading_ads":
            pool = next(st.value for st in node.body if isinstance(st, ast.Assign) and st.targets[0].id == "pool")
            out["eng_reading_ads"] = {"cases": [list(c) for c in ast.literal_eval(pool)]}
    return out


# --- fixtures --------------------------------------------------------------------------------

def _wrong_single(q):
    labels = [str(x) for x in q.get("labels", [])]
    for lbl in labels:
        if lbl.upper() != str(q["answer"]).upper():
            return lbl
    return "Z"


def evaluate_cases():
    """(task, student answer) pairs over the whole bank plus tricky hand-made answers."""
    cases = []
    for sid, tasks in get_bank().items():
        for q in tasks:
            qt = q["qtype"]
            answers = []
            if qt == "single":
                answers = [q["answer"], str(q["answer"]).lower(), _wrong_single(q), "", " " + str(q["answer"]) + " "]
            elif qt == "short":
                a = str(q["answer"])
                answers = [a, a.replace(".", ","), a + "1", "", " " + a + " ", "abc"]
            elif qt == "matching":
                corr = q["answer"]
                keys = sorted(corr)
                half = {k: (corr[k] if i % 2 == 0 else "Д") for i, k in enumerate(keys)}
                answers = [corr, {k: str(v).lower() for k, v in corr.items()}, half, {}, ""]
            elif qt == "sequence":
                c = str(q["answer"])
                answers = [c, c[::-1], c[0] + c[2] + c[1] + c[3], "-".join(c), c[0] + "XYZ"[:2] + "Q", ""]
            elif qt == "multi3":
                c = list(q["answer"])
                answers = [c, c[:2], c[:2] + ["9"], c + ["8"], [], list(reversed(c))]
            for ans in answers:
                cases.append({"task_id": q["id"], "answer": ans, "expected": list(engine.evaluate_answer(q, ans))})
    extra_task = {"qtype": "short", "answer": "-2,5", "max_points": 2}
    for ans in ["-2.5", "−2,5", "-2 , 5", "-2.50", "2.5", "-2.5000001", "-2.50000001"]:
        cases.append({"task": extra_task, "answer": ans, "expected": list(engine.evaluate_answer(extra_task, ans))})
    latin = {"qtype": "single", "answer": "В", "labels": ["А", "Б", "В", "Г"], "options": ["1", "2", "3", "4"]}
    for ans in ["B", "b", "В", "A", "C"]:
        cases.append({"task": latin, "answer": ans, "expected": list(engine.evaluate_answer(latin, ans))})
    return cases


def nmt_cases():
    out = []
    for sid in SUBJECTS_ORDER:
        for raw in range(-1, SUBJECTS_CONFIG[sid]["max_score"] + 3):
            out.append({"subject": sid, "raw": raw, "expected": score_to_nmt200(sid, raw)})
        out.append({"subject": sid, "raw": 10.5, "expected": score_to_nmt200(sid, 10.5)})
    return out


def hint_cases():
    out = []
    for tasks in get_bank().values():
        for q in tasks:
            out.append({"task_id": q["id"], "expected": hints.build_10_hints(q)})
    return out


def _fake_block(sid, rng):
    tasks = list(get_bank()[sid])
    rng.shuffle(tasks)
    qs = tasks[: rng.randint(3, 8)]
    block = engine.new_block(sid, [dict(q) for q in qs])
    for i, q in enumerate(qs):
        r = rng.random()
        if r < 0.15:
            continue
        mx = q.get("max_points", 1)
        pts = mx if r > 0.55 else rng.randint(0, mx)
        block["points"][i] = pts
        if pts < mx:
            block["mistakes"].append(i)
    block["drills_done"] = rng.randint(0, 3)
    return block


def summary_cases():
    rng = random.Random(7)
    out = []
    for sid in SUBJECTS_ORDER:
        if not get_bank().get(sid):
            continue
        for _ in range(4):
            block = _fake_block(sid, rng)
            out.append({"block": _jsonable_block(block), "summary": engine.compute_subject_summary(block),
                        "score": list(engine.block_score(block))})
    return out


def _jsonable_block(block):
    b = dict(block)
    b["questions"] = [q["id"] for q in block["questions"]]
    b["points"] = {str(k): v for k, v in block["points"].items()}
    b["answers"] = {}
    b["answer_log"] = {}
    return b


def cabinet_cases():
    """Results like the ones storage keeps, and what cabinet.py makes of them."""
    rng = random.Random(11)
    results = []
    day = 1
    for n in range(14):
        subjects = rng.sample(["ukrmova", "math", "history", "english", "biology"], rng.randint(1, 3))
        plan = [_fake_block(sid, rng) for sid in subjects]
        drill = n % 5 == 4
        focus = "Планіметрія" if (n % 6 == 5 and "math" in subjects) else None
        payload = engine.build_session_result(plan, rng.choice(["quick", "medium", "full"]), rng.random() > 0.3,
                                              mistake_drill=drill, focus_section=focus,
                                              report_id=(n if n % 3 else None))
        payload["finished_at"] = f"2026-10-{day:02d}T1{n % 10}:0{n % 6}:00"
        day += rng.randint(0, 2)
        rec = dict(payload)  # what Repository.list_results() returns
        rec.update(id=n + 1, created_at=payload["finished_at"])
        results.append(rec)
    profile = {"targets": {"math": 180, "ukrmova": 150}, "subjects": ["ukrmova", "math", "history"]}
    subjects = sorted({s["subject"] for r in results for s in r["subjects"]})
    return {
        "results": results,
        "profile": profile,
        "subject_stats": {sid: cabinet.subject_stats(results, sid, profile) for sid in subjects},
        "cabinet_subjects": cabinet.cabinet_subjects(results, profile),
        "progress_series": {sid: cabinet.progress_series(results, sid) for sid in subjects},
        "weak_topics": cabinet.weak_topics(results),
        "weak_topics_math": cabinet.weak_topics(results, subjects=["math"], limit=3),
        "history": cabinet.history(results),
        "history_3": cabinet.history(results, limit=3),
        "session_modes": [cabinet.session_mode(r) for r in results],
        "format_when": {w: cabinet.format_when(w) for w in ["2026-10-01T10:05:00", "", "bad", "2026-01-31T23:59:59"]},
    }


def export_fixtures():
    write(FIXTURES, "evaluate.json", evaluate_cases())
    write(FIXTURES, "nmt200.json", nmt_cases())
    write(FIXTURES, "hints.json", hint_cases())
    write(FIXTURES, "summary.json", summary_cases())
    write(FIXTURES, "cabinet.json", cabinet_cases())


if __name__ == "__main__":
    export_data()
    export_fixtures()
