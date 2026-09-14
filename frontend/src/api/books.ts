import client from './client'
import type { Book } from '../types'

export const getBooks = async () => (await client.get<Book[]>('/books/')).data
export const getBook = async (id: number) => (await client.get<Book>(`/books/${id}/`)).data
