import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import * as api from '../api/auth'
import { clearTokens } from '../api/client'
import type { LoginRequest, User } from '../types'

export const useAuthStore = defineStore('auth', () => {
    const user = ref<User | null>(null)
    const isAuthenticated = computed(() => user.value !== null)

    function logout() {
        clearTokens()
        user.value = null
    }

    async function fetchCurrentUser() {
        if (!localStorage.getItem('access_token')) {
            return
        }
        const currentUser = await api.getCurrentUser()
        if (localStorage.getItem('access_token')) {
            user.value = currentUser
        }
    }

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
