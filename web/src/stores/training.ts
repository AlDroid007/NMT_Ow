// The running training: plan, position, timer and the owl chat (ports the state of the desktop
// session, drill and results screens).

import { defineStore } from 'pinia'
import * as api from '../cloud/api'
import {
  blockScore, buildMistakeDrillPlan, buildSectionPlan, buildSessionPlan, buildSessionResult, evaluateAnswer,
  formatResultsReport, generateIdenticalDrill, isEmptyAnswer, nowIso, recordAnswer, recordHint,
} from '../core/engine'
import { build10Hints } from '../core/hints'
import type { Plan, SessionResult, StudentAnswer, Task } from '../core/types'
import { useAppStore } from './app'

export type Mood = 'idle' | 'thinking' | 'happy' | 'explain'

export interface ChatMessage {
  who: 'student' | 'tutor' | 'err'
  title: string
  text: string
  tone?: 'ok' | 'hint' | 'rule'
}

export interface DrillState {
  source: Task
  task: Task
  used: string[]
  hints: string[]
  hintLevel: number
  feedback: { text: string; tone: 'ok' | 'err' | 'hint' } | null
  answer: StudentAnswer | null
  key: number
}

export interface StartOptions {
  plan: Plan
  subjects: string[]
  lengthMode: string
  tutorMode: boolean
  mistakeDrill?: boolean
  focusSection?: string | null
  seconds: number
}

let timerId: ReturnType<typeof setInterval> | null = null
let drillKey = 0

export const useTrainingStore = defineStore('training', {
  state: () => ({
    active: false,
    plan: [] as Plan,
    blockIdx: 0,
    qIdx: 0,
    tutorMode: true,
    lengthMode: 'quick',
    mistakeDrill: false,
    focusSection: null as string | null,
    sessionId: '',
    startedAt: '',
    seconds: 0,
    // per task on screen
    answer: null as StudentAnswer | null,
    answerKey: 0,
    hints: [] as string[],
    hintLevel: 0,
    chat: [] as ChatMessage[],
    mood: 'idle' as Mood,
    status: '',
    drill: null as DrillState | null,
    // after the finish
    finished: false,
    report: '',
    result: null as SessionResult | null,
    saved: null as 'sent' | 'queued' | 'empty' | null,
  }),
  getters: {
    block: (s) => s.plan[s.blockIdx],
    question(): Task | undefined {
      return this.block?.questions[this.qIdx]
    },
    score(): [number, number] {
      return this.block ? blockScore(this.block) : [0, 0]
    },
    alreadyAnswered(): boolean {
      return !!this.block && this.qIdx in this.block.answers
    },
    hasMistakes: (s) => s.plan.some((b) => b.mistakes.length > 0),
  },
  actions: {
    /** Registers the training on the server, then opens it. Throws when the server or network says no. */
    async begin(o: StartOptions) {
      const app = useAppStore()
      if (!app.profile) throw new Error('Немає профілю.')
      if (!o.plan.length || !o.plan.some((b) => b.questions.length)) throw new Error('Для цього вибору поки немає завдань.')
      const sessionId = crypto.randomUUID()
      const startedAt = nowIso()
      const res = await api.beginSession({
        sessionId, profileId: app.profile.id, subjects: o.subjects, lengthMode: o.lengthMode, tutorMode: o.tutorMode,
        mistakeDrill: o.mistakeDrill, focusSection: o.focusSection,
      })
      if (res && res.allowed === false) throw new Error(String(res.message || 'Зараз розпочати тренування не можна.'))
      this.$reset()
      Object.assign(this, {
        active: true, plan: o.plan, tutorMode: o.tutorMode, lengthMode: o.lengthMode, mistakeDrill: !!o.mistakeDrill,
        focusSection: o.focusSection ?? null, sessionId, startedAt, seconds: o.seconds,
      })
      this.loadQuestion()
      this.startTimer()
    },

    async beginRegular(subjects: string[], lengthMode: string, tutorMode: boolean) {
      await this.begin({ plan: buildSessionPlan(subjects, lengthMode), subjects, lengthMode, tutorMode, seconds: subjects.length * 3600 })
    },

    async beginFocus(subject: string, section: string) {
      const plan = buildSectionPlan(subject, section, 8)
      if (!plan.length) throw new Error('Для цієї теми поки немає завдань.')
      await this.begin({ plan, subjects: [subject], lengthMode: 'focus', tutorMode: true, focusSection: section, seconds: 1800 })
    },

    async beginMistakeDrill() {
      const plan = buildMistakeDrillPlan(this.plan)
      if (!plan.length) return
      const lengthMode = this.lengthMode
      await this.begin({ plan, subjects: plan.map((b) => b.subject), lengthMode, tutorMode: true, mistakeDrill: true, seconds: 1800 })
    },

    startTimer() {
      if (timerId) clearInterval(timerId)
      timerId = setInterval(() => {
        if (!this.active) return
        if (this.seconds > 0) this.seconds -= 1
      }, 1000)
    },

    stopTimer() {
      if (timerId) clearInterval(timerId)
      timerId = null
    },

    say(who: ChatMessage['who'], title: string, text: string, tone?: ChatMessage['tone']) {
      this.chat.push({ who, title, text, tone })
    },

    loadQuestion() {
      const q = this.question
      if (!q) return
      this.answer = null
      this.answerKey += 1
      this.hints = build10Hints(q)
      this.hintLevel = 0
      this.chat = []
      this.drill = null
      this.mood = 'idle'
      if (this.tutorMode) {
        this.status = 'Уважно прочитай умову. Якщо застрягнеш — відкривай підказки по кроках (1 → 10)!'
        this.say('tutor', '🦉 Сова-Ліза:',
          `Ми на завданні №${this.qIdx + 1} (${q.section}). ` +
          'Спробуй розв’язати самостійно або натисни «Підказка (1/10)» — я проведу тебе крок за кроком від легкого натяку до повної розповіді!')
      } else {
        this.status = 'Режим іспиту: фіксую твої відповіді. Після фінішу розберемо кожну помилку!'
        this.say('tutor', '⏱ Режим іспиту:',
          'Відповідай на завдання блоку. Детальний розбір помилок та опрацювання ідентичних прикладів будуть доступні після завершення.')
      }
    },

    /** Counts an answer chosen but not checked when the student leaves the task (scored quietly). */
    capturePending() {
      const block = this.block
      if (!block || this.qIdx in block.answers || isEmptyAnswer(this.answer)) return
      const [ok, pts] = evaluateAnswer(block.questions[this.qIdx], this.answer!)
      block.answers[this.qIdx] = this.answer!
      block.points[this.qIdx] = pts
      recordAnswer(block, this.qIdx, ok, pts, false, this.hintLevel)
      if (!ok && !block.mistakes.includes(this.qIdx)) block.mistakes.push(this.qIdx)
    },

    switchBlock(i: number) {
      this.capturePending()
      this.blockIdx = i
      this.qIdx = 0
      this.loadQuestion()
    },

    goTo(i: number) {
      this.capturePending()
      this.qIdx = i
      this.loadQuestion()
    },

    /** Returns false when this was the last task (the screen then finishes). */
    next(): boolean {
      this.capturePending()
      if (this.qIdx + 1 < this.block.questions.length) {
        this.qIdx += 1
      } else if (this.blockIdx + 1 < this.plan.length) {
        this.blockIdx += 1
        this.qIdx = 0
      } else {
        return false
      }
      this.loadQuestion()
      return true
    },

    showHint(level: number) {
      const lvl = Math.max(1, Math.min(10, Math.trunc(level)))
      if (lvl > this.hintLevel) {
        const start = this.hintLevel + 1
        for (let cur = start; cur <= lvl; cur++) recordHint(this.block, this.qIdx, cur)
        this.say('student', '🎓 Учень:', `Сова-Ліза, дай підказку рівня ${lvl}/10!`)
        for (let cur = start; cur <= lvl; cur++) {
          this.say('tutor', `🦉 Сова-Ліза • Підказка ${cur}/10:`, this.hints[cur - 1], cur === 10 ? 'ok' : 'hint')
        }
        this.hintLevel = lvl
      } else {
        this.say('tutor', `🦉 Сова-Ліза • Повтор підказки ${lvl}/10:`, this.hints[lvl - 1], lvl === 10 ? 'ok' : 'hint')
      }
      if (this.hintLevel < 10) {
        this.mood = 'thinking'
        this.status = `Підказка ${this.hintLevel}/10 відкрита! Якщо треба глибше — натисни наступний рівень.`
      } else {
        this.mood = 'explain'
        this.status = 'Ось повна розповідь і правило (10/10)! Тепер сміливо закріпимо на прикладі.'
      }
    },

    /** «Перевірити»: false when nothing is chosen yet. In exam mode the screen moves on by itself. */
    submit(): boolean {
      const block = this.block
      const q = this.question!
      if (isEmptyAnswer(this.answer)) return false
      const [ok, pts, uRepr, cRepr] = evaluateAnswer(q, this.answer!)
      block.answers[this.qIdx] = this.answer!
      block.points[this.qIdx] = pts
      recordAnswer(block, this.qIdx, ok, pts, true, this.hintLevel)
      if (!ok && !block.mistakes.includes(this.qIdx)) block.mistakes.push(this.qIdx)

      if (!this.tutorMode) {
        this.say('student', '🎓 Учень:', `Відповідь збережено: ${uRepr}`)
        return true
      }
      this.say('student', '🎓 Учень:', `Моя відповідь: ${uRepr}`)
      if (ok) {
        this.mood = 'happy'
        this.status = 'Браво! Абсолютно точно! Рухаймося далі з таким же темпом!'
        this.say('tutor', '🦉 Сова-Ліза:', `✅ Чудово! Абсолютно правильно (+${pts} б.).\n${q.solution ?? ''}`, 'ok')
      } else {
        this.mood = 'explain'
        this.status = 'Нічого страшного! Зараз усе просто поясню й попрактикуємося на ідентичному прикладі нижче.'
        this.say('err', '🦉 Сова-Ліза — є помилка! Нумо розберемо зрозуміло:',
          `Ти відповів(ла): ${uRepr}, а правильна відповідь: ${cRepr} (набрано ${pts} із ${q.max_points ?? 1} б.).`)
        this.say('tutor', '📘 Правило простими словами:', q.rule ?? '', 'rule')
        this.say('tutor', '🔍 Покроковий розбір саме цього завдання:', q.solution ?? '')
        this.newDrill(q, [q.prompt ?? ''])
      }
      return true
    },

    // --- identical example after a mistake ----------------------------------------------------

    newDrill(source: Task, used?: string[]) {
      const usedPrompts = used ?? this.drill?.used ?? [source.prompt ?? '']
      const task = generateIdenticalDrill(source, usedPrompts)
      this.drill = {
        source, task, used: [...usedPrompts, task.prompt ?? ''], hints: build10Hints(task), hintLevel: 0,
        feedback: null, answer: null, key: ++drillKey,
      }
    },

    drillHint() {
      const d = this.drill
      if (!d || d.hintLevel >= 10) return
      d.hintLevel += 1
      const lvl = d.hintLevel
      this.mood = 'thinking'
      this.say('tutor', `🦉 Сова-Ліза (до прикладу • ${lvl}/10):`, d.hints[lvl - 1], lvl === 10 ? 'ok' : 'hint')
      d.feedback = { text: `💡 Підказка ${lvl}/10:\n${d.hints[lvl - 1]}`, tone: 'hint' }
    },

    /** false when nothing is chosen yet. */
    drillSubmit(): boolean {
      const d = this.drill
      if (!d) return true
      if (isEmptyAnswer(d.answer)) return false
      const [ok, , uRepr, cRepr] = evaluateAnswer(d.task, d.answer!)
      this.block.drills_done += 1
      this.say('student', '🎓 Учень (ідентичний приклад):', `Моя відповідь: ${uRepr}`)
      if (ok) {
        this.mood = 'happy'
        this.status = 'Ура! Тепер ти точно знаєш це правило! Можеш тиснути «Далі →».'
        d.feedback = { text: `✅ Правильно («${uRepr}»)! ${d.task.solution ?? ''}`, tone: 'ok' }
        this.say('tutor', '🦉 Сова-Ліза:',
          `✅ Супер! «${uRepr}» — правильно!\n${d.task.solution ?? ''}\nТепер ти впевнено впораєшся з таким типом завдань на НМТ. Можемо рухатися далі (або натисни «Інший ↻» для ще одного тренування).`, 'ok')
      } else {
        this.mood = 'explain'
        this.status = 'Майже вийшло! Перевір розбір і спробуй ще один ідентичний приклад нижче.'
        this.say('err', '🦉 Сова-Ліза (перевірка схожого прикладу):',
          `Знову є неточність (${uRepr}). Правильна відповідь: ${cRepr}.\n🔍 Поглянь крок за кроком: ${d.task.solution ?? ''}\nСпробуймо ще один ідентичний приклад!`)
        this.newDrill(d.source)
      }
      return true
    },

    // --- finish ---------------------------------------------------------------------------------

    /** Scores the training, sends it to the cloud (or the outbox) and keeps the report. */
    async finish() {
      if (this.finished) return
      this.capturePending()
      this.stopTimer()
      this.active = false
      this.finished = true
      this.report = formatResultsReport(this.plan)
      if (!this.plan.some((b) => Object.keys(b.answers).length)) {
        this.saved = 'empty'
        return
      }
      const app = useAppStore()
      const result = buildSessionResult(this.plan, this.lengthMode, this.tutorMode, {
        mistakeDrill: this.mistakeDrill, focusSection: this.focusSection, startedAt: this.startedAt, sessionUid: this.sessionId,
      })
      this.result = result
      app.addLocalResult({ ...result, id: this.sessionId, created_at: result.finished_at })
      try {
        const sent = await api.submitSession(result, this.sessionId, app.profile!.id)
        this.saved = sent ? 'sent' : 'queued'
      } catch {
        this.saved = 'queued'
      }
      app.pending = api.pendingCount()
      if (this.saved === 'sent') void app.refresh()
    },
  },
})
