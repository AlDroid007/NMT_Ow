<script setup lang="ts">
// The training: task card with answers, the owl chat with 10-level hints and the identical example.
import { IonButton, IonButtons, IonContent, IonHeader, IonPage, IonTitle, IonToolbar } from '@ionic/vue'
import { computed, nextTick, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import AnswerInput from '../components/AnswerInput.vue'
import ChatList from '../components/ChatList.vue'
import HintStepper from '../components/HintStepper.vue'
import OwlBanner from '../components/OwlBanner.vue'
import { SUBJECTS_CONFIG } from '../core/config'
import { useTrainingStore } from '../stores/training'
import { ask, say } from '../ui'

const t = useTrainingStore()
const router = useRouter()
const content = ref<InstanceType<typeof IonContent> | null>(null)
const owlPanel = ref<HTMLElement | null>(null)
const chatBox = ref<HTMLElement | null>(null)

const q = computed(() => t.question)
const cfg = computed(() => (t.block ? SUBJECTS_CONFIG[t.block.subject] : null))
const timer = computed(() => {
  if (t.seconds <= 0) return '⏱ Час вийшов!'
  const h = Math.floor(t.seconds / 3600)
  const m = Math.floor((t.seconds % 3600) / 60)
  const s = t.seconds % 60
  const pad = (n: number) => String(n).padStart(2, '0')
  return h ? `⏱ ${h}:${pad(m)}:${pad(s)}` : `⏱ ${pad(m)}:${pad(s)}`
})
const hintText = computed(() => (t.hintLevel < 10 ? `💡 Підказка (${t.hintLevel + 1}/10)` : '💡 Усі 10/10 відкрито'))

const wide = () => window.matchMedia('(min-width: 900px)').matches

async function scrollChat() {
  await nextTick()
  if (chatBox.value) chatBox.value.scrollTop = chatBox.value.scrollHeight
}
watch(() => t.chat.length, scrollChat)

/** On a phone the owl panel is under the task: bring it into view after a hint or a check. */
async function revealOwl() {
  await nextTick()
  if (wide() || !owlPanel.value || !content.value) return
  const el = await content.value.$el.getScrollElement()
  el.scrollTo({ top: owlPanel.value.offsetTop - 8, behavior: 'smooth' })
}

watch(() => [t.blockIdx, t.qIdx], async () => {
  await nextTick()
  content.value?.$el.scrollToTop(200)
})

async function hint(level?: number) {
  if (!t.tutorMode) return say('Режим іспиту', 'У режимі іспиту підказки вимкнені — перевірка буде наприкінці.')
  if (level === undefined) {
    if (t.hintLevel >= 10) return
    level = t.hintLevel + 1
  }
  t.showHint(level)
  void revealOwl()
}

async function check() {
  if (!t.submit()) return say('Немає відповіді', 'Спочатку оберіть або введіть варіант відповіді.')
  if (!t.tutorMode) return next()
  void revealOwl()
}

async function next() {
  if (!t.next()) await finish(false)
}

async function finish(confirm = true) {
  if (confirm && !(await ask('Завершити тест', 'Завершити тренування й побачити результати?', 'Завершити'))) return
  await t.finish()
  await router.replace('/results')
}

async function drillCheck() {
  if (!t.drillSubmit()) await say('Немає відповіді', 'Розв’яжи схожий приклад та обери/введи відповідь.')
}
</script>

<template>
  <ion-page>
    <ion-header>
      <ion-toolbar>
        <ion-title v-if="cfg">{{ cfg.name }} ({{ t.blockIdx + 1 }}/{{ t.plan.length }})</ion-title>
        <ion-buttons slot="end">
          <ion-button color="danger" fill="solid" @click="finish()">Завершити</ion-button>
        </ion-buttons>
      </ion-toolbar>
      <div class="bar">
        <span class="chip time">{{ timer }}</span>
        <span class="chip score">Бал: {{ t.score[0] }} / {{ t.score[1] }}</span>
        <span v-if="t.mistakeDrill" class="chip mode">🔁 Робота над помилками</span>
        <span v-else-if="t.focusSection" class="chip mode">🎯 {{ t.focusSection }}</span>
        <span v-else-if="!t.tutorMode" class="chip mode">⏱ Режим іспиту</span>
      </div>
    </ion-header>

    <ion-content v-if="q && t.block" ref="content" class="ion-padding">
      <div v-if="t.plan.length > 1" class="tabs">
        <button v-for="(b, i) in t.plan" :key="b.subject" type="button" :class="{ on: i === t.blockIdx }" @click="t.switchBlock(i)">
          {{ SUBJECTS_CONFIG[b.subject].name }}
        </button>
      </div>

      <div class="layout">
        <section class="nmt-card task">
          <div class="meta">
            <b class="num">Завдання {{ t.qIdx + 1 }} із {{ t.block.questions.length }} • макс. {{ q.max_points ?? 1 }} б.</b>
            <span v-if="q.source" class="src">{{ q.source }}</span>
          </div>
          <div class="sec">Тема: {{ q.section }}</div>
          <AnswerInput :key="t.answerKey" v-model="t.answer" :task="q" :disabled="t.alreadyAnswered" />
          <div class="actions">
            <ion-button :disabled="t.alreadyAnswered" @click="check">✓ Перевірити відповідь</ion-button>
            <ion-button color="warning" fill="outline" :disabled="!t.tutorMode || t.hintLevel >= 10" @click="hint()">{{ hintText }}</ion-button>
            <ion-button color="secondary" class="next" @click="next">Далі →</ion-button>
          </div>
          <div class="dots" aria-label="Завдання блоку">
            <button
              v-for="(_, i) in t.block.questions" :key="i" type="button"
              :class="{ cur: i === t.qIdx, done: i in t.block.answers, bad: t.tutorMode && t.block.mistakes.includes(i) }"
              @click="t.goTo(i)"
            >{{ i + 1 }}</button>
          </div>
        </section>

        <section ref="owlPanel" class="nmt-card owl-panel">
          <OwlBanner title="Сова-Ліза • Мудрий Репетитор" :text="t.status" :mood="t.mood" :size="76" />
          <HintStepper class="stepper" :level="t.hintLevel" :disabled="!t.tutorMode" @select="hint" />
          <div ref="chatBox" class="chat-box">
            <ChatList :messages="t.chat" />

            <div v-if="t.drill" class="drill">
              <div class="dhead">🔁 Опрацювання на ідентичному прикладі (закріплюємо правило!):</div>
              <AnswerInput :key="t.drill.key" v-model="t.drill.answer" :task="t.drill.task" drill />
              <p v-if="t.drill.feedback" class="dfb" :class="t.drill.feedback.tone">{{ t.drill.feedback.text }}</p>
              <div class="actions">
                <ion-button color="secondary" @click="drillCheck">✓ Перевірити</ion-button>
                <ion-button color="warning" fill="outline" :disabled="t.drill.hintLevel >= 10" @click="t.drillHint()">
                  {{ t.drill.hintLevel < 10 ? `💡 Підказка (${t.drill.hintLevel + 1}/10)` : '💡 10/10' }}
                </ion-button>
                <ion-button fill="clear" color="secondary" @click="t.newDrill(t.drill.source)">Інший ↻</ion-button>
              </div>
            </div>
          </div>
        </section>
      </div>
    </ion-content>
  </ion-page>
</template>

<style scoped>
.bar { display: flex; gap: 6px; flex-wrap: wrap; padding: 6px 12px 8px; background: var(--nmt-nav); }
.chip { font-weight: 700; font-size: 14px; padding: 4px 10px; border-radius: 10px; background: var(--nmt-nav-accent); }
.time { color: #BFDBFE; }
.score { color: #A7F3D0; }
.mode { color: #FDE68A; }
.tabs { display: flex; gap: 6px; overflow-x: auto; padding-bottom: 10px; }
.tabs button { flex: none; font: inherit; font-size: 14px; font-weight: 700; padding: 7px 12px; border-radius: 14px; border: 1px solid var(--nmt-border); background: #fff; color: var(--nmt-text); }
.tabs button.on { background: var(--ion-color-primary); border-color: var(--ion-color-primary); color: #fff; }
.layout { display: grid; gap: 14px; max-width: 1200px; margin: 0 auto; padding-bottom: 28px; }
@media (min-width: 900px) {
  .layout { grid-template-columns: minmax(0, 1.1fr) minmax(0, 1fr); align-items: start; }
  .owl-panel { position: sticky; top: 0; }
  .chat-box { max-height: calc(100vh - 300px); overflow-y: auto; }
}
.meta { display: flex; justify-content: space-between; gap: 8px; flex-wrap: wrap; align-items: center; }
.num { color: var(--ion-color-primary); }
.src { font-size: 12px; background: var(--nmt-soft-indigo); color: #3730A3; padding: 3px 10px; border-radius: 10px; }
.sec { font-size: 13px; color: var(--nmt-muted); margin: 4px 0 8px; }
.actions { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 12px; }
.actions .next { margin-left: auto; }
.dots { display: flex; flex-wrap: wrap; gap: 5px; margin-top: 12px; }
.dots button { width: 30px; height: 30px; padding: 0; border-radius: 9px; font-size: 13px; font-weight: 700; border: 1px solid var(--nmt-border); background: #fff; color: var(--nmt-muted); }
.dots button.done { background: var(--nmt-soft-indigo); color: #3730A3; border-color: var(--nmt-soft-indigo-bd); }
.dots button.bad { background: var(--nmt-soft-rose); color: var(--nmt-err-fg); border-color: var(--nmt-soft-rose-bd); }
.dots button.cur { box-shadow: 0 0 0 2px var(--ion-color-primary); }
.stepper { margin: 10px 0; }
.drill { background: var(--nmt-soft-mint); border: 1px solid var(--nmt-soft-mint-bd); border-radius: 18px; padding: 12px; margin: 8px 0 12px; }
.dhead { font-weight: 700; color: #0F766E; margin-bottom: 6px; }
.dfb { white-space: pre-wrap; font-size: 15px; }
.dfb.ok { color: var(--nmt-ok-fg); }
.dfb.err { color: var(--nmt-err-fg); }
.dfb.hint { color: #78350F; }
</style>
