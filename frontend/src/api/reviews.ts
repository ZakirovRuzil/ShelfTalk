import client from './client'
import type { Review, ReviewRequest } from '../types'

/** Отзывы на книгу, новые сначала. Публичный запрос. */
export async function getReviews(bookId: number) {
    const { data } = await client.get<Review[]>(`/books/${bookId}/reviews/`)
    return data
}

/**
 * Публикует отзыв от имени текущего пользователя (определяется по JWT).
 *
 * @throws 401 без токена, 404 без такой книги, 400 при повторном отзыве
 *   на ту же книгу или невалидном rating/text
 */
export async function createReview(bookId: number, payload: ReviewRequest) {
    const { data } = await client.post<Review>(`/books/${bookId}/reviews/`, payload)
    return data
}

/**
 * Редактирует свой отзыв.
 *
 * @throws 403 при попытке отредактировать чужой отзыв, 404 без отзыва
 */
export async function updateReview(id: number, payload: ReviewRequest) {
    const { data } = await client.patch<Review>(`/reviews/${id}/`, payload)
    return data
}

/**
 * Удаляет свой отзыв.
 *
 * @throws 403 при попытке удалить чужой отзыв, 404 без отзыва
 */
export async function deleteReview(id: number) {
    await client.delete(`/reviews/${id}/`)
}
