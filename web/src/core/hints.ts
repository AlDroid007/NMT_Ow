// Owl helper hint system: 10 levels from a light nudge (1) to the full answer with a story (10)
// (port of nmt_tutor/hints.py — texts must match the desktop one to one).

import { SUBJECTS_CONFIG } from './config'
import { collapseSpaces, pyFloat, pyFloatStr, pyLen, pyRound, pyRoundTo, pySlice, pyStr, rstripChars, sortedStrings } from './py'
import type { Task } from './types'

const LANGS = ['english', 'german', 'french', 'spanish']
const SCIENCES = ['math', 'physics', 'chemistry', 'geography']

/** dict.get(key, default): a present key wins even when its value is null. */
function get<T = string>(q: Task, key: string, dflt: T): T {
  return (Object.prototype.hasOwnProperty.call(q, key) ? q[key] : dflt) as T
}

/** get() for string fields (qtype, subject, prompt…). */
function gs(q: Task, key: string, dflt: string): string {
  return get<string>(q, key, dflt)
}

function cleanText(val: unknown): string {
  return (val === null || val === undefined || val === '' || val === 0 || val === false ? '' : pyStr(val)).trim()
}

function shorten(text: unknown, maxLen = 140): string {
  const t = collapseSpaces(pyStr(text))
  if (pyLen(t) <= maxLen) return t
  return rstripChars(pySlice(t, 0, maxLen - 1), ' ,;:') + '…'
}

const LINE_BREAKS = new RegExp('\\r\\n|[\\n\\r\\v\\f\\x1c\\x1d\\x1e\\x85\\u2028\\u2029]')

/** str.splitlines() */
function splitLines(s: string): string[] {
  const parts = s.split(LINE_BREAKS)
  if (parts.length && parts[parts.length - 1] === '') parts.pop()
  return parts
}

function zip<A, B>(a: readonly A[], b: readonly B[]): Array<[A, B]> {
  const n = Math.min(a.length, b.length)
  const out: Array<[A, B]> = []
  for (let i = 0; i < n; i++) out.push([a[i], b[i]])
  return out
}

const upper = (v: unknown) => pyStr(v).trim().toUpperCase()

function solutionLines(q: Task): string[] {
  return splitLines(cleanText(get(q, 'solution', ''))).map((ln) => ln.trim()).filter(Boolean)
}

function detectTrap(q: Task): string {
  const qt = gs(q, 'qtype', 'single')
  const prompt = pyStr(gs(q, 'prompt', ''))
  const subj = gs(q, 'subject', '')
  const pLow = prompt.toLowerCase()

  if (['окрім', 'не треба', 'не потрібно', 'не мають', 'не відбулася'].some((w) => pLow.includes(w)))
    return 'Типова пастка НМТ: у запитанні є заперечення («ОКРІМ» / «НЕ»). Шукай саме той ОДИН рядок, який порушує правило, а не підходить під нього!'
  if (qt === 'short') {
    if (SCIENCES.includes(subj))
      return 'Типова пастка НМТ для короткої відповіді: перевір одиниці виміру, знак (плюс/мінус) і запис дробу через кому чи ціле число.'
    return 'Типова пастка НМТ: уважно перечитай, що саме просять записати у відповідь — кінцеву величину чи проміжний крок.'
  }
  if (qt === 'matching')
    return 'Типова пастка в логічних парах: праворуч завжди є ОДИН зайвий варіант-приманка (5 варіантів на 4 рядки або 5 на 3). Не притягуй його силоміць!'
  if (qt === 'sequence')
    return 'Типова пастка хронології: події можуть бути дуже близько за роками або належати до однієї доби. Найперше знайди «якорі» — найдавнішу (1) та найпізнішу (4) подію.'
  if (qt === 'multi3')
    return 'Типова пастка «3 із 7»: серед варіантів підмішано події чи ознаки з ІНШОЇ епохи або іншого явища, які звучать правдоподібно, але не стосуються зазначеного періоду.'
  if (LANGS.includes(subj))
    return 'Типова пастка іноземної мови на НМТ: «хибні друзі» та схожі за звучанням слова з тексту (наприклад, часова форма, число підмета або прийменник після пропуску).'
  if (subj === 'math')
    return 'Типова пастка математики: зверни увагу на знаки нерівностей (> чи ≥), мінус перед дужками, від’ємні степені (a⁻¹ = 1/a) та ОДЗ.'
  return 'Типова пастка НМТ: 1–2 варіанти спеціально складено так, щоб спіймати на неуважному читанні умови або плутанині схожих термінів.'
}

function detectMarkers(q: Task): string {
  const qt = gs(q, 'qtype', 'single')
  const subj = gs(q, 'subject', '')
  const prompt = pyStr(gs(q, 'prompt', ''))

  if (qt === 'matching') {
    const left = get<unknown[]>(q, 'left', [])
    return `Подивись на ключові слова ліворуч (особливо на пункт «${left && left.length ? pyStr(left[0]) : '1'}») та знайди до нього точну ознаку серед варіантів А–Д.`
  }
  if (qt === 'sequence')
    return 'Підкресли подумки всі 4 події та пригадай століття або десятиліття для кожної з них — так одразу стане видно першу й останню позицію.'
  if (qt === 'multi3')
    return 'Виділи в умові часові рамки або головний критерій відбору (що саме має виконуватися одночасно для всіх 3 правильних пунктів).'
  if (LANGS.includes(subj)) {
    if (prompt.includes('_______'))
      return 'Подивись на 2–3 слова БЕЗПОСЕРЕДНЬО перед пропуском і після нього: чи є там прийменник, союз, маркер часу або підмет в однині/множині?'
    return 'Знайди в тексті ключові слова-синоніми: на НМТ правильний варіант майже ніколи не повторює слова тексту дослівно, а перефразовує їх.'
  }
  if (SCIENCES.includes(subj))
    return 'Випиши окремо всі числа, коефіцієнти та невідому величину з умови. Перевір, чи не потрібне переведення одиниць (%, см у м, хв у с, л у молі).'
  return 'Виділи головні опорні слова в самому запитанні — саме в них схована умова, яка відрізняє правильний рядок від решти.'
}

function rephraseSimple(q: Task): string {
  const subj = gs(q, 'subject', '')
  const qt = gs(q, 'qtype', 'single')
  const sec = pyStr(get(q, 'section', ''))
  if (qt === 'matching')
    return `Простими словами: тобі потрібно з’єднати кожен елемент ліворуч (1, 2, 3...) із його точною парою праворуч за темою «${sec}».`
  if (qt === 'sequence')
    return 'Простими словами: розстав ці 4 події на уявній лінії часу — від того, що сталося раніше за все, до найновішої події.'
  if (qt === 'multi3') return 'Простими словами: з 7 пунктів потрібно залишити лише 3 беззаперечно правильні, а 4 зайві — відкинути.'
  if (qt === 'short')
    return `Простими словами: тут немає готових варіантів, тому потрібно акуратно обчислити точне число за правилами розділу «${sec}».`
  if (LANGS.includes(subj))
    return `Простими словами: перевіряється твоє вміння в розділі «${sec}» — відчути контекст і підібрати єдину граматично/лексично точну форму.`
  return `Простими словами: завдання перевіряє одне базове вміння з теми «${sec}» — відокреми правильний мовний/науковий факт від схожих помилок.`
}

function singlePairs(q: Task): { correct: Array<[unknown, unknown]>; wrong: Array<[unknown, unknown]> } {
  const pairs = zip(get<unknown[]>(q, 'labels', []), get<unknown[]>(q, 'options', []))
  const corr = upper(get(q, 'answer', ''))
  return { correct: pairs.filter(([l]) => upper(l) === corr), wrong: pairs.filter(([l]) => upper(l) !== corr) }
}

function eliminationHint(q: Task): string {
  const qt = gs(q, 'qtype', 'single')
  if (qt === 'single') {
    const wrongs = singlePairs(q).wrong
    if (wrongs.length >= 2) {
      const [w1, w2] = wrongs
      return `Відсіювання зайвого: варіанти ${pyStr(w1[0])} («${shorten(w1[1], 45)}») та ${pyStr(w2[0])} («${shorten(w2[1], 45)}») точно НЕ підходять — сміливо викреслюй їх!`
    }
    if (wrongs.length) return `Відсіювання зайвого: варіант ${pyStr(wrongs[0][0])} («${shorten(wrongs[0][1], 55)}») можна одразу виключити.`
  } else if (qt === 'matching') {
    const ansMap = get<Record<string, unknown>>(q, 'answer', {})
    const used = new Set(Object.values(ansMap).map((v) => pyStr(v).toUpperCase()))
    const right = (get<Record<string, unknown> | null>(q, 'right', null) || {}) as Record<string, unknown>
    const extra = Object.keys(right).filter((k) => !used.has(k.toUpperCase()))
    if (extra.length) {
      const exK = extra[0]
      return `Відсіювання зайвого: варіант ${exK} («${shorten(right[exK], 60)}») є зайвим дистрактором і не підходить до жодного рядка!`
    }
  } else if (qt === 'sequence') {
    const ans = Array.from(pyStr(get(q, 'answer', '')))
    if (ans.length === 4)
      return `Відсіювання зайвого: найпізніша подія в цьому наборі точно НЕ перша, а найдавніша — точно НЕ ${ans[3]}.`
  } else if (qt === 'multi3') {
    const corr = new Set(get<unknown[]>(q, 'answer', []).map(pyStr))
    const items = get<Record<string, unknown>>(q, 'items', {})
    const wrongs = Object.entries(items).filter(([k]) => !corr.has(k))
    if (wrongs.length >= 2)
      return `Відсіювання зайвого: пункти ${wrongs[0][0]} («${shorten(wrongs[0][1], 42)}») та ${wrongs[1][0]} («${shorten(wrongs[1][1], 42)}») стосуються іншого — сміливо відкидай їх!`
  } else if (qt === 'short') {
    const val = pyFloat(pyStr(get(q, 'answer', '')).trim().replace(/,/g, '.'))
    if (val !== null) {
      if (val >= 0) {
        const a = Math.abs(val)
        const scale = a < 10 ? String(pyRound(val)) : a >= 20 ? pyFloatStr(pyRoundTo(val, -1)) : pyFloatStr(pyRoundTo(val, 1))
        return `Оцінка результату: відповідь — невід’ємне число (близько до порядку величини ${scale}), від’ємні варіанти тут неможливі.`
      }
      return 'Оцінка результату: зверни увагу, що у відповіді має вийти ВІД’ЄМНЕ число (зі знаком «−»).'
    }
  }
  return 'Відсіювання зайвого: відкинь варіанти, які суперечать основному правилу або стосуються іншого часу/теми.'
}

function step1Hint(q: Task): string {
  const qt = gs(q, 'qtype', 'single')
  const solLines = solutionLines(q)
  if (qt === 'matching') {
    const ansMap = get<Record<string, unknown>>(q, 'answer', {})
    const left = get<unknown[]>(q, 'left', [])
    if (ansMap && Object.keys(ansMap).length && left && left.length) {
      const k1 = sortedStrings(Object.keys(ansMap))[0]
      return `Перший крок: почни з першої пари — для пункту «${shorten(left[0], 55)}» точно підходить буква ${pyStr(ansMap[k1])}.`
    }
  }
  if (qt === 'sequence') {
    const ans = Array.from(pyStr(get(q, 'answer', '')))
    const items = get<Record<string, unknown>>(q, 'items', {})
    if (ans.length === 4 && ans[0] in items)
      return `Перший крок: найдавнішою подією є ${ans[0]} («${shorten(items[ans[0]], 60)}») — постав її на 1-ше місце!`
  }
  if (qt === 'multi3') {
    const corr = sortedStrings(get<unknown[]>(q, 'answer', []).map(pyStr))
    const items = get<Record<string, unknown>>(q, 'items', {})
    if (corr.length && corr[0] in items)
      return `Перший крок: один із трьох правильних пунктів — це ${corr[0]} («${shorten(items[corr[0]], 60)}»).`
  }
  if (qt === 'single') {
    const { correct, wrong } = singlePairs(q)
    if (correct.length && wrong.length >= 1) {
      const keep = sortedStrings([pyStr(correct[0][0]), pyStr(wrong[wrong.length - 1][0])])
      return `Перший крок: після перевірки правила залишаються лише два реальні кандидати — ${keep.join(' та ')}.`
    }
  }
  if (solLines.length) {
    const first = solLines[0]
    const ansStr = pyStr(get(q, 'answer', ''))
    if (ansStr && pyLen(ansStr) >= 2 && first.includes(ansStr) && qt === 'short')
      return 'Перший крок: підстав відомі числа з умови у базову формулу й знайди проміжну величину (уважно стеж за діями).'
    return `Перший крок розв’язання: ${shorten(first, 140)}`
  }
  return 'Перший крок: застосуй згадане правило безпосередньо до першого елемента умови.'
}

function step2Hint(q: Task): string {
  const qt = gs(q, 'qtype', 'single')
  if (qt === 'matching') {
    const ansMap = get<Record<string, unknown>>(q, 'answer', {})
    const keys = sortedStrings(Object.keys(ansMap))
    if (keys.length >= 2)
      return `Другий крок: тепер закріплюємо ще одну пару — до позиції ${keys[1]} пасує ${pyStr(ansMap[keys[1]])}. Залишилося зовсім небагато!`
  }
  if (qt === 'sequence') {
    const ans = Array.from(pyStr(get(q, 'answer', '')))
    const items = get<Record<string, unknown>>(q, 'items', {})
    if (ans.length === 4 && ans[3] in items)
      return `Другий крок: маємо обидва краї хронології — перша подія ${ans[0]}, а найпізніша (4-та) — ${ans[3]} («${shorten(items[ans[3]], 55)}»).`
  }
  if (qt === 'multi3') {
    const corr = sortedStrings(get<unknown[]>(q, 'answer', []).map(pyStr))
    const items = get<Record<string, unknown>>(q, 'items', {})
    if (corr.length >= 2 && corr[1] in items)
      return `Другий крок: другим правильним пунктом є ${corr[1]} («${shorten(items[corr[1]], 55)}»). Залишилося добрати останній третій!`
  }
  if (qt === 'single') {
    const { correct, wrong } = singlePairs(q)
    if (correct.length && wrong.length) {
      const [trapL, trapO] = wrong[wrong.length - 1]
      return `Другий крок: порівняй фінальні варіанти — у варіанті ${pyStr(trapL)} («${shorten(trapO, 45)}») є прихована невідповідність правилу.`
    }
  }
  const solLines = solutionLines(q)
  if (solLines.length >= 2) return `Другий крок: ${shorten(solLines[1], 140)}`
  return `Другий крок: зведи всі дані до фінальної перевірки — орієнтуйся на правило: ${shorten(get(q, 'rule', ''), 110)}`
}

function nearFinalHint(q: Task): string {
  const qt = gs(q, 'qtype', 'single')
  if (qt === 'matching') {
    const ansMap = get<Record<string, unknown>>(q, 'answer', {})
    const keys = sortedStrings(Object.keys(ansMap))
    if (keys.length >= 3) {
      const pairsTxt = keys.slice(0, 3).map((k) => `${k}–${pyStr(ansMap[k])}`).join(', ')
      return `Майже фінал! Маємо вже три точні пари: ${pairsTxt}. Тобі залишилося визначити лише останню пару (${keys[keys.length - 1]})!`
    }
  }
  if (qt === 'sequence') {
    const ans = Array.from(pyStr(get(q, 'answer', '')))
    if (ans.length === 4) return `Майже фінал! Порядок має вигляд ${ans[0]} _ _ ${ans[3]} — порівняй лише дві середні події між собою.`
  }
  if (qt === 'multi3') {
    const corr = sortedStrings(get<unknown[]>(q, 'answer', []).map(pyStr))
    if (corr.length >= 2) return `Майже фінал! Два з трьох пунктів — це ${corr[0]} і ${corr[1]}. Обери останній за змістом теми.`
  }
  if (qt === 'short') {
    const v = pyFloat(pyStr(get(q, 'answer', '')).trim().replace(/,/g, '.'))
    if (v !== null) {
      let low = pyRoundTo(v * 0.85, 1)
      let high = pyRoundTo(v * 1.15, 1)
      if (low > high) [low, high] = [high, low]
      return `Майже фінал! Після фінальної арифметичної дії ти отримаєш число в межах від ${pyFloatStr(low).replace('.', ',')} до ${pyFloatStr(high).replace('.', ',')}.`
    }
  }
  return `Майже фінал! Усі підготовчі кроки зроблено — зроби фінальний висновок за ключем: ${shorten(get(q, 'hint', ''), 110)}`
}

function level10Story(q: Task): string {
  const qt = gs(q, 'qtype', 'single')
  const subj = gs(q, 'subject', '')
  const cfgName = SUBJECTS_CONFIG[subj]?.name ?? 'Предмет НМТ'
  const sec = pyStr(get(q, 'section', ''))
  const rule = cleanText(get(q, 'rule', ''))
  const sol = cleanText(get(q, 'solution', ''))

  let ansDisplay: string
  if (qt === 'single') {
    const ansLbl = pyStr(get(q, 'answer', '')).trim()
    let ansOpt = ''
    for (const [l, o] of zip(get<unknown[]>(q, 'labels', []), get<unknown[]>(q, 'options', []))) {
      if (upper(l) === ansLbl.toUpperCase()) {
        ansOpt = ` (${pyStr(o)})`
        break
      }
    }
    ansDisplay = `${ansLbl}${ansOpt}`
  } else if (qt === 'matching') {
    const ansMap = get<Record<string, unknown>>(q, 'answer', {})
    ansDisplay = sortedStrings(Object.keys(ansMap)).map((k) => `${k}–${pyStr(ansMap[k])}`).join(', ')
  } else if (qt === 'multi3') {
    ansDisplay = get<unknown[]>(q, 'answer', []).map(pyStr).join(', ')
  } else {
    ansDisplay = pyStr(get(q, 'answer', ''))
  }

  return (
    `🦉 Повна відповідь і розповідь Сови-Лізи:\n` +
    `✅ Правильна відповідь: ${ansDisplay}\n\n` +
    `📖 Чому саме так (${cfgName} • ${sec}):\n` +
    `Уяви, як працює це правило на практиці: ${rule}\n\n` +
    `🔍 Як це спрацювало саме тут:\n${sol}\n\n` +
    `💡 Запам’ятай цю логіку — на НМТ подібні завдання трапляються постійно, але змінюють лише слова або числа!`
  )
}

/** 10 hints in a row: from a very light nudge (1) to the full answer with a story (10). */
export function build10Hints(q: Task): string[] {
  const custom = q.hints_10
  if (Array.isArray(custom) && custom.length === 10) return custom

  const subjName = SUBJECTS_CONFIG[gs(q, 'subject', '')]?.name ?? 'НМТ'
  const sec = pyStr(get(q, 'section', 'Програма НМТ'))

  return [
    `Рівень 1 (Дуже легкий натяк): Це завдання з предмета «${subjName}», тема — «${sec}». Прочитай умову ще раз спокійно, не підглядаючи у варіанти.`,
    `Рівень 2 (Ключовий маркер): ${detectMarkers(q)}`,
    `Рівень 3 (Суть своїми словами): ${rephraseSimple(q)}`,
    `Рівень 4 (Увага на пастку!): ${detectTrap(q)}`,
    `Рівень 5 (Натяк Сови): ${cleanText(get(q, 'hint', 'Зверни увагу на головну деталь в умові.'))}`,
    `Рівень 6 (Потрібне правило / формула): ${cleanText(get(q, 'rule', 'Пригадай базове правило цього розділу.'))}`,
    `Рівень 7 • ${eliminationHint(q)}`,
    `Рівень 8 • ${step1Hint(q)}`,
    `Рівень 9 • ${step2Hint(q)} ${nearFinalHint(q)}`,
    level10Story(q),
  ]
}
