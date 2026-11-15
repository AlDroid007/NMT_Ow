"""Console mode (`--cli`): the same tests and hints without a GUI."""

from . import APP_TITLE
from .config import SUBJECTS_CONFIG, SUBJECTS_ORDER
from .engine import build_session_plan, evaluate_answer, format_results_report, generate_identical_drill
from .hints import build_10_hints


def _cli_read_answer(q):
    qt = q["qtype"]
    hints10 = build_10_hints(q)
    hint_idx = 0

    def _next_hint():
        nonlocal hint_idx
        if hint_idx < 10:
            print(f"\n🦉 [Підказка {hint_idx + 1}/10]: {hints10[hint_idx]}\n")
            hint_idx += 1
        else:
            print(f"\n🦉 [Усі 10 підказок уже відкрито]:\n{hints10[9]}\n")

    if qt == "single":
        labels = q["labels"]
        for l, o in zip(labels, q["options"]):
            print(f"   {l}) {o}")
        while True:
            ans = input(f"Ваша відповідь ({'/'.join(labels)} або 'h' для підказки 1..10): ").strip()
            if ans.lower() == "h":
                _next_hint()
                continue
            if ans:
                return ans
    elif qt == "short":
        while True:
            ans = input("Введіть числову відповідь (або 'h' для підказки 1..10): ").strip()
            if ans.lower() == "h":
                _next_hint()
                continue
            if ans:
                return ans
    elif qt == "matching":
        for row in q["left"]:
            print(f"   {row}")
        print("Варіанти праворуч:")
        for rk, rv in q["right"].items():
            print(f"   {rk}) {rv}")
        res = {}
        for idx in range(1, len(q["left"]) + 1):
            while True:
                val = input(f"   Пара для {idx} ({'/'.join(q['right'].keys())} або 'h' для підказки): ").strip().upper()
                if val == "H":
                    _next_hint()
                    continue
                res[str(idx)] = val
                break
        return res
    elif qt == "sequence":
        for k, v in q["items"].items():
            print(f"   {k}) {v}")
        while True:
            val = input("Введіть 4 літери в хронологічному порядку (або 'h' для підказки): ").strip().upper()
            if val == "H":
                _next_hint()
                continue
            return val
    elif qt == "multi3":
        for k, v in q["items"].items():
            print(f"   {k}) {v}")
        while True:
            raw = input("Введіть 3 цифри через кому/пробіл (або 'h' для підказки): ").strip()
            if raw.lower() == "h":
                _next_hint()
                continue
            parts = [p for p in raw.replace(",", " ").split() if p.isdigit()]
            return parts
    return ""


def run_cli():
    print("=" * 64)
    print(f"  {APP_TITLE}")
    print("  🦉 Репетитор: Мудра Сова-Ліза (10 рівнів підказок • CLI)")
    print("=" * 64)
    print("\nДоступні предмети НМТ:")
    for idx, sid in enumerate(SUBJECTS_ORDER, 1):
        cfg = SUBJECTS_CONFIG[sid]
        tag = "Обов’язковий" if cfg["mandatory"] else "За вибором"
        print(f" {idx:2d}. {cfg['name']} ({tag}, {cfg['total_tasks']} завдань, макс. {cfg['max_score']} балів)")

    raw_sel = input("\nВведіть номери предметів через кому (Enter = 1,2,3,4 — Укр. мова, Матем., Історія, Англ.): ").strip()
    if not raw_sel:
        selected = ["ukrmova", "math", "history", "english"]
    else:
        selected = []
        for token in raw_sel.replace(",", " ").split():
            if token.isdigit() and 1 <= int(token) <= len(SUBJECTS_ORDER):
                sid = SUBJECTS_ORDER[int(token) - 1]
                if sid not in selected:
                    selected.append(sid)
        if not selected:
            selected = ["english"]

    len_choice = input("Обсяг тесту: [1] Швидке тренування (8 завд.), [2] Середній блок (15 завд.), [3] Повний НМТ: ").strip()
    length_mode = {"2": "medium", "3": "full"}.get(len_choice, "quick")

    tutor_choice = input("Режим: [1] Із Совою-Репетитором (розбір + ідентичні приклади), [2] Іспит: ").strip()
    tutor_mode = (tutor_choice != "2")

    plan = build_session_plan(selected, length_mode=length_mode)
    for block in plan:
        cfg = SUBJECTS_CONFIG[block["subject"]]
        print(f"\n{'='*64}\nПРЕДМЕТ: {cfg['name']} ({len(block['questions'])} завдань)\n{'='*64}")
        for idx, q in enumerate(block["questions"]):
            print(f"\n[{idx+1}/{len(block['questions'])}] ({q['section']} | {q['source']})")
            print(q["prompt"])
            u_ans = _cli_read_answer(q)
            ok, pts, u_repr, c_repr = evaluate_answer(q, u_ans)
            block["answers"][idx] = u_ans
            block["points"][idx] = pts

            if tutor_mode:
                if ok:
                    print(f"\n✅ Сова-Репетитор: Чудово! Твоя відповідь «{u_repr}» абсолютно правильна (+{pts} б.).")
                else:
                    block["mistakes"].append(idx)
                    print(f"\n🦉 Сова-Репетитор: Не хвилюйся, розберімося! Ти відповів(ла) «{u_repr}», а правильна відповідь: «{c_repr}».")
                    print(f"📘 Правило простими словами: {q['rule']}")
                    print(f"🔍 Покроковий розбір: {q['solution']}")
                    print("\n🔁 Нумо одразу закріпимо на ідентичному прикладі!")
                    used_p = [q["prompt"]]
                    for attempt_num in range(1, 3):
                        drill = generate_identical_drill(q, used_prompts=used_p)
                        used_p.append(drill["prompt"])
                        print(f"\n--- Ідентичний приклад #{attempt_num} ---")
                        print(drill["prompt"])
                        d_ans = _cli_read_answer(drill)
                        d_ok, _, d_u, d_c = evaluate_answer(drill, d_ans)
                        block["drills_done"] += 1
                        if d_ok:
                            print(f"✅ Супер! «{d_u}» — правильно! Правило закріплено.")
                            break
                        else:
                            print(f"❌ Поки неточно («{d_u}»). Правильна відповідь: «{d_c}».")
                            print(f"🔍 Розбір прикладу: {drill['solution']}")
            else:
                if not ok:
                    block["mistakes"].append(idx)

    print("\n" + format_results_report(plan))
