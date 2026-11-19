# Облачная база данных (Supabase / PostgreSQL)

SQL: [`supabase/migrations/20261118000000_cloud_sync.sql`](../supabase/migrations/20261118000000_cloud_sync.sql).
Как создать проект и применить схему — [`CLOUD_SETUP.md`](CLOUD_SETUP.md).

## Схема

```
auth.users (аккаунт Supabase: id, email)
   │ 1:1
profiles ──1:1── profile_meta            (data: серия дней, медали… | client_data: настройки приложения)
   │
   ├──1:N── sessions ──1:N── session_subjects   (итог по предмету)
   │            ├──────1:N── session_answers    (каждое задание)
   │            └──────1:N── hint_events        (каждая открытая подсказка)
   │
   └──1:N── profile_subject_stats         (накопления по предмету, считает сервер)

Покупки (заполнятся на этапе покупок):
products ── purchases ──┬── entitlements     (что открыто и до какого времени)
                        └── session_credits  (журнал доп. тренировок: +N / −1)
app_settings  (правила без обновления приложения)      admins  (кто видит всё)
```

## Кто что может

| | Ученик | Админ | Без входа |
|---|---|---|---|
| `profiles` | читает и правит свой | читает все | — |
| `profile_meta.client_data` | читает и правит свой | читает все | — |
| `profile_meta.data`, `sessions`, `session_*`, `hint_events`, `profile_subject_stats` | только читает свои | читает все | — |
| `purchases`, `entitlements`, `session_credits` | только читает свои | читает все | — |
| `app_settings`, `products` | читает | читает | — |
| `admins` | — | — (только панель Supabase) | — |

Тренировки, ответы, статистику и серию дней записывают **только серверные функции**, поэтому
подделать их через API нельзя. Ученик пишет напрямую только свой профиль и `client_data`.
Каждая строка имеет `owner` — id аккаунта, на нём построены все правила (RLS).

## Таблицы

### `profiles` — ученик
| колонка | тип | |
|---|---|---|
| `id` | uuid PK | создаёт приложение, тот же id, что в локальной базе |
| `owner` | uuid → auth.users, уникальный | одна почта = один профиль |
| `name` | text, 1–40 символов | |
| `avatar` | jsonb | `{"kind": "emoji", "value": "🦉"}` |
| `subjects` | jsonb | `["ukrmova", "math", …]` |
| `targets` | jsonb | `{"math": 180}` — цель 100–200 |
| `exam_date` | date | |
| `created_at`, `updated_at` | timestamptz | `updated_at` ставит сервер |

PIN в облако не попадает.

### `profile_meta` — дополнительные данные профиля (JSON)
| колонка | | |
|---|---|---|
| `profile_id` | uuid PK → profiles | создаётся автоматически вместе с профилем |
| `data` | jsonb | **пишет только сервер**: `{"streak": {"current": 5, "best": 12, "last_day": "2026-11-19"}}`, дальше — медали, счётчики |
| `client_data` | jsonb | может писать приложение (настройки, флаги интерфейса) |

Новое поле добавляется без изменения таблицы — просто новым ключом в JSON. Награды, которые нельзя
подделать (медали за баллы), считаются на сервере и пишутся в `data`.

### `sessions` — тренировка
| колонка | | |
|---|---|---|
| `id` | uuid PK | создаёт приложение при старте |
| `profile_id` | → profiles | |
| `status` | `active` / `finished` | |
| `started_at` | timestamptz | **время сервера** при старте (`begin_session`) |
| `finished_at` | timestamptz | время окончания (с устройства, но не раньше начала и не позже «сейчас») |
| `length_mode` | `quick` / `medium` / `full` / `focus` | обычная 8 / 15 / полный формат / одна тема |
| `tutor_mode` | bool | с подсказками Совы (false — режим экзамена) |
| `mistake_drill` | bool | работа над ошибками |
| `focus_section` | text | тема для «Потренувати» |
| `subjects` | text[] | выбранные предметы |
| `imported` | bool | загружена позже без старта на сервере (старая история) |

Длительность = `finished_at − started_at`.

### `session_subjects` — итог по предмету
PK (`session_id`, `subject`): `earned` (набрано), `max_points`, `projected_raw` (в пересчёте на
официальный тест), `nmt_200` (100–200, null — ниже порога), `is_full` (полный формат НМТ или прогноз),
`drills_done` (разобрано похожих примеров с Совой).

### `session_answers` — каждое задание
PK (`session_id`, `subject`, `question_no`):
| колонка | |
|---|---|
| `task_id` | id задания из базы (`math_2026_20`) или `gen:<генератор>` для сгенерированных |
| `section` | тема задания — отсюда слабые темы |
| `qtype` | `single` / `matching` / `short` |
| `is_correct`, `points`, `max_points` | результат |
| `checked` | нажал «Перевірити» (true) или ушёл с выбранным ответом (false) |
| `max_hint_level` | до какого уровня подсказки дошёл перед ответом (0–10) |
| `answered_at` | когда |

### `hint_events` — каждая открытая подсказка
`session_id`, `subject`, `question_no`, `task_id`, `level` (1–10), `opened_at`. Если ученик сразу
открыл уровень 5, записываются уровни 1–5 (он увидел их все).

### `profile_subject_stats` — накопления (PK `profile_id` + `subject`)
`sessions_count`, `best_nmt`, `last_nmt`, `avg_nmt`, `level_nmt` (среднее за последние 3),
`answers_total`, `answers_correct`, `hints_opened`, `last_session_at`. Работа над ошибками в баллы не
входит. Пересчитывается **из исходных таблиц** при каждой сданной тренировке, поэтому не расходится с
ними; `recalc_stats()` пересчитывает всё заново (если поменялась формула).

### Покупки (пока пустые)
- `products` — каталог: `kind` (`session_pack` / `subject_pass` / `all_access`), `subject`, `duration`
  (`7 days`), `sessions_count`, id товаров в App Store и Google Play.
- `purchases` — проверенные покупки: магазин, `store_transaction_id` (уникален — одну покупку нельзя
  засчитать дважды), статус (`active` / `refunded`), ответ магазина.
- `entitlements` — доступ: `kind`, `subject` (null — все), `valid_from`, `valid_until`.
- `session_credits` — журнал доп. тренировок: `delta` (+3 покупка, −1 тренировка сверх лимита), причина.

### `app_settings`
Ключ → JSON: `day_timezone` (`Europe/Kyiv` — для серии дней и дневного лимита), `free_daily_sessions`
(null — без лимита), `free_subjects` (null — все бесплатные). Меняются в панели Supabase без обновления приложения.

## Серверные функции (API приложения)

| функция | что делает |
|---|---|
| `begin_session(id, profile, subjects, режим…)` | старт тренировки: проверяет профиль, создаёт `sessions` с серверным временем. С покупками здесь будут лимит и платные предметы. Повтор с тем же id безопасен |
| `submit_session(json)` | конец тренировки одним вызовом: итоги, ответы, подсказки → одна транзакция + пересчёт `profile_subject_stats` + серия дней. Тренировку без старта (старая история) создаёт с `imported = true`. Повтор безопасен |
| `recalc_stats(profile?)` | полный пересчёт накоплений (админ — любой/всех, ученик — свой) |
| `delete_my_account()` | удаляет аккаунт и всё его (требование App Store) |

Внутренние: `recalc_subject_stats`, `update_streak`, `is_admin`, `setting` — через API не вызываются.

## Представления для админки
- `admin_students` — по строке на ученика: тренировок всего, последняя, средний уровень, серия дней.
- `admin_sections` — по темам: ответов, ошибок, % верных, средний уровень подсказки.
- `admin_hint_levels` — для каждого предмета и уровня подсказки: сколько ответов и % верных.

Ученик через них видит только себя, админ — всех.

## Что хранится только на устройстве
Текстовые отчёты, свои банки заданий (их импорт сейчас скрыт), PIN, ключ шифрования.
Ответы и подсказки до сдачи тренировки лежат в зашифрованной локальной базе и уходят в облако
вызовом `submit_session` (если интернет пропал на финише — при следующей синхронизации).
