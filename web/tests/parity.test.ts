// The TypeScript core must give the same answers as the Python desktop app.
// Reference values come from tools/export_web_data.py (web/tests/fixtures/*.json).

import { describe, expect, it } from 'vitest'
import { BANK, scoreToNmt200 } from '../src/core/config'
import { blockScore, computeSubjectSummary, evaluateAnswer, newBlock } from '../src/core/engine'
import { build10Hints } from '../src/core/hints'
import * as cabinet from '../src/core/cabinet'
import type { Block, StudentAnswer, Task } from '../src/core/types'
import evaluateCases from './fixtures/evaluate.json'
import nmtCases from './fixtures/nmt200.json'
import hintCases from './fixtures/hints.json'
import summaryCases from './fixtures/summary.json'
import cabinetCase from './fixtures/cabinet.json'

const BY_ID: Record<string, Task> = {}
for (const tasks of Object.values(BANK)) for (const t of tasks) BY_ID[t.id!] = t

type EvalCase = { task_id?: string; task?: Task; answer: StudentAnswer; expected: unknown[] }

describe('evaluateAnswer', () => {
  it(`matches Python on ${evaluateCases.length} answers`, () => {
    const bad: unknown[] = []
    for (const c of evaluateCases as unknown as EvalCase[]) {
      const q = c.task ?? BY_ID[c.task_id!]
      const got = evaluateAnswer(q, c.answer)
      if (JSON.stringify(got) !== JSON.stringify(c.expected)) bad.push({ id: c.task_id, answer: c.answer, got, expected: c.expected })
    }
    expect(bad).toEqual([])
  })
})

describe('scoreToNmt200', () => {
  it('matches every conversion table', () => {
    for (const c of nmtCases as Array<{ subject: string; raw: number; expected: number | null }>) {
      expect([c.subject, c.raw, scoreToNmt200(c.subject, c.raw)]).toEqual([c.subject, c.raw, c.expected])
    }
  })
})

describe('build10Hints', () => {
  it(`matches Python for all ${hintCases.length} bank tasks`, () => {
    for (const c of hintCases as Array<{ task_id: string; expected: string[] }>) {
      expect([c.task_id, build10Hints(BY_ID[c.task_id])]).toEqual([c.task_id, c.expected])
    }
  })
})

type JsonBlock = Omit<Block, 'questions'> & { questions: string[] }

function blockFrom(j: JsonBlock): Block {
  const b = newBlock(j.subject, j.questions.map((id) => ({ ...BY_ID[id] })))
  b.points = j.points
  b.mistakes = j.mistakes
  b.drills_done = j.drills_done
  return b
}

describe('subject summary', () => {
  it('computeSubjectSummary and blockScore match Python', () => {
    for (const c of summaryCases as unknown as Array<{ block: JsonBlock; summary: unknown; score: unknown }>) {
      const b = blockFrom(c.block)
      expect(computeSubjectSummary(b)).toEqual(c.summary)
      expect(blockScore(b)).toEqual(c.score)
    }
  })
})

describe('cabinet', () => {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const c = cabinetCase as any
  const results = c.results

  it('subjectStats', () => {
    for (const [sid, expected] of Object.entries(c.subject_stats)) expect(cabinet.subjectStats(results, sid, c.profile)).toEqual(expected)
  })
  it('cabinetSubjects', () => expect(cabinet.cabinetSubjects(results, c.profile)).toEqual(c.cabinet_subjects))
  it('progressSeries', () => {
    for (const [sid, expected] of Object.entries(c.progress_series)) expect(cabinet.progressSeries(results, sid)).toEqual(expected)
  })
  it('weakTopics', () => {
    expect(cabinet.weakTopics(results)).toEqual(c.weak_topics)
    expect(cabinet.weakTopics(results, ['math'], 3)).toEqual(c.weak_topics_math)
  })
  it('history and modes', () => {
    expect(cabinet.history(results)).toEqual(c.history)
    expect(cabinet.history(results, 3)).toEqual(c.history_3)
    expect(results.map(cabinet.sessionMode)).toEqual(c.session_modes)
  })
  it('formatWhen', () => {
    for (const [iso, expected] of Object.entries(c.format_when)) expect(cabinet.formatWhen(iso)).toEqual(expected)
  })
})
