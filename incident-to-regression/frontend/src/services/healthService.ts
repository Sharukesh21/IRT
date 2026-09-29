import { useQuery } from '@tanstack/react-query'
import { apiClient } from './api'
import { HealthStatus, DatabaseHealthStatus } from '@/types'

export const fetchApiHealth = async (): Promise<HealthStatus> => {
  const { data } = await apiClient.get<HealthStatus>('/api/v1/health')
  return data
}

export const fetchDatabaseHealth = async (): Promise<DatabaseHealthStatus> => {
  const { data } = await apiClient.get<DatabaseHealthStatus>('/api/v1/health/database')
  return data
}

export const useApiHealth = () => {
  return useQuery({
    queryKey: ['health', 'api'],
    queryFn: fetchApiHealth,
    refetchInterval: 30000,
  })
}

export const useDatabaseHealth = () => {
  return useQuery({
    queryKey: ['health', 'database'],
    queryFn: fetchDatabaseHealth,
    refetchInterval: 30000,
    retry: false, // Fail fast for DB health to show correct UI status
  })
}
