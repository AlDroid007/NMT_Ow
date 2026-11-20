# Веб-версия (и будущее iOS-приложение)

> 🚧 В работе. Этот документ дополняется по мере готовности шагов.

Главный клиент НМТ Сова-Репетитор: веб-приложение в папке `web/`. Им удобно пользоваться и
тестировать с любого устройства, а через **Capacitor** тот же код собирается в приложение для iPhone
и публикуется в App Store. План — [`ROADMAP.md`](ROADMAP.md), этапы 2 и 3.

## Стек

| | |
|---|---|
| Интерфейс | Vue 3 + TypeScript, **Ionic Vue** (компоненты в стиле iOS), vue-router, Pinia |
| Сборка | Vite; тесты — vitest |
| Облако | Supabase через `@supabase/supabase-js`: вход кодом из почты, таблицы и функции из [`DATABASE.md`](DATABASE.md) |
| Хостинг | Cloudflare Pages — статический сайт, бесплатно, превью-ссылка на каждую ветку |
| iOS (этап 3) | Capacitor: `web/` → проект Xcode → TestFlight → App Store |

Сервера у веб-версии нет: браузер ходит в Supabase напрямую с публичным ключом, а доступ к данным
ограничивают правила RLS в базе (ученик видит только своё).

## Структура `web/`

```
web/
├── src/core/        ← логика тренажёра без интерфейса, порт nmt_tutor/ 1:1:
│                      config (предметы, шкалы 100–200), engine (план, проверка, баллы, отчёт),
│                      hints (10 уровней), generators/* (по предметам), cabinet (цифры кабинета)
├── src/core/data/   ← задания и шкалы (JSON, перенесены из nmt_tutor/ один раз)
├── src/cloud/       ← вход, профиль, begin_session / submit_session, история, серия дней
├── src/views/       ← экраны: вход, профиль, кабинет, выбор предметов, тренировка, похожий пример, итоги, довідка
├── src/components/  ← Сова, вопрос, подсказки, график, плитки предметов
└── tests/           ← vitest: паритет с Python на эталонах + логика генераторов
```

## Чем отличается от десктопа

- Только со входом в облако: одна почта = один профиль. Нет локальных профилей и PIN.
- Нет своих банков заданий, ярлыка Windows, локальной зашифрованной базы.
- Вместо «Вийти з програми» — «Вийти з акаунта».
- Профиль, созданный на компьютере, открывается в вебе со всей историей (облако общее).

## Десктоп заморожен

`nmt_tutor/` (Python + Tkinter) больше не получает новых функций. Он остаётся эталоном: тесты веба
сверяют ответы TypeScript-логики с Python на одних и тех же заданиях. Когда веб покроет всё, десктоп
уйдёт в архивную ветку (ROADMAP, этап 8).

## Запуск и тесты

Нужен Node.js 22 (`node -v`).

```bash
cd web
npm install          # один раз
npm run dev          # http://localhost:5173 — открывается и с телефона в той же сети: npm run dev -- --host
npm test             # vitest
npm run build        # проверка типов + сборка в web/dist
```

Адрес Supabase и публичный ключ лежат в `web/src/config.ts` (те же, что в `nmt_tutor/cloud_config.json`);
их можно переопределить переменными `VITE_SUPABASE_URL` и `VITE_SUPABASE_KEY`.

## Деплой на Cloudflare Pages (один раз)

1. Зарегистрируйся на https://dash.cloudflare.com (бесплатно).
2. **Workers & Pages → Create → Pages → Connect to Git** → GitHub → репозиторий `AlDroid007/NMT_Ow`.
3. Настройки сборки:

   | Поле | Значение |
   |---|---|
   | Project name | `nmt-sova` (будет адрес `nmt-sova.pages.dev`) |
   | Production branch | `main` |
   | Framework preset | `Vue` (или None) |
   | Root directory | `web` |
   | Build command | `npm run build` |
   | Build output directory | `dist` |
   | Environment variable | `NODE_VERSION` = `22` |

4. **Save and Deploy.** Дальше Cloudflare сам собирает сайт при каждом пуше:
   - `main` → основной адрес `https://nmt-sova.pages.dev`;
   - любая другая ветка → превью `https://<ветка>.nmt-sova.pages.dev` (например, `feature-web-app.nmt-sova.pages.dev`) —
     так проверяем работу до мержа, в том числе на iPhone.
5. Свой домен — позже: **Custom domains** в проекте Pages.

Неизвестные адреса (например, `/cabinet` при обновлении страницы) Cloudflare отдаёт как `index.html`
(режим SPA), поэтому роутер работает без дополнительных настроек.

### Supabase для веба
- **Authentication → URL Configuration → Site URL**: `https://nmt-sova.pages.dev`. Вход по 6-значному коду
  не использует ссылки-редиректы, но Site URL лучше выставить.
- CORS настраивать не нужно: Supabase принимает запросы с любого сайта, доступ решают правила RLS.
