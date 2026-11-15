"""Task generators: Математика."""

import math
import random

from ._common import fmt_num, gcd, GEN_SOURCE, register_drill


@register_drill("math_ineq")
def gen_math_ineq():
    a = random.choice([2, 3, 4, 5])
    x_bound = random.randint(4, 12)
    b = random.randint(1, 15)
    c = a * x_bound + b
    step = random.choice([2, 3, 5])
    ans = x_bound + step
    vals = [x_bound - 2 * step, x_bound - step, x_bound, ans, x_bound + 2 * step]
    if vals[0] < 0:
        vals = [0, x_bound - 1, x_bound, ans, ans + step]
    labels = ["А", "Б", "В", "Г", "Д"]
    correct_idx = vals.index(ans)
    return {
        "subject": "math",
        "section": "Рівняння, нерівності та їх системи",
        "source": GEN_SOURCE,
        "qtype": "single",
        "max_points": 1,
        "prompt": f"Позначте з-поміж наведених найменше число, яке є розв’язком нерівності {a}x + {b} > {c}.",
        "options": [str(v) for v in vals],
        "labels": labels,
        "answer": labels[correct_idx],
        "hint": f"Перенеси {b} праворуч, поділи на {a} й уважно подивись на знак: строго '>' чи '≥'!",
        "rule": "Розв’язуємо як звичайне рівняння, але стежимо за строгим знаком '>'. Межове число за строгого знака '>' НЕ є розв’язком!",
        "solution": f"1) {a}x > {c} − {b}\n2) {a}x > {c - b}\n3) x > {x_bound}.\nЧисло {x_bound} не підходить (воно не строго більше за {x_bound}). Найменше із запропонованих чисел, яке більше за {x_bound}, — це {ans} ({labels[correct_idx]}).",
        "drill_key": "math_ineq",
    }


@register_drill("math_percent_trip")
def gen_math_percent_trip():
    base = random.choice([500, 600, 800, 1000, 1200])
    d1 = random.choice([10, 15, 20, 25])
    d2 = random.choice([15, 20, 25, 30])
    total = base + base * (100 - d1) / 100 + base * (100 - d2) / 100
    ans_str = fmt_num(total)
    return {
        "subject": "math",
        "section": "Числа і вирази",
        "source": GEN_SOURCE,
        "qtype": "short",
        "max_points": 2,
        "prompt": (
            f"Сім’я з трьох осіб (батько, мама й дитина) купує квитки на екскурсію. "
            f"Повна вартість становить {base} грн з особи. Мамі надають знижку {d1} %, "
            f"а дитині — {d2} %. Скільки гривень сім’я заплатить за всіх з урахуванням знижок?"
        ),
        "answer": ans_str,
        "hint": f"Якщо знижка {d1}%, то платити потрібно {100 - d1}% від ціни ({base} · {(100 - d1)/100:.2f}). Додай усі три суми.",
        "rule": "Щоб швидко знайти ціну зі знижкою p%, помнож початкову ціну на (100 − p) / 100. Помилку найчастіше роблять, коли знаходять лише розмір знижки й забувають відняти її від початкової ціни.",
        "solution": (
            f"• Батько: {base} грн\n"
            f"• Мама: {base} · {100 - d1}% = {fmt_num(base * (100 - d1) / 100)} грн\n"
            f"• Дитина: {base} · {100 - d2}% = {fmt_num(base * (100 - d2) / 100)} грн\n"
            f"Разом: {ans_str} грн."
        ),
        "drill_key": "math_percent_trip",
    }


@register_drill("math_prob")
def gen_math_prob():
    a = random.randint(3, 9)
    b = random.randint(3, 9)
    c = random.randint(2, 8)
    total = a + b + c
    fav = a + c
    g = gcd(fav, total)
    num, den = fav // g, total // g
    ans_str = f"{num}/{den}"
    candidates = [
        f"{num}/{den}",
        f"{a}/{total}" if gcd(a, total) == 1 else f"{a // gcd(a, total)}/{total // gcd(a, total)}",
        f"{b}/{total}" if gcd(b, total) == 1 else f"{b // gcd(b, total)}/{total // gcd(b, total)}",
        f"1/{fav}",
        f"1/{total}",
    ]
    opts = []
    for cand in candidates:
        if cand not in opts:
            opts.append(cand)
    extra = 1
    while len(opts) < 5:
        cand = f"{extra}/{total + 1}"
        if cand not in opts:
            opts.append(cand)
        extra += 1
    random.shuffle(opts)
    labels = ["А", "Б", "В", "Г", "Д"]
    c_idx = opts.index(ans_str)
    return {
        "subject": "math",
        "section": "Комбінаторика, ймовірність, статистика",
        "source": GEN_SOURCE,
        "qtype": "single",
        "max_points": 1,
        "prompt": (
            f"На столі лежать {total} карток: {a} із зображенням гір, {b} із зображенням моря "
            f"та {c} із зображенням лісу. Яка ймовірність того, що навмання взята картка "
            f"буде із зображенням гір або лісу?"
        ),
        "options": opts,
        "labels": labels,
        "answer": labels[c_idx],
        "hint": "Сполучник «АБО» в імовірності означає ДОДАВАННЯ сприятливих варіантів: (гори + ліс) / усього.",
        "rule": "Класична ймовірність P = m / n, де m — кількість відповідних варіантів («гори або ліс» = додаємо), n — загальна кількість об’єктів. Не забудь скоротити дріб!",
        "solution": f"Усього карток n = {total}. Підходять гори ({a}) або ліс ({c}): m = {a} + {c} = {fav}. P = {fav}/{total} = {ans_str} ({labels[c_idx]}).",
        "drill_key": "math_prob",
    }


@register_drill("math_trap_angle")
def gen_math_trap_angle():
    obtuse = random.choice([105, 110, 115, 120, 125, 130, 135])
    acute = 180 - obtuse
    vals = sorted({acute, obtuse, obtuse // 2, acute - 15, acute + 10})
    while len(vals) < 5:
        vals.append(vals[-1] + 5)
    vals = vals[:5]
    labels = ["А", "Б", "В", "Г", "Д"]
    c_idx = vals.index(acute)
    return {
        "subject": "math",
        "section": "Планіметрія",
        "source": GEN_SOURCE,
        "qtype": "single",
        "max_points": 1,
        "prompt": f"У рівнобічній трапеції ABCD (BC ∥ AD) тупий кут ∠BCD = {obtuse}°. Визначте градусну міру гострого кута ∠BAD.",
        "options": [f"{v}°" for v in vals],
        "labels": labels,
        "answer": labels[c_idx],
        "hint": "У рівнобічної трапеції кути при бічній стороні в сумі дають 180°, а кути при основі рівні.",
        "rule": "Сума односторонніх кутів трапеції при бічній стороні дорівнює 180° (∠B + ∠A = 180°). Оскільки трапеція рівнобічна, ∠B = ∠C, тому ∠A = 180° − ∠C.",
        "solution": f"Оскільки трапеція рівнобічна, ∠ABC = ∠BCD = {obtuse}°. Сума кутів при бічній стороні AB дорівнює 180°, тож ∠BAD = 180° − {obtuse}° = {acute}° ({labels[c_idx]}).",
        "drill_key": "math_trap_angle",
    }


@register_drill("math_exp_eq")
def gen_math_exp_eq():
    base = random.choice([2, 3, 5])
    k = random.randint(1, 4)
    p = random.randint(2, 4)
    ans = k - p
    vals = sorted({ans, -ans if ans != 0 else 5, ans + 2, ans - 2, p + k})
    while len(vals) < 5:
        vals.append(vals[-1] + 1)
    vals = vals[:5]
    labels = ["А", "Б", "В", "Г", "Д"]
    c_idx = vals.index(ans)
    return {
        "subject": "math",
        "section": "Рівняння, нерівності та їх системи",
        "source": GEN_SOURCE,
        "qtype": "single",
        "max_points": 1,
        "prompt": f"Розв’яжіть рівняння {base}^(x + {k}) = {base**p} · {base**2}^x.",
        "options": [str(v) for v in vals],
        "labels": labels,
        "answer": labels[c_idx],
        "hint": f"Зведи всі числа до однієї основи {base}: {base**p} = {base}^{p}, а {base**2} = {base}^2.",
        "rule": "Показникове рівняння розв’язується зведенням обох частин до спільної основи: a^f(x) = a^g(x) ⇒ f(x) = g(x). Під час множення степенів показники ДОДАЮТЬСЯ.",
        "solution": (
            f"1) Запишемо через основу {base}: {base}^(x + {k}) = {base}^{p} · {base}^(2x) = {base}^({p} + 2x)\n"
            f"2) Прирівнюємо показники: x + {k} = {p} + 2x\n"
            f"3) Звідси x = {k} − {p} = {ans} ({labels[c_idx]})."
        ),
        "drill_key": "math_exp_eq",
    }


@register_drill("math_deriv_ext")
def gen_math_deriv_ext():
    pairs = [(-3, 5), (-2, 4), (-1, 3), (-3, 3), (-2, 6), (-1, 5)]
    r1, r2 = random.choice(pairs)
    b_coef = -3 * (r1 + r2) // 2
    c_coef = 3 * r1 * r2
    d_coef = random.randint(1, 15)
    want_max = random.choice([True, False])
    target_word = "максимуму" if want_max else "мінімуму"
    ans = r1 if want_max else r2
    b_str = f"+ {b_coef}" if b_coef >= 0 else f"− {abs(b_coef)}"
    c_str = f"+ {c_coef}" if c_coef >= 0 else f"− {abs(c_coef)}"
    return {
        "subject": "math",
        "section": "Функції",
        "source": GEN_SOURCE,
        "qtype": "short",
        "max_points": 2,
        "prompt": f"Визначте точку {target_word} функції f(x) = x³ {b_str}x² {c_str}x + {d_coef}.",
        "answer": fmt_num(ans),
        "hint": "Знайди похідну f'(x), прирівняй її до 0, знайди критичні точки та перевір знак похідної (перехід із '+' на '−' дає максимум, із '−' на '+' — мінімум).",
        "rule": "Для кубічної параболи з +x³ вітки похідної f'(x) напрямлені вгору (+, −, +). Тому менший корінь завжди точка МАКСИМУМУ, а більший — точка МІНІМУМУ!",
        "solution": (
            f"1) f'(x) = 3x² {2*b_coef:+d}x {c_coef:+d} = 0\n"
            f"2) Поділимо на 3: x² {2*b_coef//3:+d}x {c_coef//3:+d} = 0\n"
            f"3) Корені: x₁ = {r1}, x₂ = {r2}.\n"
            f"4) Знаки похідної: (+) на (−∞; {r1}), (−) на ({r1}; {r2}), (+) на ({r2}; +∞).\n"
            f"Точка {target_word}: {ans}."
        ),
        "drill_key": "math_deriv_ext",
    }


@register_drill("math_vector")
def gen_math_vector():
    triples = [(1, 2, 2), (2, 3, 6), (1, 4, 8), (2, 1, 2), (3, 4, 0)]
    cx, cy, cz = random.choice(triples)
    mod_c = int(round(math.sqrt(cx*cx + cy*cy + cz*cz)))
    ax = random.randint(-4, 4)
    ay = random.randint(-4, 4)
    az = random.randint(-4, 4)
    bx, by, bz = cx - ax, cy - ay, cz - az
    vals = sorted({mod_c, abs(cx) + abs(cy) + abs(cz), mod_c + 2, max(1, mod_c - 1), mod_c * mod_c})
    while len(vals) < 5:
        vals.append(vals[-1] + 1)
    vals = vals[:5]
    labels = ["А", "Б", "В", "Г", "Д"]
    c_idx = vals.index(mod_c)
    return {
        "subject": "math",
        "section": "Стереометрія",
        "source": GEN_SOURCE,
        "qtype": "single",
        "max_points": 1,
        "prompt": f"У прямокутній системі координат у просторі задано вектори a({ax}; {ay}; {az}) і b({bx}; {by}; {bz}). Визначте модуль вектора c = a + b.",
        "options": [str(v) for v in vals],
        "labels": labels,
        "answer": labels[c_idx],
        "hint": "Спочатку додай відповідні координати (x₁+x₂; y₁+y₂; z₁+z₂), потім знайди довжину √(x² + y² + z²).",
        "rule": "Координати суми векторів дорівнюють сумі їхніх координат. Модуль (довжина) вектора (x; y; z) дорівнює √(x² + y² + z²).",
        "solution": f"1) c = ({ax}+{bx}; {ay}+{by}; {az}+{bz}) = ({cx}; {cy}; {cz}).\n2) |c| = √({cx}² + {cy}² + {cz}²) = √{cx*cx+cy*cy+cz*cz} = {mod_c} ({labels[c_idx]}).",
        "drill_key": "math_vector",
    }


@register_drill("math_module_pow")
def gen_math_module_pow():
    d = random.choice([2, 4, 5, 10])
    b = random.choice([2, 3, 4, 5])
    val = abs(1.0 / d - b)
    ans = fmt_num(val)
    neg = fmt_num(-val)
    wrong1 = fmt_num(d + b)
    wrong2 = fmt_num(1.0 / d + b)
    wrong3 = fmt_num(val + 0.5)
    opts = []
    for x in [ans, neg, wrong1, wrong2, wrong3]:
        if x not in opts:
            opts.append(x)
    while len(opts) < 5:
        opts.append(fmt_num(val + len(opts)))
    random.shuffle(opts)
    labels = ["А", "Б", "В", "Г", "Д"]
    c_idx = opts.index(ans)
    return {
        "subject": "math",
        "section": "Числа і вирази",
        "source": GEN_SOURCE,
        "qtype": "single",
        "max_points": 1,
        "prompt": f"Обчисліть значення виразу |{d}⁻¹ − {b}|.",
        "options": opts,
        "labels": labels,
        "answer": labels[c_idx],
        "hint": f"Увага! {d}⁻¹ — це НЕ −{d}, а дріб 1/{d}! І модуль числа завжди ≥ 0.",
        "rule": "Дві головні пастки НМТ: 1) a⁻¹ = 1/a (від’ємний показник перевертає число, а не змінює знак); 2) модуль |x| завжди невід’ємний.",
        "solution": f"1) {d}⁻¹ = 1/{d} = {fmt_num(1.0/d)}.\n2) {fmt_num(1.0/d)} − {b} = {fmt_num(1.0/d - b)}.\n3) |{fmt_num(1.0/d - b)}| = {ans} ({labels[c_idx]}).",
        "drill_key": "math_module_pow",
    }
