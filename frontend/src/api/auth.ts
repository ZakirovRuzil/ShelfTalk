import client from './client'
import type { LoginRequest, RegisterRequest, Tokens, User } from '../types'

/**
 * Логин по email и паролю.
 *
 * @param payload - email и пароль пользователя
 * @returns пара JWT-токенов (access живёт 15 минут, refresh — 7 дней,
 *   см. backend/config/settings.py). Токены нужно сохранить самостоятельно,
 *   этим занимается стор `stores/auth.ts`.
 * @throws при неверных данных (400) или неверном email/пароле (401)
 */
export async function login(payload: LoginRequest) {
    const { data } = await client.post<Tokens>('/auth/login/', payload)
    return data
}

/**
 * Регистрация нового пользователя. Не выдаёт токены — после успешной
 * регистрации нужно отдельно вызвать {@link login}.
 *
 * @param payload - email, отображаемое имя и пароль
 * @returns созданный пользователь (без пароля)
 * @throws 400 при занятом email или пароле, не прошедшем валидацию Django
 */
export async function register(payload: RegisterRequest) {
    const { data } = await client.post<User>('/auth/register/', payload)
    return data
}

/**
 * Текущий авторизованный пользователь.
 *
 * @returns данные пользователя, если access-токен валиден
 * @throws 401, если токена нет или он истёк
 */
export async function getCurrentUser() {
    const { data } = await client.get<User>('/auth/me/')
    return data
}
