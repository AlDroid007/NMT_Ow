<script setup lang="ts">
// The answer controls for a task: single choice, short number, matching, sequence, 3 of 7.
import { computed } from 'vue'
import type { StudentAnswer, Task } from '../core/types'

const props = defineProps<{ task: Task; modelValue: StudentAnswer | null; drill?: boolean; disabled?: boolean }>()
const emit = defineEmits<{ 'update:modelValue': [StudentAnswer] }>()

const labels = computed(() => props.task.labels ?? [])
const options = computed(() => props.task.options ?? [])
const right = computed(() => props.task.right ?? {})
const items = computed(() => props.task.items ?? {})

const single = computed(() => (typeof props.modelValue === 'string' ? props.modelValue : ''))
const matching = computed(() => (props.modelValue && typeof props.modelValue === 'object' && !Array.isArray(props.modelValue) ? props.modelValue : {}) as Record<string, string>)
const seq = computed(() => {
  const s = typeof props.modelValue === 'string' ? Array.from(props.modelValue) : []
  return [0, 1, 2, 3].map((i) => (s[i] && s[i] !== ' ' ? s[i] : ''))
})
const multi = computed(() => (Array.isArray(props.modelValue) ? props.modelValue : []) as string[])

function setMatch(k: string, v: string) {
  emit('update:modelValue', { ...matching.value, [k]: v })
}
function setSeq(i: number, v: string) {
  const s = [...seq.value]
  s[i] = v
  // Empty cells keep their place so the string stays aligned to positions 1–4.
  emit('update:modelValue', s.some((x) => x) ? s.map((x) => x || ' ').join('').trimEnd() : '')
}
function toggleMulti(k: string) {
  const cur = multi.value
  emit('update:modelValue', cur.includes(k) ? cur.filter((x) => x !== k) : [...cur, k])
}
</script>

<template>
  <div class="answer" :class="{ drill }">
    <p class="prompt">{{ task.prompt }}</p>

    <template v-if="task.qtype === 'single'">
      <button
        v-for="(lbl, i) in labels" :key="lbl" type="button" class="opt" :class="{ on: single === lbl }"
        :disabled="disabled" @click="emit('update:modelValue', lbl)"
      >
        <span class="lbl">{{ lbl }}</span><span class="otext">{{ options[i] }}</span>
      </button>
    </template>

    <template v-else-if="task.qtype === 'short'">
      <label class="muted">Відповідь (число або десятковий дріб):</label>
      <input
        class="short" inputmode="decimal" autocomplete="off" :value="single" :disabled="disabled"
        @input="emit('update:modelValue', ($event.target as HTMLInputElement).value.trim())"
      />
    </template>

    <template v-else-if="task.qtype === 'matching'">
      <div class="right-box">
        <div v-for="(v, k) in right" :key="k">{{ k }}) {{ v }}</div>
      </div>
      <div v-for="(row, i) in task.left ?? []" :key="i" class="match-row">
        <span class="left">{{ row }}</span>
        <select :value="matching[String(i + 1)] ?? ''" :disabled="disabled" @change="setMatch(String(i + 1), ($event.target as HTMLSelectElement).value)">
          <option value="">—</option>
          <option v-for="(_, k) in right" :key="k" :value="k">{{ k }}</option>
        </select>
      </div>
    </template>

    <template v-else-if="task.qtype === 'sequence'">
      <div v-for="(v, k) in items" :key="k" class="seq-item">{{ k }}) {{ v }}</div>
      <div class="seq-grid">
        <label v-for="pos in 4" :key="pos">
          <b>{{ pos }}-е:</b>
          <select :value="seq[pos - 1]" :disabled="disabled" @change="setSeq(pos - 1, ($event.target as HTMLSelectElement).value)">
            <option value="">—</option>
            <option v-for="(_, k) in items" :key="k" :value="k">{{ k }}</option>
          </select>
        </label>
      </div>
    </template>

    <template v-else-if="task.qtype === 'multi3'">
      <button
        v-for="(v, k) in items" :key="k" type="button" class="opt" :class="{ on: multi.includes(String(k)) }"
        :disabled="disabled" @click="toggleMulti(String(k))"
      >
        <span class="lbl check">{{ multi.includes(String(k)) ? '✓' : k }}</span><span class="otext">{{ v }}</span>
      </button>
    </template>
  </div>
</template>

<style scoped>
.prompt { white-space: pre-wrap; font-size: 17px; line-height: 1.45; margin: 2px 0 12px; }
.opt {
  display: flex; gap: 10px; align-items: flex-start; width: 100%; text-align: left;
  background: var(--nmt-card); border: 1px solid var(--nmt-border); border-radius: 14px;
  padding: 11px 12px; margin: 6px 0; font: inherit; color: inherit; cursor: pointer;
}
.opt.on { background: var(--nmt-soft-indigo); border-color: var(--ion-color-primary); box-shadow: inset 0 0 0 1px var(--ion-color-primary); }
.drill .opt.on { background: #D1FAE5; border-color: var(--ion-color-secondary); box-shadow: inset 0 0 0 1px var(--ion-color-secondary); }
.opt:disabled { cursor: default; opacity: .85; }
.lbl {
  flex: none; width: 28px; height: 28px; border-radius: 50%; display: grid; place-items: center;
  background: var(--nmt-soft-indigo); color: #3730A3; font-weight: 700;
}
.opt.on .lbl { background: var(--ion-color-primary); color: #fff; }
.drill .opt.on .lbl { background: var(--ion-color-secondary); }
.otext { padding-top: 4px; line-height: 1.35; white-space: pre-wrap; }
.muted { color: var(--nmt-muted); font-size: 14px; }
.short {
  display: block; margin-top: 6px; font-size: 20px; padding: 10px 12px; width: 100%; max-width: 260px;
  border: 1px solid var(--nmt-border); border-radius: 12px; background: #fff; color: var(--nmt-text);
}
.right-box { background: var(--nmt-card-soft); border: 1px solid var(--nmt-border); border-radius: 12px; padding: 8px 12px; margin-bottom: 8px; font-size: 15px; line-height: 1.5; }
.match-row { display: flex; gap: 10px; align-items: center; justify-content: space-between; padding: 6px 0; border-bottom: 1px dashed var(--nmt-border); }
.left { flex: 1; line-height: 1.35; }
select {
  font-size: 17px; font-weight: 700; padding: 8px 10px; min-width: 64px; border-radius: 10px;
  border: 1px solid var(--nmt-border); background: #fff; color: var(--nmt-text);
}
.seq-item { margin: 4px 0; line-height: 1.4; }
.seq-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 160px)); gap: 10px; margin-top: 10px; }
.seq-grid label { display: flex; align-items: center; gap: 6px; }
</style>
