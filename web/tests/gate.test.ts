// @vitest-environment jsdom
import { beforeEach, describe, expect, it } from 'vitest'
import { GATE_TOKEN_KEY, GateError, gateCheck, gateSignIn } from '../src/cloud/gate'

type Reply = { data: unknown; error: unknown }
function rpc(reply: Reply | (() => never)) {
  const calls: [string, Record<string, unknown>][] = []
  const fn = async (name: string, args: Record<string, unknown>) => {
    calls.push([name, args])
    if (typeof reply === 'function') return reply()
    return reply
  }
  return Object.assign(fn, { calls })
}

const TOKEN = '6b0f0e3c-1111-4222-8333-444455556666'

describe('access gate', () => {
  beforeEach(() => localStorage.clear())

  it('keeps the token after the right login and password', async () => {
    const r = rpc({ data: TOKEN, error: null })
    expect(await gateSignIn(' tester ', 'secret123', r)).toBe(true)
    expect(r.calls[0]).toEqual(['gate_sign_in', { p_login: 'tester', p_password: 'secret123' }])
    expect(localStorage.getItem(GATE_TOKEN_KEY)).toBe(TOKEN)
  })

  it('refuses a wrong password without keeping anything', async () => {
    expect(await gateSignIn('tester', 'nope', rpc({ data: null, error: null }))).toBe(false)
    expect(localStorage.getItem(GATE_TOKEN_KEY)).toBeNull()
  })

  it('explains the lock after too many attempts', async () => {
    const r = rpc({ data: null, error: { message: 'too many attempts', code: 'P0001' } })
    await expect(gateSignIn('tester', 'x', r)).rejects.toBeInstanceOf(GateError)
  })

  it('without a token the gate is closed and the cloud is not asked', async () => {
    const r = rpc({ data: true, error: null })
    expect(await gateCheck(r)).toBe(false)
    expect(r.calls).toHaveLength(0)
  })

  it('a valid token opens the gate', async () => {
    localStorage.setItem(GATE_TOKEN_KEY, TOKEN)
    const r = rpc({ data: true, error: null })
    expect(await gateCheck(r)).toBe(true)
    expect(r.calls[0]).toEqual(['gate_check', { p_token: TOKEN }])
  })

  it('a refused token (login turned off) is forgotten', async () => {
    localStorage.setItem(GATE_TOKEN_KEY, TOKEN)
    expect(await gateCheck(rpc({ data: false, error: null }))).toBe(false)
    expect(localStorage.getItem(GATE_TOKEN_KEY)).toBeNull()
  })

  it('a broken token (database error) is refused and forgotten', async () => {
    localStorage.setItem(GATE_TOKEN_KEY, 'not-a-uuid')
    expect(await gateCheck(rpc({ data: null, error: { message: 'invalid input syntax for type uuid', code: '22P02' } }))).toBe(false)
    expect(localStorage.getItem(GATE_TOKEN_KEY)).toBeNull()
  })

  it('offline with a kept token: still let in', async () => {
    localStorage.setItem(GATE_TOKEN_KEY, TOKEN)
    expect(await gateCheck(rpc({ data: null, error: { message: 'TypeError: Failed to fetch' } }))).toBe(true)
    expect(await gateCheck(rpc(() => { throw new TypeError('Load failed') }))).toBe(true)
    expect(localStorage.getItem(GATE_TOKEN_KEY)).toBe(TOKEN)
  })
})
