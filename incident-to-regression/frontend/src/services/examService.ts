import { useQuery } from '@tanstack/react-query'
import { apiClient } from './api'
import { Exam, ExamSession, EventTrace } from '@/types/domain'

export const fetchExam = async (examId: string): Promise<Exam> => {
  const { data } = await apiClient.get<Exam>(`/api/v1/exams/${examId}`)
  return data
}

export const startSession = async (examId: string, studentId: string): Promise<ExamSession> => {
  const { data } = await apiClient.post<ExamSession>('/api/v1/sessions', {
    exam_id: examId,
    student_id: studentId,
  })
  return data
}

export const saveAnswer = async (sessionId: string, questionId: string, optionKey: string): Promise<void> => {
  await apiClient.post(`/api/v1/sessions/${sessionId}/answers/${questionId}`, {
    selected_option: optionKey,
  })
}

export const submitExam = async (sessionId: string): Promise<void> => {
  await apiClient.post(`/api/v1/sessions/${sessionId}/submit`)
}

export const fetchTraces = async (sessionId: string): Promise<{ items: EventTrace[] }> => {
  const { data } = await apiClient.get<{ items: EventTrace[] }>(`/api/v1/sessions/${sessionId}/events`)
  return data
}

export const useExam = (examId: string) => {
  return useQuery({
    queryKey: ['exam', examId],
    queryFn: () => fetchExam(examId),
    enabled: !!examId,
  })
}

export const useSessionTraces = (sessionId: string) => {
  return useQuery({
    queryKey: ['traces', sessionId],
    queryFn: () => fetchTraces(sessionId),
    enabled: !!sessionId,
    refetchInterval: 3000,
  })
}
