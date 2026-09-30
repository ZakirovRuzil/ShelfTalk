import client from './client'
import type { Book } from '../types'

/**
 * Список всех книг каталога с посчитанными на бэкенде средним рейтингом и
 * количеством отзывов. Публичный запрос, авторизация не нужна.
 */
export async function getBooks() {
    const { data } = await client.get<Book[]>('/books/')
    return data
}

/**
 * Одна книга по id.
 *
 * @param id - идентификатор книги
 * @throws 404, если книги с таким id нет
 */
export async function getBook(id: number) {
    const { data } = await client.get<Book>(`/books/${id}/`)
    return data
}
