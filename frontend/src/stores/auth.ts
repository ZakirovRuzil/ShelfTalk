import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import * as api from '../api/auth'
import { clearTokens } from '../api/client'
import type { LoginRequest, User } from '../types'

/**
 * Pinia-стор аутентификации. Держит текущего пользователя в памяти, а
 * JWT-токены — в localStorage (см. api/client.ts). Слушает два глобальных
 * события, чтобы состояние не расходилось с реальностью:
 * - `auth-expired` — client.ts диспатчит его, когда обновить access-токен
 *   не удалось (refresh истёк или отозван);
 * - `storage` — браузер шлёт его во все ВКЛАДКИ, кроме той, что изменила
 *   localStorage, поэтому выход в одной вкладке разлогинивает остальные.
 */
export const useAuthStore = defineStore('auth', () => {
    const user = ref<User | null>(null)
    const isAuthenticated = computed(() => user.value !== null)

    /** Стирает токены и сбрасывает текущего пользователя. */
    function logout() {
        clearTokens()
        user.value = null
    }

    /**
     * Подгружает текущего пользователя, если есть access-токен. Ничего не
     * делает без токена — так `App.vue` может звать это при каждом старте,
     * не заставляя гостя ждать лишний запрос.
     *
     * @throws то же, что {@link api.getCurrentUser} (в частности 401,
     *   если токен уже истёк)
     */
    async function fetchCurrentUser() {
        if (!localStorage.getItem('access_token')) {
            return
        }
        const currentUser = await api.getCurrentUser()
        // Пользователь мог успеть нажать «Выйти», пока шёл этот запрос —
        // тогда токена уже нет, и записывать данные в user не нужно.
        if (localStorage.getItem('access_token')) {
            user.value = currentUser
        }
    }

    /**
     * Логин: получает токены, сохраняет их и подгружает пользователя.
     * Если после логина не удалось получить пользователя, откатывает вход
     * (стирает токены) и пробрасывает ошибку дальше.
     */
    async function login(payload: LoginRequest) {
        const tokens = await api.login(payload)
        localStorage.setItem('access_token', tokens.access)
        localStorage.setItem('refresh_token', tokens.refresh)
        try {
            await fetchCurrentUser()
        } catch (error) {
            logout()
            throw error
        }
    }

    window.addEventListener('auth-expired', logout)
    window.addEventListener('storage', (event) => {
        if (event.key === 'refresh_token' || event.key === null) {
            user.value = null
        }
    })

    return {
        user,
        isAuthenticated,
        login,
        register: api.register,
        logout,
        fetchCurrentUser,
    }
})
