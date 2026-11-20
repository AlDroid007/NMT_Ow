import { describe, expect, it } from 'vitest'
import { APP_TITLE, SUPABASE_URL } from '../src/config'

describe('config', () => {
  it('points to the Supabase project', () => {
    expect(APP_TITLE).toContain('НМТ')
    expect(SUPABASE_URL).toMatch(/^https:\/\/.+\.supabase\.co$/)
  })
})
