<script setup lang="ts">
// Sign-in with an e-mail code (desktop: the cloud sign-in dialog). The web needs the cloud.
import { IonButton, IonContent, IonPage, IonSpinner } from '@ionic/vue'
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import OwlBanner from '../components/OwlBanner.vue'
import * as api from '../cloud/api'
import { errorText } from '../cloud/client'
import { APP_TITLE, PRIVACY_URL } from '../config'
import { useAppStore } from '../stores/app'

const app = useAppStore()
const router = useRouter()
const step = ref<'email' | 'code'>('email')
const email = ref('')
const code = ref('')
const agree = ref(false)
const busy = ref(false)
const status = ref('')
const statusErr = ref(false)

function setStatus(text: string, err = false) {
  status.value = text
  statusErr.value = err
}

async function submit() {
  if (busy.value) return
  if (step.value === 'email') {
    const e = email.value.trim()
    if (!/^\S+@\S+\.\S+$/.test(e)) return setStatus('Введи правильну адресу пошти.', true)
    if (!agree.value) return setStatus('Щоб увімкнути хмару, познач згоду з Політикою конфіденційності.', true)
    busy.value = true
    setStatus('Надсилаємо код…')
    try {
      await api.sendCode(e)
      step.value = 'code'
      setStatus(`Ми надіслали код на ${e}.\nВведи цифри з листа (перевір і «Спам»).`)
    } catch (err) {
      setStatus(errorText(err), true)
    } finally {
      busy.value = false
    }
    return
  }
  const c = code.value.replace(/\s/g, '')
  if (!/^\d{4,10}$/.test(c)) return setStatus('Введи цифри з листа.', true)
  busy.value = true
  setStatus('Перевіряємо код…')
  try {
    const s = await api.verifyCode(email.value, c)
    await app.afterSignIn(s.user.id, s.user.email ?? email.value.trim())
    await router.replace(app.profile ? '/cabinet' : '/profile')
  } catch (err) {
    setStatus(errorText(err), true)
  } finally {
    busy.value = false
  }
}

function otherEmail() {
  step.value = 'email'
  code.value = ''
  setStatus('')
}
</script>

<template>
  <ion-page>
    <ion-content class="ion-padding">
      <div class="wrap">
        <h1 class="app-title">{{ APP_TITLE }}</h1>
        <OwlBanner :size="84" title="Привіт! Я Сова-Ліза 🦉" text="Твій персональний репетитор НМТ: 12 предметів, 10 рівнів підказок і шкала 100–200." />
        <form class="nmt-card form" @submit.prevent="submit">
          <h2>{{ step === 'email' ? 'Увійти через пошту' : 'Код із листа' }}</h2>
          <p class="nmt-muted">
            {{ step === 'email'
              ? 'Твої тренування та прогрес зберігаються в хмарі — їх можна відкрити на телефоні й комп’ютері. Введи свою пошту, ми надішлемо код для входу.'
              : 'Один акаунт — один профіль учня з усією історією.' }}
          </p>
          <template v-if="step === 'email'">
            <input v-model="email" class="field" type="email" inputmode="email" autocomplete="email" placeholder="пошта@приклад.com" />
            <label class="consent">
              <input v-model="agree" type="checkbox" />
              <span>Я погоджуюсь з <a :href="PRIVACY_URL" target="_blank" rel="noopener">Політикою конфіденційності</a></span>
            </label>
          </template>
          <input
            v-else v-model="code" class="field code" inputmode="numeric" autocomplete="one-time-code" maxlength="10" placeholder="123456"
          />
          <p v-if="status" class="status" :class="{ err: statusErr }">{{ status }}</p>
          <ion-button expand="block" type="submit" :disabled="busy">
            <ion-spinner v-if="busy" name="crescent" />
            <span v-else>{{ step === 'email' ? 'Надіслати код' : 'Підтвердити' }}</span>
          </ion-button>
          <ion-button v-if="step === 'code'" fill="clear" expand="block" :disabled="busy" @click="otherEmail">← Інша пошта</ion-button>
        </form>
        <p class="foot"><router-link to="/about">Про програму</router-link></p>
      </div>
    </ion-content>
  </ion-page>
</template>

<style scoped>
.wrap { max-width: 460px; margin: 0 auto; padding-top: max(12px, env(safe-area-inset-top)); }
.app-title { font-size: 22px; text-align: center; margin: 8px 0 14px; }
.form { margin-top: 14px; }
.form h2 { margin: 0 0 6px; font-size: 20px; }
.field {
  width: 100%; font-size: 18px; padding: 12px 14px; margin: 10px 0 6px; border-radius: 12px;
  border: 1px solid var(--nmt-border); background: #fff; color: var(--nmt-text);
}
.code { letter-spacing: 6px; text-align: center; font-size: 24px; font-weight: 700; }
.consent { display: flex; gap: 8px; align-items: center; font-size: 14px; margin: 8px 0; }
.consent input { width: 20px; height: 20px; }
.status { white-space: pre-wrap; font-size: 14px; color: var(--nmt-muted); }
.status.err { color: var(--nmt-err-fg); }
.foot { text-align: center; font-size: 14px; margin-top: 18px; }
</style>
