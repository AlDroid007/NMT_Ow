<script setup lang="ts">
import { IonBackButton, IonButtons, IonContent, IonHeader, IonPage, IonTitle, IonToolbar } from '@ionic/vue'
import OwlBanner from '../components/OwlBanner.vue'
import { APP_TITLE, APP_VERSION, PRIVACY_URL } from '../config'
import { bankSize } from '../core/config'
import { generatorCount } from '../core/generators'
</script>

<template>
  <ion-page>
    <ion-header>
      <ion-toolbar>
        <ion-buttons slot="start"><ion-back-button default-href="/cabinet" text="Назад" /></ion-buttons>
        <ion-title>Про програму</ion-title>
      </ion-toolbar>
    </ion-header>
    <ion-content class="ion-padding">
      <div class="page">
        <OwlBanner :title="APP_TITLE" :text="`Версія ${APP_VERSION}`" :size="84" />
        <section class="nmt-card">
          <ul>
            <li>Усі 12 предметів НМТ (програми 2022–2026 рр.)</li>
            <li>Вбудовано {{ bankSize() }} завдань та {{ generatorCount() }} генераторів</li>
            <li>Багаторівневі підказки Сови-Лізи (рівні 1–10)</li>
            <li>Схожий приклад після кожної помилки та робота над помилками</li>
            <li>Особистий кабінет: рівень, цілі, графік, слабкі теми та історія</li>
            <li>Хмарне збереження (вхід кодом із пошти) — на телефоні й комп’ютері</li>
          </ul>
          <p><a :href="PRIVACY_URL" target="_blank" rel="noopener">Політика конфіденційності</a></p>
        </section>
      </div>
    </ion-content>
  </ion-page>
</template>

<style scoped>
.page { max-width: 640px; margin: 0 auto; display: grid; gap: 14px; }
li { margin: 6px 0; line-height: 1.4; }
</style>
