// Small helpers that reproduce Python behaviour the desktop code relied on, so the TypeScript port
// gives the same numbers and texts (rounding, float printing, random choices, string length).

// --- random -------------------------------------------------------------------------------

let source: () => number = Math.random

/** Replaces the random source (tests use a seeded one); returns the previous one. */
export function setRandom(fn: () => number): () => number {
  const prev = source
  source = fn
  return prev
}

/** Deterministic PRNG (mulberry32) for reproducible tests. */
export function seededRandom(seed: number): () => number {
  let a = seed >>> 0
  return () => {
    a = (a + 0x6d2b79f5) >>> 0
    let t = a
    t = Math.imul(t ^ (t >>> 15), t | 1)
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61)
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}

export function random(): number {
  return source()
}

/** random.randint(a, b): integer in [a, b]. */
export function randint(a: number, b: number): number {
  return a + Math.floor(source() * (b - a + 1))
}

/** random.choice(seq). */
export function choice<T>(items: readonly T[]): T {
  if (!items.length) throw new Error('choice from an empty list')
  return items[Math.floor(source() * items.length)]
}

/** random.shuffle(list) in place. */
export function shuffle<T>(items: T[]): T[] {
  for (let i = items.length - 1; i > 0; i--) {
    const j = Math.floor(source() * (i + 1))
    ;[items[i], items[j]] = [items[j], items[i]]
  }
  return items
}

/** random.sample(seq, k). */
export function sample<T>(items: readonly T[], k: number): T[] {
  return shuffle([...items]).slice(0, k)
}

// --- numbers ------------------------------------------------------------------------------

/** Python round(x) (no digits): nearest integer, ties to even. */
export function pyRound(x: number): number {
  const floor = Math.floor(x)
  const diff = x - floor
  if (diff > 0.5) return floor + 1
  if (diff < 0.5) return floor
  return floor % 2 === 0 ? floor : floor + 1
}

/** Python round(x, ndigits) for floats: decimal rounding of the exact binary value, ties to even. */
export function pyRoundTo(x: number, ndigits: number): number {
  if (!isFinite(x)) return x
  if (ndigits < 0) {
    const f = 10 ** -ndigits
    return pyRound(x / f) * f
  }
  const away = Number(x.toFixed(ndigits)) // exact value, but ties go away from zero
  // toFixed(100) prints the exact binary value; a true tie is "…d5000…" right after the kept digits.
  const full = Math.abs(x).toFixed(100)
  const point = full.indexOf('.')
  const rest = full.slice(point + 1 + ndigits)
  if (rest[0] !== '5' || /[^0]/.test(rest.slice(1))) return away
  const kept = full.slice(0, point + 1 + ndigits).replace(/\.$/, '')
  const lastDigit = Number(kept[kept.length - 1])
  if (lastDigit % 2 === 0) return (x < 0 ? -1 : 1) * Number(kept)
  return away
}

/** str(float) in Python: always shows a fractional part ("30.0"), exponent for tiny/huge values. */
export function pyFloatStr(x: number): string {
  if (Number.isInteger(x) && Math.abs(x) < 1e16) return x.toFixed(1)
  const abs = Math.abs(x)
  if (abs !== 0 && (abs < 1e-4 || abs >= 1e16)) {
    const [m, e] = x.toExponential().split('e')
    const exp = Number(e)
    const sign = exp < 0 ? '-' : '+'
    return `${m}e${sign}${String(Math.abs(exp)).padStart(2, '0')}`
  }
  return String(x)
}

/** f"{n:+d}". */
export function signed(n: number): string {
  return n >= 0 ? `+${n}` : String(n)
}

/** Python floor division a // b for integers. */
export function floorDiv(a: number, b: number): number {
  return Math.floor(a / b)
}

/** Python a % b (result has the sign of b). */
export function pyMod(a: number, b: number): number {
  return ((a % b) + b) % b
}

/** Python float(text): accepts what Python accepts for plain decimal numbers, else null. */
export function pyFloat(text: string): number | null {
  const t = text.trim().replace(/_/g, '')
  if (!/^[+-]?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?$/.test(t) && !/^[+-]?(inf|infinity|nan)$/i.test(t)) return null
  const v = Number(t.replace(/^([+-]?)inf(inity)?$/i, '$1Infinity'))
  return Number.isNaN(v) && !/nan/i.test(t) ? null : v
}

// --- strings (Python counts code points, JS counts UTF-16 units) --------------------------------

export function pyLen(s: string): number {
  return Array.from(s).length
}

export function pySlice(s: string, start: number, end?: number): string {
  return Array.from(s).slice(start, end).join('')
}

/** str.split() + " ".join(): collapses all whitespace. */
export function collapseSpaces(s: string): string {
  return s.split(/\s+/).filter(Boolean).join(' ')
}

/** str.rstrip(chars). */
export function rstripChars(s: string, chars: string): string {
  let end = s.length
  while (end > 0 && chars.includes(s[end - 1])) end--
  return s.slice(0, end)
}

/** sorted() of strings (by code point, like Python). */
export function sortedStrings(items: Iterable<string>): string[] {
  return [...items].sort((a, b) => (a < b ? -1 : a > b ? 1 : 0))
}

/** Python truthiness for JSON-like values. */
export function truthy(v: unknown): boolean {
  if (v === null || v === undefined || v === false || v === 0 || v === '') return false
  if (Array.isArray(v)) return v.length > 0
  if (typeof v === 'object') return Object.keys(v as object).length > 0
  return true
}

/** str(value) the way Python prints JSON-like scalars. */
export function pyStr(v: unknown): string {
  if (v === null || v === undefined) return 'None'
  if (v === true) return 'True'
  if (v === false) return 'False'
  return String(v)
}
