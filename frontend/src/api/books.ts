import client from './client'
import type { Book } from '../types'

export async function getBooks() {
  const { data } = await client.get<Book[]>('/books/')
  return data
}

export async function getBook(id: number) {
  const { data } = await client.get<Book>(`/books/${id}/`)
  return data
}
