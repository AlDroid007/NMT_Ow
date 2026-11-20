// Closed access to the web app: a login and a password from public.app_gate_logins, checked before
// any other screen (like a Grails interceptor). The database compares the bcrypt hash and hands out a
// device token; the browser keeps only that token and checks it again on every start, so turning a
// login off in the dashboard lets its devices out.

import { ACCESS_GATE } from '../config'
import { supabase } from './client'

export const GATE_TOKEN_KEY = 'nmt-sova-gate'

type Rpc = (fn: string, args: Record<string, unknown>) => PromiseLike<{ data: unknown; error: unknown }>

const defaultRpc: Rpc = (fn, args) => supabase().rpc(fn, args)

function readToken(): string | null {
  try {
    return localStorage.getItem(GATE_TOKEN_KEY)
  } catch {
    return null
  }
}

function writeToken(token: string | null) {
  try {
    if (token) localStorage.setItem(GATE_TOKEN_KEY, token)
    else localStorage.removeItem(GATE_TOKEN_KEY)
  } catch {
    /* private mode: the gate asks again next time */
  }
}

export class GateError extends Error {}

/** Login + password -> true and the token is kept; false when they are wrong. */
export async function gateSignIn(login: string, password: string, rpc: Rpc = defaultRpc): Promise<boolean> {
  const { data, error } = await rpc('gate_sign_in', { p_login: login.trim(), p_password: password })
  if (error) {
    const msg = String((error as { message?: string }).message ?? error)
    if (msg.includes('too many attempts')) throw new GateError('Забагато невдалих спроб. Спробуй через 15 хвилин.')
    if (msg.includes('gate_sign_in')) throw new GateError('Вхід ще не налаштований у хмарі (немає функції gate_sign_in).')
    throw error
  }
  if (typeof data !== 'string' || !data) return false
  writeToken(data)
  return true
}

/**
 * Is this device let in? No token -> no. A token the database refuses -> no, and it is forgotten.
 * The database cannot be reached -> yes if a token is kept (the trainings need the cloud anyway).
 */
export async function gateCheck(rpc: Rpc = defaultRpc): Promise<boolean> {
  if (!ACCESS_GATE) return true
  const token = readToken()
  if (!token) return false
  let ok: boolean
  try {
    const { data, error } = await rpc('gate_check', { p_token: token })
    if (error && isNetworkError(error)) return true
    ok = !error && data === true
  } catch (e) {
    if (isNetworkError(e)) return true
    ok = false
  }
  if (!ok) writeToken(null)
  return ok
}

function isNetworkError(err: unknown): boolean {
  const msg = String((err as { message?: string })?.message ?? err ?? '').toLowerCase()
  return msg.includes('failed to fetch') || msg.includes('network') || msg.includes('load failed')
}

export function gateForget() {
  writeToken(null)
}
