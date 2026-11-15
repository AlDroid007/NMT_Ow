"""Task generators: Географія."""

import random

from ._common import GEN_SOURCE, register_drill


@register_drill("geo_map_scale")
def gen_geo_map_scale():
    scale_m = random.choice([100, 200, 250, 500])
    scale_denom = scale_m * 100
    d_cm = random.choice([4, 6, 8, 9, 12, 15, 22])
    ans = d_cm * scale_m
    return {
        "subject": "geography",
        "section": "Загальна географія та топографія",
        "source": GEN_SOURCE,
        "qtype": "short",
        "max_points": 2,
        "prompt": f"На топографічній карті масштабу 1 : {scale_denom} довжина ділянки дороги становить {d_cm} см. Визначте дійсну відстань на місцевості (у метрах).",
        "answer": str(ans),
        "hint": f"Відкинь два останні нулі від {scale_denom}, щоб отримати масштаб у метрах (в 1 см — {scale_m} м), і помнож на {d_cm}.",
        "rule": "Золоте правило масштабу на НМТ: щоб перевести числовий масштаб 1 : N у метри, закресли 2 нулі праворуч (1 м = 100 см). Потім помнож число сантиметрів на карті на отриману кількість метрів.",
        "solution": f"Масштаб 1 : {scale_denom} означає, що в 1 см — {scale_m} м. Відстань = {d_cm} · {scale_m} = {ans} м.",
        "drill_key": "geo_map_scale",
    }


@register_drill("geo_azimuth")
def gen_geo_azimuth():
    cases = [
        ("північного (0°)", "на схід", 0, 1),
        ("східного (90°)", "на північ (відхилення до півночі)", 90, -1),
        ("східного (90°)", "на південь", 90, 1),
        ("південного (180°)", "на схід", 180, -1),
        ("південного (180°)", "на захід", 180, 1),
        ("західного (270°)", "на північ", 270, 1),
        ("західного (270°)", "на південь", 270, -1),
    ]
    base_txt, dir_txt, base_deg, sign = random.choice(cases)
    dev = random.choice([7, 12, 15, 18, 25])
    az = (base_deg + sign * dev) % 360
    return {
        "subject": "geography",
        "section": "Загальна географія та топографія",
        "source": GEN_SOURCE,
        "qtype": "short",
        "max_points": 2,
        "prompt": f"Визначте азимут (у градусах) руху, якщо напрямок відхиляється від {base_txt} напрямку {dir_txt} на {dev}°.",
        "answer": str(az),
        "hint": "Азимут відлічують ВІД ПІВНОЧІ (0°) ЗА ГОДИННИКОВОЮ СТРІЛКОЮ: Схід = 90°, Південь = 180°, Захід = 270°, Північ = 360°.",
        "rule": "Азимут завжди рахують від півночі (0°) за годинниковою стрілкою: Пн = 0°/360°, Сх = 90°, Пд = 180°, Зх = 270°. Намалюй хрестик сторін світу — рух за годинниковою стрілкою додає градуси, проти — віднімає.",
        "solution": f"Базовий азимут {base_deg}°, зсув {dir_txt} на {dev}° → {base_deg} {'+' if sign > 0 else '−'} {dev} = {az}°.",
        "drill_key": "geo_azimuth",
    }


@register_drill("geo_ukr_extremes")
def gen_geo_ukr_extremes():
    pool = [
        ("північна", "село Грем’яч (Чернігівська область)"),
        ("південна", "мис Сарич (АР Крим)"),
        ("західна (найближча до Гринвіцького меридіана)", "село Соломоново (Закарпатська область)"),
        ("східна", "село Рання Зоря (Луганська область)"),
    ]
    target = random.choice(pool)
    opts = [p[1] for p in pool]
    random.shuffle(opts)
    labels = ["А", "Б", "В", "Г"]
    c_idx = opts.index(target[1])
    return {
        "subject": "geography",
        "section": "Фізична географія України",
        "source": GEN_SOURCE,
        "qtype": "single",
        "max_points": 1,
        "prompt": f"Позначте крайню {target[0]} точку території України:",
        "options": opts,
        "labels": labels,
        "answer": labels[c_idx],
        "hint": "Запам’ятай 4 крайні точки України: Грем’яч, Сарич, Соломоново, Рання Зоря.",
        "rule": "Чотири крайні точки України: Північ — Грем’яч, Південь — мис Сарич, Захід (найближче до Гринвіча) — Соломоново, Схід («раннє сонце») — Рання Зоря.",
        "solution": f"Крайня {target[0]} точка — {target[1]} ({labels[c_idx]}).",
        "drill_key": "geo_ukr_extremes",
    }
