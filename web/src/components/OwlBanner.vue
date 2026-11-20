<script setup lang="ts">
// Owl-Liza with a mood badge and a short line of text (desktop: OwlMascot + status label).
import type { Mood } from '../stores/training'

defineProps<{ title: string; text?: string; mood?: Mood; size?: number }>()
const BADGE: Record<Mood, string> = { idle: '', thinking: '🤔', happy: '🎉', explain: '💡' }
</script>

<template>
  <div class="owl-banner">
    <div class="owl" :style="{ width: (size ?? 72) + 'px', height: (size ?? 72) + 'px' }">
      <img src="/owl.png" alt="Сова-Ліза" :class="mood" />
      <span v-if="mood && BADGE[mood]" class="badge">{{ BADGE[mood] }}</span>
    </div>
    <div class="txt">
      <div class="title">{{ title }}</div>
      <div v-if="text" class="text">{{ text }}</div>
      <slot />
    </div>
  </div>
</template>

<style scoped>
.owl-banner {
  display: flex; gap: 12px; align-items: center;
  background: var(--nmt-soft-indigo); border: 1px solid var(--nmt-soft-indigo-bd);
  border-radius: 18px; padding: 10px 12px;
}
.owl { position: relative; flex: none; }
.owl img { width: 100%; height: 100%; object-fit: contain; transition: transform .25s; }
.owl img.happy { transform: translateY(-3px) rotate(-4deg); }
.owl img.thinking { transform: rotate(4deg); }
.badge { position: absolute; right: -4px; top: -4px; font-size: 20px; }
.title { font-weight: 700; color: #1E2B58; font-size: 16px; }
.text { color: #334155; font-size: 14px; margin-top: 3px; line-height: 1.35; }
</style>
