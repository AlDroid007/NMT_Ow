// Everything the web app asks from the cloud (port of the network part of nmt_tutor/cloud/sync.py).
// The cloud is the only store on the web: no local database, only a small outbox for trainings
// finished while offline.

import type { Session } from '@supabase/supabase-js'
import { normalizeProfile, type Profile } from '../core/profiles'
import type { SessionResult } from '../core/types'
import { supabase } from './client'
import {
  currentStreak, LENGTH_MODES, resultFromCloud, sessionPayload, type CloudSessionPayload, type SessionRow,
  type SubjectRow, type WrongAnswerRow,
} from './convert'

const PAGE = 1000
const ID_CHUNK = 100

function check<T>(res: { data: T; error: unknown }): T {
  if (res.error) throw res.error
  return res.data
}

// --- sign-in with an e-mail code -------------------------------------------------------------

export async function sendCode(email: string): Promise<void> {
  check(await supabase().auth.signInWithOtp({ email: email.trim(), options: { shouldCreateUser: true } }))
}

export async function verifyCode(email: string, code: string): Promise<Session> {
  const data = check(await supabase().auth.verifyOtp({ email: email.trim(), token: code.trim(), type: 'email' }))
  if (!data.session) throw new Error('Не вдалося увійти.')
  return data.session
}

export async function currentSession(): Promise<Session | null> {
  const res = await supabase().auth.getSession()
  if (res.error) throw res.error
  return res.data.session
}

export async function signOut(): Promise<void> {
  await supabase().auth.signOut()
}

/** Deletes the account and everything in the cloud (server function), then signs out. */
export async function deleteAccount(): Promise<void> {
  check(await supabase().rpc('delete_my_account'))
  await supabase().auth.signOut({ scope: 'local' })
}

// --- profile ------------------------------------------------------------------------------------

type ProfileRow = {
  id: string; name: string; avatar: Profile['avatar']; subjects: string[]; targets: Record<string, number>
  exam_date: string | null; created_at: string; updated_at: string
}

function profileFromRow(row: ProfileRow): Profile {
  return normalizeProfile({
    id: row.id,
    name: row.name || 'Учень',
    avatar: row.avatar,
    subjects: row.subjects ?? [],
    targets: row.targets ?? {},
    exam_date: row.exam_date,
    created_at: row.created_at,
    updated_at: row.updated_at,
  })
}

/** The account's profile (the oldest one, like the desktop), or null for a new account. */
export async function fetchProfile(): Promise<Profile | null> {
  const s = await currentSession()
  if (!s) return null
  const rows = check(
    await supabase().from('profiles').select('*').eq('owner', s.user.id).order('created_at', { ascending: true }).limit(1),
  ) as ProfileRow[]
  return rows.length ? profileFromRow(rows[0]) : null
}

/** Creates or updates the profile; a new one gets a fresh id. */
export async function saveProfile(p: Partial<Profile>): Promise<Profile> {
  const clean = normalizeProfile({ ...p, id: p.id || crypto.randomUUID() })
  const row = {
    id: clean.id,
    name: clean.name,
    avatar: clean.avatar,
    subjects: clean.subjects,
    targets: clean.targets,
    exam_date: clean.exam_date,
  }
  const saved = check(await supabase().from('profiles').upsert(row).select('*').single()) as ProfileRow
  return profileFromRow(saved)
}

/** Server metadata of the profile (streak, later medals). */
export async function fetchMeta(profileId: string): Promise<Record<string, unknown> | null> {
  const rows = check(await supabase().from('profile_meta').select('data').eq('profile_id', profileId)) as Array<{ data: Record<string, unknown> }>
  return rows.length ? rows[0].data : null
}

export async function fetchStreak(profileId: string): Promise<number> {
  return currentStreak((await fetchMeta(profileId)) as Parameters<typeof currentStreak>[0])
}

// --- trainings ---------------------------------------------------------------------------------

export interface BeginOptions {
  sessionId: string
  profileId: string
  subjects: string[]
  lengthMode: string
  tutorMode: boolean
  mistakeDrill?: boolean
  focusSection?: string | null
}

/** Registers the start of a training on the server; without the internet a training does not start. */
export async function beginSession(o: BeginOptions): Promise<{ allowed: boolean; started_at?: string; [k: string]: unknown }> {
  const data = check(
    await supabase().rpc('begin_session', {
      p_session_id: o.sessionId,
      p_profile_id: o.profileId,
      p_subjects: o.subjects,
      p_length_mode: LENGTH_MODES.includes(o.lengthMode) ? o.lengthMode : 'quick',
      p_tutor_mode: !!o.tutorMode,
      p_mistake_drill: !!o.mistakeDrill,
      p_focus_section: o.focusSection ?? null,
    }),
  )
  return (data as { allowed: boolean }) ?? { allowed: true }
}

const OUTBOX_KEY = 'nmt-sova-outbox'

function readOutbox(): CloudSessionPayload[] {
  try {
    return JSON.parse(localStorage.getItem(OUTBOX_KEY) || '[]')
  } catch {
    return []
  }
}

function writeOutbox(items: CloudSessionPayload[]): void {
  try {
    if (items.length) localStorage.setItem(OUTBOX_KEY, JSON.stringify(items))
    else localStorage.removeItem(OUTBOX_KEY)
  } catch {
    /* private mode: nothing to keep */
  }
}

export function pendingCount(): number {
  return readOutbox().length
}

/**
 * Sends a finished training. If the network is down it waits in the outbox and goes up with the
 * next flushOutbox(); returns true when it reached the server now.
 */
export async function submitSession(result: SessionResult, sessionId: string, profileId: string): Promise<boolean> {
  const payload = sessionPayload(result, sessionId, profileId)
  writeOutbox([...readOutbox().filter((p) => p.id !== payload.id), payload])
  return (await flushOutbox()) === 0
}

/** Uploads trainings waiting in the outbox; returns how many are still waiting. */
export async function flushOutbox(): Promise<number> {
  let waiting = readOutbox()
  for (const p of [...waiting]) {
    const res = await supabase().rpc('submit_session', { p_session: p })
    if (res.error) {
      const msg = String(res.error.message || '')
      // The server refuses this one for good (e.g. a deleted profile): drop it instead of retrying forever.
      if (msg.includes('profile not found') || msg.includes('not allowed')) waiting = waiting.filter((x) => x.id !== p.id)
      else break
    } else {
      waiting = waiting.filter((x) => x.id !== p.id)
    }
    writeOutbox(waiting)
  }
  return waiting.length
}

async function selectAll<T>(build: (from: number, to: number) => PromiseLike<{ data: T[] | null; error: unknown }>): Promise<T[]> {
  const out: T[] = []
  for (let from = 0; ; from += PAGE) {
    const rows = check(await build(from, from + PAGE - 1)) ?? []
    out.push(...rows)
    if (rows.length < PAGE) return out
  }
}

/** All finished trainings of the profile, oldest first, in the form the cabinet reads. */
export async function fetchHistory(profileId: string): Promise<SessionResult[]> {
  const db = supabase()
  const sessions = await selectAll<SessionRow>((a, b) =>
    db.from('sessions').select('id,started_at,finished_at,length_mode,tutor_mode,mistake_drill,focus_section,subjects')
      .eq('profile_id', profileId).eq('status', 'finished')
      .order('finished_at', { ascending: true }).order('id', { ascending: true }).range(a, b),
  )
  const results: SessionResult[] = []
  for (let i = 0; i < sessions.length; i += ID_CHUNK) {
    const chunk = sessions.slice(i, i + ID_CHUNK)
    const ids = chunk.map((r) => r.id)
    const subj = await selectAll<SubjectRow>((a, b) =>
      db.from('session_subjects').select('session_id,subject,earned,max_points,projected_raw,nmt_200,is_full,drills_done')
        .in('session_id', ids).order('session_id').order('subject').range(a, b),
    )
    const wrong = await selectAll<WrongAnswerRow>((a, b) =>
      db.from('session_answers').select('session_id,subject,section,is_correct')
        .in('session_id', ids).eq('is_correct', false).order('session_id').order('subject').order('question_no').range(a, b),
    )
    for (const row of chunk) {
      results.push(resultFromCloud(row, subj.filter((s) => s.session_id === row.id), wrong.filter((w) => w.session_id === row.id)))
    }
  }
  return results
}
