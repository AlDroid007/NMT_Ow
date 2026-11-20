// Conversions between app records and cloud rows (no network).

import { describe, expect, it } from 'vitest'
import { currentStreak, resultFromCloud, sessionPayload, toCloudTime, toLocalTime } from '../src/cloud/convert'
import { nowIso } from '../src/core/engine'
import type { SessionResult } from '../src/core/types'

describe('times', () => {
  it('round-trips local time through the cloud', () => {
    const local = '2026-11-20T18:31:05'
    expect(toLocalTime(toCloudTime(local))).toBe(local)
    expect(toLocalTime('2026-11-20 16:31:05.123456+00')).toBe(nowIso(new Date(Date.UTC(2026, 10, 20, 16, 31, 5))))
  })
})

describe('sessionPayload', () => {
  const result: SessionResult = {
    finished_at: '2026-11-20T18:40:00', started_at: '2026-11-20T18:30:00', length_mode: 'weird', tutor_mode: false,
    mistake_drill: false,
    subjects: [{ subject: 'math', name: 'Математика', earned: 5, actual_max: 10, projected_raw: 16, official_max: 32, threshold: 5,
      nmt_200: 150, is_full: false, drills_done: 1, weak_sections: { 'Функції': 2 } }],
    answers: [{ subject: 'math', question_no: 0, task_id: 'gen:math_ineq', section: 'Функції', qtype: 'single', is_correct: false,
      points: 0, max_points: 1, checked: true, max_hint_level: 3, answered_at: 'not a date' }],
    hints: [],
  }
  it('builds the submit_session argument', () => {
    const p = sessionPayload(result, 'sid', 'pid')
    expect(p.length_mode).toBe('quick')
    expect(p.tutor_mode).toBe(false)
    expect(p.subjects[0]).toEqual({ subject: 'math', earned: 5, max_points: 10, projected_raw: 16, nmt_200: 150, is_full: false, drills_done: 1 })
    expect(p.answers[0].answered_at).toBe(p.finished_at)
    expect(p.started_at).toBe(toCloudTime('2026-11-20T18:30:00'))
  })
})

describe('resultFromCloud', () => {
  it('rebuilds weak topics and keeps the subject order', () => {
    const r = resultFromCloud(
      { id: 'u1', started_at: '2026-11-20T10:00:00Z', finished_at: '2026-11-20T10:20:00Z', length_mode: 'focus', tutor_mode: true,
        mistake_drill: false, focus_section: 'Функції', subjects: ['math', 'ukrmova'] },
      [
        { session_id: 'u1', subject: 'ukrmova', earned: 3, max_points: 8, projected_raw: 17, nmt_200: 140, is_full: false, drills_done: 0 },
        { session_id: 'u1', subject: 'math', earned: 6, max_points: 8, projected_raw: 24, nmt_200: 170, is_full: false, drills_done: 2 },
      ],
      [
        { session_id: 'u1', subject: 'math', section: 'Функції', is_correct: false },
        { session_id: 'u1', subject: 'math', section: null, is_correct: false },
        { session_id: 'u1', subject: 'ukrmova', section: 'Орфографія', is_correct: false },
      ],
    )
    expect(r.subjects.map((s) => s.subject)).toEqual(['math', 'ukrmova'])
    expect(r.subjects[0].weak_sections).toEqual({ 'Функції': 1, 'Загальне': 1 })
    expect(r.subjects[0].official_max).toBe(32)
    expect(r.focus_section).toBe('Функції')
    expect(r.created_at).toBe(toLocalTime('2026-11-20T10:20:00Z'))
  })
})

describe('streak', () => {
  const today = new Date(2026, 10, 20)
  it('counts only when the last training was today or yesterday', () => {
    expect(currentStreak({ streak: { current: 4, last_day: '2026-11-20' } }, today)).toBe(4)
    expect(currentStreak({ streak: { current: 4, last_day: '2026-11-19' } }, today)).toBe(4)
    expect(currentStreak({ streak: { current: 4, last_day: '2026-11-18' } }, today)).toBe(0)
    expect(currentStreak(null, today)).toBe(0)
  })
})
