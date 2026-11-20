import { createRouter, createWebHistory } from '@ionic/vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAppStore } from './stores/app'
import { useTrainingStore } from './stores/training'

const routes: RouteRecordRaw[] = [
  { path: '/', redirect: '/cabinet' },
  { path: '/signin', component: () => import('./views/SignInView.vue'), meta: { public: true } },
  { path: '/about', component: () => import('./views/AboutView.vue'), meta: { public: true } },
  { path: '/profile', component: () => import('./views/ProfileView.vue'), meta: { noProfile: true } },
  { path: '/cabinet', component: () => import('./views/CabinetView.vue') },
  { path: '/setup', component: () => import('./views/SetupView.vue') },
  { path: '/reference', component: () => import('./views/ReferenceView.vue') },
  { path: '/session', component: () => import('./views/SessionView.vue'), meta: { training: true } },
  { path: '/results', component: () => import('./views/ResultsView.vue'), meta: { results: true } },
  { path: '/:pathMatch(.*)*', redirect: '/cabinet' },
]

export const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

router.beforeEach(async (to, from) => {
  const app = useAppStore()
  const training = useTrainingStore()
  await app.init()

  // Leaving a running training (browser back, a link): it is lost, so ask first.
  if (from.meta.training && training.active && !to.meta.results && !to.meta.training) {
    if (!window.confirm('Поточне тренування буде перервано без збереження. Вийти?')) return false
    training.stopTimer()
    training.$reset()
  }

  if (to.path === '/signin' && app.signedIn) return '/cabinet'
  if (to.meta.public) return true
  if (!app.signedIn) return '/signin'
  if (!app.profile && !to.meta.noProfile) return '/profile'
  if (to.meta.training && !training.active) return '/cabinet'
  if (to.meta.results && !training.finished) return '/cabinet'
  return true
})
