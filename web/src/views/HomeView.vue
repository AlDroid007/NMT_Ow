<script setup lang="ts">
import { IonContent, IonHeader, IonPage, IonTitle, IonToolbar } from '@ionic/vue'
import { APP_TITLE, APP_VERSION } from '../config'
</script>

<template>
  <ion-page>
    <ion-header>
      <ion-toolbar>
        <ion-title>{{ APP_TITLE }}</ion-title>
      </ion-toolbar>
    </ion-header>
    <ion-content class="ion-padding">
      <div class="nmt-card welcome">
        <img src="/owl.png" alt="" width="96" height="96" />
        <h1>Привіт! Я Сова-Ліза 🦉</h1>
        <p class="nmt-muted">Веб-версія тренажера НМТ готується. Версія {{ APP_VERSION }}.</p>
      </div>
    </ion-content>
  </ion-page>
</template>

<style scoped>
.welcome { max-width: 520px; margin: 24px auto; text-align: center; }
.welcome h1 { font-size: 24px; margin: 12px 0 4px; }
</style>
