import axios, { AxiosError } from 'axios'
import { ApiError } from '@/types'

const baseURL = import.meta.env.VITE_API_URL || ''

export const apiClient = axios.create({
  baseURL,
  timeout: 15000,
})

// Request interceptor — add request ID + allow callers to suppress toasts
apiClient.interceptors.request.use((config) => {
  const requestId = crypto.randomUUID()
  config.headers['X-Request-ID'] = requestId
  return config
})

// Track connection errors to avoid flooding toasts
let _lastNetworkToastAt = 0
const NETWORK_TOAST_DEBOUNCE_MS = 8000

// Response interceptor — only show toasts for user-triggered errors, not background polling
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<{ error: ApiError }>) => {
    // Suppress toasts for polling/background requests (job status, health, dashboard overview)
    const url = error.config?.url ?? ''
    const isSilent =
      url.includes('/jobs/') ||
      url.includes('/health') ||
      url.includes('/dashboard/overview')

    if (!isSilent) {
      import('@/hooks/useToast').then(({ toastService }) => {
        if (error.response) {
          if (error.response.status === 429) {
            toastService.show('Rate limit exceeded. Please slow down.', 'warning')
          } else if (error.response.status >= 500) {
            toastService.show('Server error. Please try again.', 'error')
          } else if (error.response.data?.error?.message) {
            toastService.show(error.response.data.error.message, 'error')
          }
        } else {
          // Network error — debounce so we don't spam
          const now = Date.now()
          if (now - _lastNetworkToastAt > NETWORK_TOAST_DEBOUNCE_MS) {
            _lastNetworkToastAt = now
            toastService.show('Cannot reach server. Is the backend running?', 'error')
          }
        }
      })
    }

    if (error.response?.data?.error) {
      console.warn('API Error:', error.response.data.error.message)
    } else if (!isSilent) {
      console.warn('Network or unexpected error:', error.message)
    }
    return Promise.reject(error)
  }
)
