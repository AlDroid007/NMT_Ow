"""Task generators: Біологія."""

import random

from ._common import GEN_SOURCE, register_drill


@register_drill("bio_dna_percent")
def gen_bio_dna_percent():
    pct = random.choice([12, 16, 18, 22, 28, 32, 36, 42])
    given_base, ask_base = random.choice([
        ("гуанілових (Г)", "тимідилових (Т)"),
        ("цитидилових (Ц)", "аденілових (А)"),
        ("аденілових (А)", "гуанілових (Г)"),
        ("тимідилових (Т)", "цитидилових (Ц)"),
    ])
    ans = 50 - pct
    vals = sorted({ans, pct, 2 * pct if 2 * pct <= 100 else 100 - pct, 100 - 2 * pct if 100 - 2 * pct > 0 else ans + 8})
    while len(vals) < 4:
        vals.append(vals[-1] + 4)
    vals = vals[:4]
    labels = ["А", "Б", "В", "Г"]
    c_idx = vals.index(ans)
    return {
        "subject": "biology",
        "section": "Клітина. Хімічний склад і реалізація спадкової інформації",
        "source": GEN_SOURCE,
        "qtype": "single",
        "max_points": 1,
        "prompt": f"Обчисліть частку (%) {ask_base} нуклеотидів у ділянці дволанцюгової молекули ДНК, якщо частка {given_base} становить {pct} % від загальної кількості.",
        "options": [str(v) for v in vals],
        "labels": labels,
        "answer": labels[c_idx],
        "hint": "Правило Чаргаффа: А = Т, Г = Ц, а сума А + Т + Г + Ц = 100 %. Отже, (А + Г) або (Т + Г) = 50 %!",
        "rule": "Проста формула для ДНК (правило Чаргаффа): комплементарні нуклеотиди рівні (А = Т, Г = Ц), тому сума некомплементарних (А + Г = 50 % і Т + Ц = 50 %). Щоб знайти інший тип, просто відніми даний відсоток від 50 %!",
        "solution": f"За правилом Чаргаффа сума некомплементарних пар становить 50 %: {ask_base} = 50 % − {pct} % = {ans} % ({labels[c_idx]}).",
        "drill_key": "bio_dna_percent",
    }


@register_drill("bio_dna_deoxy")
def gen_bio_dna_deoxy():
    a_cnt = random.choice([40, 60, 80, 100, 120])
    g_cnt = random.choice([30, 50, 70, 90])
    total = 2 * (a_cnt + g_cnt)
    vals = sorted({total, a_cnt + g_cnt, (a_cnt + g_cnt) // 2, total + 100})
    labels = ["А", "Б", "В", "Г"]
    c_idx = vals.index(total)
    return {
        "subject": "biology",
        "section": "Клітина. Хімічний склад і реалізація спадкової інформації",
        "source": GEN_SOURCE,
        "qtype": "single",
        "max_points": 1,
        "prompt": f"Ділянка дволанцюгової молекули ДНК містить {a_cnt} аденілових і {g_cnt} гуанілових нуклеотидів. Обчисліть кількість залишків дезоксирибози в цій ділянці ДНК.",
        "options": [str(v) for v in vals],
        "labels": labels,
        "answer": labels[c_idx],
        "hint": "У КОЖНОМУ нуклеотиді ДНК є рівно 1 залишок дезоксирибози. Але не забудь, що є ще тимідилові (Т = А) і цитидилові (Ц = Г) нуклеотиди!",
        "rule": "1 нуклеотид = 1 залишок дезоксирибози. За принципом комплементарності: Т = А, Ц = Г. Тому загальна кількість нуклеотидів (і дезоксирибоз) = 2 · (А + Г).",
        "solution": f"А = Т = {a_cnt}, Г = Ц = {g_cnt}. Усього нуклеотидів = {a_cnt} + {a_cnt} + {g_cnt} + {g_cnt} = {total}. Стільки ж і залишків дезоксирибози: {total} ({labels[c_idx]}).",
        "drill_key": "bio_dna_deoxy",
    }
