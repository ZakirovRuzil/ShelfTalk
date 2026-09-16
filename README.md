# ShelfTalk

Учебный каталог книг на Django REST Framework, PostgreSQL и Vue 3 + TypeScript. Вход по
email, оценки от 1 до 10, один отзыв на книгу от читателя. Редактировать и удалять можно
только свой отзыв. Книги добавляются через Django Admin.

## Запуск

Нужны Python 3.12+, Node.js 20.19 или 22.12+ и запущенный PostgreSQL 14+.

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

## Проверки и форматирование

Из `backend`, с активированным virtualenv:

```sh
ruff check .
ruff format --check .
python manage.py check
python manage.py test
```

Для автоисправления: `ruff check --fix .` и `ruff format .`. Для тестов
PostgreSQL-пользователю нужно право `CREATEDB`.

Из `frontend`:

```sh
npm run lint
npm run format:check
npm run build
```

Для автоисправления: `npm run lint:fix` и `npm run format`. Сборка включает проверку
TypeScript.

API: [docs/API.md](docs/API.md). История изменений: [CHANGELOG.md](CHANGELOG.md).
Лицензия: [MIT](LICENSE).

JWT хранится в localStorage для простоты учебного проекта. Для production стоит отдельно
рассмотреть HttpOnly cookies и защиту токенов.
