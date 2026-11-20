// Pure conversions between app records and cloud rows (port of the conversion part of
// nmt_tutor/cloud/sync.py). No network here, so it is unit-tested.

import { SUBJECTS_CONFIG } from '../core/config'
import { nowIso } from '../core/engine'
import type { AnswerRecord, HintRecord, SessionResult, SubjectSummary } from '../core/types'

export const LENGTH_MODES = ['quick', 'medium', 'full', 'focus']

/** Dates with more than 3 fraction digits or a space instead of "T" (Postgres output) for every browser. */
function parseTime(text: string): Date {
  let t = text.trim().replace(' ', 'T').replace(/\.(\d+)/, (_m, f: string) => '.' + (f + '000').slice(0, 3))
  if (/[+-]\d{2}$/.test(t)) t += ':00'
  const d = new Date(t)
  if (Number.isNaN(d.getTime())) throw new RangeError(`bad time: ${text}`)
  return d
}

/** Local naive ISO time from the app -> UTC ISO time for the server. */
export function toCloudTime(localIso: string): string {
  return parseTime(localIso).toISOString()
}

/** Server time with offset -> local naive ISO time (how the app keeps times). */
export function toLocalTime(cloudIso: string): string {
  return nowIso(parseTime(cloudIso))
}

function timeOr(value: string | undefined | null, fallback: string): string {
  try {
    return value ? toCloudTime(value) : fallback
  } catch {
    return fallback
  }
}

export interface CloudSessionPayload {
  id: string
  profile_id: string
  started_at: string
  finished_at: string
  length_mode: string
  tutor_mode: boolean
  mistake_drill: boolean
  focus_section: string | null
  subjects: Array<{
    subject: string; earned: number; max_points: number; projected_raw: number | null
    nmt_200: number | null; is_full: boolean; drills_done: number
  }>
  answers: AnswerRecord[]
  hints: HintRecord[]
}

/** Argument of submit_session() for a finished training (see the SQL migration). */
export function sessionPayload(result: SessionResult, sessionId: string, profileId: string): CloudSessionPayload {
  const finished = timeOr(result.finished_at, new Date().toISOString())
  const started = timeOr(result.started_at, finished)
  const mode = result.length_mode
  return {
    id: sessionId,
    profile_id: profileId,
    started_at: started,
    finished_at: finished,
    length_mode: LENGTH_MODES.includes(mode) ? mode : 'quick',
    tutor_mode: result.tutor_mode ?? true,
    mistake_drill: !!result.mistake_drill,
    focus_section: result.focus_section ?? null,
    subjects: (result.subjects ?? []).map((s) => ({
      subject: s.subject,
      earned: s.earned ?? 0,
      max_points: s.actual_max ?? 0,
      projected_raw: s.projected_raw ?? null,
      nmt_200: s.nmt_200 ?? null,
      is_full: !!s.is_full,
      drills_done: s.drills_done ?? 0,
    })),
    answers: (result.answers ?? []).map((a) => ({ ...a, answered_at: timeOr(a.answered_at, finished) })),
    hints: (result.hints ?? []).map((h) => ({ ...h, opened_at: timeOr(h.opened_at, finished) })),
  }
}

export interface SessionRow {
  id: string
  started_at: string
  finished_at: string | null
  length_mode: string
  tutor_mode: boolean
  mistake_drill: boolean
  focus_section: string | null
  subjects: string[] | null
}
export interface SubjectRow {
  session_id: string; subject: string; earned: number; max_points: number
  projected_raw: number | null; nmt_200: number | null; is_full: boolean; drills_done: number
}
export interface WrongAnswerRow {
  session_id: string; subject: string; section: string | null; is_correct: boolean
}

/** A result (what the cabinet reads) rebuilt from cloud rows; `answers` are the wrong ones only. */
export function resultFromCloud(row: SessionRow, subjectRows: SubjectRow[], answerRows: WrongAnswerRow[]): SessionResult {
  const weak: Record<string, Record<string, number>> = {}
  for (const a of answerRows) {
    if (a.is_correct) continue
    const per = (weak[a.subject] ??= {})
    const sec = a.section || 'Загальне'
    per[sec] = (per[sec] ?? 0) + 1
  }
  const subjects: SubjectSummary[] = subjectRows.map((s) => {
    const cfg = SUBJECTS_CONFIG[s.subject]
    return {
      subject: s.subject,
      name: cfg?.name ?? s.subject,
      earned: s.earned ?? 0,
      actual_max: s.max_points ?? 0,
      projected_raw: s.projected_raw as number,
      official_max: cfg?.max_score as number,
      threshold: cfg?.threshold as number,
      nmt_200: s.nmt_200,
      is_full: !!s.is_full,
      drills_done: s.drills_done ?? 0,
      weak_sections: weak[s.subject] ?? {},
    }
  })
  const order = new Map((row.subjects ?? []).map((sid, i) => [sid, i]))
  subjects.sort((a, b) => (order.get(a.subject) ?? 99) - (order.get(b.subject) ?? 99))
  const finished = toLocalTime(row.finished_at || row.started_at)
  const result: SessionResult = {
    id: row.id,
    created_at: finished,
    finished_at: finished,
    started_at: toLocalTime(row.started_at),
    session_uid: row.id,
    length_mode: row.length_mode,
    tutor_mode: !!row.tutor_mode,
    mistake_drill: !!row.mistake_drill,
    subjects,
    answers: [],
    hints: [],
    from_cloud: true,
  }
  if (row.focus_section) result.focus_section = row.focus_section
  return result
}

/** Days in a row from the server's streak; 0 when it is broken (no training yesterday or today). */
export function currentStreak(meta: { streak?: { current?: number; last_day?: string } } | null | undefined, today: Date = new Date()): number {
  const streak = meta?.streak ?? {}
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(streak.last_day ?? '')
  if (!m) return 0
  const last = Date.UTC(+m[1], +m[2] - 1, +m[3])
  const yesterday = Date.UTC(today.getFullYear(), today.getMonth(), today.getDate() - 1)
  return last >= yesterday ? Math.trunc(streak.current ?? 0) : 0
}
