import { useQuery, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/services/api'

export interface JobResult {
  job_id: string
  job_type: string
  status: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED'
  result: Record<string, unknown> | null
  error: string | null
  elapsed_seconds: number
}

export function useJobStatus(
  jobId: string | null,
  options?: { onComplete?: (job: JobResult) => void }
) {
  return useQuery({
    queryKey: ['job', jobId],
    queryFn: async (): Promise<JobResult> => {
      const res = await apiClient.get<JobResult>(`/api/v1/jobs/${jobId}`)
      return res.data
    },
    enabled: !!jobId,
    refetchInterval: (query): number | false => {
      const data = query.state.data as JobResult | undefined
      if (!data) return 1000
      if (data.status === 'COMPLETED' || data.status === 'FAILED') {
        if (options?.onComplete) options.onComplete(data)
        return false // stop polling
      }
      return 1500 // poll every 1.5s
    },
    staleTime: 0,
  })
}
