"""Task generators: Хімія."""

import random

from ._common import fmt_num, GEN_SOURCE, register_drill


@register_drill("chem_gas_molar")
def gen_chem_gas_molar():
    n = random.choice([1.5, 2.0, 2.5, 3.0, 4.0])
    molar = random.choice([28, 32, 44, 64, 128])
    v = n * 22.4
    mass = n * molar
    return {
        "subject": "chemistry",
        "section": "Обчислення в хімії",
        "source": GEN_SOURCE,
        "qtype": "short",
        "max_points": 2,
        "prompt": f"Маса газу об’ємом {fmt_num(v)} л (н. у.) дорівнює {fmt_num(mass)} г. Обчисліть молярну масу (г/моль) цього газу.",
        "answer": str(molar),
        "hint": "Спочатку знайди кількість речовини n = V / Vm (Vm = 22,4 л/моль), а потім M = m / n.",
        "rule": "За нормальних умов 1 моль будь-якого газу займає 22,4 л. Формули: n = V / 22,4 і M = m / n.",
        "solution": f"1) n = {fmt_num(v)} / 22,4 = {fmt_num(n)} моль.\n2) M = {fmt_num(mass)} / {fmt_num(n)} = {molar} г/моль.",
        "drill_key": "chem_gas_molar",
    }


@register_drill("chem_solution_sat")
def gen_chem_solution_sat():
    sol_per_100 = random.choice([150, 200, 250])
    water_g = random.choice([20, 40, 50])
    max_salt = sol_per_100 * water_g // 100
    already = max_salt - random.choice([10, 15, 20, 25])
    need = max_salt - already
    return {
        "subject": "chemistry",
        "section": "Обчислення в хімії",
        "source": GEN_SOURCE,
        "qtype": "short",
        "max_points": 2,
        "prompt": (
            f"За температури 60 °C розчинність солі становить {sol_per_100} г у 100 г води. "
            f"У воді масою {water_g} г розчинили {already} г цієї солі. Обчисліть масу (г) солі, "
            f"яку ще треба додати, щоб розчин став насиченим за 60 °C."
        ),
        "answer": str(need),
        "hint": f"Розрахуй за пропорцією, скільки максимум солі розчиняється у {water_g} г води, і відніми вже додані {already} г.",
        "rule": "Розчинність показує максимальну масу солі у 100 г води. Якщо води m_в, то гранична маса солі m_макс = S · (m_в / 100).",
        "solution": f"1) У {water_g} г води може розчинитися максимум {sol_per_100} · ({water_g}/100) = {max_salt} г.\n2) Потрібно додати: {max_salt} − {already} = {need} г.",
        "drill_key": "chem_solution_sat",
    }


@register_drill("chem_yield")
def gen_chem_yield():
    n_ethene = random.choice([2, 3, 4, 5])
    v_ethene = n_ethene * 22.4
    eta = random.choice([50, 60, 75, 80])
    mass_pract = n_ethene * 46 * eta / 100
    return {
        "subject": "chemistry",
        "section": "Обчислення в хімії",
        "source": GEN_SOURCE,
        "qtype": "short",
        "max_points": 2,
        "prompt": f"Обчисліть масу (г) етанолу (M = 46 г/моль), що утвориться внаслідок гідратації етену об’ємом {fmt_num(v_ethene)} л (н. у.), якщо відносний вихід спирту становить {eta} %.",
        "answer": fmt_num(mass_pract),
        "hint": "1) Знайди кількість речовини етену n = V / 22,4; 2) стільки ж моль спирту утвориться теоретично (1:1); 3) помнож теоретичну масу на вихід η!",
        "rule": "C₂H₄ + H₂O → C₂H₅OH (коефіцієнти 1:1). Практична маса = m_теор · (вихід % / 100).",
        "solution": (
            f"1) n(C₂H₄) = {fmt_num(v_ethene)} / 22,4 = {n_ethene} моль = n_теор(C₂H₅OH).\n"
            f"2) m_теор = {n_ethene} · 46 = {n_ethene * 46} г.\n"
            f"3) m_практ = {n_ethene * 46} · {eta/100:.2f} = {fmt_num(mass_pract)} г."
        ),
        "drill_key": "chem_yield",
    }


@register_drill("chem_alkane_combust")
def gen_chem_alkane_combust():
    n_c = random.choice([3, 4, 5, 6])
    n_alk = random.choice([0.2, 0.25, 0.5])
    o2_coef = (3 * n_c + 1) / 2.0
    n_o2 = n_alk * o2_coef
    atoms = 3 * n_c + 2
    return {
        "subject": "chemistry",
        "section": "Органічна хімія",
        "source": GEN_SOURCE,
        "qtype": "short",
        "max_points": 2,
        "prompt": (
            f"Для повного окиснення алкану кількістю речовини {fmt_num(n_alk)} моль витратили кисень "
            f"кількістю речовини {fmt_num(n_o2)} моль. Визначте формулу алкану й зазначте у відповіді "
            f"кількість УСІХ атомів у його молекулі."
        ),
        "answer": str(atoms),
        "hint": "Знайди, скільки моль O₂ потрібно на 1 моль алкану: (3n + 1)/2 = n(O₂)/n(алкану), звідки знайдеш n!",
        "rule": "Загальне рівняння горіння алкану: CₙH₂ₙ₊₂ + ((3n+1)/2) O₂ → n CO₂ + (n+1) H₂O. Кількість усіх атомів у молекулі CₙH₂ₙ₊₂ дорівнює 3n + 2.",
        "solution": (
            f"1) На 1 моль алкану потрібно {fmt_num(n_o2)} / {fmt_num(n_alk)} = {fmt_num(o2_coef)} моль O₂.\n"
            f"2) (3n + 1)/2 = {fmt_num(o2_coef)} ⇒ 3n + 1 = {3*n_c+1} ⇒ n = {n_c} (C{n_c}H{2*n_c+2}).\n"
            f"3) Усього атомів: {n_c} + {2*n_c+2} = {atoms}."
        ),
        "drill_key": "chem_alkane_combust",
    }
