#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
НМТ Тренажер із Репетитором (2022–2026) — Метадані, програми та шкали 100–200.
Кросплатформна програма для macOS та Windows (стандартна бібліотека Python 3).
"""

import json
import math
import os
import random
import sys
import time
from datetime import datetime

APP_TITLE = "НМТ Тренажер • Сова-Ліза (2022–2026)"
APP_VERSION = "3.5 (macOS)"

SUBJECTS_ORDER = [
    "ukrmova",
    "math",
    "history",
    "english",
    "german",
    "french",
    "spanish",
    "ukrlit",
    "biology",
    "physics",
    "chemistry",
    "geography",
]

SUBJECTS_CONFIG = {
    "ukrmova": {
        "name": "Українська мова",
        "mandatory": True,
        "total_tasks": 30,
        "max_score": 45,
        "threshold": 8,
        "minutes": 60,
        "program_order": "Наказ МОН від 26.06.2018 № 696",
        "structure": "25 завдань з вибором 1 відповіді (0–1 бал) + 5 завдань на встановлення відповідності (0–4 бали)",
        "sections": [
            "Фонетика. Графіка. Орфоепія",
            "Орфографія",
            "Лексикологія. Фразеологія",
            "Будова слова. Словотвір",
            "Морфологія",
            "Синтаксис. Пунктуація",
            "Стилістика (текст)",
        ],
    },
    "math": {
        "name": "Математика",
        "mandatory": True,
        "total_tasks": 22,
        "max_score": 32,
        "threshold": 5,
        "minutes": 60,
        "program_order": "Наказ МОН від 04.12.2019 № 1513",
        "structure": "15 завдань з вибором 1 відповіді (0–1 бал) + 3 на відповідність (0–3 бали) + 4 з короткою відповіддю (0 або 2 бали)",
        "sections": [
            "Числа і вирази",
            "Рівняння, нерівності та їх системи",
            "Функції",
            "Комбінаторика, ймовірність, статистика",
            "Планіметрія",
            "Стереометрія",
        ],
    },
    "history": {
        "name": "Історія України",
        "mandatory": True,
        "total_tasks": 30,
        "max_score": 54,
        "threshold": 9,
        "minutes": 60,
        "program_order": "Наказ МОН від 26.06.2018 № 696",
        "structure": "20 вибір 1 (0–1) + 4 відповідність (0–4) + 3 послідовність (0–3) + 3 вибір 3 з 7 (0–3)",
        "sections": [
            "Від найдавніших часів до першої половини XVI ст.",
            "Друга половина XVI–XVIII ст.",
            "Кінець XVIII – початок XX ст.",
            "Україна в 1914–1945 рр.",
            "Україна в 1945 р. – початок XXI ст.",
        ],
    },
    "english": {
        "name": "Англійська мова",
        "mandatory": False,
        "total_tasks": 32,
        "max_score": 32,
        "threshold": 5,
        "minutes": 60,
        "program_order": "Наказ МОН від 26.06.2018 № 696",
        "structure": "Reading (22 завдання) + Use of English (10 завдань): 5 вибір 1 + 11 відповідність + 16 пропуски (по 1 балу)",
        "sections": [
            "Reading: Загальне розуміння (Task 1)",
            "Reading: Детальне розуміння (Task 2)",
            "Reading: Пошук інформації (Task 3)",
            "Reading: Структура тексту (Task 4)",
            "Use of English: Лексика (Task 5)",
            "Use of English: Граматика (Task 6)",
        ],
    },
    "german": {
        "name": "Німецька мова",
        "mandatory": False,
        "total_tasks": 32,
        "max_score": 32,
        "threshold": 5,
        "minutes": 60,
        "program_order": "Наказ МОН від 26.06.2018 № 696",
        "structure": "Lesen (22) + Sprachverwendung (10): Aufgaben 1–6 (по 1 балу)",
        "sections": [
            "Lesen: Загальне й детальне розуміння",
            "Lesen: Структура тексту",
            "Wortschatz: Лексика в контексті",
            "Grammatik: Граматика в контексті",
        ],
    },
    "french": {
        "name": "Французька мова",
        "mandatory": False,
        "total_tasks": 32,
        "max_score": 32,
        "threshold": 5,
        "minutes": 60,
        "program_order": "Наказ МОН від 26.06.2018 № 696",
        "structure": "Compréhension écrite (22) + Usage de la langue (10): Exercices 1–6 (по 1 балу)",
        "sections": [
            "Compréhension écrite: Читання",
            "Lexique: Лексика в контексті",
            "Grammaire: Граматика в контексті",
        ],
    },
    "spanish": {
        "name": "Іспанська мова",
        "mandatory": False,
        "total_tasks": 32,
        "max_score": 32,
        "threshold": 5,
        "minutes": 60,
        "program_order": "Наказ МОН від 26.06.2018 № 696",
        "structure": "Lectura (22) + Uso de la lengua (10): Tareas 1–6 (по 1 балу)",
        "sections": [
            "Lectura: Розуміння тексту",
            "Léxico: Лексика в контексті",
            "Gramática: Граматика в контексті",
        ],
    },
    "ukrlit": {
        "name": "Українська література",
        "mandatory": False,
        "total_tasks": 30,
        "max_score": 45,
        "threshold": 7,
        "minutes": 60,
        "program_order": "Наказ МОН від 26.06.2018 № 696",
        "structure": "25 завдань з вибором 1 відповіді (0–1 бал) + 5 завдань на встановлення відповідності (0–4 бали)",
        "sections": [
            "Усна народна творчість",
            "Давня українська література",
            "Література кінця XVIII – початку XX ст.",
            "Література XX ст.",
            "Творчість письменників-емігрантів та сучасний процес",
            "Теорія літератури та аналіз текстів",
        ],
    },
    "biology": {
        "name": "Біологія",
        "mandatory": False,
        "total_tasks": 30,
        "max_score": 46,
        "threshold": 7,
        "minutes": 60,
        "program_order": "Наказ МОН від 20.12.2018 № 1426",
        "structure": "24 вибір 1 (0–1) + 4 відповідність (0–4) + 2 вибір 3 з 3 груп (0–3)",
        "sections": [
            "Клітина. Хімічний склад і реалізація спадкової інформації",
            "Закономірності спадковості і мінливості",
            "Біорізноманіття",
            "Організм людини як біологічна система",
            "Основи екології й еволюційного вчення",
        ],
    },
    "physics": {
        "name": "Фізика",
        "mandatory": False,
        "total_tasks": 22,
        "max_score": 32,
        "threshold": 5,
        "minutes": 60,
        "program_order": "Наказ МОН від 26.06.2018 № 696",
        "structure": "14 вибір 1 (0–1) + 2 відповідність (0–3) + 6 з короткою відповіддю (0 або 2 бали)",
        "sections": [
            "Механіка",
            "Молекулярна фізика та термодинаміка",
            "Електродинаміка",
            "Коливання і хвилі. Оптика",
            "Квантова фізика та теорія відносності",
        ],
    },
    "chemistry": {
        "name": "Хімія",
        "mandatory": False,
        "total_tasks": 24,
        "max_score": 32,
        "threshold": 5,
        "minutes": 60,
        "program_order": "Наказ МОН від 26.06.2018 № 696",
        "structure": "18 вибір 1 (0–1) + 2 відповідність (0–3) + 4 з короткою відповіддю (0 або 2 бали)",
        "sections": [
            "Загальна хімія",
            "Неорганічна хімія",
            "Органічна хімія",
            "Обчислення в хімії",
        ],
    },
    "geography": {
        "name": "Географія",
        "mandatory": False,
        "total_tasks": 30,
        "max_score": 46,
        "threshold": 7,
        "minutes": 60,
        "program_order": "Наказ МОН від 26.06.2018 № 696",
        "structure": "20 вибір 1 (0–1) + 4 коротка відповідь (0 або 2) + 6 вибір 3 з 7 (0–3)",
        "sections": [
            "Загальна географія та топографія",
            "Географія материків і океанів",
            "Фізична географія України",
            "Населення України та світу",
            "Україна і світове господарство. Регіони",
        ],
    },
}

_FOREIGN_TABLE = {
    5: 100, 6: 109, 7: 118, 8: 125, 9: 131, 10: 134, 11: 137, 12: 140,
    13: 143, 14: 145, 15: 147, 16: 148, 17: 149, 18: 150, 19: 151, 20: 152,
    21: 153, 22: 155, 23: 157, 24: 159, 25: 162, 26: 166, 27: 169, 28: 173,
    29: 179, 30: 185, 31: 191, 32: 200,
}

_BIO_GEO_TABLE = {
    7: 100, 8: 107, 9: 114, 10: 119, 11: 124, 12: 128, 13: 131, 14: 134,
    15: 136, 16: 138, 17: 140, 18: 142, 19: 144, 20: 145, 21: 146, 22: 147,
    23: 148, 24: 149, 25: 150, 26: 151, 27: 152, 28: 154, 29: 156, 30: 158,
    31: 160, 32: 162, 33: 164, 34: 166, 35: 168, 36: 170, 37: 172, 38: 175,
    39: 177, 40: 179, 41: 182, 42: 185, 43: 188, 44: 192, 45: 196, 46: 200,
}

_PHYS_CHEM_TABLE = {
    5: 100, 6: 109, 7: 118, 8: 125, 9: 131, 10: 134, 11: 137, 12: 140,
    13: 143, 14: 145, 15: 147, 16: 148, 17: 149, 18: 150, 19: 151, 20: 152,
    21: 156, 22: 160, 23: 164, 24: 166, 25: 169, 26: 173, 27: 176, 28: 179,
    29: 184, 30: 189, 31: 194, 32: 200,
}

CONVERSION_TABLES = {
    "ukrmova": {
        8: 100, 9: 105, 10: 110, 11: 120, 12: 125, 13: 130, 14: 134, 15: 136,
        16: 138, 17: 140, 18: 142, 19: 143, 20: 144, 21: 145, 22: 146, 23: 148,
        24: 149, 25: 150, 26: 152, 27: 154, 28: 156, 29: 157, 30: 159, 31: 160,
        32: 162, 33: 163, 34: 165, 35: 167, 36: 170, 37: 172, 38: 175, 39: 177,
        40: 180, 41: 183, 42: 186, 43: 191, 44: 195, 45: 200,
    },
    "math": {
        5: 100, 6: 108, 7: 115, 8: 123, 9: 131, 10: 134, 11: 137, 12: 140,
        13: 143, 14: 145, 15: 147, 16: 148, 17: 149, 18: 150, 19: 151, 20: 152,
        21: 155, 22: 159, 23: 163, 24: 167, 25: 170, 26: 173, 27: 176, 28: 180,
        29: 184, 30: 189, 31: 194, 32: 200,
    },
    "history": {
        9: 100, 10: 105, 11: 110, 12: 115, 13: 120, 14: 125, 15: 130, 16: 132,
        17: 134, 18: 136, 19: 138, 20: 140, 21: 141, 22: 142, 23: 143, 24: 144,
        25: 145, 26: 146, 27: 147, 28: 148, 29: 149, 30: 150, 31: 151, 32: 152,
        33: 154, 34: 156, 35: 158, 36: 160, 37: 163, 38: 166, 39: 168, 40: 169,
        41: 170, 42: 172, 43: 173, 44: 175, 45: 177, 46: 179, 47: 181, 48: 183,
        49: 185, 50: 188, 51: 191, 52: 194, 53: 197, 54: 200,
    },
    "english": _FOREIGN_TABLE,
    "german": _FOREIGN_TABLE,
    "french": _FOREIGN_TABLE,
    "spanish": _FOREIGN_TABLE,
    "ukrlit": {
        7: 100, 8: 105, 9: 110, 10: 115, 11: 120, 12: 125, 13: 131, 14: 134,
        15: 136, 16: 138, 17: 140, 18: 142, 19: 143, 20: 144, 21: 145, 22: 146,
        23: 148, 24: 149, 25: 150, 26: 152, 27: 154, 28: 156, 29: 157, 30: 159,
        31: 160, 32: 162, 33: 163, 34: 165, 35: 167, 36: 170, 37: 172, 38: 175,
        39: 177, 40: 180, 41: 183, 42: 186, 43: 191, 44: 195, 45: 200,
    },
    "biology": _BIO_GEO_TABLE,
    "geography": _BIO_GEO_TABLE,
    "physics": _PHYS_CHEM_TABLE,
    "chemistry": _PHYS_CHEM_TABLE,
}


def score_to_nmt200(subject_id, raw_score):
    """Переводить тестовий бал у рейтингову шкалу НМТ 100–200 (або None, якщо нижче порога)."""
    cfg = SUBJECTS_CONFIG[subject_id]
    if raw_score < cfg["threshold"]:
        return None
    table = CONVERSION_TABLES[subject_id]
    clamped = min(int(round(raw_score)), cfg["max_score"])
    return table.get(clamped)


"""Банк завдань і генератори: Українська мова, Математика, Історія України."""

def _gcd(a, b):
    while b:
        a, b = b, a % b
    return abs(a)


def _fmt_num(val):
    if abs(val - round(val)) < 1e-9:
        return str(int(round(val)))
    s = f"{val:.4f}".rstrip("0").rstrip(".")
    return s.replace(".", ",")


# ---------------------------------------------------------------------------
# ГЕНЕРАТОРИ ІДЕНТИЧНИХ ПРИКЛАДІВ (DRILL_GENERATORS)
# ---------------------------------------------------------------------------
DRILL_GENERATORS = {}


def register_drill(key):
    def deco(fn):
        DRILL_GENERATORS[key] = fn
        return fn
    return deco


# ========================== УКРАЇНСЬКА МОВА ================================

@register_drill("ukrmova_pref_zs")
def gen_ukrmova_pref_zs():
    kafep = [
        ("..казати", "сказати"), ("..писати", "списати"), ("..творити", "створити"),
        ("..фотографувати", "сфотографувати"), ("..хитрувати", "схитрувати"),
        ("..ховати", "сховати"), ("..копіювати", "скопіювати"), ("..формувати", "сформувати"),
        ("..палити", "спалити"), ("..пиляти", "спиляти"), ("..тримати", "стримати"),
    ]
    z_words = [
        ("..робити", "зробити"), ("..будувати", "збудувати"), ("..шити", "зшити"),
        ("..цілити", "зцілити"), ("..жалитись", "зжалитись"), ("..бирати", "збирати"),
        ("..в'язати", "зв'язати"), ("..мінити", "змінити"), ("..гадати", "згадати"),
    ]
    mode = random.choice(["find_z", "find_s"])
    if mode == "find_z":
        # 3 рядки зі "с-", 1 рядок із одним словом на "з-"
        correct_idx = random.randint(0, 3)
        options = []
        used_k = random.sample(kafep, 9)
        idx = 0
        for i in range(4):
            if i == correct_idx:
                zw = random.choice(z_words)
                pair = random.sample([w for w in kafep if w[0] != zw[0]], 2)
                words = [pair[0][0], zw[0], pair[1][0]]
                random.shuffle(words)
                options.append(", ".join(words))
                odd_word = zw[1]
            else:
                words = [used_k[idx][0], used_k[idx + 1][0], used_k[idx + 2][0]]
                idx += 3
                options.append(", ".join(words))
        labels = ["А", "Б", "В", "Г"]
        return {
            "subject": "ukrmova",
            "section": "Орфографія",
            "source": "Генератор за програмою НМТ (2022–2026)",
            "qtype": "single",
            "max_points": 1,
            "prompt": "Префікс с- треба писати на місці пропуску в усіх словах, ОКРІМ рядка:",
            "options": options,
            "labels": labels,
            "answer": labels[correct_idx],
            "hint": "Згадай чарівну фразу «КаФе «ПТаХ»». Перед цими п’ятьма приголосними пишемо с-.",
            "rule": "В українській мові префікс С- пишеться ЛИШЕ перед літерами К, Ф, П, Т, Х (мнемоніка: «КаФе «ПТаХ»»). Перед усіма іншими літерами завжди пишемо префікс З-.",
            "solution": f"У рядку {labels[correct_idx]} є слово «{odd_word}», де корінь починається не на К, Ф, П, Т, Х — отже, потрібен префікс З-. В інших словах перші літери кореня входять до «КаФе ПТаХ».",
            "drill_key": "ukrmova_pref_zs",
        }
    else:
        correct_idx = random.randint(0, 3)
        options = []
        for i in range(4):
            if i == correct_idx:
                kw = random.sample(kafep, 3)
                options.append(", ".join(w[0] for w in kw))
                win_words = ", ".join(w[1] for w in kw)
            else:
                zw = random.sample(z_words, 2)
                kw = random.choice(kafep)
                words = [zw[0][0], kw[0], zw[1][0]]
                random.shuffle(words)
                options.append(", ".join(words))
        labels = ["А", "Б", "В", "Г"]
        return {
            "subject": "ukrmova",
            "section": "Орфографія",
            "source": "Генератор за програмою НМТ (2022–2026)",
            "qtype": "single",
            "max_points": 1,
            "prompt": "Префікс с- треба писати на місці пропуску в усіх словах рядка:",
            "options": options,
            "labels": labels,
            "answer": labels[correct_idx],
            "hint": "Перевір кожну першу літеру після пропуску за правилом «КаФе «ПТаХ»».",
            "rule": "Префікс С- пишемо лише перед приголосними К, П, Т, Ф, Х («КаФе «ПТаХ»»). Навіть перед Ш або С у слові «зшити» пишемо З-!",
            "solution": f"Правильний варіант {labels[correct_idx]} ({win_words}) — усі три слова починаються на приголосні з правила «КаФе «ПТаХ»».",
            "drill_key": "ukrmova_pref_zs",
        }


@register_drill("ukrmova_nagolos")
def gen_ukrmova_nagolos():
    exact_good = [
        "мережа піце́рій", "пройти чотирна́дцять", "платіжна ві́домість", "бурштинова за́понка",
        "привітати замі́жню", "болотиста рівни́на", "ти́сові ліси", "дивлячись на ці́нник",
        "чергова ви́трата", "завча́су закінчити", "посере́дині літо́пису", "новий катало́г",
        "дієвий фено́мен", "глибоке ру́сло", "зручні жалюзі́", "тривалий кварта́л",
    ]
    exact_wrong = [
        ("у листо́паді", "правильно: у листопа́ді"),
        ("принести ко́лесо", "правильно: коле́со"),
        ("довідник з кулінарі́ї", "правильно: куліна́рії"),
        ("рідкісний феноме́н", "правильно: фено́мен"),
        ("рівна спи́на", "правильно: спина́"),
        ("новий фарту́х", "правильно: фа́ртух"),
        ("несподіваний випа́док", "правильно: ви́падок"),
        ("високий це́нтнер", "правильно: центне́р"),
    ]
    wrong_item = random.choice(exact_wrong)
    good_items = random.sample(exact_good, 7)
    wrong_idx = random.randint(0, 3)
    options = []
    g_ptr = 0
    for i in range(4):
        if i == wrong_idx:
            options.append(f"{good_items[g_ptr]}, {wrong_item[0]}")
            g_ptr += 1
        else:
            options.append(f"{good_items[g_ptr]}, {good_items[g_ptr + 1]}")
            g_ptr += 2
    labels = ["А", "Б", "В", "Г"]
    return {
        "subject": "ukrmova",
        "section": "Фонетика. Графіка. Орфоепія",
        "source": "Генератор за програмою НМТ (2022–2026)",
        "qtype": "single",
        "max_points": 1,
        "prompt": "Правильно виділено букви на позначення наголошених звуків у всіх словах, ОКРІМ рядка:",
        "options": options,
        "labels": labels,
        "answer": labels[wrong_idx],
        "hint": "Прочитай кожне слово вголос, перевіряючи типові слова-пастки НМТ (фено́мен, куліна́рія, листопа́д, коле́со, ви́падок).",
        "rule": "На НМТ щороку перевіряють нормативний наголос: фено́мен, куліна́рія, листопа́д, коле́со, спина́, фа́ртух, ви́падок, центне́р, ці́нник, ви́трата.",
        "solution": f"Помилка у варіанті {labels[wrong_idx]}: «{wrong_item[0]}» — {wrong_item[1]}.",
        "drill_key": "ukrmova_nagolos",
    }


@register_drill("ukrmova_double")
def gen_ukrmova_double():
    pure_no = [
        ("барок..о", "бароко"), ("фін..ський", "фінський"), ("ан..отація", "анотація"),
        ("лібрет..о", "лібрето"), ("ім..ітація", "імітація"), ("хоб..і", "хобі"),
        ("ал..ея", "алея"), ("ем..ігрант", "емігрант"), ("крос..ворд", "кросворд"),
        ("кол..екція", "колекція"), ("мас..а", "маса"), ("дискус..ія", "дискусія"),
    ]
    pure_yes = [
        ("буд..изм", "буддизм (власна назва Будда → подвоєння)"),
        ("андор..ський", "андоррський (Андорра → подвоєння)"),
        ("гол..андський", "голландський (Голландія → подвоєння)"),
        ("тон..а", "тонна (виняток!)"),
        ("віл..а", "вілла (виняток!)"),
        ("ван..а", "ванна (виняток!)"),
        ("брут..о", "брутто (виняток!)"),
        ("нет..о", "нетто (виняток!)"),
    ]
    good = random.sample(pure_no, 3)
    correct_idx = random.randint(0, 3)
    options = []
    for i in range(4):
        if i == correct_idx:
            options.append(", ".join(w[0] for w in good))
        else:
            b = random.choice(pure_yes)
            g2 = random.sample([w for w in pure_no if w not in good], 2)
            row = [g2[0][0], b[0], g2[1][0]]
            random.shuffle(row)
            options.append(", ".join(row))
    labels = ["А", "Б", "В", "Г"]
    return {
        "subject": "ukrmova",
        "section": "Орфографія",
        "source": "Генератор за програмою НМТ (2022–2026)",
        "qtype": "single",
        "max_points": 1,
        "prompt": "НЕ ТРЕБА писати подвоєних букв у всіх словах рядка:",
        "options": options,
        "labels": labels,
        "answer": labels[correct_idx],
        "hint": "У загальних запозичених словах подвоєння зазвичай НЕМАЄ (алея, хобі, бароко). Подвоєння зберігається лише у винятках (тонна, вілла, ванна, брутто, нетто) та у словах від власних назв (буддизм, андоррський).",
        "rule": "В українській мові в загальних словах іншомовного походження подвоєння приголосних не передається (бароко, лібрето, хобі, фінський, анотація). Винятки: тонна, вілла, ванна, мадонна, брутто, нетто, мірра та похідні від власних назв (буддизм, голландський, андоррський).",
        "solution": f"У рядку {labels[correct_idx]} усі слова — загальні назви без винятків: {', '.join(w[1] for w in good)}.",
        "drill_key": "ukrmova_double",
    }


@register_drill("ukrmova_myak")
def gen_ukrmova_myak():
    yes_b = [
        ("нян..чин", "няньчин"), ("запоріз..кий", "запорізький"),
        ("перекин..те", "перекиньте"), ("слиз..ко", "слизько"),
        ("учител..ський", "учительський"), ("погод..ся", "погодься"),
        ("сіл..ський", "сільський"), ("виріз..блений", "вирізьблений"),
        ("по-польс..кому", "по-польському"), ("донец..кий", "донецький"),
    ]
    no_b = [
        ("камін..чик", "камінчик (перед Ч після Н знак м’якшення не пишеться)"),
        ("тон..ший", "тонший (перед Ш після Н знак м’якшення не пишеться)"),
        ("велогон..щик", "велогонщик (перед Щ після Н знак м’якшення не пишеться)"),
        ("брин..чати", "бринчати (перед Ч після Н знак м’якшення не пишеться)"),
        ("базікаєш..", "базікаєш (після шиплячих знак м’якшення ніколи не пишеться)"),
        ("чотир..ма", "чотирма (після Р у середині/кінці слова знак м’якшення не пишеться)"),
    ]
    good = random.sample(yes_b, 3)
    correct_idx = random.randint(0, 3)
    options = []
    for i in range(4):
        if i == correct_idx:
            options.append(", ".join(w[0] for w in good))
        else:
            b = random.choice(no_b)
            g2 = random.sample([w for w in yes_b if w not in good], 2)
            row = [g2[0][0], b[0], g2[1][0]]
            random.shuffle(row)
            options.append(", ".join(row))
    labels = ["А", "Б", "В", "Г"]
    return {
        "subject": "ukrmova",
        "section": "Орфографія",
        "source": "Генератор за програмою НМТ (2022–2026)",
        "qtype": "single",
        "max_points": 1,
        "prompt": "М’який знак на місці пропуску треба писати в усіх словах рядка:",
        "options": options,
        "labels": labels,
        "answer": labels[correct_idx],
        "hint": "Пам’ятай: після Н перед Ж, Ч, Ш, Щ (інший, менший, камінчик, гонщик) і після Р (чотирма) м’який знак НЕ пишеться!",
        "rule": "Ь пишеться після Д, Т, З, С, Ц, Л, Н («Де Ти З’їСи Ці ЛиНи»), у суфіксах -ськ-, -зьк-, -цьк-, у наказовому способі. НЕ пишеться: після шиплячих (читаєш), після Р (чотирма), а також у сполуках НЧ, НШ, НЩ (камінчик, тонший, гонщик).",
        "solution": f"Правильний рядок {labels[correct_idx]}: {', '.join(w[1] for w in good)}.",
        "drill_key": "ukrmova_myak",
    }


@register_drill("ukrmova_rodovyi")
def gen_ukrmova_rodovyi():
    u_words = [
        ("конкурсного бал..", "конкурсного балу (абстрактне поняття/величина)"),
        ("сильного вітр..", "сильного вітру (явище природи)"),
        ("весняного дощ..", "весняного дощу (опади)"),
        ("запашного ча..", "запашного чаю (напій/речовина)"),
        ("міцного цукр..", "міцного цукру (речовина)"),
        ("зеленого га..", "зеленого гаю (збірний простір)"),
    ]
    a_words = [
        ("складання парашут..", "парашута (конкретний предмет)"),
        ("відстань одного кілометр..", "кілометра (міра довжини)"),
        ("висота старого дуб..", "дуба (окреме дерево)"),
        ("ціна нового телефон..", "телефона (конкретний прилад)"),
        ("розмір прямокутник..", "прямокутника (геометрична фігура)"),
        ("діаметр круг..", "круга (геометрична фігура)"),
        ("початок березн..", "березня (місяць)"),
    ]
    win = random.choice(u_words)
    wrongs = random.sample(a_words, 3)
    correct_idx = random.randint(0, 3)
    options = []
    w_ptr = 0
    for i in range(4):
        if i == correct_idx:
            options.append(win[0])
        else:
            options.append(wrongs[w_ptr][0])
            w_ptr += 1
    labels = ["А", "Б", "В", "Г"]
    return {
        "subject": "ukrmova",
        "section": "Морфологія",
        "source": "Генератор за програмою НМТ (2022–2026)",
        "qtype": "single",
        "max_points": 1,
        "prompt": "Закінчення -у (-ю) у родовому відмінку однини треба писати на місці пропуску в слові:",
        "options": options,
        "labels": labels,
        "answer": labels[correct_idx],
        "hint": "Конкретні предмети, люди, дерева, міри довжини та терміни-фігури мають -а (-я). Речовини, явища природи, абстрактні поняття — -у (-ю).",
        "rule": "У родовому відмінку однини іменників II відміни -а/-я пишемо в чітко окреслених предметів (парашута, телефона), мір (кілометра), місяців (березня), дерев (дуба). Закінчення -у/-ю пишемо в речовин (цукру, чаю), явищ природи (вітру, дощу) та абстрактних понять (балу, успіху).",
        "solution": f"Правильна відповідь {labels[correct_idx]}: «{win[1]}». Інші слова позначають конкретні предмети або одиниці виміру й мають закінчення -а/-я.",
        "drill_key": "ukrmova_rodovyi",
    }


# ============================= МАТЕМАТИКА ==================================

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
        "source": "Генератор за програмою НМТ (2022–2026)",
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
    ans_str = _fmt_num(total)
    return {
        "subject": "math",
        "section": "Числа і вирази",
        "source": "Генератор за програмою НМТ (2022–2026)",
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
            f"• Мама: {base} · {100 - d1}% = {_fmt_num(base * (100 - d1) / 100)} грн\n"
            f"• Дитина: {base} · {100 - d2}% = {_fmt_num(base * (100 - d2) / 100)} грн\n"
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
    g = _gcd(fav, total)
    num, den = fav // g, total // g
    ans_str = f"{num}/{den}"
    candidates = [
        f"{num}/{den}",
        f"{a}/{total}" if _gcd(a, total) == 1 else f"{a // _gcd(a, total)}/{total // _gcd(a, total)}",
        f"{b}/{total}" if _gcd(b, total) == 1 else f"{b // _gcd(b, total)}/{total // _gcd(b, total)}",
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
        "source": "Генератор за програмою НМТ (2022–2026)",
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
        "source": "Генератор за програмою НМТ (2022–2026)",
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
        "source": "Генератор за програмою НМТ (2022–2026)",
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
        "source": "Генератор за програмою НМТ (2022–2026)",
        "qtype": "short",
        "max_points": 2,
        "prompt": f"Визначте точку {target_word} функції f(x) = x³ {b_str}x² {c_str}x + {d_coef}.",
        "answer": _fmt_num(ans),
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
        "source": "Генератор за програмою НМТ (2022–2026)",
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
    ans = _fmt_num(val)
    neg = _fmt_num(-val)
    wrong1 = _fmt_num(d + b)
    wrong2 = _fmt_num(1.0 / d + b)
    wrong3 = _fmt_num(val + 0.5)
    opts = []
    for x in [ans, neg, wrong1, wrong2, wrong3]:
        if x not in opts:
            opts.append(x)
    while len(opts) < 5:
        opts.append(_fmt_num(val + len(opts)))
    random.shuffle(opts)
    labels = ["А", "Б", "В", "Г", "Д"]
    c_idx = opts.index(ans)
    return {
        "subject": "math",
        "section": "Числа і вирази",
        "source": "Генератор за програмою НМТ (2022–2026)",
        "qtype": "single",
        "max_points": 1,
        "prompt": f"Обчисліть значення виразу |{d}⁻¹ − {b}|.",
        "options": opts,
        "labels": labels,
        "answer": labels[c_idx],
        "hint": f"Увага! {d}⁻¹ — це НЕ −{d}, а дріб 1/{d}! І модуль числа завжди ≥ 0.",
        "rule": "Дві головні пастки НМТ: 1) a⁻¹ = 1/a (від’ємний показник перевертає число, а не змінює знак); 2) модуль |x| завжди невід’ємний.",
        "solution": f"1) {d}⁻¹ = 1/{d} = {_fmt_num(1.0/d)}.\n2) {_fmt_num(1.0/d)} − {b} = {_fmt_num(1.0/d - b)}.\n3) |{_fmt_num(1.0/d - b)}| = {ans} ({labels[c_idx]}).",
        "drill_key": "math_module_pow",
    }


# ========================== ІСТОРІЯ УКРАЇНИ ================================

@register_drill("hist_dates_20c")
def gen_hist_dates_20c():
    pool = [
        ("Утворення Української Центральної Ради", "березень 1917 р."),
        ("Проголошення IV Універсалу УЦР (незалежність УНР)", "січень 1918 р."),
        ("Державний переворот П. Скоропадського", "квітень 1918 р."),
        ("Утворення Директорії УНР", "листопад 1918 р."),
        ("Проголошення Акта Злуки УНР і ЗУНР", "22 січня 1919 р."),
        ("Підписання Варшавської угоди (Петлюра–Пілсудський)", "квітень 1920 р."),
        ("Другий Зимовий похід Армії УНР", "листопад 1921 р."),
        ("Утворення Української Гельсінської групи", "листопад 1976 р."),
        ("Ухвалення Декларації про державний суверенітет України", "16 липня 1990 р."),
        ("Акт проголошення незалежності України", "24 серпня 1991 р."),
        ("Ухвалення Конституції України", "28 червня 1996 р."),
        ("Початок АТО / окупація Криму РФ", "2014 р."),
    ]
    sample = random.sample(pool, 4)
    target = sample[0]
    opts = [s[1] for s in sample]
    random.shuffle(opts)
    labels = ["А", "Б", "В", "Г"]
    c_idx = opts.index(target[1])
    return {
        "subject": "history",
        "section": "Україна в 1914–1945 рр.",
        "source": "Генератор за програмою НМТ (2022–2026)",
        "qtype": "single",
        "max_points": 1,
        "prompt": f"Коли відбулася подія: «{target[0]}»?",
        "options": opts,
        "labels": labels,
        "answer": labels[c_idx],
        "hint": "Пов’яжи подію з головним політичним періодом (УЦР → Гетьманат → Директорія → 1920–1921 → дисиденти → Незалежність).",
        "rule": "На НМТ з історії хронологія XX–XXI ст. дає до третини всіх балів. Запам’ятай ключові віхи: 1917 (УЦР), 04.1918 (Скоропадський), 11.1918 (Директорія), 04.1920 (Варшавський договір), 1976 (УГГ), 1991 (Незалежність).",
        "solution": f"Правильна дата події «{target[0]}» — {target[1]} ({labels[c_idx]}).",
        "drill_key": "hist_dates_20c",
    }


@register_drill("hist_chrono_17c")
def gen_hist_chrono_17c():
    events_pools = [
        [
            ("Берестейська церковна унія", 1596),
            ("Морський похід козаків на Кафу (П. Сагайдачний)", 1616),
            ("Куруківська угода", 1625),
            ("Зборівський договір", 1649),
            ("Білоцерківський договір", 1651),
            ("Віленське перемир’я", 1656),
            ("Гадяцький договір", 1658),
            ("Андрусівське перемир’я", 1667),
        ],
        [
            ("Початок Першої світової війни на українських землях", 1914),
            ("Ухвалення I Універсалу УЦР", 1917),
            ("Варшавська угода УНР і Польщі", 1920),
            ("Голодомор в Україні (пік трагедії)", 1933),
            ("Пакт Молотова — Ріббентропа", 1939),
            ("Входження Криму до складу УРСР", 1954),
            ("Створення Української Гельсінської групи", 1976),
            ("Революція на граніті", 1990),
        ],
    ]
    pool = random.choice(events_pools)
    chosen = random.sample(pool, 4)
    letters = ["А", "Б", "В", "Г"]
    random.shuffle(chosen)
    items = {letters[i]: chosen[i][0] for i in range(4)}
    sorted_pairs = sorted(zip(letters, chosen), key=lambda p: p[1][1])
    ans = "".join(p[0] for p in sorted_pairs)
    chron_text = "\n".join(f"{i+1}. {p[0]} — {p[1][0]} ({p[1][1]} р.)" for i, p in enumerate(sorted_pairs))
    return {
        "subject": "history",
        "section": "Друга половина XVI–XVIII ст.",
        "source": "Генератор за програмою НМТ (2022–2026)",
        "qtype": "sequence",
        "max_points": 3,
        "prompt": "Установіть хронологічну послідовність подій (від найдавнішої до найпізнішої). Запишіть 4 букви без пробілів (наприклад, ГБАВ):",
        "items": items,
        "answer": ans,
        "hint": "Спочатку знайди найдавнішу (1-шу) і найпізнішу (4-ту) подію — навіть за їхні правильні позиції на НМТ уже нараховують бали!",
        "rule": "За завдання на послідовність на НМТ можна отримати від 0 до 3 балів. Порада: завжди починай із «якорів» — найдавнішої та найпізнішої події.",
        "solution": f"Правильна послідовність: {ans}.\n{chron_text}",
        "drill_key": "hist_chrono_17c",
    }


@register_drill("hist_terms_19c")
def gen_hist_terms_19c():
    pairs = [
        ("«хлопомани»", "рух частини польської чи спольщеної шляхетської інтелігенції на Правобережжі середини ХІХ ст., що прагнула зближення з українським селянством (В. Антонович, Т. Рильський)"),
        ("«москвофіли»", "суспільна течія середини ХІХ ст. на Галичині, Буковині та Закарпатті, що виступала за культурну й державну єдність із Росією"),
        ("«народовці»", "суспільно-культурний рух у Західній Україні з 1860-х рр., що обстоював самостійність українського народу та розвиток народної мови"),
        ("«радикали»", "політична течія 1870–1890-х рр. у Галичині (І. Франко, М. Павлик), яка заснувала першу українську політичну партію (РУРП) і вперше висунула гасло незалежності України"),
        ("«ждановщина»", "ідеологічна кампанія 1946–1953 рр. в СРСР проти діячів культури, науки й літератури, спрямована на посилення партійного контролю та боротьбу з «націоналізмом»"),
        ("«шістдесятники»", "покоління української інтелігенції кінця 1950-х – 1960-х рр., яке виступало за оновлення культури, свободу творчості та захист національної самобутності"),
    ]
    sample = random.sample(pairs, 4)
    target = sample[0]
    opts = [s[0] for s in sample]
    random.shuffle(opts)
    labels = ["А", "Б", "В", "Г"]
    c_idx = opts.index(target[0])
    return {
        "subject": "history",
        "section": "Кінець XVIII – початок XX ст.",
        "source": "Генератор за програмою НМТ (2022–2026)",
        "qtype": "single",
        "max_points": 1,
        "prompt": f"Якому поняттю відповідає визначення: «{target[1]}»?",
        "options": opts,
        "labels": labels,
        "answer": labels[c_idx],
        "hint": "Зверни увагу на ключові слова: регіон (Галичина чи Правобережжя), період і головну мету руху.",
        "rule": "На НМТ часто плутають течії XIX ст. Запам’ятай: хлопомани — Правобережжя (Антонович), москвофіли — за єдність із Росією, народовці — просвітництво й народна мова, радикали — перша партія і незалежність (Франко).",
        "solution": f"Це визначення стосується поняття {target[0]} ({labels[c_idx]}).",
        "drill_key": "hist_terms_19c",
    }


# ---------------------------------------------------------------------------
# ОФІЦІЙНА БАЗА ЗАВДАНЬ 2026 (ЗІ ЗВІТУ УЦОЯО) + ПРОГРАМНІ ЗАВДАННЯ
# ---------------------------------------------------------------------------

STATIC_QUESTIONS = {
    "ukrmova": [
        {
            "id": "ukrmova_2026_1",
            "subject": "ukrmova",
            "section": "Фонетика. Графіка. Орфоепія",
            "source": "Офіційний зразок НМТ-2026 (УЦОЯО)",
            "qtype": "single",
            "max_points": 1,
            "prompt": "Звук [з] є в кожному слові рядка:",
            "options": [
                "дзеркало, мазати, зухвало",
                "змінити, беззубий, показ",
                "розмова, глузд, з’явитися",
                "зшити, з’їжджати, перелаз",
            ],
            "labels": ["А", "Б", "В", "Г"],
            "answer": "В",
            "hint": "Зверни увагу на асиміляцію: м’яке «змінити» дає [з'], «дзеркало» — це злитий звук [д͡з], а «зшити» вимовляється як [ш:]!",
            "rule": "В українській фонетиці ДЗ — це один звук [д͡з], перед м’якими приголосними (змінити) звук [з] пом’якшується у [з'], а в слові «зшити» відбувається уподібнення [з+ш] → [ш:].",
            "solution": "У варіанті В в усіх словах чистий твердий [з]: ро[з]мова, глу[з]д, [з]’явитися. В А — [д͡з]еркало, у Б — [з']мінити, у Г — [ш:]ити.",
            "drill_key": "ukrmova_nagolos",
        },
        {
            "id": "ukrmova_2026_2",
            "subject": "ukrmova",
            "section": "Фонетика. Графіка. Орфоепія",
            "source": "Офіційний зразок НМТ-2026 (УЦОЯО)",
            "qtype": "single",
            "max_points": 1,
            "prompt": "Правильно виділено букви на позначення наголошених звуків у всіх словах рядка (ВЕЛИКА буква вказує на наголос):",
            "options": [
                "феномЕн пізнання, довідник з кулінарІї",
                "посерЕдині літОпису, завчАсу закінчити",
                "дивлячись на цІнник, чергова вИтрата",
                "принести кОлесо, одинАдцять кілометрів",
            ],
            "labels": ["А", "Б", "В", "Г"],
            "answer": "В",
            "hint": "Перевір наголоси у словах «феномен», «літопис», «цінник», «витрата», «колесо».",
            "rule": "Обов’язкові наголоси НМТ: цІнник, вИтрата, фенОмен, кулінАрія, літОпис, завчасУ, колЕсо.",
            "solution": "Правильні обидва наголоси лише у В: цІнник, вИтрата. В А неправильно: фенОмен, кулінАрії; у Б: літОпису (правильно), але завчасУ; у Г: колЕсо.",
            "drill_key": "ukrmova_nagolos",
        },
        {
            "id": "ukrmova_2026_3",
            "subject": "ukrmova",
            "section": "Орфографія",
            "source": "Офіційний зразок НМТ-2026 (УЦОЯО)",
            "qtype": "single",
            "max_points": 1,
            "prompt": "Букву и треба писати на місці пропуску в усіх словах рядка:",
            "options": [
                "павут..ння, ластов..ння, нач..ння",
                "гарбуз..ння, шаруд..ння, жабур..ння",
                "шумов..ння, покол..ння, буряч..ння",
                "лушп..ння, управл..ння, картопл..ння",
            ],
            "labels": ["А", "Б", "В", "Г"],
            "answer": "А",
            "hint": "Збірні іменники від рослин і предметів (павутиння, ластовиння, начиння) пишуться з И, а віддієслівні (шарудіння, покоління, управління) — з І!",
            "rule": "Суфікс -инн(я) з літерою И пишемо у словах на позначення рослин і збірних понять (павутиння, ластовиння, начиння, гарбузиння, картоплиння). Віддієслівні іменники мають -інн(я) (шарудіння, управління).",
            "solution": "У рядку А всі три слова пишуться з И: павутиння, ластовиння, начиння. У Б — шарудіння, у В — покоління, у Г — управління.",
            "drill_key": "ukrmova_double",
        },
        {
            "id": "ukrmova_2026_4",
            "subject": "ukrmova",
            "section": "Орфографія",
            "source": "Офіційний зразок НМТ-2026 (УЦОЯО)",
            "qtype": "single",
            "max_points": 1,
            "prompt": "Префікс с- треба писати на місці пропуску в усіх словах, ОКРІМ рядка:",
            "options": [
                "..творення, ..писати, ..фабрикований",
                "..поряджений, ..твердити, ..ходження",
                "..пустошення, ..жалитися, ..каменілий",
                "..копіювати, ..формований, ..пізнення",
            ],
            "labels": ["А", "Б", "В", "Г"],
            "answer": "В",
            "hint": "Застосуй правило «КаФе «ПТаХ»»: перед К, Ф, П, Т, Х пишемо С-, перед іншими — З-.",
            "rule": "Префікс С- пишемо тільки перед приголосними К, Ф, П, Т, Х («КаФе «ПТаХ»»).",
            "solution": "У рядку В слово «зжалитися» починається на Ж (не входить до «КаФе ПТаХ»), тому там потрібен префікс З-.",
            "drill_key": "ukrmova_pref_zs",
        },
        {
            "id": "ukrmova_2026_5",
            "subject": "ukrmova",
            "section": "Орфографія",
            "source": "Офіційний зразок НМТ-2026 (УЦОЯО)",
            "qtype": "single",
            "max_points": 1,
            "prompt": "М’який знак на місці пропуску треба писати в усіх словах рядка:",
            "options": [
                "слиз..ко, тон..ший, по-польс..кому",
                "сіл..ський, базікаєш.., брин..чати",
                "нян..чин, запоріз..кий, перекин..те",
                "розніс..ся, кременчуц..кий, брун..ці",
            ],
            "labels": ["А", "Б", "В", "Г"],
            "answer": "В",
            "hint": "Пам’ятай про винятки: перед Ч, Ш, Щ після Н (тонший, бринчати), у дієсловах на -ш (базікаєш) і в слові «рознісся» Ь не пишеться.",
            "rule": "Ь пишеться в няньчин (від нянька), запорізький (-зьк-), перекиньте (наказовий спосіб). Перед Ш/Ч після Н (тонший, бринчати) і після шиплячих (базікаєш) Ь не пишеться.",
            "solution": "Правильний варіант В: няньчин, запорізький, перекиньте.",
            "drill_key": "ukrmova_myak",
        },
        {
            "id": "ukrmova_2026_6",
            "subject": "ukrmova",
            "section": "Орфографія",
            "source": "Офіційний зразок НМТ-2026 (УЦОЯО)",
            "qtype": "single",
            "max_points": 1,
            "prompt": "НЕ ТРЕБА писати подвоєних букв у всіх словах рядка:",
            "options": [
                "ал..ея, ем..ігрант, андор..ський",
                "крос..ворд, контр..еволюція, хоб..і",
                "барок..о, фін..ський, ан..отація",
                "лібрет..о, буд..изм, ім..ітація",
            ],
            "labels": ["А", "Б", "В", "Г"],
            "answer": "В",
            "hint": "«Андоррський» і «буддизм» утворено від власних назв (Андорра, Будда), а у слові «контрреволюція» — збіг префікса й кореня.",
            "rule": "У загальних запозичених словах подвоєння немає (бароко, фінський, анотація). Подвоєння зберігається на межі частин слова (контрреволюція) та в похідних від власних назв (андоррський, буддизм).",
            "solution": "Лише у В немає жодного подвоєння: бароко, фінський, анотація.",
            "drill_key": "ukrmova_double",
        },
        {
            "id": "ukrmova_2026_7",
            "subject": "ukrmova",
            "section": "Орфографія",
            "source": "Офіційний зразок НМТ-2026 (УЦОЯО)",
            "qtype": "single",
            "max_points": 1,
            "prompt": "Разом треба писати всі слова в рядку:",
            "options": [
                "аква/техніка, екс/чемпіонка, держ/мито",
                "напів/фабрикат, сто/річчя, край/небо",
                "полу/мисок, гори/цвіт, бета/розпад",
                "пів/коло, блок/система, густо/лісся",
            ],
            "labels": ["А", "Б", "В", "Г"],
            "answer": "Б",
            "hint": "Складні слова з першою частиною «екс-», «бета-», а також прикладки «блок-система» пишуться через дефіс!",
            "rule": "Слова з напів-, сто-, багато- та складні іменники зі сполучним голосним пишуться РАЗОМ (напівфабрикат, сторіччя, крайнебо). Компоненти екс-, віце-, міні-, максі-, бета-розпад, блок-система — через ДЕФІС.",
            "solution": "У рядку Б усі слова пишуться разом: напівфабрикат, сторіччя, крайнебо.",
            "drill_key": "ukrmova_double",
        },
        {
            "id": "ukrmova_2026_15",
            "subject": "ukrmova",
            "section": "Лексикологія. Фразеологія",
            "source": "Офіційний зразок НМТ-2026 (УЦОЯО)",
            "qtype": "single",
            "max_points": 1,
            "prompt": "Українським відповідником до іншомовного слова «елемент» є:",
            "options": ["складник", "приклад", "цілість", "єдність", "мережа"],
            "labels": ["А", "Б", "В", "Г", "Д"],
            "answer": "А",
            "hint": "Слово «елемент» означає складову частину чого-небудь.",
            "rule": "На НМТ часто просять дібрати український синонім до запозиченого слова: елемент = складник, пріоритет = першочерговість, епатувати = вражати.",
            "solution": "Елемент — це складова частина, тобто «складник» (А).",
            "drill_key": "ukrmova_rodovyi",
        },
        {
            "id": "ukrmova_2026_16",
            "subject": "ukrmova",
            "section": "Морфологія",
            "source": "Офіційний зразок НМТ-2026 (УЦОЯО)",
            "qtype": "single",
            "max_points": 1,
            "prompt": "Правильною відповіддю на запитання «Котра година?» буде:",
            "options": [
                "без п’ятнадцяти сьома",
                "половина шостої",
                "три години дві хвилини",
                "двадцять сорок",
                "за п’ять хвилин друга",
            ],
            "labels": ["А", "Б", "В", "Г", "Д"],
            "answer": "Д",
            "hint": "В українській мові НЕ кажуть «без п’ятнадцяти», «половина шостої» або просто «три години». Потрібні прийменники «за», «на», «по» й порядковий числівник!",
            "rule": "Правильне позначення часу в українській мові: «за п’ять хвилин друга» (13:55), «пів на шосту» (не «половина»), «о третій годині дві хвилини».",
            "solution": "Єдиний нормативний варіант — «за п’ять хвилин друга» (Д).",
            "drill_key": "ukrmova_rodovyi",
        },
        {
            "id": "ukrmova_2026_19",
            "subject": "ukrmova",
            "section": "Морфологія",
            "source": "Офіційний зразок НМТ-2026 (УЦОЯО)",
            "qtype": "single",
            "max_points": 1,
            "prompt": "Закінчення -у на місці пропуску треба писати в слові рядка:",
            "options": [
                "технологія складання парашут..",
                "іхтіофауна Південного Буг..",
                "обчислення конкурсного бал..",
                "на відстані одного кілометр..",
                "гідрологічний режим Дністр..",
            ],
            "labels": ["А", "Б", "В", "Г", "Д"],
            "answer": "В",
            "hint": "Бал — це абстрактна оцінка, величина. А парашут (предмет), кілометр (міра) і річки з наголосом на основі/закінченні (Дністра, Буга) мають інші правила.",
            "rule": "Закінчення -у/-ю в родовому відмінку пишеться в абстрактних понять і термінів (конкурсного балу), а конкретні предмети (парашута) та одиниці виміру (кілометра) мають -а.",
            "solution": "«Обчислення конкурсного балу» (В) — абстрактне поняття, закінчення -у.",
            "drill_key": "ukrmova_rodovyi",
        },
        {
            "id": "ukrmova_2026_26",
            "subject": "ukrmova",
            "section": "Лексикологія. Фразеологія",
            "source": "Офіційний зразок НМТ-2026 (УЦОЯО)",
            "qtype": "matching",
            "max_points": 4,
            "prompt": (
                "Доберіть до кожного речення (1–4) відповідний фразеологізм (А–Д):\n"
                "1. Прагнучи з’ясувати причину проблеми, ви маєте говорити прямо, а не […].\n"
                "2. Звичайно, легше […], аніж самотужки намагатися знайти нестандартний спосіб.\n"
                "3. Маєте вивчити питання докорінно, аби діяти чітко, а не […].\n"
                "4. Після успішного завершення справи кожному хочеться […], бо добре попрацювали."
            ),
            "left": ["1. Говорити прямо, а не […]", "2. Легше […], ніж шукати нове", "3. Діяти чітко, а не […]", "4. Після успіху хочеться […]"],
            "right": {
                "А": "ходити з темними очима",
                "Б": "ходити довкола",
                "В": "ходити іменинником",
                "Г": "ходити второваними стежками",
                "Д": "ходити манівцями",
            },
            "answer": {"1": "Б", "2": "Г", "3": "Д", "4": "В"},
            "hint": "«Второвані стежки» — звичний, легкий шлях; «ходити іменинником» — радіти й пишатися успіхом.",
            "rule": "Значення фразеологізмів перевіряємо за контекстом: довкола (навколо, не прямо), второвані стежки (шаблонний шлях), манівці (обхідні/хибні шляхи), іменинник (гордий переможець).",
            "solution": "1–Б (говорити не прямо = ходити довкола), 2–Г (не шукати нестандартного = второвані стежки), 3–Д (діяти нечітко/плутано = ходити манівцями), 4–В (святкувати успіх = ходити іменинником).",
            "drill_key": "ukrmova_pref_zs",
        },
        {
            "id": "ukrmova_2026_27",
            "subject": "ukrmova",
            "section": "Морфологія",
            "source": "Офіційний зразок НМТ-2026 (УЦОЯО)",
            "qtype": "matching",
            "max_points": 4,
            "prompt": (
                "З’ясуйте, якою частиною мови (А–Д) є виділені в реченні слова (1–4):\n"
                "«Інтерес до вивчення мов [1: ЗАВЖДИ] високий, бо можемо стверджувати, "
                "[2: ЩО] той, [3: ХТО] знатиме їх багато, отримає ключ [4: ДО] успіху.»"
            ),
            "left": ["1. ЗАВЖДИ", "2. ЩО", "3. ХТО", "4. ДО"],
            "right": {"А": "частка", "Б": "сполучник", "В": "займенник", "Г": "прислівник", "Д": "прийменник"},
            "answer": {"1": "Г", "2": "Б", "3": "В", "4": "Д"},
            "hint": "«Що» тут лише з’єднує частини речення (не можна замінити іменником), а «хто» вказує на особу.",
            "rule": "Відрізняй сполучник «що» від займенника «що»: якщо «що» не можна замінити іншим словом і воно не є членом речення — це сполучник. «Хто» — завжди займенник. «Завжди» (коли?) — прислівник.",
            "solution": "1–Г (завжди = прислівник), 2–Б (що = сполучник), 3–В (хто = займенник), 4–Д (до = прийменник).",
            "drill_key": "ukrmova_rodovyi",
        },
        {
            "id": "ukrmova_2026_29",
            "subject": "ukrmova",
            "section": "Синтаксис. Пунктуація",
            "source": "Офіційний зразок НМТ-2026 (УЦОЯО)",
            "qtype": "matching",
            "max_points": 4,
            "prompt": "Доберіть приклад (А–Д) до кожного типу складного речення (1–4):",
            "left": ["1. Складносурядне", "2. Складнопідрядне", "3. Безсполучникове", "4. З різними видами зв’язку"],
            "right": {
                "А": "Стояла ніч, красива, мов Кармен, червоні й чорні міряла троянди.",
                "Б": "Іронія – це блискавка ума, яка освітить всі глибини смислу.",
                "В": "Візьми від життя все, що зможеш, і воно засяє яскравими барвами.",
                "Г": "Зіграй мені мелодію любові і обернеться хай на щастя розпач!",
                "Д": "Завалились мости кам’яні – подорожні шукають веселку.",
            },
            "answer": {"1": "Г", "2": "Б", "3": "Д", "4": "В"},
            "hint": "В одному з речень дві граматичні основи з’єднані лише тире (без сполучників), а одне речення взагалі ПРОСТЕ з однорідними присудками (пастка!).",
            "rule": "1) Виділяй усі граматичні основи (підмет + присудок). У реченні А основа ОДНА («ніч стояла й міряла») — це просте речення! 2) Сурядний сполучник (і, та, але) між двома основами → складносурядне; 3) підрядний (яка, що, бо) → складнопідрядне; 4) без сполучників (тире/двокрапка/кома) → безсполучникове.",
            "solution": "1–Г (сполучник «і» між основами), 2–Б (сполучне слово «яка»), 3–Д (дві основи через тире без сполучника), 4–В (підрядний «що» + сурядний «і»).",
            "drill_key": "ukrmova_pref_zs",
        },
        {
            "id": "ukrmova_2026_30",
            "subject": "ukrmova",
            "section": "Синтаксис. Пунктуація",
            "source": "Офіційний зразок НМТ-2026 (УЦОЯО)",
            "qtype": "matching",
            "max_points": 4,
            "prompt": "Доберіть приклад (А–Д) до кожного типу відокремленого члена речення (1–4):",
            "left": ["1. Відокремлене означення", "2. Відокремлена прикладка", "3. Відокремлена обставина", "4. Відокремлений додаток"],
            "right": {
                "А": "Кирилівська церква в Києві, зведена ще в середині ХІІ століття, – видатна пам’ятка.",
                "Б": "За майже дев’ять століть цей храм пережив періоди розквіту і занепаду.",
                "В": "У 1929 р., зважаючи на виняткову цінність церкви, відкрили музей-заповідник.",
                "Г": "Тут поховано Святослава Всеволодовича – прототипа одного з героїв поеми.",
                "Д": "Можемо побачити справжні скарби, зокрема фрески ХІІ століття, олійний стінопис.",
            },
            "answer": {"1": "А", "2": "Г", "3": "В", "4": "Д"},
            "hint": "Шукай маркери: дієприкметниковий зворот (означення), друга назва іменника через тире (прикладка), дієприслівниковий зворот (обставина) і слова «зокрема, крім, окрім» (додаток).",
            "rule": "Відокремлений додаток майже завжди починається зі слів «крім, окрім, опріч, за винятком, зокрема». Прикладка — іменник-характеристика через тире або кому.",
            "solution": "1–А («зведена ще в середині ХІІ ст.»), 2–Г («– прототипа...»), 3–В («зважаючи на...»), 4–Д («зокрема фрески...»).",
            "drill_key": "ukrmova_double",
        },
    ],
    "math": [
        {
            "id": "math_2026_1",
            "subject": "math",
            "section": "Комбінаторика, ймовірність, статистика",
            "source": "Офіційний зразок НМТ-2026 (УЦОЯО)",
            "qtype": "single",
            "max_points": 1,
            "prompt": "Камера зафіксувала кількість автомобілів у кожному інтервалі швидкості: 40–60 км/год (8 авто), 61–80 км/год (12 авто), 81–100 км/год (15 авто), 101–120 км/год (10 авто), понад 120 км/год (4 авто). Визначте загальну кількість автомобілів.",
            "options": ["15", "39", "48", "49", "59"],
            "labels": ["А", "Б", "В", "Г", "Д"],
            "answer": "Г",
            "hint": "Потрібно просто додати висоти всіх п’яти стовпчиків діаграми — не плутай із найвищим стовпчиком (15)!",
            "rule": "У задачах на читання діаграм уважно читай запитання: якщо питають «загальну кількість», потрібно додати всі категорії.",
            "solution": "8 + 12 + 15 + 10 + 4 = 49 автомобілів (варіант Г).",
            "drill_key": "math_prob",
        },
        {
            "id": "math_2026_2",
            "subject": "math",
            "section": "Числа і вирази",
            "source": "Офіційний зразок НМТ-2026 (УЦОЯО)",
            "qtype": "single",
            "max_points": 1,
            "prompt": "Дарина купила сир і фрукти, витративши 240 грн. Скільки грошей (грн) Дарина витратила на фрукти, якщо за сир вона заплатила 3/5 витраченої суми?",
            "options": ["96", "30", "34", "45", "60"],
            "labels": ["А", "Б", "В", "Г", "Д"],
            "answer": "А",
            "hint": "Якщо за сир заплатили 3/5 усієї суми, яка частина залишилася на фрукти?",
            "rule": "Коли дано частину одного товару (3/5), решта (другий товар) становить 1 − 3/5 = 2/5 від цілого. Помнож 240 на 2/5.",
            "solution": "1) На фрукти пішло 1 − 3/5 = 2/5 усієї суми.\n2) 240 · 2/5 = 48 · 2 = 96 грн (варіант А).",
            "drill_key": "math_percent_trip",
        },
        {
            "id": "math_2026_3",
            "subject": "math",
            "section": "Планіметрія",
            "source": "Офіційний зразок НМТ-2026 (УЦОЯО)",
            "qtype": "single",
            "max_points": 1,
            "prompt": "Будівельна драбина має форму рівнобічної трапеції ABCD (BC ∥ AD). Визначте градусну міру кута ∠BAD, якщо ∠BCD = 110°.",
            "options": ["80°", "70°", "55°", "50°", "20°"],
            "labels": ["А", "Б", "В", "Г", "Д"],
            "answer": "Б",
            "hint": "У рівнобічної трапеції кути при верхній основі рівні (∠B = ∠C = 110°), а сума кутів при бічній стороні дорівнює 180°.",
            "rule": "Сума кутів при бічній стороні трапеції = 180°. Тому гострий кут = 180° − тупий кут.",
            "solution": "∠BAD = 180° − 110° = 70° (варіант Б).",
            "drill_key": "math_trap_angle",
        },
        {
            "id": "math_2026_4",
            "subject": "math",
            "section": "Рівняння, нерівності та їх системи",
            "source": "Офіційний зразок НМТ-2026 (УЦОЯО)",
            "qtype": "single",
            "max_points": 1,
            "prompt": "Позначте з-поміж наведених найменше число, яке є розв’язком нерівності 2x + 7 > 27.",
            "options": ["0", "5", "10", "15", "20"],
            "labels": ["А", "Б", "В", "Г", "Д"],
            "answer": "Г",
            "hint": "Після розв’язання отримаєш x > 10. Чи входить сама десятка до розв’язку?",
            "rule": "За строгого знака '>' межове число (10) НЕ входить до відповіді! Із решти варіантів обираємо найменше більше за 10.",
            "solution": "2x > 20 ⇒ x > 10. Число 10 не підходить (нерівність строга), найменше з варіантів > 10 — це 15 (варіант Г).",
            "drill_key": "math_ineq",
        },
        {
            "id": "math_2026_7",
            "subject": "math",
            "section": "Комбінаторика, ймовірність, статистика",
            "source": "Офіційний зразок НМТ-2026 (УЦОЯО)",
            "qtype": "single",
            "max_points": 1,
            "prompt": "На столі лежать 18 світлин: 8 — із зображенням природи, 4 — із зображенням людини, 6 — із зображенням будівель. Яка ймовірність того, що навмання взята зі столу світлина буде із зображенням природи або будівлі?",
            "options": ["1/18", "1/14", "2/9", "2/3", "7/9"],
            "labels": ["А", "Б", "В", "Г", "Д"],
            "answer": "Д",
            "hint": "Додай кількість фото природи (8) і будівель (6), потім поділи на загальне число (18) та скороти дріб.",
            "rule": "Ймовірність P = m / n. Для події «А або Б» (несумісних) додаємо сприятливі випадки.",
            "solution": "(8 + 6) / 18 = 14 / 18 = 7/9 (варіант Д).",
            "drill_key": "math_prob",
        },
        {
            "id": "math_2026_9",
            "subject": "math",
            "section": "Числа і вирази",
            "source": "Офіційний зразок НМТ-2026 (УЦОЯО)",
            "qtype": "single",
            "max_points": 1,
            "prompt": "Спростіть вираз 25b − (b − 5)(5 + b) + 25.",
            "options": ["25b − b²", "25b − b² − 50", "25b + b² − 50", "25b − b² + 50", "25b + b²"],
            "labels": ["А", "Б", "В", "Г", "Д"],
            "answer": "Г",
            "hint": "(b − 5)(b + 5) = b² − 25. Увага на МІНУС перед дужками!",
            "rule": "Формула різниці квадратів: (a − b)(a + b) = a² − b². Якщо перед дужкою стоїть мінус, він змінює знаки КОЖНОГО доданка всередині!",
            "solution": "25b − (b² − 25) + 25 = 25b − b² + 25 + 25 = 25b − b² + 50 (варіант Г).",
            "drill_key": "math_module_pow",
        },
        {
            "id": "math_2026_11",
            "subject": "math",
            "section": "Рівняння, нерівності та їх системи",
            "source": "Офіційний зразок НМТ-2026 (УЦОЯО)",
            "qtype": "single",
            "max_points": 1,
            "prompt": "Розв’яжіть рівняння 3^x = 81 · 9^x.",
            "options": ["−4", "−2", "6", "−4/3", "4"],
            "labels": ["А", "Б", "В", "Г", "Д"],
            "answer": "А",
            "hint": "Заміни 81 на 3⁴, а 9^x на (3²)^x = 3^(2x).",
            "rule": "Зводимо до однієї основи 3: під час множення степенів з однаковою основою показники додаються.",
            "solution": "3^x = 3⁴ · 3^(2x) ⇒ 3^x = 3^(4 + 2x) ⇒ x = 4 + 2x ⇒ −x = 4 ⇒ x = −4 (варіант А).",
            "drill_key": "math_exp_eq",
        },
        {
            "id": "math_2026_14",
            "subject": "math",
            "section": "Числа і вирази",
            "source": "Офіційний зразок НМТ-2026 (УЦОЯО)",
            "qtype": "single",
            "max_points": 1,
            "prompt": "Обчисліть |5⁻¹ − 3|.",
            "options": ["8", "2,8", "2,5", "−2,8", "−8"],
            "labels": ["А", "Б", "В", "Г", "Д"],
            "answer": "Б",
            "hint": "5⁻¹ — це 1/5 = 0,2, а НЕ −5!",
            "rule": "a⁻¹ = 1/a, а модуль будь-якого числа завжди невід’ємний: |−2,8| = 2,8.",
            "solution": "|0,2 − 3| = |−2,8| = 2,8 (варіант Б).",
            "drill_key": "math_module_pow",
        },
        {
            "id": "math_2026_16",
            "subject": "math",
            "section": "Функції",
            "source": "Офіційний зразок НМТ-2026 (УЦОЯО)",
            "qtype": "matching",
            "max_points": 3,
            "prompt": "Доберіть до функції (1–3) її властивість (А–Д):",
            "left": ["1. y = x² + 2", "2. y = sin x", "3. y = 3x + 2"],
            "right": {
                "А": "спадає на всій області визначення",
                "Б": "графік функції проходить через точку (0; 0)",
                "В": "зростає на всій області визначення",
                "Г": "є парною",
                "Д": "графік симетричний відносно осі x",
            },
            "answer": {"1": "Г", "2": "Б", "3": "В"},
            "hint": "Перевір y(−x) для парності, підстав x=0 для точки (0; 0) і подивись на кутовий коефіцієнт k=3 у лінійної функції.",
            "rule": "x² — парна функція (y(−x) = y(x)); sin(0) = 0; лінійна функція kx + b при k > 0 завжди зростає.",
            "solution": "1–Г (y(−x) = (−x)²+2 = y(x), парна), 2–Б (sin 0 = 0), 3–В (k = 3 > 0 → зростає).",
            "drill_key": "math_deriv_ext",
        },
        {
            "id": "math_2026_19",
            "subject": "math",
            "section": "Функції",
            "source": "Офіційний зразок НМТ-2026 (УЦОЯО)",
            "qtype": "short",
            "max_points": 2,
            "prompt": "Визначте критичні точки функції f(x) = 4x³ + 9x² − 30x + 1. Яка із цих точок є точкою максимуму функції f(x)?",
            "answer": "-2,5",
            "hint": "Знайди f'(x) = 12x² + 18x − 30 = 0. Точка максимуму — там, де похідна змінює знак із '+' на '−'.",
            "rule": "Знаходимо похідну, прирівнюємо до 0. Для квадратичної похідної з плюсом перед x² знаки йдуть (+, −, +), тому менший корінь — точка максимуму.",
            "solution": "f'(x) = 12x² + 18x − 30 = 0 ⇒ 2x² + 3x − 5 = 0. Корені: x₁ = −2,5 і x₂ = 1. Перехід (+ → −) у точці −2,5.",
            "drill_key": "math_deriv_ext",
        },
        {
            "id": "math_2026_20",
            "subject": "math",
            "section": "Числа і вирази",
            "source": "Офіційний зразок НМТ-2026 (УЦОЯО)",
            "qtype": "short",
            "max_points": 2,
            "prompt": "Сім’я з трьох осіб — батька, мами й сина — запланувала сплав на байдарці. Вартість сплаву становить 800 грн із особи. Мамі й сину надають знижки: 20 % і 25 % відповідно. Скільки гривень ця сім’я заплатить за сплав з урахуванням наданих знижок?",
            "answer": "2040",
            "hint": "Батько платить 100 % (800), мама — 80 % від 800, син — 75 % від 800.",
            "rule": "Обчислюємо вартість зі знижкою для кожного члена сім’ї та додаємо.",
            "solution": "Батько: 800 грн; Мама: 800 · 0,8 = 640 грн; Син: 800 · 0,75 = 600 грн. Разом: 800 + 640 + 600 = 2040 грн.",
            "drill_key": "math_percent_trip",
        },
    ],
    "history": [
        {
            "id": "hist_2026_1",
            "subject": "history",
            "section": "Від найдавніших часів до першої половини XVI ст.",
            "source": "Офіційний зразок НМТ-2026 (УЦОЯО)",
            "qtype": "single",
            "max_points": 1,
            "prompt": "На світлинах із архіву Інституту археології НАН України зображено керівника експедиції Бориса Мозолевського та знайдену золоту пектораль. У якому скіфському кургані знайдено цю визначну пам’ятку?",
            "options": ["Солоха", "Чортомлик", "Товста Могила", "Гайманова Могила"],
            "labels": ["А", "Б", "В", "Г"],
            "answer": "В",
            "hint": "У 1971 році Борис Мозолевський відкрив золоту пектораль на Дніпропетровщині...",
            "rule": "Золота скіфська пектораль (IV ст. до н. е.) — одна з найчастіших візуальних карток НМТ. Знайдена в 1971 р. Борисом Мозолевським у кургані Товста Могила.",
            "solution": "Правильна відповідь — Товста Могила (В).",
            "drill_key": "hist_dates_20c",
        },
        {
            "id": "hist_2026_2",
            "subject": "history",
            "section": "Від найдавніших часів до першої половини XVI ст.",
            "source": "Офіційний зразок НМТ-2026 (УЦОЯО)",
            "qtype": "single",
            "max_points": 1,
            "prompt": "Прочитайте уривок джерела: «Візантійські та латинські джерела приписують йому похід 941 року й укладення договору 944 року... Про його вбивство древлянами знає й руська \"Повість минулих літ\", а Іларіон згадує його як діда Володимира». Про кого йдеться?",
            "options": ["Аскольда", "Олега", "Ігоря", "Святослава"],
            "labels": ["А", "Б", "В", "Г"],
            "answer": "В",
            "hint": "Походи на Візантію 941 та 944 рр., повстання древлян у 945 р. — це правління чоловіка княгині Ольги.",
            "rule": "Маркери князів Русі: Олег (907, 911 договори), Ігор (941, 944 походи, 945 вбитий древлянами), Святослав (розгром Хозарії, Балкани), Володимир (988 хрещення).",
            "solution": "Походи 941 та 944 рр. і загибель від древлян — це князь Ігор (варіант В).",
            "drill_key": "hist_dates_20c",
        },
        {
            "id": "hist_2026_4",
            "subject": "history",
            "section": "Друга половина XVI–XVIII ст.",
            "source": "Офіційний зразок НМТ-2026 (УЦОЯО)",
            "qtype": "single",
            "max_points": 1,
            "prompt": "Який термін треба використовувати для характеристики фільваркового господарства?",
            "options": ["«панщина»", "«полюддя»", "«зимівник»", "«відруб»"],
            "labels": ["А", "Б", "В", "Г"],
            "answer": "А",
            "hint": "Фільварок — це багатогалузеве шляхетське господарство, що працювало на продаж зерна за рахунок примусової праці селян.",
            "rule": "Фільварок і панщина (відробіткова рента залежних селян) нерозривно пов’язані з XVI–XVIII ст. Полюддя — збирання данини в Русі, зимівник — козацький хутір, відруб — столипінська реформа.",
            "solution": "Основою фільваркового господарства була «панщина» (варіант А).",
            "drill_key": "hist_terms_19c",
        },
        {
            "id": "hist_2026_7",
            "subject": "history",
            "section": "Друга половина XVI–XVIII ст.",
            "source": "Офіційний зразок НМТ-2026 (УЦОЯО)",
            "qtype": "single",
            "max_points": 1,
            "prompt": "Прочитайте уривок: «…незабаром Слідча комісія підтвердила, що деякі чолобитні, надіслані цареві нібито від імені народу, складалися самим наказним гетьманом…». Висновки слідства стали підставою для звинувачення в «злочинних задумах»:",
            "options": ["Івана Самойловича", "Дем’яна Многогрішного", "Івана Мазепи", "Павла Полуботка"],
            "labels": ["А", "Б", "В", "Г"],
            "answer": "Г",
            "hint": "Ідеться про «наказного гетьмана» після створення Першої Малоросійської колегії (1722–1724), автора Коломацьких чолобитних.",
            "rule": "Павло Полуботок (наказний гетьман 1722–1724 рр.) подав Петру I Коломацькі чолобитні з вимогою скасувати Малоросійську колегію й дозволити вибори гетьмана, за що був заарештований у Петропавлівській фортеці.",
            "solution": "Правильна відповідь — Павло Полуботок (варіант Г).",
            "drill_key": "hist_chrono_17c",
        },
        {
            "id": "hist_2026_22",
            "subject": "history",
            "section": "Кінець XVIII – початок XX ст.",
            "source": "Офіційний зразок НМТ-2026 (УЦОЯО)",
            "qtype": "matching",
            "max_points": 4,
            "prompt": "Узгодьте поняття (1–4) з його визначенням (А–Д):",
            "left": ["1. «хлопомани»", "2. «москвофіли»", "3. «народовці»", "4. «радикали»"],
            "right": {
                "А": "течія середини ХІХ ст. на Галичині й Буковині, що виступала за єдність із російським народом",
                "Б": "течія 1870-х рр. на Галичині, що прагнула політизувати український рух і виступила за незалежність",
                "В": "рух молоді з польської шляхти на Правобережжі за зближення із селянами (В. Антонович)",
                "Г": "культурницький рух у Галичині з 1860-х рр. («Просвіта»), що утверджував окремішність українців",
                "Д": "таємне політичне товариство в Наддніпрянщині початку ХХ ст.",
            },
            "answer": {"1": "В", "2": "А", "3": "Г", "4": "Б"},
            "hint": "Розділи за географією та суттю: «хлопомани» — Правобережжя (В. Антонович), «радикали» — політична незалежність (Франко).",
            "rule": "Запам’ятай 4 течії XIX ст.: хлопомани (до селян на Правобережжі), москвофіли (до Росії), народовці (просвітництво, «Просвіта»), радикали (РУРП, програма незалежності).",
            "solution": "1–В, 2–А, 3–Г, 4–Б.",
            "drill_key": "hist_terms_19c",
        },
        {
            "id": "hist_2026_23",
            "subject": "history",
            "section": "Україна в 1914–1945 рр.",
            "source": "Офіційний зразок НМТ-2026 (УЦОЯО)",
            "qtype": "matching",
            "max_points": 4,
            "prompt": "Увідповідніть дату (1–4) та подію (А–Д), коли вона відбулася:",
            "left": ["1. квітень 1918 р.", "2. листопад 1918 р.", "3. квітень 1920 р.", "4. листопад 1921 р."],
            "right": {
                "А": "утворення Директорії – керівного органу антигетьманського повстання",
                "Б": "Другий Зимовий похід Армії УНР",
                "В": "державний переворот і прихід до влади Павла Скоропадського",
                "Г": "підписання Ризького мирного договору",
                "Д": "укладення Варшавської угоди між Польщею й УНР",
            },
            "answer": {"1": "В", "2": "А", "3": "Д", "4": "Б"},
            "hint": "Гетьманат проіснував із квітня по листопад/грудень 1918 року!",
            "rule": "Опорні дати Української революції: 04.1918 — Скоропадський; 11.1918 — Директорія; 04.1920 — Варшавський договір; 11.1921 — Другий Зимовий похід (Базар).",
            "solution": "1–В, 2–А, 3–Д, 4–Б.",
            "drill_key": "hist_dates_20c",
        },
        {
            "id": "hist_2026_24",
            "subject": "history",
            "section": "Україна в 1945 р. – початок XXI ст.",
            "source": "Офіційний зразок НМТ-2026 (УЦОЯО)",
            "qtype": "matching",
            "max_points": 4,
            "prompt": "Узгодьте подію (1–4) з її проявом (А–Д):",
            "left": ["1. Революція на граніті", "2. Помаранчева революція", "3. Революція Гідності", "4. Українська революція"],
            "right": {
                "А": "громадські протести, спричинені відмовою уряду підписати Угоду про асоціацію з ЄС",
                "Б": "масове студентське голодування з вимогами демократичних реформ (1990 р.)",
                "В": "національний рух, що еволюціонував від автономії до проголошення державної незалежності (1917–1921)",
                "Г": "рух громадянської непокори, викликаний масовими фальсифікаціями виборів президента (2004 р.)",
                "Д": "події, у ході яких було остаточно закріплено однопартійну диктатуру",
            },
            "answer": {"1": "Б", "2": "Г", "3": "А", "4": "В"},
            "hint": "Розрізняй 1990 (студенти на граніті), 2004 (вибори) і 2013–2014 (Євроінтеграція / ЄС).",
            "rule": "Три революції новітньої України: 1990 — Революція на граніті (студенти), 2004 — Помаранчева (вибори), 2013–2014 — Гідності (Асоціація з ЄС).",
            "solution": "1–Б, 2–Г, 3–А, 4–В.",
            "drill_key": "hist_dates_20c",
        },
        {
            "id": "hist_2026_25",
            "subject": "history",
            "section": "Друга половина XVI–XVIII ст.",
            "source": "Офіційний зразок НМТ-2026 (УЦОЯО)",
            "qtype": "sequence",
            "max_points": 3,
            "prompt": "Визначте послідовність укладення угод XVII ст. (від найранішої до найпізнішої, запишіть 4 букви без пробілів):",
            "items": {
                "А": "Віленське перемир’я",
                "Б": "Білоцерківський договір",
                "В": "Андрусівське перемир’я",
                "Г": "Зборівський договір",
            },
            "answer": "ГБАВ",
            "hint": "Спочатку дві перемоги/договори Богдана Хмельницького з Річчю Посполитою (1649 і 1651), потім союз Московії з Польщею (1656) і поділ по Дніпру (1667).",
            "rule": "Хронологія договорів XVII ст.: Зборів (1649) → Біла Церква (1651) → Переяслав/Березневі статті (1654) → Вільно (1656) → Гадяч (1658) → Андрусів (1667).",
            "solution": "Г (Зборівський, 1649) → Б (Білоцерківський, 1651) → А (Віленське перемир’я, 1656) → В (Андрусівське перемир’я, 1667). Код: ГБАВ.",
            "drill_key": "hist_chrono_17c",
        },
        {
            "id": "hist_2026_29",
            "subject": "history",
            "section": "Україна в 1914–1945 рр.",
            "source": "Офіційний зразок НМТ-2026 (УЦОЯО)",
            "qtype": "multi3",
            "max_points": 3,
            "prompt": "Визначте три складники політики радянізації західних областей України (1939–1941 рр.):",
            "items": {
                "1": "ліквідація церковного землеволодіння",
                "2": "заохочення приватної торгівлі",
                "3": "колективізація селянських господарств",
                "4": "викуп державою поміщицьких земель",
                "5": "націоналізація промислових підприємств",
                "6": "створення раднаргоспів",
                "7": "запровадження Продовольчої програми",
            },
            "answer": ["1", "3", "5"],
            "hint": "Радянізація (1939–1941) — це перенесення радянської моделі: націоналізація, колективізація, боротьба з церквою. Раднаргоспи — це 1957 (Хрущов), Продовольча програма — 1982 (Брежнєв).",
            "rule": "У завданнях «3 із 7» завжди відсіюй події іншої епохи! Раднаргоспи (1957) і Продовольча програма (1982) стосуються повоєнного часу, а приватну торгівлю СРСР не заохочував.",
            "solution": "Правильні пункти: 1 (ліквідація церковного землеволодіння), 3 (колективізація), 5 (націоналізація підприємств).",
            "drill_key": "hist_dates_20c",
        },
        {
            "id": "hist_2026_30",
            "subject": "history",
            "section": "Україна в 1945 р. – початок XXI ст.",
            "source": "Офіційний зразок НМТ-2026 (УЦОЯО)",
            "qtype": "multi3",
            "max_points": 3,
            "prompt": "Які три події російсько-української війни відбулися протягом 2014 року?",
            "items": {
                "1": "початок Операції об’єднаних сил (ООС)",
                "2": "створення формату мирних переговорів — «нормандської четвірки»",
                "3": "початок Антитерористичної операції (АТО)",
                "4": "окупація Російською Федерацією Кримського півострова",
                "5": "надання Томоса про автокефалію Православній Церкві в Україні",
                "6": "запровадження безвізового режиму з країнами ЄС",
                "7": "початок широкомасштабного вторгнення армії РФ в Україну",
            },
            "answer": ["2", "3", "4"],
            "hint": "Безвіз (2017), ООС (2018), Томос (2019), повномасштабне вторгнення (2022) — вони були пізніше 2014 року!",
            "rule": "Події 2014 року: окупація Криму (лютий–березень), початок АТО (квітень), створення «нормандської четвірки» (червень), Мінськ-1 (вересень).",
            "solution": "У 2014 році відбулися: 2 (створення «нормандської четвірки»), 3 (початок АТО), 4 (окупація Криму).",
            "drill_key": "hist_dates_20c",
        },
    ],
}


"""Банк завдань і генератори: Англійська, Німецька, Французька, Іспанська мови."""

# ============================ АНГЛІЙСЬКА МОВА ==============================

@register_drill("eng_verb_agreement")
def gen_eng_verb_agreement():
    cases = [
        (
            "Most robots have three essential features that _______ them easy to control.",
            ["making", "make", "makes", "is making"],
            "B",
            "Визнач, якого слова стосується 'that': 'features' (множина)!",
            "Після 'that / which / who' в означальному підрядному реченні дієслово узгоджується з іменником перед ним. 'Features' — множина → потрібне дієслово без -s (make).",
            "Підмет перед 'that' — 'three essential features' (множина), отже правильна форма у множині — make (B).",
        ),
        (
            "Every student who participates in the NMT marathon _______ a detailed progress chart.",
            ["receive", "receiving", "receives", "are receiving"],
            "C",
            "Поглянь на головний підмет речення: 'Every student' — це однина чи множина?",
            "Слова 'every', 'each', 'everyone', 'someone' в англійській ЗАВЖДИ вимагають дієслова в однині (+ -s у Present Simple)!",
            "Підмет 'Every student' — однина, тому правильне дієслово — receives (C).",
        ),
        (
            "A collection of rare historical maps _______ displayed in the central museum hall this month.",
            ["are", "were", "is", "have been"],
            "C",
            "Не потрап у пастку зі словом 'maps' перед дієсловом! Хто є головним підметом: 'maps' чи 'A collection'?",
            "У конструкції «A [noun] of [plural nouns]» дієслово узгоджується з ПЕРШИМ словом до 'of' (a collection — одн.), а не зі словом після 'of'!",
            "Головне слово — 'A collection' (одна колекція, одн.), тож потрібно is (C).",
        ),
        (
            "Neither the teacher nor the students _______ ready to finish the discussion early.",
            ["is", "was", "were", "has been"],
            "C",
            "У сполучнику 'neither ... nor ...' дієслово узгоджується з найближчим до нього підметом ('the students').",
            "Правило близькості: у 'neither A nor B' та 'either A or B' форма дієслова залежить від B (того, хто стоїть ближче до дієслова).",
            "Найближчий підмет 'the students' — множина, отже обираємо were (C).",
        ),
    ]
    c = random.choice(cases)
    return {
        "subject": "english",
        "section": "Use of English: Граматика (Task 6)",
        "source": "Генератор за програмою НМТ (2022–2026)",
        "qtype": "single",
        "max_points": 1,
        "prompt": f"Choose the correct answer (A, B, C or D):\n{c[0]}",
        "options": c[1],
        "labels": ["A", "B", "C", "D"],
        "answer": c[2],
        "hint": c[3],
        "rule": c[4],
        "solution": c[5],
        "drill_key": "eng_verb_agreement",
    }


@register_drill("eng_passive_past")
def gen_eng_passive_past():
    cases = [
        (
            "The novel became famous in 1961 and _______ into an award-winning film in 1962.",
            ["is made", "has been made", "was made", "had been made"],
            "C",
            "Є точна дата в минулому ('in 1962'), а сам роман фільм НЕ знімає — його екранізували (пасив).",
            "Якщо вказано конкретний рік або момент у минулому (in 1962, yesterday, two years ago), вживаємо Past Simple. Для пасиву (дія над предметом): was / were + V3.",
            "Точний рік у минулому (1962) + пасивна дія → Past Simple Passive: was made (C).",
        ),
        (
            "The first electric tram line in Kyiv _______ in 1892, transforming urban transport.",
            ["opens", "was opened", "has been opened", "is opened"],
            "B",
            "Лінія трамвая сама себе не відкривала (пасив), і вказано точний 1892 рік.",
            "Конкретний рік у минулому завжди скасовує Present Perfect ('has been') і вимагає Past Simple Passive ('was/were + V3').",
            "У 1892 році → Past Simple Passive: was opened (B).",
        ),
        (
            "Nowadays, thousands of tonnes of plastic bottles _______ every week to reduce pollution.",
            ["recycle", "are recycled", "recycled", "were recycling"],
            "B",
            "Маркер 'nowadays / every week' — теперішній регулярний час, а пляшки самі себе не переробляють.",
            "Регулярна дія в теперішньому часі (Present Simple) + об’єкт зазнає дії → am / is / are + V3.",
            "У множині в Present Simple Passive: are recycled (B).",
        ),
        (
            "By the time the rescue team arrived, all the hikers _______ safely from the mountain.",
            ["were evacuated", "have been evacuated", "had been evacuated", "are evacuated"],
            "C",
            "Маркер 'By the time + Past Simple' означає дію, завершену ДО іншого моменту в минулому.",
            "Передминулий час (дія завершилася раніше за іншу подію в минулому, маркер 'by the time') у пасиві: had been + V3.",
            "Евакуація закінчилася до прибуття команди → Past Perfect Passive: had been evacuated (C).",
        ),
    ]
    c = random.choice(cases)
    return {
        "subject": "english",
        "section": "Use of English: Граматика (Task 6)",
        "source": "Генератор за програмою НМТ (2022–2026)",
        "qtype": "single",
        "max_points": 1,
        "prompt": f"Choose the correct answer (A, B, C or D):\n{c[0]}",
        "options": c[1],
        "labels": ["A", "B", "C", "D"],
        "answer": c[2],
        "hint": c[3],
        "rule": c[4],
        "solution": c[5],
        "drill_key": "eng_passive_past",
    }


@register_drill("eng_connectors_whether")
def gen_eng_connectors_whether():
    cases = [
        (
            "_______ you study in the morning or late at night, regular practice is the key to success.",
            ["When", "Why", "While", "Whether"],
            "D",
            "Подивись на слово 'or' у другій частині речення! Яке слово завжди утворює пару '... or ...'?",
            "Зв’язка 'Whether ... or (not)' перекладається «незалежно від того, ... чи (ні)». Ні 'When', ні 'While' із 'or not / or' так не працюють.",
            "Є парний сполучник 'or' — правильний вибір Whether (D).",
        ),
        (
            "Some learners prefer paper flashcards, _______ others revise vocabulary using mobile apps.",
            ["therefore", "whereas", "whether", "since"],
            "B",
            "Дві частини протиставляються (одні надають перевагу паперовим карткам, тоді як інші — застосункам).",
            "'Whereas' = «тоді як / у той час як» (протиставлення). 'Therefore' = «тому», 'since' = «оскільки / відтоді як».",
            "Протиставлення двох груп → whereas (B).",
        ),
        (
            "_______ the heavy rain, the outdoor charity concert attracted hundreds of visitors.",
            ["Although", "Despite", "However", "Because"],
            "B",
            "Після пропуску стоїть іменник ('the heavy rain'), а не ціле речення (підмет + присудок)!",
            "Запам’ятай пастку НМТ: 'Although' вимагає (підмет + дієслово), а 'Despite / In spite of' вимагають іменника або V-ing! 'Despite the rain', але 'Although it rained'.",
            "Після пропуску іменна група 'the heavy rain' → Despite (B).",
        ),
        (
            "You should save a copy of your essay _______ your laptop unexpectedly turns off.",
            ["in case", "unless", "although", "provided"],
            "A",
            "Навіщо ми зберігаємо копію? На той випадок, якщо ноутбук вимкнеться.",
            "'In case' = «на випадок якщо» (дія заздалегідь для підстраховки). 'Unless' = «якщо не».",
            "Дія про всяк випадок → in case (A).",
        ),
    ]
    c = random.choice(cases)
    return {
        "subject": "english",
        "section": "Use of English: Граматика (Task 6)",
        "source": "Генератор за програмою НМТ (2022–2026)",
        "qtype": "single",
        "max_points": 1,
        "prompt": f"Choose the correct answer (A, B, C or D):\n{c[0]}",
        "options": c[1],
        "labels": ["A", "B", "C", "D"],
        "answer": c[2],
        "hint": c[3],
        "rule": c[4],
        "solution": c[5],
        "drill_key": "eng_connectors_whether",
    }


@register_drill("eng_vocab_context")
def gen_eng_vocab_context():
    cases = [
        (
            "_______ spending hours scrolling social media, Maya decided to learn Spanish.",
            ["Except for", "Instead of", "Owing to", "Aside from"],
            "B",
            "Вона не сиділа в соцмережах, а вирішила натомість вивчати іспанську.",
            "'Instead of' + V-ing = «замість того щоб». 'Owing to' = «завдяки / через», 'except for' = «за винятком».",
            "Значення «замість цього» → Instead of (B).",
        ),
        (
            "Upon _______ the familiar melody, the lost dog immediately ran toward its owner.",
            ["hearing", "listening", "observing", "picking"],
            "A",
            "Собака почув звук (мимоволі) — і зверни увагу, що після пропуску НЕМАЄ прийменника 'to'!",
            "Головна відмінність на НМТ: 'listen TO' (вимагає 'to', прислухатися), а 'hear' (почути, без 'to').",
            "Немає прийменника 'to' + значення «почути» → hearing (A).",
        ),
        (
            "The museum hopes to give the ancient manuscript _______ life by digitising all its pages.",
            ["further", "the further", "farther", "the farthest"],
            "A",
            "Йдеться про переносне значення («подальше, нове життя»), а не про фізичну відстань, і без артикля 'the'.",
            "'Farther' — лише про фізичну відстань (кілометри). 'Further' — переносне значення («подальший, додатковий»): further information, further life.",
            "У значенні «подальший» без артикля перед незлічуваним/абстрактним поняттям → further (A).",
        ),
        (
            "Before signing the contract, the lawyer carefully _______ every paragraph of the document.",
            ["looked through", "looked about", "looked down", "looked out"],
            "A",
            "Юрист уважно переглянув кожен абзац.",
            "Фразові дієслова з LOOK: look through (переглянути текст/документ), look for (шукати), look after (доглядати), look out (стерегтися).",
            "Переглянути документ → looked through (A).",
        ),
    ]
    c = random.choice(cases)
    return {
        "subject": "english",
        "section": "Use of English: Лексика (Task 5)",
        "source": "Генератор за програмою НМТ (2022–2026)",
        "qtype": "single",
        "max_points": 1,
        "prompt": f"Choose the correct answer (A, B, C or D):\n{c[0]}",
        "options": c[1],
        "labels": ["A", "B", "C", "D"],
        "answer": c[2],
        "hint": c[3],
        "rule": c[4],
        "solution": c[5],
        "drill_key": "eng_vocab_context",
    }


@register_drill("eng_reading_ads")
def gen_eng_reading_ads():
    pool = [
        (
            "GREEN CITY BIKE RENTAL: Explore downtown parks and historic streets on an electric bike! Daily and weekly passes available online.",
            ["eating out", "hiring a vehicle", "shopping opportunities", "a job offer"],
            "B",
            "Ключові слова: 'Bike Rental', 'daily and weekly passes'. Bike — це транспортний засіб (vehicle), rental = hiring.",
            "У Task 1 (Reading) правильна відповідь майже завжди є перефразуванням: rent a bike = hire a vehicle.",
            "Оренда велосипедів = hiring a vehicle (B).",
        ),
        (
            "SUNRISE BAKERY IS HIRING! Friendly baristas and weekend cashiers wanted. $15/hour + tips. Send your CV to jobs@sunrise.org.",
            ["eating out", "an educational institution", "a job offer", "medical services"],
            "C",
            "Слова 'is hiring', '$15/hour', 'Send your CV' вказують на вакансію.",
            "Не плутай рекламу кав’ярні з вакансією в кав’ярні! Якщо вказані зарплата й резюме (CV/resume), це 'a job offer'.",
            "Пошук працівників і прийом резюме = a job offer (C).",
        ),
        (
            "CLEAR VISION CLINIC: Comprehensive eye exams, glasses fitting, and laser consultation with experienced doctors. Book your appointment today.",
            ["shopping opportunities", "a holiday party", "a visit to the theatre", "medical services"],
            "D",
            "Ключові слова: 'Clinic', 'eye exams', 'doctors', 'appointment'.",
            "Слова clinic, care, health, doctors, appointment однозначно вказують на medical services.",
            "Обстеження в лікарів у клініці = medical services (D).",
        ),
        (
            "OAKWOOD PERFORMING ARTS SCHOOL: Grades 7–12 college prep with theatre, music, and visual arts. Admissions deadline: Feb 1.",
            ["an educational institution", "a visit to the theatre", "a job offer", "eating out"],
            "A",
            "Обережно, пастка! Слово 'theatre' тут лише частина шкільної програми ('Grades 7–12', 'Admissions').",
            "Класична пастка НМТ: у тексті про школу мистецтв є слово 'theatre', але сам текст про вступ до школи (Grades 7–12, Admissions) → 'an educational institution'.",
            "Школа з набором учнів (admissions) = an educational institution (A).",
        ),
    ]
    c = random.choice(pool)
    return {
        "subject": "english",
        "section": "Reading: Загальне розуміння (Task 1)",
        "source": "Генератор за програмою НМТ (2022–2026)",
        "qtype": "single",
        "max_points": 1,
        "prompt": f"Read the advertisement. Which topic matches it?\n\n«{c[0]}»\n\nThis advertisement is about _______.",
        "options": c[1],
        "labels": ["A", "B", "C", "D"],
        "answer": c[2],
        "hint": c[3],
        "rule": c[4],
        "solution": c[5],
        "drill_key": "eng_reading_ads",
    }


# ============================ НІМЕЦЬКА МОВА ===============================

@register_drill("ger_gram_context")
def gen_ger_gram_context():
    cases = [
        (
            "_______ das Programm zu benutzen, muss man kein Informatik-Experte sein.",
            ["ohne", "damit", "statt", "um"],
            "D",
            "Подивись у кінець частини речення: стоїть '... zu benutzen'. Яка конструкція з інфінітивом перекладається «щоб»?",
            "Конструкція 'um ... zu + Infinitiv' виражає мету («щоб...»). Сполучник 'damit' теж перекладається «щоб», але вимагає ПОВНОГО речення з дієсловом у кінці без 'zu'!",
            "Є частка 'zu' перед інфінітивом і значення мети («щоб користуватися програмою») → um (D).",
        ),
        (
            "Mit der neuen Software _______ schon das alte Wörterbuch erfolgreich digitalisiert.",
            ["wurde", "werde", "wurdet", "werdet"],
            "A",
            "Словник сам себе не оцифровував — це пасив у минулому часі (Präteritum Passiv) для 'das Wörterbuch' (3-тя особа одн.).",
            "Präteritum Passiv утворюється за допомогою 'wurde / wurden + Partizip II'. Для однини (es/das Wörterbuch) завжди 'wurde'.",
            "Однина (das Wörterbuch) у минулому пасиві → wurde (A).",
        ),
        (
            "Das Programm scannt historische Texte, _______ der Computer danach lesen kann.",
            ["der", "des", "dem", "den"],
            "D",
            "Відносний займенник стосується 'Text' (чоловічий рід, der Text), але в підрядному він є додатком: комп’ютер читає (кого? що? — Akkusativ!).",
            "В означальному підрядному рід і число займенника беремо від слова перед комою (der Text → чол. р., одн.), а відмінок — від дієслова всередині підрядного (lesen + Akkusativ → den).",
            "Чоловічий рід, Akkusativ (що? текст) → den (D).",
        ),
        (
            "Es ist wichtig, dass _______ als fünf Prozent der Antworten falsch sind.",
            ["wenig", "wenige", "weniger", "wenigen"],
            "C",
            "Бачиш слово 'als' (ніж) після пропуску? Це маркер вищого ступеня порівняння!",
            "Перед сполучником порівняння 'als' («ніж») завжди стоїть вищий ступінь порівняння (Komparativ): менше ніж = weniger als.",
            "Порівняння 'als' вимагає вищого ступеня → weniger (C).",
        ),
    ]
    c = random.choice(cases)
    return {
        "subject": "german",
        "section": "Grammatik: Граматика в контексті",
        "source": "Генератор за програмою НМТ (2022–2026)",
        "qtype": "single",
        "max_points": 1,
        "prompt": f"Wählen Sie die richtige Variante (A, B, C oder D):\n{c[0]}",
        "options": c[1],
        "labels": ["A", "B", "C", "D"],
        "answer": c[2],
        "hint": c[3],
        "rule": c[4],
        "solution": c[5],
        "drill_key": "ger_gram_context",
    }


# ============================ ФРАНЦУЗЬКА МОВА =============================

@register_drill("fr_gram_context")
def gen_fr_gram_context():
    cases = [
        (
            "— Qui a mangé le pain ?\n— J’ai pris _______ pain et de la confiture.",
            ["du", "de la", "de", "d’un"],
            "A",
            "Слово 'pain' — чоловічого роду (le pain), стверджувальне речення, незлічувана кількість («трохи хліба»).",
            "Частковий артикль у французькій: de + le = du (чол. р.), de la (жін. р.), de l' (перед голосною). У запереченні змінюється просто на 'de'.",
            "Чоловічий рід, стверджувальне речення → du (A).",
        ),
        (
            "Je ne sais pas si elle viendra. Mais si je la _______ chez André, j’enverrai un message.",
            ["verrai", "verrais", "vois", "vis"],
            "C",
            "У другій частині стоїть майбутній час ('j'enverrai'). Який час ЗАВЖДИ ставиться в умові після 'si' (якщо), коли результат у майбутньому?",
            "Золоте правило НМТ із французької: після умовного 'si' НІКОЛИ не ставиться Futur simple чи Conditionnel! Для 1-го типу умови: Si + Présent → Futur simple.",
            "Після умовного 'si' (якщо) за майбутнього результату потрібен теперішній час (Présent) → vois (C).",
        ),
        (
            "Tous les enfants ont le même âge. Cependant, _______ élèves ont plus de difficultés que d’autres.",
            ["aucun", "autres", "certains", "tous les"],
            "C",
            "Є протиставлення '... ont plus de difficultés que d’autres' («ніж інші»). Тобто «деякі учні».",
            "'Certains' (деякі) + іменник у множині без артикля узгоджується з дієсловом у множині ('ont'). 'Aucun' вимагає 'ne' та однини.",
            "За змістом та узгодженням у множині ('ont') підходить certains (C).",
        ),
        (
            "Tous les vacanciers n’empruntent pas le même transport. Généralement, _______ n’est pressé de rentrer.",
            ["aucun", "certains", "chacun", "quelqu’un"],
            "A",
            "Подивись на заперечення 'n’est pressé' (ніхто не поспішає)!",
            "У заперечному реченні з 'ne' для значення «жоден / ніхто (з них)» вживається 'aucun'. 'Chacun' і 'quelqu'un' не поєднуються з таким запереченням.",
            "Із часткою 'n’' та одниною 'est' → aucun (A).",
        ),
    ]
    c = random.choice(cases)
    return {
        "subject": "french",
        "section": "Grammaire: Граматика в контексті",
        "source": "Генератор за програмою НМТ (2022–2026)",
        "qtype": "single",
        "max_points": 1,
        "prompt": f"Choisissez la bonne réponse (A, B, C ou D) :\n{c[0]}",
        "options": c[1],
        "labels": ["A", "B", "C", "D"],
        "answer": c[2],
        "hint": c[3],
        "rule": c[4],
        "solution": c[5],
        "drill_key": "fr_gram_context",
    }


# ============================= ІСПАНСЬКА МОВА =============================

@register_drill("esp_gram_context")
def gen_esp_gram_context():
    cases = [
        (
            "El museo _______ abierto todos los días de martes a domingo.",
            ["es", "está", "son", "están"],
            "B",
            "Відчинено/зачинено — це тимчасовий стан або результат дії, а не постійна властивість.",
            "Відмінність SER vs ESTAR: із дієприкметниками стану (abierto, cerrado, cansado, ocupado) завжди вживається ESTAR.",
            "Однина ('el museo') + стан ('abierto') → está (B).",
        ),
        (
            "Muchas gracias _______ tu ayuda con los ejercicios de matemáticas.",
            ["para", "por", "de", "en"],
            "B",
            "Подяка за щось (причина подяки) — який прийменник обирається в іспанській?",
            "POR vs PARA: POR виражає причину, обмін, подяку (gracias por..., pagar por...). PARA — мету, адресата, дедлайн.",
            "Причина подяки ('gracias ...') завжди вимагає прийменник por (B).",
        ),
        (
            "Ayer por la tarde mis amigos y yo _______ al cine del centro.",
            ["vamos", "íbamos", "fuimos", "hemos ido"],
            "C",
            "Показник 'Ayer' (учора) — завершена одноразова дія в минулому.",
            "З точним маркером завершеного минулого (ayer, el año pasado, en 2024) вживається Pretérito Indefinido (fuimos), а не Imperfecto чи Pretérito Perfecto.",
            "Одноразова дія вчора → fuimos (C).",
        ),
        (
            "Espero que _______ buen tiempo durante nuestro viaje a las montañas.",
            ["hace", "haga", "hará", "hizo"],
            "B",
            "Дієслово сподівання/бажання ('Espero que...') вимагає умовного способу (Subjuntivo)!",
            "Після дієслів бажання, сподівання та емоцій (espero que, quiero que, me alegra que) ставиться Presente de Subjuntivo. Для hacer → haga.",
            "Після 'Espero que' потрібне Subjuntivo від hacer → haga (B).",
        ),
    ]
    c = random.choice(cases)
    return {
        "subject": "spanish",
        "section": "Gramática: Граматика в контексті",
        "source": "Генератор за програмою НМТ (2022–2026)",
        "qtype": "single",
        "max_points": 1,
        "prompt": f"Elige la opción correcta (A, B, C o D):\n{c[0]}",
        "options": c[1],
        "labels": ["A", "B", "C", "D"],
        "answer": c[2],
        "hint": c[3],
        "rule": c[4],
        "solution": c[5],
        "drill_key": "esp_gram_context",
    }


# ---------------------------------------------------------------------------
# СТАТИЧНІ ОФІЦІЙНІ ЗАВДАННЯ НМТ-2026 З ІНОЗЕМНИХ МОВ
# ---------------------------------------------------------------------------
STATIC_LANG_QUESTIONS = {
    "english": [
        {
            "id": "eng_2026_demo_1",
            "subject": "english",
            "section": "Reading: Загальне розуміння (Task 1)",
            "source": "Офіційний демоваріант НМТ-2026 (УЦОЯО)",
            "qtype": "single",
            "max_points": 1,
            "prompt": (
                "Read the advertisement:\n"
                "«VALLEY BIKE: Explore Pioneer Valley on a ValleyBike. Enjoy the ride in eight cities "
                "and towns. Register today at www.ValleyBike.org.»\n\n"
                "Which advertisement is about _______?"
            ),
            "options": ["eating out", "hiring a vehicle", "shopping opportunities", "a job offer"],
            "labels": ["A", "B", "C", "D"],
            "answer": "B",
            "hint": "Bike — транспортний засіб (vehicle), а реєстрація для поїздок містами — це прокат.",
            "rule": "У Task 1 шукай синоніми: bike sharing / rental = hiring a vehicle.",
            "solution": "Велопрокат ValleyBike — це прокат транспортного засобу: hiring a vehicle (B).",
            "drill_key": "eng_reading_ads",
        },
        {
            "id": "eng_2026_demo_4",
            "subject": "english",
            "section": "Reading: Загальне розуміння (Task 1)",
            "source": "Офіційний демоваріант НМТ-2026 (УЦОЯО)",
            "qtype": "single",
            "max_points": 1,
            "prompt": (
                "Read the advertisement:\n"
                "«PVPA Charter Public School — Grades 7–12 College Prep. Arts-Focused Curriculum featuring: "
                "Theatre, Music, Dance, Film, Visual Arts. Apply @ www.pvpa.org/admissions.»\n\n"
                "Which advertisement is about _______?"
            ),
            "options": ["a holiday party", "an educational institution", "medical services", "a visit to the theatre"],
            "labels": ["A", "B", "C", "D"],
            "answer": "B",
            "hint": "Зверни увагу на 'Grades 7–12 College Prep' та 'admissions' — це не похід до театру!",
            "rule": "Слова 'theatre' або 'film' в оголошенні про школу — відволікальна приманка. Головний зміст — навчання і прийом учнів.",
            "solution": "Йдеться про школу (Charter Public School, Grades 7–12) → an educational institution (B).",
            "drill_key": "eng_reading_ads",
        },
        {
            "id": "eng_2026_s1_6",
            "subject": "english",
            "section": "Reading: Детальне розуміння (Task 2)",
            "source": "Офіційний зразок НМТ-2026, 1 сесія (УЦОЯО / Освіта.UA)",
            "qtype": "single",
            "max_points": 1,
            "prompt": (
                "Read the paragraph:\n"
                "«Visit virtually any city these days, and no matter where in the world it is, you'll surely "
                "find its own public bike rental scheme. China, for example, has about 60 of its own, while "
                "many of the European cycling countries, like Denmark, France, Germany, and the Netherlands "
                "have also successfully introduced bike sharing in their cities. Perhaps what has made these "
                "schemes so popular is their accessibility. You can hire bikes in all shapes and sizes.»\n\n"
                "What is stated in PARAGRAPH 1?"
            ),
            "options": [
                "You can go on a virtual bike tour in any city.",
                "Bike-sharing programmes are taking over the world.",
                "European countries have identical rental schemes.",
                "Bike sharing has reached its peak accessibility.",
            ],
            "labels": ["A", "B", "C", "D"],
            "answer": "B",
            "hint": "Зверни увагу на пастку зі схожими словами: 'virtually any city' (майже будь-яке місто) ≠ 'virtual bike tour'!",
            "rule": "У Task 2 дистрактори часто беруть слово з тексту ('virtually', 'accessibility') і спотворюють зміст. Слово 'virtually' означає 'almost / practically', а не 'віртуальний'!",
            "solution": "'Visit virtually any city... no matter where in the world' = велопрокат поширюється по всьому світу → B.",
            "drill_key": "eng_reading_ads",
        },
        {
            "id": "eng_2026_s1_26",
            "subject": "english",
            "section": "Use of English: Лексика (Task 5)",
            "source": "Офіційний демоваріант / 1 сесія НМТ-2026 (УЦОЯО)",
            "qtype": "single",
            "max_points": 1,
            "prompt": (
                "Choose the correct word for gap (26):\n"
                "«To the astonishment of the police, upon (26) _______ the tune, the husky began 'singing'.»"
            ),
            "options": ["hearing", "listening", "observing", "picking"],
            "labels": ["A", "B", "C", "D"],
            "answer": "A",
            "hint": "Після 'listen' завжди потрібен прийменник 'to' (listening to the tune), а його тут немає.",
            "rule": "Дієслово 'hear' вживається без прийменника (hear a sound/tune), а 'listen' вимагає прийменник 'to'.",
            "solution": "Без прийменника 'to' граматично й за змістом підходить hearing (A).",
            "drill_key": "eng_vocab_context",
        },
        {
            "id": "eng_2026_s1_27",
            "subject": "english",
            "section": "Use of English: Лексика (Task 5)",
            "source": "Офіційний демоваріант / 1 сесія НМТ-2026 (УЦОЯО)",
            "qtype": "single",
            "max_points": 1,
            "prompt": (
                "Choose the correct word for gap (27):\n"
                "«The owner, who was listening on the phone, (27) _______ the dog’s voice and rushed over.»"
            ),
            "options": ["remembered", "approved", "realised", "recognised"],
            "labels": ["A", "B", "C", "D"],
            "answer": "D",
            "hint": "Господар телефоном саме «упізнав» голос свого собаки.",
            "rule": "'Recognise' = упізнати (голос, обличчя, місце). 'Realise' = усвідомити (факт/ситуацію), 'remember' = пам’ятати.",
            "solution": "Упізнати голос собаки телефоном — recognised (D).",
            "drill_key": "eng_vocab_context",
        },
        {
            "id": "eng_2026_demo_28",
            "subject": "english",
            "section": "Use of English: Граматика (Task 6)",
            "source": "Офіційний демоваріант НМТ-2026 (УЦОЯО)",
            "qtype": "single",
            "max_points": 1,
            "prompt": (
                "Choose the correct word for gap (28):\n"
                "«A robot is a machine that can move around and respond to (28) _______ surroundings.»"
            ),
            "options": ["their", "its", "his", "her"],
            "labels": ["A", "B", "C", "D"],
            "answer": "B",
            "hint": "'A robot' — однина, неістота.",
            "rule": "Для одного предмета/машини/тварини в середньому роді присвійний займенник — 'its' (без апострофа!).",
            "solution": "'A robot' (it) → присвійний its (B).",
            "drill_key": "eng_verb_agreement",
        },
        {
            "id": "eng_2026_demo_31",
            "subject": "english",
            "section": "Use of English: Граматика (Task 6)",
            "source": "Офіційний демоваріант НМТ-2026 (УЦОЯО)",
            "qtype": "single",
            "max_points": 1,
            "prompt": (
                "Choose the correct word for gap (31):\n"
                "«(31) _______ they look like us or not, most robots have three essential ingredients.»"
            ),
            "options": ["When", "Why", "While", "Whether"],
            "labels": ["A", "B", "C", "D"],
            "answer": "D",
            "hint": "Зверни увагу на '... or not' наприкінці першої частини!",
            "rule": "Конструкція 'Whether ... or not' означає «незалежно від того, ... чи ні».",
            "solution": "Із 'or not' поєднується лише Whether (D).",
            "drill_key": "eng_connectors_whether",
        },
        {
            "id": "eng_2026_demo_32",
            "subject": "english",
            "section": "Use of English: Граматика (Task 6)",
            "source": "Офіційний демоваріант НМТ-2026 (УЦОЯО)",
            "qtype": "single",
            "max_points": 1,
            "prompt": (
                "Choose the correct word for gap (32):\n"
                "«...most robots have three essential ingredients that (32) _______ them a robot: sensors, actuators, and programs.»"
            ),
            "options": ["making", "make", "makes", "is making"],
            "labels": ["A", "B", "C", "D"],
            "answer": "B",
            "hint": "Слово 'that' замінює 'three essential ingredients' (множина).",
            "rule": "Узгодження дієслова з іменником перед 'that': ingredients (множина) → make (без -s).",
            "solution": "Підмет 'ingredients' у множині, теперішній час факт → make (B).",
            "drill_key": "eng_verb_agreement",
        },
        {
            "id": "eng_2026_zvit_31",
            "subject": "english",
            "section": "Use of English: Граматика (Task 6)",
            "source": "Офіційний звіт НМТ-2026, Том ІІ (УЦОЯО)",
            "qtype": "single",
            "max_points": 1,
            "prompt": (
                "Choose the correct answer for gap (31):\n"
                "«Harper Lee's novel won the Pulitzer Prize in 1961 and (31) _______ into an Academy Award-winning film in 1962.»"
            ),
            "options": ["is made", "has been made", "was made", "had been made"],
            "labels": ["A", "B", "C", "D"],
            "answer": "C",
            "hint": "Вказано точний рік у минулому ('in 1962'), а книга не сама себе екранізувала.",
            "rule": "Точний рік у минулому (in 1962) + пасивний стан → Past Simple Passive (was made).",
            "solution": "У 1962 році роман був екранізований → was made (C).",
            "drill_key": "eng_passive_past",
        },
        {
            "id": "eng_2026_zvit_32",
            "subject": "english",
            "section": "Use of English: Граматика (Task 6)",
            "source": "Офіційний звіт НМТ-2026, Том ІІ (УЦОЯО)",
            "qtype": "single",
            "max_points": 1,
            "prompt": (
                "Choose the correct answer for gap (32):\n"
                "«...giving the story and its characters (32) _______ life and influence over the American social sphere.»"
            ),
            "options": ["further", "the further", "farther", "the farthest"],
            "labels": ["A", "B", "C", "D"],
            "answer": "A",
            "hint": "Тут переносне значення («подальше життя»), не відстань у метрах!",
            "rule": "'Further' = подальший/додатковий (абстрактно), 'farther' = далі за відстанню. Слово 'life' тут без 'the'.",
            "solution": "Правильний варіант — further (A).",
            "drill_key": "eng_vocab_context",
        },
    ],
    "german": [
        {
            "id": "ger_2026_28",
            "subject": "german",
            "section": "Grammatik: Граматика в контексті",
            "source": "Офіційний звіт НМТ-2026, Том ІІ (УЦОЯО)",
            "qtype": "single",
            "max_points": 1,
            "prompt": (
                "Lesen Sie den Text «Historische Dokumente» und ergänzen Sie die Lücke (28):\n"
                "«(28) _______ kann man historische Dokumente scannen und zu einem Text machen...»"
            ),
            "options": ["dabei", "dazu", "damit", "davon"],
            "labels": ["A", "B", "C", "D"],
            "answer": "C",
            "hint": "Мається на увазі «за допомогою цього (інструмента / програми) можна сканувати документи».",
            "rule": "'Damit' на початку речення (як займенниковий прислівник) означає «за допомогою цього / цим» (mit + der Software = damit).",
            "solution": "Інструментальне значення («за її допомогою») → damit (C).",
            "drill_key": "ger_gram_context",
        },
        {
            "id": "ger_2026_29",
            "subject": "german",
            "section": "Grammatik: Граматика в контексті",
            "source": "Офіційний звіт НМТ-2026, Том ІІ (УЦОЯО)",
            "qtype": "single",
            "max_points": 1,
            "prompt": (
                "Ergänzen Sie die Lücke (29):\n"
                "«...zu einem Text machen, (29) _______ der Computer dann lesen kann.»"
            ),
            "options": ["der", "des", "dem", "den"],
            "labels": ["A", "B", "C", "D"],
            "answer": "D",
            "hint": "'Der Text' — чоловічий рід, але в підрядному 'der Computer' уже підмет (Nominativ), а текст комп’ютер читає (кого? що? — Akkusativ).",
            "rule": "У відносному підрядному рід беремо від 'der Text', а відмінок — від дієслова 'lesen' (Akkusativ) → den.",
            "solution": "Чоловічий рід Akkusativ → den (D).",
            "drill_key": "ger_gram_context",
        },
        {
            "id": "ger_2026_30",
            "subject": "german",
            "section": "Grammatik: Граматика в контексті",
            "source": "Офіційний звіт НМТ-2026, Том ІІ (УЦОЯО)",
            "qtype": "single",
            "max_points": 1,
            "prompt": (
                "Ergänzen Sie die Lücke (30):\n"
                "«(30) _______ als ein Prozent der Buchstaben sind am Ende falsch.»"
            ),
            "options": ["wenig", "wenige", "weniger", "wenigen"],
            "labels": ["A", "B", "C", "D"],
            "answer": "C",
            "hint": "Після пропуску стоїть сполучник порівняння 'als' («ніж»).",
            "rule": "Порівняльна конструкція «менше ніж» у німецькій — завжди 'weniger als'.",
            "solution": "Вищий ступінь порівняння з 'als' → weniger (C).",
            "drill_key": "ger_gram_context",
        },
        {
            "id": "ger_2026_31",
            "subject": "german",
            "section": "Grammatik: Граматика в контексті",
            "source": "Офіційний звіт НМТ-2026, Том ІІ (УЦОЯО)",
            "qtype": "single",
            "max_points": 1,
            "prompt": (
                "Ergänzen Sie die Lücke (31):\n"
                "«(31) _______ das Programm zu benutzen, muss man kein Informatik-Experte sein.»"
            ),
            "options": ["ohne", "damit", "statt", "um"],
            "labels": ["A", "B", "C", "D"],
            "answer": "D",
            "hint": "Наприкінці інфінітивного звороту стоїть '... zu benutzen', а за змістом — «для того щоб користуватися програмою».",
            "rule": "'Um ... zu + Infinitiv' виражає мету («щоб»). 'Ohne ... zu' = не роблячи чогось, 'statt ... zu' = замість того щоб.",
            "solution": "Значення мети + 'zu benutzen' → um (D).",
            "drill_key": "ger_gram_context",
        },
        {
            "id": "ger_2026_32",
            "subject": "german",
            "section": "Grammatik: Граматика в контексті",
            "source": "Офіційний звіт НМТ-2026, Том ІІ (УЦОЯО)",
            "qtype": "single",
            "max_points": 1,
            "prompt": (
                "Ergänzen Sie die Lücke (32):\n"
                "«Mit der Software (32) _______ schon das Wörterbuch der deutschen Sprache (1859–1865) digitalisiert.»"
            ),
            "options": ["wurde", "werde", "wurdet", "werdet"],
            "labels": ["A", "B", "C", "D"],
            "answer": "A",
            "hint": "'Schon ... digitalisiert' — дія вже відбулася в минулому, 'das Wörterbuch' — 3-тя особа одн.",
            "rule": "Präteritum Passiv (3-тя особа одн.): wurde + Partizip II.",
            "solution": "Однина в минулому пасиві → wurde (A).",
            "drill_key": "ger_gram_context",
        },
    ],
    "french": [
        {
            "id": "fr_2026_28",
            "subject": "french",
            "section": "Grammaire: Граматика в контексті",
            "source": "Офіційний звіт НМТ-2026, Том ІІ (УЦОЯО)",
            "qtype": "single",
            "max_points": 1,
            "prompt": (
                "Complétez la phrase :\n"
                "«Vous savez, tous les enfants de ma classe ont le même âge. Cependant, _______ élèves ont plus de difficultés que d’autres pour apprendre à lire et à écrire.»"
            ),
            "options": ["aucun", "autres", "certains", "tous les"],
            "labels": ["A", "B", "C", "D"],
            "answer": "C",
            "hint": "Протиставлення «однак деякі учні мають більше труднощів, ніж інші».",
            "rule": "'Certains + іменник у мн.' (без артикля) = «деякі». 'Autres' вимагало б 'd'autres'.",
            "solution": "Правильний варіант — certains (C).",
            "drill_key": "fr_gram_context",
        },
        {
            "id": "fr_2026_29",
            "subject": "french",
            "section": "Grammaire: Граматика в контексті",
            "source": "Офіційний звіт НМТ-2026, Том ІІ (УЦОЯО)",
            "qtype": "single",
            "max_points": 1,
            "prompt": (
                "Complétez le dialogue :\n"
                "— Qui a mangé le pain ?\n"
                "— J’ai pris _______ pain et de la confiture."
            ),
            "options": ["du", "de la", "de", "d’un"],
            "labels": ["A", "B", "C", "D"],
            "answer": "A",
            "hint": "Хліб у французькій — чоловічого роду (le pain). Потрібен частковий артикль.",
            "rule": "Частковий артикль чоловічого роду: de + le = du (у стверджувальному реченні).",
            "solution": "Для чоловічого роду 'pain' → du (A).",
            "drill_key": "fr_gram_context",
        },
        {
            "id": "fr_2026_30",
            "subject": "french",
            "section": "Grammaire: Граматика в контексті",
            "source": "Офіційний звіт НМТ-2026, Том ІІ (УЦОЯО)",
            "qtype": "single",
            "max_points": 1,
            "prompt": (
                "Complétez le dialogue :\n"
                "— Je ne sais pas si elle viendra à la soirée. Mais si je la _______ chez André, j’enverrai un message."
            ),
            "options": ["verrai", "verrais", "vois", "vis"],
            "labels": ["A", "B", "C", "D"],
            "answer": "C",
            "hint": "Після умовного 'si' (якщо) майбутній час (verrai) НЕ ставиться!",
            "rule": "В умовному реченні 1-го типу: Si + Présent → Futur simple.",
            "solution": "У другій частині Futur simple ('j'enverrai'), отже після 'si' потрібне Présent → vois (C).",
            "drill_key": "fr_gram_context",
        },
        {
            "id": "fr_2026_32",
            "subject": "french",
            "section": "Grammaire: Граматика в контексті",
            "source": "Офіційний звіт НМТ-2026, Том ІІ (УЦОЯО)",
            "qtype": "single",
            "max_points": 1,
            "prompt": (
                "Complétez le dialogue :\n"
                "— Je ne vois plus Marguerite dans le bureau. Elle est où ?\n"
                "— Elle n’est plus là. Elle a dit qu’elle en _______ eu par-dessus la tête des caprices de directrice."
            ),
            "options": ["aura", "aurait", "avait", "eut"],
            "labels": ["A", "B", "C", "D"],
            "answer": "C",
            "hint": "Узгодження часів! Головне речення в минулому ('Elle a dit que...'), а дія в підрядному відбулася ще раніше.",
            "rule": "У непрямій мові в минулому ('Elle a dit que') теперішній перетворюється на Imparfait, а минулий (Passé composé) — на Plus-que-parfait (avait eu).",
            "solution": "Plus-que-parfait для узгодження часів у минулому → avait (C).",
            "drill_key": "fr_gram_context",
        },
    ],
    "spanish": [],
}


"""Банк завдань і генератори: Українська література, Біологія, Фізика, Хімія, Географія."""

# =========================== УКРАЇНСЬКА ЛІТЕРАТУРА =========================

@register_drill("lit_pseudonyms")
def gen_lit_pseudonyms():
    pool = [
        ("Микола Хвильовий", "Фітільов"),
        ("Іван Багряний", "Лозов’ягін"),
        ("Остап Вишня", "Губенко"),
        ("Іван Карпенко-Карий", "Тобілевич"),
        ("Олександр Олесь", "Кандиба"),
        ("Леся Українка", "Косач"),
        ("Панас Мирний", "Рудченко"),
        ("Марко Вовчок", "Вілінська"),
    ]
    sample = random.sample(pool, 5)
    target = sample[0]
    opts = [s[1] for s in sample]
    random.shuffle(opts)
    labels = ["А", "Б", "В", "Г", "Д"]
    c_idx = opts.index(target[1])
    return {
        "subject": "ukrlit",
        "section": "Література XX ст.",
        "source": "Генератор за програмою НМТ (2022–2026)",
        "qtype": "single",
        "max_points": 1,
        "prompt": f"Яке справжнє прізвище має український письменник / письменниця {target[0]}?",
        "options": opts,
        "labels": labels,
        "answer": labels[c_idx],
        "hint": "Згадай пари «псевдонім — справжнє прізвище», які щороку трапляються на НМТ.",
        "rule": "Обов’язкові псевдоніми для НМТ: Хвильовий = Фітільов, Багряний = Лозов’ягін, Вишня = Губенко, Карпенко-Карий = Тобілевич, Олесь = Кандиба, Леся Українка = Косач, Панас Мирний = Рудченко.",
        "solution": f"Справжнє прізвище автора ({target[0]}) — {target[1]} ({labels[c_idx]}).",
        "drill_key": "lit_pseudonyms",
    }


@register_drill("lit_genres")
def gen_lit_genres():
    pool = [
        ("«Енеїда» (І. Котляревський)", "поема-бурлеск / травестійна поема"),
        ("«Наталка Полтавка» (І. Котляревський)", "соціально-побутова драма"),
        ("«Чорна рада» (П. Куліш)", "перший український історичний роман (роман-хроніка)"),
        ("«Хіба ревуть воли, як ясла повні?» (Панас Мирний)", "соціально-психологічний роман"),
        ("«Мартин Боруля» (І. Карпенко-Карий)", "трагікомедія"),
        ("«Камінний хрест» (В. Стефаник)", "психологічна новела (студія)"),
        ("«Лісова пісня» (Леся Українка)", "драма-феєрія"),
        ("«Intermezzo» (М. Коцюбинський)", "імпресіоністична новела"),
        ("«Тигролови» (І. Багряний)", "пригодницький роман"),
        ("«Моя автобіографія» (Остап Вишня)", "усмішка"),
    ]
    sample = random.sample(pool, 5)
    target = sample[0]
    opts = [s[1] for s in sample]
    random.shuffle(opts)
    labels = ["А", "Б", "В", "Г", "Д"]
    c_idx = opts.index(target[1])
    return {
        "subject": "ukrlit",
        "section": "Теорія літератури та аналіз текстів",
        "source": "Генератор за програмою НМТ (2022–2026)",
        "qtype": "single",
        "max_points": 1,
        "prompt": f"Визначте жанр твору {target[0]}:",
        "options": opts,
        "labels": labels,
        "answer": labels[c_idx],
        "hint": "Пов’яжи твір із його унікальним жанром (драма-феєрія, трагікомедія, усмішка, новела, перший історичний роман).",
        "rule": "Жанри-візитівки в програмі НМТ: «Лісова пісня» — драма-феєрія; «Мартин Боруля» — трагікомедія; «Чорна рада» — перший історичний роман; «Хіба ревуть воли...» — перший соціально-психологічний роман; Остап Вишня — усмішка.",
        "solution": f"Твір {target[0]} за жанром — {target[1]} ({labels[c_idx]}).",
        "drill_key": "lit_genres",
    }


# ================================ БІОЛОГІЯ =================================

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
        "source": "Генератор за програмою НМТ (2022–2026)",
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
        "source": "Генератор за програмою НМТ (2022–2026)",
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


# ================================= ФІЗИКА ==================================

@register_drill("phys_free_fall")
def gen_phys_free_fall():
    t = random.choice([2, 3, 4, 5, 6])
    h = 5 * t * t
    return {
        "subject": "physics",
        "section": "Механіка",
        "source": "Генератор за програмою НМТ (2022–2026)",
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
        "source": "Генератор за програмою НМТ (2022–2026)",
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
        "source": "Генератор за програмою НМТ (2022–2026)",
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
        "source": "Генератор за програмою НМТ (2022–2026)",
        "qtype": "short",
        "max_points": 2,
        "prompt": (
            f"У герметичний балон об’ємом {_fmt_num(v)} м³ поставили посудину з водою. До насичення пари в балоні "
            f"випарувалася вода масою {_fmt_num(m_evap)} г. Якою була початкова відносна вологість повітря в балоні (у %), "
            f"якщо густина насиченої пари за цієї температури дорівнює {rho_sat} г/м³?"
        ),
        "answer": str(phi0),
        "hint": "Спочатку знайди, скільки грамів пари може поміститися в балоні загалом (m_нас = ρ_нас · V), а потім відніми масу, що випарувалася!",
        "rule": "У стані насичення маса пари m_нас = ρ_нас · V (100 %). Початкова маса пари m₀ = m_нас − m_вип, а φ₀ = (m₀ / m_нас) · 100 %.",
        "solution": (
            f"1) Маса насиченої пари в об’ємі {_fmt_num(v)} м³: m_нас = {rho_sat} · {_fmt_num(v)} = {_fmt_num(rho_sat * v)} г.\n"
            f"2) Спочатку було пари: m₀ = {_fmt_num(rho_sat * v)} − {_fmt_num(m_evap)} = {_fmt_num(rho_sat * v - m_evap)} г.\n"
            f"3) φ₀ = ({_fmt_num(rho_sat * v - m_evap)} / {_fmt_num(rho_sat * v)}) · 100 % = {phi0} %."
        ),
        "drill_key": "phys_humidity",
    }


@register_drill("phys_halflife")
def gen_phys_halflife():
    half_life = random.choice([5700, 1600, 30, 8])
    n_periods = random.choice([2, 3])
    rem_pct = _fmt_num(100 / (2 ** n_periods))
    ans = half_life * n_periods
    return {
        "subject": "physics",
        "section": "Квантова фізика та теорія відносності",
        "source": "Генератор за програмою НМТ (2022–2026)",
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


# ================================= ХІМІЯ ===================================

@register_drill("chem_gas_molar")
def gen_chem_gas_molar():
    n = random.choice([1.5, 2.0, 2.5, 3.0, 4.0])
    molar = random.choice([28, 32, 44, 64, 128])
    v = n * 22.4
    mass = n * molar
    return {
        "subject": "chemistry",
        "section": "Обчислення в хімії",
        "source": "Генератор за програмою НМТ (2022–2026)",
        "qtype": "short",
        "max_points": 2,
        "prompt": f"Маса газу об’ємом {_fmt_num(v)} л (н. у.) дорівнює {_fmt_num(mass)} г. Обчисліть молярну масу (г/моль) цього газу.",
        "answer": str(molar),
        "hint": "Спочатку знайди кількість речовини n = V / Vm (Vm = 22,4 л/моль), а потім M = m / n.",
        "rule": "За нормальних умов 1 моль будь-якого газу займає 22,4 л. Формули: n = V / 22,4 і M = m / n.",
        "solution": f"1) n = {_fmt_num(v)} / 22,4 = {_fmt_num(n)} моль.\n2) M = {_fmt_num(mass)} / {_fmt_num(n)} = {molar} г/моль.",
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
        "source": "Генератор за програмою НМТ (2022–2026)",
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
        "source": "Генератор за програмою НМТ (2022–2026)",
        "qtype": "short",
        "max_points": 2,
        "prompt": f"Обчисліть масу (г) етанолу (M = 46 г/моль), що утвориться внаслідок гідратації етену об’ємом {_fmt_num(v_ethene)} л (н. у.), якщо відносний вихід спирту становить {eta} %.",
        "answer": _fmt_num(mass_pract),
        "hint": "1) Знайди кількість речовини етену n = V / 22,4; 2) стільки ж моль спирту утвориться теоретично (1:1); 3) помнож теоретичну масу на вихід η!",
        "rule": "C₂H₄ + H₂O → C₂H₅OH (коефіцієнти 1:1). Практична маса = m_теор · (вихід % / 100).",
        "solution": (
            f"1) n(C₂H₄) = {_fmt_num(v_ethene)} / 22,4 = {n_ethene} моль = n_теор(C₂H₅OH).\n"
            f"2) m_теор = {n_ethene} · 46 = {n_ethene * 46} г.\n"
            f"3) m_практ = {n_ethene * 46} · {eta/100:.2f} = {_fmt_num(mass_pract)} г."
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
        "source": "Генератор за програмою НМТ (2022–2026)",
        "qtype": "short",
        "max_points": 2,
        "prompt": (
            f"Для повного окиснення алкану кількістю речовини {_fmt_num(n_alk)} моль витратили кисень "
            f"кількістю речовини {_fmt_num(n_o2)} моль. Визначте формулу алкану й зазначте у відповіді "
            f"кількість УСІХ атомів у його молекулі."
        ),
        "answer": str(atoms),
        "hint": "Знайди, скільки моль O₂ потрібно на 1 моль алкану: (3n + 1)/2 = n(O₂)/n(алкану), звідки знайдеш n!",
        "rule": "Загальне рівняння горіння алкану: CₙH₂ₙ₊₂ + ((3n+1)/2) O₂ → n CO₂ + (n+1) H₂O. Кількість усіх атомів у молекулі CₙH₂ₙ₊₂ дорівнює 3n + 2.",
        "solution": (
            f"1) На 1 моль алкану потрібно {_fmt_num(n_o2)} / {_fmt_num(n_alk)} = {_fmt_num(o2_coef)} моль O₂.\n"
            f"2) (3n + 1)/2 = {_fmt_num(o2_coef)} ⇒ 3n + 1 = {3*n_c+1} ⇒ n = {n_c} (C{n_c}H{2*n_c+2}).\n"
            f"3) Усього атомів: {n_c} + {2*n_c+2} = {atoms}."
        ),
        "drill_key": "chem_alkane_combust",
    }


# ================================ ГЕОГРАФІЯ =================================

@register_drill("geo_map_scale")
def gen_geo_map_scale():
    scale_m = random.choice([100, 200, 250, 500])
    scale_denom = scale_m * 100
    d_cm = random.choice([4, 6, 8, 9, 12, 15, 22])
    ans = d_cm * scale_m
    return {
        "subject": "geography",
        "section": "Загальна географія та топографія",
        "source": "Генератор за програмою НМТ (2022–2026)",
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
        "source": "Генератор за програмою НМТ (2022–2026)",
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
        "source": "Генератор за програмою НМТ (2022–2026)",
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


# ---------------------------------------------------------------------------
# ОФІЦІЙНІ СТАТИЧНІ ЗАВДАННЯ 2026 (УЦОЯО) ДЛЯ ЦИХ 5 ПРЕДМЕТІВ
# ---------------------------------------------------------------------------
STATIC_SCI_LIT_QUESTIONS = {
    "ukrlit": [
        {
            "id": "ukrlit_2026_1",
            "subject": "ukrlit",
            "section": "Усна народна творчість",
            "source": "Офіційний зразок НМТ-2026 (УЦОЯО)",
            "qtype": "single",
            "max_points": 1,
            "prompt": "Уривок «Ой на Івана та й на Купала / Там дівчинонька квіти збирала...» взято з:",
            "options": [
                "родинно-побутової пісні",
                "народної думи",
                "суспільно-побутової пісні",
                "народної балади",
                "календарно-обрядової пісні",
            ],
            "labels": ["А", "Б", "В", "Г", "Д"],
            "answer": "Д",
            "hint": "Іван Купала — літній календарний обряд.",
            "rule": "Пісні, прив’язані до свят річного циклу (колядки, веснянки, купальські, жниварські), належать до календарно-обрядової лірики.",
            "solution": "Купальська пісня належить до календарно-обрядових пісень (Д).",
            "drill_key": "lit_genres",
        },
        {
            "id": "ukrlit_2026_2",
            "subject": "ukrlit",
            "section": "Давня українська література",
            "source": "Офіційний зразок НМТ-2026 (УЦОЯО)",
            "qtype": "single",
            "max_points": 1,
            "prompt": "Задля увиразнення ідеї слова Епікура «Подяка блаженній натурі за те, що потрібне зробила неважким, а важке – непотрібним» використав у своєму творі:",
            "options": ["Іван Котляревський", "Григорій Сковорода", "Тарас Шевченко", "Пантелеймон Куліш", "Панас Мирний"],
            "labels": ["А", "Б", "В", "Г", "Д"],
            "answer": "Б",
            "hint": "Це філософська ідея «сродної праці» та щастя у збірці «Байки Харківські» / «Бджола та Шершень».",
            "rule": "Григорій Сковорода — український філософ доби бароко, цитував Епікура в силі (моралі) до байки «Бджола та Шершень» (ідея «сродної праці»).",
            "solution": "Цитату Епікура використав Григорій Сковорода (Б).",
            "drill_key": "lit_genres",
        },
        {
            "id": "ukrlit_2026_3",
            "subject": "ukrlit",
            "section": "Література кінця XVIII – початку XX ст.",
            "source": "Офіційний зразок НМТ-2026 (УЦОЯО)",
            "qtype": "single",
            "max_points": 1,
            "prompt": "Доповніть пропуски: «Сюжет ___________ взято з часів ___________. Соціальні антагонізми, що виявилися відразу по смерті Богдана Хмельницького, слугують тлом для історії двох закоханих героїв – ___________.»",
            "options": [
                "«Кайдашевої сім’ї»; пореформених; Лавріна Кайдаша та Мелашки Балаш",
                "«Чорної ради»; Руїни; Петра Шраменка та Лесі Череванівни",
                "«Мини Мазайла»; українізації; Мокія Мазайла та Улі Розсохи",
                "«Марусі Чурай»; Національно-визвольної війни; Марусі Чурай та Гриця Бобренка",
                "«Захара Беркута»; Карпатської Руси; Максима Беркута та Мирослави",
            ],
            "labels": ["А", "Б", "В", "Г", "Д"],
            "answer": "Б",
            "hint": "Доба після смерті Б. Хмельницького (1663 рік, Ніжин) у першому історичному романі П. Куліша!",
            "rule": "«Чорна рада» (П. Куліш) зображає події Руїни (1663 р., боротьба Якима Сомка й Івана Брюховецького) та кохання Петра Шраменка й Лесі Череванівни.",
            "solution": "Правильний варіант — Б.",
            "drill_key": "lit_genres",
        },
        {
            "id": "ukrlit_2026_12",
            "subject": "ukrlit",
            "section": "Література XX ст.",
            "source": "Офіційний зразок НМТ-2026 (УЦОЯО)",
            "qtype": "single",
            "max_points": 1,
            "prompt": "Від першої особи (однієї з трьох героїнь) іде розповідь у творі:",
            "options": ["«Модри Камень»", "«Три зозулі з поклоном»", "«Contra spem spero!»", "«Моя автобіографія»", "«Valse mélancolique»"],
            "labels": ["А", "Б", "В", "Г", "Д"],
            "answer": "Д",
            "hint": "У цій новелі Ольги Кобилянської три подруги-мисткині живуть разом (Ганнуся, Софія й Марта).",
            "rule": "Не потрап у пастку «Три зозулі з поклоном» через слово «три»! Три героїні (Марта, Ганнуся, Софія) і розповідь від 1-ї особи Марти — у «Valse mélancolique» О. Кобилянської.",
            "solution": "Розповідь від імені однієї з трьох подруг (Марти) ведеться у «Valse mélancolique» (Д).",
            "drill_key": "lit_genres",
        },
        {
            "id": "ukrlit_2026_26",
            "subject": "ukrlit",
            "section": "Література кінця XVIII – початку XX ст.",
            "source": "Офіційний зразок НМТ-2026 (УЦОЯО)",
            "qtype": "matching",
            "max_points": 4,
            "prompt": "Поєднайте тему твору (А–Д) з іменем його літературного героя (1–4):",
            "left": ["1. Омелько Кайдаш", "2. Іван Дідух", "3. Мартин Боруля", "4. Іван Палійчук"],
            "right": {
                "А": "прагнення заможного селянина відновити дворянські права",
                "Б": "життєпис селянина-злочинця на широкому суспільному тлі",
                "В": "зображення побуту українських селян у пореформену добу",
                "Г": "змалювання життя гуцулів, їхніх вірувань, звичаїв, ритуалів",
                "Д": "показ трудової еміграції галицького селянства за океан",
            },
            "answer": {"1": "В", "2": "Д", "3": "А", "4": "Г"},
            "hint": "Кайдаш → «Кайдашева сім’я»; Дідух → «Камінний хрест» (еміграція до Канади); Боруля → дворянство; Палійчук → «Тіні забутих предків».",
            "rule": "Пов’язуй героя з твором і його головною темою: Омелько Кайдаш (пореформений побут), Іван Дідух (еміграція за океан), Мартин Боруля (погоня за дворянством), Іван Палійчук (життя гуцулів).",
            "solution": "1–В, 2–Д, 3–А, 4–Г.",
            "drill_key": "lit_pseudonyms",
        },
    ],
    "biology": [
        {
            "id": "bio_2026_2",
            "subject": "biology",
            "section": "Клітина. Хімічний склад і реалізація спадкової інформації",
            "source": "Офіційний зразок НМТ-2026 (УЦОЯО)",
            "qtype": "single",
            "max_points": 1,
            "prompt": "Позначте назву білка, який виконує каталітичну функцію:",
            "options": ["міозин", "глюкагон", "мальтаза", "фібриноген"],
            "labels": ["А", "Б", "В", "Г"],
            "answer": "В",
            "hint": "Каталітична функція — це ферменти! Шукай слово із закінченням на «-аза».",
            "rule": "Назви ферментів (біологічних каталізаторів) майже завжди закінчуються на «-аза» (мальтаза, амілаза, ліпаза). Міозин — руховий, глюкагон — гормон, фібриноген — згортання крові.",
            "solution": "Фермент, що виконує каталітичну функцію, — мальтаза (В).",
            "drill_key": "bio_dna_percent",
        },
        {
            "id": "bio_2026_3",
            "subject": "biology",
            "section": "Клітина. Хімічний склад і реалізація спадкової інформації",
            "source": "Офіційний зразок НМТ-2026 (УЦОЯО)",
            "qtype": "single",
            "max_points": 1,
            "prompt": "Ділянка молекули ДНК містить 100 аденілових і 50 гуанілових нуклеотидів. Обчисліть кількість залишків дезоксирибози в цій ділянці молекули ДНК:",
            "options": ["75", "150", "200", "300"],
            "labels": ["А", "Б", "В", "Г"],
            "answer": "Г",
            "hint": "У ДНК два ланцюги! Якщо А = 100 і Г = 50, то Т = 100 і Ц = 50.",
            "rule": "Кожен нуклеотид містить 1 залишок дезоксирибози. За правилом Чаргаффа А = Т, Г = Ц, отже всього нуклеотидів 2 · (А + Г).",
            "solution": "Усього нуклеотидів: 100(А) + 100(Т) + 50(Г) + 50(Ц) = 300. Отже, і залишків дезоксирибози 300 (Г).",
            "drill_key": "bio_dna_deoxy",
        },
        {
            "id": "bio_2026_5",
            "subject": "biology",
            "section": "Клітина. Хімічний склад і реалізація спадкової інформації",
            "source": "Офіційний зразок НМТ-2026 (УЦОЯО)",
            "qtype": "single",
            "max_points": 1,
            "prompt": "Деякі вакцини містять матричну РНК (мРНК). Коли вона потрапляє в клітину, механізм синтезу білків забезпечує утворення закодованого білка-антигена. Який процес забезпечує синтез білка за матрицею мРНК?",
            "options": ["реплікація", "трансляція", "транскрипція", "репарація"],
            "labels": ["А", "Б", "В", "Г"],
            "answer": "Б",
            "hint": "Синтез РНК із ДНК — це транскрипція («переписування»), а синтез білка з мРНК на рибосомах — «переклад» (трансляція).",
            "rule": "Реплікація = подвоєння ДНК; Транскрипція = синтез РНК за ДНК; Трансляція = синтез білка за мРНК на рибосомах; Репарація = лагодження ДНК.",
            "solution": "Синтез поліпептидного ланцюга (білка) за матрицею мРНК називається трансляцією (Б).",
            "drill_key": "bio_dna_percent",
        },
        {
            "id": "bio_2026_12",
            "subject": "biology",
            "section": "Біорізноманіття",
            "source": "Офіційний зразок НМТ-2026 (УЦОЯО)",
            "qtype": "single",
            "max_points": 1,
            "prompt": "Учитель біології дав завдання виростити плоди капусти білоголової. Учень приніс качан капусти, але вчитель сказав, що це вегетативний орган (видозмінена брунька), а плід капусти —",
            "options": ["сім’янка", "коробочка", "ягода", "стручок"],
            "labels": ["А", "Б", "В", "Г"],
            "answer": "Г",
            "hint": "Капуста належить до родини Капустяні (Хрестоцвіті), як редька й гірчиця.",
            "rule": "Плоди ключових родин: Капустяні (капуста, редис) → стручок; Пасльонові (томат, картопля) → ягода або коробочка; Бобові (горох, квасоля) → біб; Айстрові/Складноцвіті (соняшник) → сім’янка.",
            "solution": "Плід капусти — стручок (Г).",
            "drill_key": "bio_dna_deoxy",
        },
        {
            "id": "bio_2026_26",
            "subject": "biology",
            "section": "Біорізноманіття",
            "source": "Офіційний зразок НМТ-2026 (УЦОЯО)",
            "qtype": "matching",
            "max_points": 4,
            "prompt": "Поєднайте групу рослин (1–4) з назвою представника (А–Д) цієї групи:",
            "left": ["1. мохи", "2. папороті", "3. голонасінні", "4. покритонасінні"],
            "right": {
                "А": "страусове перо звичайне",
                "Б": "модрина європейська",
                "В": "баранець звичайний",
                "Г": "маршанція мінлива",
                "Д": "шипшина собача",
            },
            "answer": {"1": "Г", "2": "А", "3": "Б", "4": "Д"},
            "hint": "«Баранець звичайний» — це плаун (зайвий варіант!), «модрина» — хвойне дерево, «шипшина» — квіткова.",
            "rule": "Класика НМТ із ботаніки: мохи (зозулин льон, сфагнум, маршанція), папороті (щитник, орляк, страусове перо), плауни (баранець, булавовидний), голонасінні (сосна, ялина, модрина, тис), покритонасінні (квіткові).",
            "solution": "1–Г (маршанція), 2–А (страусове перо), 3–Б (модрина), 4–Д (шипшина).",
            "drill_key": "bio_dna_percent",
        },
        {
            "id": "bio_2026_27",
            "subject": "biology",
            "section": "Біорізноманіття",
            "source": "Офіційний зразок НМТ-2026 (УЦОЯО)",
            "qtype": "matching",
            "max_points": 4,
            "prompt": "Поєднайте назву клітин (1–4) тіла гідри з їхньою функцією (А–Д):",
            "left": ["1. епітеліально-м’язові", "2. жалкі", "3. залозисті", "4. проміжні"],
            "right": {
                "А": "зміна форми тіла й участь у рухах",
                "Б": "захист та добування їжі",
                "В": "забезпечення порожнинного травлення",
                "Г": "розмноження і регенерація",
                "Д": "сприйняття подразнень і здійснення рефлексів",
            },
            "answer": {"1": "А", "2": "Б", "3": "В", "4": "Г"},
            "hint": "Нервові клітини («Д») у переліку ліворуч не вказані — це зайвий варіант!",
            "rule": "Клітини кишковопорожнинних (гідра): епітеліально-м’язові (покриви та рух), жалкі (захист і полювання), залозисті (ферменти для порожнинного травлення), проміжні (регенерація — перетворюються на будь-які інші).",
            "solution": "1–А, 2–Б, 3–В, 4–Г.",
            "drill_key": "bio_dna_deoxy",
        },
    ],
    "physics": [
        {
            "id": "phys_2026_2",
            "subject": "physics",
            "section": "Механіка",
            "source": "Офіційний зразок НМТ-2026 (УЦОЯО)",
            "qtype": "single",
            "max_points": 1,
            "prompt": "Сувенірний магніт «прилип» до металевої вертикальної поверхні холодильника. Яка сила під час цього зрівноважує силу тяжіння, що діє на цей магніт?",
            "options": ["сила тертя ковзання", "сила тертя спокою", "сила магнітного притягання", "сила нормальної реакції поверхні"],
            "labels": ["А", "Б", "В", "Г"],
            "answer": "Б",
            "hint": "Сила тяжіння напрямлена вниз. Сила магнітного притягання — горизонтально (до дверцят). Що тягне магніт угору й не дає йому сповзати?",
            "rule": "Магнітне притягання напрямлене горизонтально (перпендикулярно до сили тяжіння) й задає силу реакції опори N. Униз тягне mg, а вгору її зрівноважує сила тертя спокою (магніт нерухомий!).",
            "solution": "Оскільки магніт перебуває у спокої на вертикальній стінці, силу тяжіння зрівноважує напрямлена вгору сила тертя спокою (Б).",
            "drill_key": "phys_incline",
        },
        {
            "id": "phys_2026_5",
            "subject": "physics",
            "section": "Молекулярна фізика та термодинаміка",
            "source": "Офіційний зразок НМТ-2026 (УЦОЯО)",
            "qtype": "single",
            "max_points": 1,
            "prompt": "Ідеальний одноатомний газ незмінної маси, якому надали 50 Дж теплоти, виконав роботу 20 Дж. Як змінилася внутрішня енергія цього газу?",
            "options": ["зменшилася на 30 Дж", "зменшилася на 70 Дж", "збільшилася на 30 Дж", "збільшилася на 70 Дж"],
            "labels": ["А", "Б", "В", "Г"],
            "answer": "В",
            "hint": "Перший закон термодинаміки: Q = ΔU + A.",
            "rule": "ΔU = Q − A. Якщо газу НАДАЛИ 50 Дж (Q = +50), а він ВИКОНАВ роботу 20 Дж (A = +20), то в нього залишилося 30 Дж: ΔU = +30 Дж.",
            "solution": "ΔU = 50 − 20 = +30 Дж → збільшилася на 30 Дж (В).",
            "drill_key": "phys_thermo_1law",
        },
        {
            "id": "phys_2026_12",
            "subject": "physics",
            "section": "Коливання і хвилі. Оптика",
            "source": "Офіційний зразок НМТ-2026 (УЦОЯО)",
            "qtype": "single",
            "max_points": 1,
            "prompt": "Яке явище пояснюють повним відбиттям світла?",
            "options": ["сонячне затемнення", "забарвлення крила метелика", "утворення веселки", "поширення світла у світловоді"],
            "labels": ["А", "Б", "В", "Г"],
            "answer": "Г",
            "hint": "В оптоволокні (світловоді) промінь багаторазово відбивається від стінок і не виходить назовні.",
            "rule": "Повне внутрішнє відбиття: оптоволокно (світловоди), призми біноклів, блиск алмазів. Веселка — дисперсія + заломлення; крило метелика — інтерференція; затемнення — прямолінійне поширення.",
            "solution": "Поширення світла у світловоді (Г).",
            "drill_key": "phys_free_fall",
        },
        {
            "id": "phys_2026_13",
            "subject": "physics",
            "section": "Квантова фізика та теорія відносності",
            "source": "Офіційний зразок НМТ-2026 (УЦОЯО)",
            "qtype": "single",
            "max_points": 1,
            "prompt": "Атом, рухаючись у вакуумі зі швидкістю 0,4c відносно нерухомої системи відліку, випромінює фотон у напрямку свого руху. Чому дорівнює швидкість цього фотона в нерухомій системі відліку?",
            "options": ["0,4c", "0,6c", "c", "1,4c"],
            "labels": ["А", "Б", "В", "Г"],
            "answer": "В",
            "hint": "Звичайне додавання швидкостей (0,4c + c = 1,4c) для світла НЕ працює! Згадай постулат Ейнштейна.",
            "rule": "Другий постулат СТВ Ейнштейна: швидкість світла у вакуумі (c) однакова в усіх інерціальних системах відліку й не залежить від швидкості джерела!",
            "solution": "Швидкість фотона у вакуумі в будь-якій ІСВ дорівнює c (В).",
            "drill_key": "phys_halflife",
        },
        {
            "id": "phys_2026_17",
            "subject": "physics",
            "section": "Механіка",
            "source": "Офіційний зразок НМТ-2026 (УЦОЯО)",
            "qtype": "short",
            "max_points": 2,
            "prompt": "Визначте час вільного падіння тіла з висоти 45 м зі стану спокою. Уважайте, що g = 10 м/с². Відповідь запишіть у секундах (с).",
            "answer": "3",
            "hint": "Використай формулу h = g·t² / 2.",
            "rule": "Під час падіння зі стану спокою h = g·t² / 2 ⇒ t = √(2h / g).",
            "solution": "t = √(2 · 45 / 10) = √9 = 3 с.",
            "drill_key": "phys_free_fall",
        },
        {
            "id": "phys_2026_18",
            "subject": "physics",
            "section": "Механіка",
            "source": "Офіційний зразок НМТ-2026 (УЦОЯО)",
            "qtype": "short",
            "max_points": 2,
            "prompt": "Санчата масою 15 кг перебувають на схилі, кут нахилу якого до горизонту становить 30°. Яку силу треба прикласти до санчат уздовж схилу, щоб утримувати їх у рівновазі? Тертя не враховуйте, g = 10 м/с². Відповідь запишіть у ньютонах (Н).",
            "answer": "75",
            "hint": "F = m·g·sin(30°).",
            "rule": "Для рівноваги на похилій площині без тертя: F = m·g·sin(α).",
            "solution": "F = 15 · 10 · 0,5 = 75 Н.",
            "drill_key": "phys_incline",
        },
        {
            "id": "phys_2026_22",
            "subject": "physics",
            "section": "Квантова фізика та теорія відносності",
            "source": "Офіційний зразок НМТ-2026 (УЦОЯО)",
            "qtype": "short",
            "max_points": 2,
            "prompt": "Дослідження скелета тварини показало, що в кістках залишилося 25 % радіоактивного Карбону ¹⁴C, період піврозпаду якого 5700 років. Скільки часу минуло після припинення життєдіяльності тварини? Відповідь запишіть у роках.",
            "answer": "11400",
            "hint": "Від 100 % до 25 % кількість зменшилася в 4 рази — скільки минуло періодів піврозпаду?",
            "rule": "100 % → 50 % (1 період) → 25 % (2 періоди). Множимо 2 на 5700.",
            "solution": "Минуло 2 періоди піврозпаду: 2 · 5700 = 11400 років.",
            "drill_key": "phys_halflife",
        },
    ],
    "chemistry": [
        {
            "id": "chem_2026_1",
            "subject": "chemistry",
            "section": "Загальна хімія",
            "source": "Офіційний зразок НМТ-2026 (УЦОЯО)",
            "qtype": "single",
            "max_points": 1,
            "prompt": "Позначте назву простої речовини:",
            "options": ["бронза", "бензен", "бром", "бутан"],
            "labels": ["А", "Б", "В", "Г"],
            "answer": "В",
            "hint": "Бронза — сплав (суміш), бензен (C₆H₆) і бутан (C₄H₁₀) — складні органічні речовини.",
            "rule": "Проста речовина складається з атомів ОДНОГО хімічного елемента. Бром (Br₂) — елемент-галоген і проста речовина.",
            "solution": "Бром (Br₂) — проста речовина (В).",
            "drill_key": "chem_gas_molar",
        },
        {
            "id": "chem_2026_10",
            "subject": "chemistry",
            "section": "Неорганічна хімія",
            "source": "Офіційний зразок НМТ-2026 (УЦОЯО)",
            "qtype": "single",
            "max_points": 1,
            "prompt": "Досліджували властивості розведених хлоридної та нітратної кислот. Позначте схему реакції, яка НЕ ВІДБУЛАСЯ:",
            "options": ["Cu + HCl →", "Cu + HNO₃ →", "CuO + HCl →", "CuO + HNO₃ →"],
            "labels": ["А", "Б", "В", "Г"],
            "answer": "А",
            "hint": "Подивись на ряд активності металів! Де стоїть мідь (Cu) відносно водню (H)?",
            "rule": "Звичайні кислоти (HCl, розб. H₂SO₄) НЕ реагують із металами, що стоять ПІСЛЯ водню (Cu, Ag, Hg, Au)! А от нітратна кислота (HNO₃) — окисник і реагує навіть із міддю.",
            "solution": "Мідь стоїть після водню, тому Cu + HCl не відбувається (А).",
            "drill_key": "chem_yield",
        },
        {
            "id": "chem_2026_14",
            "subject": "chemistry",
            "section": "Органічна хімія",
            "source": "Офіційний зразок НМТ-2026 (УЦОЯО)",
            "qtype": "single",
            "max_points": 1,
            "prompt": "Позначте молекулярну формулу продукту гідратації алкену C₅H₁₀:",
            "options": ["C₅H₁₀O", "C₅H₁₀O₂", "C₅H₁₂O₂", "C₅H₁₂O"],
            "labels": ["А", "Б", "В", "Г"],
            "answer": "Г",
            "hint": "Гідратація — це ПРИЄДНАННЯ води (H₂O)! Просто додай до формули алкену 2 атоми H та 1 атом O.",
            "rule": "Алкени CₙH₂ₙ + H₂O → одноатомний спирт CₙH₂ₙ₊₂O (або CₙH₂ₙ₊₁OH).",
            "solution": "C₅H₁₀ + H₂O → C₅H₁₂O (варіант Г).",
            "drill_key": "chem_alkane_combust",
        },
        {
            "id": "chem_2026_19",
            "subject": "chemistry",
            "section": "Органічна хімія",
            "source": "Офіційний зразок НМТ-2026 (УЦОЯО)",
            "qtype": "matching",
            "max_points": 3,
            "prompt": "Доберіть до хімічної реакції (1–3) її продукт (А–Д):",
            "left": ["1. ізомеризація гексану", "2. відновлення нітробензену", "3. тримеризація етину"],
            "right": {
                "А": "2,3-диметилбутан",
                "Б": "циклогексан",
                "В": "бензен",
                "Г": "анілін",
                "Д": "3-метилгексан",
            },
            "answer": {"1": "А", "2": "Г", "3": "В"},
            "hint": "Ізомери мають ОДНАКОВУ кількість атомів Карбону (у гексану 6 атомів C, у 3-метилгексану — 7!). Реакція Зініна (відновлення нітробензену) дає анілін.",
            "rule": "1) Ізомеризація зберігає формулу C₆H₁₄ (2,3-диметилбутан = 2+4 = 6 атомів C); 2) C₆H₅NO₂ + 6[H] → C₆H₅NH₂ (анілін); 3) 3 C₂H₂ → C₆H₆ (бензен, реакція Зелінського).",
            "solution": "1–А, 2–Г, 3–В.",
            "drill_key": "chem_alkane_combust",
        },
        {
            "id": "chem_2026_22",
            "subject": "chemistry",
            "section": "Обчислення в хімії",
            "source": "Офіційний зразок НМТ-2026 (УЦОЯО)",
            "qtype": "short",
            "max_points": 2,
            "prompt": "За температури 60 °C розчинність RbNO₃ становить 200 г у 100 г води. Обчисліть масу (г) насиченого за 60 °C розчину RbNO₃, для приготування якого використали воду масою 90 г.",
            "answer": "270",
            "hint": "Не забудь, що запитують масу ВСЬОГО РОЗЧИНУ (вода + сіль), а не лише масу солі!",
            "rule": "Маса розчину = m(води) + m(розчиненої солі). Спочатку знаходимо масу солі у 90 г води: 200 · 0,9 = 180 г, потім додаємо 90 г води!",
            "solution": "1) У 90 г води розчиняється 200 · (90/100) = 180 г солі.\n2) Маса розчину = 90 + 180 = 270 г.",
            "drill_key": "chem_solution_sat",
        },
        {
            "id": "chem_2026_23",
            "subject": "chemistry",
            "section": "Обчислення в хімії",
            "source": "Офіційний зразок НМТ-2026 (УЦОЯО)",
            "qtype": "short",
            "max_points": 2,
            "prompt": "Обчисліть масу (г) етанолу (M = 46 г/моль), що утвориться внаслідок гідратації етену об’ємом 112 л (н. у.), якщо відносний вихід спирту становить 60 %.",
            "answer": "138",
            "hint": "112 / 22,4 = 5 моль етену. Отже, теоретично утвориться 5 моль етанолу.",
            "rule": "n = V / 22,4; m_практ = n · M · (вихід % / 100).",
            "solution": "1) n(C₂H₄) = 112 / 22,4 = 5 моль.\n2) m_теор = 5 · 46 = 230 г.\n3) m_практ = 230 · 0,6 = 138 г.",
            "drill_key": "chem_yield",
        },
    ],
    "geography": [
        {
            "id": "geo_2026_1",
            "subject": "geography",
            "section": "Фізична географія України",
            "source": "Офіційний зразок НМТ-2026 (УЦОЯО)",
            "qtype": "single",
            "max_points": 1,
            "prompt": "Позначте назву географічного об’єкту, поблизу якого розташована найближча до Гринвіцького меридіана крайня точка України:",
            "options": ["Грем’яч", "Соломоново", "Рання Зоря", "Сарич"],
            "labels": ["А", "Б", "В", "Г"],
            "answer": "Б",
            "hint": "Гринвіцький меридіан (0° довготи) проходить через Велику Британію та Західну Європу. Отже, до нього найближча крайня ЗАХІДНА точка України!",
            "rule": "Україна лежить у Східній півкулі (22°–40° сх. д.). Тому найближче до 0° (Гринвіча) розташована крайня західна точка — с. Соломоново (Закарпатська обл.).",
            "solution": "Крайня західна точка України — с. Соломоново (Б).",
            "drill_key": "geo_ukr_extremes",
        },
        {
            "id": "geo_2026_3",
            "subject": "geography",
            "section": "Фізична географія України",
            "source": "Офіційний зразок НМТ-2026 (УЦОЯО)",
            "qtype": "single",
            "max_points": 1,
            "prompt": "Рівнинна частина території України піднята над рівнем Світового океану в середньому на 175 метрів. Зважаючи на цей показник, визначте форму рівнин, яка переважає в Україні:",
            "options": ["западини", "низовини", "височини", "плоскогір’я"],
            "labels": ["А", "Б", "В", "Г"],
            "answer": "Б",
            "hint": "Згадай класифікацію рівнин за абсолютною висотою: до 200 м, від 200 до 500 м, понад 500 м!",
            "rule": "Шкала рівнин: до 200 м — низовини, 200–500 м — височини, > 500 м — плоскогір’я. 175 м < 200 м!",
            "solution": "Середня висота 175 м (< 200 м) відповідає низовинам (Б).",
            "drill_key": "geo_ukr_extremes",
        },
        {
            "id": "geo_2026_4",
            "subject": "geography",
            "section": "Географія материків і океанів",
            "source": "Офіційний зразок НМТ-2026 (УЦОЯО)",
            "qtype": "single",
            "max_points": 1,
            "prompt": "Судно із Чорного моря зайшло в протоку Босфор і рухається в Атлантичний океан. Які три моря пройде судно, перш ніж перетне Гібралтарську протоку?",
            "options": [
                "Північне → Червоне → Аравійське",
                "Біле → Саргасове → Карибське",
                "Азовське → Балтійське → Каспійське",
                "Мармурове → Егейське → Середземне",
            ],
            "labels": ["А", "Б", "В", "Г"],
            "answer": "Г",
            "hint": "Уяви шлях із Чорного моря повз Туреччину та Грецію до Іспанії/Гібралтару.",
            "rule": "Морський шлях із Чорного моря в Атлантику: Чорне → Босфор → Мармурове → Дарданелли → Егейське → Середземне → Гібралтар.",
            "solution": "Правильний маршрут: Мармурове → Егейське → Середземне (Г).",
            "drill_key": "geo_map_scale",
        },
        {
            "id": "geo_2026_23",
            "subject": "geography",
            "section": "Загальна географія та топографія",
            "source": "Офіційний зразок НМТ-2026 (УЦОЯО)",
            "qtype": "short",
            "max_points": 2,
            "prompt": "За фрагментом топографічної карти масштабу 1 : 20 000 визначте відстань (у метрах) від перехрестя автошляхів до мосту над залізницею, якщо на карті довжина цього шляху становить 9 см.",
            "answer": "1800",
            "hint": "Відкинь два нулі від 20 000: в 1 см = 200 м.",
            "rule": "Масштаб 1 : 20 000 → в 1 см 200 м. Множимо 9 см на 200 м.",
            "solution": "9 · 200 = 1800 м.",
            "drill_key": "geo_map_scale",
        },
        {
            "id": "geo_2026_24",
            "subject": "geography",
            "section": "Загальна географія та топографія",
            "source": "Офіційний зразок НМТ-2026 (УЦОЯО)",
            "qtype": "short",
            "max_points": 2,
            "prompt": "Визначте азимут (у градусах) руху автомобіля дорогою від села Шутнівці до мосту над залізницею, якщо напрямок руху відхиляється від напрямку на схід на 15° (на північний схід).",
            "answer": "75",
            "hint": "Схід — це 90°, а відхилення до півночі (проти годинникової стрілки) зменшує кут від 90°.",
            "rule": "Азимут півночі = 0°, сходу = 90°, півдня = 180°, заходу = 270°. Відхилення від сходу до півночі на 15° дає 90° − 15°.",
            "solution": "90° − 15° = 75°.",
            "drill_key": "geo_azimuth",
        },
        {
            "id": "geo_2026_30",
            "subject": "geography",
            "section": "Україна і світове господарство. Регіони",
            "source": "Офіційний зразок НМТ-2026 (УЦОЯО)",
            "qtype": "multi3",
            "max_points": 3,
            "prompt": "Позначте три сегменти світового ринку товарів і послуг, на яких суб’єкти економіки України є експортерами, а США — імпортерами:",
            "items": {
                "1": "скраплений природний газ",
                "2": "нафтопродукти",
                "3": "металообробні верстати",
                "4": "соняшникова олія",
                "5": "натуральний мед",
                "6": "програмне забезпечення",
                "7": "легкові автомобілі",
            },
            "answer": ["4", "5", "6"],
            "hint": "Згадай головну спеціалізацію експорту України (АПК, харчові продукти та IT-аутсорсинг) і подумай, що США імпортують, а що експортують самі (СПГ, авто).",
            "rule": "Україна — один зі світових лідерів з експорту соняшникової олії, меду та IT-послуг/ПЗ, а США самі є великим експортером СПГ та нафтопродуктів.",
            "solution": "Правильні пункти: 4 (соняшникова олія), 5 (натуральний мед), 6 (програмне забезпечення).",
            "drill_key": "geo_ukr_extremes",
        },
    ],
}

# Об’єднуємо всі статичні завдання в єдиний словник BANK_QUESTIONS
BANK_QUESTIONS = {}
for k, v in STATIC_QUESTIONS.items():
    BANK_QUESTIONS[k] = list(v)
for k, v in STATIC_LANG_QUESTIONS.items():
    BANK_QUESTIONS[k] = list(v)
for k, v in STATIC_SCI_LIT_QUESTIONS.items():
    BANK_QUESTIONS[k] = list(v)

# Зіставляємо генератори за предметами для наповнення розгорнутих варіантів

# ---------------------------------------------------------------------------
# ВБУДОВАНИЙ АРХІВ ЗАВДАНЬ НМТ 2022–2025 РР. (УСІ 12 ПРЕДМЕТІВ)
# ---------------------------------------------------------------------------
ARCHIVE_2022_2025 = {
  "ukrmova": [
    {
      "id": "arch_ukr_2025_1",
      "section": "Фонетика. Графіка. Орфоепія",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "Однаковий звук позначають букви, виділені в кожному слові рядка (бороть[б]а / д[з]веніти / по[д]ія; ане[к]дот / [ґ]речний / е[к]зотика; сміє[т]ься / у[т]іха / шіс[т]сот; кі[г]тик / ле[г]ко / подру[г]а):",
      "options": [
        "боротьба, дзвеніти, подія (д / дз / д)",
        "анекдот, ґречний, екзотика (к / ґ / к)",
        "сміється, утіха, шістсот (т / т / т)",
        "кігтик, легко, подруга (г / г / г)"
      ],
      "labels": [
        "А",
        "Б",
        "В",
        "Г"
      ],
      "answer": "Б",
      "hint": "Пам’ятай про одзвінчення глухих перед дзвінкими: у словах «анекдот» і «екзотика» [к] стоїть перед дзвінкими [д] і [з], тому одзвінчується у [ґ]!",
      "rule": "В українській мові глухий приголосний перед дзвінким (крім в, м, н, л, р, й) уподібнюється до дзвінкого. Зокрема, [к] + дзвінкий → [ґ] (ане[ґ]дот, е[ґ]зотика, во[ґ]зал, рю[ґ]зак).",
      "solution": "У рядку Б в усіх трьох словах звучить твердий [ґ]: ане[ґ]дот, [ґ]речний, е[ґ]зотика. В А — дзвеніти дає африкату [д͡з]; у В — у слові «шістсот» [т] випадає; у Г — легко [х], подруга [г].",
      "drill_key": "ukrmova_nagolos"
    },
    {
      "id": "arch_ukr_2025_2",
      "section": "Фонетика. Графіка. Орфоепія",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "Правильно виділено букви на позначення наголошених звуків у всіх словах, ОКРІМ рядка (ВЕЛИКА буква вказує на наголос):",
      "options": [
        "заіржАвілі гальма, новий Обруч",
        "вирАзне читАння, замІжня донькА",
        "черговА пОмилка, заклАдка в довідникУ",
        "принести завчАсу, украЇнське видАння"
      ],
      "labels": [
        "А",
        "Б",
        "В",
        "Г"
      ],
      "answer": "А",
      "hint": "Перевір наголос у слові «обруч» — у значенні спортивного снаряда або обода він падає НЕ на перший склад.",
      "rule": "Нормативний наголос у словах зі списку НМТ: обрУч, заіржАвілий, читАння, замІжня, пОмилка і помИлка (обидва допустимі), завчАсу, видАння.",
      "solution": "Помилка у варіанті А: правильно вимовляти «обрУч», а не «Обруч».",
      "drill_key": "ukrmova_nagolos"
    },
    {
      "id": "arch_ukr_2025_4",
      "section": "Орфографія",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "М’який знак треба писати на місці пропуску в усіх словах рядка:",
      "options": [
        "посол..ський, дивиш..ся, охолон..те",
        "чотир..ох, кін..ський, Уман..щина",
        "т..мяність, с..орбати, колодяз..ний",
        "посун..ся, катаєт..ся, Гуцул..щина"
      ],
      "labels": [
        "А",
        "Б",
        "В",
        "Г"
      ],
      "answer": "Г",
      "hint": "Перевіряй три головні заборони: після шиплячих (дивишся), перед -ськ- після Н (кінський, Уманщина) та у слові-винятку «колодязний» Ь не пишеться!",
      "rule": "Після Л м’який знак пишеться навіть перед шиплячими (Гуцульщина, їдальня). Перед -ськ- після Н (кінський) і в слові «колодязний» Ь не ставиться.",
      "solution": "Правильний рядок Г: посунься (наказовий спосіб), катається (-ться у дієслові), Гуцульщина (після Л перед шиплячим).",
      "drill_key": "ukrmova_myak"
    },
    {
      "id": "arch_ukr_2025_6",
      "section": "Орфографія",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "НЕ ПОТРІБНО писати жодної букви на місці пропуску в усіх словах рядка:",
      "options": [
        "швидкіс..ний, пес..ливий, заздріс..ний",
        "буревіс..ник, перехрес..ний, аген..ський",
        "безчес..ний, щас..ливий, тиж..невий",
        "хворос..няк, радіс..ний, пристрас..ний"
      ],
      "labels": [
        "А",
        "Б",
        "В",
        "Г"
      ],
      "answer": "В",
      "hint": "Шукай рядок без запозичених слів і без винятків: «пестливий», «хворостняк», «агентський» зберігають літеру Т!",
      "rule": "У групах -ждн-, -здн-, -стн-, -стл- відбувається спрощення (Т/Д випадають: щасливий, тижневий, безчесний). Винятки: зап’ястний, кістлявий, пестливий, хвастливий, хворостняк, шістнадцять та іншомовні (агентський).",
      "solution": "У рядку В в усіх словах відбувається спрощення: безчесний, щасливий, тижневий (В).",
      "drill_key": "ukrmova_double"
    },
    {
      "id": "arch_ukr_2025_15",
      "section": "Лексикологія. Фразеологія",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "Українським відповідником до іншомовного слова «тактильний» є:",
      "options": [
        "чутливий",
        "обхідливий",
        "розмірений",
        "увічливий",
        "дотиковий"
      ],
      "labels": [
        "А",
        "Б",
        "В",
        "Г",
        "Д"
      ],
      "answer": "Д",
      "hint": "Згадай словосполучення «тактильні відчуття» — відчуття від дотику.",
      "rule": "Лат. tactilis буквально означає «той, що сприймається дотиком» — тобто «дотиковий».",
      "solution": "Український синонім до слова «тактильний» — «дотиковий» (Д).",
      "drill_key": "ukrmova_rodovyi"
    },
    {
      "id": "arch_ukr_2025_26",
      "section": "Лексикологія. Фразеологія",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "matching",
      "max_points": 4,
      "prompt": "Приєднайте до фрагмента діалогу (1–4) відповідний за змістом фразеологізм (А–Д):\n1. – Було багато охочих зіграти головну роль у п’єсі? – Так, претендентів […].\n2. – Легко працювати в команді з Миколою? – Звісно, він такий спокійний, […].\n3. – Наталка вже готова до виступу? – Безперечно, красуня, […].\n4. – Як ти думаєш, сцену достатньо освітлено? – Авжеж, видно […].",
      "left": [
        "1. Багато претендентів […]",
        "2. Спокійний, […]",
        "3. Красуня, […]",
        "4. Світло, видно […]"
      ],
      "right": {
        "А": "хоч у рамці вправ",
        "Б": "хоч у вухо бгай",
        "В": "хоч греблю гати",
        "Г": "хоч вовком вий",
        "Д": "хоч голки збирай"
      },
      "answer": {
        "1": "В",
        "2": "Б",
        "3": "А",
        "4": "Д"
      },
      "hint": "«Хоч греблю гати» — дуже багато; «хоч у вухо бгай» — тихий і поступливий; «хоч голки збирай» — світло, усе видно.",
      "rule": "Значення фразеологізмів перевіряємо за змістом ситуації: «хоч у рамці вправ» — писана красуня; «хоч вовком вий» — нестерпно важко (зайвий варіант).",
      "solution": "1–В (багато = хоч греблю гати), 2–Б (спокійний = хоч у вухо бгай), 3–А (красуня = хоч у рамці вправ), 4–Д (світло = хоч голки збирай).",
      "drill_key": "ukrmova_pref_zs"
    },
    {
      "id": "arch_ukr_2024_3",
      "section": "Орфографія",
      "source": "Архів НМТ-2024 (1 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "Подвоєні букви треба писати у формі орудного відмінка однини в усіх словах рядка:",
      "options": [
        "верф, паралель, подорож, ціль",
        "папороть, сіль, велич, стриманість",
        "кров, заметіль, емаль, світлотінь",
        "магістраль, мазь, мігрень, мідь"
      ],
      "labels": [
        "А",
        "Б",
        "В",
        "Г"
      ],
      "answer": "Г",
      "hint": "В орудному відмінку іменників III відміни подвоюються ЛИШЕ приголосні «Де Ти З’їСи Цю ЧаШу ЖиЛя» (д, т, з, с, ц, ч, ш, ж, л, н) між двома голосними. Губні (б, п, в, м, ф) і збіги приголосних (-ість) НЕ подвоюються!",
      "rule": "Після губних (верф’ю, кров’ю) ставиться апостроф, а при збігу двох різних приголосних (стриманістю, радістю) подвоєння немає.",
      "solution": "У рядку Г усі чотири слова закінчуються на один приголосний із правила подвоєння (л, з, н, д) після голосного: магістраллю, маззю, мігренню, міддю.",
      "drill_key": "ukrmova_double"
    },
    {
      "id": "arch_ukr_2024_4",
      "section": "Орфографія",
      "source": "Архів НМТ-2024 (1 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "Апостроф треба писати на місці пропуску в усіх словах рядка, ОКРІМ:",
      "options": [
        "між..ярусний, сузір..я, розм..якшити",
        "під..юджувати, солов..їний, стерв..ятник",
        "верб..я, подзв..якувати, перем..ятий",
        "підв..ялений, арф..ярка, роз..їхатися"
      ],
      "labels": [
        "А",
        "Б",
        "В",
        "Г"
      ],
      "answer": "В",
      "hint": "Якщо перед губним Б/П/В/М/Ф у корені стоїть інший приголосний (крім Р), апостроф НЕ пишеться!",
      "rule": "Перед Я, Ю, Є, Ї після губних апостроф не ставиться, якщо перед губним є інший кореневий приголосний (крім Р): подзвякувати (корінь дзвяк-, перед В стоїть З — апостроф не потрібен), свято, цвях, мавпячий.",
      "solution": "Помилка у варіанті В: у слові «подзвякувати» літера З належить до кореня («дзвяк»), тому апостроф не пишеться.",
      "drill_key": "ukrmova_myak"
    },
    {
      "id": "arch_ukr_2023_9",
      "section": "Будова слова. Словотвір",
      "source": "Архів НМТ-2023 (1 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "НЕ МАЮТЬ закінчення обидва слова в рядку:",
      "options": [
        "гордість, вчасно",
        "метро, джунглі",
        "читаючи, кашне",
        "розбито, блакить"
      ],
      "labels": [
        "А",
        "Б",
        "В",
        "Г"
      ],
      "answer": "В",
      "hint": "Відрізняй нульове закінчення (у змінних слів: гордість → гордості) від відсутності закінчення (у незмінних слів: прислівників, дієприслівників, невідмінюваних запозичень).",
      "rule": "Закінчення взагалі НЕМАЄ лише у незмінних частин мови: прислівників (вчасно), дієприслівників (читаючи), інфінітива, невідмінюваних іменників (метро, кашне) і форм на -но/-то (розбито). У відмінюваних іменників (гордість, блакить) — нульове закінчення, а «джунглі» — закінчення -і.",
      "solution": "Лише у В обидва слова незмінні: «читаючи» (дієприслівник) і «кашне» (невідмінюваний іменник).",
      "drill_key": "ukrmova_rodovyi"
    },
    {
      "id": "arch_ukr_2022_9",
      "section": "Орфографія",
      "source": "Архів НМТ-2022 (основна сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "Правильно написано всі похідні слова в рядку:",
      "options": [
        "Запоріжжя – запорізький, чех – чеський, Цюрих – цюриський",
        "Прага – пражський, козак – козацький, Овруч – овруцький",
        "Буг – бузький, латиш – латиський, Париж – парижський",
        "Рига – ризький, узбек – узбецький, Дрогобич – дрогобицький",
        "Кавказ – кавказський, турок – турецький, Збараж – збаразький"
      ],
      "labels": [
        "А",
        "Б",
        "В",
        "Г",
        "Д"
      ],
      "answer": "Г",
      "hint": "Згадай чергування перед суфіксом -ськ-: г/ж/з → -зьк- (Рига → ризький), к/ч/ц → -цьк- (узбек → узбецький, Дрогобич → дрогобицький). Винятки: казахський, баскський, меккський, цюрихський!",
      "rule": "При приєднанні -ськ-: г, ж, з переходять у -зьк- (празький, паризький, кавказький); к, ч, ц — у -цьк-; х, ш, с — у -ськ-. Винятки з іншомовних назв: цюрихський, казахський, тюркський.",
      "solution": "Без жодної помилки утворено всі прикметники в рядку Г: ризький, узбецький, дрогобицький.",
      "drill_key": "ukrmova_pref_zs"
    },
    {
      "id": "arch_ukr_2022_16",
      "section": "Лексикологія. Фразеологія",
      "source": "Архів НМТ-2022 (основна сесія)",
      "qtype": "matching",
      "max_points": 4,
      "prompt": "З’ясуйте значення (А–Д) кожного фразеологізму (1–4):",
      "left": [
        "1. шапкою докинути",
        "2. хоч греблю гати",
        "3. до нових віників",
        "4. як мокре горить"
      ],
      "right": {
        "А": "багато",
        "Б": "повільно",
        "В": "надовго",
        "Г": "близько",
        "Д": "незручно"
      },
      "answer": {
        "1": "Г",
        "2": "А",
        "3": "В",
        "4": "Б"
      },
      "hint": "«Шапкою докинути» — рукою подати (близько); «як мокре горить» — ледве-ледве, повільно.",
      "rule": "Фразеологізми-синоніми та значення: шапкою докинути = близько; хоч греблю гати = багато; до нових віників (пам’ятати) = надовго; як мокре горить = повільно.",
      "solution": "1–Г, 2–А, 3–В, 4–Б.",
      "drill_key": "ukrmova_pref_zs"
    },
    {
      "id": "arch_ukr_2022_20",
      "section": "Морфологія",
      "source": "Архів НМТ-2022 (основна сесія)",
      "qtype": "matching",
      "max_points": 4,
      "prompt": "З’ясуйте, якими частинами мови (А–Д) є виділені слова (1–4) в реченні:\n«Національний центр Олександра Довженка викупив у Японії й повернув в Україну копію [1: віднайденого] в місцевому кіноархіві [2: повнометражного] наукового фільму 1930 року «Людина і мавпа», [3: що] [4: донедавна] вважали втраченим.»",
      "left": [
        "1. віднайденого",
        "2. повнометражного",
        "3. що",
        "4. донедавна"
      ],
      "right": {
        "А": "займенник",
        "Б": "прикметник",
        "В": "прислівник",
        "Г": "форма дієслова (дієприкметник)",
        "Д": "форма дієслова (дієприслівник)"
      },
      "answer": {
        "1": "Г",
        "2": "Б",
        "3": "А",
        "4": "В"
      },
      "hint": "«Віднайденого» — ознака за дією (того, якого знайшли → дієприкметник). «Що» можна замінити на «який» → сполучне слово (займенник)!",
      "rule": "Якщо слово «що» в підрядному реченні можна замінити на «який / яку» і до нього ставиться відмінкове питання (вважали кого/що?), це займенник, а не сполучник.",
      "solution": "1–Г (дієприкметник), 2–Б (прикметник), 3–А (займенник «який/що»), 4–В (прислівник «доки?»).",
      "drill_key": "ukrmova_rodovyi"
    }
  ],
  "math": [
    {
      "id": "arch_math_2025_3",
      "section": "Рівняння, нерівності та їх системи",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "Позначте число, що є розв’язком системи нерівностей: { x > −3; x ≤ 7 }.",
      "options": [
        "−10",
        "−7",
        "−3",
        "5",
        "10"
      ],
      "labels": [
        "А",
        "Б",
        "В",
        "Г",
        "Д"
      ],
      "answer": "Г",
      "hint": "Точка −3 виколота (знак строго '>'), тому саме число −3 не входить у відповідь, а 7 входить.",
      "rule": "Розв’язком системи є перетин проміжків: x ∈ (−3; 7]. Строга нерівність не включає межу.",
      "solution": "Із запропонованих чисел до проміжку (−3; 7] потрапляє лише 5 (варіант Г).",
      "drill_key": "math_ineq"
    },
    {
      "id": "arch_math_2025_4",
      "section": "Числа і вирази",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "Спростіть вираз: 0,6x³ · 5x⁴ =",
      "options": [
        "30x⁷",
        "3x⁷",
        "30x¹²",
        "3x¹²",
        "0,3x¹²"
      ],
      "labels": [
        "А",
        "Б",
        "В",
        "Г",
        "Д"
      ],
      "answer": "Б",
      "hint": "Під час множення степенів з однаковою основою показники ДОДАЮТЬСЯ, а 0,6 · 5 = 3 (не 30!).",
      "rule": "aⁿ · aᵐ = aⁿ⁺ᵐ. Числові коефіцієнти перемножуємо окремо: 0,6 · 5 = 3.",
      "solution": "0,6 · 5 = 3; x³ · x⁴ = x³⁺⁴ = x⁷. Підсумок: 3x⁷ (Б).",
      "drill_key": "math_module_pow"
    },
    {
      "id": "arch_math_2025_7",
      "section": "Числа і вирази",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "Під час миття рук милом із крана витікає 25 л води, з них 60 % марнують під час намилювання. Скільки літрів води можна зберегти, якщо закривати кран перед намилюванням рук?",
      "options": [
        "19",
        "15",
        "12",
        "10",
        "6"
      ],
      "labels": [
        "А",
        "Б",
        "В",
        "Г",
        "Д"
      ],
      "answer": "Б",
      "hint": "Знайди 60 % від 25 літрів: помнож 25 на 0,60.",
      "rule": "Щоб знайти p % від числа A, помнож A на p/100.",
      "solution": "25 · 60 / 100 = 15 л (варіант Б).",
      "drill_key": "math_percent_trip"
    },
    {
      "id": "arch_math_2025_8",
      "section": "Стереометрія",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "У прямокутній системі координат у просторі задано точки A(5; −4; 0) і B(7; 2; −2). Визначте точку C, симетричну точці A відносно точки B.",
      "options": [
        "C(1; 3; −1)",
        "C(2; 6; −2)",
        "C(6; −1; −1)",
        "C(3; −10; 2)",
        "C(9; 8; −4)"
      ],
      "labels": [
        "А",
        "Б",
        "В",
        "Г",
        "Д"
      ],
      "answer": "Д",
      "hint": "Якщо C симетрична A відносно B, то B — це СЕРЕДИНА відрізка AC, а не C — середина AB!",
      "rule": "Координати кінця відрізка C за відомої середини B: x_C = 2x_B − x_A, y_C = 2y_B − y_A, z_C = 2z_B − z_A.",
      "solution": "x = 2·7 − 5 = 9; y = 2·2 − (−4) = 8; z = 2·(−2) − 0 = −4. Отримуємо C(9; 8; −4) (Д).",
      "drill_key": "math_vector"
    },
    {
      "id": "arch_math_2025_11",
      "section": "Рівняння, нерівності та їх системи",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "Розв’яжіть рівняння (2x − 7) / 3 = (5x + 4) / 2.",
      "options": [
        "−2/9",
        "−1 7/19",
        "−2 4/11",
        "−3 2/3",
        "−2/19"
      ],
      "labels": [
        "А",
        "Б",
        "В",
        "Г",
        "Д"
      ],
      "answer": "В",
      "hint": "Перемнож навхрест (основна властивість пропорції): 2(2x − 7) = 3(5x + 4).",
      "rule": "a/b = c/d ⇒ a·d = b·c.",
      "solution": "4x − 14 = 15x + 12 ⇒ −11x = 26 ⇒ x = −26/11 = −2 4/11 (В).",
      "drill_key": "math_ineq"
    },
    {
      "id": "arch_math_2025_14",
      "section": "Рівняння, нерівності та їх системи",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "Позначте проміжок, якому належить корінь рівняння 1 − log₀,₅(x) = 3.",
      "options": [
        "(−∞; −3)",
        "[−3; 0)",
        "[0; 3)",
        "[3; 10)",
        "[10; +∞)"
      ],
      "labels": [
        "А",
        "Б",
        "В",
        "Г",
        "Д"
      ],
      "answer": "Г",
      "hint": "Перенеси 1 праворуч: −log₀,₅(x) = 2 ⇒ log₀,₅(x) = −2, потім піднеси 0,5 до степеня −2.",
      "rule": "За означенням логарифма log_a(x) = b ⇔ x = a^b (при x > 0). А (1/2)⁻² = 2² = 4.",
      "solution": "log₀,₅(x) = −2 ⇒ x = (0,5)⁻² = (1/2)⁻² = 4. Число 4 належить [3; 10) (Г).",
      "drill_key": "math_exp_eq"
    },
    {
      "id": "arch_math_2025_17",
      "section": "Числа і вирази",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "matching",
      "max_points": 3,
      "prompt": "Доберіть до числового виразу (1–3) його значення (А–Д):\n1. sin(−π/6)\n2. π − |π + 2|\n3. (−1/√2)²",
      "left": [
        "1. sin(−π/6)",
        "2. π − |π + 2|",
        "3. (−1/√2)²"
      ],
      "right": {
        "А": "1/2",
        "Б": "−2",
        "В": "2",
        "Г": "−1/2",
        "Д": "√2"
      },
      "answer": {
        "1": "Г",
        "2": "Б",
        "3": "А"
      },
      "hint": "Синус непарний: sin(−α) = −sin(α). Модуль додатного числа (π + 2 > 0) розкривається з плюсом!",
      "rule": "sin(−π/6) = −1/2; |π + 2| = π + 2 ⇒ π − (π + 2) = −2; квадрат мінуса дає плюс: (−1/√2)² = 1/2.",
      "solution": "1–Г (−1/2), 2–Б (−2), 3–А (1/2).",
      "drill_key": "math_module_pow"
    },
    {
      "id": "arch_math_2025_19",
      "section": "Функції",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "short",
      "max_points": 2,
      "prompt": "Дотична, проведена до графіка функції y = f(x) у точці з абсцисою x₀ = 3, паралельна прямій y = 1,5x + 5. Обчисліть значення похідної функції g(x) = 18/x − f(x) в точці x₀ = 3.",
      "answer": "-3.5",
      "hint": "Якщо дотична паралельна прямій y = 1,5x + 5, то f'(3) = 1,5! А похідна (18/x)' = −18/x².",
      "rule": "У паралельних прямих кутові коефіцієнти рівні: f'(x₀) = k = 1,5. Похідна (1/x)' = −1/x².",
      "solution": "g'(x) = −18/x² − f'(x). У точці x₀ = 3: g'(3) = −18/9 − 1,5 = −2 − 1,5 = −3,5.",
      "drill_key": "math_deriv_ext"
    },
    {
      "id": "arch_math_2025_20",
      "section": "Комбінаторика, ймовірність, статистика",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "short",
      "max_points": 2,
      "prompt": "У салоні літака налічується n рядів, у кожному з яких розташовано по 6 крісел (обабіч проходу по 3). Імовірність того, що першому пасажиру дістанеться місце біля проходу в першому або останньому ряду, дорівнює 1/45. Визначте n.",
      "answer": "30",
      "hint": "Скільки всього місць біля проходу в першому ТА останньому рядах разом? (У кожному ряду по 2 місця біля проходу: ліворуч і праворуч від проходу).",
      "rule": "Усього місць 6n. Сприятливих (біля проходу в 1-му й n-му рядах) рівно 4. P = 4 / (6n) = 1/45.",
      "solution": "4 / (6n) = 1/45 ⇒ 6n = 180 ⇒ n = 30 рядів.",
      "drill_key": "math_prob"
    },
    {
      "id": "arch_math_2024_9",
      "section": "Стереометрія",
      "source": "Архів НМТ-2024 (1 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "Обчисліть площу бічної поверхні правильної трикутної піраміди, сторона основи якої дорівнює 8 см, а апофема на 2 см більша за сторону основи піраміди.",
      "options": [
        "72 см²",
        "384 см²",
        "192 см²",
        "120 см²",
        "240 см²"
      ],
      "labels": [
        "А",
        "Б",
        "В",
        "Г",
        "Д"
      ],
      "answer": "Г",
      "hint": "Апофема m = 8 + 2 = 10 см. Площа бічної поверхні правильної піраміди S_б = ½ · P_осн · m.",
      "rule": "Для правильної трикутної піраміди периметр основи P = 3a, бічна поверхня S_б = ½ · P · m.",
      "solution": "P = 3 · 8 = 24 см; m = 10 см; S_б = ½ · 24 · 10 = 120 см² (Г).",
      "drill_key": "math_trap_angle"
    },
    {
      "id": "arch_math_2024_19",
      "section": "Функції",
      "source": "Архів НМТ-2024 (1 сесія)",
      "qtype": "short",
      "max_points": 2,
      "prompt": "Обчисліть визначений інтеграл ∫ від 3 до 5 виразу (x² + 2x + 1) / (x + 1) dx.",
      "answer": "10",
      "hint": "Чисельник — це формула квадрата суми (x + 1)²! Спочатку скороти дріб на (x + 1).",
      "rule": "(x² + 2x + 1) / (x + 1) = x + 1 (на [3; 5] знаменник не 0). Первісна від (x + 1) дорівнює x²/2 + x.",
      "solution": "F(5) − F(3) = (25/2 + 5) − (9/2 + 3) = 17,5 − 7,5 = 10.",
      "drill_key": "math_deriv_ext"
    },
    {
      "id": "arch_math_2023_19",
      "section": "Функції",
      "source": "Архів НМТ-2023 (1 сесія)",
      "qtype": "short",
      "max_points": 2,
      "prompt": "Число 27 є членом арифметичної прогресії з різницею d = 5. Визначте числа з проміжку (60; 75), що є членами цієї прогресії. У відповіді запишіть суму цих чисел.",
      "answer": "201",
      "hint": "Додавай по 5 від числа 27: 27, 32, 37, ..., доки не потрапиш у проміжок (60; 75).",
      "rule": "Члени арифметичної прогресії відрізняються на крок d = 5. Звичайним перебором кроку легко виписати числа між 60 і 75.",
      "solution": "Після 27 ідуть: 32, 37, 42, 47, 52, 57, [62, 67, 72], 77. Сума в (60; 75): 62 + 67 + 72 = 201.",
      "drill_key": "math_ineq"
    },
    {
      "id": "arch_math_2022_11",
      "section": "Рівняння, нерівності та їх системи",
      "source": "Архів НМТ-2022 (основна сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "Розв’яжіть систему рівнянь: { 3√x = 12; x − 2y = 26 }. Якщо (x₀; y₀) — розв’язок системи, то x₀ + y₀ =",
      "options": [
        "11",
        "21",
        "−7",
        "−10",
        "−14"
      ],
      "labels": [
        "А",
        "Б",
        "В",
        "Г",
        "Д"
      ],
      "answer": "А",
      "hint": "Із першого рівняння √x = 4 ⇒ x = 16 (не 4!). Підстав x = 16 у друге рівняння.",
      "rule": "Щоб позбутися квадратного кореня √x = a (a ≥ 0), підносимо обидві частини до квадрата: x = a².",
      "solution": "√x = 4 ⇒ x₀ = 16. Тоді 16 − 2y₀ = 26 ⇒ −2y₀ = 10 ⇒ y₀ = −5. Сума: 16 + (−5) = 11 (А).",
      "drill_key": "math_ineq"
    }
  ],
  "history": [
    {
      "id": "arch_hist_2025_1",
      "section": "Від найдавніших часів до першої половини XVI ст.",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "Залізні знаряддя праці та зброю на українських землях першими почали виготовляти племена:",
      "options": [
        "скіфів",
        "сарматів",
        "трипільців",
        "кіммерійців"
      ],
      "labels": [
        "А",
        "Б",
        "В",
        "Г"
      ],
      "answer": "Г",
      "hint": "Ранній залізний вік на території України (IX–VII ст. до н. е.) відкрили саме кочовики, які прийшли до скіфів.",
      "rule": "Послідовність степових культур на півдні України: кіммерійці (IX–VII ст. до н. е., перші опанували залізо) → скіфи (VII–III ст. до н. е.) → сармати (III ст. до н. е. – IV ст. н. е.). Трипільці — енеоліт (мідь).",
      "solution": "Першими залізо на українських землях почали обробляти кіммерійці (Г).",
      "drill_key": "hist_terms_19c"
    },
    {
      "id": "arch_hist_2025_5",
      "section": "Друга половина XVI–XVIII ст.",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "Який документ став компромісом для розв’язання гострого релігійного питання в Речі Посполитій (1632 р.)?",
      "options": [
        "«Пункти для заспокоєння руського народу»",
        "Куруківська угода",
        "Хотинський мир",
        "«Ординація Війська Запорозького»"
      ],
      "labels": [
        "А",
        "Б",
        "В",
        "Г"
      ],
      "answer": "А",
      "hint": "Цей документ ухвалили 1632 р. за короля Владислава IV, і він легалізував православну митрополію на чолі з Петром Могилою.",
      "rule": "«Пункти для заспокоєння руського народу» (1632) повернули права православній церкві й визнали Київську митрополію Петра Могили. Інші варіанти — про реєстр або війни з Туреччиною/козаками.",
      "solution": "Релігійний компроміс 1632 р. — «Пункти для заспокоєння руського народу» (А).",
      "drill_key": "hist_chrono_17c"
    },
    {
      "id": "arch_hist_2025_10",
      "section": "Кінець XVIII – початок XX ст.",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "Суспільно-політична течія народовців серед молодої західноукраїнської інтелігенції в 1860-ті рр. у Галичині, Буковині та Закарпатті ідеологічно була опонентом:",
      "options": [
        "москвофілам",
        "українофілам",
        "чорносотенцям",
        "народникам"
      ],
      "labels": [
        "А",
        "Б",
        "В",
        "Г"
      ],
      "answer": "А",
      "hint": "У XIX столітті в Галичині боролися дві головні течії: одні вважали українців окремим народом («Просвіта»), інші орієнтувалися на Російську імперію.",
      "rule": "Головне ідейне протистояння на західноукраїнських землях у 1860–1880-х рр.: народовці (українська мова, єдиний народ) проти москвофілів («язичіє», єдність із Росією).",
      "solution": "Ідеологічними опонентами народовців були москвофіли (А).",
      "drill_key": "hist_terms_19c"
    },
    {
      "id": "arch_hist_2025_17",
      "section": "Україна в 1945 р. – початок XXI ст.",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "Генерал-хорунжий, командувач Української повстанської армії (УПА) з 1950 року, – це:",
      "options": [
        "Дмитро Клячківський",
        "Степан Бандера",
        "Роман Шухевич",
        "Василь Кук"
      ],
      "labels": [
        "А",
        "Б",
        "В",
        "Г"
      ],
      "answer": "Г",
      "hint": "Роман Шухевич командував УПА до загибелі в березні 1950 року. Хто прийняв командування після нього?",
      "rule": "Командувачі УПА: Д. Клячківський (Клим Савур) — 1943 р., Р. Шухевич (Тарас Чупринка) — 1943–1950 рр., В. Кук (Леміш) — 1950–1954 рр.",
      "solution": "Після загибелі Романа Шухевича в 1950 році командувачем УПА став Василь Кук (Г).",
      "drill_key": "hist_dates_20c"
    },
    {
      "id": "arch_hist_2025_22",
      "section": "Україна в 1914–1945 рр.",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "matching",
      "max_points": 4,
      "prompt": "Узгодьте подію (1–4) з роком (А–Д), коли вона відбулася:",
      "left": [
        "1. проголошення курсу на індустріалізацію",
        "2. входження УСРР до складу СРСР",
        "3. утворення Української автокефальної православної церкви",
        "4. початок насильницької колективізації"
      ],
      "right": {
        "А": "1921 р.",
        "Б": "1922 р.",
        "В": "1923 р.",
        "Г": "1925 р.",
        "Д": "1929 р."
      },
      "answer": {
        "1": "Г",
        "2": "Б",
        "3": "А",
        "4": "Д"
      },
      "hint": "УАПЦ (В. Липківський) — 1921; СРСР — грудень 1922; курс на індустріалізацію (XIV з’їзд) — 1925; «рік великого перелому» (суцільна колективізація) — 1929.",
      "rule": "Обов’язкові дати 1920-х рр.: 1921 (НЕП, УАПЦ), 1922 (СРСР), 1923 (коренізація), 1925 (індустріалізація), 1929 (колективізація).",
      "solution": "1–Г (1925), 2–Б (1922), 3–А (1921), 4–Д (1929).",
      "drill_key": "hist_dates_20c"
    },
    {
      "id": "arch_hist_2025_25",
      "section": "Від найдавніших часів до першої половини XVI ст.",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "sequence",
      "max_points": 3,
      "prompt": "Розташуйте поняття відповідно до перебігу соціально-економічних процесів (від найдавнішого до найпізнішого):",
      "items": {
        "А": "«відруб»",
        "Б": "«вотчина»",
        "В": "«полюддя»",
        "Г": "«фільварок»"
      },
      "answer": "ВБГА",
      "hint": "Полюддя — збирання данини в IX–X ст.; вотчина — спадкове землеволодіння з XI ст.; фільварок — панське господарство XV–XVI ст.; відруб — столипінська реформа 1906 р.",
      "rule": "Хронологія форм господарювання: полюддя (Русь IX–X ст.) → вотчина (XI–XIV ст.) → фільварок (Річ Посполита XV–XVIII ст.) → відруб (Столипін 1906 р.).",
      "solution": "Правильна послідовність: ВБГА.",
      "drill_key": "hist_chrono_17c"
    },
    {
      "id": "arch_hist_2025_28",
      "section": "Кінець XVIII – початок XX ст.",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "multi3",
      "max_points": 3,
      "prompt": "Які губернії Російської імперії створено у XIX ст. на землях колишньої Лівобережної Гетьманщини та Слобожанщини? (Оберіть 3 відповіді)",
      "items": {
        "1": "Чернігівську",
        "2": "Миколаївську",
        "3": "Харківську",
        "4": "Київську",
        "5": "Полтавську",
        "6": "Таврійську",
        "7": "Катеринославську"
      },
      "answer": [
        "1",
        "3",
        "5"
      ],
      "hint": "Київська — Правобережжя; Таврійська та Катеринославська — Південна Україна. Які 3 на Лівому березі (разом зі Слобожанщиною)?",
      "rule": "9 українських губерній Російської імперії: Лівобережжя + Слобожанщина (Чернігівська, Полтавська, Харківська); Правобережжя (Київська, Волинська, Подільська); Південь (Катеринославська, Херсонська, Таврійська).",
      "solution": "На землях Лівобережної Гетьманщини та Слобожанщини були створені Чернігівська (1), Харківська (3) і Полтавська (5) губернії.",
      "drill_key": "hist_terms_19c"
    },
    {
      "id": "arch_hist_2024_5",
      "section": "Друга половина XVI–XVIII ст.",
      "source": "Архів НМТ-2024 (1 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "«Вони... приговорили та постановили мир на тринадцять років під корисними умовами для обох монархій; покривджено тільки козаків...», – так Самійло Величко схарактеризував укладення:",
      "options": [
        "«Вічного миру»",
        "Гадяцького договору",
        "Зборівського договору",
        "Андрусівського перемир’я"
      ],
      "labels": [
        "А",
        "Б",
        "В",
        "Г"
      ],
      "answer": "Г",
      "hint": "Ключовий маркер: перемир’я на 13 років (1667 р.), що поділило Гетьманщину по Дніпру між Москвою та Річчю Посполитою.",
      "rule": "Андрусівське перемир’я 1667 р. — перемир’я на 13,5 років між Московським царством і Річчю Посполитою (Правобережжя — Польщі, Лівобережжя й тимчасово Київ — Москві, Запорожжя — під подвійним підпорядкуванням).",
      "solution": "Ідеться про Андрусівське перемир’я 1667 року (Г).",
      "drill_key": "hist_chrono_17c"
    },
    {
      "id": "arch_hist_2023_22",
      "section": "Кінець XVIII – початок XX ст.",
      "source": "Архів НМТ-2023 (1 сесія)",
      "qtype": "matching",
      "max_points": 4,
      "prompt": "Поєднайте назву організації (1–4) з іменем історичної особи, яка була її членом (А–Д):",
      "left": [
        "1. Братство тарасівців",
        "2. Кирило-Мефодіївське братство",
        "3. «Південно-Західний відділ Російського географічного товариства»",
        "4. Наукове товариство ім. Т. Шевченка"
      ],
      "right": {
        "А": "Микола Гулак",
        "Б": "Михайло Грушевський",
        "В": "Дмитро Донцов",
        "Г": "Павло Чубинський",
        "Д": "Микола Міхновський"
      },
      "answer": {
        "1": "Д",
        "2": "А",
        "3": "Г",
        "4": "Б"
      },
      "hint": "Міхновський проголосив «Credo молодих українців» (Братство тарасівців); Гулак — один із 3 засновників Кирило-Мефодіївського братства; Чубинський — етнограф у відділі Географічного товариства; Грушевський очолював НТШ у Львові.",
      "rule": "Зіставляй організації XIX ст. з лідерами: Братство тарасівців (1891) → М. Міхновський; Кирило-Мефодіївське братство (1846) → М. Костомаров, М. Гулак, В. Білозерський; Південно-Західний відділ РГТ (1873) → П. Чубинський, В. Антонович; НТШ → М. Грушевський.",
      "solution": "1–Д, 2–А, 3–Г, 4–Б.",
      "drill_key": "hist_terms_19c"
    },
    {
      "id": "arch_hist_2022_17",
      "section": "Україна в 1914–1945 рр.",
      "source": "Архів НМТ-2022 (основна сесія)",
      "qtype": "matching",
      "max_points": 4,
      "prompt": "Установіть відповідність між прізвищем діяча (1–4) та подією (А–Д), до якої він причетний:",
      "left": [
        "1. С. Петлюра",
        "2. П. Скоропадський",
        "3. Д. Вітовський",
        "4. Н. Махно"
      ],
      "right": {
        "А": "створення Холодноярської республіки",
        "Б": "розгром армії генерала П. Врангеля в Криму",
        "В": "формування Української галицької армії (УГА)",
        "Г": "гетьманський переворот",
        "Д": "укладання Варшавської угоди"
      },
      "answer": {
        "1": "Д",
        "2": "Г",
        "3": "В",
        "4": "Б"
      },
      "hint": "Дмитро Вітовський — командир «Листопадового зриву» і перший держсекретар військових справ ЗУНР (УГА); Махно 1920 р. в союзі з червоними форсував Сиваш проти Врангеля.",
      "rule": "Ключові персоналії 1918–1920 рр.: Скоропадський (гетьманський переворот 29.04.1918), Петлюра (Директорія і Варшавський договір 04.1920), Вітовський (Листопадовий зрив та УГА), Махно (розгром Врангеля в Криму 1920).",
      "solution": "1–Д, 2–Г, 3–В, 4–Б.",
      "drill_key": "hist_dates_20c"
    },
    {
      "id": "arch_hist_2022_20",
      "section": "Україна в 1945 р. – початок XXI ст.",
      "source": "Архів НМТ-2022 (основна сесія)",
      "qtype": "matching",
      "max_points": 4,
      "prompt": "Установіть відповідність між періодом в історії України (1–4) та поняттями й термінами (А–Д), які його характеризують:",
      "left": [
        "1. Україна в перші повоєнні роки (1945 – поч. 1950-х рр.)",
        "2. Україна в умовах десталінізації (1953–1964 рр.)",
        "3. Україна в період загострення кризи радянської системи (1965–1985 рр.)",
        "4. Україна в умовах незалежності (1991 р. – поч. XXI ст.)"
      ],
      "right": {
        "А": "«самвидав», «номенклатура», «дефіцит», «правозахисник»",
        "Б": "«новий порядок», «радянізація», «план “Ост”», «депортація»",
        "В": "«приватизація», «тимчасово окупована територія», «АТО», «європейська інтеграція»",
        "Г": "«“саморозпуск” УГКЦ», «ждановщина», «космополітизм», «лисенківщина»",
        "Д": "«відлига», «політична реабілітація», «раднаргоспи», «шістдесятники»"
      },
      "answer": {
        "1": "Г",
        "2": "Д",
        "3": "А",
        "4": "В"
      },
      "hint": "1945–1953 — «ждановщина» та ліквідація УГКЦ; 1953–1964 — «відлига» та «шістдесятники»; 1965–1985 — «застій» («дефіцит», «самвидав»).",
      "rule": "Поняття-маркери епох XX століття: повоєнні роки → ждановщина, космополітизм; хрущовська доба → відлига, раднаргоспи, шістдесятники; застій → дефіцит, самвидав.",
      "solution": "1–Г, 2–Д, 3–А, 4–В.",
      "drill_key": "hist_terms_19c"
    }
  ],
  "english": [
    {
      "id": "arch_eng_2025_s1_23",
      "section": "Use of English: Лексика (Task 5)",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "Read the sentence and choose the best word (A–D):\n«According to experts, the British accent (23) _______ every 25 miles, and it’s thought a lot of the accents have developed due to geographic location and immigration.»",
      "options": [
        "moves",
        "changes",
        "reaches",
        "turns"
      ],
      "labels": [
        "A",
        "B",
        "C",
        "D"
      ],
      "answer": "B",
      "hint": "Йдеться про те, що британський акцент «змінюється» кожні 25 миль.",
      "rule": "За змістом географічного розмаїття діалектів вживається дієслово change («змінюватися»). Move = рухатися, reach = досягати, turn = повертати/перетворюватися.",
      "solution": "Правильний варіант B (changes): акцент змінюється кожні 25 миль.",
      "drill_key": "eng_vocab_context"
    },
    {
      "id": "arch_eng_2025_s1_24",
      "section": "Use of English: Лексика (Task 5)",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "Read the sentence and choose the best word (A–D):\n«It’s thought a lot of the accents have developed as a (24) _______ of geographic location, early settlers and immigration.»",
      "options": [
        "result",
        "reason",
        "reaction",
        "conclusion"
      ],
      "labels": [
        "A",
        "B",
        "C",
        "D"
      ],
      "answer": "A",
      "hint": "Сталий вираз-зв’язка з прийменником «as a ... of» зі значенням «у результаті / внаслідок».",
      "rule": "Стала колокація: as a result of something («у результаті чогось»). Після reason зазвичай ставиться прийменник for/why, а не конструкція as a reason of.",
      "solution": "Правильна відповідь A (result): as a result of = у результаті чогось.",
      "drill_key": "eng_vocab_context"
    },
    {
      "id": "arch_eng_2025_s1_25",
      "section": "Use of English: Лексика (Task 5)",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "Read the sentence and choose the best word (A–D):\n«For example, it’s been said that until the mid-1800s Liverpudlians (25) _______ similar to those from Manchester, before port industries boomed.»",
      "options": [
        "voiced",
        "said",
        "sounded",
        "pronounced"
      ],
      "labels": [
        "A",
        "B",
        "C",
        "D"
      ],
      "answer": "C",
      "hint": "Яке дієслово-зв’язка поєднується з прикметником «similar» у значенні «звучали схоже»?",
      "rule": "Дієслово сприйняття sound + прикметник (sound similar to — звучати схоже на). Дієслова say і pronounce вимагають прямого додатка (say something, pronounce a word), а не прикметника.",
      "solution": "Правильний варіант C (sounded): «мешканці Ліверпуля звучали схоже на мешканців Манчестера».",
      "drill_key": "eng_vocab_context"
    },
    {
      "id": "arch_eng_2025_s1_28",
      "section": "Use of English: Граматика (Task 6)",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "Choose the correct word (A–D) to fill in the gap:\n«Italian immigrants themselves brought pasta (28) _______ they went.»",
      "options": [
        "elsewhere",
        "otherwhere",
        "everywhere",
        "somewhere"
      ],
      "labels": [
        "A",
        "B",
        "C",
        "D"
      ],
      "answer": "C",
      "hint": "«Куди б вони не вирушали / усюди, куди б вони не їхали».",
      "rule": "У стверджувальному підрядному реченні місця зі значенням «усюди, куди б не» вживається сполучний прислівник everywhere.",
      "solution": "Правильний варіант C (everywhere): «привозили пасту всюди, куди б не їхали».",
      "drill_key": "eng_connectors_whether"
    },
    {
      "id": "arch_eng_2025_s1_30",
      "section": "Use of English: Граматика (Task 6)",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "Choose the correct grammar form (A–D):\n«One of the most popular theories (30) _______ in the Macaroni Journal by the Association of Food Industries.»",
      "options": [
        "published",
        "was published",
        "has published",
        "were published"
      ],
      "labels": [
        "A",
        "B",
        "C",
        "D"
      ],
      "answer": "B",
      "hint": "Поглянь на два маркери: 1) підмет «ONE of the theories» (однина!); 2) прийменник «by ...» (пасивний стан!).",
      "rule": "У конструкції «One of + іменник у мн.» присудок узгоджується зі словом ONE (однина!). Якщо дія виконана над теорією (маркер by), потрібен Passive Voice → was published.",
      "solution": "Підмет в однині («one») + пасивний стан («by ...») → was published (B).",
      "drill_key": "eng_passive_past"
    },
    {
      "id": "arch_eng_2025_s1_31",
      "section": "Use of English: Граматика (Task 6)",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "Choose the correct form (A–D):\n«(31) _______ even some evidence of 4,000-year-old noodles made from millet.»",
      "options": [
        "It is",
        "Here are",
        "There is",
        "There are"
      ],
      "labels": [
        "A",
        "B",
        "C",
        "D"
      ],
      "answer": "C",
      "hint": "Пастка НМТ: іменник «evidence» (доказ/свідчення) в англійській мові НЕЗЛІЧУВАНИЙ (завжди однина)!",
      "rule": "Іменники evidence, information, advice, news, research — незлічувані (uncountable) і завжди вимагають дієслова в однині: There is some evidence (не There are!).",
      "solution": "Існує свідчення = There is ... evidence (одн., C).",
      "drill_key": "eng_verb_agreement"
    },
    {
      "id": "arch_eng_2025_s2_28",
      "section": "Use of English: Граматика (Task 6)",
      "source": "Архів НМТ-2025 (2 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "Choose the correct grammar form (A–D):\n«A woman (28) _______ on the 10th floor of an apartment building was shocked to discover a raccoon asleep on her balcony.»",
      "options": [
        "living",
        "lives",
        "lived",
        "live"
      ],
      "labels": [
        "A",
        "B",
        "C",
        "D"
      ],
      "answer": "A",
      "hint": "Присудок у реченні вже є («was shocked»). Потрібен дієприкметниковий зворот: жінка, ЯКА ЖИВЕ (активна дія)...",
      "rule": "Скорочене означальне підрядне з активним значенням передається дієприкметником на -ing (Participle I): A woman living on the 10th floor = A woman who lives/was living...",
      "solution": "Активний дієприкметник від дієслова live — living (A).",
      "drill_key": "eng_passive_past"
    },
    {
      "id": "arch_eng_2025_s2_31",
      "section": "Use of English: Граматика (Task 6)",
      "source": "Архів НМТ-2025 (2 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "Choose the correct grammar form (A–D):\n«Larry Sorel says balconies can be inviting places for raccoons to shelter, especially if food (31) _______ out.»",
      "options": [
        "are left",
        "leave",
        "leaves",
        "is left"
      ],
      "labels": [
        "A",
        "B",
        "C",
        "D"
      ],
      "answer": "D",
      "hint": "Слово «food» (їжа) незлічуване (однина), і їжу «залишають» (пасивний стан!).",
      "rule": "Food — незлічуваний іменник (дієслово в однині). Оскільки їжа не залишає себе сама, потрібен Passive Voice (Present Simple Passive): is left.",
      "solution": "Food (одн.) + пасив → is left (D).",
      "drill_key": "eng_verb_agreement"
    },
    {
      "id": "arch_eng_2024_s1_11",
      "section": "Reading: Пошук інформації (Task 3)",
      "source": "Архів НМТ-2024 (1 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "Read the text and match the best statement (A–D):\n«Leo Houlding began climbing at the age of 10 and by 18 had become the first Briton to free-climb the infamous El Capitan. Since then he has specialised in tackling the most technical peaks. He’s also an experienced base jumper and at the forefront of para-alpinism, scaling up mountains then parachuting down.»\n\nThis traveller _______:",
      "options": [
        "travelled alone to the coldest points on the earth",
        "combined ascending and flying down the summit",
        "shared environmental ideas with statespeople",
        "managed to survive a traumatic incident"
      ],
      "labels": [
        "A",
        "B",
        "C",
        "D"
      ],
      "answer": "B",
      "hint": "Шукай перефразування фрази «scaling up mountains then parachuting down»!",
      "rule": "У Task 3 відповіді завжди замасковані синонімами: scaling up mountains = ascending (підйом), parachuting down = flying down the summit (спуск/політ униз із вершини).",
      "solution": "Фраза «scaling up mountains then parachuting down» перефразована у варіанті B: combined ascending and flying down the summit.",
      "drill_key": "eng_reading_ads"
    },
    {
      "id": "arch_eng_2023_s1_28",
      "section": "Use of English: Граматика (Task 6)",
      "source": "Архів НМТ-2023 (1 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "Choose the correct form (A–D):\n«She may be four years older than the other girls in her class, but Parisa looks forward to (28) _______ to school every day.»",
      "options": [
        "be going",
        "go",
        "going",
        "be gone"
      ],
      "labels": [
        "A",
        "B",
        "C",
        "D"
      ],
      "answer": "C",
      "hint": "Головна пастка НМТ! Після виразу «look forward to» частка «to» — це ПРИЙМЕННИК, тому за нею ставиться дієслово із закінченням -ing (герундій)!",
      "rule": "Після сталих конструкцій look forward to, be used to, get used to, object to завжди вживається герундій (V-ing), а НЕ чистий інфінітив.",
      "solution": "Після «look forward to» потрібен герундій → going (C).",
      "drill_key": "eng_connectors_whether"
    },
    {
      "id": "arch_eng_2023_s2_30",
      "section": "Use of English: Граматика (Task 6)",
      "source": "Архів НМТ-2023 (2 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "Choose the correct form (A–D):\n«AutoX already has more than two (30) _______ robotaxis deployed in five Chinese cities, including Shanghai and Wuhan.»",
      "options": [
        "hundreds of",
        "hundred of",
        "hundreds",
        "hundred"
      ],
      "labels": [
        "A",
        "B",
        "C",
        "D"
      ],
      "answer": "D",
      "hint": "Перед пропуском стоїть точний числівник «two»! За точної лічби до слів hundred, thousand, million закінчення -s НЕ додається!",
      "rule": "Після точного числа (two, five, several) слова hundred, thousand, million вживаються в однині без -s і без of (two hundred robotaxis). Закінчення -s + of ставиться лише за невизначеної множини (hundreds of cars).",
      "solution": "Після числівника «two» ставимо форму без -s і без of → hundred (D).",
      "drill_key": "eng_verb_agreement"
    },
    {
      "id": "arch_eng_2023_s2_32",
      "section": "Use of English: Граматика (Task 6)",
      "source": "Архів НМТ-2023 (2 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "Choose the correct form (A–D):\n«Whether the company can pull humans from behind the wheel in other markets (32) _______ on local regulators.»",
      "options": [
        "depend",
        "depends",
        "depended",
        "has depended"
      ],
      "labels": [
        "A",
        "B",
        "C",
        "D"
      ],
      "answer": "B",
      "hint": "Усе підметне підрядне («Whether the company can pull humans...» — «Чи зможе компанія...») сприймається як ОДНА ситуація в однині (it)!",
      "rule": "Коли підметом є ціле підрядне речення з whether/that/what або герундій, дієслово-присудок завжди ставиться в однині (3-тя особа одн. у Present Simple → -s).",
      "solution": "Підмет виражений цілим підрядним («Чи зможе компанія...»), що відповідає 3-й особі однини (it) → depends (B).",
      "drill_key": "eng_verb_agreement"
    }
  ],
  "german": [
    {
      "id": "arch_ger_2025_1",
      "section": "Lesen: Загальне й детальне розуміння",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "Wählen Sie die passende Überschrift (A–D):\n«Die 67 niedrigen gelben Häuser in Augsburg sind ein sehr spezieller Wohnort. Die Fuggerei ist wahrscheinlich die älteste Sozialsiedlung der Welt. Der Kaufmann Jakob Fugger hat sie vor genau 500 Jahren für arme Augsburger gestiftet. In den 142 Wohnungen leben auch heute noch Menschen, die im Jahr nur 88 Cent Kaltmiete bezahlen – und drei Mal am Tag beten.»",
      "options": [
        "Augsburg statt Regensburg: Ein Tipp für Touristen",
        "Den Ort Dorf gibt es wirklich",
        "Ein wahres Beispiel der Liebe zu seinem Nächsten",
        "Kleine Stadt, die viel anbieten kann"
      ],
      "labels": [
        "A",
        "B",
        "C",
        "D"
      ],
      "answer": "C",
      "hint": "Ключова думка: купець заснував поселення для бідних містян («für arme Augsburger gestiftet»), де оренда коштує символічні 88 центів на рік.",
      "rule": "У завданнях на добір заголовка (Aufgabe 1) обирай варіант, що відображає головну ідею: благодійність і допомога бідним = «Liebe zu seinem Nächsten» (любов до ближнього).",
      "solution": "Правильний заголовок C («Справжній приклад любові до ближнього»).",
      "drill_key": "ger_gram_context"
    },
    {
      "id": "arch_ger_2025_28",
      "section": "Grammatik: Граматика в контексті",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "Ergänzen Sie die richtige Verbform:\n«Zu Hause kein Platz für Pflanzen? Oder (28) _______ der grüne Daumen?»",
      "options": [
        "fehlen",
        "fehlt",
        "fehlst",
        "fehle"
      ],
      "labels": [
        "A",
        "B",
        "C",
        "D"
      ],
      "answer": "B",
      "hint": "Знайди підмет: «der grüne Daumen» — це однина (3-тя особа, чоловічий рід)!",
      "rule": "У Present Simple (Präsens) для 3-ї особи одн. (er/sie/es, der Daumen) дієслово отримує закінчення -t.",
      "solution": "Підмет «der grüne Daumen» (одн.) → fehlt (B).",
      "drill_key": "ger_gram_context"
    },
    {
      "id": "arch_ger_2025_29",
      "section": "Grammatik: Граматика в контексті",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "Wählen Sie die richtige Präposition:\n«Der Hamburger Biergarten Kiez Garden hilft: (29) _______ einem halben Jahr kann man dort in einer Klappe Blumen anonym abgeben.»",
      "options": [
        "vor",
        "nach",
        "seit",
        "in"
      ],
      "labels": [
        "A",
        "B",
        "C",
        "D"
      ],
      "answer": "C",
      "hint": "Дія почалася пів року тому і триває в теперішньому часі (kann man abgeben — Präsens!).",
      "rule": "Прийменник «seit + Dativ» позначає дію, що почалася в минулому й досі триває в теперішньому (відтоді / вже пів року). «Vor + Dativ» вживається з минулим часом (пів року тому).",
      "solution": "Теперішній час («kann abgeben») + тривалість дотепер → seit einem halben Jahr (C).",
      "drill_key": "ger_gram_context"
    },
    {
      "id": "arch_ger_2025_30",
      "section": "Grammatik: Граматика в контексті",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "Wählen Sie das richtige Pronomen:\n«Seit einem halben Jahr kann (30) _______ dort in einer Klappe Blumen anonym abgeben.»",
      "options": [
        "er",
        "man",
        "sie",
        "es"
      ],
      "labels": [
        "A",
        "B",
        "C",
        "D"
      ],
      "answer": "B",
      "hint": "Безособове узагальнене значення: «там можна здати квіти анонімно».",
      "rule": "Неозначено-особовий займенник «man» використовується в загальних твердженнях (будь-хто / можна) і завжди вимагає дієслова в 3-й особі одн. (kann man).",
      "solution": "Безособове значення «можна здати» передає займенник man (B).",
      "drill_key": "ger_gram_context"
    },
    {
      "id": "arch_ger_2025_31",
      "section": "Grammatik: Граматика в контексті",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "Wählen Sie das richtige Reflexivpronomen:\n«Im Kiez Garden kümmert man (31) _______ dann um sie.»",
      "options": [
        "mich",
        "dich",
        "sich",
        "euch"
      ],
      "labels": [
        "A",
        "B",
        "C",
        "D"
      ],
      "answer": "C",
      "hint": "Займенник «man» узгоджується з 3-ю особою — який зворотний займенник у дієслова «sich kümmern um» у 3-й особі?",
      "rule": "Із підметом man (та er/sie/es/sie) зворотні дієслова (sich kümmern) завжди вживаються із займенником sich.",
      "solution": "Із підметом «man» зворотний займенник лише sich (C).",
      "drill_key": "ger_gram_context"
    },
    {
      "id": "arch_ger_2025_32",
      "section": "Grammatik: Граматика в контексті",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "Wählen Sie die richtige Verbform:\n«Rund hundert Pflanzen haben so bis heute ein neues Heim (32) _______.»",
      "options": [
        "bekommen",
        "bekamen",
        "bekommt",
        "bekam"
      ],
      "labels": [
        "A",
        "B",
        "C",
        "D"
      ],
      "answer": "A",
      "hint": "У реченні вже є допоміжне дієслово «haben» і показник «bis heute» — це Perfekt! Який Partizip II у дієслова bekommen?",
      "rule": "У дієслів із невідокремлюваним префіксом be- (bekommen) у Partizip II префікс ge- НЕ додається: bekommen → hat bekommen.",
      "solution": "Perfekt: haben + Partizip II (bekommen) → A.",
      "drill_key": "ger_gram_context"
    }
  ],
  "french": [
    {
      "id": "arch_fr_2025_1",
      "section": "Compréhension écrite: Читання",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "Choisissez la rubrique qui correspond à ce texte:\n«La portion de la Route Centre Europe Atlantique (RCEA) traversant l’Allier va officiellement devenir une autoroute que les automobilistes pourront emprunter. L’A79, c’est son nom, va en effet être ouverte à la circulation pour tous les types d’utilisateurs ce vendredi 4 novembre.»",
      "options": [
        "Sport",
        "Transport",
        "Culture",
        "Actualité"
      ],
      "labels": [
        "A",
        "B",
        "C",
        "D"
      ],
      "answer": "D",
      "hint": "У цьому блоці текстів рубрика «Transport» стосується іншої нотатки (про електромобілі та автовиробників), а тут повідомляється про конкретну новинну подію з датою («ce vendredi 4 novembre» — відкриття траси А79).",
      "rule": "В Exercice 1 на НМТ перевіряється вміння відрізняти загальне новинне повідомлення (Actualité — конкретна подія з датою відкриття об’єкта) від тематичних оглядів (Transport, Planète, High-Tech).",
      "solution": "Офіційний ключ УЦОЯО: D (Actualité).",
      "drill_key": "fr_gram_context"
    },
    {
      "id": "arch_fr_2025_28",
      "section": "Grammaire: Граматика в контексті",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "Complétez le dialogue:\n«– Bonjour, Lili ! – Tiens ! Tu connais mon prénom ! Mais _______ es-tu ?»",
      "options": [
        "qui",
        "pourquoi",
        "comment",
        "quand"
      ],
      "labels": [
        "A",
        "B",
        "C",
        "D"
      ],
      "answer": "A",
      "hint": "«Ти знаєш моє ім’я! Але ХТО ти?»",
      "rule": "Питальний займенник «qui» («хто») використовується для істот (людей): Qui es-tu ?",
      "solution": "За змістом підходить лише qui («хто») → A.",
      "drill_key": "fr_gram_context"
    },
    {
      "id": "arch_fr_2025_29",
      "section": "Grammaire: Граматика в контексті",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "Choisissez le pronom démonstratif correct:\n«– Laisse ton vélo ici et prends _______ de Luc. Il sera d’accord.»",
      "options": [
        "celle",
        "celles",
        "celui",
        "ceux"
      ],
      "labels": [
        "A",
        "B",
        "C",
        "D"
      ],
      "answer": "C",
      "hint": "Слово «vélo» у французькій мові чоловічого роду в однині (le vélo).",
      "rule": "Вказівні займенники перед прийменником de: celui (чол. р. одн.), celle (жін. р. одн.), ceux (чол. р. мн.), celles (жін. р. мн.).",
      "solution": "Оскільки le vélo чоловічого роду одн., потрібен варіант celui (C).",
      "drill_key": "fr_gram_context"
    },
    {
      "id": "arch_fr_2025_30",
      "section": "Grammaire: Граматика в контексті",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "Choisissez le pronom personnel correct:\n«Pendant le carnaval, tout est permis ! Les règles sont mises entre parenthèses et chacun fait ce qu’il _______ plaît.»",
      "options": [
        "leur",
        "te",
        "vous",
        "lui"
      ],
      "labels": [
        "A",
        "B",
        "C",
        "D"
      ],
      "answer": "D",
      "hint": "Підмет — «chacun» (кожен, 3-тя особа одн.), отже «що ЙОМУ подобається».",
      "rule": "Дієслово plaire вимагає непрямого додатка (plaire à quelqu'un). Для 3-ї особи одн. (chacun) вживається займенник lui («йому»).",
      "solution": "Chacun (одн., 3-тя особа) → ce qu’il lui plaît (D).",
      "drill_key": "fr_gram_context"
    },
    {
      "id": "arch_fr_2025_31",
      "section": "Grammaire: Граматика в контексті",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "Choisissez la forme verbale correcte:\n«– Il y a quelqu’un dehors. – Qui _______ venir à cette heure ?»",
      "options": [
        "pourra",
        "pourrait",
        "pouvait",
        "peux"
      ],
      "labels": [
        "A",
        "B",
        "C",
        "D"
      ],
      "answer": "B",
      "hint": "Значення припущення/невпевненості в теперішньому часі: «Хто б це міг прийти о такій порі?» (Conditionnel présent).",
      "rule": "Для вираження припущення або ввічливого запитання («міг би») використовується Conditionnel présent: pouvoir → pourrait.",
      "solution": "Ввічливе припущення в теперішньому часі → pourrait (B).",
      "drill_key": "fr_gram_context"
    },
    {
      "id": "arch_fr_2025_32",
      "section": "Grammaire: Граматика в контексті",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "Choisissez le mode correct:\n«Si les troupeaux sont mieux protégés, le loup ne les attaquera pas. Il faut qu’ils _______ gardés par un ou plusieurs bergers.»",
      "options": [
        "sont",
        "seraient",
        "soient",
        "seront"
      ],
      "labels": [
        "A",
        "B",
        "C",
        "D"
      ],
      "answer": "C",
      "hint": "Після безособового виразу необхідності «Il faut que...» завжди ставиться Subjonctif!",
      "rule": "Конструкція «Il faut que + підмет» вимагає Subjonctif présent. Дієслово être у Subjonctif для 3-ї особи мн. (ils) має форму soient.",
      "solution": "Після «Il faut qu’ils» потрібен Subjonctif дієслова être → soient (C).",
      "drill_key": "fr_gram_context"
    }
  ],
  "spanish": [
    {
      "id": "arch_esp_2025_1",
      "section": "Lectura: Розуміння тексту",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "Elige el título más adecuado para el texto:\n«Los científicos llevan muchos años observando que los individuos que tienen una menor cantidad o calidad de relaciones sociales presentan más problemas de salud. Existen abundantes evidencias de que el aislamiento social prolongado tiene un impacto negativo sobre el sistema nervioso.»",
      "options": [
        "El impacto negativo de las redes sociales",
        "Un alarmante crecimiento",
        "Para estar sano, hay que tener amigos",
        "¿Cómo ser más feliz con menos?"
      ],
      "labels": [
        "A",
        "B",
        "C",
        "D"
      ],
      "answer": "C",
      "hint": "Обережно з пасткою A: у тексті взагалі немає слів про соцмережі! Йдеться про те, що тривала соціальна ізоляція шкодить здоров’ю.",
      "rule": "Якщо люди з малою кількістю соціальних зв’язків частіше хворіють, отже для здоров’я потрібні друзі (Para estar sano, hay que tener amigos).",
      "solution": "Правильний заголовок C («Щоб бути здоровим, треба мати друзів»).",
      "drill_key": "esp_gram_context"
    },
    {
      "id": "arch_esp_2025_28",
      "section": "Gramática: Граматика в контексті",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "Elige la forma verbal correcta:\n«Si _______ lloviendo, tendremos una buena cosecha.»",
      "options": [
        "continúe",
        "continuará",
        "continuaría",
        "continúa"
      ],
      "labels": [
        "A",
        "B",
        "C",
        "D"
      ],
      "answer": "D",
      "hint": "Реальна умова (1-й тип умовних речень): після «Si» (якщо) в іспанській НІКОЛИ не ставиться майбутній час (Futuro) чи Subjuntivo presente!",
      "rule": "У реальних умовних реченнях (I типу): Si + Presente de Indicativo (continúa), Futuro Simple (tendremos).",
      "solution": "Після Si в умові 1-го типу вживається Presente de Indicativo → continúa (D).",
      "drill_key": "esp_gram_context"
    },
    {
      "id": "arch_esp_2025_29",
      "section": "Gramática: Граматика в контексті",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "Elige la preposición correcta:\n«Me gusta muchísimo este país, estoy enamorado _______ su cultura.»",
      "options": [
        "a",
        "de",
        "con",
        "en"
      ],
      "labels": [
        "A",
        "B",
        "C",
        "D"
      ],
      "answer": "B",
      "hint": "Який прийменник в іспанській потрібен після «estar enamorado» («бути закоханим у...»)?",
      "rule": "Стале керування в іспанській мові: estar enamorado DE alguien / algo (на відміну від українського «у»). Не плутай з «en»!",
      "solution": "Правильний прийменник: enamorado DE su cultura (B).",
      "drill_key": "esp_gram_context"
    },
    {
      "id": "arch_esp_2025_30",
      "section": "Gramática: Граматика в контексті",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "Elige la forma del imperativo negativo:\n«Niños, por favor, no _______; me duele mucho la cabeza.»",
      "options": [
        "gritéis",
        "gritad",
        "grites",
        "gritáis"
      ],
      "labels": [
        "A",
        "B",
        "C",
        "D"
      ],
      "answer": "A",
      "hint": "Звертання до дітей на «ви» у множині (vosotros) + ЗАПЕРЕЧЕННЯ (no) → у заперечному наказовому способі вживається Presente de Subjuntivo!",
      "rule": "В іспанській Imperativo negativo завжди збігається з Presente de Subjuntivo: для vosotros від дієслова gritar (-ar) закінчення -éis → no gritéis.",
      "solution": "Заперечний імператив для vosotros → no gritéis (A).",
      "drill_key": "esp_gram_context"
    },
    {
      "id": "arch_esp_2025_31",
      "section": "Gramática: Граматика в контексті",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "Elige la forma verbal correcta:\n«Hoy Pedro tiene un examen muy importante. ¡Ojalá _______ suerte!»",
      "options": [
        "tiene",
        "tendrá",
        "tendría",
        "tenga"
      ],
      "labels": [
        "A",
        "B",
        "C",
        "D"
      ],
      "answer": "D",
      "hint": "Слово «¡Ojalá!» («Хоч би / Дай боже!») завжди вимагає умовного способу (Subjuntivo)!",
      "rule": "Після ¡Ojalá (que)! за реального побажання на теперішній/майбутній час вживається Presente de Subjuntivo: tener → tenga.",
      "solution": "¡Ojalá tenga suerte! → варіант D.",
      "drill_key": "esp_gram_context"
    },
    {
      "id": "arch_esp_2025_32",
      "section": "Gramática: Граматика в контексті",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "Elige la preposición correcta:\n«Me he acostumbrado _______ vivir aquí.»",
      "options": [
        "en",
        "por",
        "a",
        "de"
      ],
      "labels": [
        "A",
        "B",
        "C",
        "D"
      ],
      "answer": "C",
      "hint": "Керування дієслова «acostumbrarse» («звикнути до чогось»).",
      "rule": "Зворотне дієслово acostumbarse завжди вимагає прийменника «a» (acostumbrarse a hacer algo).",
      "solution": "Правильний прийменник: acostumbrado A vivir aquí (C).",
      "drill_key": "esp_gram_context"
    }
  ],
  "ukrlit": [
    {
      "id": "arch_lit_2025_1",
      "section": "Усна народна творчість",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "Уривок:\n«Вчора була суботонька, сьогодні неділя, –\nЧом на тобі, наймиточку, сорочка не біла?\nОй, не біла, ой, не біла, та й не буде біла,\nБо не знає бурлак бідний, коли та неділя»\nузято з:",
      "options": [
        "родинно-побутової пісні",
        "суспільно-побутової пісні",
        "календарно-обрядової пісні",
        "історичної пісні",
        "народної балади"
      ],
      "labels": [
        "А",
        "Б",
        "В",
        "Г",
        "Д"
      ],
      "answer": "Б",
      "hint": "Ключові герої — «наймиточок» (наймит) і «бурлак бідний». Це соціальна верства, а не сімейні стосунки чи свята календаря.",
      "rule": "Суспільно-побутові пісні (козацькі, чумацькі, бурлацькі, наймитські) відображають життя й важку працю окремих соціальних груп.",
      "solution": "Пісня про важку долю наймита/бурлака належить до суспільно-побутових пісень (Б).",
      "drill_key": "lit_genres"
    },
    {
      "id": "arch_lit_2025_3",
      "section": "Література кінця XVIII – початку XX ст.",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "Якову де Бальмену Тарас Шевченко присвячує твір, у якому:",
      "options": [
        "засуджує колонізаторську політику російського самодержавства на Кавказі",
        "закликає земляків звільнитися від кайданів самодержавства",
        "розповідає про трагічне кохання дівчини-покритки до російського офіцера",
        "висміює вірнопідданство й аморальність земляків-перевертнів",
        "критикує українську еліту, яка зневажає свій народ"
      ],
      "labels": [
        "А",
        "Б",
        "В",
        "Г",
        "Д"
      ],
      "answer": "А",
      "hint": "Художник Яків де Бальмен, друг Шевченка, загинув у 1845 році на Кавказі. Яку поему поет присвятив його пам’яті?",
      "rule": "Поема Т. Шевченка «Кавказ» присвячена «Искреннему моему Якову де Бальмену» і викриває колоніальну війну Російської імперії на Кавказі.",
      "solution": "Правильний варіант А: поема «Кавказ» засуджує колонізаторську політику самодержавства на Кавказі.",
      "drill_key": "lit_genres"
    },
    {
      "id": "arch_lit_2025_5",
      "section": "Література кінця XVIII – початку XX ст.",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "Прислів’я «На язиці – мед, а на думці – отрута» характеризує:",
      "options": [
        "Омелька Кайдаша",
        "Івана Палійчука",
        "Мартина Борулю",
        "Івана Брюховецького",
        "Чіпку Варениченка"
      ],
      "labels": [
        "А",
        "Б",
        "В",
        "Г",
        "Д"
      ],
      "answer": "Г",
      "hint": "Згадай «Чорну раду» П. Куліша: хто прикидався простим другом бідняків на виборах, а отримавши булаву, цинічно сказав: «Обдули ми дурне мужицтво...»?",
      "rule": "Лицемірний демагог у романі П. Куліша «Чорна рада» — Іван Брюховецький (повна протилежність прямому Якимові Сомку).",
      "solution": "Це характеристика Івана Брюховецького (Г).",
      "drill_key": "lit_pseudonyms"
    },
    {
      "id": "arch_lit_2025_11",
      "section": "Література XX ст.",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "Образи весняної ночі, солов’їного співу, летючої миті життя, радісного свята квіток, Фауста створив поет, який належав до:",
      "options": [
        "київських неокласиків",
        "«празької школи»",
        "дисидентів",
        "шістдесятників",
        "Театру корифеїв"
      ],
      "labels": [
        "А",
        "Б",
        "В",
        "Г",
        "Д"
      ],
      "answer": "Б",
      "hint": "Ідеться про вірш «Чари ночі» («Сміються, плачуть солов’ї...»). Хто його автор і до якої емігрантської групи поетів він належав?",
      "rule": "Олександр Олесь (О. Кандиба) — автор «Чар ночі», який жив в еміграції в Чехословаччині (його відносять до «празької школи» поетів).",
      "solution": "Автор «Чар ночі» Олександр Олесь належав до «празької школи» (Б).",
      "drill_key": "lit_pseudonyms"
    },
    {
      "id": "arch_lit_2025_26",
      "section": "Література XX ст.",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "matching",
      "max_points": 4,
      "prompt": "Поєднайте назву твору (1–4) з його історичним тлом (А–Д):",
      "left": [
        "1. «Захар Беркут»",
        "2. «Мина Мазайло»",
        "3. «Маруся Чурай»",
        "4. «Тигролови»"
      ],
      "right": {
        "А": "доба Хмельниччини",
        "Б": "період Руїни",
        "В": "українізація в 20-ті роки XX ст.",
        "Г": "монгольська навала XIII ст.",
        "Д": "сталінські репресії в 30-ті роки XX ст."
      },
      "answer": {
        "1": "Г",
        "2": "В",
        "3": "А",
        "4": "Д"
      },
      "hint": "Тухольці проти орди Бурунди (1241 р.); Мазайло і суперечки про українську мову (1920-ті); Маруся Чурай за Богдана Хмельницького; Григорій Многогрішний тікає зі сталінського ешелону (1930-ті).",
      "rule": "Історичне тло програмових творів: «Захар Беркут» (1241), «Маруся Чурай» (Хмельниччина XVII ст.), «Мина Мазайло» (українізація 1920-х), «Тигролови» (сталінські репресії 1930-х).",
      "solution": "1–Г, 2–В, 3–А, 4–Д.",
      "drill_key": "lit_genres"
    },
    {
      "id": "arch_lit_2024_3",
      "section": "Теорія літератури та аналіз текстів",
      "source": "Архів НМТ-2024 (1 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "До ліро-епосу належать обидва твори в рядку:",
      "options": [
        "«Мойсей»; «Енеїда»",
        "«Заповіт»; «Ой летіла стріла»",
        "«Бджола та Шершень»; «Катерина»",
        "«Чари ночі»; «Балада про соняшник»",
        "«Лісова пісня»; «Кавказ»"
      ],
      "labels": [
        "А",
        "Б",
        "В",
        "Г",
        "Д"
      ],
      "answer": "А",
      "hint": "Ліро-епос поєднує сюжет (епос) і віршовані переживання (лірика): поеми, балади, романи у віршах, співомовки.",
      "rule": "До ліро-епосу належать поеми («Мойсей» І. Франка, «Енеїда» І. Котляревського, «Кавказ», «Катерина»), балади («Ой летіла стріла», «Балада про соняшник»). А «Заповіт» і «Чари ночі» — чиста лірика; «Бджола та Шершень» — епос (байка); «Лісова пісня» — драма.",
      "solution": "Обидва твори ліро-епічні лише в рядку А: поеми «Мойсей» і «Енеїда».",
      "drill_key": "lit_genres"
    },
    {
      "id": "arch_lit_2024_28",
      "section": "Література XX ст.",
      "source": "Архів НМТ-2024 (1 сесія)",
      "qtype": "matching",
      "max_points": 4,
      "prompt": "Поєднайте назву твору (1–4) з його уривком (А–Д):",
      "left": [
        "1. «Моя автобіографія»",
        "2. «Зачарована Десна»",
        "3. «Я (Романтика)»",
        "4. «Майстер корабля»"
      ],
      "right": {
        "А": "«Але мати не спала. Вона підходить до мене... і каже, що я, її м’ятежний син, зовсім замучив себе...»",
        "Б": "«Мої спогади я присвячую молодим... Я не виходив кілька день з монтажної кімнати між рулонами плівки...»",
        "В": "«Померкло, стерлося все... Бо далекі Рудні гори скрізь ідуть за мною...»",
        "Г": "«Світ одкривається перед ясними очима перших літ пізнання... Сумно людині, коли висихає і сліпне уява...»",
        "Д": "«І от коли пригадаєш життя своє, то приходиш до висновку, що письменника супроводять явища незвичайні...»"
      },
      "answer": {
        "1": "Д",
        "2": "Г",
        "3": "А",
        "4": "Б"
      },
      "hint": "«М’ятежний син» — новела «Я (Романтика)»; «монтажна кімната, рулони плівки» — кінороман Яновського «Майстер корабля»; дитинство в «Зачарованій Десні».",
      "rule": "Маркери в цитатах: «м’ятежний син» → М. Хвильовий; кіноплівка й монтаж → Ю. Яновський; спогади про дитинство/Десну → О. Довженко; іронія про становлення письменника → Остап Вишня.",
      "solution": "1–Д, 2–Г, 3–А, 4–Б.",
      "drill_key": "lit_pseudonyms"
    },
    {
      "id": "arch_lit_2024_29",
      "section": "Теорія літератури та аналіз текстів",
      "source": "Архів НМТ-2024 (1 сесія)",
      "qtype": "matching",
      "max_points": 4,
      "prompt": "Узгодьте назви двох творів (1–4) та (А–Д), що належать до одного жанру:",
      "left": [
        "1. «Майстер корабля»",
        "2. «Я (Романтика)»",
        "3. «Моя автобіографія»",
        "4. «Захар Беркут»"
      ],
      "right": {
        "А": "«Сом»",
        "Б": "«Тіні забутих предків»",
        "В": "«Тигролови»",
        "Г": "«Мина Мазайло»",
        "Д": "«Модри Камень»"
      },
      "answer": {
        "1": "В",
        "2": "Д",
        "3": "А",
        "4": "Б"
      },
      "hint": "«Майстер корабля» і «Тигролови» — романи; «Моя автобіографія» і «Сом» — усмішки Остапа Вишні.",
      "rule": "Жанрові пари: роман («Майстер корабля» / «Тигролови»), новела («Я (Романтика)» / «Модри Камень»), усмішка («Моя автобіографія» / «Сом»), повість («Захар Беркут» / «Тіні забутих предків»).",
      "solution": "1–В, 2–Д, 3–А, 4–Б.",
      "drill_key": "lit_genres"
    }
  ],
  "biology": [
    {
      "id": "arch_bio_2025_2",
      "section": "Клітина. Хімічний склад і реалізація спадкової інформації",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "Позначте назву сполуки, яка належить до вуглеводів:",
      "options": [
        "фібриноген",
        "лізоцим",
        "глюкоза",
        "урацил"
      ],
      "labels": [
        "А",
        "Б",
        "В",
        "Г"
      ],
      "answer": "В",
      "hint": "Фібриноген і лізоцим — білки, урацил — нітратна основа (нуклеїнові кислоти).",
      "rule": "Глюкоза (C₆H₁₂O₆) — основний моносахарид, представник вуглеводів.",
      "solution": "До вуглеводів належить моносахарид глюкоза (В).",
      "drill_key": "bio_dna_percent"
    },
    {
      "id": "arch_bio_2025_4",
      "section": "Клітина. Хімічний склад і реалізація спадкової інформації",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "В умовах інтенсивної фізичної роботи кровоносна система не встигає повністю забезпечити надходження в м’язові клітини кисню. Проаналізуйте твердження:\nI. Енергетичні потреби забезпечено переважно гліколізом.\nII. М’язи виробляють у великих кількостях молочну кислоту, яка утворюється з піровиноградної кислоти.",
      "options": [
        "правильне лише I",
        "правильне лише II",
        "обидва правильні",
        "немає правильних"
      ],
      "labels": [
        "А",
        "Б",
        "В",
        "Г"
      ],
      "answer": "В",
      "hint": "За нестачі кисню (анаеробний режим) м’язи переходять на безкисневе розщеплення глюкози — гліколіз.",
      "rule": "Під час гліколізу (безкисневий етап) глюкоза розщеплюється до піровиноградної кислоти (пірувату), яка без O₂ перетворюється на молочну кислоту (лактат).",
      "solution": "Обидва твердження правильні (В).",
      "drill_key": "bio_dna_deoxy"
    },
    {
      "id": "arch_bio_2025_5",
      "section": "Клітина. Хімічний склад і реалізація спадкової інформації",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "Який приклад є свідченням перетворення лейкопластів на хлоропласти?",
      "options": [
        "дозрівання томатів на сонці",
        "пожовтіння лимонів та мандаринів",
        "утворення білої м’якоті в полуниць",
        "позеленіння бульб картоплі на сонці"
      ],
      "labels": [
        "А",
        "Б",
        "В",
        "Г"
      ],
      "answer": "Г",
      "hint": "У бульбах картоплі крохмаль запасається в безбарвних лейкопластах. Що відбувається на світлі?",
      "rule": "Лейкопласти (безбарвні пластиди, що запасають крохмаль у бульбах картоплі) на світлі здатні перетворюватися на зелені хлоропласти. Почервоніння томатів або пожовтіння цитрусових — це перехід хлоропластів у хромопласти.",
      "solution": "Позеленіння бульб картоплі на сонці (Г) — класичний приклад перетворення лейкопластів на хлоропласти.",
      "drill_key": "bio_dna_percent"
    },
    {
      "id": "arch_bio_2025_12",
      "section": "Біорізноманіття",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "Науковці вивчали особливості клітин організму й визначили, що він належить до грибів. Такого висновку дійшли, бо:",
      "options": [
        "клітини здатні до мітотичного поділу",
        "клітинна стінка містить хітин",
        "складником клітини є ядро",
        "клітини не мають хлоропластів"
      ],
      "labels": [
        "А",
        "Б",
        "В",
        "Г"
      ],
      "answer": "Б",
      "hint": "Мітоз, ядро та відсутність хлоропластів є також у тварин і деяких протистів. Який полісахарид унікальний для клітинної стінки грибів?",
      "rule": "Характерна ознака клітин грибів — наявність клітинної стінки з хітину (у рослин — целюлоза, у бактерій — муреїн, у тварин стінки немає).",
      "solution": "Наявність хітину в клітинній стінці однозначно вказує на гриби (Б).",
      "drill_key": "bio_dna_percent"
    },
    {
      "id": "arch_bio_2025_17",
      "section": "Організм людини як біологічна система",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "Унаслідок потрапляння крапель води в гортань людина починає кашляти. Цю рефлекторну відповідь забезпечує центр, який міститься в:",
      "options": [
        "мозочку",
        "довгастому мозку",
        "середньому мозку",
        "проміжному мозку"
      ],
      "labels": [
        "А",
        "Б",
        "В",
        "Г"
      ],
      "answer": "Б",
      "hint": "Захисні рефлекси (кашель, чхання, блювання), а також дихальний і судиноруховий центри розташовані в найнижчому відділі головного мозку.",
      "rule": "Довгастий мозок містить центри дихання, серцебиття й захисних рефлексів (кашель, чхання, мигання, ковтання).",
      "solution": "Центр кашльового рефлексу розташований у довгастому мозку (Б).",
      "drill_key": "bio_dna_deoxy"
    },
    {
      "id": "arch_bio_2025_25",
      "section": "Клітина. Хімічний склад і реалізація спадкової інформації",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "matching",
      "max_points": 4,
      "prompt": "Поєднайте назву білка (1–4) зі складником організму людини (А–Д), у якому цей білок міститься у великій кількості:",
      "left": [
        "1. гемоглобін",
        "2. амілаза",
        "3. пепсин",
        "4. актин"
      ],
      "right": {
        "А": "шлунковий сік",
        "Б": "секрет слинних залоз",
        "В": "цитоплазма еритроцитів",
        "Г": "пухка сполучна тканина",
        "Д": "цитоплазма м’язових волокон"
      },
      "answer": {
        "1": "В",
        "2": "Б",
        "3": "А",
        "4": "Д"
      },
      "hint": "Гемоглобін переносить кисень у крові (еритроцити); амілаза розщеплює крохмаль уже в роті (слина); пепсин працює в шлунку; актин — скоротливий білок м’язів.",
      "rule": "Функції білків: гемоглобін (еритроцити), амілаза (слина/підшлункова), пепсин (шлунковий сік), актин і міозин (м’язові волокна), колаген (сполучна тканина).",
      "solution": "1–В, 2–Б, 3–А, 4–Д.",
      "drill_key": "bio_dna_percent"
    },
    {
      "id": "arch_bio_2025_27",
      "section": "Біорізноманіття",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "matching",
      "max_points": 4,
      "prompt": "Поєднайте особливості будови хребетних тварин (1–4) з твариною (А–Д), для якої вони характерні:",
      "left": [
        "1. Має зуби, але не має кіля на груднині",
        "2. Не має зубів, але на груднині є кіль",
        "3. Має ребра, але не має груднини",
        "4. Має груднину, але не має ребер"
      ],
      "right": {
        "А": "страус африканський",
        "Б": "ворона сіра",
        "В": "жаба озерна",
        "Г": "окунь річковий",
        "Д": "їжак вухатий"
      },
      "answer": {
        "1": "Д",
        "2": "Б",
        "3": "Г",
        "4": "В"
      },
      "hint": "У безхвостих амфібій (жаба) немає ребер; у риб (окунь) немає груднини; у літаючих птахів (ворона) на груднині є кіль; у ссавців (їжак) є зуби, але немає кіля.",
      "rule": "Еволюція скелета: риби (ребра є, груднини немає) → амфібії (груднина є, ребер немає) → птахи з кілем (літаючі: ворона; без кіля: страус) → ссавці (зуби диференційовані, кіля немає).",
      "solution": "1–Д (їжак), 2–Б (ворона), 3–Г (окунь), 4–В (жаба).",
      "drill_key": "bio_dna_deoxy"
    }
  ],
  "physics": [
    {
      "id": "arch_phys_2025_1",
      "section": "Механіка",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "Початкова координата тіла, що рухається вздовж осі Ox, дорівнює 10 м, прискорення становить 5 м/с², а початкова швидкість руху дорівнює 2,5 м/с. Яке рівняння описує рух тіла (в одиницях SI)?",
      "options": [
        "x = 10 + 2,5t + 2,5t²",
        "x = 5 + 10t − 2,5t²",
        "x = 2,5 + 10t + 5t²",
        "x = 10 + 5t − 5t²"
      ],
      "labels": [
        "А",
        "Б",
        "В",
        "Г"
      ],
      "answer": "А",
      "hint": "У формулі координати x = x₀ + v₀t + (a·t²)/2 прискорення ділиться НАВПІЛ!",
      "rule": "Рівняння рівноприскореного руху: x(t) = x₀ + v₀ₓt + (aₓ/2)·t². Часто забувають поділити прискорення на 2!",
      "solution": "x₀ = 10, v₀ = 2,5, a/2 = 5/2 = 2,5 ⇒ x = 10 + 2,5t + 2,5t² (А).",
      "drill_key": "phys_free_fall"
    },
    {
      "id": "arch_phys_2025_5",
      "section": "Молекулярна фізика та термодинаміка",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "Унаслідок адіабатного стискання поршнем газу в циліндрі внутрішня енергія газу змінилася на 50 Дж. Чи відбувся теплообмін, і яке значення роботи A, яку виконує ГАЗ під час стискання?",
      "options": [
        "теплообміну немає; A = 50 Дж",
        "теплообмін є; A = −50 Дж",
        "теплообмін є; A = 50 Дж",
        "теплообміну немає; A = −50 Дж"
      ],
      "labels": [
        "А",
        "Б",
        "В",
        "Г"
      ],
      "answer": "Г",
      "hint": "Адіабатний процес — без теплообміну (Q = 0). Під час СТИСКАННЯ об’єм зменшується, отже сам ГАЗ виконує ВІД’ЄМНУ роботу!",
      "rule": "I закон термодинаміки: Q = ΔU + A. Для адіабатного процесу Q = 0 ⇒ A = −ΔU. Під час стискання робота газу A < 0 (робота зовнішніх сил > 0).",
      "solution": "Оскільки процес адіабатний, Q = 0 (теплообміну немає), і A = −ΔU = −50 Дж (Г).",
      "drill_key": "phys_thermo_1law"
    },
    {
      "id": "arch_phys_2025_7",
      "section": "Електродинаміка",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "Електронагрівальний пристрій, увімкнений у мережу зі сталою напругою, споживає певну потужність. Якщо спіраль пристрою вкоротити й увімкнути його в цю ж мережу, то спожита потужність буде:",
      "options": [
        "більшою, оскільки опір зменшиться",
        "меншою, оскільки опір збільшиться",
        "меншою, оскільки опір зменшиться",
        "більшою, оскільки опір збільшиться"
      ],
      "labels": [
        "А",
        "Б",
        "В",
        "Г"
      ],
      "answer": "А",
      "hint": "Мережа має СТАЛУ напругу U = const, тому обирай формулу потужності P = U² / R!",
      "rule": "Опір R = ρ·l/S прямо пропорційний довжині l: вкоротили спіраль → R зменшився. При U = const потужність P = U²/R зростає!",
      "solution": "Довжина менша → опір менший → за формулою P = U²/R потужність стане більшою (А).",
      "drill_key": "phys_incline"
    },
    {
      "id": "arch_phys_2025_12",
      "section": "Квантова фізика та теорія відносності",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "Ядро нукліда Нітрогену ¹⁴₇N поглинуло β-частинку (електрон ⁰₋₁e). Унаслідок цієї реакції ядро втратило протон (¹₁p) й утворилося ядро атома елемента X. Позначте порядковий номер елемента X:",
      "options": [
        "5",
        "6",
        "10",
        "12"
      ],
      "labels": [
        "А",
        "Б",
        "В",
        "Г"
      ],
      "answer": "А",
      "hint": "Закон збереження заряду (нижні індекси): 7 + (−1) = Z_X + 1.",
      "rule": "У ядерній реакції сума нижніх індексів (зарядове число Z = порядковий номер) і сума верхніх індексів (масове число A) ліворуч і праворуч рівні.",
      "solution": "¹⁴₇N + ⁰₋₁e → ¹³_Z X + ¹₁p. За нижніми індексами: 7 − 1 = Z + 1 ⇒ Z = 5 (А).",
      "drill_key": "phys_halflife"
    },
    {
      "id": "arch_phys_2025_14",
      "section": "Електродинаміка",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "matching",
      "max_points": 3,
      "prompt": "Установіть відповідність між фізичним терміном (1–4) і середовищем (А–Д), протікання струму в якому він характеризує:",
      "left": [
        "1. p–n перехід",
        "2. іскровий розряд",
        "3. надпровідність",
        "4. гальванопластика"
      ],
      "right": {
        "А": "метали",
        "Б": "напівпровідники",
        "В": "вакуум",
        "Г": "гази",
        "Д": "електроліти"
      },
      "answer": {
        "1": "Б",
        "2": "Г",
        "3": "А",
        "4": "Д"
      },
      "hint": "p–n перехід — це напівпровідники (діоди); іскра (блискавка) — газ; нульовий опір при охолодженні — метали; електролітичне копіювання — електроліти.",
      "rule": "Ключові явища за середовищами: метали (надпровідність), напівпровідники (p–n перехід), гази (іскровий/коронний/тліючий розряди), електроліти (електроліз, гальванопластика).",
      "solution": "1–Б, 2–Г, 3–А, 4–Д.",
      "drill_key": "phys_humidity"
    },
    {
      "id": "arch_phys_2025_15",
      "section": "Механіка",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "short",
      "max_points": 2,
      "prompt": "Барабан пральної машини робить 900 обертів за хвилину. Визначте частоту його обертання (у с⁻¹).",
      "answer": "15",
      "hint": "Переведи 1 хвилину в секунди (60 с) і поділи кількість обертів N на час t!",
      "rule": "Частота обертання n = N / t [об/с = с⁻¹].",
      "solution": "n = 900 / 60 с = 15 с⁻¹.",
      "drill_key": "phys_free_fall"
    },
    {
      "id": "arch_phys_2025_17",
      "section": "Молекулярна фізика та термодинаміка",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "short",
      "max_points": 2,
      "prompt": "Гумова нитка площею перерізу 1,5 мм² і завдовжки 60 см під дією тягарця масою 100 г видовжилася на 2 см. Обчисліть модуль Юнга для гуми (у МПа). Уважайте g = 10 м/с².",
      "answer": "20",
      "hint": "Переведи все в систему СІ: m = 0,1 кг, S = 1,5 · 10⁻⁶ м², l₀ = 0,6 м, Δl = 0,02 м. Використай закон Гука σ = E·ε ⇒ E = (F·l₀) / (S·Δl).",
      "rule": "Модуль Юнга E = F·l₀ / (S·Δl), де F = mg. Наприкінці переведи Па у МПа (поділи на 10⁶).",
      "solution": "E = (0,1 · 10 · 0,6) / (1,5·10⁻⁶ · 0,02) = 0,6 / (3·10⁻⁸) = 20·10⁶ Па = 20 МПа.",
      "drill_key": "phys_humidity"
    },
    {
      "id": "arch_phys_2025_20",
      "section": "Квантова фізика та теорія відносності",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "short",
      "max_points": 2,
      "prompt": "Унаслідок випускання електромагнітного випромінювання маса зорі зменшилася на 4 мкг. Визначте енергію випромінювання (у МДж). Швидкість світла c = 3·10⁸ м/с.",
      "answer": "360",
      "hint": "Формула Ейнштейна ΔE = Δm · c². Увага: 1 мкг = 10⁻⁶ г = 10⁻⁹ кг!",
      "rule": "У СІ масу переводимо в кілограми: 1 мкг = 10⁻⁹ кг. 1 МДж = 10⁶ Дж.",
      "solution": "ΔE = 4·10⁻⁹ · (3·10⁸)² = 4·10⁻⁹ · 9·10¹⁶ = 36·10⁷ Дж = 360·10⁶ Дж = 360 МДж.",
      "drill_key": "phys_halflife"
    }
  ],
  "chemistry": [
    {
      "id": "arch_chem_2025_1",
      "section": "Загальна хімія",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "До хімічних явищ належить:",
      "options": [
        "подрібнення крейди",
        "бродіння яблучного соку",
        "тверднення розплавленого парафіну",
        "розшарування струшеної суміші води й олії"
      ],
      "labels": [
        "А",
        "Б",
        "В",
        "Г"
      ],
      "answer": "Б",
      "hint": "У хімічному явищі утворюються НОВІ речовини (змінюється склад, смак, виділяється газ).",
      "rule": "Подрібнення, плавлення/тверднення й розшарування сумішей — фізичні явища. Бродіння — біохімічна реакція перетворення цукрів на спирт і CO₂.",
      "solution": "Хімічним явищем є бродіння яблучного соку (Б).",
      "drill_key": "chem_gas_molar"
    },
    {
      "id": "arch_chem_2025_4",
      "section": "Загальна хімія",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "У йонах ClO⁻ і ClO₃⁻ ступені окиснення Хлору дорівнюють відповідно:",
      "options": [
        "−1 і +3",
        "+1 і +3",
        "−1 і +5",
        "+1 і +5"
      ],
      "labels": [
        "А",
        "Б",
        "В",
        "Г"
      ],
      "answer": "Г",
      "hint": "У складному йоні сума ступенів окиснення всіх атомів дорівнює ЗАРЯДУ йона (−1), а в Оксигену ступінь окиснення −2!",
      "rule": "Для йона ClOₓ⁻: x(Cl) + k·(−2) = −1.",
      "solution": "Для ClO⁻: x − 2 = −1 ⇒ x = +1. Для ClO₃⁻: x + 3·(−2) = −1 ⇒ x = +5. Відповідь: +1 і +5 (Г).",
      "drill_key": "chem_alkane_combust"
    },
    {
      "id": "arch_chem_2025_13",
      "section": "Неорганічна хімія",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "Позначте формулу солі, унаслідок повного термічного розкладання якої НЕ утвориться твердий залишок:",
      "options": [
        "BaCO₃",
        "NaHCO₃",
        "NH₄HCO₃",
        "MgCO₃"
      ],
      "labels": [
        "А",
        "Б",
        "В",
        "Г"
      ],
      "answer": "В",
      "hint": "Солі амонію (NH₄⁺) зі слабкими леткими кислотами розкладаються лише на гази й воду!",
      "rule": "NH₄HCO₃ → NH₃↑ + CO₂↑ + H₂O↑ — усі продукти леткі, твердого залишку немає. Інші карбонати/гідрокарбонати металів дають тверді оксиди (BaO, MgO) або карбонат (Na₂CO₃).",
      "solution": "Під час розкладання NH₄HCO₃ твердий залишок не утворюється (В).",
      "drill_key": "chem_solution_sat"
    },
    {
      "id": "arch_chem_2025_16",
      "section": "Органічна хімія",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "Термічне розкладання вуглеводню описано хімічним рівнянням: C₁₂H₂₆ = C₆H₁₄ + X. Речовина X — це:",
      "options": [
        "алкан",
        "алкен",
        "алкін",
        "арен"
      ],
      "labels": [
        "А",
        "Б",
        "В",
        "Г"
      ],
      "answer": "Б",
      "hint": "Порахуй кількість атомів C і H, яких бракує в правій частині рівняння (12 − 6 і 26 − 14)!",
      "rule": "Під час крекінгу (термічного розкладання) алкану завжди утворюється менший алкан (CₙH₂ₙ₊₂) та алкен (CₘH₂ₘ).",
      "solution": "X = C₁₂₋₆H₂₆₋₁₄ = C₆H₁₂ — загальна формула CₙH₂ₙ, це алкен (Б).",
      "drill_key": "chem_alkane_combust"
    },
    {
      "id": "arch_chem_2025_23",
      "section": "Органічна хімія",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "matching",
      "max_points": 3,
      "prompt": "Доберіть до реакції (1–3) назву її продукту (А–Д):",
      "left": [
        "1. естерифікації",
        "2. гідратації алкену",
        "3. бродіння глюкози"
      ],
      "right": {
        "А": "молочна кислота",
        "Б": "метилетаноат",
        "В": "гексан-3-ол",
        "Г": "гліцерол",
        "Д": "гексан"
      },
      "answer": {
        "1": "Б",
        "2": "В",
        "3": "А"
      },
      "hint": "Естерифікація дає естер (-оат); гідратація (+H₂O) алкену дає спирт (-ол); молочнокисле бродіння глюкози — молочну кислоту.",
      "rule": "Типи органічних реакцій: кислота + спирт → естер (метилетаноат); алкен + H₂O → спирт (гексан-3-ол); бродіння глюкози → етанол або молочна кислота.",
      "solution": "1–Б, 2–В, 3–А.",
      "drill_key": "chem_yield"
    },
    {
      "id": "arch_chem_2025_25",
      "section": "Обчислення в хімії",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "short",
      "max_points": 2,
      "prompt": "Молярна маса вуглеводню дорівнює 28 г/моль. Скільки атомів Карбону в його молекулі?",
      "answer": "2",
      "hint": "Поділи 28 на атомну масу Карбону (12), щоб оцінити число атомів C: 12·2 = 24, залишається 4 на Гідроген!",
      "rule": "M(CₓHᵧ) = 12x + y = 28. При x = 2: 24 + y = 28 ⇒ y = 4 ⇒ C₂H₄ (етен).",
      "solution": "Формула C₂H₄ (M = 2·12 + 4 = 28 г/моль), отже атомів Карбону 2.",
      "drill_key": "chem_gas_molar"
    },
    {
      "id": "arch_chem_2025_26",
      "section": "Обчислення в хімії",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "short",
      "max_points": 2,
      "prompt": "Обчисліть масу (г) кальцій оксиду, який утворився внаслідок повного розкладання кальцій карбонату масою 25 г.",
      "answer": "14",
      "hint": "CaCO₃ → CaO + CO₂↑. Молярна маса CaCO₃ = 100 г/моль, CaO = 56 г/моль.",
      "rule": "Знаходимо кількість речовини n = m / M, за рівнянням n(CaO) = n(CaCO₃), потім m(CaO) = n · M(CaO).",
      "solution": "n(CaCO₃) = 25 / 100 = 0,25 моль = n(CaO). m(CaO) = 0,25 · 56 = 14 г.",
      "drill_key": "chem_yield"
    },
    {
      "id": "arch_chem_2025_27",
      "section": "Обчислення в хімії",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "short",
      "max_points": 2,
      "prompt": "Формалін — це водний розчин, масова частка метаналю (CH₂O) в якому 40 %. Обчисліть масу (г) формаліну, який можна виготовити, розчинивши у воді метаналь об’ємом 4,48 л (н. у.).",
      "answer": "15",
      "hint": "1) n(CH₂O) = 4,48 / 22,4 = 0,2 моль; 2) M(CH₂O) = 12 + 2 + 16 = 30 г/моль; 3) m_р-ну = m_реч / w.",
      "rule": "Об’єм газу за н. у.: n = V / 22,4. Маса розчину: m(розчину) = m(речовини) / w (у частках одиниці: 0,4).",
      "solution": "n = 4,48 / 22,4 = 0,2 моль; m(CH₂O) = 0,2 · 30 = 6 г; m(формаліну) = 6 / 0,4 = 15 г.",
      "drill_key": "chem_solution_sat"
    }
  ],
  "geography": [
    {
      "id": "arch_geo_2025_1",
      "section": "Загальна географія та топографія",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "Яке значення першої навколосвітньої подорожі під керівництвом Фернана Магеллана?",
      "options": [
        "створено першу географічну карту світу",
        "визначено площі суходолу й Океану",
        "винайдено умовну фігуру Землі – геоїд",
        "доведено, що Земля має форму кулі"
      ],
      "labels": [
        "А",
        "Б",
        "В",
        "Г"
      ],
      "answer": "Г",
      "hint": "Саме навколосвітнє плавання вперше практично довело кулястість нашої планети.",
      "rule": "Експедиція Ф. Магеллана (1519–1522) довела, що Земля має кулясту форму і Світовий океан єдиний.",
      "solution": "Правильна відповідь Г: доведено, що Земля має форму кулі.",
      "drill_key": "geo_ukr_extremes"
    },
    {
      "id": "arch_geo_2025_5",
      "section": "Україна і світове господарство. Регіони",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "Відомий економіст Джеффрі Сакс стверджував, що країни, які не мають виходу до моря, ніколи не досягнуть високого рівня економічного розвитку. Географи для спростування цієї думки наводять приклад:",
      "options": [
        "Китаю",
        "Казахстану",
        "Німеччини",
        "Швейцарії"
      ],
      "labels": [
        "А",
        "Б",
        "В",
        "Г"
      ],
      "answer": "Г",
      "hint": "Потрібна високорозвинена країна (член європейської економічної еліти), яка НЕ має виходу до моря.",
      "rule": "Китай і Німеччина мають вихід до морів; Казахстан — перехідна економіка; Швейцарія (як і Австрія, Люксембург) — внутрішньоконтинентальна високорозвинена країна.",
      "solution": "Спростовує тезу приклад високорозвиненої внутрішньоконтинентальної Швейцарії (Г).",
      "drill_key": "geo_ukr_extremes"
    },
    {
      "id": "arch_geo_2025_17",
      "section": "Україна і світове господарство. Регіони",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "single",
      "max_points": 1,
      "prompt": "Прочитайте прогноз аналітика ринку цукру в Україні: «Залишаться лише найефективніші цукрові заводи... На ринку з 30 заводів, які нині працюють, залишиться 18–20, але потужніших». Про яку форму суспільної організації виробництва йдеться?",
      "options": [
        "спеціалізацію",
        "кооперування",
        "концентрацію",
        "комбінування"
      ],
      "labels": [
        "А",
        "Б",
        "В",
        "Г"
      ],
      "answer": "В",
      "hint": "Підприємств стає менше, але кожне з них — більше й потужніше (зосередження виробництва).",
      "rule": "Концентрація — зосередження виробництва на дедалі більших підприємствах. Спеціалізація — випуск однорідної продукції; кооперування — зв’язки між суміжниками; комбінування — різні виробництва на одному комбінаті.",
      "solution": "Укрупнення заводів — це концентрація (В).",
      "drill_key": "geo_ukr_extremes"
    },
    {
      "id": "arch_geo_2025_22",
      "section": "Загальна географія та топографія",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "short",
      "max_points": 2,
      "prompt": "На яку висоту (м) потрібно піднімати воду, якщо прокласти водогін від річки (абсолютна висота урізу води 111,4 м) до виробничого майданчика (абсолютна висота верхньої точки траси 191,4 м)?",
      "answer": "80",
      "hint": "Висота підйому — це відносна висота (різниця між абсолютною висотою верхньої та нижньої точок).",
      "rule": "Відносна висота Δh = H_верх − H_низ.",
      "solution": "191,4 − 111,4 = 80 м.",
      "drill_key": "geo_map_scale"
    },
    {
      "id": "arch_geo_2025_23",
      "section": "Загальна географія та топографія",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "short",
      "max_points": 2,
      "prompt": "Визначте довжину (м) проєктної ділянки водогону, якщо на топографічній карті масштабу 1 : 20 000 ця відстань становить 7 см.",
      "answer": "1400",
      "hint": "У масштабі 1 : 20 000 відкидаємо два нулі → 1 см на карті = 200 м на місцевості!",
      "rule": "Щоб перевести числовий масштаб у метри (в 1 см), закресліть два останні нулі: 1 : 20 000 → в 1 см 200 м.",
      "solution": "7 см · 200 м/см = 1400 м.",
      "drill_key": "geo_map_scale"
    },
    {
      "id": "arch_geo_2025_24",
      "section": "Загальна географія та топографія",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "short",
      "max_points": 2,
      "prompt": "Визначте азимут (у градусах), яким прокладатимуть трасу водогону, якщо за проєктом вона зорієнтована чітко на схід.",
      "answer": "90",
      "hint": "Північ = 0°, Схід = 90°, Південь = 180°, Захід = 270°.",
      "rule": "Азимут відлічується за годинниковою стрілкою від напрямку на північ (0°): схід відповідає рівно 90°.",
      "solution": "Напрямок чітко на схід — азимут 90°.",
      "drill_key": "geo_azimuth"
    },
    {
      "id": "arch_geo_2025_25",
      "section": "Фізична географія України",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "multi3",
      "max_points": 3,
      "prompt": "Родина переїхала з Луганщини в село поблизу Трускавця (Львівська область). Що правильно схарактеризувало відмінності клімату й погоди на Львівщині? (Оберіть 3 відповіді)",
      "items": {
        "1": "більша тривалість світлового дня",
        "2": "пізніше сходить і заходить сонце",
        "3": "вища температура повітря протягом доби",
        "4": "менш тривала спека",
        "5": "вища вологість повітря",
        "6": "менше днів з дощами й мрякою",
        "7": "частіше дошкуляють суховії"
      },
      "answer": [
        "2",
        "4",
        "5"
      ],
      "hint": "Львівська область значно західніше за Луганщину (Земля обертається із заходу на схід!) і ближче до Карпат/Атлантики (вологіше та прохолодніше влітку).",
      "rule": "Що західніше регіон України, то пізніше схід/захід Сонця (2). На заході України вища вологість (5) і м’якша/коротша літня спека (4), ніж у степах сходу.",
      "solution": "Правильні твердження: 2, 4, 5.",
      "drill_key": "geo_ukr_extremes"
    },
    {
      "id": "arch_geo_2025_30",
      "section": "Україна і світове господарство. Регіони",
      "source": "Архів НМТ-2025 (1 сесія)",
      "qtype": "multi3",
      "max_points": 3,
      "prompt": "Позначте відмінності Великої Британії від Італії (Оберіть 3 відповіді):",
      "items": {
        "1": "півострівне географічне положення",
        "2": "країна Великої сімки",
        "3": "забезпеченість власними ресурсами нафти й природного газу",
        "4": "велика частка емігрантів із країн Співдружності",
        "5": "високий рівень урбанізованості території",
        "6": "домінування третинного сектору в структурі економіки",
        "7": "гіперконцентрація виробництва в столичній агломерації"
      },
      "answer": [
        "3",
        "4",
        "7"
      ],
      "hint": "Виключи спільні риси (обидві в G7, обидві високоурбанізовані, в обох домінує сфера послуг) та ознаки Італії (півострів — це Італія, а Британія — острів!).",
      "rule": "Відмінності Великої Британії: видобуток нафти й газу на шельфі Північного моря (3), іммігранти з країн Співдружності (4), гіперконцентрація в Лондоні (7 — тоді як в Італії головний промисловий пояс на півночі: Мілан–Турин–Генуя).",
      "solution": "Правильні відмінності: 3, 4, 7.",
      "drill_key": "geo_ukr_extremes"
    }
  ]
}

for _sid, _items in ARCHIVE_2022_2025.items():
    for _item in _items:
        _item_copy = dict(_item)
        _item_copy["subject"] = _sid
        BANK_QUESTIONS.setdefault(_sid, []).append(_item_copy)

SUBJECT_GENERATORS = {
    "ukrmova": ["ukrmova_pref_zs", "ukrmova_nagolos", "ukrmova_double", "ukrmova_myak", "ukrmova_rodovyi"],
    "math": ["math_ineq", "math_percent_trip", "math_prob", "math_trap_angle", "math_exp_eq", "math_deriv_ext", "math_vector", "math_module_pow"],
    "history": ["hist_dates_20c", "hist_chrono_17c", "hist_terms_19c"],
    "english": ["eng_verb_agreement", "eng_passive_past", "eng_connectors_whether", "eng_vocab_context", "eng_reading_ads"],
    "german": ["ger_gram_context"],
    "french": ["fr_gram_context"],
    "spanish": ["esp_gram_context"],
    "ukrlit": ["lit_pseudonyms", "lit_genres"],
    "biology": ["bio_dna_percent", "bio_dna_deoxy"],
    "physics": ["phys_free_fall", "phys_incline", "phys_thermo_1law", "phys_humidity", "phys_halflife"],
    "chemistry": ["chem_gas_molar", "chem_solution_sat", "chem_yield", "chem_alkane_combust"],
    "geography": ["geo_map_scale", "geo_azimuth", "geo_ukr_extremes"],
}

"""Рушій генерації тестів НМТ, перевірки відповідей, добору ідентичних прикладів та імпорту JSON."""


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
        # Підтримка латинсько-кириличної відповідності (A/А, B/В, C/С, E/Е)
        equiv = {"A": "А", "B": "В", "C": "С", "E": "Е", "K": "К", "M": "М", "O": "О", "P": "Р", "T": "Т", "X": "Х"}
        labels = [str(l).upper() for l in q.get("labels", [])]
        is_ok = (ans == corr) or (equiv.get(ans) == corr) or (equiv.get(corr) == ans)
        opts = q.get("options", [])

        def _fmt_opt(lbl):
            for l, o in zip(labels, opts):
                if l == lbl or equiv.get(l) == lbl or equiv.get(lbl) == l:
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
        equiv = {"A": "А", "B": "В", "C": "С", "E": "Е"}
        pts = 0
        u_parts, c_parts = [], []
        for k in sorted(corr_map.keys()):
            c_val = str(corr_map[k]).strip().upper()
            u_val = str(u_map.get(k, "")).strip().upper()
            if u_val == c_val or equiv.get(u_val) == c_val or equiv.get(c_val) == u_val:
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

    if dkey and dkey in DRILL_GENERATORS:
        gen_fn = DRILL_GENERATORS[dkey]
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
    gens = SUBJECT_GENERATORS.get(subj, [])
    if gens:
        gen_fn = DRILL_GENERATORS[random.choice(gens)]
        cand = gen_fn()
        cand["is_drill"] = True
        return cand

    pool = [item for item in BANK_QUESTIONS.get(subj, []) if item.get("prompt") != q.get("prompt")]
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
    static_pool = list(BANK_QUESTIONS.get(subject_id, []))
    random.shuffle(static_pool)
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
    gens = SUBJECT_GENERATORS.get(subject_id, [])
    attempts = 0
    while len(questions) < target_n and attempts < target_n * 8:
        attempts += 1
        if gens:
            gkey = gens[(len(questions) + attempts) % len(gens)]
            cand = DRILL_GENERATORS[gkey]()
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


def build_session_plan(selected_subjects, length_mode="quick", custom_bank=None):
    """Створює повний план тестування з усіх обраних користувачем предметів."""
    plan = []
    for subj_id in selected_subjects:
        qs = generate_test_for_subject(subj_id, length_mode=length_mode, custom_bank=custom_bank)
        plan.append({
            "subject": subj_id,
            "questions": qs,
            "answers": {},
            "points": {},
            "mistakes": [],
            "drills_done": 0,
        })
    return plan


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


def load_custom_json(filepath):
    """Завантажує користувацький банк завдань із JSON-файлу."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("JSON має бути об’єктом вигляду {'english': [...], 'math': [...]}.")
    validated = {}
    for subj_id, items in data.items():
        if subj_id not in SUBJECTS_CONFIG:
            continue
        if not isinstance(items, list):
            continue
        clean_list = []
        for idx, q in enumerate(items):
            if isinstance(q, dict) and "prompt" in q and "answer" in q and "qtype" in q:
                item = dict(q)
                item.setdefault("id", f"custom_{subj_id}_{idx+1}")
                item["subject"] = subj_id
                item.setdefault("section", "Користувацький банк")
                item.setdefault("source", "Завантажений файл користувача")
                item.setdefault("max_points", 1)
                item.setdefault("hint", "Уважно перечитай умову завдання.")
                item.setdefault("rule", "Пояснення не вказано у файлі користувача.")
                item.setdefault("solution", f"Правильна відповідь: {item['answer']}")
                clean_list.append(item)
        if clean_list:
            validated[subj_id] = clean_list
    return validated


def export_json_template(filepath):
    """Зберігає приклад відкритого JSON-банку, щоб користувач міг додавати тести 2022–2025 рр."""
    template = {
        "english": [
            {
                "id": "my_eng_2025_1",
                "section": "Use of English: Граматика",
                "source": "Архів НМТ-2025",
                "qtype": "single",
                "max_points": 1,
                "prompt": "She _______ in Kyiv since 2022.",
                "options": ["lives", "lived", "has lived", "is living"],
                "labels": ["A", "B", "C", "D"],
                "answer": "C",
                "hint": "Зверни увагу на маркер 'since 2022' (дія почалася в минулому й триває дотепер).",
                "rule": "Із прийменниками 'since' (з якогось моменту) та 'for' (протягом) для дії, що досі триває, вживається Present Perfect.",
                "solution": "Дія почалася у 2022 році й триває зараз → has lived (C).",
                "drill_key": "eng_passive_past",
            }
        ],
        "math": [
            {
                "id": "my_math_2025_1",
                "section": "Числа і вирази",
                "source": "Архів НМТ-2025",
                "qtype": "short",
                "max_points": 2,
                "prompt": "Товар коштував 500 грн. Після знижки 10 % його ціна стала дорівнювати (грн):",
                "answer": "450",
                "hint": "Знайди 90 % від 500.",
                "rule": "Ціна зі знижкою 10 % становить 0,9 від початкової ціни.",
                "solution": "500 · 0,9 = 450 грн.",
                "drill_key": "math_percent_trip",
            }
        ],
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(template, f, ensure_ascii=False, indent=2)


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



"""Багаторівнева система підказок (1..10) для будь-якого завдання НМТ (2022–2026)."""


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

"""Графічний інтерфейс (сучасний закруглений дизайн, плавна анімована прокрутка, 10-рівневі підказки, Сова-Репетитор) + CLI."""

try:
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
    from tkinter import font as tkfont
    HAS_TK = True
except Exception:
    tk = None
    ttk = None
    messagebox = None
    filedialog = None
    tkfont = None
    HAS_TK = False


def get_user_data_dir():
    base = os.path.join(os.path.expanduser("~"), "Documents", "NMT_Tutor")
    try:
        os.makedirs(base, exist_ok=True)
    except Exception:
        base = os.path.expanduser("~")
    return base


# ===========================================================================
# КОНСОЛЬНИЙ РЕЖИМ (CLI — резервний для термінала)
# ===========================================================================
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


# ===========================================================================
# КРОСПЛАТФОРМНИЙ СУЧАСНИЙ GUI (MACOS І WINDOWS)
# ПЛАВНА АНІМАЦІЯ ПРОКРУТКИ • 10 РІВНІВ ПІДКАЗОК • СОВА СОФІЯ
# ===========================================================================
if HAS_TK:
    PALETTE = {
        "bg": "#F3F5FC",
        "card": "#FFFFFF",
        "card_soft": "#F8FAFF",
        "shadow": "#E4E8F5",
        "nav": "#262F4D",
        "nav_accent": "#344068",
        "nav_fg": "#FFFFFF",
        "primary": "#5B6EF5",
        "primary_hover": "#485BE2",
        "accent": "#22A094",
        "accent_hover": "#19877C",
        "soft_indigo": "#EEF1FF",
        "soft_indigo_bd": "#C7D2FE",
        "soft_mint": "#ECFCF6",
        "soft_mint_bd": "#6EE7B7",
        "soft_amber": "#FFF9E6",
        "soft_amber_bd": "#FCD34D",
        "soft_rose": "#FFF1F2",
        "soft_rose_bd": "#FECDD3",
        "text": "#1E293B",
        "muted": "#64748B",
        "border": "#DCE2F2",
        "ok_bg": "#DCFCE7",
        "ok_fg": "#15803D",
        "err_bg": "#FEE2E2",
        "err_fg": "#B91C1C",
        "chip_req_bg": "#EDE9FE",
        "chip_req_fg": "#5B21B6",
        "chip_opt_bg": "#E0F2FE",
        "chip_opt_fg": "#0369A1",
        "scroll_track": "#EBF0FA",
        "scroll_thumb": "#B4C0E4",
        "scroll_thumb_hover": "#5B6EF5",
    }

    def _hand_cursor():
        return "pointinghand" if sys.platform == "darwin" else "hand2"

    def _pick_fonts(root):
        try:
            avail = set(tkfont.families(root))
        except Exception:
            avail = set()

        if sys.platform == "darwin":
            candidates = ["Avenir Next", "SF Pro Text", "Nunito", "Helvetica Neue", "Helvetica"]
        elif sys.platform.startswith("win"):
            candidates = ["Segoe UI Variable Text", "Segoe UI", "Trebuchet MS", "Calibri", "Arial"]
        else:
            candidates = ["DejaVu Sans", "Liberation Sans", "Ubuntu"]

        base = candidates[-1]
        for c in candidates:
            if c in avail:
                base = c
                break

        return {
            "family": base,
            "h1": (base, 17, "bold"),
            "h2": (base, 13, "bold"),
            "h3": (base, 11, "bold"),
            "body": (base, 11),
            "body_sm": (base, 10),
            "small": (base, 9),
            "bold": (base, 11, "bold"),
            "bold_sm": (base, 10, "bold"),
            "mono": ("Menlo" if sys.platform == "darwin" else "Consolas" if sys.platform.startswith("win") else "DejaVu Sans Mono", 10),
        }

    def draw_round_rect(canvas, x1, y1, x2, y2, r=16, fill="", outline="", width=1, tags=None):
        """Малює плавний прямокутник із закругленими кутами на tk.Canvas."""
        w = max(0, x2 - x1)
        h = max(0, y2 - y1)
        r = max(0, min(r, w / 2.0, h / 2.0))
        pts = [
            x1 + r, y1, x1 + r, y1,
            x2 - r, y1, x2 - r, y1,
            x2, y1, x2, y1 + r, x2, y1 + r,
            x2, y2 - r, x2, y2 - r, x2, y2,
            x2 - r, y2, x2 - r, y2,
            x1 + r, y2, x1 + r, y2, x1, y2,
            x1, y2 - r, x1, y2 - r,
            x1, y1 + r, x1, y1 + r, x1, y1,
        ]
        kw = {"smooth": True, "splinesteps": 24, "fill": fill if fill else ""}
        if outline and width > 0:
            kw["outline"] = outline
            kw["width"] = width
        else:
            kw["outline"] = ""
            kw["width"] = 0
        if tags:
            kw["tags"] = tags
        return canvas.create_polygon(pts, **kw)

    class SmoothScrollView(tk.Frame):
        """
        Плавна молодіжна область прокрутки для macOS:
        - 60fps cubic ease-out анімація без затримок на трекпаді;
        - додатковий нижній запас (bottom_pad), щоб завжди докручувалося до самого низу;
        - видимий закруглений скролбар-пігулка + підтримка PageUp/PageDown/Home/End.
        """

        _REGISTRY = []

        def __init__(self, parent, bg=PALETTE["card"], pad_right=6, bottom_pad=32):
            super().__init__(parent, bg=bg)
            self._bg = bg
            self._bottom_pad = bottom_pad
            self._start_frac = 0.0
            self._target_frac = 0.0
            self._current_frac = 0.0
            self._anim_start_t = 0.0
            self._anim_duration = 0.22
            self._anim_job = None
            self._sync_job = None
            self._hover_sb = False
            self._dragging = False
            self._scrolling_active = False
            self._drag_offset = 0.0
            self._thumb_coords = (0.0, 1.0)
            self._resize_listeners = []

            self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0)
            self.canvas.pack(side="left", fill="both", expand=True)

            self.sb_canvas = tk.Canvas(self, width=12, bg=bg, highlightthickness=0, bd=0, cursor=_hand_cursor())
            self.sb_canvas.pack(side="right", fill="y", padx=(pad_right, 0))

            self.inner = tk.Frame(self.canvas, bg=bg)
            self._win_id = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")

            self.inner.bind("<Configure>", self._schedule_sync)
            self.canvas.bind("<Configure>", self._on_canvas_configure)
            self.canvas.configure(yscrollcommand=self._on_yscroll)
            self.bind("<Map>", lambda _e: self._schedule_sync(delay=30))

            self.sb_canvas.bind("<Configure>", lambda _e: self._draw_scrollbar())
            self.sb_canvas.bind("<Enter>", lambda _e: self._set_sb_hover(True))
            self.sb_canvas.bind("<Leave>", lambda _e: self._set_sb_hover(False))
            self.sb_canvas.bind("<ButtonPress-1>", self._on_sb_press)
            self.sb_canvas.bind("<B1-Motion>", self._on_sb_drag)
            self.sb_canvas.bind("<ButtonRelease-1>", lambda _e: self._on_sb_release())

            SmoothScrollView._REGISTRY.append(self)
            self.bind("<Destroy>", self._on_destroy)

        def _on_destroy(self, e):
            if e.widget is self:
                if self._anim_job is not None:
                    try:
                        self.after_cancel(self._anim_job)
                    except Exception:
                        pass
                    self._anim_job = None
                if self._sync_job is not None:
                    try:
                        self.after_cancel(self._sync_job)
                    except Exception:
                        pass
                    self._sync_job = None
                if self in SmoothScrollView._REGISTRY:
                    SmoothScrollView._REGISTRY.remove(self)

        def register_width_listener(self, callback):
            self._resize_listeners.append(callback)

        def _schedule_sync(self, _e=None, delay=20):
            if self._sync_job is not None:
                return
            try:
                self._sync_job = self.after(delay, self._run_scheduled_sync)
            except Exception:
                self._sync_job = None

        def _run_scheduled_sync(self):
            self._sync_job = None
            self.sync_scrollregion()

        def _content_and_view_heights(self):
            try:
                cw = max(120, self.canvas.winfo_width())
                ch = max(1, self.canvas.winfo_height())
                if ch <= 2:
                    ch = max(1, self.canvas.winfo_reqheight())
                bbox = self.canvas.bbox("all")
                bbox_h = (bbox[3] - bbox[1]) if bbox else 0
                req_h = max(self.inner.winfo_reqheight(), bbox_h) + self._bottom_pad
                return cw, ch, max(ch, req_h)
            except Exception:
                return 300, 300, 300

        def sync_scrollregion(self):
            try:
                if not self.winfo_exists():
                    return
                self.inner.update_idletasks()
                cw, ch, total_h = self._content_and_view_heights()
                self.canvas.configure(scrollregion=(0, 0, cw, total_h))
                self._clamp_and_sync()
            except Exception:
                pass

        def _on_canvas_configure(self, e):
            try:
                w = max(120, e.width)
                self.canvas.itemconfig(self._win_id, width=w)
                for cb in list(self._resize_listeners):
                    try:
                        cb(w)
                    except Exception:
                        pass
                self._schedule_sync(delay=14)
            except Exception:
                pass

        def _max_top_frac(self):
            try:
                _, ch, total_h = self._content_and_view_heights()
                if total_h <= ch + 2:
                    return 0.0
                return max(0.0, min(1.0, (total_h - ch) / float(total_h)))
            except Exception:
                return 0.0

        def _clamp_and_sync(self):
            max_top = self._max_top_frac()
            if self._target_frac > max_top:
                self._target_frac = max_top
            if self._current_frac > max_top:
                self._current_frac = max_top
                try:
                    self.canvas.yview_moveto(self._current_frac)
                except Exception:
                    pass
            try:
                f0, f1 = self.canvas.yview()
                self._thumb_coords = (float(f0), float(f1))
            except Exception:
                pass
            self._draw_scrollbar()

        def _on_yscroll(self, first, last):
            try:
                self._thumb_coords = (float(first), float(last))
                if self._anim_job is None and not self._dragging:
                    self._current_frac = float(first)
                self._draw_scrollbar()
            except Exception:
                pass

        def _set_sb_hover(self, state):
            self._hover_sb = state
            self._draw_scrollbar()

        def _on_sb_release(self):
            self._dragging = False
            self._draw_scrollbar()

        def _draw_scrollbar(self):
            c = self.sb_canvas
            try:
                if not c.winfo_exists():
                    return
                c.delete("all")
                w = max(10, c.winfo_width())
                h = max(30, c.winfo_height())
                f0, f1 = self._thumb_coords
                if f1 - f0 >= 0.992:
                    return
                draw_round_rect(c, 2, 4, w - 2, h - 4, r=4, fill=PALETTE["scroll_track"], outline="")
                track_h = max(1, h - 8)
                y1 = 4 + f0 * track_h
                y2 = 4 + f1 * track_h
                if y2 - y1 < 30:
                    mid = (y1 + y2) / 2.0
                    y1 = max(4, mid - 15)
                    y2 = min(h - 4, y1 + 30)
                    if y2 - y1 < 30:
                        y1 = max(4, h - 4 - 30)
                active = self._hover_sb or self._dragging or self._scrolling_active
                thumb_col = PALETTE["scroll_thumb_hover"] if active else PALETTE["scroll_thumb"]
                pad_x = 1.5 if active else 2.2
                draw_round_rect(c, pad_x, y1, w - pad_x, y2, r=4.5, fill=thumb_col, outline="")
            except Exception:
                pass

        def _on_sb_press(self, e):
            self.sync_scrollregion()
            h = max(30, self.sb_canvas.winfo_height())
            track_h = max(1, h - 8)
            f0, f1 = self._thumb_coords
            y1 = 4 + f0 * track_h
            y2 = 4 + f1 * track_h
            self._dragging = True
            if y1 <= e.y <= y2:
                self._drag_offset = e.y - y1
            else:
                self._drag_offset = (y2 - y1) / 2.0
                self._move_thumb_to(e.y - self._drag_offset, smooth=True)

        def _on_sb_drag(self, e):
            if self._dragging:
                self._move_thumb_to(e.y - self._drag_offset, smooth=False)

        def _move_thumb_to(self, top_px, smooth=False):
            h = max(30, self.sb_canvas.winfo_height())
            track_h = max(1, h - 8)
            frac = max(0.0, min(self._max_top_frac(), (top_px - 4) / track_h))
            if smooth:
                self.smooth_scroll_to(frac)
            else:
                if self._anim_job is not None:
                    try:
                        self.after_cancel(self._anim_job)
                    except Exception:
                        pass
                    self._anim_job = None
                self._scrolling_active = False
                self._target_frac = frac
                self._current_frac = frac
                try:
                    self.canvas.yview_moveto(frac)
                except Exception:
                    pass
                self._draw_scrollbar()

        def scroll_by_pixels(self, delta_px):
            """Плавна анімована прокрутка (cubic ease-out) на задану кількість пікселів."""
            try:
                _, ch, total_h = self._content_and_view_heights()
                if total_h <= ch + 2:
                    return
                max_top = max(0.0, (total_h - ch) / float(total_h))
                delta_frac = float(delta_px) / float(total_h)
                new_target = max(0.0, min(max_top, self._target_frac + delta_frac))
                self.smooth_scroll_to(new_target, duration=0.18)
            except Exception:
                pass

        def smooth_scroll_to(self, target_frac, duration=0.26):
            max_top = self._max_top_frac()
            self._start_frac = self._current_frac
            self._target_frac = max(0.0, min(max_top, float(target_frac)))
            self._anim_start_t = time.monotonic()
            self._anim_duration = max(0.10, float(duration))
            self._scrolling_active = True
            if self._anim_job is None:
                self._animate_step()

        def scroll_to_top(self, immediate=False):
            if immediate:
                if self._anim_job is not None:
                    try:
                        self.after_cancel(self._anim_job)
                    except Exception:
                        pass
                    self._anim_job = None
                self._scrolling_active = False
                self._start_frac = 0.0
                self._target_frac = 0.0
                self._current_frac = 0.0
                try:
                    self.canvas.yview_moveto(0.0)
                except Exception:
                    pass
                self._draw_scrollbar()
            else:
                self.smooth_scroll_to(0.0)

        def scroll_to_bottom(self, delay_ms=60):
            def _go():
                try:
                    if not self.winfo_exists():
                        return
                    self.sync_scrollregion()
                    self.smooth_scroll_to(self._max_top_frac(), duration=0.32)
                except Exception:
                    pass
            self.after(delay_ms, _go)

        def _animate_step(self):
            self._anim_job = None
            try:
                if not self.winfo_exists():
                    return
                elapsed = time.monotonic() - self._anim_start_t
                t = min(1.0, elapsed / self._anim_duration)
                eased = 1.0 - ((1.0 - t) ** 3)
                self._current_frac = self._start_frac + (self._target_frac - self._start_frac) * eased
                self.canvas.yview_moveto(self._current_frac)
                self._draw_scrollbar()
                if t >= 1.0 or abs(self._target_frac - self._current_frac) < 0.0005:
                    self._current_frac = self._target_frac
                    self.canvas.yview_moveto(self._current_frac)
                    self._scrolling_active = False
                    self._draw_scrollbar()
                    return
                self._anim_job = self.after(16, self._animate_step)
            except Exception:
                self._scrolling_active = False
                self._anim_job = None

        @classmethod
        def install_global_wheel(cls, root):
            """Прив’язує колесо миші, трекпад macOS і клавіші прокрутки до активного SmoothScrollView."""
            def _find_scroll_view(widget):
                w = widget
                while w is not None:
                    if isinstance(w, SmoothScrollView):
                        return w
                    try:
                        pname = w.winfo_parent()
                        w = w.nametowidget(pname) if pname else None
                    except Exception:
                        break
                return None

            def _handle_wheel(event, fixed_dir=0):
                try:
                    target_w = root.winfo_containing(event.x_root, event.y_root) or event.widget
                except Exception:
                    target_w = getattr(event, "widget", None)
                sv = _find_scroll_view(target_w)
                if sv is None:
                    return
                if fixed_dir != 0:
                    sv.scroll_by_pixels(fixed_dir * 76)
                    return
                delta = getattr(event, "delta", 0)
                if delta == 0:
                    return
                if sys.platform == "darwin":
                    px = max(-160, min(160, -delta * 18))
                else:
                    px = -(delta / 120.0) * 84
                sv.scroll_by_pixels(px)

            def _handle_key(direction):
                try:
                    fw = root.focus_get()
                    if isinstance(fw, (tk.Entry, tk.Text, ttk.Entry, ttk.Combobox)):
                        return
                    x, y = root.winfo_pointerxy()
                    target_w = root.winfo_containing(x, y) or fw
                except Exception:
                    target_w = None
                sv = _find_scroll_view(target_w)
                if sv is None and cls._REGISTRY:
                    sv = cls._REGISTRY[-1]
                if sv is None:
                    return
                if direction == "end":
                    sv.scroll_to_bottom(delay_ms=10)
                elif direction == "home":
                    sv.scroll_to_top()
                else:
                    sv.scroll_by_pixels(direction)

            root.bind_all("<MouseWheel>", lambda e: _handle_wheel(e, 0))
            root.bind_all("<Button-4>", lambda e: _handle_wheel(e, -1))
            root.bind_all("<Button-5>", lambda e: _handle_wheel(e, 1))
            root.bind_all("<Prior>", lambda _e: _handle_key(-240))
            root.bind_all("<Next>", lambda _e: _handle_key(240))
            root.bind_all("<End>", lambda _e: _handle_key("end"))
            root.bind_all("<Home>", lambda _e: _handle_key("home"))

    class RoundedButton(tk.Canvas):
        """Кнопка-пігулка із закругленими кутами, hover-ефектом та м’якою рамкою."""

        def __init__(
            self,
            parent,
            text,
            command=None,
            bg=PALETTE["primary"],
            hover_bg=PALETTE["primary_hover"],
            fg="#FFFFFF",
            border_color="",
            font=None,
            radius=16,
            height=38,
            min_width=110,
            pad_x=18,
            parent_bg=PALETTE["card"],
            state="normal",
        ):
            self._text = text
            self._command = command
            self._bg = bg
            self._hover_bg = hover_bg
            self._fg = fg
            self._border = border_color
            self._font = font or ("Helvetica", 11, "bold")
            self._radius = radius
            self._height = height
            self._pad_x = pad_x
            self._state = state
            self._hover = False
            self._parent_bg = parent_bg

            try:
                f_obj = tkfont.Font(font=self._font)
                tw = f_obj.measure(self._text)
            except Exception:
                tw = len(self._text) * 8
            self._min_w = max(min_width, tw + 2 * pad_x)

            super().__init__(
                parent,
                width=self._min_w,
                height=height + 2,
                bg=parent_bg,
                highlightthickness=0,
                bd=0,
                cursor=_hand_cursor() if state == "normal" else "arrow",
            )
            self.bind("<Configure>", lambda _e: self._redraw())
            self.bind("<Enter>", self._on_enter)
            self.bind("<Leave>", self._on_leave)
            self.bind("<ButtonRelease-1>", self._on_click)
            self._redraw()

        def set_state(self, state):
            self._state = state
            self.configure(cursor=_hand_cursor() if state == "normal" else "arrow")
            self._redraw()

        def set_text(self, text):
            self._text = text
            try:
                f_obj = tkfont.Font(font=self._font)
                tw = f_obj.measure(self._text)
                self._min_w = max(self._min_w, tw + 2 * self._pad_x)
                self.configure(width=self._min_w)
            except Exception:
                pass
            self._redraw()

        def set_colors(self, bg=None, hover_bg=None, fg=None, border_color=None):
            if bg is not None:
                self._bg = bg
            if hover_bg is not None:
                self._hover_bg = hover_bg
            if fg is not None:
                self._fg = fg
            if border_color is not None:
                self._border = border_color
            self._redraw()

        def _on_enter(self, _e):
            if self._state == "normal":
                self._hover = True
                self._redraw()

        def _on_leave(self, _e):
            self._hover = False
            self._redraw()

        def _on_click(self, e):
            if self._state != "normal" or not self._command:
                return
            if 0 <= e.x <= self.winfo_width() and 0 <= e.y <= self.winfo_height():
                self._command()

        def _redraw(self):
            self.delete("all")
            w = max(self._min_w, self.winfo_width())
            h = max(self._height, self.winfo_height() - 2)
            if self._state == "disabled":
                fill = "#CBD5E1"
                fg = "#64748B"
                bd = ""
            else:
                fill = self._hover_bg if self._hover else self._bg
                fg = self._fg
                bd = self._border
            draw_round_rect(self, 2, 1, w - 2, h, r=self._radius, fill=fill, outline=bd, width=1 if bd else 0)
            self.create_text(w / 2.0, (h + 1) / 2.0, text=self._text, fill=fg, font=self._font)

    class RoundedCard(tk.Canvas):
        """Контейнер із плавно закругленими кутами; авто-висота завжди синхронізує SmoothScrollView."""

        def __init__(self, parent, bg=PALETTE["card"], border=PALETTE["border"], parent_bg=PALETTE["bg"], radius=20, pad=12, shadow=True, auto_height=False, **kwargs):
            if auto_height and "height" not in kwargs:
                kwargs["height"] = 60
            super().__init__(parent, bg=parent_bg, highlightthickness=0, bd=0, **kwargs)
            self._card_bg = bg
            self._border = border
            self._radius = radius
            self._pad = pad
            self._shadow = shadow
            self._auto_height = auto_height
            self._sync_job = None

            self.inner = tk.Frame(self, bg=bg)
            self._win_id = self.create_window(pad, pad, window=self.inner, anchor="nw")
            self.bind("<Configure>", self._on_resize)
            if auto_height:
                self.inner.bind("<Configure>", self._schedule_auto_height)

        def _notify_scroll_ancestors(self):
            w = self.master
            while w is not None:
                if isinstance(w, SmoothScrollView):
                    w._schedule_sync(delay=16)
                    break
                w = getattr(w, "master", None)

        def _schedule_auto_height(self, _e=None):
            if not self._auto_height or self._sync_job is not None:
                return
            try:
                self._sync_job = self.after(16, self._run_auto_height)
            except Exception:
                self._sync_job = None

        def _run_auto_height(self):
            self._sync_job = None
            self.sync_height(notify=True)

        def sync_height(self, notify=True):
            if not self._auto_height:
                return
            try:
                if not self.winfo_exists():
                    return
                self.inner.update_idletasks()
                req_h = self.inner.winfo_reqheight() + 2 * self._pad + 8
                cur_h = int(float(self.cget("height") or 0))
                if req_h != cur_h and req_h > 24:
                    self.configure(height=req_h)
                    self._redraw_bg(max(40, self.winfo_width()), req_h)
                if notify:
                    self._notify_scroll_ancestors()
            except Exception:
                pass

        def _redraw_bg(self, w, h):
            self.delete("bg_shape")
            if self._shadow and w > 12 and h > 12:
                draw_round_rect(self, 3, 4, w - 2, h - 1, r=self._radius, fill=PALETTE["shadow"], outline="", width=0, tags="bg_shape")
            draw_round_rect(self, 2, 1, w - 3, h - 3, r=self._radius, fill=self._card_bg, outline=self._border, width=1, tags="bg_shape")
            self.tag_lower("bg_shape")

        def _on_resize(self, e):
            w = max(40, e.width)
            h = max(40, e.height)
            self._redraw_bg(w, h)
            inner_w = max(20, w - 2 * self._pad)
            self.itemconfig(self._win_id, width=inner_w)
            if not self._auto_height:
                inner_h = max(20, h - 2 * self._pad)
                self.itemconfig(self._win_id, height=inner_h)
            else:
                self._schedule_auto_height()
            self.coords(self._win_id, self._pad, self._pad)

    class OwlMascot(tk.Canvas):
        """Розумна, мила та виразна Сова-Ліза з живими реакціями."""

        def __init__(self, parent, size=104, bg=PALETTE["soft_indigo"]):
            super().__init__(parent, width=size, height=size, bg=bg, highlightthickness=0, bd=0)
            self._size = size
            self._bg = bg
            self._mood = "idle"
            self._blink = False
            self._draw()
            self._schedule_blink()

        def set_mood(self, mood):
            self._mood = mood
            self._blink = False
            self._draw()

        def _schedule_blink(self):
            try:
                if not self.winfo_exists():
                    return
                if self._mood in ("idle", "explain") and not self._blink:
                    self._blink = True
                    self._draw()
                    self.after(160, self._unblink)
                self.after(3600, self._schedule_blink)
            except Exception:
                pass

        def _unblink(self):
            try:
                if self.winfo_exists():
                    self._blink = False
                    self._draw()
            except Exception:
                pass

        def _draw(self):
            self.delete("all")
            s = self._size / 120.0
            med_bg = {
                "idle": "#E0E7FF",
                "thinking": "#FEF3C7",
                "happy": "#DCFCE7",
                "explain": "#E0F2FE",
            }.get(self._mood, "#E0E7FF")
            self.create_oval(6 * s, 6 * s, 114 * s, 114 * s, fill=med_bg, outline="#C7D2FE", width=max(1, int(1.5 * s)))
            self.create_line(18 * s, 102 * s, 102 * s, 102 * s, fill="#94A3B8", width=max(2, int(2.5 * s)), capstyle="round")
            for fx in (47, 73):
                self.create_oval((fx - 6) * s, 96 * s, (fx + 6) * s, 104 * s, fill="#F59E0B", outline="#D97706", width=1)
            self.create_oval(27 * s, 44 * s, 93 * s, 101 * s, fill="#5B619D", outline="#43487D", width=max(1, int(1.5 * s)))
            self.create_oval(39 * s, 58 * s, 81 * s, 97 * s, fill="#FEF7EC", outline="")
            for row_y, xs in [(72, [50, 60, 70]), (81, [54, 66])]:
                for px in xs:
                    self.create_arc((px - 4) * s, (row_y - 3) * s, (px + 4) * s, (row_y + 4) * s, start=200, extent=140, style="arc", outline="#D9C5A8", width=max(1, int(1.3 * s)))

            self.create_oval(20 * s, 56 * s, 38 * s, 88 * s, fill="#4B518B", outline="#3C4174", width=1)
            if self._mood == "explain":
                self.create_polygon(84 * s, 66 * s, 106 * s, 48 * s, 109 * s, 58 * s, 90 * s, 79 * s, fill="#4B518B", outline="#3C4174", width=1, smooth=True)
            elif self._mood == "happy":
                self.create_polygon(28 * s, 64 * s, 12 * s, 46 * s, 16 * s, 39 * s, 34 * s, 58 * s, fill="#4B518B", outline="#3C4174", width=1, smooth=True)
                self.create_polygon(92 * s, 64 * s, 108 * s, 46 * s, 104 * s, 39 * s, 86 * s, 58 * s, fill="#4B518B", outline="#3C4174", width=1, smooth=True)
            else:
                self.create_oval(82 * s, 56 * s, 100 * s, 88 * s, fill="#4B518B", outline="#3C4174", width=1)

            self.create_polygon(28 * s, 36 * s, 21 * s, 16 * s, 42 * s, 27 * s, fill="#4B518B", outline="#3C4174", width=1, smooth=True)
            self.create_polygon(92 * s, 36 * s, 99 * s, 16 * s, 78 * s, 27 * s, fill="#4B518B", outline="#3C4174", width=1, smooth=True)
            self.create_oval(25 * s, 22 * s, 95 * s, 70 * s, fill="#646AB0", outline="#43487D", width=max(1, int(1.5 * s)))
            self.create_oval(30 * s, 32 * s, 63 * s, 63 * s, fill="#FFF9F0", outline="")
            self.create_oval(57 * s, 32 * s, 90 * s, 63 * s, fill="#FFF9F0", outline="")

            cheek_col = "#FDA4AF" if self._mood == "happy" else "#FECDD3"
            self.create_oval(31 * s, 51 * s, 40 * s, 57 * s, fill=cheek_col, outline="")
            self.create_oval(80 * s, 51 * s, 89 * s, 57 * s, fill=cheek_col, outline="")

            if self._mood == "happy":
                self.create_arc(37 * s, 40 * s, 55 * s, 55 * s, start=15, extent=150, style="arc", outline="#1E293B", width=max(2, int(2.6 * s)))
                self.create_arc(65 * s, 40 * s, 83 * s, 55 * s, start=15, extent=150, style="arc", outline="#1E293B", width=max(2, int(2.6 * s)))
            elif self._blink:
                self.create_arc(37 * s, 44 * s, 55 * s, 53 * s, start=190, extent=160, style="arc", outline="#1E293B", width=max(2, int(2.2 * s)))
                self.create_arc(65 * s, 44 * s, 83 * s, 53 * s, start=190, extent=160, style="arc", outline="#1E293B", width=max(2, int(2.2 * s)))
            else:
                dx, dy = (1.5, -2.0) if self._mood == "thinking" else (0.0, 0.0)
                for ex in (46, 74):
                    self.create_oval((ex - 9.5) * s, 36.5 * s, (ex + 9.5) * s, 55.5 * s, fill="#FFFFFF", outline="#CBD5E1", width=1)
                    self.create_oval((ex - 7.5 + dx) * s, (38.5 + dy) * s, (ex + 7.5 + dx) * s, (53.5 + dy) * s, fill="#F59E0B", outline="")
                    self.create_oval((ex - 4.8 + dx) * s, (41.2 + dy) * s, (ex + 4.8 + dx) * s, (50.8 + dy) * s, fill="#1E293B", outline="")
                    self.create_oval((ex - 3.0 + dx) * s, (41.5 + dy) * s, (ex + 0.2 + dx) * s, (44.7 + dy) * s, fill="#FFFFFF", outline="")
                    self.create_oval((ex + 1.5 + dx) * s, (46.5 + dy) * s, (ex + 3.2 + dx) * s, (48.2 + dy) * s, fill="#FFFFFF", outline="")

            gl_col = "#B45309"
            gw = max(1, int(2.0 * s))
            self.create_oval(34.5 * s, 34.5 * s, 57.5 * s, 57.5 * s, outline=gl_col, width=gw)
            self.create_oval(62.5 * s, 34.5 * s, 85.5 * s, 57.5 * s, outline=gl_col, width=gw)
            self.create_arc(56.5 * s, 42 * s, 63.5 * s, 48 * s, start=0, extent=180, style="arc", outline=gl_col, width=gw)
            self.create_polygon(56 * s, 50 * s, 64 * s, 50 * s, 60 * s, 58 * s, fill="#F97316", outline="#EA580C", width=1, smooth=True)
            self.create_polygon(36 * s, 21 * s, 60 * s, 12 * s, 84 * s, 21 * s, 60 * s, 29 * s, fill="#262F4D", outline="#1E253D", width=1)
            self.create_rectangle(46 * s, 23 * s, 74 * s, 28 * s, fill="#334155", outline="")
            self.create_line(60 * s, 21 * s, 82 * s, 24 * s, 84 * s, 34 * s, fill="#FBBF24", width=max(1, int(2.0 * s)))
            self.create_oval(81 * s, 32 * s, 87 * s, 38 * s, fill="#F59E0B", outline="")

            star_f = "Avenir Next" if sys.platform == "darwin" else "Segoe UI"
            if self._mood == "happy":
                for sx, sy in [(18, 22), (101, 24), (96, 86)]:
                    self.create_text(sx * s, sy * s, text="✦", fill="#F59E0B", font=(star_f, max(8, int(11 * s)), "bold"))
            elif self._mood == "thinking":
                self.create_oval(92 * s, 10 * s, 112 * s, 29 * s, fill="#FFFFFF", outline="#F59E0B", width=1)
                self.create_text(102 * s, 19.5 * s, text="?", fill="#D97706", font=(star_f, max(9, int(12 * s)), "bold"))

    class HintStepperBar(tk.Frame):
        """Інтерактивна шкала підказок 1 → 10 із круглими точками та кроковим перемикачем."""

        def __init__(self, parent, fonts, on_step, on_select_level=None, bg=PALETTE["card_soft"]):
            super().__init__(parent, bg=bg)
            self.fonts = fonts
            self.on_step = on_step
            self.on_select_level = on_select_level
            self._bg = bg
            self._current = 0  # 0..10

            top = tk.Frame(self, bg=bg)
            top.pack(fill="x", padx=10, pady=(6, 4))
            self.lbl_title = tk.Label(top, text="💡 Підказки Сови: 0 / 10", font=fonts["bold_sm"], bg=bg, fg="#92400E")
            self.lbl_title.pack(side="left")

            self.btn_next_hint = RoundedButton(
                top,
                text="Підказка 1/10 →",
                command=self.on_step,
                bg=PALETTE["soft_amber"],
                hover_bg="#FEF08A",
                fg="#92400E",
                border_color=PALETTE["soft_amber_bd"],
                font=fonts["small"],
                radius=12,
                height=26,
                min_width=130,
                pad_x=10,
                parent_bg=bg,
            )
            self.btn_next_hint.pack(side="right")

            self.dots_canvas = tk.Canvas(self, height=28, bg=bg, highlightthickness=0, bd=0, cursor=_hand_cursor())
            self.dots_canvas.pack(fill="x", padx=10, pady=(0, 6))
            self.dots_canvas.bind("<Configure>", lambda _e: self._redraw_dots())
            self.dots_canvas.bind("<ButtonRelease-1>", self._on_dot_click)
            self._dot_boxes = []

        def set_level(self, level):
            self._current = max(0, min(10, int(level)))
            if self._current == 0:
                self.lbl_title.config(text="💡 Підказки Сови: 0 / 10 (від легкого натяку до розповіді)")
                self.btn_next_hint.set_text("Підказка 1/10 →")
                self.btn_next_hint.set_state("normal")
            elif self._current < 10:
                self.lbl_title.config(text=f"💡 Відкрито підказок: {self._current} / 10")
                self.btn_next_hint.set_text(f"Ще підказка ({self._current + 1}/10) →")
                self.btn_next_hint.set_state("normal")
            else:
                self.lbl_title.config(text="💡 Відкрито всі 10 / 10 (повна відповідь і розповідь!)")
                self.btn_next_hint.set_text("Усі 10/10 відкрито ✓")
                self.btn_next_hint.set_state("disabled")
            self._redraw_dots()

        def _redraw_dots(self):
            c = self.dots_canvas
            c.delete("all")
            self._dot_boxes = []
            w = max(240, c.winfo_width())
            step = w / 10.0
            for i in range(1, 11):
                cx = (i - 0.5) * step
                cy = 14
                r_w = min(13, max(9, step * 0.38))
                if i <= self._current:
                    fill = "#D97706" if i == 10 else "#F59E0B"
                    fg = "#FFFFFF"
                    bd = ""
                elif i == self._current + 1:
                    fill = "#FEF3C7"
                    fg = "#92400E"
                    bd = "#F59E0B"
                else:
                    fill = "#FFFFFF"
                    fg = "#94A3B8"
                    bd = PALETTE["border"]
                draw_round_rect(c, cx - r_w, cy - 11, cx + r_w, cy + 11, r=9, fill=fill, outline=bd, width=1 if bd else 0)
                c.create_text(cx, cy, text=str(i), fill=fg, font=(self.fonts["family"], 8, "bold"))
                self._dot_boxes.append((i, cx - r_w, cy - 12, cx + r_w, cy + 12))

        def _on_dot_click(self, e):
            if not self.on_select_level:
                return
            for lvl, x1, y1, x2, y2 in self._dot_boxes:
                if x1 - 4 <= e.x <= x2 + 4 and y1 <= e.y <= y2:
                    self.on_select_level(lvl)
                    return

    class SubjectTile(tk.Canvas):
        """Закруглена інтерактивна плитка для вибору предмета НМТ."""

        def __init__(self, parent, sid, cfg, var, fonts, on_change=None):
            super().__init__(parent, height=64, bg=PALETTE["card"], highlightthickness=0, bd=0, cursor=_hand_cursor())
            self.sid = sid
            self.cfg = cfg
            self.var = var
            self.fonts = fonts
            self.on_change = on_change
            self._hover = False

            self.bind("<Configure>", lambda _e: self._redraw())
            self.bind("<Enter>", self._on_enter)
            self.bind("<Leave>", self._on_leave)
            self.bind("<ButtonRelease-1>", self._toggle)
            self.var.trace_add("write", lambda *_: self._redraw())
            self._redraw()

        def _on_enter(self, _e):
            self._hover = True
            self._redraw()

        def _on_leave(self, _e):
            self._hover = False
            self._redraw()

        def _toggle(self, _e):
            self.var.set(not self.var.get())
            if self.on_change:
                self.on_change()

        def _redraw(self):
            self.delete("all")
            w = max(210, self.winfo_width())
            h = max(62, self.winfo_height())
            selected = bool(self.var.get())

            if selected:
                fill = PALETTE["soft_indigo"]
                border = PALETTE["primary"]
                bw = 2
            else:
                fill = "#F3F6FD" if self._hover else PALETTE["card_soft"]
                border = "#BAC5E6" if self._hover else PALETTE["border"]
                bw = 1

            draw_round_rect(self, 2, 2, w - 2, h - 2, r=15, fill=fill, outline=border, width=bw)

            cx, cy = 22, h / 2.0
            if selected:
                draw_round_rect(self, cx - 10, cy - 10, cx + 10, cy + 10, r=7, fill=PALETTE["primary"], outline="")
                self.create_text(cx, cy, text="✓", fill="#FFFFFF", font=self.fonts["bold_sm"])
            else:
                draw_round_rect(self, cx - 10, cy - 10, cx + 10, cy + 10, r=7, fill="#FFFFFF", outline="#94A3B8", width=1.5)

            self.create_text(42, 21, text=self.cfg["name"], anchor="w", fill=PALETTE["text"], font=self.fonts["h3"])
            meta = f"{self.cfg['total_tasks']} завдань • макс. {self.cfg['max_score']} б. • поріг {self.cfg['threshold']}"
            self.create_text(42, 43, text=meta, anchor="w", fill=PALETTE["muted"], font=self.fonts["small"])

            if self.cfg["mandatory"]:
                badge_txt = "Обов’язковий"
                b_bg, b_fg = PALETTE["chip_req_bg"], PALETTE["chip_req_fg"]
            else:
                badge_txt = "За вибором"
                b_bg, b_fg = PALETTE["chip_opt_bg"], PALETTE["chip_opt_fg"]
            bw_px = 88 if self.cfg["mandatory"] else 78
            draw_round_rect(self, w - bw_px - 12, 11, w - 12, 30, r=10, fill=b_bg, outline="")
            self.create_text(w - bw_px / 2.0 - 12, 20.5, text=badge_txt, fill=b_fg, font=(self.fonts["family"], 8, "bold"))

    class RoundedOptionRow(tk.Frame):
        """Закруглена інтерактивна кнопка-варіант відповіді (А/Б/В/Г/Д)."""

        def __init__(self, parent, label_txt, option_txt, var, fonts, base_bg=PALETTE["card"], active_bg=PALETTE["soft_indigo"], active_bd=PALETTE["primary"]):
            super().__init__(parent, bg=base_bg)
            self.label_txt = label_txt
            self.option_txt = option_txt
            self.var = var
            self.fonts = fonts
            self.base_bg = base_bg
            self.active_bg = active_bg
            self.active_bd = active_bd
            self._hover = False

            self.canvas = tk.Canvas(self, bg=base_bg, highlightthickness=0, bd=0, height=44, cursor=_hand_cursor())
            self.canvas.pack(fill="x", expand=True)

            self.canvas.bind("<Configure>", lambda _e: self._redraw())
            self.canvas.bind("<Enter>", self._on_enter)
            self.canvas.bind("<Leave>", self._on_leave)
            self.canvas.bind("<ButtonRelease-1>", self._select)
            self.var.trace_add("write", lambda *_: self._redraw())

        def _on_enter(self, _e):
            self._hover = True
            self._redraw()

        def _on_leave(self, _e):
            self._hover = False
            self._redraw()

        def _select(self, _e):
            self.var.set(self.label_txt)

        def _redraw(self):
            c = self.canvas
            c.delete("all")
            w = max(220, c.winfo_width())
            selected = (self.var.get() == self.label_txt)

            text_x = 50
            avail_w = max(130, w - text_x - 16)
            t_id = c.create_text(text_x, 0, text=self.option_txt, anchor="nw", width=avail_w, font=self.fonts["body"], fill=PALETTE["text"])
            bbox = c.bbox(t_id)
            th = (bbox[3] - bbox[1]) if bbox else 20
            c.delete(t_id)

            h = max(44, th + 20)
            if int(c.cget("height")) != h:
                c.configure(height=h)

            if selected:
                fill = self.active_bg
                bd = self.active_bd
                bw = 2
                badge_bg = self.active_bd
                badge_fg = "#FFFFFF"
            else:
                fill = "#F3F6FD" if self._hover else "#FAFBFD"
                bd = "#BDC8E6" if self._hover else PALETTE["border"]
                bw = 1
                badge_bg = "#E8ECF8"
                badge_fg = PALETTE["text"]

            draw_round_rect(c, 2, 2, w - 2, h - 2, r=14, fill=fill, outline=bd, width=bw)

            cy = h / 2.0
            draw_round_rect(c, 12, cy - 13, 38, cy + 13, r=10, fill=badge_bg, outline="")
            c.create_text(25, cy, text=self.label_txt, fill=badge_fg, font=self.fonts["bold_sm"])
            c.create_text(text_x, cy, text=self.option_txt, anchor="w", width=avail_w, font=self.fonts["body"], fill=PALETTE["text"])

    class RoundedCheckRow(tk.Frame):
        """Закруглена інтерактивна кнопка-прапорець (для завдань «обери 3 із 7») із перенесенням тексту."""

        def __init__(self, parent, key_txt, item_txt, var, fonts, base_bg=PALETTE["card"], active_bg="#D1FAE5", active_bd=PALETTE["accent"]):
            super().__init__(parent, bg=base_bg)
            self.key_txt = key_txt
            self.item_txt = item_txt
            self.var = var
            self.fonts = fonts
            self.base_bg = base_bg
            self.active_bg = active_bg
            self.active_bd = active_bd
            self._hover = False

            self.canvas = tk.Canvas(self, bg=base_bg, highlightthickness=0, bd=0, height=40, cursor=_hand_cursor())
            self.canvas.pack(fill="x", expand=True)

            self.canvas.bind("<Configure>", lambda _e: self._redraw())
            self.canvas.bind("<Enter>", self._on_enter)
            self.canvas.bind("<Leave>", self._on_leave)
            self.canvas.bind("<ButtonRelease-1>", self._toggle)
            self.var.trace_add("write", lambda *_: self._redraw())

        def _on_enter(self, _e):
            self._hover = True
            self._redraw()

        def _on_leave(self, _e):
            self._hover = False
            self._redraw()

        def _toggle(self, _e):
            self.var.set(not self.var.get())

        def _redraw(self):
            c = self.canvas
            c.delete("all")
            w = max(220, c.winfo_width())
            checked = bool(self.var.get())

            text_x = 50
            avail_w = max(130, w - text_x - 16)
            t_id = c.create_text(text_x, 0, text=self.item_txt, anchor="nw", width=avail_w, font=self.fonts["body_sm"], fill=PALETTE["text"])
            bbox = c.bbox(t_id)
            th = (bbox[3] - bbox[1]) if bbox else 18
            c.delete(t_id)

            h = max(40, th + 18)
            if int(c.cget("height")) != h:
                c.configure(height=h)

            if checked:
                fill = self.active_bg
                bd = self.active_bd
                bw = 2
                badge_bg = self.active_bd
                badge_fg = "#FFFFFF"
            else:
                fill = "#F3F6FD" if self._hover else "#FAFBFD"
                bd = "#BDC8E6" if self._hover else PALETTE["border"]
                bw = 1
                badge_bg = "#E8ECF8"
                badge_fg = PALETTE["text"]

            draw_round_rect(c, 2, 2, w - 2, h - 2, r=13, fill=fill, outline=bd, width=bw)
            cy = h / 2.0
            draw_round_rect(c, 12, cy - 12, 38, cy + 12, r=8, fill=badge_bg, outline="")
            lbl_show = f"✓ {self.key_txt}" if checked else self.key_txt
            c.create_text(25, cy, text=lbl_show, fill=badge_fg, font=(self.fonts["family"], 9, "bold"))
            c.create_text(text_x, cy, text=self.item_txt, anchor="w", width=avail_w, font=self.fonts["body_sm"], fill=PALETTE["text"])

    class NmtTutorApp:
        def __init__(self, root):
            self.root = root
            self.root.title(APP_TITLE)

            try:
                sw = self.root.winfo_screenwidth()
                sh = self.root.winfo_screenheight()
            except Exception:
                sw, sh = 1440, 900
            win_w = min(1280, max(940, sw - 48))
            win_h = min(820, max(640, sh - 80))
            pos_x = max(0, (sw - win_w) // 2)
            pos_y = max(20, (sh - win_h) // 2)
            self.root.geometry(f"{win_w}x{win_h}+{pos_x}+{pos_y}")
            self.root.minsize(880, 600)
            self.root.configure(bg=PALETTE["bg"])

            self.fonts = _pick_fonts(self.root)
            self._configure_ttk_styles()
            self._set_app_icon()
            self._setup_menus()
            SmoothScrollView.install_global_wheel(self.root)

            self.custom_bank = {}
            self._autoload_local_json()
            self.plan = []
            self.current_block_idx = 0
            self.current_q_idx = 0
            self.tutor_mode = True
            self.length_mode = "quick"
            self.timer_seconds = 0
            self.timer_running = False
            self.active_drill = None
            self.drill_used_prompts = []
            self.q_hint_level = 0
            self.q_hints_10 = []
            self.drill_hint_level = 0
            self.drill_hints_10 = []
            self._chat_labels = []
            self._pane = None
            self._pane_orient = "horizontal"
            self._drill_modal = None

            self.main_container = tk.Frame(self.root, bg=PALETTE["bg"])
            self.main_container.pack(fill="both", expand=True)

            self.show_setup()

        def _set_app_icon(self):
            res_dir = os.path.dirname(os.path.abspath(__file__))
            if sys.platform.startswith("win"):
                ico_path = os.path.join(res_dir, "owl_icon.ico")
                if os.path.exists(ico_path):
                    try:
                        self.root.iconbitmap(default=ico_path)
                    except Exception:
                        pass
            png_path = os.path.join(res_dir, "owl_icon.png")
            if os.path.exists(png_path):
                try:
                    self._icon_img = tk.PhotoImage(file=png_path)
                    self.root.iconphoto(True, self._icon_img)
                except Exception:
                    pass

        def _setup_menus(self):
            try:
                is_mac = (sys.platform == "darwin")
                accel_o = "⌘O" if is_mac else "Ctrl+O"
                accel_q = "⌘Q" if is_mac else "Ctrl+Q"

                menubar = tk.Menu(self.root)
                file_menu = tk.Menu(menubar, tearoff=0)
                file_menu.add_command(label="Додати свій банк (.json)…", accelerator=accel_o, command=self._on_load_json)
                file_menu.add_command(label="Зберегти шаблон (.json)…", command=self._on_export_template)
                if sys.platform.startswith("win"):
                    file_menu.add_command(label="Створити ярлик на Робочому столі", command=self._create_windows_shortcut)
                file_menu.add_separator()
                file_menu.add_command(label="Вийти з програми", accelerator=accel_q, command=self._quit_app)
                menubar.add_cascade(label="Файл", menu=file_menu)

                nav_menu = tk.Menu(menubar, tearoff=0)
                nav_menu.add_command(label="Вибір предметів", command=self.show_setup)
                nav_menu.add_command(label="Програми НМТ та шкала 100–200", command=self._show_reference_dialog)
                menubar.add_cascade(label="Навігація", menu=nav_menu)

                help_menu = tk.Menu(menubar, tearoff=0)
                help_menu.add_command(label="Про програму «НМТ Сова-Репетитор»", command=self._show_about_dialog)
                menubar.add_cascade(label="Довідка", menu=help_menu)

                self.root.config(menu=menubar)
                if is_mac:
                    self.root.bind_all("<Command-q>", lambda _e: self._quit_app())
                    self.root.bind_all("<Command-o>", lambda _e: self._on_load_json())
                    self.root.createcommand("tk::mac::Quit", self._quit_app)
                    self.root.createcommand("tk::mac::ShowHelp", self._show_about_dialog)
                else:
                    self.root.bind_all("<Control-q>", lambda _e: self._quit_app())
                    self.root.bind_all("<Control-o>", lambda _e: self._on_load_json())
            except Exception:
                pass

        def _create_windows_shortcut(self):
            if not sys.platform.startswith("win"):
                return
            try:
                import subprocess
                app_dir = os.path.dirname(os.path.abspath(__file__))
                target_pyw = os.path.abspath(__file__)
                ico_path = os.path.join(app_dir, "owl_icon.ico")
                pyw_exe = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
                if not os.path.exists(pyw_exe):
                    pyw_exe = sys.executable
                desktop = os.path.join(os.path.expanduser("~"), "Desktop")
                lnk_path = os.path.join(desktop, "НМТ Сова-Репетитор.lnk")
                ps = (
                    "$ws = New-Object -ComObject WScript.Shell; "
                    f"$s = $ws.CreateShortcut('{lnk_path}'); "
                    f"$s.TargetPath = '{pyw_exe}'; "
                    f"$s.Arguments = '\"{target_pyw}\"'; "
                    f"$s.WorkingDirectory = '{app_dir}'; "
                    + (f"$s.IconLocation = '{ico_path}'; " if os.path.exists(ico_path) else "")
                    + "$s.Save()"
                )
                subprocess.run(["powershell", "-NoProfile", "-Command", ps], check=True)
                messagebox.showinfo("Ярлик створено", f"Ярлик «НМТ Сова-Репетитор» успішно додано на Робочий стіл!\n\n{lnk_path}")
            except Exception as exc:
                messagebox.showerror("Не вдалося створити ярлик", f"Виникла помилка:\n{exc}")

        def _quit_app(self):
            self.timer_running = False
            try:
                self.root.destroy()
            except Exception:
                pass

        def _show_about_dialog(self):
            os_label = "macOS" if sys.platform == "darwin" else "Windows" if sys.platform.startswith("win") else "Desktop"
            messagebox.showinfo(
                "Про програму",
                f"{APP_TITLE}\nВерсія {APP_VERSION} ({os_label})\n\n"
                "• Усі 12 предметів НМТ (програми 2022–2026 рр.)\n"
                f"• Вбудовано {sum(len(v) for v in BANK_QUESTIONS.values())} завдань та {len(DRILL_GENERATORS)} генераторів\n"
                "• Багаторівневі підказки Сови-Лізи (рівні 1–10)\n"
                "• Плавна анімована прокрутка та адаптація під екран\n"
                "• Звіти зберігаються у Документи/NMT_Tutor"
            )

        def _autoload_local_json(self):
            data_dir = get_user_data_dir()
            try:
                for fname in os.listdir(data_dir):
                    if fname.endswith(".json") and "template" not in fname.lower():
                        fpath = os.path.join(data_dir, fname)
                        loaded = load_custom_json(fpath)
                        for k, v in loaded.items():
                            self.custom_bank.setdefault(k, []).extend(v)
            except Exception:
                pass

        def _configure_ttk_styles(self):
            style = ttk.Style(self.root)
            try:
                style.theme_use("clam")
            except Exception:
                pass
            style.configure("TFrame", background=PALETTE["bg"])
            style.configure("TLabel", background=PALETTE["card"], foreground=PALETTE["text"], font=self.fonts["body"])
            style.configure("TCheckbutton", background=PALETTE["card"], foreground=PALETTE["text"], font=self.fonts["body"])
            style.configure("TRadiobutton", background=PALETTE["card"], foreground=PALETTE["text"], font=self.fonts["body"])
            style.configure("Soft.TRadiobutton", background=PALETTE["card_soft"], foreground=PALETTE["text"], font=self.fonts["body_sm"])
            style.configure(
                "TCombobox",
                font=self.fonts["bold"],
                padding=4,
                fieldbackground="#FFFFFF",
                background="#EEF2FF",
                foreground=PALETTE["text"],
            )
            style.map("TCombobox", fieldbackground=[("readonly", "#FFFFFF")], foreground=[("readonly", PALETTE["text"])])
            style.configure("TEntry", padding=6, fieldbackground="#FFFFFF", foreground=PALETTE["text"])

        def _clear_main(self):
            self.timer_running = False
            self._chat_labels = []
            for w in self.main_container.winfo_children():
                w.destroy()

        # -------------------------------------------------------------------
        # 1. ЕКРАН ВИБОРУ ПРЕДМЕТІВ І НАЛАШТУВАНЬ
        # -------------------------------------------------------------------
        def show_setup(self):
            self._clear_main()

            header = tk.Frame(self.main_container, bg=PALETTE["nav"], height=74)
            header.pack(fill="x")
            header.pack_propagate(False)

            title_wrap = tk.Frame(header, bg=PALETTE["nav"])
            title_wrap.pack(side="left", padx=24, pady=10)
            tk.Label(
                title_wrap,
                text="НМТ Тренажер • Репетитор Сова-Ліза (2022–2026)",
                font=self.fonts["h1"],
                bg=PALETTE["nav"],
                fg=PALETTE["nav_fg"],
            ).pack(anchor="w")
            os_sub = "macOS" if sys.platform == "darwin" else "Windows" if sys.platform.startswith("win") else "Desktop"
            tk.Label(
                title_wrap,
                text=f"Версія для {os_sub} • Усі 12 предметів, 10 рівнів підказок та шкала 100–200",
                font=self.fonts["small"],
                bg=PALETTE["nav"],
                fg="#CBD5E1",
            ).pack(anchor="w")

            RoundedButton(
                header,
                text="📘 Програми та шкала 100–200",
                command=self._show_reference_dialog,
                bg=PALETTE["nav_accent"],
                hover_bg="#425182",
                fg="#FFFFFF",
                border_color="#526296",
                font=self.fonts["bold_sm"],
                radius=14,
                height=36,
                min_width=230,
                parent_bg=PALETTE["nav"],
            ).pack(side="right", padx=22, pady=18)

            body = tk.Frame(self.main_container, bg=PALETTE["bg"])
            body.pack(fill="both", expand=True, padx=20, pady=14)

            left_card = RoundedCard(body, bg=PALETTE["card"], border=PALETTE["border"], parent_bg=PALETTE["bg"], radius=20, pad=14)
            left_card.pack(side="left", fill="both", expand=True, padx=(0, 12))
            left = left_card.inner

            welcome_box = RoundedCard(left, bg=PALETTE["soft_indigo"], border=PALETTE["soft_indigo_bd"], parent_bg=PALETTE["card"], radius=18, pad=8, shadow=False, height=110)
            welcome_box.pack(fill="x", pady=(0, 10))
            welcome_box.pack_propagate(False)
            w_in = welcome_box.inner

            owl_welcome = OwlMascot(w_in, size=88, bg=PALETTE["soft_indigo"])
            owl_welcome.pack(side="left", padx=(4, 10))

            w_txt = tk.Frame(w_in, bg=PALETTE["soft_indigo"])
            w_txt.pack(side="left", fill="both", expand=True, pady=4)
            tk.Label(
                w_txt,
                text="Привіт! Я Сова-Ліза — твій персональний репетитор НМТ 🦉",
                font=self.fonts["h3"],
                bg=PALETTE["soft_indigo"],
                fg="#1E2B58",
            ).pack(anchor="w")
            lbl_wdesc = tk.Label(
                w_txt,
                text=(
                    "Обирай предмети нижче (усе вже вбудовано всередину!). "
                    "У кожному завданні є 10 рівнів підказок (від легкого натяку до повної розповіді) та схожі приклади після помилки."
                ),
                font=self.fonts["body_sm"],
                bg=PALETTE["soft_indigo"],
                fg="#334155",
                wraplength=520,
                justify="left",
            )
            lbl_wdesc.pack(anchor="w", pady=(3, 0))
            w_txt.bind("<Configure>", lambda e, l=lbl_wdesc: l.config(wraplength=max(220, e.width - 12)))

            tk.Label(left, text="1. Оберіть предмети самостійно (клікай на картки):", font=self.fonts["h2"], bg=PALETTE["card"], fg=PALETTE["text"]).pack(anchor="w", pady=(0, 6))

            preset_bar = tk.Frame(left, bg=PALETTE["card"])
            preset_bar.pack(fill="x", pady=(0, 6))
            presets = [
                ("Стандарт НМТ (3 + Англ.)", ["ukrmova", "math", "history", "english"]),
                ("Лише обов’язкові (3)", ["ukrmova", "math", "history"]),
                ("Усі 12 предметів", SUBJECTS_ORDER),
                ("Скинути", []),
            ]
            for p_title, p_list in presets:
                RoundedButton(
                    preset_bar,
                    text=p_title,
                    command=lambda lst=p_list: self._apply_preset(lst),
                    bg=PALETTE["card_soft"],
                    hover_bg=PALETTE["soft_indigo"],
                    fg=PALETTE["text"],
                    border_color=PALETTE["border"],
                    font=self.fonts["small"],
                    radius=12,
                    height=28,
                    min_width=85,
                    pad_x=11,
                    parent_bg=PALETTE["card"],
                ).pack(side="left", padx=(0, 6))

            grid_scroll = SmoothScrollView(left, bg=PALETTE["card"])
            grid_scroll.pack(fill="both", expand=True, pady=2)
            grid_wrap = grid_scroll.inner
            grid_wrap.columnconfigure(0, weight=1)
            grid_wrap.columnconfigure(1, weight=1)

            self.subj_vars = {}
            default_sel = {"ukrmova", "math", "history", "english"}
            for idx, sid in enumerate(SUBJECTS_ORDER):
                cfg = SUBJECTS_CONFIG[sid]
                var = tk.BooleanVar(value=(sid in default_sel))
                self.subj_vars[sid] = var
                r, c = divmod(idx, 2)
                tile = SubjectTile(grid_wrap, sid, cfg, var, self.fonts)
                tile.grid(row=r, column=c, sticky="nsew", padx=4, pady=3)

            right_card = RoundedCard(body, bg=PALETTE["card"], border=PALETTE["border"], parent_bg=PALETTE["bg"], radius=20, pad=16, width=376)
            right_card.pack(side="right", fill="y")
            right_card.pack_propagate(False)
            right = right_card.inner

            tk.Label(right, text="2. Режим підготовки:", font=self.fonts["h2"], bg=PALETTE["card"], fg=PALETTE["text"]).pack(anchor="w", pady=(0, 6))
            self.var_mode = tk.StringVar(value="tutor")
            mode_box = tk.Frame(right, bg=PALETTE["card_soft"], highlightbackground=PALETTE["border"], highlightthickness=1)
            mode_box.pack(fill="x", pady=(0, 10))
            ttk.Radiobutton(
                mode_box,
                text="🦉 Із Совою-Репетитором (рекомендовано)\n10 рівнів підказок + схожий приклад при помилці",
                variable=self.var_mode,
                value="tutor",
                style="Soft.TRadiobutton",
            ).pack(anchor="w", padx=10, pady=(8, 4))
            ttk.Radiobutton(
                mode_box,
                text="⏱ Режим іспиту НМТ\nТаймер без підказок, підсумок наприкінці",
                variable=self.var_mode,
                value="exam",
                style="Soft.TRadiobutton",
            ).pack(anchor="w", padx=10, pady=(0, 8))

            tk.Label(right, text="3. Обсяг тесту:", font=self.fonts["h2"], bg=PALETTE["card"], fg=PALETTE["text"]).pack(anchor="w", pady=(0, 6))
            self.var_length = tk.StringVar(value="quick")
            len_box = tk.Frame(right, bg=PALETTE["card_soft"], highlightbackground=PALETTE["border"], highlightthickness=1)
            len_box.pack(fill="x", pady=(0, 10))
            ttk.Radiobutton(len_box, text="Швидке тренування (8 завд. / предмет)", variable=self.var_length, value="quick", style="Soft.TRadiobutton").pack(anchor="w", padx=10, pady=(7, 3))
            ttk.Radiobutton(len_box, text="Середній блок (15 завд. / предмет)", variable=self.var_length, value="medium", style="Soft.TRadiobutton").pack(anchor="w", padx=10, pady=3)
            ttk.Radiobutton(len_box, text="Повний формат НМТ (22 / 24 / 30 / 32)", variable=self.var_length, value="full", style="Soft.TRadiobutton").pack(anchor="w", padx=10, pady=(3, 7))

            total_static = sum(len(v) for v in BANK_QUESTIONS.values())
            extra_cnt = sum(len(v) for v in self.custom_bank.values())
            tk.Label(right, text="4. База завдань (2022–2026):", font=self.fonts["h2"], bg=PALETTE["card"], fg=PALETTE["text"]).pack(anchor="w", pady=(0, 4))
            base_msg = f"Вбудовано {total_static} завдань НМТ 2022–2026 рр. + {len(DRILL_GENERATORS)} генераторів."
            if extra_cnt:
                base_msg += f" Додатково: {extra_cnt}."
            self.lbl_custom = tk.Label(
                right,
                text=base_msg,
                font=self.fonts["small"],
                bg=PALETTE["card"],
                fg=PALETTE["ok_fg"],
                wraplength=330,
                justify="left",
            )
            self.lbl_custom.pack(anchor="w", pady=(0, 6))

            json_row = tk.Frame(right, bg=PALETTE["card"])
            json_row.pack(fill="x", pady=(0, 6))
            RoundedButton(
                json_row,
                text="📂 Додати .json",
                command=self._on_load_json,
                bg=PALETTE["card_soft"],
                hover_bg=PALETTE["soft_indigo"],
                fg=PALETTE["text"],
                border_color=PALETTE["border"],
                font=self.fonts["small"],
                radius=12,
                height=30,
                min_width=140,
                pad_x=8,
                parent_bg=PALETTE["card"],
            ).pack(side="left", fill="x", expand=True, padx=(0, 6))
            RoundedButton(
                json_row,
                text="💾 Шаблон .json",
                command=self._on_export_template,
                bg=PALETTE["card_soft"],
                hover_bg=PALETTE["soft_indigo"],
                fg=PALETTE["text"],
                border_color=PALETTE["border"],
                font=self.fonts["small"],
                radius=12,
                height=30,
                min_width=140,
                pad_x=8,
                parent_bg=PALETTE["card"],
            ).pack(side="right", fill="x", expand=True)

            if sys.platform.startswith("win"):
                RoundedButton(
                    right,
                    text="📌 Ярлик на Робочий стіл",
                    command=self._create_windows_shortcut,
                    bg=PALETTE["soft_indigo"],
                    hover_bg="#DCE2FF",
                    fg=PALETTE["primary"],
                    border_color=PALETTE["soft_indigo_bd"],
                    font=self.fonts["small"],
                    radius=12,
                    height=30,
                    min_width=290,
                    parent_bg=PALETTE["card"],
                ).pack(fill="x", pady=(0, 6))

            RoundedButton(
                right,
                text="🚀 Розпочати тренування",
                command=self._start_session,
                bg=PALETTE["primary"],
                hover_bg=PALETTE["primary_hover"],
                fg="#FFFFFF",
                font=self.fonts["h3"],
                radius=18,
                height=44,
                min_width=310,
                parent_bg=PALETTE["card"],
            ).pack(side="bottom", fill="x", pady=(6, 0))

        def _apply_preset(self, sids):
            s_set = set(sids)
            for sid, var in self.subj_vars.items():
                var.set(sid in s_set)

        def _on_load_json(self):
            path = filedialog.askopenfilename(
                title="Оберіть JSON-файл із завданнями НМТ",
                initialdir=get_user_data_dir(),
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            )
            if not path:
                return
            try:
                loaded = load_custom_json(path)
                if not loaded:
                    messagebox.showwarning("Порожній файл", "У вибраному файлі не знайдено коректних завдань для предметів НМТ.")
                    return
                for k, v in loaded.items():
                    self.custom_bank.setdefault(k, []).extend(v)
                total = sum(len(v) for v in self.custom_bank.values())
                self.lbl_custom.config(text=f"Додано з вашого файлу: {total} завдань (активні разом із вбудованою базою!).", fg=PALETTE["ok_fg"])
            except Exception as exc:
                messagebox.showerror("Помилка завантаження", f"Не вдалося прочитати файл:\n{exc}")

        def _on_export_template(self):
            path = filedialog.asksaveasfilename(
                title="Зберегти шаблон бази завдань",
                initialdir=get_user_data_dir(),
                defaultextension=".json",
                initialfile="nmt_custom_bank_template.json",
                filetypes=[("JSON files", "*.json")],
            )
            if not path:
                return
            try:
                export_json_template(path)
                messagebox.showinfo("Готово", f"Шаблон збережено:\n{path}\n\nВи можете додавати туди власні тести й підвантажувати їх у програму.")
            except Exception as exc:
                messagebox.showerror("Помилка", str(exc))

        def _show_reference_dialog(self):
            win = tk.Toplevel(self.root)
            win.title("Офіційна структура НМТ та шкали 100–200")
            win.geometry("780x560")
            win.configure(bg=PALETTE["bg"])
            card = RoundedCard(win, bg=PALETTE["card"], border=PALETTE["border"], parent_bg=PALETTE["bg"], radius=18, pad=16)
            card.pack(fill="both", expand=True, padx=16, pady=16)
            txt = tk.Text(card.inner, wrap="word", font=self.fonts["body"], bg=PALETTE["card"], fg=PALETTE["text"], padx=10, pady=8, relief="flat")
            txt.pack(fill="both", expand=True)
            lines = ["СТРУКТУРА НМТ І ЧИННІ ПРОГРАМИ (2022–2026)\n" + "=" * 58 + "\n"]
            for sid in SUBJECTS_ORDER:
                c = SUBJECTS_CONFIG[sid]
                lines.append(f"• {c['name']} ({'Обов’язковий' if c['mandatory'] else 'За вибором'})")
                lines.append(f"  Завдань: {c['total_tasks']} | Макс. бал: {c['max_score']} | Поріг «склав»: {c['threshold']} (100 б.)")
                lines.append(f"  Програма: {c['program_order']}")
                lines.append(f"  Форми: {c['structure']}\n")
            txt.insert("1.0", "\n".join(lines))
            txt.config(state="disabled")

        # -------------------------------------------------------------------
        # 2. ЕКРАН ТЕСТУВАННЯ + ЄДИНА ПЛАВНО ПРОКРУЧУВАНА ПРАВА ПАНЕЛЬ
        # -------------------------------------------------------------------
        def _start_session(self):
            selected = [sid for sid in SUBJECTS_ORDER if self.subj_vars[sid].get()]
            if not selected:
                messagebox.showwarning("Оберіть предмети", "Позначте бодай один предмет НМТ для початку тренування.")
                return
            self.tutor_mode = (self.var_mode.get() == "tutor")
            self.length_mode = self.var_length.get()
            self.plan = build_session_plan(selected, length_mode=self.length_mode, custom_bank=self.custom_bank)
            self.current_block_idx = 0
            self.current_q_idx = 0
            self.timer_seconds = len(selected) * 60 * 60
            self._build_test_view()
            self._load_current_question()
            self._tick_timer()

        def _on_pane_configure(self, e):
            if self._pane is None:
                return
            want_orient = "vertical" if e.width < 820 else "horizontal"
            if want_orient != self._pane_orient:
                self._pane_orient = want_orient
                try:
                    self._pane.configure(orient=want_orient)
                except Exception:
                    pass

        def _build_test_view(self):
            self._clear_main()

            top = tk.Frame(self.main_container, bg=PALETTE["nav"], height=64)
            top.pack(fill="x")
            top.pack_propagate(False)

            self.lbl_subj_title = tk.Label(top, text="", font=self.fonts["h2"], bg=PALETTE["nav"], fg="#FFFFFF")
            self.lbl_subj_title.pack(side="left", padx=20)

            RoundedButton(
                top,
                text="Завершити тест",
                command=self._finish_session,
                bg="#EF4444",
                hover_bg="#DC2626",
                fg="#FFFFFF",
                font=self.fonts["bold_sm"],
                radius=14,
                height=34,
                min_width=136,
                parent_bg=PALETTE["nav"],
            ).pack(side="right", padx=16, pady=14)

            self.lbl_timer = tk.Label(top, text="⏱ 60:00", font=self.fonts["h3"], bg=PALETTE["nav_accent"], fg="#BFDBFE", padx=12, pady=5)
            self.lbl_timer.pack(side="right", padx=8)
            self.lbl_score_live = tk.Label(top, text="Бал: 0", font=self.fonts["h3"], bg=PALETTE["nav_accent"], fg="#A7F3D0", padx=12, pady=5)
            self.lbl_score_live.pack(side="right", padx=8)

            subj_bar = tk.Frame(self.main_container, bg=PALETTE["bg"])
            subj_bar.pack(fill="x", padx=18, pady=(8, 2))
            self.subj_tab_btns = []
            for idx, b in enumerate(self.plan):
                cname = SUBJECTS_CONFIG[b["subject"]]["name"]
                btn = RoundedButton(
                    subj_bar,
                    text=cname,
                    command=lambda i=idx: self._switch_block(i),
                    bg=PALETTE["card"],
                    hover_bg=PALETTE["soft_indigo"],
                    fg=PALETTE["text"],
                    border_color=PALETTE["border"],
                    font=self.fonts["bold_sm"],
                    radius=14,
                    height=30,
                    min_width=100,
                    pad_x=12,
                    parent_bg=PALETTE["bg"],
                )
                btn.pack(side="left", padx=(0, 8), pady=2)
                self.subj_tab_btns.append(btn)

            self._pane_orient = "horizontal"
            pane = tk.PanedWindow(self.main_container, orient="horizontal", bg=PALETTE["bg"], sashwidth=10, sashrelief="flat", bd=0)
            pane.pack(fill="both", expand=True, padx=18, pady=(6, 14))
            pane.bind("<Configure>", self._on_pane_configure)
            self._pane = pane

            # ЛІВА КОЛОНКА: Завдання (нижні кнопки закріплені ПЕРШИМИ з side="bottom", тому ніколи не зникають!)
            q_card = RoundedCard(pane, bg=PALETTE["card"], border=PALETTE["border"], parent_bg=PALETTE["bg"], radius=20, pad=16)
            pane.add(q_card, minsize=380, stretch="always")
            q_wrap = q_card.inner

            meta_row = tk.Frame(q_wrap, bg=PALETTE["card"])
            meta_row.pack(fill="x", pady=(0, 4))
            self.lbl_q_num = tk.Label(meta_row, text="", font=self.fonts["h3"], bg=PALETTE["card"], fg=PALETTE["primary"])
            self.lbl_q_num.pack(side="left")
            self.lbl_q_source = tk.Label(meta_row, text="", font=self.fonts["small"], bg=PALETTE["soft_indigo"], fg="#3730A3", padx=10, pady=3)
            self.lbl_q_source.pack(side="right")

            self.lbl_q_section = tk.Label(q_wrap, text="", font=self.fonts["small"], bg=PALETTE["card"], fg=PALETTE["muted"])
            self.lbl_q_section.pack(anchor="w", pady=(0, 6))

            # Закріплені нижні кнопки завдання (звичайний tk.Frame + .grid(), ніколи не зникають і не обрізаються)
            q_actions = tk.Frame(q_wrap, bg=PALETTE["card"])
            q_actions.pack(side="bottom", fill="x", pady=(10, 2))
            q_actions.columnconfigure(2, weight=1)
            self.btn_submit = RoundedButton(
                q_actions,
                text="✓ Перевірити відповідь",
                command=self._submit_question,
                bg=PALETTE["primary"],
                hover_bg=PALETTE["primary_hover"],
                fg="#FFFFFF",
                font=self.fonts["bold_sm"],
                radius=16,
                height=38,
                min_width=164,
                pad_x=12,
                parent_bg=PALETTE["card"],
            )
            self.btn_hint = RoundedButton(
                q_actions,
                text="💡 Підказка (1/10)",
                command=self._step_next_hint,
                bg=PALETTE["soft_amber"],
                hover_bg="#FEF08A",
                fg="#92400E",
                border_color=PALETTE["soft_amber_bd"],
                font=self.fonts["bold_sm"],
                radius=16,
                height=38,
                min_width=144,
                pad_x=10,
                parent_bg=PALETTE["card"],
            )
            self.btn_next = RoundedButton(
                q_actions,
                text="Далі →",
                command=self._next_question,
                bg=PALETTE["accent"],
                hover_bg=PALETTE["accent_hover"],
                fg="#FFFFFF",
                font=self.fonts["bold_sm"],
                radius=16,
                height=38,
                min_width=94,
                pad_x=12,
                parent_bg=PALETTE["card"],
            )
            q_actions._mode = None

            def _layout_q_actions(w=None):
                cur_w = w or q_actions.winfo_width() or 520
                mode = "wide" if cur_w >= 430 else "compact"
                if mode == q_actions._mode:
                    return
                q_actions._mode = mode
                self.btn_submit.grid_forget()
                self.btn_hint.grid_forget()
                self.btn_next.grid_forget()
                if mode == "wide":
                    self.btn_submit.grid(row=0, column=0, padx=(0, 6), sticky="w")
                    self.btn_hint.grid(row=0, column=1, padx=(0, 6), sticky="w")
                    self.btn_next.grid(row=0, column=2, sticky="e")
                else:
                    self.btn_submit.grid(row=0, column=0, padx=(0, 6), pady=(0, 6), sticky="w")
                    self.btn_hint.grid(row=0, column=1, pady=(0, 6), sticky="w")
                    self.btn_next.grid(row=1, column=0, columnspan=3, sticky="e")

            q_actions.bind("<Configure>", lambda e: _layout_q_actions(e.width))
            _layout_q_actions(520)

            self.q_scroll = SmoothScrollView(q_wrap, bg=PALETTE["card"], bottom_pad=24)
            self.q_scroll.pack(side="top", fill="both", expand=True, pady=4)
            self.q_inner = self.q_scroll.inner

            # ПРАВА КОЛОНКА: Закріплена Сова-Ліза + 10-рівневий степпер + ЄДИНА плавна область прокрутки
            t_card = RoundedCard(pane, bg=PALETTE["card"], border=PALETTE["border"], parent_bg=PALETTE["bg"], radius=20, pad=14)
            pane.add(t_card, minsize=360, stretch="always")
            t_wrap = t_card.inner

            owl_banner = RoundedCard(t_wrap, bg=PALETTE["soft_indigo"], border=PALETTE["soft_indigo_bd"], parent_bg=PALETTE["card"], radius=18, pad=10, shadow=False, height=106)
            owl_banner.pack(fill="x", pady=(0, 8))
            owl_banner.pack_propagate(False)
            ob_in = owl_banner.inner

            self.owl_tutor = OwlMascot(ob_in, size=86, bg=PALETTE["soft_indigo"])
            self.owl_tutor.pack(side="left", padx=(2, 10))

            owl_info = tk.Frame(ob_in, bg=PALETTE["soft_indigo"])
            owl_info.pack(side="left", fill="both", expand=True, pady=2)
            tk.Label(
                owl_info,
                text="Сова-Ліза • Мудрий Репетитор",
                font=self.fonts["h3"],
                bg=PALETTE["soft_indigo"],
                fg="#1E2B58",
            ).pack(anchor="w")
            self.lbl_owl_status = tk.Label(
                owl_info,
                text="Читаю умову разом із тобою. Тисни підказку (1–10) або обирай відповідь!",
                font=self.fonts["body_sm"],
                bg=PALETTE["soft_indigo"],
                fg="#334155",
                wraplength=280,
                justify="left",
            )
            self.lbl_owl_status.pack(anchor="w", pady=(3, 0))
            owl_info.bind("<Configure>", lambda e: self.lbl_owl_status.config(wraplength=max(160, e.width - 12)))

            # Шкала 10 рівнів підказок під Совою-Лізою
            self.hint_stepper = HintStepperBar(
                t_wrap,
                self.fonts,
                on_step=self._step_next_hint,
                on_select_level=self._show_hint_level,
                bg=PALETTE["card_soft"],
            )
            self.hint_stepper.pack(fill="x", pady=(0, 6))

            # ЄДИНА ПЛАВНА ОБЛАСТЬ ПРОКРУТКИ: Чат-бульбашки + Блок ідентичного прикладу!
            self.tutor_scroll = SmoothScrollView(t_wrap, bg=PALETTE["card"], bottom_pad=32)
            self.tutor_scroll.pack(fill="both", expand=True, pady=(2, 0))
            self.tutor_scroll.register_width_listener(self._on_tutor_width_change)

            self.chat_stack = tk.Frame(self.tutor_scroll.inner, bg=PALETTE["card"])
            self.chat_stack.pack(fill="x", padx=2, pady=(2, 4))

            # Блок ідентичних прикладів усередині тієї ж прокрутки — прокручується до самого низу!
            self.drill_card = RoundedCard(
                self.tutor_scroll.inner,
                bg=PALETTE["soft_mint"],
                border=PALETTE["soft_mint_bd"],
                parent_bg=PALETTE["card"],
                radius=18,
                pad=12,
                shadow=False,
                auto_height=True,
            )
            self.drill_frame = self.drill_card.inner

            self.timer_running = True

        def _on_tutor_width_change(self, new_w):
            wrap = max(160, new_w - 58)
            for lbl in list(self._chat_labels):
                try:
                    if lbl.winfo_exists():
                        lbl.config(wraplength=wrap)
                except Exception:
                    pass
            try:
                if self.drill_card.winfo_ismapped():
                    self.drill_card.sync_height(notify=False)
                self.tutor_scroll._schedule_sync(delay=20)
            except Exception:
                pass

        def _update_tab_styles(self):
            for idx, btn in enumerate(self.subj_tab_btns):
                if idx == self.current_block_idx:
                    btn.set_colors(bg=PALETTE["primary"], hover_bg=PALETTE["primary_hover"], fg="#FFFFFF", border_color=PALETTE["primary"])
                else:
                    btn.set_colors(bg=PALETTE["card"], hover_bg=PALETTE["soft_indigo"], fg=PALETTE["text"], border_color=PALETTE["border"])

        def _tick_timer(self):
            if not self.timer_running:
                return
            if self.timer_seconds > 0:
                self.timer_seconds -= 1
                mins, secs = divmod(self.timer_seconds, 60)
                hrs, mins = divmod(mins, 60)
                if hrs:
                    self.lbl_timer.config(text=f"⏱ {hrs}:{mins:02d}:{secs:02d}")
                else:
                    self.lbl_timer.config(text=f"⏱ {mins:02d}:{secs:02d}")
                self.root.after(1000, self._tick_timer)
            else:
                self.lbl_timer.config(text="⏱ Час вийшов!")

        def _append_chat(self, speaker_tag, speaker_title, message, body_tag=None):
            bg_map = {
                "student_lbl": PALETTE["card_soft"],
                "tutor_lbl": PALETTE["soft_indigo"],
                "err": PALETTE["soft_rose"],
            }
            bd_map = {
                "student_lbl": PALETTE["border"],
                "tutor_lbl": PALETTE["soft_indigo_bd"],
                "err": PALETTE["soft_rose_bd"],
            }
            title_col = {
                "student_lbl": "#475569",
                "tutor_lbl": PALETTE["primary"],
                "err": PALETTE["err_fg"],
            }
            if body_tag == "ok":
                b_bg, b_bd, b_fg = PALETTE["ok_bg"], "#86EFAC", PALETTE["ok_fg"]
            elif body_tag == "hint":
                b_bg, b_bd, b_fg = PALETTE["soft_amber"], PALETTE["soft_amber_bd"], "#78350F"
            elif body_tag == "rule":
                b_bg, b_bd, b_fg = "#EEF2FF", "#A5B4FC", PALETTE["text"]
            else:
                b_bg = bg_map.get(speaker_tag, PALETTE["card_soft"])
                b_bd = bd_map.get(speaker_tag, PALETTE["border"])
                b_fg = PALETTE["text"]

            bubble = RoundedCard(
                self.chat_stack,
                bg=b_bg,
                border=b_bd,
                parent_bg=PALETTE["card"],
                radius=15,
                pad=10,
                shadow=False,
                auto_height=True,
            )
            bubble.pack(fill="x", pady=(0, 6))

            try:
                cur_w = max(220, self.tutor_scroll.canvas.winfo_width() - 58)
            except Exception:
                cur_w = 340

            tk.Label(
                bubble.inner,
                text=speaker_title,
                font=self.fonts["bold_sm"],
                bg=b_bg,
                fg=title_col.get(speaker_tag, PALETTE["primary"]),
                anchor="w",
            ).pack(anchor="w")
            lbl_msg = tk.Label(
                bubble.inner,
                text=message,
                font=self.fonts["body_sm"],
                bg=b_bg,
                fg=b_fg,
                wraplength=cur_w,
                justify="left",
            )
            lbl_msg.pack(anchor="w", pady=(2, 0))
            self._chat_labels.append(lbl_msg)
            self.tutor_scroll.scroll_to_bottom(delay_ms=50)

        def _clear_chat(self):
            self._chat_labels = []
            for w in self.chat_stack.winfo_children():
                w.destroy()

        def _switch_block(self, b_idx):
            self.current_block_idx = b_idx
            self.current_q_idx = 0
            self._load_current_question()

        def _build_answer_widgets(self, parent, q, bg_color, is_drill=False):
            qt = q["qtype"]
            try:
                base_wrap = max(220, parent.winfo_width() - 28) if parent.winfo_width() > 80 else 440
            except Exception:
                base_wrap = 440

            lbl_prompt = tk.Label(parent, text=q["prompt"], font=self.fonts["body"], bg=bg_color, fg=PALETTE["text"], justify="left", wraplength=base_wrap)
            lbl_prompt.pack(anchor="w", pady=(2, 10))
            parent.bind("<Configure>", lambda e, lbl=lbl_prompt: lbl.config(wraplength=max(200, e.width - 24)))

            if qt == "single":
                var = tk.StringVar(value="")
                active_bg = "#D1FAE5" if is_drill else PALETTE["soft_indigo"]
                active_bd = PALETTE["accent"] if is_drill else PALETTE["primary"]
                for lbl, opt in zip(q["labels"], q["options"]):
                    row = RoundedOptionRow(parent, lbl, opt, var, self.fonts, base_bg=bg_color, active_bg=active_bg, active_bd=active_bd)
                    row.pack(fill="x", pady=3)
                return lambda: var.get()

            elif qt == "short":
                tk.Label(parent, text="Відповідь (число або десятковий дріб):", font=self.fonts["small"], bg=bg_color, fg=PALETTE["muted"]).pack(anchor="w")
                ent_wrap = tk.Frame(parent, bg=PALETTE["border"], padx=1, pady=1)
                ent_wrap.pack(anchor="w", pady=6)
                ent = tk.Entry(ent_wrap, font=self.fonts["h3"], width=20, bg="#FFFFFF", fg=PALETTE["text"], insertbackground=PALETTE["text"], relief="flat", bd=6)
                ent.pack()
                return lambda: ent.get().strip()

            elif qt == "matching":
                right_box = tk.Frame(parent, bg=PALETTE["card_soft"], highlightbackground=PALETTE["border"], highlightthickness=1)
                right_box.pack(fill="x", pady=(2, 8))
                r_lbls = []
                for rk, rv in q["right"].items():
                    rl = tk.Label(right_box, text=f"{rk}) {rv}", font=self.fonts["small"], bg=PALETTE["card_soft"], fg=PALETTE["text"], wraplength=max(200, base_wrap - 20), justify="left")
                    rl.pack(anchor="w", padx=10, pady=2)
                    r_lbls.append(rl)
                right_box.bind("<Configure>", lambda e, lst=r_lbls: [x.config(wraplength=max(180, e.width - 24)) for x in lst])

                choices = list(q["right"].keys())
                combos = {}
                for idx, row_text in enumerate(q["left"], 1):
                    row_f = tk.Frame(parent, bg=bg_color)
                    row_f.pack(fill="x", pady=4)
                    l_lbl = tk.Label(row_f, text=row_text, font=self.fonts["body_sm"], bg=bg_color, fg=PALETTE["text"], wraplength=max(160, base_wrap - 90), justify="left")
                    l_lbl.pack(side="left", anchor="w", fill="x", expand=True)
                    cb = ttk.Combobox(row_f, values=choices, state="readonly", width=5, font=self.fonts["bold"])
                    cb.pack(side="right", padx=(8, 4))
                    row_f.bind("<Configure>", lambda e, ll=l_lbl: ll.config(wraplength=max(140, e.width - 86)))
                    combos[str(idx)] = cb
                return lambda: {k: c.get() for k, c in combos.items()}

            elif qt == "sequence":
                s_lbls = []
                for k, v in q["items"].items():
                    sl = tk.Label(parent, text=f"{k}) {v}", font=self.fonts["body_sm"], bg=bg_color, fg=PALETTE["text"], wraplength=base_wrap, justify="left")
                    sl.pack(anchor="w", pady=2)
                    s_lbls.append(sl)
                parent.bind("<Configure>", lambda e, lbl=lbl_prompt, lst=s_lbls: [lbl.config(wraplength=max(160, e.width - 24))] + [x.config(wraplength=max(160, e.width - 24)) for x in lst])

                grid_f = tk.Frame(parent, bg=bg_color)
                grid_f.pack(fill="x", pady=8)
                letters = list(q["items"].keys())
                cbs = []
                for pos in range(1, 5):
                    r_i, c_i = divmod(pos - 1, 2)
                    cell = tk.Frame(grid_f, bg=bg_color)
                    cell.grid(row=r_i, column=c_i, sticky="w", padx=(0, 14), pady=3)
                    tk.Label(cell, text=f"{pos}-е:", font=self.fonts["bold_sm"], bg=bg_color, fg=PALETTE["text"]).pack(side="left", padx=(0, 4))
                    cb = ttk.Combobox(cell, values=letters, state="readonly", width=4, font=self.fonts["bold"])
                    cb.pack(side="left")
                    cbs.append(cb)
                return lambda: "".join(c.get() for c in cbs)

            elif qt == "multi3":
                vars_map = {}
                active_bg = "#D1FAE5" if is_drill else PALETTE["soft_indigo"]
                active_bd = PALETTE["accent"] if is_drill else PALETTE["primary"]
                for k, v in q["items"].items():
                    bv = tk.BooleanVar(value=False)
                    vars_map[k] = bv
                    row = RoundedCheckRow(parent, k, v, bv, self.fonts, base_bg=bg_color, active_bg=active_bg, active_bd=active_bd)
                    row.pack(fill="x", pady=2)
                return lambda: [k for k, bv in vars_map.items() if bv.get()]

            return lambda: ""

        def _load_current_question(self):
            block = self.plan[self.current_block_idx]
            cfg = SUBJECTS_CONFIG[block["subject"]]
            qs = block["questions"]
            q = qs[self.current_q_idx]

            self._update_tab_styles()
            self.lbl_subj_title.config(text=f"{cfg['name']} ({self.current_block_idx + 1}/{len(self.plan)})")
            self.lbl_q_num.config(text=f"Завдання {self.current_q_idx + 1} із {len(qs)}  •  макс. {q.get('max_points', 1)} б.")
            self.lbl_q_source.config(text=q.get("source", ""))
            self.lbl_q_section.config(text=f"Тема: {q.get('section', '')}")

            earned_total = sum(block["points"].values())
            max_so_far = sum(item.get("max_points", 1) for item in qs)
            self.lbl_score_live.config(text=f"Бал: {earned_total} / {max_so_far}")

            for w in self.q_inner.winfo_children():
                w.destroy()
            self.q_scroll.scroll_to_top(immediate=True)

            self.active_answer_getter = self._build_answer_widgets(self.q_inner, q, PALETTE["card"], is_drill=False)
            self.drill_card.pack_forget()
            self.active_drill = None

            self.q_hints_10 = build_10_hints(q)
            self.q_hint_level = 0
            self.hint_stepper.set_level(0)
            self.btn_hint.set_text("💡 Підказка (1/10)")
            self.btn_hint.set_state("normal" if self.tutor_mode else "disabled")

            self._clear_chat()
            self.tutor_scroll.scroll_to_top(immediate=True)
            self.owl_tutor.set_mood("idle")
            if self.tutor_mode:
                self.lbl_owl_status.config(text="Уважно прочитай умову. Якщо застрягнеш — відкривай підказки по кроках (1 → 10)!")
                self._append_chat(
                    "tutor_lbl",
                    "🦉 Сова-Ліза:",
                    f"Ми на завданні №{self.current_q_idx + 1} ({q['section']}). "
                    "Спробуй розв’язати самостійно або натисни «Підказка (1/10)» — я проведу тебе крок за кроком від легкого натяку до повної розповіді!"
                )
            else:
                self.lbl_owl_status.config(text="Режим іспиту: фіксую твої відповіді. Після фінішу розберемо кожну помилку!")
                self._append_chat(
                    "tutor_lbl",
                    "⏱ Режим іспиту:",
                    "Відповідай на завдання блоку. Детальний розбір помилок та опрацювання ідентичних прикладів будуть доступні після завершення."
                )

            already = self.current_q_idx in block["answers"]
            self.btn_submit.set_state("disabled" if already else "normal")

        def _step_next_hint(self):
            if self.q_hint_level >= 10:
                return
            self._show_hint_level(self.q_hint_level + 1)

        def _show_hint_level(self, level):
            if not self.tutor_mode:
                messagebox.showinfo("Режим іспиту", "У режимі іспиту підказки вимкнені — перевірка буде наприкінці.")
                return
            lvl = max(1, min(10, int(level)))
            if not self.q_hints_10:
                block = self.plan[self.current_block_idx]
                self.q_hints_10 = build_10_hints(block["questions"][self.current_q_idx])

            if lvl > self.q_hint_level:
                # Відкриваємо проміжні рівні послідовно або прямо до обраного рівня
                start_lvl = self.q_hint_level + 1
                self._append_chat("student_lbl", "🎓 Учень:", f"Сова-Ліза, дай підказку рівня {lvl}/10!")
                for cur in range(start_lvl, lvl + 1):
                    self._append_chat(
                        "tutor_lbl",
                        f"🦉 Сова-Ліза • Підказка {cur}/10:",
                        self.q_hints_10[cur - 1],
                        body_tag=("ok" if cur == 10 else "hint"),
                    )
                self.q_hint_level = lvl
            else:
                # Повторно показуємо обраний рівень із лінійки 1..10
                self._append_chat(
                    "tutor_lbl",
                    f"🦉 Сова-Ліза • Повтор підказки {lvl}/10:",
                    self.q_hints_10[lvl - 1],
                    body_tag=("ok" if lvl == 10 else "hint"),
                )

            self.hint_stepper.set_level(self.q_hint_level)
            if self.q_hint_level < 10:
                self.btn_hint.set_text(f"💡 Підказка ({self.q_hint_level + 1}/10)")
                self.btn_hint.set_state("normal")
                self.owl_tutor.set_mood("thinking")
                self.lbl_owl_status.config(text=f"Підказка {self.q_hint_level}/10 відкрита! Якщо треба глибше — натисни наступний рівень.")
            else:
                self.btn_hint.set_text("💡 Усі 10/10 відкрито")
                self.btn_hint.set_state("disabled")
                self.owl_tutor.set_mood("explain")
                self.lbl_owl_status.config(text="Ось повна розповідь і правило (10/10)! Тепер сміливо закріпимо на прикладі.")
            self.tutor_scroll.scroll_to_bottom(delay_ms=60)

        def _submit_question(self):
            block = self.plan[self.current_block_idx]
            q = block["questions"][self.current_q_idx]
            u_ans = self.active_answer_getter()

            if u_ans in ("", []) or (isinstance(u_ans, dict) and not any(u_ans.values())):
                messagebox.showinfo("Немає відповіді", "Спочатку оберіть або введіть варіант відповіді.")
                return

            ok, pts, u_repr, c_repr = evaluate_answer(q, u_ans)
            block["answers"][self.current_q_idx] = u_ans
            block["points"][self.current_q_idx] = pts
            self.btn_submit.set_state("disabled")

            earned_total = sum(block["points"].values())
            max_so_far = sum(item.get("max_points", 1) for item in block["questions"])
            self.lbl_score_live.config(text=f"Бал: {earned_total} / {max_so_far}")

            if not ok and self.current_q_idx not in block["mistakes"]:
                block["mistakes"].append(self.current_q_idx)

            if not self.tutor_mode:
                self._append_chat("student_lbl", "🎓 Учень:", f"Відповідь збережено: {u_repr}")
                self._next_question()
                return

            self._append_chat("student_lbl", "🎓 Учень:", f"Моя відповідь: {u_repr}")
            if ok:
                self.owl_tutor.set_mood("happy")
                self.lbl_owl_status.config(text="Браво! Абсолютно точно! Рухаймося далі з таким же темпом!")
                self._append_chat(
                    "tutor_lbl",
                    "🦉 Сова-Ліза:",
                    f"✅ Чудово! Абсолютно правильно (+{pts} б.).\n{q['solution']}",
                    body_tag="ok"
                )
            else:
                self.owl_tutor.set_mood("explain")
                self.lbl_owl_status.config(text="Нічого страшного! Зараз усе просто поясню й попрактикуємося на ідентичному прикладі нижче.")
                self._append_chat(
                    "err",
                    "🦉 Сова-Ліза — є помилка! Нумо розберемо зрозуміло:",
                    f"Ти відповів(ла): {u_repr}, а правильна відповідь: {c_repr} (набрано {pts} із {q.get('max_points', 1)} б.)."
                )
                self._append_chat("tutor_lbl", "📘 Правило простими словами:", q["rule"], body_tag="rule")
                self._append_chat("tutor_lbl", "🔍 Покроковий розбір саме цього завдання:", q["solution"])
                self._launch_identical_drill(q)

        def _launch_identical_drill(self, source_q):
            self.drill_used_prompts = [source_q["prompt"]]
            self._show_new_drill(source_q)

        def _show_new_drill(self, source_q):
            drill = generate_identical_drill(source_q, used_prompts=self.drill_used_prompts)
            self.drill_used_prompts.append(drill["prompt"])
            self.active_drill = (source_q, drill)
            self.drill_hints_10 = build_10_hints(drill)
            self.drill_hint_level = 0

            for w in self.drill_frame.winfo_children():
                w.destroy()
            self.drill_card.pack(fill="x", padx=2, pady=(8, 18))

            hdr = tk.Frame(self.drill_frame, bg=PALETTE["soft_mint"])
            hdr.pack(fill="x", pady=(0, 6))
            lbl_hdr = tk.Label(
                hdr,
                text="🔁 Опрацювання на ідентичному прикладі (закріплюємо правило!):",
                font=self.fonts["h3"],
                bg=PALETTE["soft_mint"],
                fg="#0F766E",
                wraplength=240,
                justify="left",
            )
            lbl_hdr.pack(side="left", fill="x", expand=True)
            RoundedButton(
                hdr,
                text="⤢ На весь екран",
                command=self._open_drill_fullscreen,
                bg="#FFFFFF",
                hover_bg="#D1FAE5",
                fg="#0F766E",
                border_color=PALETTE["soft_mint_bd"],
                font=self.fonts["small"],
                radius=11,
                height=26,
                min_width=112,
                pad_x=8,
                parent_bg=PALETTE["soft_mint"],
            ).pack(side="right", padx=(6, 0))
            hdr.bind("<Configure>", lambda e, l=lbl_hdr: l.config(wraplength=max(130, e.width - 130)))

            inner = tk.Frame(self.drill_frame, bg=PALETTE["soft_mint"])
            inner.pack(fill="x", pady=2)
            self.drill_answer_getter = self._build_answer_widgets(inner, drill, PALETTE["soft_mint"], is_drill=True)

            self.lbl_drill_fb = tk.Label(
                self.drill_frame,
                text="",
                font=self.fonts["body_sm"],
                bg=PALETTE["soft_mint"],
                fg=PALETTE["text"],
                wraplength=260,
                justify="left",
            )
            self.drill_frame.bind("<Configure>", lambda e, l=self.lbl_drill_fb: l.config(wraplength=max(160, e.width - 16)))

            # Адаптивна 2-рядна .grid() панель кнопок (ніколи не обрізається й не перекривається)
            d_btns = tk.Frame(self.drill_frame, bg=PALETTE["soft_mint"])
            d_btns.pack(fill="x", pady=(10, 2))
            btn_chk = RoundedButton(
                d_btns,
                text="✓ Перевірити",
                command=self._submit_drill,
                bg=PALETTE["accent"],
                hover_bg=PALETTE["accent_hover"],
                fg="#FFFFFF",
                font=self.fonts["bold_sm"],
                radius=14,
                height=34,
                min_width=120,
                pad_x=12,
                parent_bg=PALETTE["soft_mint"],
            )
            self.btn_drill_hint = RoundedButton(
                d_btns,
                text="💡 Підказка (1/10)",
                command=self._step_drill_hint,
                bg=PALETTE["soft_amber"],
                hover_bg="#FEF08A",
                fg="#92400E",
                border_color=PALETTE["soft_amber_bd"],
                font=self.fonts["small"],
                radius=14,
                height=34,
                min_width=128,
                pad_x=10,
                parent_bg=PALETTE["soft_mint"],
            )
            btn_other = RoundedButton(
                d_btns,
                text="Інший ↻",
                command=lambda: self._show_new_drill(source_q),
                bg="#FFFFFF",
                hover_bg="#D1FAE5",
                fg="#0F766E",
                border_color=PALETTE["soft_mint_bd"],
                font=self.fonts["small"],
                radius=14,
                height=34,
                min_width=88,
                pad_x=10,
                parent_bg=PALETTE["soft_mint"],
            )

            d_btns._mode = None

            def _layout_drill_btns(w=None):
                cur_w = w or d_btns.winfo_width() or 380
                mode = "wide" if cur_w >= 362 else "compact"
                if mode == d_btns._mode:
                    return
                d_btns._mode = mode
                btn_chk.grid_forget()
                self.btn_drill_hint.grid_forget()
                btn_other.grid_forget()
                if mode == "wide":
                    btn_chk.grid(row=0, column=0, padx=(0, 6), pady=(0, 2), sticky="w")
                    self.btn_drill_hint.grid(row=0, column=1, padx=(0, 6), pady=(0, 2), sticky="w")
                    btn_other.grid(row=0, column=2, pady=(0, 2), sticky="w")
                else:
                    btn_chk.grid(row=0, column=0, padx=(0, 6), pady=(0, 6), sticky="w")
                    self.btn_drill_hint.grid(row=0, column=1, pady=(0, 6), sticky="w")
                    btn_other.grid(row=1, column=0, columnspan=2, sticky="w")
                self.drill_card._schedule_auto_height()

            d_btns.bind("<Configure>", lambda e: _layout_drill_btns(e.width))
            _layout_drill_btns(380)

            self.drill_card.sync_height(notify=True)
            self.tutor_scroll.sync_scrollregion()
            self.tutor_scroll.scroll_to_bottom(delay_ms=70)
            self.root.after(240, self._realign_drill_scroll)

        def _realign_drill_scroll(self):
            try:
                if self.drill_card.winfo_exists() and self.drill_card.winfo_ismapped():
                    self.drill_card.sync_height(notify=True)
                    self.tutor_scroll.scroll_to_bottom(delay_ms=20)
            except Exception:
                pass

        def _open_drill_fullscreen(self):
            if not self.active_drill:
                return
            source_q, drill = self.active_drill
            if self._drill_modal is not None:
                try:
                    self._drill_modal.destroy()
                except Exception:
                    pass

            win = tk.Toplevel(self.root)
            win.title("🔁 Опрацювання ідентичного прикладу • Сова-Ліза")
            try:
                sw = self.root.winfo_screenwidth()
                sh = self.root.winfo_screenheight()
            except Exception:
                sw, sh = 1280, 800
            mw = min(820, max(520, sw - 100))
            mh = min(680, max(440, sh - 120))
            win.geometry(f"{mw}x{mh}+{(sw - mw)//2}+{(sh - mh)//2}")
            win.configure(bg=PALETTE["bg"])
            self._drill_modal = win

            card = RoundedCard(win, bg=PALETTE["soft_mint"], border=PALETTE["soft_mint_bd"], parent_bg=PALETTE["bg"], radius=20, pad=16)
            card.pack(fill="both", expand=True, padx=16, pady=16)

            top_m = tk.Frame(card.inner, bg=PALETTE["soft_mint"])
            top_m.pack(side="top", fill="x", pady=(0, 8))
            tk.Label(top_m, text="🔁 Ідентичний приклад (повний екран)", font=self.fonts["h2"], bg=PALETTE["soft_mint"], fg="#0F766E").pack(side="left")
            RoundedButton(
                top_m,
                text="✕ Згорнути",
                command=win.destroy,
                bg="#FFFFFF",
                hover_bg="#FEE2E2",
                fg=PALETTE["text"],
                border_color=PALETTE["border"],
                font=self.fonts["small"],
                radius=12,
                height=28,
                min_width=95,
                parent_bg=PALETTE["soft_mint"],
            ).pack(side="right")

            btns_m = tk.Frame(card.inner, bg=PALETTE["soft_mint"])
            btns_m.pack(side="bottom", fill="x", pady=(10, 0))

            m_scroll = SmoothScrollView(card.inner, bg=PALETTE["soft_mint"], bottom_pad=24)
            m_scroll.pack(side="top", fill="both", expand=True)

            getter = self._build_answer_widgets(m_scroll.inner, drill, PALETTE["soft_mint"], is_drill=True)
            lbl_fb = tk.Label(m_scroll.inner, text="", font=self.fonts["body_sm"], bg=PALETTE["soft_mint"], fg=PALETTE["text"], wraplength=mw - 100, justify="left")
            lbl_fb.pack(anchor="w", pady=(10, 4))
            m_scroll.sync_scrollregion()

            def _submit_modal():
                d_ans = getter()
                if d_ans in ("", []) or (isinstance(d_ans, dict) and not any(d_ans.values())):
                    messagebox.showinfo("Немає відповіді", "Обери або введи відповідь.", parent=win)
                    return
                ok, _, u_repr, c_repr = evaluate_answer(drill, d_ans)
                self.plan[self.current_block_idx]["drills_done"] += 1
                self._append_chat("student_lbl", "🎓 Учень (ідентичний приклад):", f"Моя відповідь: {u_repr}")
                if ok:
                    self.owl_tutor.set_mood("happy")
                    self.lbl_owl_status.config(text="Ура! Тепер ти точно знаєш це правило! Можеш тиснути «Далі →».")
                    lbl_fb.config(text=f"✅ Супер! «{u_repr}» — правильно!\n{drill['solution']}", fg=PALETTE["ok_fg"])
                    self._append_chat("tutor_lbl", "🦉 Сова-Ліза:", f"✅ Супер! «{u_repr}» — правильно!\n{drill['solution']}", body_tag="ok")
                else:
                    self.owl_tutor.set_mood("explain")
                    lbl_fb.config(text=f"❌ Неточність ({u_repr}). Правильна відповідь: {c_repr}.\n🔍 Розбір: {drill['solution']}", fg=PALETTE["err_fg"])
                    self._append_chat("err", "🦉 Сова-Ліза (перевірка прикладу):", f"Неточність ({u_repr}). Правильна відповідь: {c_repr}.\n{drill['solution']}")
                m_scroll.scroll_to_bottom(delay_ms=40)

            def _hint_modal():
                if self.drill_hint_level >= 10:
                    return
                self.drill_hint_level += 1
                lvl = self.drill_hint_level
                lbl_fb.config(text=f"💡 Підказка {lvl}/10:\n{self.drill_hints_10[lvl - 1]}", fg="#78350F")
                self._step_drill_hint_update_ui(lvl)
                m_scroll.scroll_to_bottom(delay_ms=40)

            RoundedButton(btns_m, text="✓ Перевірити", command=_submit_modal, bg=PALETTE["accent"], hover_bg=PALETTE["accent_hover"], fg="#FFFFFF", font=self.fonts["bold_sm"], radius=14, height=36, min_width=130, parent_bg=PALETTE["soft_mint"]).pack(side="left", padx=(0, 8))
            RoundedButton(btns_m, text="💡 Підказка (1..10)", command=_hint_modal, bg=PALETTE["soft_amber"], hover_bg="#FEF08A", fg="#92400E", border_color=PALETTE["soft_amber_bd"], font=self.fonts["small"], radius=14, height=36, min_width=145, parent_bg=PALETTE["soft_mint"]).pack(side="left", padx=(0, 8))
            RoundedButton(btns_m, text="Інший приклад ↻", command=lambda: (win.destroy(), self._show_new_drill(source_q), self._open_drill_fullscreen()), bg="#FFFFFF", hover_bg="#D1FAE5", fg="#0F766E", border_color=PALETTE["soft_mint_bd"], font=self.fonts["small"], radius=14, height=36, min_width=130, parent_bg=PALETTE["soft_mint"]).pack(side="right")

        def _step_drill_hint_update_ui(self, lvl):
            if hasattr(self, "btn_drill_hint") and self.btn_drill_hint.winfo_exists():
                if lvl < 10:
                    self.btn_drill_hint.set_text(f"💡 Підказка ({lvl + 1}/10)")
                else:
                    self.btn_drill_hint.set_text("💡 10/10")
                    self.btn_drill_hint.set_state("disabled")

        def _step_drill_hint(self):
            if not self.active_drill or self.drill_hint_level >= 10:
                return
            self.drill_hint_level += 1
            lvl = self.drill_hint_level
            self.owl_tutor.set_mood("thinking")
            self._append_chat(
                "tutor_lbl",
                f"🦉 Сова-Ліза (до прикладу • {lvl}/10):",
                self.drill_hints_10[lvl - 1],
                body_tag=("ok" if lvl == 10 else "hint"),
            )
            if hasattr(self, "lbl_drill_fb") and self.lbl_drill_fb.winfo_exists():
                self.lbl_drill_fb.config(text=f"💡 Підказка {lvl}/10:\n{self.drill_hints_10[lvl - 1]}", fg="#78350F")
                self.lbl_drill_fb.pack(anchor="w", pady=(6, 2))
                self.drill_card.sync_height(notify=True)
            self._step_drill_hint_update_ui(lvl)
            self.tutor_scroll.scroll_to_bottom(delay_ms=60)

        def _submit_drill(self):
            if not self.active_drill:
                return
            source_q, drill = self.active_drill
            d_ans = self.drill_answer_getter()
            if d_ans in ("", []) or (isinstance(d_ans, dict) and not any(d_ans.values())):
                messagebox.showinfo("Немає відповіді", "Розв’яжи схожий приклад та обери/введи відповідь.")
                return

            ok, _, u_repr, c_repr = evaluate_answer(drill, d_ans)
            self.plan[self.current_block_idx]["drills_done"] += 1

            self._append_chat("student_lbl", "🎓 Учень (ідентичний приклад):", f"Моя відповідь: {u_repr}")
            if ok:
                self.owl_tutor.set_mood("happy")
                self.lbl_owl_status.config(text="Ура! Тепер ти точно знаєш це правило! Можеш тиснути «Далі →».")
                if hasattr(self, "lbl_drill_fb") and self.lbl_drill_fb.winfo_exists():
                    self.lbl_drill_fb.config(text=f"✅ Правильно («{u_repr}»)! {drill['solution']}", fg=PALETTE["ok_fg"])
                    self.lbl_drill_fb.pack(anchor="w", pady=(6, 2))
                    self.drill_card.sync_height(notify=True)
                self._append_chat(
                    "tutor_lbl",
                    "🦉 Сова-Ліза:",
                    f"✅ Супер! «{u_repr}» — правильно!\n{drill['solution']}\nТепер ти впевнено впораєшся з таким типом завдань на НМТ. Можемо рухатися далі (або натисни «Інший ↻» для ще одного тренування).",
                    body_tag="ok"
                )
            else:
                self.owl_tutor.set_mood("explain")
                self.lbl_owl_status.config(text="Майже вийшло! Перевір розбір і спробуй ще один ідентичний приклад нижче.")
                self._append_chat(
                    "err",
                    "🦉 Сова-Ліза (перевірка схожого прикладу):",
                    f"Знову є неточність ({u_repr}). Правильна відповідь: {c_repr}.\n🔍 Поглянь крок за кроком: {drill['solution']}\nСпробуймо ще один ідентичний приклад!"
                )
                self._show_new_drill(source_q)

        def _next_question(self):
            block = self.plan[self.current_block_idx]
            if self.current_q_idx + 1 < len(block["questions"]):
                self.current_q_idx += 1
                self._load_current_question()
            elif self.current_block_idx + 1 < len(self.plan):
                self.current_block_idx += 1
                self.current_q_idx = 0
                self._load_current_question()
            else:
                self._finish_session()

        # -------------------------------------------------------------------
        # 3. ЕКРАН РЕЗУЛЬТАТІВ ТА ОЦІНКИ 100–200
        # -------------------------------------------------------------------
        def _finish_session(self):
            self._clear_main()

            header = tk.Frame(self.main_container, bg=PALETTE["nav"], height=70)
            header.pack(fill="x")
            header.pack_propagate(False)
            tk.Label(header, text="📊 Результати тренування НМТ (шкала 100–200)", font=self.fonts["h1"], bg=PALETTE["nav"], fg="#FFFFFF").pack(side="left", padx=24, pady=18)

            wrap = tk.Frame(self.main_container, bg=PALETTE["bg"])
            wrap.pack(fill="both", expand=True, padx=24, pady=14)

            has_mistakes = any(b["mistakes"] for b in self.plan)
            top_owl_card = RoundedCard(wrap, bg=PALETTE["soft_indigo"], border=PALETTE["soft_indigo_bd"], parent_bg=PALETTE["bg"], radius=18, pad=12, shadow=False, height=112)
            top_owl_card.pack(fill="x", pady=(0, 12))
            top_owl_card.pack_propagate(False)
            owl_res = OwlMascot(top_owl_card.inner, size=88, bg=PALETTE["soft_indigo"])
            owl_res.set_mood("explain" if has_mistakes else "happy")
            owl_res.pack(side="left", padx=(4, 14))
            res_msg = (
                "Чудова робота! У тебе є кілька помилок, і ми можемо прямо зараз відпрацювати їх на ідентичних прикладах!"
                if has_mistakes
                else "Фантастично! Жодної помилки — ти повністю готовий(а) до такого варіанта НМТ!"
            )
            tk.Label(top_owl_card.inner, text="Підсумок від Сови-Лізи 🦉", font=self.fonts["h3"], bg=PALETTE["soft_indigo"], fg="#1E2B58").pack(anchor="w", pady=(8, 2))
            tk.Label(top_owl_card.inner, text=res_msg, font=self.fonts["body"], bg=PALETTE["soft_indigo"], fg="#334155", wraplength=780, justify="left").pack(anchor="w")

            rep_card = RoundedCard(wrap, bg=PALETTE["card"], border=PALETTE["border"], parent_bg=PALETTE["bg"], radius=20, pad=16)
            rep_card.pack(fill="both", expand=True)
            txt = tk.Text(rep_card.inner, wrap="word", font=self.fonts["body"], bg=PALETTE["card"], fg=PALETTE["text"], padx=10, pady=8, relief="flat")
            txt.pack(fill="both", expand=True)
            txt.insert("1.0", format_results_report(self.plan))
            txt.config(state="disabled")

            actions = tk.Frame(self.main_container, bg=PALETTE["bg"])
            actions.pack(fill="x", padx=24, pady=(0, 16))

            if has_mistakes:
                RoundedButton(
                    actions,
                    text="🔁 Відпрацювати помилки з Совою",
                    command=self._start_mistake_drill_session,
                    bg=PALETTE["primary"],
                    hover_bg=PALETTE["primary_hover"],
                    fg="#FFFFFF",
                    font=self.fonts["bold"],
                    radius=16,
                    height=40,
                    min_width=270,
                    parent_bg=PALETTE["bg"],
                ).pack(side="left", padx=(0, 10))
            RoundedButton(
                actions,
                text="💾 Зберегти звіт (.txt)",
                command=self._save_report,
                bg=PALETTE["accent"],
                hover_bg=PALETTE["accent_hover"],
                fg="#FFFFFF",
                font=self.fonts["bold"],
                radius=16,
                height=40,
                min_width=195,
                parent_bg=PALETTE["bg"],
            ).pack(side="left", padx=(0, 10))
            RoundedButton(
                actions,
                text="🏠 Обрати інші предмети",
                command=self.show_setup,
                bg=PALETTE["card"],
                hover_bg=PALETTE["soft_indigo"],
                fg=PALETTE["text"],
                border_color=PALETTE["border"],
                font=self.fonts["bold_sm"],
                radius=16,
                height=40,
                min_width=210,
                parent_bg=PALETTE["bg"],
            ).pack(side="right")

        def _start_mistake_drill_session(self):
            drill_plan = []
            for block in self.plan:
                if not block["mistakes"]:
                    continue
                qs = []
                for idx in block["mistakes"]:
                    orig = block["questions"][idx]
                    qs.append(generate_identical_drill(orig))
                drill_plan.append({
                    "subject": block["subject"],
                    "questions": qs,
                    "answers": {},
                    "points": {},
                    "mistakes": [],
                    "drills_done": 0,
                })
            if drill_plan:
                self.tutor_mode = True
                self.plan = drill_plan
                self.current_block_idx = 0
                self.current_q_idx = 0
                self.timer_seconds = 30 * 60
                self._build_test_view()
                self._load_current_question()
                self._tick_timer()

        def _save_report(self):
            path = filedialog.asksaveasfilename(
                title="Зберегти звіт",
                initialdir=get_user_data_dir(),
                defaultextension=".txt",
                initialfile=f"nmt_report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                filetypes=[("Text files", "*.txt")],
            )
            if not path:
                return
            with open(path, "w", encoding="utf-8") as f:
                f.write(format_results_report(self.plan))
            messagebox.showinfo("Збережено", f"Звіт збережено:\n{path}")


def main():
    if "--cli" in sys.argv or not HAS_TK:
        run_cli()
        return

    if sys.platform.startswith("win"):
        try:
            from ctypes import windll
            try:
                windll.shell32.SetCurrentProcessExplicitAppUserModelID("NMT.SovaTutor.Windows.3.2")
            except Exception:
                pass
            try:
                windll.shcore.SetProcessDpiAwareness(1)
            except Exception:
                try:
                    windll.user32.SetProcessDPIAware()
                except Exception:
                    pass
        except Exception:
            pass

    try:
        root = tk.Tk()
        NmtTutorApp(root)
        root.mainloop()
    except Exception as exc:
        print(f"Не вдалося запустити графічний інтерфейс ({exc}). Перемикаюся на консольний режим...")
        run_cli()


if __name__ == "__main__":
    main()
