import client from './client'
import type { Review, ReviewRequest } from '../types'

export const getReviews = async (bookId: number) => (await client.get<Review[]>(`/books/${bookId}/reviews/`)).data
export const createReview = async (bookId: number, payload: ReviewRequest) =>
  (await client.post<Review>(`/books/${bookId}/reviews/`, payload)).data
export const updateReview = async (id: number, payload: ReviewRequest) =>
  (await client.patch<Review>(`/reviews/${id}/`, payload)).data
export const deleteReview = async (id: number) => { await client.delete(`/reviews/${id}/`) }
