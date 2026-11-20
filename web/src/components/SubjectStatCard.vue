<script setup lang="ts">
import type { SubjectStats } from '../core/cabinet'
defineProps<{ stats: SubjectStats; selected?: boolean }>()
defineEmits<{ select: [string] }>()
</script>

<template>
  <button type="button" class="stat" :class="{ selected }" @click="$emit('select', stats.subject)">
    <div class="name">{{ stats.name }}</div>
    <template v-if="!stats.sessions">
      <div class="muted big-muted">Ще не тренувався(лась)</div>
      <div v-if="stats.target" class="muted small">Ціль: {{ stats.target }}</div>
    </template>
    <template v-else>
      <div class="row">
        <span class="big" :class="{ fail: stats.recent === null }">{{ stats.recent ?? '< поріг' }}</span>
        <span v-if="stats.target && stats.gap !== null && stats.gap <= 0" class="chip ok">🎯 ціль {{ stats.target }} досягнута</span>
        <span v-else-if="stats.target && stats.gap !== null" class="chip">до цілі {{ stats.target }}: ще {{ stats.gap }}</span>
        <span v-else-if="stats.target" class="chip">ціль {{ stats.target }}</span>
      </div>
      <div class="row small">
        <span class="muted">рівень • тренувань: {{ stats.sessions }}</span>
        <span v-if="stats.trend" :class="stats.trend > 0 ? 'up' : 'down'">{{ stats.trend > 0 ? '▲' : '▼' }} {{ Math.abs(stats.trend) }} за останні</span>
      </div>
      <div class="muted small">
        {{ [stats.best !== null ? `найкращий ${stats.best}` : '', stats.accuracy !== null ? `правильних ${stats.accuracy}%` : ''].filter(Boolean).join(' • ') }}
      </div>
    </template>
  </button>
</template>

<style scoped>
.stat {
  text-align: left; width: 100%; background: var(--nmt-card-soft); border: 1px solid var(--nmt-border);
  border-radius: 16px; padding: 12px 14px; font: inherit; color: inherit; cursor: pointer; min-height: 112px;
}
.stat.selected { border: 2px solid var(--ion-color-primary); padding: 11px 13px; }
.name { font-weight: 700; font-size: 16px; }
.row { display: flex; justify-content: space-between; align-items: center; gap: 8px; margin-top: 4px; }
.big { font-size: 26px; font-weight: 800; }
.big.fail { color: var(--nmt-err-fg); font-size: 20px; }
.big-muted { margin-top: 14px; }
.chip { font-size: 11px; font-weight: 700; padding: 3px 9px; border-radius: 11px; background: var(--nmt-soft-amber); color: #92400E; }
.chip.ok { background: var(--nmt-ok-bg); color: var(--nmt-ok-fg); }
.small { font-size: 12.5px; }
.muted { color: var(--nmt-muted); }
.up { color: var(--nmt-ok-fg); }
.down { color: var(--nmt-err-fg); }
</style>
