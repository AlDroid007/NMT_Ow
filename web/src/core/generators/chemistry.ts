// Task generators: Хімія (port of generators/chemistry.py).

import { choice, floorDiv } from '../py'
import { fixed2, fmtNum, GEN_SOURCE, registerDrill } from './common'

registerDrill('chem_gas_molar', () => {
  const n = choice([1.5, 2.0, 2.5, 3.0, 4.0])
  const molar = choice([28, 32, 44, 64, 128])
  const v = n * 22.4
  const mass = n * molar
  return {
    subject: 'chemistry',
    section: 'Обчислення в хімії',
    source: GEN_SOURCE,
    qtype: 'short',
    max_points: 2,
    prompt: `Маса газу об’ємом ${fmtNum(v)} л (н. у.) дорівнює ${fmtNum(mass)} г. Обчисліть молярну масу (г/моль) цього газу.`,
    answer: String(molar),
    hint: 'Спочатку знайди кількість речовини n = V / Vm (Vm = 22,4 л/моль), а потім M = m / n.',
    rule: 'За нормальних умов 1 моль будь-якого газу займає 22,4 л. Формули: n = V / 22,4 і M = m / n.',
    solution: `1) n = ${fmtNum(v)} / 22,4 = ${fmtNum(n)} моль.\n2) M = ${fmtNum(mass)} / ${fmtNum(n)} = ${molar} г/моль.`,
    drill_key: 'chem_gas_molar',
  }
})

registerDrill('chem_solution_sat', () => {
  const solPer100 = choice([150, 200, 250])
  const waterG = choice([20, 40, 50])
  const maxSalt = floorDiv(solPer100 * waterG, 100)
  const already = maxSalt - choice([10, 15, 20, 25])
  const need = maxSalt - already
  return {
    subject: 'chemistry',
    section: 'Обчислення в хімії',
    source: GEN_SOURCE,
    qtype: 'short',
    max_points: 2,
    prompt:
      `За температури 60 °C розчинність солі становить ${solPer100} г у 100 г води. ` +
      `У воді масою ${waterG} г розчинили ${already} г цієї солі. Обчисліть масу (г) солі, ` +
      `яку ще треба додати, щоб розчин став насиченим за 60 °C.`,
    answer: String(need),
    hint: `Розрахуй за пропорцією, скільки максимум солі розчиняється у ${waterG} г води, і відніми вже додані ${already} г.`,
    rule: 'Розчинність показує максимальну масу солі у 100 г води. Якщо води m_в, то гранична маса солі m_макс = S · (m_в / 100).',
    solution: `1) У ${waterG} г води може розчинитися максимум ${solPer100} · (${waterG}/100) = ${maxSalt} г.\n2) Потрібно додати: ${maxSalt} − ${already} = ${need} г.`,
    drill_key: 'chem_solution_sat',
  }
})

registerDrill('chem_yield', () => {
  const nEthene = choice([2, 3, 4, 5])
  const vEthene = nEthene * 22.4
  const eta = choice([50, 60, 75, 80])
  const massPract = (nEthene * 46 * eta) / 100
  return {
    subject: 'chemistry',
    section: 'Обчислення в хімії',
    source: GEN_SOURCE,
    qtype: 'short',
    max_points: 2,
    prompt: `Обчисліть масу (г) етанолу (M = 46 г/моль), що утвориться внаслідок гідратації етену об’ємом ${fmtNum(vEthene)} л (н. у.), якщо відносний вихід спирту становить ${eta} %.`,
    answer: fmtNum(massPract),
    hint: '1) Знайди кількість речовини етену n = V / 22,4; 2) стільки ж моль спирту утвориться теоретично (1:1); 3) помнож теоретичну масу на вихід η!',
    rule: 'C₂H₄ + H₂O → C₂H₅OH (коефіцієнти 1:1). Практична маса = m_теор · (вихід % / 100).',
    solution:
      `1) n(C₂H₄) = ${fmtNum(vEthene)} / 22,4 = ${nEthene} моль = n_теор(C₂H₅OH).\n` +
      `2) m_теор = ${nEthene} · 46 = ${nEthene * 46} г.\n` +
      `3) m_практ = ${nEthene * 46} · ${fixed2(eta / 100)} = ${fmtNum(massPract)} г.`,
    drill_key: 'chem_yield',
  }
})

registerDrill('chem_alkane_combust', () => {
  const nC = choice([3, 4, 5, 6])
  const nAlk = choice([0.2, 0.25, 0.5])
  const o2Coef = (3 * nC + 1) / 2.0
  const nO2 = nAlk * o2Coef
  const atoms = 3 * nC + 2
  return {
    subject: 'chemistry',
    section: 'Органічна хімія',
    source: GEN_SOURCE,
    qtype: 'short',
    max_points: 2,
    prompt:
      `Для повного окиснення алкану кількістю речовини ${fmtNum(nAlk)} моль витратили кисень ` +
      `кількістю речовини ${fmtNum(nO2)} моль. Визначте формулу алкану й зазначте у відповіді ` +
      `кількість УСІХ атомів у його молекулі.`,
    answer: String(atoms),
    hint: 'Знайди, скільки моль O₂ потрібно на 1 моль алкану: (3n + 1)/2 = n(O₂)/n(алкану), звідки знайдеш n!',
    rule: 'Загальне рівняння горіння алкану: CₙH₂ₙ₊₂ + ((3n+1)/2) O₂ → n CO₂ + (n+1) H₂O. Кількість усіх атомів у молекулі CₙH₂ₙ₊₂ дорівнює 3n + 2.',
    solution:
      `1) На 1 моль алкану потрібно ${fmtNum(nO2)} / ${fmtNum(nAlk)} = ${fmtNum(o2Coef)} моль O₂.\n` +
      `2) (3n + 1)/2 = ${fmtNum(o2Coef)} ⇒ 3n + 1 = ${3 * nC + 1} ⇒ n = ${nC} (C${nC}H${2 * nC + 2}).\n` +
      `3) Усього атомів: ${nC} + ${2 * nC + 2} = ${atoms}.`,
    drill_key: 'chem_alkane_combust',
  }
})
