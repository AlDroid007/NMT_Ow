// Task generators: Географія (port of generators/geography.py).

import { choice, pyMod, shuffle } from '../py'
import { GEN_SOURCE, LABELS4, registerDrill } from './common'

const TOPO = 'Загальна географія та топографія'

registerDrill('geo_map_scale', () => {
  const scaleM = choice([100, 200, 250, 500])
  const denom = scaleM * 100
  const dCm = choice([4, 6, 8, 9, 12, 15, 22])
  const ans = dCm * scaleM
  return {
    subject: 'geography',
    section: TOPO,
    source: GEN_SOURCE,
    qtype: 'short',
    max_points: 2,
    prompt: `На топографічній карті масштабу 1 : ${denom} довжина ділянки дороги становить ${dCm} см. Визначте дійсну відстань на місцевості (у метрах).`,
    answer: String(ans),
    hint: `Відкинь два останні нулі від ${denom}, щоб отримати масштаб у метрах (в 1 см — ${scaleM} м), і помнож на ${dCm}.`,
    rule: 'Золоте правило масштабу на НМТ: щоб перевести числовий масштаб 1 : N у метри, закресли 2 нулі праворуч (1 м = 100 см). Потім помнож число сантиметрів на карті на отриману кількість метрів.',
    solution: `Масштаб 1 : ${denom} означає, що в 1 см — ${scaleM} м. Відстань = ${dCm} · ${scaleM} = ${ans} м.`,
    drill_key: 'geo_map_scale',
  }
})

registerDrill('geo_azimuth', () => {
  const cases: Array<[string, string, number, number]> = [
    ['північного (0°)', 'на схід', 0, 1],
    ['східного (90°)', 'на північ (відхилення до півночі)', 90, -1],
    ['східного (90°)', 'на південь', 90, 1],
    ['південного (180°)', 'на схід', 180, -1],
    ['південного (180°)', 'на захід', 180, 1],
    ['західного (270°)', 'на північ', 270, 1],
    ['західного (270°)', 'на південь', 270, -1],
  ]
  const [baseTxt, dirTxt, baseDeg, sign] = choice(cases)
  const dev = choice([7, 12, 15, 18, 25])
  const az = pyMod(baseDeg + sign * dev, 360)
  return {
    subject: 'geography',
    section: TOPO,
    source: GEN_SOURCE,
    qtype: 'short',
    max_points: 2,
    prompt: `Визначте азимут (у градусах) руху, якщо напрямок відхиляється від ${baseTxt} напрямку ${dirTxt} на ${dev}°.`,
    answer: String(az),
    hint: 'Азимут відлічують ВІД ПІВНОЧІ (0°) ЗА ГОДИННИКОВОЮ СТРІЛКОЮ: Схід = 90°, Південь = 180°, Захід = 270°, Північ = 360°.',
    rule: 'Азимут завжди рахують від півночі (0°) за годинниковою стрілкою: Пн = 0°/360°, Сх = 90°, Пд = 180°, Зх = 270°. Намалюй хрестик сторін світу — рух за годинниковою стрілкою додає градуси, проти — віднімає.',
    solution: `Базовий азимут ${baseDeg}°, зсув ${dirTxt} на ${dev}° → ${baseDeg} ${sign > 0 ? '+' : '−'} ${dev} = ${az}°.`,
    drill_key: 'geo_azimuth',
  }
})

registerDrill('geo_ukr_extremes', () => {
  const pool: Array<[string, string]> = [
    ['північна', 'село Грем’яч (Чернігівська область)'],
    ['південна', 'мис Сарич (АР Крим)'],
    ['західна (найближча до Гринвіцького меридіана)', 'село Соломоново (Закарпатська область)'],
    ['східна', 'село Рання Зоря (Луганська область)'],
  ]
  const target = choice(pool)
  const opts = shuffle(pool.map((p) => p[1]))
  const labels = [...LABELS4]
  const ci = opts.indexOf(target[1])
  return {
    subject: 'geography',
    section: 'Фізична географія України',
    source: GEN_SOURCE,
    qtype: 'single',
    max_points: 1,
    prompt: `Позначте крайню ${target[0]} точку території України:`,
    options: opts,
    labels,
    answer: labels[ci],
    hint: 'Запам’ятай 4 крайні точки України: Грем’яч, Сарич, Соломоново, Рання Зоря.',
    rule: 'Чотири крайні точки України: Північ — Грем’яч, Південь — мис Сарич, Захід (найближче до Гринвіча) — Соломоново, Схід («раннє сонце») — Рання Зоря.',
    solution: `Крайня ${target[0]} точка — ${target[1]} (${labels[ci]}).`,
    drill_key: 'geo_ukr_extremes',
  }
})
