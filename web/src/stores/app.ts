// Who is signed in, their profile and their finished trainings (all from the cloud).

import { defineStore } from 'pinia'
import * as api from '../cloud/api'
import type { Profile } from '../core/profiles'
import type { SessionResult } from '../core/types'

export const useAppStore = defineStore('app', {
  state: () => ({
    ready: false,
    email: null as string | null,
    userId: null as string | null,
    profile: null as Profile | null,
    results: [] as SessionResult[],
    streak: 0,
    pending: 0,
    historyError: null as string | null,
    loadingHistory: false,
  }),
  getters: {
    signedIn: (s) => !!s.userId,
  },
  actions: {
    /** Restores the browser's sign-in session and the profile (once, before the first screen). */
    async init() {
      if (this.ready) return
      try {
        const session = await api.currentSession()
        if (session) await this.afterSignIn(session.user.id, session.user.email ?? null)
      } catch {
        /* offline or expired: the sign-in screen handles it */
      } finally {
        this.ready = true
      }
    },

    async afterSignIn(userId: string, email: string | null) {
      this.userId = userId
      this.email = email
      this.profile = await api.fetchProfile()
      if (this.profile) void this.refresh()
    },

    setProfile(p: Profile) {
      this.profile = p
    },

    /** Sends waiting trainings, then reloads history and the streak. */
    async refresh() {
      if (!this.profile) return
      this.loadingHistory = true
      this.historyError = null
      try {
        this.pending = await api.flushOutbox().catch(() => api.pendingCount())
        const [results, streak] = await Promise.all([api.fetchHistory(this.profile.id), api.fetchStreak(this.profile.id)])
        this.results = results
        this.streak = streak
      } catch (e) {
        this.historyError = String((e as Error)?.message ?? e)
      } finally {
        this.loadingHistory = false
      }
    },

    /** A training finished on this device: show it at once, the cloud copy comes with the next refresh. */
    addLocalResult(r: SessionResult) {
      if (!this.results.some((x) => x.id === r.id)) this.results = [...this.results, r]
    },

    async signOut() {
      await api.signOut()
      this.$reset()
      this.ready = true
    },

    async deleteAccount() {
      await api.deleteAccount()
      this.$reset()
      this.ready = true
    },
  },
})
