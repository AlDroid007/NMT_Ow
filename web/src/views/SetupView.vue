<script setup lang="ts">
// Subject selection and session settings (desktop: setup screen).
import { IonBackButton, IonButton, IonButtons, IonContent, IonHeader, IonPage, IonSpinner, IonTitle, IonToolbar } from '@ionic/vue'
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import OwlBanner from '../components/OwlBanner.vue'
import { errorText } from '../cloud/client'
import { bankSize, SUBJECTS_CONFIG, SUBJECTS_ORDER } from '../core/config'
import { generatorCount } from '../core/generators'
import { DEFAULT_SUBJECTS } from '../core/profiles'
import { useAppStore } from '../stores/app'
import { useTrainingStore } from '../stores/training'
import { say } from '../ui'

const app = useAppStore()
const training = useTrainingStore()
const router = useRouter()

const selected = ref<string[]>([...(app.profile?.subjects?.length ? app.profile.subjects : DEFAULT_SUBJECTS)])
const mode = ref<'tutor' | 'exam'>('tutor')
const length = ref<'quick' | 'medium' | 'full'>('quick')
const busy = ref(false)

const presets: Array<[string, string[]]> = [
  ['Стандарт НМТ (3 + Англ.)', ['ukrmova', 'math', 'history', 'english']],
  ['Лише обов’язкові (3)', ['ukrmova', 'math', 'history']],
  ['Усі 12 предметів', SUBJECTS_ORDER],
  ['Скинути', []],
]

function toggle(sid: string) {
  selected.value = selected.value.includes(sid) ? selected.value.filter((s) => s !== sid) : [...selected.value, sid]
}

async function start() {
  const subjects = SUBJECTS_ORDER.filter((s) => selected.value.includes(s))
  if (!subjects.length) return say('Оберіть предмети', 'Позначте бодай один предмет НМТ для початку тренування.')
  busy.value = true
  try {
    await training.beginRegular(subjects, length.value, mode.value === 'tutor')
    await router.push('/session')
  } catch (e) {
    const msg = errorText(e)
    await say(msg.includes('інтернет') ? 'Потрібен інтернет' : 'Тренування',
      msg.includes('інтернет') ? 'Щоб почати тренування, потрібне підключення до інтернету.\n\nПеревір з’єднання і спробуй ще раз.' : `Не вдалося почати тренування:\n${msg}`)
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <ion-page>
    <ion-header>
      <ion-toolbar>
        <ion-buttons slot="start"><ion-back-button default-href="/cabinet" text="Кабінет" /></ion-buttons>
        <ion-title>Нове тренування</ion-title>
        <ion-buttons slot="end"><ion-button router-link="/reference">📘 Шкала</ion-button></ion-buttons>
      </ion-toolbar>
    </ion-header>
    <ion-content class="ion-padding">
      <div class="page">
        <OwlBanner title="Привіт! Я Сова-Ліза — твій персональний репетитор НМТ 🦉"
          text="Обирай предмети нижче. У кожному завданні є 10 рівнів підказок (від легкого натяку до повної розповіді) та схожі приклади після помилки." />

        <section class="nmt-card">
          <h2>1. Оберіть предмети</h2>
          <div class="presets">
            <button v-for="[title, list] in presets" :key="title" type="button" @click="selected = [...list]">{{ title }}</button>
          </div>
          <div class="tiles">
            <button v-for="sid in SUBJECTS_ORDER" :key="sid" type="button" class="tile" :class="{ on: selected.includes(sid) }" @click="toggle(sid)">
              <span class="box">{{ selected.includes(sid) ? '✓' : '' }}</span>
              <span class="tt">
                <span class="tname">{{ SUBJECTS_CONFIG[sid].name }}</span>
                <span class="tmeta">{{ SUBJECTS_CONFIG[sid].total_tasks }} завдань • макс. {{ SUBJECTS_CONFIG[sid].max_score }} б. • поріг {{ SUBJECTS_CONFIG[sid].threshold }}</span>
              </span>
              <span class="badge" :class="{ req: SUBJECTS_CONFIG[sid].mandatory }">{{ SUBJECTS_CONFIG[sid].mandatory ? 'Обов’язковий' : 'За вибором' }}</span>
            </button>
          </div>
        </section>

        <section class="nmt-card">
          <h2>2. Режим підготовки</h2>
          <label class="radio" :class="{ on: mode === 'tutor' }">
            <input v-model="mode" type="radio" value="tutor" />
            <span><b>🦉 Із Совою-Репетитором (рекомендовано)</b><br /><small>10 рівнів підказок + схожий приклад при помилці</small></span>
          </label>
          <label class="radio" :class="{ on: mode === 'exam' }">
            <input v-model="mode" type="radio" value="exam" />
            <span><b>⏱ Режим іспиту НМТ</b><br /><small>Таймер без підказок, підсумок наприкінці</small></span>
          </label>

          <h2>3. Обсяг тесту</h2>
          <label class="radio" :class="{ on: length === 'quick' }"><input v-model="length" type="radio" value="quick" /><span>Швидке тренування (8 завд. / предмет)</span></label>
          <label class="radio" :class="{ on: length === 'medium' }"><input v-model="length" type="radio" value="medium" /><span>Середній блок (15 завд. / предмет)</span></label>
          <label class="radio" :class="{ on: length === 'full' }"><input v-model="length" type="radio" value="full" /><span>Повний формат НМТ (22 / 24 / 30 / 32)</span></label>

          <p class="nmt-muted base">Вбудовано {{ bankSize() }} завдань НМТ 2022–2026 рр. + {{ generatorCount() }} генераторів.</p>
        </section>

        <ion-button expand="block" size="large" color="secondary" :disabled="busy" @click="start">
          <ion-spinner v-if="busy" name="crescent" /><span v-else>🚀 Розпочати тренування</span>
        </ion-button>
      </div>
    </ion-content>
  </ion-page>
</template>

<style scoped>
.page { max-width: 900px; margin: 0 auto; display: grid; gap: 14px; padding-bottom: 28px; }
h2 { font-size: 18px; margin: 6px 0 10px; }
.presets { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 10px; }
.presets button { font: inherit; font-size: 14px; padding: 6px 12px; border-radius: 14px; border: 1px solid var(--nmt-soft-indigo-bd); background: var(--nmt-soft-indigo); color: #3730A3; }
.tiles { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 8px; }
.tile { display: flex; gap: 10px; align-items: center; text-align: left; font: inherit; color: inherit; padding: 10px 12px; border-radius: 14px; border: 1px solid var(--nmt-border); background: var(--nmt-card-soft); cursor: pointer; }
.tile.on { border-color: var(--ion-color-primary); background: var(--nmt-soft-indigo); }
.box { flex: none; width: 22px; height: 22px; border-radius: 7px; border: 2px solid var(--nmt-border); display: grid; place-items: center; color: #fff; font-weight: 700; font-size: 13px; }
.tile.on .box { background: var(--ion-color-primary); border-color: var(--ion-color-primary); }
.tt { flex: 1; display: flex; flex-direction: column; min-width: 0; }
.tname { font-weight: 700; }
.tmeta { font-size: 12.5px; color: var(--nmt-muted); }
.badge { flex: none; font-size: 11px; font-weight: 700; padding: 3px 8px; border-radius: 10px; background: var(--nmt-chip-opt-bg); color: var(--nmt-chip-opt-fg); }
.badge.req { background: var(--nmt-chip-req-bg); color: var(--nmt-chip-req-fg); }
.radio { display: flex; gap: 10px; align-items: flex-start; padding: 10px 12px; border-radius: 12px; border: 1px solid var(--nmt-border); background: var(--nmt-card-soft); margin-bottom: 6px; cursor: pointer; }
.radio.on { border-color: var(--ion-color-primary); background: var(--nmt-soft-indigo); }
.radio input { margin-top: 3px; width: 18px; height: 18px; accent-color: var(--ion-color-primary); }
small { color: var(--nmt-muted); }
.base { font-size: 14px; margin: 10px 0 0; }
</style>
