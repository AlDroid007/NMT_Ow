<script setup lang="ts">
// Results on the 100–200 scale, the report and mistake practice (desktop: results screen).
import { IonButton, IonContent, IonHeader, IonPage, IonSpinner, IonTitle, IonToolbar } from '@ionic/vue'
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import OwlBanner from '../components/OwlBanner.vue'
import { errorText } from '../cloud/client'
import { computeSubjectSummary } from '../core/engine'
import { useTrainingStore } from '../stores/training'
import { downloadText, reportFileName, say } from '../ui'

const t = useTrainingStore()
const router = useRouter()
const busy = ref(false)
const summaries = computed(() => t.plan.map(computeSubjectSummary))

async function drillMistakes() {
  busy.value = true
  try {
    await t.beginMistakeDrill()
    await router.replace('/session')
  } catch (e) {
    await say('Тренування', `Не вдалося почати тренування:\n${errorText(e)}`)
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <ion-page>
    <ion-header>
      <ion-toolbar><ion-title>📊 Результати (шкала 100–200)</ion-title></ion-toolbar>
    </ion-header>
    <ion-content class="ion-padding">
      <div class="page">
        <OwlBanner
          title="Підсумок від Сови-Лізи 🦉" :mood="t.hasMistakes ? 'explain' : 'happy'" :size="80"
          :text="t.hasMistakes
            ? 'Чудова робота! У тебе є кілька помилок, і ми можемо прямо зараз відпрацювати їх на ідентичних прикладах!'
            : 'Фантастично! Жодної помилки — ти повністю готовий(а) до такого варіанта НМТ!'"
        />
        <p v-if="t.saved === 'empty'" class="note warn">Ти не відповів(ла) на жодне завдання, тому це тренування не збережено в кабінеті.</p>
        <p v-else-if="t.saved === 'queued'" class="note warn">Немає зв’язку з хмарою: тренування збережено на цьому пристрої й надішлеться, щойно з’явиться інтернет.</p>
        <p v-else-if="t.saved === 'sent'" class="note ok">☁️ Тренування збережено в хмарі.</p>

        <div class="cards">
          <div v-for="s in summaries" :key="s.subject" class="nmt-card score">
            <div class="sname">{{ s.name }}</div>
            <div class="big" :class="{ fail: s.nmt_200 === null }">{{ s.nmt_200 ?? `< ${s.threshold}` }}</div>
            <div class="nmt-muted small">{{ s.earned }} із {{ s.actual_max }} б. • {{ s.is_full ? 'точний формат' : 'прогноз' }}</div>
          </div>
        </div>

        <pre class="nmt-card report">{{ t.report }}</pre>

        <div class="actions">
          <ion-button v-if="t.hasMistakes" :disabled="busy" @click="drillMistakes">
            <ion-spinner v-if="busy" name="crescent" /><span v-else>🔁 Відпрацювати помилки з Совою</span>
          </ion-button>
          <ion-button color="secondary" fill="outline" @click="downloadText(reportFileName(), t.report)">💾 Зберегти звіт (.txt)</ion-button>
          <ion-button fill="outline" router-link="/setup" router-direction="root">🏠 Обрати інші предмети</ion-button>
          <ion-button router-link="/cabinet" router-direction="root">👤 Мій кабінет</ion-button>
        </div>
      </div>
    </ion-content>
  </ion-page>
</template>

<style scoped>
.page { max-width: 900px; margin: 0 auto; display: grid; gap: 12px; padding-bottom: 28px; }
.note { margin: 0; padding: 10px 12px; border-radius: 12px; font-size: 14px; }
.note.warn { background: var(--nmt-soft-amber); color: #92400E; }
.note.ok { background: var(--nmt-ok-bg); color: var(--nmt-ok-fg); }
.cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 8px; }
.score { padding: 12px 14px; }
.sname { font-weight: 700; }
.big { font-size: 30px; font-weight: 800; color: var(--ion-color-primary); }
.big.fail { color: var(--nmt-err-fg); font-size: 22px; }
.small { font-size: 13px; }
.report { white-space: pre-wrap; font-family: ui-monospace, Menlo, monospace; font-size: 13px; margin: 0; overflow-x: auto; }
.actions { display: flex; flex-wrap: wrap; gap: 6px; }
</style>
