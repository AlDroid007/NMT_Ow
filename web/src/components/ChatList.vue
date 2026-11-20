<script setup lang="ts">
import type { ChatMessage } from '../stores/training'
defineProps<{ messages: ChatMessage[] }>()
</script>

<template>
  <div class="chat">
    <div v-for="(m, i) in messages" :key="i" class="bubble" :class="[m.who, m.tone]">
      <div class="who">{{ m.title }}</div>
      <div class="msg">{{ m.text }}</div>
    </div>
  </div>
</template>

<style scoped>
.bubble { border-radius: 15px; padding: 10px 12px; margin-bottom: 8px; border: 1px solid var(--nmt-border); background: var(--nmt-card-soft); }
.bubble.tutor { background: var(--nmt-soft-indigo); border-color: var(--nmt-soft-indigo-bd); }
.bubble.err { background: var(--nmt-soft-rose); border-color: var(--nmt-soft-rose-bd); }
.bubble.ok { background: var(--nmt-ok-bg); border-color: #86EFAC; }
.bubble.hint { background: var(--nmt-soft-amber); border-color: var(--nmt-soft-amber-bd); }
.bubble.rule { background: #EEF2FF; border-color: #A5B4FC; }
.who { font-weight: 700; font-size: 14px; color: var(--ion-color-primary); }
.student .who { color: #475569; }
.err .who { color: var(--nmt-err-fg); }
.msg { white-space: pre-wrap; font-size: 15px; line-height: 1.42; margin-top: 3px; }
.ok .msg { color: var(--nmt-ok-fg); }
.hint .msg { color: #78350F; }
</style>
