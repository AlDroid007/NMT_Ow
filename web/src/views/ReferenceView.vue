<script setup lang="ts">
// «Програми та шкала 100–200»: official structure of every subject and its conversion scale.
import { IonBackButton, IonButtons, IonContent, IonHeader, IonPage, IonTitle, IonToolbar } from '@ionic/vue'
import { ref } from 'vue'
import { conversionTable, SUBJECTS_CONFIG, SUBJECTS_ORDER } from '../core/config'
const open = ref<string | null>(null)
</script>

<template>
  <ion-page>
    <ion-header>
      <ion-toolbar>
        <ion-buttons slot="start"><ion-back-button default-href="/setup" text="Назад" /></ion-buttons>
        <ion-title>Програми та шкала 100–200</ion-title>
      </ion-toolbar>
    </ion-header>
    <ion-content class="ion-padding">
      <div class="page">
        <p class="nmt-muted">Структура НМТ і чинні програми (2022–2026). Натисни на предмет, щоб побачити шкалу переведення балів.</p>
        <section v-for="sid in SUBJECTS_ORDER" :key="sid" class="nmt-card">
          <button type="button" class="title" @click="open = open === sid ? null : sid">
            <b>{{ SUBJECTS_CONFIG[sid].name }}</b>
            <span class="nmt-muted">({{ SUBJECTS_CONFIG[sid].mandatory ? 'Обов’язковий' : 'За вибором' }})</span>
            <span class="chev">{{ open === sid ? '▲' : '▼' }}</span>
          </button>
          <div class="meta">Завдань: {{ SUBJECTS_CONFIG[sid].total_tasks }} | Макс. бал: {{ SUBJECTS_CONFIG[sid].max_score }} | Поріг «склав»: {{ SUBJECTS_CONFIG[sid].threshold }} (100 б.)</div>
          <div class="meta">Програма: {{ SUBJECTS_CONFIG[sid].program_order }}</div>
          <div class="meta">Форми: {{ SUBJECTS_CONFIG[sid].structure }}</div>
          <div v-if="open === sid" class="scale">
            <span v-for="[raw, nmt] in conversionTable(sid)" :key="raw"><b>{{ raw }}</b> → {{ nmt }}</span>
          </div>
        </section>
      </div>
    </ion-content>
  </ion-page>
</template>

<style scoped>
.page { max-width: 820px; margin: 0 auto; display: grid; gap: 10px; padding-bottom: 24px; }
.title { display: flex; gap: 8px; align-items: baseline; width: 100%; background: none; border: 0; padding: 0; font: inherit; color: inherit; text-align: left; font-size: 17px; cursor: pointer; }
.chev { margin-left: auto; color: var(--nmt-muted); font-size: 12px; }
.meta { font-size: 14px; margin-top: 4px; line-height: 1.4; }
.scale { display: grid; grid-template-columns: repeat(auto-fill, minmax(84px, 1fr)); gap: 4px 10px; margin-top: 10px; font-size: 14px; }
</style>
