"""Headless self-test of the core, the encrypted storage and profiles (no windows).

Used by tests/smoke_test.py, by CI and by packaged builds: `nmt_tutor_mac.py --selftest [--out FILE]`.
"""

import os
import random
import shutil
import tempfile
import traceback


def _check_core():
    from .banks import CUSTOM_BANK_TEMPLATE, validate_custom_bank
    from .config import SUBJECTS_ORDER
    from .data import bank_size
    from .engine import (build_mistake_drill_plan, build_session_plan, build_session_result,
                         compute_subject_summary, evaluate_answer, format_results_report,
                         generate_identical_drill)
    from .generators import generator_count, load_all
    from .hints import build_10_hints

    assert bank_size() == 189, f"bank has {bank_size()} tasks"
    gens = load_all()
    assert len(gens) == generator_count() == 40, f"{len(gens)} generators"
    rnd_state = random.getstate()
    try:
        random.seed(2026)
        for key, fn in sorted(gens.items()):
            for _ in range(5):
                q = fn()
                ok, pts, _, _ = evaluate_answer(q, q["answer"])
                assert ok and pts == q.get("max_points", 1), f"generator {key}: own answer not accepted"
                assert len(build_10_hints(q)) == 10
        plan = build_session_plan(SUBJECTS_ORDER, "full")
        for block in plan:
            for i, q in enumerate(block["questions"]):
                ok, pts, _, _ = evaluate_answer(q, q["answer"] if i % 3 else "")
                block["points"][i] = pts
                block["answers"][i] = q["answer"]
                if not ok:
                    block["mistakes"].append(i)
                assert len(build_10_hints(q)) == 10
                generate_identical_drill(q)
            s = compute_subject_summary(block)
            assert 100 <= (s["nmt_200"] or 100) <= 200
        assert build_mistake_drill_plan(plan)
        assert "ЗВІТ" in format_results_report(plan)
        assert validate_custom_bank(CUSTOM_BANK_TEMPLATE)
        return plan, build_session_result(plan, "full", True)
    finally:
        random.setstate(rnd_state)


def _check_storage(result, keystore):
    from . import storage
    from .storage import paths

    old_override = paths._override
    tmp = tempfile.mkdtemp(prefix="nmt_selftest_")
    try:
        repo = storage.open_repository(tmp, keystore=keystore)
        repo.save_result(result)
        repo.save_report("selftest report", title="selftest")
        repo.save_custom_bank("selftest.json", {"math": [{"prompt": "1+1", "answer": "2", "qtype": "short"}]})
        repo.close()
        repo = storage.open_repository(tmp, keystore=keystore)
        assert len(repo.list_results()) == 1 and repo.get_progress()
        assert repo.get_report(repo.list_reports()[0]["id"])["text"] == "selftest report"
        assert repo.load_custom_banks()["math"][0]["answer"] == "2"
        repo.close()
        with open(paths.db_path(), "rb") as f:
            raw = f.read()
        assert b"selftest report" not in raw, "report stored in clear text"
    finally:
        paths.set_data_dir(old_override)
        shutil.rmtree(tmp, ignore_errors=True)


def _check_profiles(result, keystore):
    """Profiles in the encrypted store: data split per profile, sign-in lookup, PIN, cabinet numbers."""
    from . import storage
    from .auth.local import PinGuard, hash_pin
    from .cabinet import history, progress_series, subject_stats, weak_topics
    from .profiles import link_identity, new_profile
    from .storage import paths

    old_override = paths._override
    tmp = tempfile.mkdtemp(prefix="nmt_selftest_")
    try:
        repo = storage.open_repository(tmp, keystore=keystore, import_legacy=False)
        repo.save_result(result)  # data from before profiles
        a = new_profile("Selftest A", subjects=["math"], targets={"math": 180}, exam_date="20.05.2027")
        a["pin"] = hash_pin("2468")
        link_identity(a, "google", "selftest-sub-1")
        repo.save_profile(a)
        assert repo.assign_unassigned(a["id"]) == 1
        b = new_profile("Selftest B")
        repo.save_profile(b)
        repo.for_profile(b["id"]).save_report("only b", "b")
        repo.close()
        repo = storage.open_repository(tmp, keystore=keystore, import_legacy=False)
        sa, sb = repo.for_profile(a["id"]), repo.for_profile(b["id"])
        assert len(sa.list_results()) == 1 and sb.list_results() == []
        assert sa.list_reports() == [] and len(sb.list_reports()) == 1
        assert repo.find_profile_by_identity("google", "selftest-sub-1")["id"] == a["id"]
        assert PinGuard().check(repo.get_profile(a["id"]), "2468")[0]
        assert not PinGuard().check(repo.get_profile(a["id"]), "1111")[0]
        results = sa.list_results()
        for sid in [s["subject"] for s in result["subjects"]]:
            subject_stats(results, sid, a)
            progress_series(results, sid)
        weak_topics(results)
        assert history(results)[0]["subjects"]
        repo.delete_profile(b["id"])
        assert [p["id"] for p in repo.list_profiles()] == [a["id"]]
        repo.close()
        with open(paths.db_path(), "rb") as f:
            raw = f.read()
        assert b"Selftest A" not in raw and b"selftest-sub-1" not in raw, "profile data stored in clear text"
    finally:
        paths.set_data_dir(old_override)
        shutil.rmtree(tmp, ignore_errors=True)


def run_selftest(keystore=None):
    """Returns (ok, lines). keystore=None uses an in-memory key (never touches the OS key store)."""
    from .storage.keystore import MemoryKeyStore

    lines = []
    ok = True
    result = None
    ks = keystore or MemoryKeyStore()
    checks = (
        ("core", lambda: _check_core()),
        ("storage", lambda: _check_storage(result, ks)),
        ("profiles", lambda: _check_profiles(result, ks)),
    )
    for name, fn in checks:
        try:
            out = fn()
            if name == "core":
                result = out[1]
            lines.append(f"OK    {name}")
        except Exception:
            ok = False
            lines.append(f"FAIL  {name}\n{traceback.format_exc()}")
            if name == "core":
                break
    return ok, lines


def main(argv):
    out = None
    if "--out" in argv:
        out = argv[argv.index("--out") + 1]
    keystore = None
    if "--real-keystore" in argv:
        # OS key store (DPAPI on Windows, Keychain on macOS) under a throwaway name, never the user's key.
        from .storage.keystore import MacKeychainKeyStore, default_keystore
        keystore = default_keystore(os.path.join(tempfile.mkdtemp(prefix="nmt_key_"), ".nmt_tutor_key"))
        if isinstance(keystore, MacKeychainKeyStore):
            keystore = MacKeychainKeyStore(account="selftest-throwaway-key")
    try:
        ok, lines = run_selftest(keystore)
    finally:
        if keystore is not None and hasattr(keystore, "delete_key"):
            try:
                keystore.delete_key()
            except Exception:
                pass
    text = "\n".join(lines) + f"\n{'SELFTEST PASSED' if ok else 'SELFTEST FAILED'}\n"
    if out:
        with open(out, "w", encoding="utf-8") as f:
            f.write(text)
    try:
        print(text)
    except Exception:
        pass  # windowed builds have no console
    return 0 if ok else 1
