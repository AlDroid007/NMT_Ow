// Task generators: Українська мова (port of generators/ukrmova.py).

import { choice, randint, sample, shuffle } from '../py'
import { GEN_SOURCE, LABELS4, registerDrill } from './common'

type Pair = [string, string]

registerDrill('ukrmova_pref_zs', () => {
  const kafep: Pair[] = [
    ['..казати', 'сказати'], ['..писати', 'списати'], ['..творити', 'створити'],
    ['..фотографувати', 'сфотографувати'], ['..хитрувати', 'схитрувати'],
    ['..ховати', 'сховати'], ['..копіювати', 'скопіювати'], ['..формувати', 'сформувати'],
    ['..палити', 'спалити'], ['..пиляти', 'спиляти'], ['..тримати', 'стримати'],
  ]
  const zWords: Pair[] = [
    ['..робити', 'зробити'], ['..будувати', 'збудувати'], ['..шити', 'зшити'],
    ['..цілити', 'зцілити'], ['..жалитись', 'зжалитись'], ['..бирати', 'збирати'],
    ["..в'язати", "зв'язати"], ['..мінити', 'змінити'], ['..гадати', 'згадати'],
  ]
  const labels = [...LABELS4]
  const mode = choice(['find_z', 'find_s'])
  const correctIdx = randint(0, 3)
  const options: string[] = []
  if (mode === 'find_z') {
    const usedK = sample(kafep, 9)
    let idx = 0
    let oddWord = ''
    for (let i = 0; i < 4; i++) {
      if (i === correctIdx) {
        const zw = choice(zWords)
        const pair = sample(kafep.filter((w) => w[0] !== zw[0]), 2)
        const words = shuffle([pair[0][0], zw[0], pair[1][0]])
        options.push(words.join(', '))
        oddWord = zw[1]
      } else {
        options.push([usedK[idx][0], usedK[idx + 1][0], usedK[idx + 2][0]].join(', '))
        idx += 3
      }
    }
    return {
      subject: 'ukrmova',
      section: 'Орфографія',
      source: GEN_SOURCE,
      qtype: 'single',
      max_points: 1,
      prompt: 'Префікс с- треба писати на місці пропуску в усіх словах, ОКРІМ рядка:',
      options,
      labels,
      answer: labels[correctIdx],
      hint: 'Згадай чарівну фразу «КаФе «ПТаХ»». Перед цими п’ятьма приголосними пишемо с-.',
      rule: 'В українській мові префікс С- пишеться ЛИШЕ перед літерами К, Ф, П, Т, Х (мнемоніка: «КаФе «ПТаХ»»). Перед усіма іншими літерами завжди пишемо префікс З-.',
      solution: `У рядку ${labels[correctIdx]} є слово «${oddWord}», де корінь починається не на К, Ф, П, Т, Х — отже, потрібен префікс З-. В інших словах перші літери кореня входять до «КаФе ПТаХ».`,
      drill_key: 'ukrmova_pref_zs',
    }
  }
  let winWords = ''
  for (let i = 0; i < 4; i++) {
    if (i === correctIdx) {
      const kw = sample(kafep, 3)
      options.push(kw.map((w) => w[0]).join(', '))
      winWords = kw.map((w) => w[1]).join(', ')
    } else {
      let row: string[] = []
      for (let tries = 0; tries < 50; tries++) {
        const zw = sample(zWords, 2)
        const kw = choice(kafep)
        row = shuffle([zw[0][0], kw[0], zw[1][0]])
        if (!options.some((o) => rowKey(o.split(', ')) === rowKey(row))) break
      }
      options.push(row.join(', '))
    }
  }
  return {
    subject: 'ukrmova',
    section: 'Орфографія',
    source: GEN_SOURCE,
    qtype: 'single',
    max_points: 1,
    prompt: 'Префікс с- треба писати на місці пропуску в усіх словах рядка:',
    options,
    labels,
    answer: labels[correctIdx],
    hint: 'Перевір кожну першу літеру після пропуску за правилом «КаФе «ПТаХ»».',
    rule: 'Префікс С- пишемо лише перед приголосними К, П, Т, Ф, Х («КаФе «ПТаХ»»). Навіть перед Ш або С у слові «зшити» пишемо З-!',
    solution: `Правильний варіант ${labels[correctIdx]} (${winWords}) — усі три слова починаються на приголосні з правила «КаФе «ПТаХ»».`,
    drill_key: 'ukrmova_pref_zs',
  }
})

registerDrill('ukrmova_nagolos', () => {
  const exactGood = [
    'мережа піце́рій', 'пройти чотирна́дцять', 'платіжна ві́домість', 'бурштинова за́понка',
    'привітати замі́жню', 'болотиста рівни́на', 'ти́сові ліси', 'дивлячись на ці́нник',
    'чергова ви́трата', 'завча́су закінчити', 'посере́дині літо́пису', 'новий катало́г',
    'дієвий фено́мен', 'глибоке ру́сло', 'зручні жалюзі́', 'тривалий кварта́л',
  ]
  const exactWrong: Pair[] = [
    ['у листо́паді', 'правильно: у листопа́ді'],
    ['принести ко́лесо', 'правильно: коле́со'],
    ['довідник з кулінарі́ї', 'правильно: куліна́рії'],
    ['рідкісний феноме́н', 'правильно: фено́мен'],
    ['рівна спи́на', 'правильно: спина́'],
    ['новий фарту́х', 'правильно: фа́ртух'],
    ['несподіваний випа́док', 'правильно: ви́падок'],
    ['високий це́нтнер', 'правильно: центне́р'],
  ]
  const wrongItem = choice(exactWrong)
  const goodItems = sample(exactGood, 7)
  const wrongIdx = randint(0, 3)
  const options: string[] = []
  let g = 0
  for (let i = 0; i < 4; i++) {
    if (i === wrongIdx) {
      options.push(`${goodItems[g]}, ${wrongItem[0]}`)
      g += 1
    } else {
      options.push(`${goodItems[g]}, ${goodItems[g + 1]}`)
      g += 2
    }
  }
  const labels = [...LABELS4]
  return {
    subject: 'ukrmova',
    section: 'Фонетика. Графіка. Орфоепія',
    source: GEN_SOURCE,
    qtype: 'single',
    max_points: 1,
    prompt: 'Правильно виділено букви на позначення наголошених звуків у всіх словах, ОКРІМ рядка:',
    options,
    labels,
    answer: labels[wrongIdx],
    hint: 'Прочитай кожне слово вголос, перевіряючи типові слова-пастки НМТ (фено́мен, куліна́рія, листопа́д, коле́со, ви́падок).',
    rule: 'На НМТ щороку перевіряють нормативний наголос: фено́мен, куліна́рія, листопа́д, коле́со, спина́, фа́ртух, ви́падок, центне́р, ці́нник, ви́трата.',
    solution: `Помилка у варіанті ${labels[wrongIdx]}: «${wrongItem[0]}» — ${wrongItem[1]}.`,
    drill_key: 'ukrmova_nagolos',
  }
})

/** The same words in another order count as the same row. */
const rowKey = (words: string[]) => [...words].sort().join('|')

/**
 * Three good words in the right row, one bad word mixed into each other row.
 * Unlike the desktop, a row never repeats another one (the desktop could show two equal options).
 */
function oddRows(good: Pair[], pool: Pair[], bad: Pair[], correctIdx: number): string[] {
  const rows: string[][] = []
  const seen = new Set([rowKey(good.map((w) => w[0]))])
  for (let i = 0; i < 4; i++) {
    if (i === correctIdx) {
      rows.push(good.map((w) => w[0]))
      continue
    }
    let row: string[] = []
    for (let tries = 0; tries < 50; tries++) {
      const b = choice(bad)
      const g2 = sample(pool.filter((w) => !good.includes(w)), 2)
      row = shuffle([g2[0][0], b[0], g2[1][0]])
      if (!seen.has(rowKey(row))) break
    }
    seen.add(rowKey(row))
    rows.push(row)
  }
  return rows.map((r) => r.join(', '))
}

registerDrill('ukrmova_double', () => {
  const pureNo: Pair[] = [
    ['барок..о', 'бароко'], ['фін..ський', 'фінський'], ['ан..отація', 'анотація'],
    ['лібрет..о', 'лібрето'], ['ім..ітація', 'імітація'], ['хоб..і', 'хобі'],
    ['ал..ея', 'алея'], ['ем..ігрант', 'емігрант'], ['крос..ворд', 'кросворд'],
    ['кол..екція', 'колекція'], ['мас..а', 'маса'], ['дискус..ія', 'дискусія'],
  ]
  const pureYes: Pair[] = [
    ['буд..изм', 'буддизм (власна назва Будда → подвоєння)'],
    ['андор..ський', 'андоррський (Андорра → подвоєння)'],
    ['гол..андський', 'голландський (Голландія → подвоєння)'],
    ['тон..а', 'тонна (виняток!)'],
    ['віл..а', 'вілла (виняток!)'],
    ['ван..а', 'ванна (виняток!)'],
    ['брут..о', 'брутто (виняток!)'],
    ['нет..о', 'нетто (виняток!)'],
  ]
  const good = sample(pureNo, 3)
  const correctIdx = randint(0, 3)
  const labels = [...LABELS4]
  return {
    subject: 'ukrmova',
    section: 'Орфографія',
    source: GEN_SOURCE,
    qtype: 'single',
    max_points: 1,
    prompt: 'НЕ ТРЕБА писати подвоєних букв у всіх словах рядка:',
    options: oddRows(good, pureNo, pureYes, correctIdx),
    labels,
    answer: labels[correctIdx],
    hint: 'У загальних запозичених словах подвоєння зазвичай НЕМАЄ (алея, хобі, бароко). Подвоєння зберігається лише у винятках (тонна, вілла, ванна, брутто, нетто) та у словах від власних назв (буддизм, андоррський).',
    rule: 'В українській мові в загальних словах іншомовного походження подвоєння приголосних не передається (бароко, лібрето, хобі, фінський, анотація). Винятки: тонна, вілла, ванна, мадонна, брутто, нетто, мірра та похідні від власних назв (буддизм, голландський, андоррський).',
    solution: `У рядку ${labels[correctIdx]} усі слова — загальні назви без винятків: ${good.map((w) => w[1]).join(', ')}.`,
    drill_key: 'ukrmova_double',
  }
})

registerDrill('ukrmova_myak', () => {
  const yesB: Pair[] = [
    ['нян..чин', 'няньчин'], ['запоріз..кий', 'запорізький'],
    ['перекин..те', 'перекиньте'], ['слиз..ко', 'слизько'],
    ['учител..ський', 'учительський'], ['погод..ся', 'погодься'],
    ['сіл..ський', 'сільський'], ['виріз..блений', 'вирізьблений'],
    ['по-польс..кому', 'по-польському'], ['донец..кий', 'донецький'],
  ]
  const noB: Pair[] = [
    ['камін..чик', 'камінчик (перед Ч після Н знак м’якшення не пишеться)'],
    ['тон..ший', 'тонший (перед Ш після Н знак м’якшення не пишеться)'],
    ['велогон..щик', 'велогонщик (перед Щ після Н знак м’якшення не пишеться)'],
    ['брин..чати', 'бринчати (перед Ч після Н знак м’якшення не пишеться)'],
    ['базікаєш..', 'базікаєш (після шиплячих знак м’якшення ніколи не пишеться)'],
    ['чотир..ма', 'чотирма (після Р у середині/кінці слова знак м’якшення не пишеться)'],
  ]
  const good = sample(yesB, 3)
  const correctIdx = randint(0, 3)
  const labels = [...LABELS4]
  return {
    subject: 'ukrmova',
    section: 'Орфографія',
    source: GEN_SOURCE,
    qtype: 'single',
    max_points: 1,
    prompt: 'М’який знак на місці пропуску треба писати в усіх словах рядка:',
    options: oddRows(good, yesB, noB, correctIdx),
    labels,
    answer: labels[correctIdx],
    hint: 'Пам’ятай: після Н перед Ж, Ч, Ш, Щ (інший, менший, камінчик, гонщик) і після Р (чотирма) м’який знак НЕ пишеться!',
    rule: 'Ь пишеться після Д, Т, З, С, Ц, Л, Н («Де Ти З’їСи Ці ЛиНи»), у суфіксах -ськ-, -зьк-, -цьк-, у наказовому способі. НЕ пишеться: після шиплячих (читаєш), після Р (чотирма), а також у сполуках НЧ, НШ, НЩ (камінчик, тонший, гонщик).',
    solution: `Правильний рядок ${labels[correctIdx]}: ${good.map((w) => w[1]).join(', ')}.`,
    drill_key: 'ukrmova_myak',
  }
})

registerDrill('ukrmova_rodovyi', () => {
  const uWords: Pair[] = [
    ['конкурсного бал..', 'конкурсного балу (абстрактне поняття/величина)'],
    ['сильного вітр..', 'сильного вітру (явище природи)'],
    ['весняного дощ..', 'весняного дощу (опади)'],
    ['запашного ча..', 'запашного чаю (напій/речовина)'],
    ['міцного цукр..', 'міцного цукру (речовина)'],
    ['зеленого га..', 'зеленого гаю (збірний простір)'],
  ]
  const aWords: Pair[] = [
    ['складання парашут..', 'парашута (конкретний предмет)'],
    ['відстань одного кілометр..', 'кілометра (міра довжини)'],
    ['висота старого дуб..', 'дуба (окреме дерево)'],
    ['ціна нового телефон..', 'телефона (конкретний прилад)'],
    ['розмір прямокутник..', 'прямокутника (геометрична фігура)'],
    ['діаметр круг..', 'круга (геометрична фігура)'],
    ['початок березн..', 'березня (місяць)'],
  ]
  const win = choice(uWords)
  const wrongs = sample(aWords, 3)
  const correctIdx = randint(0, 3)
  const options: string[] = []
  let w = 0
  for (let i = 0; i < 4; i++) {
    if (i === correctIdx) options.push(win[0])
    else options.push(wrongs[w++][0])
  }
  const labels = [...LABELS4]
  return {
    subject: 'ukrmova',
    section: 'Морфологія',
    source: GEN_SOURCE,
    qtype: 'single',
    max_points: 1,
    prompt: 'Закінчення -у (-ю) у родовому відмінку однини треба писати на місці пропуску в слові:',
    options,
    labels,
    answer: labels[correctIdx],
    hint: 'Конкретні предмети, люди, дерева, міри довжини та терміни-фігури мають -а (-я). Речовини, явища природи, абстрактні поняття — -у (-ю).',
    rule: 'У родовому відмінку однини іменників II відміни -а/-я пишемо в чітко окреслених предметів (парашута, телефона), мір (кілометра), місяців (березня), дерев (дуба). Закінчення -у/-ю пишемо в речовин (цукру, чаю), явищ природи (вітру, дощу) та абстрактних понять (балу, успіху).',
    solution: `Правильна відповідь ${labels[correctIdx]}: «${win[1]}». Інші слова позначають конкретні предмети або одиниці виміру й мають закінчення -а/-я.`,
    drill_key: 'ukrmova_rodovyi',
  }
})
