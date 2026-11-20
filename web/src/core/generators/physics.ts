// Task generators: Фізика (port of generators/physics.py).

import { choice, floorDiv } from '../py'
import { fmtNum, GEN_SOURCE, LABELS4, registerDrill } from './common'

registerDrill('phys_free_fall', () => {
  const t = choice([2, 3, 4, 5, 6])
  const h = 5 * t * t
  return {
    subject: 'physics',
    section: 'Механіка',
    source: GEN_SOURCE,
    qtype: 'short',
    max_points: 2,
    prompt: `Визначте час вільного падіння тіла з висоти ${h} м зі стану спокою. Уважайте, що g = 10 м/с². Відповідь запишіть у секундах (с).`,
    answer: String(t),
    hint: 'Використай формулу шляху без початкової швидкості: h = (g · t²) / 2.',
    rule: 'Під час вільного падіння без початкової швидкості: h = g·t² / 2 ⇒ t = √(2h / g). При g = 10 м/с² це просто √(h / 5).',
    solution: `t = √(2 · ${h} / 10) = √(${floorDiv(2 * h, 10)}) = ${t} с.`,
    drill_key: 'phys_free_fall',
  }
})

registerDrill('phys_incline', () => {
  const m = choice([8, 12, 15, 18, 24, 30])
  const f = 5 * m
  return {
    subject: 'physics',
    section: 'Механіка',
    source: GEN_SOURCE,
    qtype: 'short',
    max_points: 2,
    prompt: `Санчата масою ${m} кг перебувають на схилі з кутом нахилу 30° до горизонту. Яку силу треба прикласти вздовж схилу вгору, щоб утримувати їх у рівновазі? Тертя не враховуйте, g = 10 м/с². Відповідь запишіть у ньютонах (Н).`,
    answer: String(f),
    hint: 'Сила вздовж похилої площини дорівнює скочувальній силі тяжіння: F = m · g · sin(α).',
    rule: 'На похилій площині без тертя утримувальна сила вздовж схилу дорівнює F = m·g·sin(α). Пам’ятай, що sin(30°) = 0,5!',
    solution: `F = m · g · sin(30°) = ${m} · 10 · 0,5 = ${f} Н.`,
    drill_key: 'phys_incline',
  }
})

registerDrill('phys_thermo_1law', () => {
  const q = choice([40, 50, 60, 80, 100])
  const a = choice([15, 20, 25, 30])
  const du = q - a
  return {
    subject: 'physics',
    section: 'Молекулярна фізика та термодинаміка',
    source: GEN_SOURCE,
    qtype: 'single',
    max_points: 1,
    prompt: `Ідеальному одноатомному газу незмінної маси надали ${q} Дж теплоти, і він виконав роботу ${a} Дж. Як змінилася внутрішня енергія цього газу?`,
    options: [
      `зменшилася на ${du} Дж`,
      `зменшилася на ${q + a} Дж`,
      `збільшилася на ${du} Дж`,
      `збільшилася на ${q + a} Дж`,
    ],
    labels: [...LABELS4],
    answer: 'В',
    hint: 'Перший закон термодинаміки: Q = ΔU + A (отримане тепло йде на зміну внутрішньої енергії та на роботу газу).',
    rule: 'Перший закон термодинаміки: Q = ΔU + A ⇒ ΔU = Q − A. Якщо ΔU > 0, внутрішня енергія збільшилася; якщо ΔU < 0 — зменшилася.',
    solution: `ΔU = Q − A = ${q} − ${a} = +${du} Дж → внутрішня енергія збільшилася на ${du} Дж (В).`,
    drill_key: 'phys_thermo_1law',
  }
})

registerDrill('phys_humidity', () => {
  const v = choice([0.5, 1.0, 2.0])
  const rhoSat = choice([20, 25])
  const phi0 = choice([30, 40, 50, 60])
  const mEvap = ((100 - phi0) / 100.0) * rhoSat * v
  const mSat = rhoSat * v
  return {
    subject: 'physics',
    section: 'Молекулярна фізика та термодинаміка',
    source: GEN_SOURCE,
    qtype: 'short',
    max_points: 2,
    prompt:
      `У герметичний балон об’ємом ${fmtNum(v)} м³ поставили посудину з водою. До насичення пари в балоні ` +
      `випарувалася вода масою ${fmtNum(mEvap)} г. Якою була початкова відносна вологість повітря в балоні (у %), ` +
      `якщо густина насиченої пари за цієї температури дорівнює ${rhoSat} г/м³?`,
    answer: String(phi0),
    hint: 'Спочатку знайди, скільки грамів пари може поміститися в балоні загалом (m_нас = ρ_нас · V), а потім відніми масу, що випарувалася!',
    rule: 'У стані насичення маса пари m_нас = ρ_нас · V (100 %). Початкова маса пари m₀ = m_нас − m_вип, а φ₀ = (m₀ / m_нас) · 100 %.',
    solution:
      `1) Маса насиченої пари в об’ємі ${fmtNum(v)} м³: m_нас = ${rhoSat} · ${fmtNum(v)} = ${fmtNum(mSat)} г.\n` +
      `2) Спочатку було пари: m₀ = ${fmtNum(mSat)} − ${fmtNum(mEvap)} = ${fmtNum(mSat - mEvap)} г.\n` +
      `3) φ₀ = (${fmtNum(mSat - mEvap)} / ${fmtNum(mSat)}) · 100 % = ${phi0} %.`,
    drill_key: 'phys_humidity',
  }
})

registerDrill('phys_halflife', () => {
  const halfLife = choice([5700, 1600, 30, 8])
  const n = choice([2, 3])
  const remPct = fmtNum(100 / 2 ** n)
  const ans = halfLife * n
  return {
    subject: 'physics',
    section: 'Квантова фізика та теорія відносності',
    source: GEN_SOURCE,
    qtype: 'short',
    max_points: 2,
    prompt: `У зразку залишилося ${remPct} % радіоактивного ізотопу, період піврозпаду якого становить ${halfLife} років. Скільки років минуло від початку розпаду?`,
    answer: String(ans),
    hint: 'За 1 період залишається 50 %, за 2 періоди — 25 %, за 3 періоди — 12,5 %!',
    rule: 'Закон радіоактивного розпаду: за кожен період T кількість речовини зменшується у 2 рази (100 % → 50 % → 25 % → 12,5 %). Час t = n · T.',
    solution: `${remPct} % = 100 % / 2^${n}, отже минуло n = ${n} періоди. Час t = ${n} · ${halfLife} = ${ans} років.`,
    drill_key: 'phys_halflife',
  }
})
