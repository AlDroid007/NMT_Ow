// Registry of the "identical example" generators (port of generators/__init__.py).
// All subject modules are small, so they are loaded eagerly.

import { SUBJECT_GENERATORS } from '../config'
import { type Generator, REGISTRY } from './common'
import './ukrmova'
import './maths'
import './history'
import './languages'
import './ukrlit'
import './biology'
import './physics'
import './chemistry'
import './geography'

export { REGISTRY as DRILL_GENERATORS, registerDrill } from './common'

const KEY_TO_SUBJECT: Record<string, string> = {}
for (const [sid, keys] of Object.entries(SUBJECT_GENERATORS)) for (const k of keys) KEY_TO_SUBJECT[k] = sid

export function generatorCount(): number {
  return Object.keys(KEY_TO_SUBJECT).length
}

export function hasGenerator(key: string | undefined | null): boolean {
  return !!key && (key in REGISTRY || key in KEY_TO_SUBJECT)
}

export function getGenerator(key: string | undefined | null): Generator | undefined {
  return key ? REGISTRY[key] : undefined
}

export function generatorsForSubject(subjectId: string): string[] {
  return SUBJECT_GENERATORS[subjectId] ?? []
}
