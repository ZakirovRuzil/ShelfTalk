import axios from 'axios'

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
  if (token && !config.url?.startsWith('/auth/')) {
    config.headers.Authorization = `Bearer ${token}`
  }
  if (token && config.url === '/auth/me/') config.headers.Authorization = `Bearer ${token}`
  return config
})

// Retry once with a fresh access token. Refresh tokens are not rotated.
client.interceptors.response.use(undefined, async (error: unknown) => {
  if (!axios.isAxiosError(error) || !error.config) return Promise.reject(error)
  const config = error.config as typeof error.config & { _retry?: boolean }
  const isPublicAuth = config.url?.startsWith('/auth/') && config.url !== '/auth/me/'
  if (error.response?.status !== 401 || isPublicAuth) return Promise.reject(error)
  const refresh = localStorage.getItem('refresh_token')
  if (refresh && !config._retry) {
    try {
      const { data } = await client.post<{ access: string }>('/auth/refresh/', { refresh })
      // Do not restore a session if the user logged out during this request.
      if (localStorage.getItem('refresh_token') !== refresh) return Promise.reject(error)
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

export function errorMessage(error: unknown): string {
  if (!axios.isAxiosError(error)) return 'Something went wrong. Please try again.'
  if (!error.response) return 'Cannot reach ShelfTalk. Check your connection and try again.'
  if (error.response.status >= 500) return 'The server could not complete your request. Please try again.'
  if (error.response.status === 401) return 'Please sign in again. Your email or password may be incorrect, or your session has expired.'
  if (error.response.status === 404) return 'This book or review could not be found.'
  const data: unknown = error.response.data
  if (data && typeof data === 'object') {
    return Object.entries(data).map(([field, value]) => {
      const message = Array.isArray(value) ? value.join(' ') : String(value)
      return ['detail', 'non_field_errors'].includes(field) ? message : `${field.replaceAll('_', ' ')}: ${message}`
    }).join(' ')
  }
  return 'The request could not be completed. Please try again.'
}

export default client
