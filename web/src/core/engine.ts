// Test engine: answer checking, test assembly, identical drills, scoring and the text report
// (port of nmt_tutor/engine.py).

import { BANK, SUBJECTS_CONFIG, scoreToNmt200 } from './config'
import { generatorsForSubject, getGenerator, hasGenerator } from './generators'
import { choice, floorDiv, pyFloat, pyRound, pyStr, randint, shuffle, sortedStrings } from './py'
import type { AnswerRecord, Block, Plan, SessionResult, StudentAnswer, SubjectSummary, Task } from './types'

type Bank = Record<string, Task[]>

// Latin letters that look like Cyrillic answer labels (A/А, B/В, C/С, ...).
const LABEL_EQUIV: Record<string, string> = { A: 'А', B: 'В', C: 'С', E: 'Е', K: 'К', M: 'М', O: 'О', P: 'Р', T: 'Т', X: 'Х' }
const MATCH_EQUIV: Record<string, string> = { A: 'А', B: 'В', C: 'С', E: 'Е' }

function normalizeNumStr(s: unknown): string {
  return pyStr(s).trim().replace(/,/g, '.').replace(/ /g, '').replace(/−/g, '-')
}

function numsEqual(a: unknown, b: unknown): boolean {
  const na = normalizeNumStr(a)
  const nb = normalizeNumStr(b)
  if (na.toLowerCase() === nb.toLowerCase()) return true
  const fa = pyFloat(na)
  const fb = pyFloat(nb)
  if (fa === null || fb === null) return false
  return Math.abs(fa - fb) < 1e-6
}

function sameLabel(a: string, b: string, equiv: Record<string, string>): boolean {
  return a === b || equiv[a] === b || equiv[b] === a
}

/** True when the student has not chosen or typed anything yet. */
export function isEmptyAnswer(ans: unknown): boolean {
  // null: nothing chosen yet on the web (the desktop widgets always return "" instead)
  if (ans === null || ans === undefined || ans === '' || (Array.isArray(ans) && ans.length === 0)) return true
  if (ans && typeof ans === 'object' && !Array.isArray(ans)) return !Object.values(ans).some((v) => !!v)
  return false
}

/** [is fully correct, earned points, student's answer as text, correct answer as text] */
export type Evaluation = [boolean, number, string, string]

export function evaluateAnswer(q: Task, userAns: StudentAnswer | null | undefined): Evaluation {
  const qt = q.qtype
  const maxPts = q.max_points ?? 1

  if (qt === 'single') {
    const ans = pyStr(userAns).trim().toUpperCase()
    const corr = pyStr(q.answer).trim().toUpperCase()
    const labels = (q.labels ?? []).map((l) => String(l).toUpperCase())
    const isOk = sameLabel(ans, corr, LABEL_EQUIV)
    const opts = q.options ?? []
    const fmtOpt = (lbl: string) => {
      const n = Math.min(labels.length, opts.length)
      for (let i = 0; i < n; i++) if (sameLabel(labels[i], lbl, LABEL_EQUIV)) return `${lbl} (${opts[i]})`
      return lbl || '—'
    }
    return [isOk, isOk ? maxPts : 0, fmtOpt(ans), fmtOpt(corr)]
  }

  if (qt === 'short') {
    const ansRaw = pyStr(userAns).trim()
    const corrRaw = pyStr(q.answer).trim()
    const isOk = !!ansRaw && numsEqual(ansRaw, corrRaw)
    return [isOk, isOk ? maxPts : 0, ansRaw || '—', corrRaw]
  }

  if (qt === 'matching') {
    const corrMap = q.answer as Record<string, unknown>
    const uMap = (userAns && typeof userAns === 'object' && !Array.isArray(userAns) ? userAns : {}) as Record<string, unknown>
    let pts = 0
    const uParts: string[] = []
    const cParts: string[] = []
    const keys = sortedStrings(Object.keys(corrMap))
    for (const k of keys) {
      const cVal = pyStr(corrMap[k]).trim().toUpperCase()
      const uVal = (k in uMap ? pyStr(uMap[k]) : '').trim().toUpperCase()
      if (sameLabel(uVal, cVal, MATCH_EQUIV)) pts += 1
      uParts.push(`${k}–${uVal || '?'}`)
      cParts.push(`${k}–${cVal}`)
    }
    return [pts === keys.length, Math.min(pts, maxPts), uParts.join(', '), cParts.join(', ')]
  }

  if (qt === 'sequence') {
    const uStr = Array.from(pyStr(userAns).trim().toUpperCase().replace(/[ \-–]/g, ''))
    const cStr = Array.from(pyStr(q.answer).trim().toUpperCase())
    // НМТ points for a sequence: 3 — all four, 2 — first and last, 1 — first or last
    let pts = 0
    const u = uStr.join('')
    const c = cStr.join('')
    if (uStr.length === 4 && cStr.length === 4) {
      if (u === c) pts = 3
      else if (uStr[0] === cStr[0] && uStr[3] === cStr[3]) pts = 2
      else if (uStr[0] === cStr[0] || uStr[3] === cStr[3]) pts = 1
    }
    return [u === c, pts, u || '—', c]
  }

  if (qt === 'multi3') {
    const uSet = sortedStrings(new Set(((userAns as unknown[]) || []).map((x) => pyStr(x).trim())))
    const cSet = sortedStrings(new Set((q.answer as unknown[]).map((x) => pyStr(x).trim())))
    // НМТ «3 of 7»: 1 point per correct choice if no more than 3 are chosen
    const pts = uSet.length > 3 ? Math.max(0, 3 - uSet.length) : uSet.filter((x) => cSet.includes(x)).length
    const isOk = uSet.length === cSet.length && uSet.every((x, i) => x === cSet[i])
    return [isOk, pts, uSet.join(', ') || '—', cSet.join(', ')]
  }

  return [false, 0, pyStr(userAns), pyStr(q.answer ?? '')]
}

/** An identical example (new numbers or words) for the task's rule; falls back to a task of the same subject. */
export function generateIdenticalDrill(q: Task, usedPrompts?: Iterable<string>): Task {
  const used = new Set(usedPrompts ?? [])
  used.add(q.prompt ?? '')
  const dkey = q.drill_key

  const genFn = hasGenerator(dkey) ? getGenerator(dkey) : undefined
  if (genFn) {
    for (let i = 0; i < 15; i++) {
      const cand = genFn()
      if (!used.has(cand.prompt ?? '')) return { ...cand, is_drill: true }
    }
    return { ...genFn(), is_drill: true }
  }

  const subj = q.subject ?? 'math'
  const gens = generatorsForSubject(subj)
  if (gens.length) return { ...getGenerator(choice(gens))!(), is_drill: true }

  const pool = (BANK[subj] ?? []).filter((item) => item.prompt !== q.prompt)
  if (pool.length) return { ...choice(pool), is_drill: true }

  return { ...q, is_drill: true }
}

/** A random test of one subject: 'quick' — 8 tasks, 'medium' — 15, 'full' — the official count. */
export function generateTestForSubject(subjectId: string, lengthMode: string = 'quick', customBank?: Bank | null): Task[] {
  const cfg = SUBJECTS_CONFIG[subjectId]
  const targetN = lengthMode === 'quick' ? 8 : lengthMode === 'medium' ? Math.min(15, cfg.total_tasks) : cfg.total_tasks

  const questions: Task[] = []
  const seenPrompts = new Set<string | undefined>()

  // 1. Custom tasks from a loaded JSON (desktop only for now)
  if (customBank && subjectId in customBank) {
    const customPool = shuffle([...customBank[subjectId]])
    for (const q of customPool) {
      if (questions.length >= targetN) break
      if (!seenPrompts.has(q.prompt)) {
        questions.push({ ...q })
        seenPrompts.add(q.prompt)
      }
    }
  }

  // 2. Bank tasks in random order
  const staticPool = shuffle([...(BANK[subjectId] ?? [])])
  // Kept as in v3.5: this bound never stops the loop early, so the bank fills the test up to targetN.
  const staticLimit = lengthMode === 'full' ? targetN : Math.max(3, floorDiv(targetN, 2))
  for (const q of staticPool) {
    if (questions.length >= Math.min(targetN, staticLimit + questions.length)) break
    if (!seenPrompts.has(q.prompt)) {
      questions.push({ ...q })
      seenPrompts.add(q.prompt)
    }
    if (questions.length >= targetN) break
  }

  // 3. Generators fill the rest
  const gens = generatorsForSubject(subjectId)
  let attempts = 0
  while (questions.length < targetN && attempts < targetN * 8) {
    attempts += 1
    if (gens.length) {
      const gkey = gens[(questions.length + attempts) % gens.length]
      const cand = getGenerator(gkey)!()
      if (!seenPrompts.has(cand.prompt) || attempts > targetN * 4) {
        cand.id = `${subjectId}_gen_${questions.length + 1}_${randint(100, 999)}`
        questions.push(cand)
        seenPrompts.add(cand.prompt)
      }
    } else if (staticPool.length) {
      const cand: Task = { ...choice(staticPool) }
      cand.bank_id = cand.id
      cand.id = `${subjectId}_rep_${questions.length + 1}`
      questions.push(cand)
    } else {
      break
    }
  }
  return questions
}

export function newBlock(subjectId: string, questions: Task[]): Block {
  return { subject: subjectId, questions, answers: {}, points: {}, mistakes: [], drills_done: 0, answer_log: {}, hint_log: [] }
}

// --- per-answer and per-hint records (uploaded to the cloud for statistics) --------------

let bankIds: Set<string | undefined> | null = null

/** Stable task id: the bank id, or "gen:<generator key>" for generated tasks. */
export function taskRef(q: Task): string | undefined {
  if (!bankIds) bankIds = new Set(Object.values(BANK).flatMap((tasks) => tasks.map((t) => t.id)))
  if (q.bank_id) return q.bank_id
  if (bankIds.has(q.id)) return q.id
  if (q.drill_key) return `gen:${q.drill_key}`
  return q.id
}

const pad = (n: number) => String(n).padStart(2, '0')

/** datetime.now().isoformat(timespec="seconds"): local time without an offset. */
export function nowIso(d: Date = new Date()): string {
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
}

/** Remembers how task `idx` of the block was answered (the last answer wins). */
export function recordAnswer(block: Block, idx: number, ok: boolean, points: number, checked = true, hintLevel = 0): void {
  const q = block.questions[idx]
  block.answer_log[idx] = {
    subject: block.subject,
    question_no: idx,
    task_id: taskRef(q),
    section: q.section ?? 'Загальне',
    qtype: q.qtype,
    is_correct: !!ok,
    points: Math.trunc(points),
    max_points: Math.trunc(q.max_points ?? 1),
    checked: !!checked,
    max_hint_level: Math.trunc(hintLevel || 0),
    answered_at: nowIso(),
  }
}

/** Remembers that hint `level` (1-10) of task `idx` was opened. */
export function recordHint(block: Block, idx: number, level: number): void {
  block.hint_log.push({
    subject: block.subject,
    question_no: idx,
    task_id: taskRef(block.questions[idx]),
    level: Math.trunc(level),
    opened_at: nowIso(),
  })
}

export function buildSessionPlan(selectedSubjects: string[], lengthMode = 'quick', customBank?: Bank | null): Plan {
  return selectedSubjects.map((sid) => newBlock(sid, generateTestForSubject(sid, lengthMode, customBank)))
}

const GEN_SECTIONS: Record<string, string | undefined> = {}

/** Section of a generator's tasks (generators always produce the same section). */
function generatorSection(key: string): string | undefined {
  if (!(key in GEN_SECTIONS)) {
    const fn = getGenerator(key)
    GEN_SECTIONS[key] = fn ? fn().section : undefined
  }
  return GEN_SECTIONS[key]
}

/** All section names that have tasks for the subject (bank, custom bank, generators). */
export function subjectSections(subjectId: string, customBank?: Bank | null): string[] {
  const found: string[] = []
  const pools = [...(BANK[subjectId] ?? []), ...(customBank?.[subjectId] ?? [])]
  for (const q of pools) if (q.section && !found.includes(q.section)) found.push(q.section)
  for (const key of generatorsForSubject(subjectId)) {
    const sec = generatorSection(key)
    if (sec && !found.includes(sec)) found.push(sec)
  }
  return found
}

/** Up to n tasks of one section: bank and custom tasks first, generators fill the rest. */
export function generateSectionTest(subjectId: string, section: string, n = 8, customBank?: Bank | null): Task[] {
  const pool = shuffle(
    [...(customBank?.[subjectId] ?? []), ...(BANK[subjectId] ?? [])]
      .filter((q) => (q.section ?? 'Загальне') === section)
      .map((q) => ({ ...q })),
  )
  const questions: Task[] = []
  const seen = new Set<string | undefined>()
  for (const q of pool) {
    if (questions.length >= n) break
    if (!seen.has(q.prompt)) {
      seen.add(q.prompt)
      questions.push(q)
    }
  }
  const gens = generatorsForSubject(subjectId).filter((k) => generatorSection(k) === section)
  let attempts = 0
  while (gens.length && questions.length < n && attempts < n * 8) {
    attempts += 1
    const cand = getGenerator(gens[attempts % gens.length])!()
    if (!seen.has(cand.prompt) || attempts > n * 4) {
      seen.add(cand.prompt)
      cand.id = `${subjectId}_focus_${questions.length + 1}_${randint(100, 999)}`
      questions.push(cand)
    }
  }
  return questions
}

/** Session plan that practises one weak topic; empty if the topic has no tasks. */
export function buildSectionPlan(subjectId: string, section: string, n = 8, customBank?: Bank | null): Plan {
  const qs = generateSectionTest(subjectId, section, n, customBank)
  return qs.length ? [newBlock(subjectId, qs)] : []
}

/** One identical example for every mistake of the finished session. */
export function buildMistakeDrillPlan(plan: Plan): Plan {
  const drillPlan: Plan = []
  for (const block of plan) {
    if (block.mistakes.length) {
      drillPlan.push(newBlock(block.subject, block.mistakes.map((idx) => generateIdenticalDrill(block.questions[idx]))))
    }
  }
  return drillPlan
}

/** [earned points, max points] of a block for the live score badge. */
export function blockScore(block: Block): [number, number] {
  const earned = Object.values(block.points).reduce((a, b) => a + b, 0)
  const maxPts = block.questions.reduce((a, q) => a + (q.max_points ?? 1), 0)
  return [earned, maxPts]
}

export function computeSubjectSummary(block: Block): SubjectSummary {
  const sid = block.subject
  const cfg = SUBJECTS_CONFIG[sid]
  const qs = block.questions
  let earned = 0
  for (let i = 0; i < qs.length; i++) earned += block.points[i] ?? 0
  const actualMax = qs.reduce((a, q) => a + (q.max_points ?? 1), 0) || 1
  const isFull = qs.length === cfg.total_tasks && actualMax === cfg.max_score
  const projectedRaw = isFull ? earned : pyRound((earned * cfg.max_score) / actualMax)
  const weak: Record<string, number> = {}
  for (const i of block.mistakes) {
    const sec = qs[i].section ?? 'Загальне'
    weak[sec] = (weak[sec] ?? 0) + 1
  }
  return {
    subject: sid,
    name: cfg.name,
    earned,
    actual_max: actualMax,
    projected_raw: projectedRaw,
    official_max: cfg.max_score,
    threshold: cfg.threshold,
    nmt_200: scoreToNmt200(sid, projectedRaw),
    is_full: isFull,
    drills_done: block.drills_done ?? 0,
    weak_sections: weak,
  }
}

export interface SessionResultOptions {
  mistakeDrill?: boolean
  focusSection?: string | null
  reportId?: string | number | null
  startedAt?: string | null
  sessionUid?: string | null
}

/** Serializable record of a finished session (what the cloud keeps as progress). */
export function buildSessionResult(plan: Plan, lengthMode: string, tutorMode: boolean, opts: SessionResultOptions = {}): SessionResult {
  const answers: AnswerRecord[] = []
  for (const block of plan) {
    const entries = Object.entries(block.answer_log ?? {}).sort((a, b) => Number(a[0]) - Number(b[0]))
    for (const [, rec] of entries) answers.push(rec)
  }
  const result: SessionResult = {
    finished_at: nowIso(),
    length_mode: lengthMode,
    tutor_mode: !!tutorMode,
    mistake_drill: !!opts.mistakeDrill,
    subjects: plan.map(computeSubjectSummary),
    answers,
    hints: plan.flatMap((b) => b.hint_log ?? []),
  }
  if (opts.startedAt) result.started_at = opts.startedAt
  if (opts.sessionUid) result.session_uid = opts.sessionUid
  if (opts.focusSection) result.focus_section = opts.focusSection
  if (opts.reportId !== undefined && opts.reportId !== null) result.report_id = opts.reportId
  return result
}

/** strftime('%d.%m.%Y %H:%M') */
export function formatDateTime(d: Date): string {
  return `${pad(d.getDate())}.${pad(d.getMonth() + 1)}.${d.getFullYear()} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

export function formatResultsReport(plan: Plan, now: Date = new Date()): string {
  return formatSummariesReport(plan.map(computeSubjectSummary), now)
}

/** The same report from stored subject summaries (the web rebuilds old reports from the cloud history). */
export function formatSummariesReport(summaries: SubjectSummary[], when: Date = new Date()): string {
  const bar = '='.repeat(64)
  const lines = [bar, `ЗВІТ ЗА РЕЗУЛЬТАТАМИ ТРЕНУВАННЯ НМТ (${formatDateTime(when)})`, bar, '']
  for (const s of summaries) {
    const nmtStr = s.nmt_200 !== null && s.nmt_200 !== undefined ? `${s.nmt_200} балів` : `Не складено (< ${s.threshold})`
    const modeNote = s.is_full ? 'точний формат' : `прогноз із ${s.actual_max} макс. балів`
    lines.push(`Предмет: ${s.name}`)
    lines.push(`  Набрано балів: ${s.earned} із ${s.actual_max} (${modeNote})`)
    lines.push(`  Оцінка за шкалою НМТ 100–200: ${nmtStr}`)
    lines.push(`  Опрацьовано ідентичних прикладів із репетитором: ${s.drills_done}`)
    const weak = Object.entries(s.weak_sections ?? {})
    if (weak.length) {
      lines.push('  Теми для повторення:')
      for (const [sec, cnt] of weak) lines.push(`    • ${sec} (помилок: ${cnt})`)
    } else {
      lines.push('  Помилок не виявлено!')
    }
    lines.push('')
  }
  return lines.join('\n')
}
