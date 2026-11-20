// Personal cabinet numbers computed from stored session results, no UI and no storage
// (port of nmt_tutor/cabinet.py). Input: results oldest first, as the cloud history returns them.
// Mistake-practice sessions only repeat wrong answers, so they are left out of the score
// statistics and the chart but still count for weak topics.

import { SUBJECTS_CONFIG, SUBJECTS_ORDER } from './config'
import { targetFor, type Profile } from './profiles'
import { pyRound, pyRoundTo } from './py'
import type { SessionResult, SubjectSummary } from './types'

export const RECENT_WINDOW = 3 // sessions in the "recent level" average
export const WEAK_DECAY = 0.85 // weight of a mistake per session it is older
export const WEAK_HISTORY = 12 // sessions per subject looked at for weak topics

export const MODE_TITLES: Record<string, string> = {
  tutor: 'Із Совою',
  exam: 'Режим іспиту',
  drill: 'Робота над помилками',
  focus: 'Тема',
}

type Result = Partial<SessionResult> & { subjects?: Array<Partial<SubjectSummary>> }
type Entry = [Result, Partial<SubjectSummary>]

const scored = (results: Result[]) => results.filter((r) => !r.mistake_drill)

/** (result, subject summary) pairs of one subject, oldest first. */
function entries(results: Result[], subjectId: string): Entry[] {
  const out: Entry[] = []
  for (const res of results) for (const s of res.subjects ?? []) if (s.subject === subjectId) out.push([res, s])
  return out
}

function mean(values: Array<number | null | undefined>): number | null {
  const v = values.filter((x): x is number => x !== null && x !== undefined)
  return v.length ? pyRound(v.reduce((a, b) => a + b, 0) / v.length) : null
}

export interface SubjectStats {
  subject: string
  name: string
  sessions: number
  failed: number
  avg: number | null
  best: number | null
  last: number | null
  recent: number | null
  trend: number | null
  accuracy: number | null
  drills_done: number
  target: number | null
  gap: number | null
  last_at: string | null
}

/** Numbers for one subject card. */
export function subjectStats(results: Result[], subjectId: string, profile?: Partial<Profile> | null): SubjectStats {
  const ents = entries(scored(results), subjectId)
  const scores = ents.map(([, s]) => (s.nmt_200 ?? null) as number | null)
  const earned = ents.reduce((a, [, s]) => a + (s.earned ?? 0), 0)
  const total = ents.reduce((a, [, s]) => a + (s.actual_max ?? 0), 0)
  const passed = scores.filter((v): v is number => v !== null)
  const recent = passed.length ? mean(scores.slice(-RECENT_WINDOW)) : null
  const before = scores.length > RECENT_WINDOW ? mean(scores.slice(-2 * RECENT_WINDOW, -RECENT_WINDOW)) : null
  const target = profile ? (targetFor(profile, subjectId) ?? null) : null
  return {
    subject: subjectId,
    name: SUBJECTS_CONFIG[subjectId].name,
    sessions: ents.length,
    failed: scores.length - passed.length,
    avg: mean(passed),
    best: passed.length ? Math.max(...passed) : null,
    last: scores.length ? scores[scores.length - 1] : null,
    recent,
    trend: recent !== null && before !== null ? recent - before : null,
    accuracy: total ? pyRound((100 * earned) / total) : null,
    drills_done: entries(results, subjectId).reduce((a, [, s]) => a + (s.drills_done ?? 0), 0),
    target,
    gap: target !== null && recent !== null ? target - recent : null,
    last_at: ents.length ? ((ents[ents.length - 1][0].created_at ?? null) as string | null) : null,
  }
}

/** Subjects shown in the cabinet: the profile's own plus any with results, in NMT order. */
export function cabinetSubjects(results: Result[], profile?: Partial<Profile> | null): string[] {
  const wanted = new Set<string | undefined>(profile?.subjects ?? [])
  for (const res of results) for (const s of res.subjects ?? []) wanted.add(s.subject)
  return SUBJECTS_ORDER.filter((sid) => wanted.has(sid))
}

export interface ProgressPoint {
  at: string | null
  nmt_200: number | null
  accuracy: number | null
}

/** Chart points, oldest first (nmt_200 null = below threshold). */
export function progressSeries(results: Result[], subjectId: string): ProgressPoint[] {
  return entries(scored(results), subjectId).map(([res, s]) => {
    const mx = s.actual_max || 0
    return {
      at: (res.created_at ?? null) as string | null,
      nmt_200: (s.nmt_200 ?? null) as number | null,
      accuracy: mx ? pyRound((100 * (s.earned ?? 0)) / mx) : null,
    }
  })
}

export interface WeakTopic {
  subject: string
  subject_name: string
  section: string
  mistakes: number
  score: number
}

const cmp = (a: string, b: string) => (a < b ? -1 : a > b ? 1 : 0)

/** Sections with the most mistakes, worst first; recent sessions weigh more. */
export function weakTopics(results: Result[], subjects?: string[] | null, limit = 8): WeakTopic[] {
  const subs = subjects && subjects.length ? subjects : SUBJECTS_ORDER
  const scores = new Map<string, WeakTopic>()
  for (const sid of subs) {
    const ents = entries(results, sid).slice(-WEAK_HISTORY).reverse()
    ents.forEach(([, s], age) => {
      const weight = WEAK_DECAY ** age
      for (const [section, cnt] of Object.entries(s.weak_sections ?? {})) {
        const key = JSON.stringify([sid, section])
        let item = scores.get(key)
        if (!item) {
          item = { subject: sid, subject_name: SUBJECTS_CONFIG[sid].name, section, mistakes: 0, score: 0 }
          scores.set(key, item)
        }
        item.mistakes += cnt
        item.score += cnt * weight
      }
    })
  }
  const ranked = [...scores.values()].sort(
    (a, b) => b.score - a.score || b.mistakes - a.mistakes || cmp(a.subject_name, b.subject_name) || cmp(a.section, b.section),
  )
  for (const item of ranked) item.score = pyRoundTo(item.score, 2)
  return ranked.slice(0, limit)
}

export type SessionMode = 'drill' | 'focus' | 'tutor' | 'exam'

export function sessionMode(result: Result): SessionMode {
  if (result.mistake_drill) return 'drill'
  if (result.focus_section) return 'focus'
  return result.tutor_mode ? 'tutor' : 'exam'
}

export interface HistoryRow {
  id: string | number | null
  at: string | null
  mode: SessionMode
  title: string
  report_id: string | number | null
  subjects: Array<{ subject: string | undefined; name: string | undefined; nmt_200: number | null | undefined; earned: number | undefined; actual_max: number | undefined }>
}

/** Rows for the history list, newest first. */
export function history(results: Result[], limit?: number | null): HistoryRow[] {
  const rows: HistoryRow[] = []
  for (const res of [...results].reverse()) {
    const mode = sessionMode(res)
    const title = mode === 'focus' ? `Тема: ${res.focus_section}` : MODE_TITLES[mode]
    rows.push({
      id: res.id ?? null,
      at: (res.created_at ?? null) as string | null,
      mode,
      title,
      report_id: res.report_id ?? null,
      subjects: (res.subjects ?? []).map((s) => ({
        subject: s.subject,
        name: (s.subject && SUBJECTS_CONFIG[s.subject]?.name) ?? s.subject,
        nmt_200: s.nmt_200,
        earned: s.earned,
        actual_max: s.actual_max,
      })),
    })
    if (limit && rows.length >= limit) break
  }
  return rows
}

const ISO_RE = /^(\d{4})-(\d{2})-(\d{2})(?:[T ](\d{2})(?::?(\d{2})(?::?(\d{2})(?:[.,]\d+)?)?)?)?(?:Z|[+-]\d{2}(?::?\d{2})?)?$/

/** '15.11.2026 21:40' from an ISO timestamp (wall-clock time as written, like datetime.fromisoformat). */
export function formatWhen(iso: string | null | undefined): string {
  if (!iso) return iso ?? ''
  const m = ISO_RE.exec(iso)
  if (!m) return iso
  const [, y, mo, d, h = '00', mi = '00'] = m
  const dt = new Date(Date.UTC(+y, +mo - 1, +d))
  if (dt.getUTCMonth() !== +mo - 1 || dt.getUTCDate() !== +d || +h > 23 || +mi > 59) return iso
  return `${d}.${mo}.${y} ${h}:${mi}`
}
