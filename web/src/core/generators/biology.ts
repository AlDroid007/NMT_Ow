// Task generators: Біологія (port of generators/biology.py).

import { choice, floorDiv } from '../py'
import { GEN_SOURCE, LABELS4, registerDrill, sortedUnique } from './common'

const SECTION = 'Клітина. Хімічний склад і реалізація спадкової інформації'

registerDrill('bio_dna_percent', () => {
  const pct = choice([12, 16, 18, 22, 28, 32, 36, 42])
  const [givenBase, askBase] = choice([
    ['гуанілових (Г)', 'тимідилових (Т)'],
    ['цитидилових (Ц)', 'аденілових (А)'],
    ['аденілових (А)', 'гуанілових (Г)'],
    ['тимідилових (Т)', 'цитидилових (Ц)'],
  ] as Array<[string, string]>)
  const ans = 50 - pct
  let vals = sortedUnique([ans, pct, 2 * pct <= 100 ? 2 * pct : 100 - pct, 100 - 2 * pct > 0 ? 100 - 2 * pct : ans + 8])
  while (vals.length < 4) vals.push(vals[vals.length - 1] + 4)
  vals = vals.slice(0, 4)
  const labels = [...LABELS4]
  const ci = vals.indexOf(ans)
  return {
    subject: 'biology',
    section: SECTION,
    source: GEN_SOURCE,
    qtype: 'single',
    max_points: 1,
    prompt: `Обчисліть частку (%) ${askBase} нуклеотидів у ділянці дволанцюгової молекули ДНК, якщо частка ${givenBase} становить ${pct} % від загальної кількості.`,
    options: vals.map(String),
    labels,
    answer: labels[ci],
    hint: 'Правило Чаргаффа: А = Т, Г = Ц, а сума А + Т + Г + Ц = 100 %. Отже, (А + Г) або (Т + Г) = 50 %!',
    rule: 'Проста формула для ДНК (правило Чаргаффа): комплементарні нуклеотиди рівні (А = Т, Г = Ц), тому сума некомплементарних (А + Г = 50 % і Т + Ц = 50 %). Щоб знайти інший тип, просто відніми даний відсоток від 50 %!',
    solution: `За правилом Чаргаффа сума некомплементарних пар становить 50 %: ${askBase} = 50 % − ${pct} % = ${ans} % (${labels[ci]}).`,
    drill_key: 'bio_dna_percent',
  }
})

registerDrill('bio_dna_deoxy', () => {
  const aCnt = choice([40, 60, 80, 100, 120])
  const gCnt = choice([30, 50, 70, 90])
  const total = 2 * (aCnt + gCnt)
  const vals = sortedUnique([total, aCnt + gCnt, floorDiv(aCnt + gCnt, 2), total + 100])
  const labels = [...LABELS4]
  const ci = vals.indexOf(total)
  return {
    subject: 'biology',
    section: SECTION,
    source: GEN_SOURCE,
    qtype: 'single',
    max_points: 1,
    prompt: `Ділянка дволанцюгової молекули ДНК містить ${aCnt} аденілових і ${gCnt} гуанілових нуклеотидів. Обчисліть кількість залишків дезоксирибози в цій ділянці ДНК.`,
    options: vals.map(String),
    labels,
    answer: labels[ci],
    hint: 'У КОЖНОМУ нуклеотиді ДНК є рівно 1 залишок дезоксирибози. Але не забудь, що є ще тимідилові (Т = А) і цитидилові (Ц = Г) нуклеотиди!',
    rule: '1 нуклеотид = 1 залишок дезоксирибози. За принципом комплементарності: Т = А, Ц = Г. Тому загальна кількість нуклеотидів (і дезоксирибоз) = 2 · (А + Г).',
    solution: `А = Т = ${aCnt}, Г = Ц = ${gCnt}. Усього нуклеотидів = ${aCnt} + ${aCnt} + ${gCnt} + ${gCnt} = ${total}. Стільки ж і залишків дезоксирибози: ${total} (${labels[ci]}).`,
    drill_key: 'bio_dna_deoxy',
  }
})
