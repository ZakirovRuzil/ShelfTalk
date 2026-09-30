# Установка и настройка

Подробная версия быстрого старта из [README.md](../README.md). Архитектура — в
[ARCHITECTURE.md](ARCHITECTURE.md), команды разработки — в
[DEVELOPMENT.md](DEVELOPMENT.md).

## Требования

- Python 3.12+ (в `backend/ruff.toml` указан `target-version = "py312"`)
- Node.js `^20.19.0` или `>=22.12.0` (см. `frontend/package.json: engines`)
- PostgreSQL 14+, запущенный локально
- Для запуска тестов backend: у PostgreSQL-пользователя должно быть право `CREATEDB`
  (Django создаёт отдельную тестовую БД на время прогона)

Различий в командах между macOS и Linux нет. Отличие для Windows отмечено отдельно в
шаге активации виртуального окружения.

## 1. Переменные окружения

Скопируйте пример и заполните своими значениями:

```sh
cp .env.example .env
```

`.env` лежит в корне репозитория и общий для backend и frontend
(`backend/config/settings.py` и `frontend/vite.config.ts: envDir: '..'` читают именно
его).

| Переменная             | Назначение                                                      | Обязательна                                                                      | Пример                                        |
| ---------------------- | --------------------------------------------------------------- | -------------------------------------------------------------------------------- | --------------------------------------------- |
| `DJANGO_SECRET_KEY`    | Ключ Django для подписи сессий, токенов и т.д.                  | Да, без запасного значения — `os.environ["DJANGO_SECRET_KEY"]`                   | `django-insecure-...`                         |
| `DJANGO_DEBUG`         | Режим отладки Django (подробные страницы ошибок)                | Нет, по умолчанию `False`                                                        | `True`                                        |
| `DJANGO_ALLOWED_HOSTS` | Список хостов через запятую, с которых Django принимает запросы | Нет, по умолчанию `localhost,127.0.0.1`                                          | `localhost,127.0.0.1`                         |
| `CORS_ALLOWED_ORIGINS` | Origin'ы фронтенда, которым разрешены CORS-запросы              | Нет, по умолчанию `http://localhost:5173,http://127.0.0.1:5173`                  | `http://localhost:5173,http://127.0.0.1:5173` |
| `POSTGRES_DB`          | Имя базы данных                                                 | Да, без запасного значения                                                       | `shelftalk`                                   |
| `POSTGRES_USER`        | Пользователь PostgreSQL                                         | Да, без запасного значения                                                       | `shelftalk`                                   |
| `POSTGRES_PASSWORD`    | Пароль пользователя PostgreSQL                                  | Да, без запасного значения                                                       | `change-me`                                   |
| `POSTGRES_HOST`        | Хост PostgreSQL                                                 | Нет, по умолчанию `localhost`                                                    | `localhost`                                   |
| `POSTGRES_PORT`        | Порт PostgreSQL                                                 | Нет, по умолчанию `5432`                                                         | `5432`                                        |
| `VITE_API_BASE_URL`    | Базовый URL API для фронтенда                                   | Нет, по умолчанию `http://localhost:8000/api` (см. `frontend/src/api/client.ts`) | `http://localhost:8000/api`                   |

Ключ `DJANGO_SECRET_KEY` можно сгенерировать так:

```sh
python -c \
  "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Вставьте результат в `.env` в одинарных кавычках.

## 2. База данных

Если базы ещё нет, создайте роль и саму базу (пароль роли должен совпадать с
`POSTGRES_PASSWORD` из `.env`):

```sh
createuser -h localhost -U postgres --pwprompt --createdb shelftalk
createdb -h localhost -U postgres --owner=shelftalk shelftalk
```

Флаг `--createdb` у роли нужен, чтобы `python manage.py test` мог создавать временную
тестовую базу.

## 3. Backend

Из корня проекта:

```sh
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

На Windows активация окружения другая:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

`requirements-dev.txt` подключает `requirements.txt` и добавляет `ruff` — этого
достаточно и для разработки, и для запуска приложения; отдельного prod-файла
зависимостей в проекте нет.

## Миграции и демо-данные

Из `backend`, с активированным окружением:

```sh
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_books
python manage.py runserver
```

- `migrate` — применяет две существующие миграции (`accounts`, `books`), см.
  [DATA_MODEL.md](DATA_MODEL.md#миграции).
- `createsuperuser` — спросит email, отображаемое имя (`display_name`) и пароль;
  понадобится для входа в Django Admin.
- `seed_books` — добавляет восемь демо-книг. Команду можно выполнять повторно: она не
  создаёт дублей и не перезаписывает уже изменённые книги (использует `get_or_create` по
  названию и автору).
- `runserver` — поднимает backend на `http://localhost:8000`. Admin: `/admin/`, API:
  `/api/`.

## 4. Frontend

В отдельном терминале, из корня проекта:

```sh
cd frontend
npm install
npm run dev
```

Сайт: `http://localhost:5173` (порт зафиксирован в `frontend/vite.config.ts`:
`server: { port: 5173, strictPort: true }` — если порт занят, Vite не переключится на
другой сам, а завершится с ошибкой).

## Dev и prod режимы

В проекте нет отдельных prod-скриптов или Dockerfile — только то, что даёт сам
Django/Vite:

- **Dev**: `DJANGO_DEBUG=True`, `python manage.py runserver`, `npm run dev` — именно так
  описано выше.
- **Prod-сборка frontend**: `npm run build` (в `frontend/`) выполняет проверку типов
  (`vue-tsc --noEmit`) и собирает статические файлы через Vite; `npm run preview` —
  локально посмотреть результат сборки.
- **Prod-режим backend**: поставить `DJANGO_DEBUG=False` (значение по умолчанию, если
  переменная не задана), заполнить реальный `DJANGO_ALLOWED_HOSTS` и
  `DJANGO_SECRET_KEY`, собрать статику Django (`STATIC_ROOT = BASE_DIR / "staticfiles"`
  в `config/settings.py`) командой `python manage.py collectstatic`. Сам WSGI-сервер
  (gunicorn/uwsgi), реверс-прокси и контейнеризация в проект не входят — этот раздел
  учебный, для реального деплоя нужно выбрать и настроить их отдельно.

## Частые проблемы

| Симптом                                                                                                 | Причина                                                     | Решение                                                                                                 |
| ------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| `KeyError: 'DJANGO_SECRET_KEY'` (или `POSTGRES_DB`/`POSTGRES_USER`/`POSTGRES_PASSWORD`) при `runserver` | Не скопирован `.env` или не заполнено обязательное значение | Выполнить `cp .env.example .env` и заполнить переменные из таблицы выше                                 |
| Frontend не может получить данные, в консоли браузера ошибка CORS                                       | Origin фронтенда не входит в `CORS_ALLOWED_ORIGINS`         | Проверить, что frontend открыт на `http://localhost:5173` (или добавить свой origin в `.env`)           |
| `python manage.py test` падает с ошибкой прав на создание базы                                          | У `POSTGRES_USER` нет `CREATEDB`                            | Пересоздать роль с `--createdb` (см. шаг 2) или выполнить `ALTER ROLE shelftalk CREATEDB;`              |
| `EADDRINUSE` / Vite завершается при `npm run dev`                                                       | Порт 5173 уже занят другим процессом                        | Освободить порт 5173 (в `vite.config.ts` включён `strictPort`, поэтому Vite не выберет другой порт сам) |
| При запросах с фронта приходит 401 сразу после логина                                                   | Не совпадает `VITE_API_BASE_URL` с адресом backend          | Проверить `.env` и что `python manage.py runserver` слушает `localhost:8000`                            |

## Проверки перед коммитом

Полный список и назначение каждой проверки — в
[DEVELOPMENT.md](DEVELOPMENT.md#проверки-и-форматирование).
