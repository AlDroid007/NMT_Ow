// Invariants of the generators and test assembly (random, so run many times with a fixed seed).

import { afterAll, beforeAll, describe, expect, it } from 'vitest'
import { SUBJECT_GENERATORS, SUBJECTS_CONFIG, SUBJECTS_ORDER } from '../src/core/config'
import {
  buildMistakeDrillPlan, buildSectionPlan, evaluateAnswer, generateIdenticalDrill, generateTestForSubject, isEmptyAnswer,
  newBlock, subjectSections,
} from '../src/core/engine'
import { generatorCount, getGenerator } from '../src/core/generators'
import { build10Hints } from '../src/core/hints'
import { daysWord, normalizeProfile, parseExamDate, ProfileError, shortName } from '../src/core/profiles'
import { pyFloatStr, pyRound, pyRoundTo, seededRandom, setRandom } from '../src/core/py'
import type { Task } from '../src/core/types'

let prev: () => number
beforeAll(() => (prev = setRandom(seededRandom(20261120))))
afterAll(() => setRandom(prev))

const RUNS = 200

describe('generators', () => {
  it('has all 40 desktop generators', () => {
    expect(generatorCount()).toBe(40)
    for (const keys of Object.values(SUBJECT_GENERATORS)) for (const k of keys) expect(getGenerator(k), k).toBeTypeOf('function')
  })

  for (const [sid, keys] of Object.entries(SUBJECT_GENERATORS)) {
    for (const key of keys) {
      it(`${key}: the right answer passes, wrong ones fail`, () => {
        for (let n = 0; n < RUNS; n++) {
          const q = getGenerator(key)!()
          expect(q.subject).toBe(sid)
          expect(q.drill_key).toBe(key)
          expect(q.prompt).toBeTruthy()
          const [ok, pts] = evaluateAnswer(q, q.answer as string)
          expect([key, ok, pts]).toEqual([key, true, q.max_points])
          if (q.qtype === 'single') {
            expect(q.options!.length).toBe(q.labels!.length)
            expect(new Set(q.options).size, `${key} options ${q.options}`).toBe(q.options!.length)
            expect(q.labels).toContain(q.answer)
            for (const l of q.labels!) if (l !== q.answer) expect(evaluateAnswer(q, l)[0]).toBe(false)
          }
          if (q.qtype === 'sequence') expect([...(q.answer as string)].sort()).toEqual(Object.keys(q.items!).sort())
          expect(build10Hints(q)).toHaveLength(10)
        }
      })
    }
  }
})

describe('test assembly', () => {
  for (const sid of SUBJECTS_ORDER) {
    it(`${sid}: quick / medium / full have the right size and no repeated prompts`, () => {
      const cfg = SUBJECTS_CONFIG[sid]
      for (const [mode, n] of [['quick', 8], ['medium', Math.min(15, cfg.total_tasks)], ['full', cfg.total_tasks]] as const) {
        const qs = generateTestForSubject(sid, mode)
        expect(qs.length).toBe(n)
        expect(new Set(qs.map((q) => q.id)).size).toBe(n)
      }
    })
  }

  it('identical drills keep the rule and change the task', () => {
    const q = getGenerator('math_ineq')!()
    for (let i = 0; i < 20; i++) {
      const d = generateIdenticalDrill(q)
      expect(d.is_drill).toBe(true)
      expect(d.drill_key).toBe('math_ineq')
      expect(d.prompt).not.toBe(q.prompt)
    }
    const bankTask: Task = { subject: 'history', qtype: 'single', prompt: 'x' }
    expect(generateIdenticalDrill(bankTask).subject).toBe('history')
  })

  it('nothing chosen counts as no answer', () => {
    for (const a of [null, undefined, '', [], {}, { 1: '', 2: '' }]) expect(isEmptyAnswer(a), JSON.stringify(a)).toBe(true)
    for (const a of ['А', ['1'], { 1: 'Б' }]) expect(isEmptyAnswer(a)).toBe(false)
  })

  it('mistake drill has one task per mistake', () => {
    const b = newBlock('math', generateTestForSubject('math', 'quick'))
    b.mistakes = [0, 3, 5]
    const plan = buildMistakeDrillPlan([b, newBlock('ukrmova', [])])
    expect(plan).toHaveLength(1)
    expect(plan[0].questions).toHaveLength(3)
  })

  it('section plans only use that section', () => {
    for (const sid of SUBJECTS_ORDER) {
      for (const sec of subjectSections(sid)) {
        const plan = buildSectionPlan(sid, sec)
        expect(plan.length, `${sid} / ${sec}`).toBe(1)
        for (const q of plan[0].questions) expect(q.section ?? 'Загальне').toBe(sec)
      }
    }
  })
})

describe('python helpers', () => {
  it('round like Python', () => {
    expect([pyRound(0.5), pyRound(1.5), pyRound(2.5), pyRound(-0.5) + 0, pyRound(2.6)]).toEqual([0, 2, 2, 0, 3])
    expect([pyRoundTo(2.675, 2), pyRoundTo(0.125, 2), pyRoundTo(25, -1), pyRoundTo(35, -1), pyRoundTo(12.25, 1)]).toEqual([2.67, 0.12, 20, 40, 12.2])
    expect([pyFloatStr(30), pyFloatStr(12.3), pyFloatStr(-0.5), pyFloatStr(1e-5)]).toEqual(['30.0', '12.3', '-0.5', '1e-05'])
  })
})

describe('profiles', () => {
  it('validates names, targets and dates', () => {
    const p = normalizeProfile({ name: '  Ліза   К ', subjects: ['math', 'ukrmova', 'nope'], targets: { math: '180' as unknown as number }, exam_date: '20.05.2027' })
    expect(p.name).toBe('Ліза К')
    expect(p.subjects).toEqual(['ukrmova', 'math'])
    expect(p.targets).toEqual({ math: 180 })
    expect(p.exam_date).toBe('2027-05-20')
    expect(p.avatar.value).toBe('🦉')
    expect(() => normalizeProfile({ name: ' ' })).toThrow(ProfileError)
    expect(() => normalizeProfile({ name: 'A', targets: { math: 90 } })).toThrow('від 100 до 200')
    expect(() => parseExamDate('31.02.2027')).toThrow(ProfileError)
    expect([daysWord(1), daysWord(3), daysWord(12), daysWord(21), daysWord(25)]).toEqual(['день', 'дні', 'днів', 'день', 'днів'])
    expect(shortName('Олександра', 5)).toBe('Олек…')
  })
})
