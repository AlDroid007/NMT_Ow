<script setup lang="ts">
// The 1–10 hint scale under the owl: opened levels are filled; any level can be (re)opened.
defineProps<{ level: number; disabled?: boolean }>()
const emit = defineEmits<{ select: [number] }>()
</script>

<template>
  <div class="stepper" :class="{ disabled }">
    <span class="cap">Підказки:</span>
    <button
      v-for="n in 10" :key="n" type="button" :class="{ open: n <= level, next: n === level + 1 }"
      :disabled="disabled" :aria-label="`Підказка ${n} з 10`" @click="emit('select', n)"
    >{{ n }}</button>
  </div>
</template>

<style scoped>
.stepper { display: flex; align-items: center; gap: 4px; flex-wrap: wrap; background: var(--nmt-card-soft); border-radius: 14px; padding: 6px 8px; }
.cap { font-size: 13px; color: var(--nmt-muted); margin-right: 4px; }
button {
  width: 28px; height: 28px; border-radius: 50%; border: 1px solid var(--nmt-soft-amber-bd);
  background: #fff; color: #92400E; font-weight: 700; font-size: 13px; cursor: pointer; padding: 0;
}
button.open { background: #F59E0B; color: #fff; border-color: #F59E0B; }
button.next { box-shadow: 0 0 0 2px #FDE68A; }
.disabled button { opacity: .45; cursor: default; }
</style>
