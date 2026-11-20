// The Supabase client of the web app. The browser keeps the sign-in session (refresh tokens rotate).

import { createClient, type SupabaseClient } from '@supabase/supabase-js'
import { SUPABASE_KEY, SUPABASE_URL } from '../config'

let client: SupabaseClient | null = null

export function supabase(): SupabaseClient {
  if (!client) {
    client = createClient(SUPABASE_URL, SUPABASE_KEY, {
      auth: { persistSession: true, autoRefreshToken: true, detectSessionInUrl: false, storageKey: 'nmt-sova-auth' },
    })
  }
  return client
}

/** A message for the student (Ukrainian) from a Supabase / network error. */
export function errorText(err: unknown): string {
  const msg = String((err as { message?: string })?.message ?? err ?? '')
  const low = msg.toLowerCase()
  if (low.includes('failed to fetch') || low.includes('network') || low.includes('load failed'))
    return 'Немає з’єднання з інтернетом. Перевір мережу й спробуй ще раз.'
  if (low.includes('token has expired') || low.includes('invalid') && low.includes('otp'))
    return 'Код неправильний або застарів. Запроси новий код.'
  if (low.includes('rate limit') || low.includes('only request this after'))
    return 'Забагато спроб. Зачекай хвилину й спробуй ще раз.'
  if (low.includes('not signed in') || low.includes('jwt')) return 'Сесія завершилася. Увійди знову.'
  return msg || 'Невідома помилка хмари.'
}
