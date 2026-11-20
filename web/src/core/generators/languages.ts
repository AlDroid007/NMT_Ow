// Task generators: Англійська, німецька, французька, іспанська (port of generators/languages.py).
// The A–D case tables are exported from the Python source into data/language_cases.json.

import { choice } from '../py'
import { type Case, caseTableGenerator, GEN_SOURCE, registerDrill } from './common'
import tables from '../data/language_cases.json'

type Table = { subject?: string; section?: string; prompt_head?: string; cases: Case[] }
const TABLES = tables as unknown as Record<string, Table>

for (const [key, t] of Object.entries(TABLES)) {
  if (key === 'eng_reading_ads') continue
  caseTableGenerator(key, t.subject!, t.section!, t.prompt_head!, t.cases)
}

registerDrill('eng_reading_ads', () => {
  const c = choice(TABLES.eng_reading_ads.cases)
  return {
    subject: 'english',
    section: 'Reading: Загальне розуміння (Task 1)',
    source: GEN_SOURCE,
    qtype: 'single',
    max_points: 1,
    prompt: `Read the advertisement. Which topic matches it?\n\n«${c[0]}»\n\nThis advertisement is about _______.`,
    options: [...c[1]],
    labels: ['A', 'B', 'C', 'D'],
    answer: c[2],
    hint: c[3],
    rule: c[4],
    solution: c[5],
    drill_key: 'eng_reading_ads',
  }
})
