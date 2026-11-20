/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_SUPABASE_URL?: string
  readonly VITE_SUPABASE_KEY?: string
  readonly VITE_ACCESS_GATE?: string
}
interface ImportMeta {
  readonly env: ImportMetaEnv
}
