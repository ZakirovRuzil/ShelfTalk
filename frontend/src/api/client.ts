import axios from 'axios'
import { hasKey, t } from '../i18n'

const client = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
    timeout: 10000,
})

export function clearTokens() {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
}

client.interceptors.request.use((config) => {
    const token = localStorage.getItem('access_token')
    const isPublicAuth = config.url?.startsWith('/auth/') && config.url !== '/auth/me/'
    if (token && !isPublicAuth) {
        config.headers.Authorization = `Bearer ${token}`
    }
    return config
})

// Retry once with a fresh access token. Refresh tokens are not rotated.
client.interceptors.response.use(undefined, async (error: unknown) => {
    if (!axios.isAxiosError(error) || !error.config) {
        return Promise.reject(error)
    }
    const config = error.config as typeof error.config & { _retry?: boolean }
    const isPublicAuth = config.url?.startsWith('/auth/') && config.url !== '/auth/me/'
    if (error.response?.status !== 401 || isPublicAuth) {
        return Promise.reject(error)
    }
    const refresh = localStorage.getItem('refresh_token')
    if (refresh && !config._retry) {
        try {
            const { data } = await client.post<{ access: string }>('/auth/refresh/', {
                refresh,
            })
            // Do not restore a session if the user logged out during this request.
            if (localStorage.getItem('refresh_token') !== refresh) {
                return Promise.reject(error)
            }
            localStorage.setItem('access_token', data.access)
            config._retry = true
            return client(config)
        } catch {
            // An expired refresh token requires another login.
        }
    }
    clearTokens()
    window.dispatchEvent(new Event('auth-expired'))
    return Promise.reject(error)
})

function fieldLabel(field: string): string {
    const key = `fields.${field}`
    return hasKey(key) ? t(key) : field.replaceAll('_', ' ')
}

export function errorMessage(error: unknown): string {
    if (!axios.isAxiosError(error)) {
        return t('errors.generic')
    }
    if (!error.response) {
        return t('errors.network')
    }
    if (error.response.status >= 500) {
        return t('errors.server')
    }
    if (error.response.status === 401) {
        return t('errors.unauthorized')
    }
    if (error.response.status === 404) {
        return t('errors.notFound')
    }
    const data: unknown = error.response.data
    if (data && typeof data === 'object') {
        return Object.entries(data)
            .map(([field, value]) => {
                const message = Array.isArray(value) ? value.join(' ') : String(value)
                return ['detail', 'non_field_errors'].includes(field)
                    ? message
                    : `${fieldLabel(field)}: ${message}`
            })
            .join(' ')
    }
    return t('errors.request')
}

export default client
