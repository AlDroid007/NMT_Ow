// Shapes shared by the core modules (same JSON as the Python desktop app and the cloud).

export type QType = 'single' | 'short' | 'matching' | 'sequence' | 'multi3'

export interface Task {
  id?: string
  bank_id?: string
  subject?: string
  section?: string
  source?: string
  qtype: QType | string
  max_points?: number
  prompt?: string
  options?: string[]
  labels?: string[]
  /** single/short/sequence: string; matching: {"1": "А", …}; multi3: ["1", "4", "6"] */
  answer?: unknown
  left?: string[]
  right?: Record<string, string>
  items?: Record<string, string>
  hint?: string
  rule?: string
  solution?: string
  drill_key?: string
  hints_10?: string[]
  is_drill?: boolean
  [key: string]: unknown
}

/** What the student entered: a label, typed text, {"1": "А"} for matching, ["1","3"] for multi3. */
export type StudentAnswer = string | string[] | Record<string, string>

export interface AnswerRecord {
  subject: string
  question_no: number
  task_id: string | undefined
  section: string
  qtype: string | undefined
  is_correct: boolean
  points: number
  max_points: number
  checked: boolean
  max_hint_level: number
  answered_at: string
}

export interface HintRecord {
  subject: string
  question_no: number
  task_id: string | undefined
  level: number
  opened_at: string
}

export interface Block {
  subject: string
  questions: Task[]
  answers: Record<number, StudentAnswer>
  points: Record<number, number>
  mistakes: number[]
  drills_done: number
  answer_log: Record<number, AnswerRecord>
  hint_log: HintRecord[]
}

export type Plan = Block[]

export interface SubjectSummary {
  subject: string
  name: string
  earned: number
  actual_max: number
  projected_raw: number
  official_max: number
  threshold: number
  nmt_200: number | null
  is_full: boolean
  drills_done: number
  weak_sections: Record<string, number>
}

export type LengthMode = 'quick' | 'medium' | 'full' | 'focus'

/** A finished session as the cabinet reads it (desktop: Repository.list_results()). */
export interface SessionResult {
  id?: string | number
  created_at?: string
  finished_at: string
  started_at?: string
  session_uid?: string
  length_mode: string
  tutor_mode: boolean
  mistake_drill: boolean
  focus_section?: string
  report_id?: string | number | null
  subjects: SubjectSummary[]
  answers: AnswerRecord[]
  hints: HintRecord[]
  from_cloud?: boolean
}

export interface SubjectConfig {
  name: string
  mandatory: boolean
  total_tasks: number
  max_score: number
  threshold: number
  minutes: number
  program_order: string
  structure: string
  sections: string[]
}
