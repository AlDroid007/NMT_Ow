// Shared helpers and the registry of "identical example" generators (port of generators/_common.py).

import { choice, pyRoundTo } from '../py'
import type { Task } from '../types'

export const GEN_SOURCE = 'Генератор за програмою НМТ (2022–2026)'

export type Generator = () => Task

/** drill_key -> generator */
export const REGISTRY: Record<string, Generator> = {}

export function registerDrill(key: string, fn: Generator): Generator {
  REGISTRY[key] = fn
  return fn
}

export function gcd(a: number, b: number): number {
  while (b) [a, b] = [b, a % b]
  return Math.abs(a)
}

/** Integer as "12", otherwise up to 4 decimals with a comma: "2,5". */
export function fmtNum(val: number): string {
  if (Math.abs(val - Math.round(val)) < 1e-9) return String(Math.round(val))
  const s = pyRoundTo(val, 4).toFixed(4).replace(/0+$/, '').replace(/\.$/, '')
  return s.replace('.', ',')
}

/** f"{x:.2f}" */
export function fixed2(x: number): string {
  return pyRoundTo(x, 2).toFixed(2)
}

export type Case = [sentence: string, options: string[], answer: string, hint: string, rule: string, solution: string]

/** A generator that picks one prepared A–D case. */
export function caseTableGenerator(key: string, subject: string, section: string, promptHead: string, cases: Case[]): Generator {
  return registerDrill(key, () => {
    const c = choice(cases)
    return {
      subject,
      section,
      source: GEN_SOURCE,
      qtype: 'single',
      max_points: 1,
      prompt: promptHead + c[0],
      options: [...c[1]],
      labels: ['A', 'B', 'C', 'D'],
      answer: c[2],
      hint: c[3],
      rule: c[4],
      solution: c[5],
      drill_key: key,
    }
  })
}

export const LABELS5 = ['А', 'Б', 'В', 'Г', 'Д']
export const LABELS4 = ['А', 'Б', 'В', 'Г']

/** sorted(set(values)) for numbers */
export function sortedUnique(values: number[]): number[] {
  return [...new Set(values)].sort((a, b) => a - b)
}
