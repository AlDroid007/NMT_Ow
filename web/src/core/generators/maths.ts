// Task generators: Математика (port of generators/maths.py).

import { choice, floorDiv, randint, shuffle, signed } from '../py'
import { fixed2, fmtNum, gcd, GEN_SOURCE, LABELS5, registerDrill, sortedUnique } from './common'

registerDrill('math_ineq', () => {
  const a = choice([2, 3, 4, 5])
  const xBound = randint(4, 12)
  const b = randint(1, 15)
  const c = a * xBound + b
  const step = choice([2, 3, 5])
  const ans = xBound + step
  let vals = [xBound - 2 * step, xBound - step, xBound, ans, xBound + 2 * step]
  if (vals[0] < 0) vals = [0, xBound - 1, xBound, ans, ans + step]
  const labels = LABELS5
  const ci = vals.indexOf(ans)
  return {
    subject: 'math',
    section: 'Рівняння, нерівності та їх системи',
    source: GEN_SOURCE,
    qtype: 'single',
    max_points: 1,
    prompt: `Позначте з-поміж наведених найменше число, яке є розв’язком нерівності ${a}x + ${b} > ${c}.`,
    options: vals.map(String),
    labels: [...labels],
    answer: labels[ci],
    hint: `Перенеси ${b} праворуч, поділи на ${a} й уважно подивись на знак: строго '>' чи '≥'!`,
    rule: "Розв’язуємо як звичайне рівняння, але стежимо за строгим знаком '>'. Межове число за строгого знака '>' НЕ є розв’язком!",
    solution: `1) ${a}x > ${c} − ${b}\n2) ${a}x > ${c - b}\n3) x > ${xBound}.\nЧисло ${xBound} не підходить (воно не строго більше за ${xBound}). Найменше із запропонованих чисел, яке більше за ${xBound}, — це ${ans} (${labels[ci]}).`,
    drill_key: 'math_ineq',
  }
})

registerDrill('math_percent_trip', () => {
  const base = choice([500, 600, 800, 1000, 1200])
  const d1 = choice([10, 15, 20, 25])
  const d2 = choice([15, 20, 25, 30])
  const total = base + (base * (100 - d1)) / 100 + (base * (100 - d2)) / 100
  const ansStr = fmtNum(total)
  return {
    subject: 'math',
    section: 'Числа і вирази',
    source: GEN_SOURCE,
    qtype: 'short',
    max_points: 2,
    prompt:
      `Сім’я з трьох осіб (батько, мама й дитина) купує квитки на екскурсію. ` +
      `Повна вартість становить ${base} грн з особи. Мамі надають знижку ${d1} %, ` +
      `а дитині — ${d2} %. Скільки гривень сім’я заплатить за всіх з урахуванням знижок?`,
    answer: ansStr,
    hint: `Якщо знижка ${d1}%, то платити потрібно ${100 - d1}% від ціни (${base} · ${fixed2((100 - d1) / 100)}). Додай усі три суми.`,
    rule: 'Щоб швидко знайти ціну зі знижкою p%, помнож початкову ціну на (100 − p) / 100. Помилку найчастіше роблять, коли знаходять лише розмір знижки й забувають відняти її від початкової ціни.',
    solution:
      `• Батько: ${base} грн\n` +
      `• Мама: ${base} · ${100 - d1}% = ${fmtNum((base * (100 - d1)) / 100)} грн\n` +
      `• Дитина: ${base} · ${100 - d2}% = ${fmtNum((base * (100 - d2)) / 100)} грн\n` +
      `Разом: ${ansStr} грн.`,
    drill_key: 'math_percent_trip',
  }
})

registerDrill('math_prob', () => {
  const a = randint(3, 9)
  const b = randint(3, 9)
  const c = randint(2, 8)
  const total = a + b + c
  const fav = a + c
  const g = gcd(fav, total)
  const num = floorDiv(fav, g)
  const den = floorDiv(total, g)
  const ansStr = `${num}/${den}`
  const reduced = (x: number) =>
    gcd(x, total) === 1 ? `${x}/${total}` : `${floorDiv(x, gcd(x, total))}/${floorDiv(total, gcd(x, total))}`
  const candidates = [`${num}/${den}`, reduced(a), reduced(b), `1/${fav}`, `1/${total}`]
  const opts: string[] = []
  for (const cand of candidates) if (!opts.includes(cand)) opts.push(cand)
  let extra = 1
  while (opts.length < 5) {
    const cand = `${extra}/${total + 1}`
    if (!opts.includes(cand)) opts.push(cand)
    extra += 1
  }
  shuffle(opts)
  const labels = LABELS5
  const ci = opts.indexOf(ansStr)
  return {
    subject: 'math',
    section: 'Комбінаторика, ймовірність, статистика',
    source: GEN_SOURCE,
    qtype: 'single',
    max_points: 1,
    prompt:
      `На столі лежать ${total} карток: ${a} із зображенням гір, ${b} із зображенням моря ` +
      `та ${c} із зображенням лісу. Яка ймовірність того, що навмання взята картка ` +
      `буде із зображенням гір або лісу?`,
    options: opts,
    labels: [...labels],
    answer: labels[ci],
    hint: 'Сполучник «АБО» в імовірності означає ДОДАВАННЯ сприятливих варіантів: (гори + ліс) / усього.',
    rule: 'Класична ймовірність P = m / n, де m — кількість відповідних варіантів («гори або ліс» = додаємо), n — загальна кількість об’єктів. Не забудь скоротити дріб!',
    solution: `Усього карток n = ${total}. Підходять гори (${a}) або ліс (${c}): m = ${a} + ${c} = ${fav}. P = ${fav}/${total} = ${ansStr} (${labels[ci]}).`,
    drill_key: 'math_prob',
  }
})

registerDrill('math_trap_angle', () => {
  const obtuse = choice([105, 110, 115, 120, 125, 130, 135])
  const acute = 180 - obtuse
  let vals = sortedUnique([acute, obtuse, floorDiv(obtuse, 2), acute - 15, acute + 10])
  while (vals.length < 5) vals.push(vals[vals.length - 1] + 5)
  vals = vals.slice(0, 5)
  const labels = LABELS5
  const ci = vals.indexOf(acute)
  return {
    subject: 'math',
    section: 'Планіметрія',
    source: GEN_SOURCE,
    qtype: 'single',
    max_points: 1,
    prompt: `У рівнобічній трапеції ABCD (BC ∥ AD) тупий кут ∠BCD = ${obtuse}°. Визначте градусну міру гострого кута ∠BAD.`,
    options: vals.map((v) => `${v}°`),
    labels: [...labels],
    answer: labels[ci],
    hint: 'У рівнобічної трапеції кути при бічній стороні в сумі дають 180°, а кути при основі рівні.',
    rule: 'Сума односторонніх кутів трапеції при бічній стороні дорівнює 180° (∠B + ∠A = 180°). Оскільки трапеція рівнобічна, ∠B = ∠C, тому ∠A = 180° − ∠C.',
    solution: `Оскільки трапеція рівнобічна, ∠ABC = ∠BCD = ${obtuse}°. Сума кутів при бічній стороні AB дорівнює 180°, тож ∠BAD = 180° − ${obtuse}° = ${acute}° (${labels[ci]}).`,
    drill_key: 'math_trap_angle',
  }
})

registerDrill('math_exp_eq', () => {
  const base = choice([2, 3, 5])
  const k = randint(1, 4)
  const p = randint(2, 4)
  const ans = k - p
  let vals = sortedUnique([ans, ans !== 0 ? -ans : 5, ans + 2, ans - 2, p + k])
  while (vals.length < 5) vals.push(vals[vals.length - 1] + 1)
  vals = vals.slice(0, 5)
  const labels = LABELS5
  const ci = vals.indexOf(ans)
  return {
    subject: 'math',
    section: 'Рівняння, нерівності та їх системи',
    source: GEN_SOURCE,
    qtype: 'single',
    max_points: 1,
    prompt: `Розв’яжіть рівняння ${base}^(x + ${k}) = ${base ** p} · ${base ** 2}^x.`,
    options: vals.map(String),
    labels: [...labels],
    answer: labels[ci],
    hint: `Зведи всі числа до однієї основи ${base}: ${base ** p} = ${base}^${p}, а ${base ** 2} = ${base}^2.`,
    rule: 'Показникове рівняння розв’язується зведенням обох частин до спільної основи: a^f(x) = a^g(x) ⇒ f(x) = g(x). Під час множення степенів показники ДОДАЮТЬСЯ.',
    solution:
      `1) Запишемо через основу ${base}: ${base}^(x + ${k}) = ${base}^${p} · ${base}^(2x) = ${base}^(${p} + 2x)\n` +
      `2) Прирівнюємо показники: x + ${k} = ${p} + 2x\n` +
      `3) Звідси x = ${k} − ${p} = ${ans} (${labels[ci]}).`,
    drill_key: 'math_exp_eq',
  }
})

registerDrill('math_deriv_ext', () => {
  const pairs: Array<[number, number]> = [[-3, 5], [-2, 4], [-1, 3], [-3, 3], [-2, 6], [-1, 5]]
  const [r1, r2] = choice(pairs)
  const bCoef = floorDiv(-3 * (r1 + r2), 2)
  const cCoef = 3 * r1 * r2
  const dCoef = randint(1, 15)
  const wantMax = choice([true, false])
  const targetWord = wantMax ? 'максимуму' : 'мінімуму'
  const ans = wantMax ? r1 : r2
  const bStr = bCoef >= 0 ? `+ ${bCoef}` : `− ${Math.abs(bCoef)}`
  const cStr = cCoef >= 0 ? `+ ${cCoef}` : `− ${Math.abs(cCoef)}`
  return {
    subject: 'math',
    section: 'Функції',
    source: GEN_SOURCE,
    qtype: 'short',
    max_points: 2,
    prompt: `Визначте точку ${targetWord} функції f(x) = x³ ${bStr}x² ${cStr}x + ${dCoef}.`,
    answer: fmtNum(ans),
    hint: "Знайди похідну f'(x), прирівняй її до 0, знайди критичні точки та перевір знак похідної (перехід із '+' на '−' дає максимум, із '−' на '+' — мінімум).",
    rule: 'Для кубічної параболи з +x³ вітки похідної f\'(x) напрямлені вгору (+, −, +). Тому менший корінь завжди точка МАКСИМУМУ, а більший — точка МІНІМУМУ!',
    solution:
      `1) f'(x) = 3x² ${signed(2 * bCoef)}x ${signed(cCoef)} = 0\n` +
      `2) Поділимо на 3: x² ${signed(floorDiv(2 * bCoef, 3))}x ${signed(floorDiv(cCoef, 3))} = 0\n` +
      `3) Корені: x₁ = ${r1}, x₂ = ${r2}.\n` +
      `4) Знаки похідної: (+) на (−∞; ${r1}), (−) на (${r1}; ${r2}), (+) на (${r2}; +∞).\n` +
      `Точка ${targetWord}: ${ans}.`,
    drill_key: 'math_deriv_ext',
  }
})

registerDrill('math_vector', () => {
  const triples: Array<[number, number, number]> = [[1, 2, 2], [2, 3, 6], [1, 4, 8], [2, 1, 2], [3, 4, 0]]
  const [cx, cy, cz] = choice(triples)
  const modC = Math.round(Math.sqrt(cx * cx + cy * cy + cz * cz))
  const ax = randint(-4, 4)
  const ay = randint(-4, 4)
  const az = randint(-4, 4)
  const [bx, by, bz] = [cx - ax, cy - ay, cz - az]
  let vals = sortedUnique([modC, Math.abs(cx) + Math.abs(cy) + Math.abs(cz), modC + 2, Math.max(1, modC - 1), modC * modC])
  while (vals.length < 5) vals.push(vals[vals.length - 1] + 1)
  vals = vals.slice(0, 5)
  const labels = LABELS5
  const ci = vals.indexOf(modC)
  return {
    subject: 'math',
    section: 'Стереометрія',
    source: GEN_SOURCE,
    qtype: 'single',
    max_points: 1,
    prompt: `У прямокутній системі координат у просторі задано вектори a(${ax}; ${ay}; ${az}) і b(${bx}; ${by}; ${bz}). Визначте модуль вектора c = a + b.`,
    options: vals.map(String),
    labels: [...labels],
    answer: labels[ci],
    hint: 'Спочатку додай відповідні координати (x₁+x₂; y₁+y₂; z₁+z₂), потім знайди довжину √(x² + y² + z²).',
    rule: 'Координати суми векторів дорівнюють сумі їхніх координат. Модуль (довжина) вектора (x; y; z) дорівнює √(x² + y² + z²).',
    solution: `1) c = (${ax}+${bx}; ${ay}+${by}; ${az}+${bz}) = (${cx}; ${cy}; ${cz}).\n2) |c| = √(${cx}² + ${cy}² + ${cz}²) = √${cx * cx + cy * cy + cz * cz} = ${modC} (${labels[ci]}).`,
    drill_key: 'math_vector',
  }
})

registerDrill('math_module_pow', () => {
  const d = choice([2, 4, 5, 10])
  const b = choice([2, 3, 4, 5])
  const val = Math.abs(1.0 / d - b)
  const ans = fmtNum(val)
  const neg = fmtNum(-val)
  const wrong1 = fmtNum(d + b)
  const wrong2 = fmtNum(1.0 / d + b)
  const wrong3 = fmtNum(val + 0.5)
  const opts: string[] = []
  for (const x of [ans, neg, wrong1, wrong2, wrong3]) if (!opts.includes(x)) opts.push(x)
  while (opts.length < 5) opts.push(fmtNum(val + opts.length))
  shuffle(opts)
  const labels = LABELS5
  const ci = opts.indexOf(ans)
  return {
    subject: 'math',
    section: 'Числа і вирази',
    source: GEN_SOURCE,
    qtype: 'single',
    max_points: 1,
    prompt: `Обчисліть значення виразу |${d}⁻¹ − ${b}|.`,
    options: opts,
    labels: [...labels],
    answer: labels[ci],
    hint: `Увага! ${d}⁻¹ — це НЕ −${d}, а дріб 1/${d}! І модуль числа завжди ≥ 0.`,
    rule: 'Дві головні пастки НМТ: 1) a⁻¹ = 1/a (від’ємний показник перевертає число, а не змінює знак); 2) модуль |x| завжди невід’ємний.',
    solution: `1) ${d}⁻¹ = 1/${d} = ${fmtNum(1.0 / d)}.\n2) ${fmtNum(1.0 / d)} − ${b} = ${fmtNum(1.0 / d - b)}.\n3) |${fmtNum(1.0 / d - b)}| = ${ans} (${labels[ci]}).`,
    drill_key: 'math_module_pow',
  }
})
