import client from './client'
import type { Review, ReviewRequest } from '../types'

export async function getReviews(bookId: number) {
    const { data } = await client.get<Review[]>(`/books/${bookId}/reviews/`)
    return data
}

export async function createReview(bookId: number, payload: ReviewRequest) {
    const { data } = await client.post<Review>(`/books/${bookId}/reviews/`, payload)
    return data
}

export async function updateReview(id: number, payload: ReviewRequest) {
    const { data } = await client.patch<Review>(`/reviews/${id}/`, payload)
    return data
}

export async function deleteReview(id: number) {
    await client.delete(`/reviews/${id}/`)
}
