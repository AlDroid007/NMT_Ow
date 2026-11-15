"""Task generators: Фізика."""

import random

from ._common import fmt_num, GEN_SOURCE, register_drill


@register_drill("phys_free_fall")
def gen_phys_free_fall():
    t = random.choice([2, 3, 4, 5, 6])
    h = 5 * t * t
    return {
        "subject": "physics",
        "section": "Механіка",
        "source": GEN_SOURCE,
        "qtype": "short",
        "max_points": 2,
        "prompt": f"Визначте час вільного падіння тіла з висоти {h} м зі стану спокою. Уважайте, що g = 10 м/с². Відповідь запишіть у секундах (с).",
        "answer": str(t),
        "hint": "Використай формулу шляху без початкової швидкості: h = (g · t²) / 2.",
        "rule": "Під час вільного падіння без початкової швидкості: h = g·t² / 2 ⇒ t = √(2h / g). При g = 10 м/с² це просто √(h / 5).",
        "solution": f"t = √(2 · {h} / 10) = √({2 * h // 10}) = {t} с.",
        "drill_key": "phys_free_fall",
    }


@register_drill("phys_incline")
def gen_phys_incline():
    m = random.choice([8, 12, 15, 18, 24, 30])
    f_val = 5 * m
    return {
        "subject": "physics",
        "section": "Механіка",
        "source": GEN_SOURCE,
        "qtype": "short",
        "max_points": 2,
        "prompt": f"Санчата масою {m} кг перебувають на схилі з кутом нахилу 30° до горизонту. Яку силу треба прикласти вздовж схилу вгору, щоб утримувати їх у рівновазі? Тертя не враховуйте, g = 10 м/с². Відповідь запишіть у ньютонах (Н).",
        "answer": str(f_val),
        "hint": "Сила вздовж похилої площини дорівнює скочувальній силі тяжіння: F = m · g · sin(α).",
        "rule": "На похилій площині без тертя утримувальна сила вздовж схилу дорівнює F = m·g·sin(α). Пам’ятай, що sin(30°) = 0,5!",
        "solution": f"F = m · g · sin(30°) = {m} · 10 · 0,5 = {f_val} Н.",
        "drill_key": "phys_incline",
    }


@register_drill("phys_thermo_1law")
def gen_phys_thermo_1law():
    q = random.choice([40, 50, 60, 80, 100])
    a = random.choice([15, 20, 25, 30])
    du = q - a
    opts = [
        f"зменшилася на {du} Дж",
        f"зменшилася на {q + a} Дж",
        f"збільшилася на {du} Дж",
        f"збільшилася на {q + a} Дж",
    ]
    return {
        "subject": "physics",
        "section": "Молекулярна фізика та термодинаміка",
        "source": GEN_SOURCE,
        "qtype": "single",
        "max_points": 1,
        "prompt": f"Ідеальному одноатомному газу незмінної маси надали {q} Дж теплоти, і він виконав роботу {a} Дж. Як змінилася внутрішня енергія цього газу?",
        "options": opts,
        "labels": ["А", "Б", "В", "Г"],
        "answer": "В",
        "hint": "Перший закон термодинаміки: Q = ΔU + A (отримане тепло йде на зміну внутрішньої енергії та на роботу газу).",
        "rule": "Перший закон термодинаміки: Q = ΔU + A ⇒ ΔU = Q − A. Якщо ΔU > 0, внутрішня енергія збільшилася; якщо ΔU < 0 — зменшилася.",
        "solution": f"ΔU = Q − A = {q} − {a} = +{du} Дж → внутрішня енергія збільшилася на {du} Дж (В).",
        "drill_key": "phys_thermo_1law",
    }


@register_drill("phys_humidity")
def gen_phys_humidity():
    v = random.choice([0.5, 1.0, 2.0])
    rho_sat = random.choice([20, 25])
    phi0 = random.choice([30, 40, 50, 60])
    m_evap = (100 - phi0) / 100.0 * rho_sat * v
    return {
        "subject": "physics",
        "section": "Молекулярна фізика та термодинаміка",
        "source": GEN_SOURCE,
        "qtype": "short",
        "max_points": 2,
        "prompt": (
            f"У герметичний балон об’ємом {fmt_num(v)} м³ поставили посудину з водою. До насичення пари в балоні "
            f"випарувалася вода масою {fmt_num(m_evap)} г. Якою була початкова відносна вологість повітря в балоні (у %), "
            f"якщо густина насиченої пари за цієї температури дорівнює {rho_sat} г/м³?"
        ),
        "answer": str(phi0),
        "hint": "Спочатку знайди, скільки грамів пари може поміститися в балоні загалом (m_нас = ρ_нас · V), а потім відніми масу, що випарувалася!",
        "rule": "У стані насичення маса пари m_нас = ρ_нас · V (100 %). Початкова маса пари m₀ = m_нас − m_вип, а φ₀ = (m₀ / m_нас) · 100 %.",
        "solution": (
            f"1) Маса насиченої пари в об’ємі {fmt_num(v)} м³: m_нас = {rho_sat} · {fmt_num(v)} = {fmt_num(rho_sat * v)} г.\n"
            f"2) Спочатку було пари: m₀ = {fmt_num(rho_sat * v)} − {fmt_num(m_evap)} = {fmt_num(rho_sat * v - m_evap)} г.\n"
            f"3) φ₀ = ({fmt_num(rho_sat * v - m_evap)} / {fmt_num(rho_sat * v)}) · 100 % = {phi0} %."
        ),
        "drill_key": "phys_humidity",
    }


@register_drill("phys_halflife")
def gen_phys_halflife():
    half_life = random.choice([5700, 1600, 30, 8])
    n_periods = random.choice([2, 3])
    rem_pct = fmt_num(100 / (2 ** n_periods))
    ans = half_life * n_periods
    return {
        "subject": "physics",
        "section": "Квантова фізика та теорія відносності",
        "source": GEN_SOURCE,
        "qtype": "short",
        "max_points": 2,
        "prompt": (
            f"У зразку залишилося {rem_pct} % радіоактивного ізотопу, період піврозпаду якого становить {half_life} років. "
            f"Скільки років минуло від початку розпаду?"
        ),
        "answer": str(ans),
        "hint": "За 1 період залишається 50 %, за 2 періоди — 25 %, за 3 періоди — 12,5 %!",
        "rule": "Закон радіоактивного розпаду: за кожен період T кількість речовини зменшується у 2 рази (100 % → 50 % → 25 % → 12,5 %). Час t = n · T.",
        "solution": f"{rem_pct} % = 100 % / 2^{n_periods}, отже минуло n = {n_periods} періоди. Час t = {n_periods} · {half_life} = {ans} років.",
        "drill_key": "phys_halflife",
    }
