// Формы этого файла зеркалят сериализаторы DRF (backend/accounts/serializers.py,
// backend/books/serializers.py) — при изменении полей на бэкенде обновляйте и здесь.

/** Пользователь, как его возвращает `/api/auth/me/` и `/api/auth/register/`. */
export interface User {
    id: number
    email: string
    display_name: string
    first_name: string
    last_name: string
}

/** Книга из каталога. Агрегаты `average_rating`/`reviews_count` считает ORM. */
export interface Book {
    id: number
    title: string
    author: string
    description: string
    publication_year: number | null
    /** null, если ни одного отзыва ещё нет. */
    average_rating: number | null
    reviews_count: number
}

/** Отзыв на книгу. Email автора сервер никогда не отдаёт в этом объекте. */
export interface Review {
    id: number
    /** Целое число от 1 до 10 (ограничено и на бэкенде — models.Review). */
    rating: number
    text: string
    author: Pick<User, 'id' | 'display_name'>
    created_at: string
    updated_at: string
}

export interface LoginRequest {
    email: string
    password: string
}
export interface RegisterRequest extends LoginRequest {
    display_name: string
}
export interface Tokens {
    access: string
    refresh: string
}
export interface ReviewRequest {
    rating: number
    text: string
}
