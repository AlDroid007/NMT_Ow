// Public settings of the web app. The Supabase key is the publishable one (safe in the browser;
// access is limited by row-level security in the database). Override with VITE_* variables.
export const SUPABASE_URL: string =
  import.meta.env.VITE_SUPABASE_URL || 'https://txfabcsvyvcaqpcqvhka.supabase.co'
export const SUPABASE_KEY: string =
  import.meta.env.VITE_SUPABASE_KEY || 'sb_publishable_prjskakkDNKqnHxWwtDfpw_B9KSrs5W'
export const PRIVACY_URL = 'https://aldroid007.github.io/NMT_Ow/privacy/'
export const APP_TITLE = 'НМТ Сова-Репетитор'
export const APP_VERSION = '4.0 (web)'
/** Closed access (login + password before everything). VITE_ACCESS_GATE=off turns it off for local work. */
export const ACCESS_GATE: boolean = (import.meta.env.VITE_ACCESS_GATE ?? 'on') !== 'off'
