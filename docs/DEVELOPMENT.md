# Разработка

Как проверять код, запускать тесты и добавлять фичи. Установка окружения — в
[SETUP.md](SETUP.md), архитектура — в [ARCHITECTURE.md](ARCHITECTURE.md).

## Стиль кода и инструменты

| Слой              | Линтер                                                                                                         | Форматтер   | Конфиг                                                                                             |
| ----------------- | -------------------------------------------------------------------------------------------------------------- | ----------- | -------------------------------------------------------------------------------------------------- |
| Backend (Python)  | [ruff](https://docs.astral.sh/ruff/) (`select = ["E", "F", "I"]` — pycodestyle, pyflakes, сортировка импортов) | ruff format | [backend/ruff.toml](../backend/ruff.toml)                                                          |
| Frontend (TS/Vue) | ESLint (`@eslint/js` + `typescript-eslint` + `eslint-plugin-vue`)                                              | Prettier    | [frontend/eslint.config.js](../frontend/eslint.config.js), [.prettierrc.json](../.prettierrc.json) |

Договорённости, закреплённые в конфигах:

- 4 пробела отступа везде (`.prettierrc.json: tabWidth: 4`, `ruff.toml` не
  переопределяет стандартные 4 пробела Python).
- Максимальная длина строки 88 символов и в Python (`ruff.toml: line-length = 88`), и во
  frontend (`.prettierrc.json: printWidth: 88`).
- Одинарные кавычки и без `;` в TS/Vue
  (`.prettierrc.json: semi: false, singleQuote: true`).
- В `.vue`-файлах порядок блоков — `template` → `script` → `style`
  (`eslint.config.js: vue/block-order`).
- `curly: ['error', 'all']` — фигурные скобки обязательны даже для однострочных `if`.

## Проверки и форматирование

Из `backend`, с активированным virtualenv:

```sh
ruff check .
ruff format --check .
python manage.py check
python manage.py test
```

Автоисправление: `ruff check --fix .` и `ruff format .`.

Из `frontend`:

```sh
npm run lint
npm run format:check
npm run build
```

Автоисправление: `npm run lint:fix` и `npm run format`. `npm run build` сначала
прогоняет `vue-tsc --noEmit` (проверку типов), затем собирает проект — так же, как это
описано в [SETUP.md](SETUP.md#dev-и-prod-режимы).

`npm run format`/`format:check` форматируют весь репозиторий (`prettier --write ..`), а
не только `frontend/` — Prettier настроен как общий инструмент для проекта.

## Тесты

**Backend**: 24 теста в `backend/accounts/tests.py` и `backend/books/tests.py`
(`APITestCase` из DRF). Покрывают: регистрацию и нормализацию email, хеширование пароля,
login и JWT refresh, права доступа к отзывам (владелец/чужой/гость), валидацию рейтинга
и текста на уровне API и БД (`CheckConstraint`), агрегаты рейтинга книги,
идемпотентность `seed_books`, 404 и 405 в граничных случаях.

```sh
cd backend
python manage.py test
```

Для этой команды у PostgreSQL-пользователя нужно право `CREATEDB` (см.
[SETUP.md](SETUP.md#частые-проблемы)).

**Frontend**: тестов и тестового раннера в проекте пока нет — `frontend/package.json`
содержит только `lint`, `type-check` и `build`. Это отмечено как пробел в
[TODO.md](TODO.md).

## Как добавить фичу: пример по образцу существующего кода

Ниже — на что ориентироваться, если добавлять новый эндпоинт вида «список + создание»,
аналогичный отзывам.

1. **Модель** (`books/models.py` или новое приложение) — поля, `Meta.constraints` для
   инвариантов, которые должны держаться даже при гонке запросов (как
   `one_review_per_user_book` у `Review`).
2. **Миграция**: `python manage.py makemigrations <app>`.
3. **Сериализатор** (`books/serializers.py`) — какие поля отдаются и что вычисляется на
   сервере (`ReviewSerializer.author` берётся из `source="user"`, а не принимается от
   клиента).
4. **Право доступа**, если нужна проверка владения — по образцу
   `books/permissions.py: IsReviewOwner`.
5. **Вьюха** (`books/views.py`) — обычно `generics.ListCreateAPIView`/`RetrieveAPIView`
   из DRF; бизнес-правила — в `perform_create`/`get_queryset`, как у `BookReviewsView`.
6. **Маршрут** в `books/urls.py`, подключённом через `config/urls.py`.
7. **Тесты** в `books/tests.py` — по образцу уже существующих (публичный доступ, доступ
   гостя, доступ владельца/не владельца, граничные значения, поведение БД-constraint
   напрямую).
8. **Frontend**: типы в `frontend/src/types/index.ts`, функция запроса в
   `frontend/src/api/`, использование во `views/` или `components/`, новые строки — в
   `frontend/src/i18n/locales/en.ts` и `ru.ts` (оба словаря обязаны совпадать по ключам
   — проверяется TypeScript'ом, см. `frontend/src/i18n/types.ts`).
9. Прогнать проверки из раздела выше перед коммитом.

Добавление нового языка интерфейса — отдельный, более узкий процесс, описанный в
docstring [`frontend/src/i18n/index.ts`](../frontend/src/i18n/index.ts).

## Git-процесс и коммиты

Отдельного файла с правилами нет, но история проекта следует
[Conventional Commits](https://www.conventionalcommits.org/): `feat(scope): ...`,
`fix: ...`, `docs: ...`, `test: ...`, `refactor: ...`, `style: ...`, `chore: ...`.
Примеры из `git log`:

```
feat(auth): initialize Django with custom email users and JWT
feat(books): add catalog, owned reviews and demo data
test: cover authentication, review permissions and database constraints
fix: stabilize catalog order and pin verified backend dependencies
docs: document setup, API and release 1.0.0
```

Разработка ведётся в отдельных ветках (`feature/...`, `release/...`, `docs/...`) с
последующим Pull Request в `main`. Подробнее и короче — в
[CONTRIBUTING.md](../CONTRIBUTING.md).

## CI/CD

В проекте нет настроенного CI — папки `.github/workflows` (или аналогов для другой
системы CI) не существует. Проверки из раздела «Проверки и форматирование» запускаются
только вручную, локально, перед коммитом/PR.
