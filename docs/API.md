# ShelfTalk API · 1.0.0

Base URL: `http://localhost:8000/api`. Запросы и ответы — JSON, кроме пустого ответа
DELETE. Завершающий `/` обязателен. Коллекции возвращаются массивами без пагинации.
Поиск выполняется во frontend.

Для защищённых запросов: `Authorization: Bearer <access_token>`. Нет/невалидный/истёкший
токен — **401**. Чужой отзыв — **403**, отсутствующий объект — **404**, неподдерживаемый
method — **405**. Ошибки валидации — **400** с полями или `detail`; текст ошибок может
отличаться в зависимости от валидатора.

## Authentication

### POST `/auth/register/`

Авторизация не нужна. Создаёт пользователя; **201**. `first_name` и `last_name`
необязательны.

Request:

```json
{
  "email": "reader@example.com",
  "display_name": "Reader",
  "password": "A-good-book-2026!"
}
```

Response:

```json
{
  "id": 1,
  "email": "reader@example.com",
  "display_name": "Reader",
  "first_name": "",
  "last_name": ""
}
```

Ошибки **400**: занятый или невалидный email, пустой display_name, слабый/пропущенный
пароль. Например:

```json
{ "email": ["A user with this email already exists."] }
```

Email приводится к нижнему регистру и уникален без учёта регистра. Display name: до 80
символов. Password не возвращается. Регистрация не выдаёт токены — после неё выполните
login.

### POST `/auth/login/`

Авторизация не нужна. Request:

```json
{ "email": "reader@example.com", "password": "A-good-book-2026!" }
```

Response **200**:

```json
{ "access": "<access_token>", "refresh": "<refresh_token>" }
```

Ошибки: **400** при отсутствии полей; **401** при неверном пароле/email или неактивном
пользователе:

```json
{ "detail": "No active account found with the given credentials" }
```

### POST `/auth/refresh/`

Access token не нужен. Request:

```json
{ "refresh": "<refresh_token>" }
```

Response **200**:

```json
{ "access": "<new_access_token>" }
```

Срок access token — 15 минут, refresh — 7 дней. Refresh token не меняется. Ошибки:
**400** без поля refresh; **401** при невалидном/истёкшем токене. Старый refresh не
продлевается при использовании.

### GET `/auth/me/`

Нужен access token. Тело запроса отсутствует. Response **200**:

```json
{
  "id": 1,
  "email": "reader@example.com",
  "display_name": "Reader",
  "first_name": "",
  "last_name": ""
}
```

Ошибка: **401** без действующего access token. Email доступен только самому пользователю
в этом ответе.

## Books

### GET `/books/`

Авторизация не нужна. Тело запроса отсутствует. Response **200**, сортировка по title и
id:

```json
[
  {
    "id": 1,
    "title": "1984",
    "author": "George Orwell",
    "description": "A story about power and individual freedom.",
    "publication_year": 1949,
    "average_rating": 8.5,
    "reviews_count": 2
  }
]
```

Пустой каталог — `[]`. Без отзывов `average_rating: null`, `reviews_count: 0`.
`publication_year` может быть `null`. Агрегаты рассчитываются ORM; average_rating не
округляется API. POST — **405** для авторизованного пользователя (невалидный присланный
JWT может дать 401 до проверки method).

### GET `/books/{id}/`

Авторизация не нужна. Тело запроса отсутствует. Response **200** — объект книги:

```json
{
  "id": 1,
  "title": "1984",
  "author": "George Orwell",
  "description": "A story about power and individual freedom.",
  "publication_year": 1949,
  "average_rating": null,
  "reviews_count": 0
}
```

Ошибка: **404**, если книги нет. POST/PATCH/PUT/DELETE не поддерживаются (**405**).
Каталог изменяется через `/admin/`.

## Reviews

### GET `/books/{book_id}/reviews/`

Авторизация не нужна. Тело запроса отсутствует. Response **200**, новые отзывы первыми:

```json
[
  {
    "id": 1,
    "rating": 8,
    "text": "I really enjoyed this book.",
    "author": { "id": 1, "display_name": "Reader" },
    "created_at": "2026-09-14T12:00:00Z",
    "updated_at": "2026-09-14T12:00:00Z"
  }
]
```

Без отзывов — `[]`. Ошибка: **404**, если книги нет. Email автора никогда не включается
в этот ответ.

### POST `/books/{book_id}/reviews/`

Нужен access token. Request:

```json
{ "rating": 8, "text": "I really enjoyed this book." }
```

Response **201**:

```json
{
  "id": 1,
  "rating": 8,
  "text": "I really enjoyed this book.",
  "author": { "id": 1, "display_name": "Reader" },
  "created_at": "2026-09-14T12:00:00Z",
  "updated_at": "2026-09-14T12:00:00Z"
}
```

`rating` — целое число **1–10**, `text` — обязательный непустой текст. Автор берётся из
JWT (`request.user`), книга — из URL. Переданные `user`, `book` и `author` не изменяют
эти значения.

Ошибки: **401** без входа; **404** без книги; **400** при невалидных данных или
повторном отзыве:

```json
{ "detail": "You have already reviewed this book." }
```

```json
{ "rating": ["Ensure this value is less than or equal to 10."] }
```

### PATCH `/reviews/{id}/`

Нужен access token **автора**. Допускается передать только изменяемые поля (`rating`,
`text`). Request:

```json
{ "rating": 9, "text": "Even better on rereading." }
```

Response **200**:

```json
{
  "id": 1,
  "rating": 9,
  "text": "Even better on rereading.",
  "author": { "id": 1, "display_name": "Reader" },
  "created_at": "2026-09-14T12:00:00Z",
  "updated_at": "2026-09-14T12:30:00Z"
}
```

Автор, книга и created_at не меняются. Ошибки: **400** при неверных полях, **401** без
входа, **403** для чужого отзыва, **404** если отзыва нет. Даже staff-пользователь через
этот API не может изменять чужой отзыв.

### DELETE `/reviews/{id}/`

Нужен access token **автора**. Тело запроса отсутствует. Response **204 No Content**,
без JSON.

Ошибки: **401** без входа, **403** для чужого отзыва, **404** если отзыва нет. После
удаления пользователь может снова оставить отзыв этой книге. GET/PUT на `/reviews/{id}/`
не поддерживаются (**405** для авторизованного пользователя).

## Пример запроса

```sh
curl http://localhost:8000/api/books/1/reviews/ \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer <access_token>' \
  -d '{"rating":8,"text":"I really enjoyed this book."}'
```

Браузерные запросы разрешены только с origin из `CORS_ALLOWED_ORIGINS`. При неверном
присланном JWT даже публичный GET может вернуть 401; для гостевого запроса просто не
передавайте Authorization.
