<script setup lang="ts">
// Personal cabinet: subject levels and goals, progress chart, weak topics, training history.
import {
  IonButton, IonButtons, IonContent, IonHeader, IonModal, IonPage, IonRefresher, IonRefresherContent, IonTitle, IonToolbar,
  type RefresherCustomEvent,
} from '@ionic/vue'
import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import OwlBanner from '../components/OwlBanner.vue'
import ProgressChart from '../components/ProgressChart.vue'
import SubjectStatCard from '../components/SubjectStatCard.vue'
import { errorText } from '../cloud/client'
import { cabinetSubjects, formatWhen, history, progressSeries, subjectStats, weakTopics } from '../core/cabinet'
import { SUBJECTS_CONFIG } from '../core/config'
import { formatSummariesReport } from '../core/engine'
import { avatarText, daysUntilExam, daysWord, shortName, targetFor } from '../core/profiles'
import type { SessionResult } from '../core/types'
import { useAppStore } from '../stores/app'
import { useTrainingStore } from '../stores/training'
import { downloadText, reportFileName, say } from '../ui'

const HISTORY_LIMIT = 30
const app = useAppStore()
const training = useTrainingStore()
const router = useRouter()

const profile = computed(() => app.profile!)
const results = computed(() => app.results)
const subjects = computed(() => cabinetSubjects(results.value, profile.value))
const stats = computed(() => subjects.value.map((sid) => subjectStats(results.value, sid, profile.value)))
const topics = computed(() => weakTopics(results.value, subjects.value))
const worst = computed(() => Math.max(1, ...topics.value.map((t) => t.mistakes)))
const rows = computed(() => history(results.value, HISTORY_LIMIT))

const chartSubject = ref<string | null>(null)
watch(stats, (st) => {
  if (!chartSubject.value || !subjects.value.includes(chartSubject.value)) {
    const withData = st.filter((s) => s.sessions).map((s) => s.subject)
    chartSubject.value = (withData.length ? withData : subjects.value)[0] ?? null
  }
}, { immediate: true })
const series = computed(() => (chartSubject.value ? progressSeries(results.value, chartSubject.value) : []))

const subline = computed(() => {
  const days = daysUntilExam(profile.value)
  let sub: string
  if (days === null) sub = 'Дату НМТ не вказано'
  else if (days > 0) sub = `До НМТ ${days} ${daysWord(days)}`
  else if (days === 0) sub = 'НМТ сьогодні — успіху! 🍀'
  else sub = 'Дата НМТ минула — онови її в профілі'
  const scored = results.value.filter((r) => !r.mistake_drill).length
  return `Особистий кабінет • ${sub} • тренувань: ${scored}`
})
const cloudLine = computed(() => {
  let t = `☁️ ${app.email ?? ''}`
  if (app.loadingHistory) t += ' • синхронізація…'
  else if (app.historyError) t += ' • не вдалося оновити — потягни вниз, щоб повторити'
  if (app.pending) t += ` • очікують відправки: ${app.pending}`
  if (app.streak) t = `🔥 ${app.streak} ${daysWord(app.streak)} поспіль • ` + t
  return t
})

async function onRefresh(ev: RefresherCustomEvent) {
  await app.refresh()
  ev.target.complete()
}

const starting = ref(false)
async function train(subject: string, section: string) {
  if (starting.value) return
  starting.value = true
  try {
    await training.beginFocus(subject, section)
    await router.push('/session')
  } catch (e) {
    await say('Тренування', `Не вдалося почати тренування:\n${errorText(e)}`)
  } finally {
    starting.value = false
  }
}

const reportOpen = ref(false)
const reportText = ref('')
const reportWhen = ref('')
function openReport(id: string | number | null) {
  const r = results.value.find((x) => x.id === id) as SessionResult | undefined
  if (!r) return
  const when = new Date((r.created_at ?? r.finished_at).replace(' ', 'T'))
  reportText.value = formatSummariesReport(r.subjects, Number.isNaN(when.getTime()) ? new Date() : when)
  reportWhen.value = formatWhen(r.created_at ?? r.finished_at)
  reportOpen.value = true
}
</script>

<template>
  <ion-page>
    <ion-header>
      <ion-toolbar>
        <ion-title>Мій кабінет</ion-title>
        <ion-buttons slot="end">
          <ion-button router-link="/about" aria-label="Про програму">ⓘ</ion-button>
          <ion-button router-link="/profile">✎ Профіль</ion-button>
        </ion-buttons>
      </ion-toolbar>
    </ion-header>
    <ion-content class="ion-padding">
      <ion-refresher slot="fixed" @ion-refresh="onRefresh"><ion-refresher-content /></ion-refresher>
      <div class="page">
        <div class="hero">
          <div class="avatar">{{ avatarText(profile) }}</div>
          <div class="who">
            <h1>{{ shortName(profile.name, 24) }}</h1>
            <div class="sub">{{ subline }}</div>
            <div class="cloud">{{ cloudLine }}</div>
          </div>
        </div>
        <ion-button expand="block" size="large" router-link="/setup">🚀 До тренування</ion-button>

        <div v-if="!results.length && !app.loadingHistory" class="nmt-card empty">
          <OwlBanner :size="76" title="Тут буде твій прогрес 🦉"
            text="Пройди перше тренування — і Сова-Ліза покаже рівень з кожного предмета, графік, слабкі теми та історію." />
        </div>

        <section v-if="stats.length" class="nmt-card">
          <div class="head"><h2>📚 Мої предмети</h2><span class="hint">Рівень — середній бал НМТ за останні 3 тренування</span></div>
          <div class="grid">
            <SubjectStatCard v-for="st in stats" :key="st.subject" :stats="st" :selected="st.subject === chartSubject" @select="chartSubject = $event" />
          </div>
        </section>

        <section v-if="subjects.length" class="nmt-card">
          <div class="head"><h2>📈 Прогрес</h2><span class="hint">Бал НМТ (100–200) у кожному тренуванні; пунктир — твоя ціль</span></div>
          <div class="tabs">
            <button v-for="sid in subjects" :key="sid" type="button" :class="{ on: sid === chartSubject }" @click="chartSubject = sid">
              {{ SUBJECTS_CONFIG[sid].name }}
            </button>
          </div>
          <ProgressChart :points="series" :target="chartSubject ? targetFor(profile, chartSubject) : null" />
        </section>

        <section class="nmt-card">
          <div class="head"><h2>🎯 Слабкі теми</h2><span class="hint">Розділи з найбільшою кількістю помилок (свіжі тренування важать більше)</span></div>
          <p v-if="!topics.length" class="nmt-muted">Поки що слабких тем немає. Пройди тренування — і Сова-Ліза підкаже, що повторити.</p>
          <div v-for="t in topics" :key="t.subject + t.section" class="topic">
            <div class="ttext">
              <div class="tsec">{{ t.section }}</div>
              <div class="nmt-muted small">{{ t.subject_name }} • помилок: {{ t.mistakes }}</div>
              <div class="bar"><span :style="{ width: Math.max(5, (100 * t.mistakes) / worst) + '%' }" /></div>
            </div>
            <ion-button size="small" color="secondary" :disabled="starting" @click="train(t.subject, t.section)">Потренувати</ion-button>
          </div>
        </section>

        <section class="nmt-card">
          <div class="head"><h2>🗓 Історія тренувань</h2><span v-if="results.length > HISTORY_LIMIT" class="hint">Останні {{ HISTORY_LIMIT }}</span></div>
          <p v-if="!rows.length" class="nmt-muted">Тут з’являться твої тренування.</p>
          <button v-for="h in rows" :key="String(h.id)" type="button" class="hrow" @click="openReport(h.id)">
            <div class="hwhen"><b>{{ formatWhen(h.at) }}</b><span class="nmt-muted">{{ h.title }}</span></div>
            <div class="hsubj">
              <span v-for="s in h.subjects" :key="s.subject">{{ s.name }}: <b>{{ s.nmt_200 ?? '<поріг' }}</b></span>
            </div>
            <span class="hrep">📄</span>
          </button>
        </section>
      </div>

      <ion-modal :is-open="reportOpen" @did-dismiss="reportOpen = false">
        <ion-header>
          <ion-toolbar>
            <ion-title>Звіт від {{ reportWhen }}</ion-title>
            <ion-buttons slot="end"><ion-button @click="reportOpen = false">Закрити</ion-button></ion-buttons>
          </ion-toolbar>
        </ion-header>
        <ion-content class="ion-padding">
          <pre class="report">{{ reportText }}</pre>
          <ion-button expand="block" color="secondary" @click="downloadText(reportFileName(), reportText)">💾 Зберегти (.txt)</ion-button>
        </ion-content>
      </ion-modal>
    </ion-content>
  </ion-page>
</template>

<style scoped>
.page { max-width: 1040px; margin: 0 auto; display: grid; gap: 14px; padding-bottom: 28px; }
.hero { display: flex; gap: 12px; align-items: center; background: var(--nmt-nav); color: #fff; border-radius: 20px; padding: 14px 16px; }
.avatar { width: 56px; height: 56px; flex: none; border-radius: 50%; background: #fff; display: grid; place-items: center; font-size: 28px; color: var(--nmt-text); font-weight: 700; }
.who h1 { margin: 0; font-size: 22px; }
.sub { font-size: 13px; color: #CBD5E1; margin-top: 2px; }
.cloud { font-size: 13px; color: #A5B4FC; margin-top: 2px; }
.head { display: flex; flex-wrap: wrap; align-items: baseline; gap: 4px 12px; margin-bottom: 8px; }
.head h2 { margin: 0; font-size: 18px; }
.hint { font-size: 13px; color: var(--nmt-muted); }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)); gap: 8px; }
.tabs { display: flex; gap: 6px; overflow-x: auto; padding-bottom: 6px; }
.tabs button { flex: none; font: inherit; font-size: 14px; padding: 6px 12px; border-radius: 14px; border: 1px solid var(--nmt-border); background: #fff; color: var(--nmt-text); }
.tabs button.on { background: var(--ion-color-primary); border-color: var(--ion-color-primary); color: #fff; }
.topic { display: flex; align-items: center; gap: 12px; padding: 8px 0; border-bottom: 1px dashed var(--nmt-border); }
.ttext { flex: 1; min-width: 0; }
.tsec { font-weight: 700; }
.small { font-size: 13px; }
.bar { height: 8px; border-radius: 4px; background: var(--nmt-soft-rose); margin-top: 5px; max-width: 220px; }
.bar span { display: block; height: 100%; border-radius: 4px; background: #F87171; }
.hrow { display: flex; flex-wrap: wrap; gap: 4px 14px; align-items: center; width: 100%; text-align: left; font: inherit; color: inherit; padding: 10px 8px; border: 0; border-bottom: 1px solid var(--nmt-border); background: transparent; cursor: pointer; }
.hrow:nth-child(odd) { background: var(--nmt-card-soft); }
.hwhen { display: flex; flex-direction: column; min-width: 150px; font-size: 14px; }
.hsubj { flex: 1; display: flex; flex-wrap: wrap; gap: 4px 14px; font-size: 14px; }
.hrep { font-size: 18px; }
.report { white-space: pre-wrap; font-family: ui-monospace, Menlo, monospace; font-size: 13px; background: var(--nmt-card); border: 1px solid var(--nmt-border); border-radius: 14px; padding: 12px; }
</style>
