# ShelfTalk

Учебный каталог книг на Django REST Framework, PostgreSQL и Vue 3 + TypeScript. Читатель
входит по email, ставит книге оценку от 1 до 10 и пишет один отзыв на книгу; свой отзыв
можно отредактировать или удалить. Каталог книг наполняется через Django Admin — проект
про отзывы и рейтинги, а не про самостоятельную загрузку книг пользователями.

Сделан как учебный проект: показать полный цикл SPA + REST API + PostgreSQL с
JWT-аутентификацией, без лишней инфраструктуры (без очередей, кеша и внешних
интеграций).

> **TODO:** скриншоты каталога и страницы книги. В репозитории их пока нет — добавить
> `docs/screenshots/` и вставить сюда `![Каталог](docs/screenshots/home.png)`.

## Возможности

- Каталог книг с названием, автором, годом издания и описанием.
- Средний рейтинг и число отзывов у каждой книги считаются на сервере.
- Регистрация и вход по email, сессия — на JWT (access + refresh токены).
- Один отзыв (оценка 1–10 и текст) от пользователя на книгу; свой отзыв можно менять и
  удалять.
- Поиск по названию и автору на странице каталога.
- Интерфейс на английском и русском языке с переключателем — собственная реализация i18n
  без внешних библиотек (`frontend/src/i18n/`).
- Django Admin для управления книгами, пользователями и модерации отзывов.

## Стек технологий

| Слой        | Технологии                                                                                                |
| ----------- | --------------------------------------------------------------------------------------------------------- |
| Backend     | Django 5, Django REST Framework, djangorestframework-simplejwt, django-cors-headers, PostgreSQL (psycopg) |
| Frontend    | Vue 3 (Composition API, `<script setup>`), TypeScript, Vite, Vue Router, Pinia, axios                     |
| Инструменты | ruff (backend), ESLint + typescript-eslint + eslint-plugin-vue, Prettier                                  |

Подробный разбор — в [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Быстрый старт

Требования: Python 3.12+, Node.js `^20.19.0` или `>=22.12.0`, запущенный PostgreSQL 14+.
Подробная версия этого раздела, включая Windows и таблицу переменных окружения, —
[docs/SETUP.md](docs/SETUP.md).

### Backend

Из корня проекта (если `.env` уже настроен, не копируйте его заново):

```sh
cp .env.example .env
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

В Windows: `python -m venv .venv` и `.venv\Scripts\Activate.ps1`.

В корневом `.env` укажите свои `POSTGRES_*` и `DJANGO_SECRET_KEY`. Ключ можно
сгенерировать командой ниже и вставить в `.env` в одинарных кавычках:

```sh
python -c \
  "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Если базы ещё нет, создайте роль и базу; пароль роли укажите в `.env`:

```sh
createuser -h localhost -U postgres --pwprompt --createdb shelftalk
createdb -h localhost -U postgres --owner=shelftalk shelftalk
```

Затем из `backend`:

```sh
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_books
python manage.py runserver
```

Admin: http://localhost:8000/admin/. `seed_books` добавляет восемь книг без дублей.

### Frontend

В другом терминале, из корня проекта:

```sh
cd frontend
npm install
npm run dev
```

Сайт: http://localhost:5173. Оба приложения читают один корневой `.env`.

## Пример использования

После `createsuperuser` и `seed_books` откройте http://localhost:5173, нажмите «Join
ShelfTalk» и зарегистрируйтесь, затем войдите и оставьте отзыв любой книге из каталога.
То же самое — через API напрямую:

```sh
# Регистрация
curl http://localhost:8000/api/auth/register/ \
  -H 'Content-Type: application/json' \
  -d '{"email":"reader@example.com","display_name":"Reader","password":"A-good-book-2026!"}'

# Вход — получаем access и refresh токены
curl http://localhost:8000/api/auth/login/ \
  -H 'Content-Type: application/json' \
  -d '{"email":"reader@example.com","password":"A-good-book-2026!"}'

# Отзыв на книгу с id=1 (access-токен из ответа выше)
curl http://localhost:8000/api/books/1/reviews/ \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer <access_token>' \
  -d '{"rating":8,"text":"I really enjoyed this book."}'
```

Полное описание всех эндпоинтов — в [docs/API.md](docs/API.md).

## Запуск тестов

Backend (нужно право `CREATEDB` у PostgreSQL-пользователя):

```sh
cd backend
python manage.py test
```

24 теста покрывают регистрацию, JWT-аутентификацию, права на отзывы и ограничения БД —
подробнее в [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md#тесты).

Frontend-тестов в проекте пока нет (см. [docs/TODO.md](docs/TODO.md)); есть проверка
типов и сборка:

```sh
cd frontend
npm run build
```

## Проверки и форматирование

Из `backend`, с активированным virtualenv:

```sh
ruff check .
ruff format --check .
python manage.py check
python manage.py test
```

Для автоисправления: `ruff check --fix .` и `ruff format .`.

Из `frontend`:

```sh
npm run lint
npm run format:check
npm run build
```

Для автоисправления: `npm run lint:fix` и `npm run format`. Сборка включает проверку
TypeScript. Что именно проверяет каждая команда — в
[docs/DEVELOPMENT.md](docs/DEVELOPMENT.md#стиль-кода-и-инструменты).

## Структура проекта

```
ShelfTalk/
├── backend/                    Django-проект
│   ├── config/                 Настройки, корневые маршруты, WSGI
│   ├── accounts/                Пользователь по email, регистрация, JWT-логин
│   │   ├── models.py            Кастомная модель User
│   │   ├── serializers.py       Регистрация, логин, профиль
│   │   ├── views.py             RegisterView, CurrentUserView
│   │   └── tests.py             Тесты аутентификации
│   ├── books/                   Каталог книг и отзывы
│   │   ├── models.py            Book, Review
│   │   ├── serializers.py       Сериализация книг и отзывов
│   │   ├── views.py             Список/деталь книги, CRUD отзывов
│   │   ├── permissions.py       IsReviewOwner
│   │   ├── management/commands/seed_books.py  Демо-данные
│   │   └── tests.py             Тесты каталога и отзывов
│   ├── manage.py
│   ├── requirements.txt         Зависимости
│   └── requirements-dev.txt     + ruff
├── frontend/                    Vue 3 + TypeScript SPA
│   └── src/
│       ├── views/                Страницы (каталог, книга, логин, регистрация)
│       ├── components/           AppNavbar, BookCard, ReviewItem
│       ├── api/                  Обёртки над эндпоинтами + общий axios-клиент
│       ├── stores/auth.ts        Pinia-стор текущего пользователя
│       ├── i18n/                 Собственная интернационализация (en/ru)
│       ├── router/               Маршруты vue-router
│       └── types/                TypeScript-типы, зеркалящие API
├── docs/                        Архитектура, установка, API, модель данных, разработка
├── .env.example                 Шаблон переменных окружения
├── CHANGELOG.md
└── LICENSE
```

Подробное назначение каждого модуля — в [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Документация

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — компоненты, поток данных, ключевые
  решения
- [docs/SETUP.md](docs/SETUP.md) — установка по шагам, переменные окружения, частые
  проблемы
- [docs/API.md](docs/API.md) — все эндпоинты с примерами запросов и ответов
- [docs/DATA_MODEL.md](docs/DATA_MODEL.md) — сущности, поля, ER-диаграмма
- [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) — стиль кода, тесты, git-процесс
- [docs/TODO.md](docs/TODO.md) — известные ограничения и открытые вопросы
- [CHANGELOG.md](CHANGELOG.md) — история изменений
- [CONTRIBUTING.md](CONTRIBUTING.md) — как вносить изменения

## Известные ограничения

- JWT хранится в `localStorage` для простоты учебного проекта. Для production стоит
  отдельно рассмотреть HttpOnly cookies и защиту токенов.
- Ошибки от backend не локализуются вслед за интерфейсом (см.
  [docs/TODO.md](docs/TODO.md)).
- Каталог `/api/books/` не пагинирован — рассчитан на небольшой каталог книг.
- Нет восстановления пароля и ограничения частоты запросов на вход/регистрацию.

Полный список — в [docs/TODO.md](docs/TODO.md).

## Лицензия и контакты

Лицензия: [MIT](LICENSE). Репозиторий и issues:
[github.com/ZakirovRuzil/ShelfTalk](https://github.com/ZakirovRuzil/ShelfTalk).
