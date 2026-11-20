<script setup lang="ts">
// NMT score (100–200) per training, goal as a dashed line (desktop: ProgressChart canvas).
import { computed } from 'vue'
import { formatWhen, type ProgressPoint } from '../core/cabinet'

const props = defineProps<{ points: ProgressPoint[]; target?: number | null }>()
const W = 640
const H = 250
const L = 44
const R = 24
const T = 18
const B = 34
const y = (score: number) => H - B - ((score - 100) / 100) * (H - B - T)

const xs = computed(() => {
  const n = props.points.length
  const span = W - R - L - 20
  return props.points.map((_, i) => L + 10 + (n > 1 ? (span * i) / (n - 1) : span / 2))
})
const line = computed(() =>
  props.points.map((p, i) => (p.nmt_200 !== null ? `${xs.value[i]},${y(p.nmt_200)}` : null)).filter(Boolean).join(' '),
)
const labels = computed(() => {
  const n = props.points.length
  const step = Math.max(1, Math.floor(n / ((W - L - R) / 70)) + (n > 1 ? 1 : 0))
  const out: Array<{ x: number; text: string }> = []
  for (let i = 0; i < n; i += step) out.push({ x: xs.value[i], text: formatWhen(props.points[i].at).slice(0, 5) })
  return out
})
const last = computed(() => props.points[props.points.length - 1])
const anyFailed = computed(() => props.points.some((p) => p.nmt_200 === null))
const r = computed(() => (props.points.length <= 30 ? 5 : 3))
</script>

<template>
  <svg :viewBox="`0 0 ${W} ${H}`" class="chart" role="img" aria-label="Графік балів НМТ">
    <g v-for="s in [100, 125, 150, 175, 200]" :key="s">
      <line :x1="L" :x2="W - R" :y1="y(s)" :y2="y(s)" stroke="#E8ECF7" />
      <text :x="L - 8" :y="y(s) + 4" text-anchor="end" class="axis">{{ s }}</text>
    </g>
    <text v-if="!points.length" :x="(L + W - R) / 2" :y="(T + H - B) / 2" text-anchor="middle" class="empty">Ще немає тренувань із цього предмета</text>
    <template v-else>
      <g v-if="target">
        <line :x1="L" :x2="W - R" :y1="y(target)" :y2="y(target)" stroke="#22A094" stroke-width="2" stroke-dasharray="6 4" />
        <text :x="W - R" :y="y(target) - 6" text-anchor="end" class="goal">ціль {{ target }}</text>
      </g>
      <polyline v-if="line.split(' ').length >= 2" :points="line" fill="none" stroke="#5B6EF5" stroke-width="3" stroke-linejoin="round" stroke-linecap="round" />
      <template v-for="(p, i) in points" :key="i">
        <circle v-if="p.nmt_200 === null" :cx="xs[i]" :cy="y(100)" :r="r" fill="#fff" stroke="#B91C1C" stroke-width="2" />
        <circle v-else :cx="xs[i]" :cy="y(p.nmt_200)" :r="r" fill="#5B6EF5" stroke="#fff" stroke-width="2" />
      </template>
      <text v-if="last.nmt_200 !== null" :x="xs[xs.length - 1]" :y="y(last.nmt_200) - 11" text-anchor="middle" class="last">{{ last.nmt_200 }}</text>
      <text v-for="(l, i) in labels" :key="'l' + i" :x="l.x" :y="H - B + 18" text-anchor="middle" class="axis">{{ l.text }}</text>
      <text v-if="anyFailed" :x="L + 6" :y="T + 10" class="fail">○ — нижче порогу «склав»</text>
    </template>
  </svg>
</template>

<style scoped>
.chart { width: 100%; height: auto; display: block; }
.axis { font-size: 12px; fill: var(--nmt-muted); }
.empty { font-size: 15px; fill: var(--nmt-muted); }
.goal { font-size: 13px; font-weight: 700; fill: #22A094; }
.last { font-size: 13px; font-weight: 700; fill: #5B6EF5; }
.fail { font-size: 12px; fill: #B91C1C; }
</style>
