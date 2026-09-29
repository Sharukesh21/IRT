import { useApiHealth, useDatabaseHealth } from '@/services/healthService'
import { SystemStatus } from '@/types'

export function useSystemStatus() {
  const { 
    data: apiData, 
    isLoading: apiLoading, 
    isError: apiError 
  } = useApiHealth()
  
  const { 
    data: dbData, 
    isLoading: dbLoading, 
    isError: dbError 
  } = useDatabaseHealth()

  const isLoading = apiLoading || dbLoading
  
  let apiStatus: SystemStatus['api'] = 'checking'
  if (!apiLoading) {
    apiStatus = apiError ? 'unavailable' : 'operational'
  }

  let dbStatus: SystemStatus['database'] = 'checking'
  if (!dbLoading) {
    if (dbError) {
      dbStatus = 'disconnected'
    } else if (dbData?.status === 'ok') {
      dbStatus = 'connected'
    } else {
      dbStatus = 'disconnected'
    }
  }

  return {
    apiStatus,
    dbStatus,
    environment: apiData?.environment || 'unknown',
    latency_ms: dbData?.latency_ms,
    isLoading,
    isError: apiError,
  }
}
