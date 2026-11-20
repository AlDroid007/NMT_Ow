// User profile model, no UI and no storage (port of the parts of nmt_tutor/profiles.py the web needs).
// On the web one cloud account = one profile; local profiles and PINs stay desktop-only.

import { SUBJECTS_CONFIG, SUBJECTS_ORDER } from './config'
import { collapseSpaces, pyLen, pySlice } from './py'

export const AVATARS = ['🦉', '🦊', '🐼', '🐱', '🐶', '🐯', '🦁', '🐸', '🐨', '🐰', '🦄', '🐙', '🐝', '🚀', '⭐', '🎧', '📚', '⚽']
export const DEFAULT_AVATAR = AVATARS[0]
export const DEFAULT_SUBJECTS = ['ukrmova', 'math', 'history', 'english']
export const NAME_MAX = 40
export const SCORE_MIN = 100
export const SCORE_MAX = 200
export const DEFAULT_TARGET = 170

export interface Avatar {
  kind: 'emoji' | 'url'
  value: string
}

export interface Profile {
  id: string
  name: string
  avatar: Avatar
  subjects: string[]
  targets: Record<string, number>
  exam_date: string | null
  identities?: Array<{ provider: string; subject: string; email: string | null }>
  created_at?: string
  updated_at?: string
  [key: string]: unknown
}

/** Invalid profile data; the message is shown to the user (Ukrainian). */
export class ProfileError extends Error {}

const pad = (n: number) => String(n).padStart(2, '0')

function validDate(y: number, m: number, d: number): boolean {
  const dt = new Date(Date.UTC(y, m - 1, d))
  return dt.getUTCFullYear() === y && dt.getUTCMonth() === m - 1 && dt.getUTCDate() === d
}

/** Accepts 'ДД.ММ.РРРР' or 'РРРР-ММ-ДД' (or empty); returns ISO 'YYYY-MM-DD' or null. */
export function parseExamDate(text: string | null | undefined): string | null {
  const t = (text ?? '').trim()
  if (!t) return null
  const patterns: Array<[RegExp, (m: RegExpMatchArray) => [number, number, number]]> = [
    [/^(\d{1,2})\.(\d{1,2})\.(\d{4})$/, (m) => [+m[3], +m[2], +m[1]]],
    [/^(\d{4})-(\d{1,2})-(\d{1,2})$/, (m) => [+m[1], +m[2], +m[3]]],
    [/^(\d{1,2})\/(\d{1,2})\/(\d{4})$/, (m) => [+m[3], +m[2], +m[1]]],
    [/^(\d{1,2})-(\d{1,2})-(\d{4})$/, (m) => [+m[3], +m[2], +m[1]]],
  ]
  for (const [re, parts] of patterns) {
    const m = t.match(re)
    if (!m) continue
    const [y, mo, d] = parts(m)
    if (validDate(y, mo, d)) return `${String(y).padStart(4, '0')}-${pad(mo)}-${pad(d)}`
  }
  throw new ProfileError('Дату НМТ введіть у форматі ДД.ММ.РРРР, наприклад 20.05.2027.')
}

function isoParts(iso: string): [number, number, number] | null {
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso)
  if (!m || !validDate(+m[1], +m[2], +m[3])) return null
  return [+m[1], +m[2], +m[3]]
}

export function formatExamDate(iso: string | null | undefined): string {
  if (!iso) return ''
  const p = isoParts(iso)
  return p ? `${pad(p[2])}.${pad(p[1])}.${p[0]}` : ''
}

/** Validates and cleans a profile in place (throws ProfileError); returns it. */
export function normalizeProfile<P extends Partial<Profile>>(profile: P): P & Profile {
  const name = collapseSpaces(String(profile.name || ''))
  if (!name) throw new ProfileError('Введіть ім’я.')
  if (pyLen(name) > NAME_MAX) throw new ProfileError(`Ім’я задовге (до ${NAME_MAX} символів).`)
  profile.name = name

  let avatar = (profile.avatar || {}) as Partial<Avatar>
  if ((avatar.kind !== 'emoji' && avatar.kind !== 'url') || !avatar.value) avatar = { kind: 'emoji', value: DEFAULT_AVATAR }
  profile.avatar = { kind: avatar.kind!, value: String(avatar.value) }

  const chosen = new Set(profile.subjects || [])
  profile.subjects = SUBJECTS_ORDER.filter((s) => chosen.has(s))

  const targets: Record<string, number> = {}
  for (const [sid, raw] of Object.entries(profile.targets || {})) {
    if (!(sid in SUBJECTS_CONFIG)) continue
    const txt = String(raw).trim()
    if (!/^[+-]?\d+$/.test(txt) && typeof raw !== 'number')
      throw new ProfileError(`Ціль для «${SUBJECTS_CONFIG[sid].name}» має бути числом від 100 до 200.`)
    const score = Math.trunc(Number(raw))
    if (!(SCORE_MIN <= score && score <= SCORE_MAX))
      throw new ProfileError(`Ціль для «${SUBJECTS_CONFIG[sid].name}» має бути від 100 до 200.`)
    targets[sid] = score
  }
  profile.targets = targets

  profile.exam_date = profile.exam_date ? parseExamDate(profile.exam_date) : null
  return profile as P & Profile
}

/** Emoji to draw for the profile (image avatars fall back to the first letter). */
export function avatarText(profile: Partial<Profile>): string {
  const av = profile.avatar
  if (av?.kind === 'emoji') return av.value || DEFAULT_AVATAR
  return pySlice(profile.name || '?', 0, 1).toUpperCase()
}

/** Name cut to `limit` characters with an ellipsis (for narrow buttons and tiles). */
export function shortName(name: string, limit: number): string {
  return pyLen(name) <= limit ? name : pySlice(name, 0, limit - 1).trimEnd() + '…'
}

/** Days left until the exam date (0 on the day, negative after it) or null. */
export function daysUntilExam(profile: Partial<Profile>, today: Date = new Date()): number | null {
  const iso = profile.exam_date
  if (!iso) return null
  const p = isoParts(iso)
  if (!p) return null
  const exam = Date.UTC(p[0], p[1] - 1, p[2])
  const now = Date.UTC(today.getFullYear(), today.getMonth(), today.getDate())
  return Math.round((exam - now) / 86400000)
}

/** Ukrainian plural of «день». */
export function daysWord(n: number): string {
  n = Math.abs(n)
  if (n % 10 === 1 && n % 100 !== 11) return 'день'
  if (n % 10 >= 2 && n % 10 <= 4 && !(n % 100 >= 12 && n % 100 <= 14)) return 'дні'
  return 'днів'
}

export function targetFor(profile: Partial<Profile> | null | undefined, subjectId: string): number | undefined {
  return (profile?.targets || {})[subjectId]
}
