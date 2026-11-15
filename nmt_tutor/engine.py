"""Test engine: answer checking, test assembly, identical drills, scoring and the text report."""

import random
from datetime import datetime

from .config import SUBJECTS_CONFIG, score_to_nmt200
from .data import get_bank
from .generators import generators_for_subject, get_generator, has_generator

# Latin letters that look like Cyrillic answer labels (A/А, B/В, C/С, ...).
_LABEL_EQUIV = {"A": "А", "B": "В", "C": "С", "E": "Е", "K": "К", "M": "М", "O": "О", "P": "Р", "T": "Т", "X": "Х"}
_MATCH_EQUIV = {"A": "А", "B": "В", "C": "С", "E": "Е"}


def _normalize_num_str(s):
    return str(s).strip().replace(",", ".").replace(" ", "").replace("−", "-")


def _nums_equal(a, b):
    na = _normalize_num_str(a)
    nb = _normalize_num_str(b)
    if na.lower() == nb.lower():
        return True
    try:
        return abs(float(na) - float(nb)) < 1e-6
    except ValueError:
        return False


def _same_label(a, b, equiv):
    return a == b or equiv.get(a) == b or equiv.get(b) == a


def is_empty_answer(ans):
    """True when the student has not chosen or typed anything yet."""
    return ans in ("", []) or (isinstance(ans, dict) and not any(ans.values()))


def evaluate_answer(q, user_ans):
    """
    Перевіряє відповідь учня на запитання q.
    Повертає (is_full_correct: bool, earned_points: int, student_repr: str, correct_repr: str).
    """
    qt = q["qtype"]
    max_pts = q.get("max_points", 1)

    if qt == "single":
        ans = str(user_ans).strip().upper()
        corr = str(q["answer"]).strip().upper()
        labels = [str(l).upper() for l in q.get("labels", [])]
        is_ok = _same_label(ans, corr, _LABEL_EQUIV)
        opts = q.get("options", [])

        def _fmt_opt(lbl):
            for l, o in zip(labels, opts):
                if _same_label(l, lbl, _LABEL_EQUIV):
                    return f"{lbl} ({o})"
            return lbl or "—"

        return is_ok, (max_pts if is_ok else 0), _fmt_opt(ans), _fmt_opt(corr)

    if qt == "short":
        ans_raw = str(user_ans).strip()
        corr_raw = str(q["answer"]).strip()
        is_ok = bool(ans_raw) and _nums_equal(ans_raw, corr_raw)
        return is_ok, (max_pts if is_ok else 0), (ans_raw or "—"), corr_raw

    if qt == "matching":
        corr_map = q["answer"]
        u_map = user_ans if isinstance(user_ans, dict) else {}
        pts = 0
        u_parts, c_parts = [], []
        for k in sorted(corr_map.keys()):
            c_val = str(corr_map[k]).strip().upper()
            u_val = str(u_map.get(k, "")).strip().upper()
            if _same_label(u_val, c_val, _MATCH_EQUIV):
                pts += 1
            u_parts.append(f"{k}–{u_val or '?'}")
            c_parts.append(f"{k}–{c_val}")
        is_ok = (pts == len(corr_map))
        return is_ok, min(pts, max_pts), ", ".join(u_parts), ", ".join(c_parts)

    if qt == "sequence":
        u_str = str(user_ans).strip().upper().replace(" ", "").replace("-", "").replace("–", "")
        c_str = str(q["answer"]).strip().upper()
        # Бали НМТ за послідовність: 3 бали — усі 4, 2 — перша й остання, 1 — перша або остання
        pts = 0
        if len(u_str) == 4 and len(c_str) == 4:
            if u_str == c_str:
                pts = 3
            elif u_str[0] == c_str[0] and u_str[3] == c_str[3]:
                pts = 2
            elif u_str[0] == c_str[0] or u_str[3] == c_str[3]:
                pts = 1
        return (u_str == c_str), pts, (u_str or "—"), c_str

    if qt == "multi3":
        u_set = sorted(set(str(x).strip() for x in (user_ans or [])))
        c_set = sorted(set(str(x).strip() for x in q["answer"]))
        # У НМТ за 3 відповіді з 7: 1 бал за кожну правильну, якщо обрано не більше 3
        if len(u_set) > 3:
            pts = max(0, 3 - len(u_set))
        else:
            pts = sum(1 for x in u_set if x in c_set)
        is_ok = (u_set == c_set)
        return is_ok, pts, (", ".join(u_set) or "—"), ", ".join(c_set)

    return False, 0, str(user_ans), str(q.get("answer", ""))


def generate_identical_drill(q, used_prompts=None):
    """
    Генерує ідентичний за правилом/структурою тренувальний приклад (із новими числами або словами).
    Якщо генератор для drill_key недоступний, підбирає паралельне завдання з того ж розділу.
    """
    used = set(used_prompts or [])
    used.add(q.get("prompt", ""))
    dkey = q.get("drill_key")

    gen_fn = get_generator(dkey) if has_generator(dkey) else None
    if gen_fn is not None:
        for _ in range(15):
            cand = gen_fn()
            if cand["prompt"] not in used:
                cand["is_drill"] = True
                return cand
        cand = gen_fn()
        cand["is_drill"] = True
        return cand

    # Запасний варіант: випадковий генератор предмета або інше завдання з того ж розділу
    subj = q.get("subject", "math")
    gens = generators_for_subject(subj)
    if gens:
        cand = get_generator(random.choice(gens))()
        cand["is_drill"] = True
        return cand

    pool = [item for item in get_bank().get(subj, []) if item.get("prompt") != q.get("prompt")]
    if pool:
        cand = dict(random.choice(pool))
        cand["is_drill"] = True
        return cand

    fallback = dict(q)
    fallback["is_drill"] = True
    return fallback


def generate_test_for_subject(subject_id, length_mode="quick", custom_bank=None):
    """
    Збирає випадковий варіант тесту з обраного предмета згідно з програмою НМТ 2022–2026.
    length_mode: 'quick' (8 завдань), 'medium' (15 завдань), 'full' (офіційна кількість: 22/24/30/32).
    """
    cfg = SUBJECTS_CONFIG[subject_id]
    if length_mode == "quick":
        target_n = 8
    elif length_mode == "medium":
        target_n = min(15, cfg["total_tasks"])
    else:
        target_n = cfg["total_tasks"]

    questions = []
    seen_prompts = set()

    # 1. Користувацькі завдання із завантаженого JSON (якщо є)
    if custom_bank and subject_id in custom_bank:
        custom_pool = list(custom_bank[subject_id])
        random.shuffle(custom_pool)
        for q in custom_pool:
            if len(questions) >= target_n:
                break
            if q.get("prompt") not in seen_prompts:
                questions.append(dict(q))
                seen_prompts.add(q.get("prompt"))

    # 2. Офіційні завдання 2026 року з банку (у випадковому порядку)
    static_pool = list(get_bank().get(subject_id, []))
    random.shuffle(static_pool)
    # Kept as in v3.5: this bound never stops the loop early, so the bank fills
    # the test up to target_n before generators are used.
    static_limit = target_n if length_mode == "full" else max(3, target_n // 2)
    for q in static_pool:
        if len(questions) >= min(target_n, static_limit + len(questions)):
            break
        if q["prompt"] not in seen_prompts:
            questions.append(dict(q))
            seen_prompts.add(q["prompt"])
        if len(questions) >= target_n:
            break

    # 3. Добираємо решту завдань динамічними генераторами за програмою НМТ
    gens = generators_for_subject(subject_id)
    attempts = 0
    while len(questions) < target_n and attempts < target_n * 8:
        attempts += 1
        if gens:
            gkey = gens[(len(questions) + attempts) % len(gens)]
            cand = get_generator(gkey)()
            if cand["prompt"] not in seen_prompts or attempts > target_n * 4:
                cand["id"] = f"{subject_id}_gen_{len(questions)+1}_{random.randint(100,999)}"
                questions.append(cand)
                seen_prompts.add(cand["prompt"])
        elif static_pool:
            cand = dict(random.choice(static_pool))
            cand["id"] = f"{subject_id}_rep_{len(questions)+1}"
            questions.append(cand)
        else:
            break

    return questions


def new_block(subject_id, questions):
    return {
        "subject": subject_id,
        "questions": questions,
        "answers": {},
        "points": {},
        "mistakes": [],
        "drills_done": 0,
    }


def build_session_plan(selected_subjects, length_mode="quick", custom_bank=None):
    """Створює повний план тестування з усіх обраних користувачем предметів."""
    return [
        new_block(subj_id, generate_test_for_subject(subj_id, length_mode=length_mode, custom_bank=custom_bank))
        for subj_id in selected_subjects
    ]


def build_mistake_drill_plan(plan):
    """One identical example for every mistake of the finished session."""
    drill_plan = []
    for block in plan:
        if block["mistakes"]:
            qs = [generate_identical_drill(block["questions"][idx]) for idx in block["mistakes"]]
            drill_plan.append(new_block(block["subject"], qs))
    return drill_plan


def block_score(block):
    """(earned points, max points) of a block for the live score badge."""
    earned = sum(block["points"].values())
    max_pts = sum(item.get("max_points", 1) for item in block["questions"])
    return earned, max_pts


def compute_subject_summary(block):
    subj_id = block["subject"]
    cfg = SUBJECTS_CONFIG[subj_id]
    qs = block["questions"]
    earned = sum(block["points"].get(i, 0) for i in range(len(qs)))
    actual_max = sum(q.get("max_points", 1) for q in qs) or 1
    is_full = (len(qs) == cfg["total_tasks"] and actual_max == cfg["max_score"])
    projected_raw = earned if is_full else int(round(earned * cfg["max_score"] / actual_max))
    nmt_200 = score_to_nmt200(subj_id, projected_raw)
    weak_sections = {}
    for i in block["mistakes"]:
        sec = qs[i].get("section", "Загальне")
        weak_sections[sec] = weak_sections.get(sec, 0) + 1
    return {
        "subject": subj_id,
        "name": cfg["name"],
        "earned": earned,
        "actual_max": actual_max,
        "projected_raw": projected_raw,
        "official_max": cfg["max_score"],
        "threshold": cfg["threshold"],
        "nmt_200": nmt_200,
        "is_full": is_full,
        "drills_done": block.get("drills_done", 0),
        "weak_sections": weak_sections,
    }


def build_session_result(plan, length_mode, tutor_mode, mistake_drill=False):
    """Serializable record of a finished session (what storage keeps as progress)."""
    return {
        "finished_at": datetime.now().isoformat(timespec="seconds"),
        "length_mode": length_mode,
        "tutor_mode": bool(tutor_mode),
        "mistake_drill": bool(mistake_drill),
        "subjects": [compute_subject_summary(block) for block in plan],
    }


def format_results_report(plan):
    lines = [
        "=" * 64,
        f"ЗВІТ ЗА РЕЗУЛЬТАТАМИ ТРЕНУВАННЯ НМТ ({datetime.now().strftime('%d.%m.%Y %H:%M')})",
        "=" * 64,
        "",
    ]
    for block in plan:
        s = compute_subject_summary(block)
        nmt_str = f"{s['nmt_200']} балів" if s["nmt_200"] is not None else f"Не складено (< {s['threshold']})"
        mode_note = "точний формат" if s["is_full"] else f"прогноз із {s['actual_max']} макс. балів"
        lines.append(f"Предмет: {s['name']}")
        lines.append(f"  Набрано балів: {s['earned']} із {s['actual_max']} ({mode_note})")
        lines.append(f"  Оцінка за шкалою НМТ 100–200: {nmt_str}")
        lines.append(f"  Опрацьовано ідентичних прикладів із репетитором: {s['drills_done']}")
        if s["weak_sections"]:
            lines.append("  Теми для повторення:")
            for sec, cnt in s["weak_sections"].items():
                lines.append(f"    • {sec} (помилок: {cnt})")
        else:
            lines.append("  Помилок не виявлено!")
        lines.append("")
    return "\n".join(lines)
