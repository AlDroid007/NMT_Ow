<script setup lang="ts">
// «Створимо твій профіль» / «Мій профіль»: name, avatar, subjects, goals, exam date, account.
import { IonBackButton, IonButton, IonButtons, IonContent, IonHeader, IonPage, IonTitle, IonToolbar } from '@ionic/vue'
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import * as api from '../cloud/api'
import { errorText } from '../cloud/client'
import { SUBJECTS_CONFIG, SUBJECTS_ORDER } from '../core/config'
import { AVATARS, DEFAULT_SUBJECTS, formatExamDate, ProfileError } from '../core/profiles'
import { useAppStore } from '../stores/app'
import { ask, say, toast } from '../ui'

const app = useAppStore()
const router = useRouter()
const isNew = computed(() => !app.profile)
const p = app.profile

const name = ref(p?.name ?? '')
const avatar = ref(p?.avatar.kind === 'emoji' ? p.avatar.value : AVATARS[0])
const subjects = ref<string[]>([...(p?.subjects ?? DEFAULT_SUBJECTS)])
const targets = ref<Record<string, string>>(Object.fromEntries(Object.entries(p?.targets ?? {}).map(([k, v]) => [k, String(v)])))
const examDate = ref(formatExamDate(p?.exam_date))
const busy = ref(false)

const chosen = computed(() => SUBJECTS_ORDER.filter((s) => subjects.value.includes(s)))

function toggle(sid: string) {
  subjects.value = subjects.value.includes(sid) ? subjects.value.filter((s) => s !== sid) : [...subjects.value, sid]
}

async function save() {
  if (busy.value) return
  const t: Record<string, number> = {}
  for (const sid of chosen.value) {
    const raw = (targets.value[sid] ?? '').trim()
    if (raw) t[sid] = raw as unknown as number
  }
  busy.value = true
  try {
    const saved = await api.saveProfile({
      ...(p ?? {}),
      name: name.value,
      avatar: { kind: 'emoji', value: avatar.value },
      subjects: chosen.value,
      targets: t,
      exam_date: examDate.value.trim() || null,
    })
    const wasNew = isNew.value
    app.setProfile(saved)
    if (wasNew) void app.refresh()
    void toast(wasNew ? 'Профіль створено!' : 'Профіль збережено', 'success')
    await router.replace('/cabinet')
  } catch (e) {
    await say('Перевірте профіль', e instanceof ProfileError ? e.message : errorText(e))
  } finally {
    busy.value = false
  }
}

async function signOut() {
  if (!(await ask('Вийти з акаунта', `Вийти з акаунта ${app.email ?? ''} на цьому пристрої? Усе збережено в хмарі.`, 'Вийти'))) return
  await app.signOut()
  await router.replace('/signin')
}

async function deleteAll() {
  const ok = await ask(
    'Видалити дані з хмари',
    `Видалити хмарний акаунт ${app.email ?? ''} і ВСІ збережені в хмарі тренування та прогрес? Скасувати видалення неможливо.`,
    'Видалити', true,
  )
  if (!ok) return
  try {
    await app.deleteAccount()
    await say('Хмара', 'Хмарний акаунт і всі дані в хмарі видалено.')
    await router.replace('/signin')
  } catch (e) {
    await say('Хмара', `Не вдалося видалити:\n${errorText(e)}`)
  }
}
</script>

<template>
  <ion-page>
    <ion-header>
      <ion-toolbar>
        <ion-buttons v-if="!isNew" slot="start"><ion-back-button default-href="/cabinet" text="Назад" /></ion-buttons>
        <ion-title>{{ isNew ? 'Створимо твій профіль' : 'Мій профіль' }}</ion-title>
      </ion-toolbar>
    </ion-header>
    <ion-content class="ion-padding">
      <form class="page" @submit.prevent="save">
        <section class="nmt-card">
          <h2>Як тебе звати?</h2>
          <input v-model="name" class="field" maxlength="40" autocomplete="given-name" placeholder="Ім’я" />
          <h2>Аватар</h2>
          <div class="avatars">
            <button v-for="a in AVATARS" :key="a" type="button" :class="{ on: avatar === a }" @click="avatar = a">{{ a }}</button>
          </div>
        </section>

        <section class="nmt-card">
          <h2>Мої предмети НМТ</h2>
          <p class="nmt-muted hint">Їх буде позначено одразу на екрані вибору, а в кабінеті — показано прогрес</p>
          <div class="chips">
            <button v-for="sid in SUBJECTS_ORDER" :key="sid" type="button" :class="{ on: subjects.includes(sid) }" @click="toggle(sid)">
              {{ subjects.includes(sid) ? '✓ ' : '' }}{{ SUBJECTS_CONFIG[sid].name }}
            </button>
          </div>
        </section>

        <section class="nmt-card">
          <h2>Мої цілі</h2>
          <p class="nmt-muted hint">Бажаний бал НМТ за шкалою 100–200 для кожного предмета</p>
          <p v-if="!chosen.length" class="nmt-muted">Спершу оберіть предмети вище.</p>
          <div v-for="sid in chosen" :key="sid" class="target">
            <span>{{ SUBJECTS_CONFIG[sid].name }}</span>
            <input v-model="targets[sid]" inputmode="numeric" maxlength="3" placeholder="170" />
          </div>
        </section>

        <section class="nmt-card">
          <h2>Дата НМТ</h2>
          <p class="nmt-muted hint">Наприклад 20.05.2027 — у кабінеті з’явиться відлік днів. Можна залишити порожнім.</p>
          <input v-model="examDate" class="field" inputmode="numeric" placeholder="ДД.ММ.РРРР" />
        </section>

        <ion-button expand="block" type="submit" :disabled="busy">{{ isNew ? '✨ Створити профіль' : '💾 Зберегти' }}</ion-button>

        <section class="nmt-card account">
          <h2>Акаунт</h2>
          <p class="nmt-muted">☁️ {{ app.email }}</p>
          <ion-button fill="outline" expand="block" @click="signOut">Вийти з акаунта</ion-button>
          <ion-button v-if="!isNew" fill="clear" color="danger" expand="block" @click="deleteAll">🗑 Видалити дані з хмари</ion-button>
        </section>
      </form>
    </ion-content>
  </ion-page>
</template>

<style scoped>
.page { max-width: 640px; margin: 0 auto; display: grid; gap: 14px; padding-bottom: 24px; }
h2 { font-size: 18px; margin: 4px 0 8px; }
.hint { margin: -4px 0 8px; font-size: 14px; }
.field { width: 100%; font-size: 18px; padding: 11px 13px; border-radius: 12px; border: 1px solid var(--nmt-border); background: #fff; color: var(--nmt-text); margin-bottom: 10px; }
.avatars { display: grid; grid-template-columns: repeat(auto-fill, minmax(48px, 1fr)); gap: 8px; }
.avatars button { font-size: 26px; height: 48px; border-radius: 14px; border: 1px solid var(--nmt-border); background: var(--nmt-card-soft); }
.avatars button.on { border: 2px solid var(--ion-color-primary); background: var(--nmt-soft-indigo); }
.chips { display: flex; flex-wrap: wrap; gap: 8px; }
.chips button { font: inherit; font-size: 15px; padding: 8px 12px; border-radius: 16px; border: 1px solid var(--nmt-border); background: #fff; color: var(--nmt-text); }
.chips button.on { background: var(--ion-color-primary); border-color: var(--ion-color-primary); color: #fff; }
.target { display: flex; justify-content: space-between; align-items: center; padding: 6px 0; border-bottom: 1px dashed var(--nmt-border); }
.target input { width: 84px; font-size: 18px; text-align: center; padding: 8px; border-radius: 10px; border: 1px solid var(--nmt-border); background: #fff; color: var(--nmt-text); }
.account { margin-top: 10px; }
</style>
