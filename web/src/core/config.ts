// NMT subjects, official task counts and the 100–200 conversion scales (port of nmt_tutor/config.py).
// The numbers live in data/subjects.json, exported once from the desktop app.

import subjects from './data/subjects.json'
import bankJson from './data/bank.json'
import { pyRound } from './py'
import type { SubjectConfig, Task } from './types'

export const SUBJECTS_ORDER: string[] = subjects.order
export const SUBJECTS_CONFIG: Record<string, SubjectConfig> = subjects.config as Record<string, SubjectConfig>
const CONVERSION_TABLES: Record<string, Record<string, number>> = subjects.conversion
/** subject -> generator keys (drill_key), in the desktop order */
export const SUBJECT_GENERATORS: Record<string, string[]> = subjects.generators

/** Built-in task bank {subject: [task]}: official 2026 samples first, then the 2022–2025 archive. */
export const BANK: Record<string, Task[]> = bankJson as unknown as Record<string, Task[]>

export function bankSize(): number {
  return Object.values(BANK).reduce((n, tasks) => n + tasks.length, 0)
}

/** Test score -> NMT 100–200, or null below the threshold. */
export function scoreToNmt200(subjectId: string, rawScore: number): number | null {
  const cfg = SUBJECTS_CONFIG[subjectId]
  if (rawScore < cfg.threshold) return null
  const clamped = Math.min(pyRound(rawScore), cfg.max_score)
  return CONVERSION_TABLES[subjectId][String(clamped)] ?? null
}

/** The whole scale of a subject (for the «Програми та шкала 100–200» screen). */
export function conversionTable(subjectId: string): Array<[number, number]> {
  return Object.entries(CONVERSION_TABLES[subjectId]).map(([raw, nmt]) => [Number(raw), nmt])
}
