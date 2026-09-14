export interface User {
  id: number
  email: string
  display_name: string
  first_name: string
  last_name: string
}

export interface Book {
  id: number
  title: string
  author: string
  description: string
  publication_year: number | null
  average_rating: number | null
  reviews_count: number
}

export interface Review {
  id: number
  rating: number
  text: string
  author: Pick<User, 'id' | 'display_name'>
  created_at: string
  updated_at: string
}

export interface LoginRequest { email: string; password: string }
export interface RegisterRequest extends LoginRequest { display_name: string }
export interface Tokens { access: string; refresh: string }
export interface ReviewRequest { rating: number; text: string }
