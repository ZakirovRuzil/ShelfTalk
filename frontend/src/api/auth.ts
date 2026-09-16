import client from './client'
import type { LoginRequest, RegisterRequest, Tokens, User } from '../types'

export async function login(payload: LoginRequest) {
    const { data } = await client.post<Tokens>('/auth/login/', payload)
    return data
}

export async function register(payload: RegisterRequest) {
    const { data } = await client.post<User>('/auth/register/', payload)
    return data
}

export async function getCurrentUser() {
    const { data } = await client.get<User>('/auth/me/')
    return data
}
