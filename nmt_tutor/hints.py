"""Owl helper hint system: 10 levels from a light nudge (1) to the full answer with a story (10)."""

from .config import SUBJECTS_CONFIG


def _clean_text(val):
    return str(val or "").strip()


def _shorten(text, max_len=140):
    t = " ".join(str(text).split())
    if len(t) <= max_len:
        return t
    return t[: max_len - 1].rstrip(" ,;:") + "…"


def _detect_trap(q):
    qt = q.get("qtype", "single")
    prompt = q.get("prompt", "")
    subj = q.get("subject", "")
    p_low = prompt.lower()

    if "окрім" in p_low or "не треба" in p_low or "не потрібно" in p_low or "не мають" in p_low or "не відбулася" in p_low:
        return "Типова пастка НМТ: у запитанні є заперечення («ОКРІМ» / «НЕ»). Шукай саме той ОДИН рядок, який порушує правило, а не підходить під нього!"
    if qt == "short":
        if subj in ("math", "physics", "chemistry", "geography"):
            return "Типова пастка НМТ для короткої відповіді: перевір одиниці виміру, знак (плюс/мінус) і запис дробу через кому чи ціле число."
        return "Типова пастка НМТ: уважно перечитай, що саме просять записати у відповідь — кінцеву величину чи проміжний крок."
    if qt == "matching":
        return "Типова пастка в логічних парах: праворуч завжди є ОДИН зайвий варіант-приманка (5 варіантів на 4 рядки або 5 на 3). Не притягуй його силоміць!"
    if qt == "sequence":
        return "Типова пастка хронології: події можуть бути дуже близько за роками або належати до однієї доби. Найперше знайди «якорі» — найдавнішу (1) та найпізнішу (4) подію."
    if qt == "multi3":
        return "Типова пастка «3 із 7»: серед варіантів підмішано події чи ознаки з ІНШОЇ епохи або іншого явища, які звучать правдоподібно, але не стосуються зазначеного періоду."
    if subj in ("english", "german", "french", "spanish"):
        return "Типова пастка іноземної мови на НМТ: «хибні друзі» та схожі за звучанням слова з тексту (наприклад, часова форма, число підмета або прийменник після пропуску)."
    if subj == "math":
        return "Типова пастка математики: зверни увагу на знаки нерівностей (> чи ≥), мінус перед дужками, від’ємні степені (a⁻¹ = 1/a) та ОДЗ."
    return "Типова пастка НМТ: 1–2 варіанти спеціально складено так, щоб спіймати на неуважному читанні умови або плутанині схожих термінів."


def _detect_markers(q):
    qt = q.get("qtype", "single")
    subj = q.get("subject", "")
    prompt = q.get("prompt", "")

    if qt == "matching":
        left = q.get("left", [])
        return f"Подивись на ключові слова ліворуч (особливо на пункт «{left[0] if left else '1'}») та знайди до нього точну ознаку серед варіантів А–Д."
    if qt == "sequence":
        return "Підкресли подумки всі 4 події та пригадай століття або десятиліття для кожної з них — так одразу стане видно першу й останню позицію."
    if qt == "multi3":
        return "Виділи в умові часові рамки або головний критерій відбору (що саме має виконуватися одночасно для всіх 3 правильних пунктів)."
    if subj in ("english", "german", "french", "spanish"):
        if "_______" in prompt:
            return "Подивись на 2–3 слова БЕЗПОСЕРЕДНЬО перед пропуском і після нього: чи є там прийменник, союз, маркер часу або підмет в однині/множині?"
        return "Знайди в тексті ключові слова-синоніми: на НМТ правильний варіант майже ніколи не повторює слова тексту дослівно, а перефразовує їх."
    if subj in ("math", "physics", "chemistry", "geography"):
        return "Випиши окремо всі числа, коефіцієнти та невідому величину з умови. Перевір, чи не потрібне переведення одиниць (%, см у м, хв у с, л у молі)."
    return "Виділи головні опорні слова в самому запитанні — саме в них схована умова, яка відрізняє правильний рядок від решти."


def _rephrase_simple(q):
    subj = q.get("subject", "")
    qt = q.get("qtype", "single")
    sec = q.get("section", "")
    if qt == "matching":
        return f"Простими словами: тобі потрібно з’єднати кожен елемент ліворуч (1, 2, 3...) із його точною парою праворуч за темою «{sec}»."
    if qt == "sequence":
        return "Простими словами: розстав ці 4 події на уявній лінії часу — від того, що сталося раніше за все, до найновішої події."
    if qt == "multi3":
        return "Простими словами: з 7 пунктів потрібно залишити лише 3 беззаперечно правильні, а 4 зайві — відкинути."
    if qt == "short":
        return f"Простими словами: тут немає готових варіантів, тому потрібно акуратно обчислити точне число за правилами розділу «{sec}»."
    if subj in ("english", "german", "french", "spanish"):
        return f"Простими словами: перевіряється твоє вміння в розділі «{sec}» — відчути контекст і підібрати єдину граматично/лексично точну форму."
    return f"Простими словами: завдання перевіряє одне базове вміння з теми «{sec}» — відокреми правильний мовний/науковий факт від схожих помилок."


def _build_elimination_hint(q):
    qt = q.get("qtype", "single")
    if qt == "single":
        labels = q.get("labels", [])
        opts = q.get("options", [])
        corr = str(q.get("answer", "")).strip().upper()
        wrongs = [(l, o) for l, o in zip(labels, opts) if str(l).strip().upper() != corr]
        if len(wrongs) >= 2:
            w1, w2 = wrongs[0], wrongs[1]
            return f"Відсіювання зайвого: варіанти {w1[0]} («{_shorten(w1[1], 45)}») та {w2[0]} («{_shorten(w2[1], 45)}») точно НЕ підходять — сміливо викреслюй їх!"
        if wrongs:
            return f"Відсіювання зайвого: варіант {wrongs[0][0]} («{_shorten(wrongs[0][1], 55)}») можна одразу виключити."
    elif qt == "matching":
        ans_map = q.get("answer", {})
        used_letters = set(str(v).upper() for v in ans_map.values())
        all_letters = list((q.get("right") or {}).keys())
        extra = [k for k in all_letters if k.upper() not in used_letters]
        if extra:
            ex_k = extra[0]
            ex_v = _shorten(q["right"][ex_k], 60)
            return f"Відсіювання зайвого: варіант {ex_k} («{ex_v}») є зайвим дистрактором і не підходить до жодного рядка!"
    elif qt == "sequence":
        ans = str(q.get("answer", ""))
        if len(ans) == 4:
            return f"Відсіювання зайвого: найпізніша подія в цьому наборі точно НЕ перша, а найдавніша — точно НЕ {ans[-1]}."
    elif qt == "multi3":
        corr = set(str(x) for x in q.get("answer", []))
        items = q.get("items", {})
        wrongs = [(k, v) for k, v in items.items() if str(k) not in corr]
        if len(wrongs) >= 2:
            return f"Відсіювання зайвого: пункти {wrongs[0][0]} («{_shorten(wrongs[0][1], 42)}») та {wrongs[1][0]} («{_shorten(wrongs[1][1], 42)}») стосуються іншого — сміливо відкидай їх!"
    elif qt == "short":
        ans_raw = str(q.get("answer", "")).strip().replace(",", ".")
        try:
            val = float(ans_raw)
            if val >= 0:
                return f"Оцінка результату: відповідь — невід’ємне число (близько до порядку величини {int(round(val)) if abs(val) < 10 else round(val, -1) if abs(val) >= 20 else round(val, 1)}), від’ємні варіанти тут неможливі."
            return "Оцінка результату: зверни увагу, що у відповіді має вийти ВІД’ЄМНЕ число (зі знаком «−»)."
        except Exception:
            pass
    return "Відсіювання зайвого: відкинь варіанти, які суперечать основному правилу або стосуються іншого часу/теми."


def _build_step1_hint(q):
    qt = q.get("qtype", "single")
    sol_lines = [ln.strip() for ln in _clean_text(q.get("solution", "")).splitlines() if ln.strip()]
    if qt == "matching":
        ans_map = q.get("answer", {})
        left = q.get("left", [])
        if ans_map and left:
            k1 = sorted(ans_map.keys())[0]
            v1 = ans_map[k1]
            return f"Перший крок: почни з першої пари — для пункту «{_shorten(left[0], 55)}» точно підходить буква {v1}."
    if qt == "sequence":
        ans = str(q.get("answer", ""))
        items = q.get("items", {})
        if len(ans) == 4 and ans[0] in items:
            return f"Перший крок: найдавнішою подією є {ans[0]} («{_shorten(items[ans[0]], 60)}») — постав її на 1-ше місце!"
    if qt == "multi3":
        corr = sorted(str(x) for x in q.get("answer", []))
        items = q.get("items", {})
        if corr and corr[0] in items:
            return f"Перший крок: один із трьох правильних пунктів — це {corr[0]} («{_shorten(items[corr[0]], 60)}»)."
    if qt == "single":
        labels = q.get("labels", [])
        opts = q.get("options", [])
        corr = str(q.get("answer", "")).strip().upper()
        c_pair = [(l, o) for l, o in zip(labels, opts) if str(l).strip().upper() == corr]
        w_pairs = [(l, o) for l, o in zip(labels, opts) if str(l).strip().upper() != corr]
        if c_pair and len(w_pairs) >= 1:
            keep = [c_pair[0][0], w_pairs[-1][0]]
            keep.sort()
            return f"Перший крок: після перевірки правила залишаються лише два реальні кандидати — {' та '.join(keep)}."
    if sol_lines:
        first = sol_lines[0]
        ans_str = str(q.get("answer", ""))
        if ans_str and len(ans_str) >= 2 and ans_str in first and qt == "short":
            return "Перший крок: підстав відомі числа з умови у базову формулу й знайди проміжну величину (уважно стеж за діями)."
        return f"Перший крок розв’язання: {_shorten(first, 140)}"
    return "Перший крок: застосуй згадане правило безпосередньо до першого елемента умови."


def _build_step2_hint(q):
    qt = q.get("qtype", "single")
    if qt == "matching":
        ans_map = q.get("answer", {})
        keys = sorted(ans_map.keys())
        if len(keys) >= 2:
            return f"Другий крок: тепер закріплюємо ще одну пару — до позиції {keys[1]} пасує {ans_map[keys[1]]}. Залишилося зовсім небагато!"
    if qt == "sequence":
        ans = str(q.get("answer", ""))
        items = q.get("items", {})
        if len(ans) == 4 and ans[3] in items:
            return f"Другий крок: маємо обидва краї хронології — перша подія {ans[0]}, а найпізніша (4-та) — {ans[3]} («{_shorten(items[ans[3]], 55)}»)."
    if qt == "multi3":
        corr = sorted(str(x) for x in q.get("answer", []))
        items = q.get("items", {})
        if len(corr) >= 2 and corr[1] in items:
            return f"Другий крок: другим правильним пунктом є {corr[1]} («{_shorten(items[corr[1]], 55)}»). Залишилося добрати останній третій!"
    if qt == "single":
        labels = q.get("labels", [])
        opts = q.get("options", [])
        corr = str(q.get("answer", "")).strip().upper()
        c_pair = [(l, o) for l, o in zip(labels, opts) if str(l).strip().upper() == corr]
        w_pairs = [(l, o) for l, o in zip(labels, opts) if str(l).strip().upper() != corr]
        if c_pair and w_pairs:
            trap_l, trap_o = w_pairs[-1]
            return f"Другий крок: порівняй фінальні варіанти — у варіанті {trap_l} («{_shorten(trap_o, 45)}») є прихована невідповідність правилу."
    sol_lines = [ln.strip() for ln in _clean_text(q.get("solution", "")).splitlines() if ln.strip()]
    if len(sol_lines) >= 2:
        return f"Другий крок: {_shorten(sol_lines[1], 140)}"
    return f"Другий крок: зведи всі дані до фінальної перевірки — орієнтуйся на правило: {_shorten(q.get('rule', ''), 110)}"


def _build_near_final_hint(q):
    qt = q.get("qtype", "single")
    if qt == "matching":
        ans_map = q.get("answer", {})
        keys = sorted(ans_map.keys())
        if len(keys) >= 3:
            pairs_txt = ", ".join(f"{k}–{ans_map[k]}" for k in keys[:3])
            return f"Майже фінал! Маємо вже три точні пари: {pairs_txt}. Тобі залишилося визначити лише останню пару ({keys[-1]})!"
    if qt == "sequence":
        ans = str(q.get("answer", ""))
        if len(ans) == 4:
            return f"Майже фінал! Порядок має вигляд {ans[0]} _ _ {ans[3]} — порівняй лише дві середні події між собою."
    if qt == "multi3":
        corr = sorted(str(x) for x in q.get("answer", []))
        if len(corr) >= 2:
            return f"Майже фінал! Два з трьох пунктів — це {corr[0]} і {corr[1]}. Обери останній за змістом теми."
    if qt == "short":
        ans_raw = str(q.get("answer", "")).strip()
        try:
            v = float(ans_raw.replace(",", "."))
            low = round(v * 0.85, 1)
            high = round(v * 1.15, 1)
            if low > high:
                low, high = high, low
            return f"Майже фінал! Після фінальної арифметичної дії ти отримаєш число в межах від {str(low).replace('.', ',')} до {str(high).replace('.', ',')}."
        except Exception:
            pass
    return f"Майже фінал! Усі підготовчі кроки зроблено — зроби фінальний висновок за ключем: {_shorten(q.get('hint', ''), 110)}"


def _build_level10_story(q):
    qt = q.get("qtype", "single")
    subj = q.get("subject", "")
    cfg_name = SUBJECTS_CONFIG.get(subj, {}).get("name", "Предмет НМТ")
    sec = q.get("section", "")
    rule = _clean_text(q.get("rule", ""))
    sol = _clean_text(q.get("solution", ""))

    if qt == "single":
        ans_lbl = str(q.get("answer", "")).strip()
        labels = q.get("labels", [])
        opts = q.get("options", [])
        ans_opt = ""
        for l, o in zip(labels, opts):
            if str(l).strip().upper() == ans_lbl.upper():
                ans_opt = f" ({o})"
                break
        ans_display = f"{ans_lbl}{ans_opt}"
    elif qt == "matching":
        ans_map = q.get("answer", {})
        ans_display = ", ".join(f"{k}–{ans_map[k]}" for k in sorted(ans_map.keys()))
    elif qt == "multi3":
        ans_display = ", ".join(str(x) for x in q.get("answer", []))
    else:
        ans_display = str(q.get("answer", ""))

    story = (
        f"🦉 Повна відповідь і розповідь Сови-Лізи:\n"
        f"✅ Правильна відповідь: {ans_display}\n\n"
        f"📖 Чому саме так ({cfg_name} • {sec}):\n"
        f"Уяви, як працює це правило на практиці: {rule}\n\n"
        f"🔍 Як це спрацювало саме тут:\n{sol}\n\n"
        f"💡 Запам’ятай цю логіку — на НМТ подібні завдання трапляються постійно, але змінюють лише слова або числа!"
    )
    return story


def build_10_hints(q):
    """Повертає список із 10 послідовних підказок: від дуже легкого натяку (1) до повної відповіді з розповіддю (10)."""
    custom = q.get("hints_10")
    if isinstance(custom, list) and len(custom) == 10:
        return custom

    subj_name = SUBJECTS_CONFIG.get(q.get("subject", ""), {}).get("name", "НМТ")
    sec = q.get("section", "Програма НМТ")

    h1 = f"Рівень 1 (Дуже легкий натяк): Це завдання з предмета «{subj_name}», тема — «{sec}». Прочитай умову ще раз спокійно, не підглядаючи у варіанти."
    h2 = f"Рівень 2 (Ключовий маркер): {_detect_markers(q)}"
    h3 = f"Рівень 3 (Суть своїми словами): {_rephrase_simple(q)}"
    h4 = f"Рівень 4 (Увага на пастку!): {_detect_trap(q)}"
    h5 = f"Рівень 5 (Натяк Сови): {_clean_text(q.get('hint', 'Зверни увагу на головну деталь в умові.'))}"
    h6 = f"Рівень 6 (Потрібне правило / формула): {_clean_text(q.get('rule', 'Пригадай базове правило цього розділу.'))}"
    h7 = f"Рівень 7 • {_build_elimination_hint(q)}"
    h8 = f"Рівень 8 • {_build_step1_hint(q)}"
    h9 = f"Рівень 9 • {_build_step2_hint(q)} {_build_near_final_hint(q)}"
    h10 = _build_level10_story(q)

    return [h1, h2, h3, h4, h5, h6, h7, h8, h9, h10]
