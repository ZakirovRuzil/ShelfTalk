# ShelfTalk
A simple book catalog and review platform built with Django, Vue 3 and PostgreSQL.

Учебный full-stack проект **1.0.0**: небольшой каталог книг, оценки от 1 до 10 и отзывы читателей. Каталог открыт всем; писать отзывы можно после входа. Книги добавляет администратор через Django Admin.

## Features

- Каталог, описание книги и поиск по названию/автору.
- Custom User без username, регистрация и вход по email.
- JWT authentication и обновление access token.
- Один отзыв на книгу от пользователя; редактирование/удаление только своего отзыва.
- Средняя оценка и количество отзывов, вычисляемые ORM.
- Django Admin для пользователей, книг и отзывов.
- Восемь демонстрационных книг, 24 backend-теста, адаптивный Vue UI.

## Tech Stack

**Backend:** Python, Django 5.2 LTS, Django REST Framework, SimpleJWT, django-cors-headers, psycopg и python-dotenv.

**Frontend:** Vue 3 Composition API, TypeScript, Vite, Vue Router, Pinia, Axios, обычный CSS.

**Database:** PostgreSQL. SQLite и Docker не используются.

## Project Structure

```text
backend/
  config/        # настройки и корневые маршруты Django
  accounts/      # custom User, регистрация, JWT и /me
  books/         # Book, Review, permissions, API, seed_books, тесты
  manage.py
  requirements.txt
frontend/
  src/
    api/         # общий Axios client и функции запросов
    components/  # навигация, карточка книги, отзыв
    router/      # четыре основных маршрута
    stores/      # только authentication state
    types/       # интерфейсы TypeScript
    views/       # Books, BookDetail, Login, Register
docs/API.md
.env.example
```

## Requirements

- Python **3.12+**.
- Node.js **20.19+** или **22.12+** (рекомендуется поддерживаемая LTS-версия), npm.
- Запущенный PostgreSQL **14+**, команды `psql`, `createuser`, `createdb` в PATH.

Совместимость: [Django 5.2](https://docs.djangoproject.com/en/5.2/releases/5.2/), [Vite](https://vite.dev/guide/).

## Backend Setup

Из корня репозитория:

```sh
cp .env.example .env
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Windows PowerShell: используйте `Copy-Item .env.example .env`, `python -m venv .venv` и `.venv\Scripts\Activate.ps1` вместо соответствующих команд выше.

В **корневом `.env`** замените `DJANGO_SECRET_KEY` и `POSTGRES_PASSWORD` на свои значения. Сгенерировать ключ можно из `backend`:

```sh
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Ключ заключите в одинарные кавычки в `.env`. Файл не попадает в Git. Django и Vite читают один корневой `.env`; в клиентскую сборку Vite передаёт только переменные с префиксом `VITE_`. Не используйте этот префикс для секретов.

Создайте роль и базу через установленный PostgreSQL (обычно административная роль — `postgres`; в Homebrew это может быть имя пользователя macOS):

```sh
createuser -h localhost -U postgres --pwprompt --createdb shelftalk
createdb -h localhost -U postgres --owner=shelftalk shelftalk
```

Введите для новой роли тот же пароль, что в `POSTGRES_PASSWORD`. `CREATEDB` нужен только для создания временной базы `test_shelftalk` при запуске тестов; роль приложения не обязана быть суперпользователем. При другом порте PostgreSQL добавьте `-p <порт>` и измените `POSTGRES_PORT` в `.env`.

Из `backend` с активированным virtualenv:

```sh
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_books
python manage.py runserver
```

- API: http://localhost:8000/api/books/
- Admin: http://localhost:8000/admin/ — вход по email суперпользователя.
- `seed_books` можно запускать повторно: команда не дублирует книги и не перезаписывает изменения администратора.

Custom User входит в **первую** миграцию `accounts`, `AUTH_USER_MODEL` настроен до миграций. Стандартная таблица пользователя Django не создаётся.

## Frontend Setup

В другом терминале, из корня репозитория:

```sh
cd frontend
npm install
npm run dev
```

Откройте http://localhost:5173. Отдельный frontend `.env` не нужен: Vite использует корневой файл. `VITE_API_BASE_URL=http://localhost:8000/api` задаёт адрес API. После изменения `.env` перезапустите dev-серверы.

```sh
npm run build       # TypeScript check + production bundle в dist/
npm run preview     # локальный просмотр сборки
```

Для запросов из preview добавьте `http://localhost:4173` в `CORS_ALLOWED_ORIGINS` и перезапустите Django. Для размещения SPA веб-сервер должен возвращать `index.html` при открытии `/books/:id`, `/login` и `/register`.

## Tests

Из `backend` с активированным virtualenv и работающим PostgreSQL:

```sh
python manage.py check
python manage.py makemigrations --check
python manage.py migrate
python manage.py test
```

24 теста проверяют регистрацию, хеширование пароля, email без учёта регистра, JWT login/me/refresh, публичное чтение, права на отзывы, запрет подмены автора, ограничения БД, агрегаты и повторный seed. Django создаёт и удаляет отдельную тестовую базу; основные данные не затрагиваются.

Из `frontend`: `npm run type-check` и `npm run build`. Frontend unit/E2E suite не добавлен, чтобы сохранить проект небольшим.

## API

| Method | URL | Доступ |
| --- | --- | --- |
| POST | `/api/auth/register/` | Все |
| POST | `/api/auth/login/` | Все |
| POST | `/api/auth/refresh/` | По refresh token |
| GET | `/api/auth/me/` | Авторизованный пользователь |
| GET | `/api/books/` | Все |
| GET | `/api/books/{id}/` | Все |
| GET / POST | `/api/books/{book_id}/reviews/` | Чтение всем, создание после входа |
| PATCH / DELETE | `/api/reviews/{id}/` | Только автор |

Форматы запросов, ответов и ошибок: [docs/API.md](docs/API.md).

## Authentication

Регистрация создаёт пользователя и перенаправляет на страницу входа. Email нормализуется в нижний регистр; password проверяется стандартными валидаторами Django и сохраняется через `set_password()`. Login возвращает access token на 15 минут и refresh token на 7 дней. Общий Axios client добавляет `Authorization: Bearer <access_token>` к запросам и один раз повторяет запрос после обновления access token при ответе 401. Если обновить токен нельзя, нужно войти снова.

Pinia хранит текущего пользователя, а токены сохраняются в **localStorage для упрощения учебного проекта**. Для production-систем стоит отдельно рассматривать HttpOnly cookies и более строгую token security strategy. Logout удаляет локальные токены; серверный отзыв токенов и refresh-token rotation здесь не реализованы, поэтому ранее выданный токен действует до истечения срока.

Backend устанавливает автора из `request.user` и проверяет ownership независимо от кнопок Vue. `UniqueConstraint(user, book)` не допускает два отзыва даже при одновременных запросах, а рейтинг проверяется сериализатором и `CheckConstraint` PostgreSQL. Публичный API возвращает только id и display_name автора, без email. Изменять книги через API нельзя даже администратору: для этого есть Django Admin.

## Как объяснить проект

Путь запроса: Vue view → функция в `api/` → Axios → Django URL → DRF view → serializer → модель/PostgreSQL. Serializer проверяет входные данные и формирует JSON; permission проверяет автора; модель и БД отвечают за сохранение и ограничения. `Avg` и `Count` вычисляются при чтении книг, а не хранятся в таблице. Книги и отзывы остаются локальным состоянием страниц Vue, Pinia используется только для входа.

При проверке вручную зарегистрируйте двух читателей: первый создаёт, редактирует и удаляет свой отзыв; второй читает его без кнопок управления. Все проверки прав также покрыты API-тестами, включая прямые запросы от второго пользователя.

## Versioning

Версия учебного проекта — **1.0.0**, используется Semantic Versioning. Изменения описаны в [CHANGELOG.md](CHANGELOG.md), этапы разработки записаны Conventional Commits.

## License

[MIT License](LICENSE).
