<script setup lang="ts">
// Closed access: a login and a password given by the owner (public.app_gate_logins), before the
// e-mail sign-in and every other screen. See src/cloud/gate.ts.
import { IonButton, IonContent, IonPage, IonSpinner } from '@ionic/vue'
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import OwlBanner from '../components/OwlBanner.vue'
import { errorText } from '../cloud/client'
import { GateError, gateSignIn } from '../cloud/gate'
import { APP_TITLE } from '../config'
import { useAppStore } from '../stores/app'

const app = useAppStore()
const route = useRoute()
const router = useRouter()
const login = ref('')
const password = ref('')
const busy = ref(false)
const status = ref('')

async function submit() {
  if (busy.value) return
  if (!login.value.trim() || !password.value) {
    status.value = 'Введи логін і пароль.'
    return
  }
  busy.value = true
  status.value = ''
  try {
    if (await gateSignIn(login.value, password.value)) {
      app.gateOpen = true
      password.value = ''
      const next = typeof route.query.next === 'string' && route.query.next.startsWith('/') ? route.query.next : '/'
      await router.replace(next)
    } else {
      status.value = 'Неправильний логін або пароль.'
    }
  } catch (err) {
    status.value = err instanceof GateError ? err.message : errorText(err)
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <ion-page>
    <ion-content class="ion-padding">
      <div class="wrap">
        <h1 class="app-title">{{ APP_TITLE }}</h1>
        <OwlBanner :size="84" title="Закритий доступ 🦉" text="Програма поки відкрита лише для тестувальників. Введи логін і пароль, які тобі дали." />
        <form class="nmt-card form" @submit.prevent="submit">
          <h2>Вхід для тестувальників</h2>
          <input
            v-model="login" class="field" name="username" autocomplete="username" autocapitalize="none"
            autocorrect="off" spellcheck="false" placeholder="Логін"
          />
          <input v-model="password" class="field" name="password" type="password" autocomplete="current-password" placeholder="Пароль" />
          <p v-if="status" class="status">{{ status }}</p>
          <ion-button expand="block" type="submit" :disabled="busy">
            <ion-spinner v-if="busy" name="crescent" />
            <span v-else>Увійти</span>
          </ion-button>
        </form>
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
  width: 100%; font-size: 18px; padding: 12px 14px; margin: 8px 0 4px; border-radius: 12px;
  border: 1px solid var(--nmt-border); background: #fff; color: var(--nmt-text);
}
.status { white-space: pre-wrap; font-size: 14px; color: var(--nmt-err-fg); }
</style>
