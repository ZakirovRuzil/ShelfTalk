import client from './client'
import type { LoginRequest, RegisterRequest, Tokens, User } from '../types'

export const login = async (payload: LoginRequest) => (await client.post<Tokens>('/auth/login/', payload)).data
export const register = async (payload: RegisterRequest) => (await client.post<User>('/auth/register/', payload)).data
export const getCurrentUser = async () => (await client.get<User>('/auth/me/')).data
