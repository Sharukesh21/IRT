export interface Student {
  id: string
  name: string
  email: string
}

export interface AnswerOption {
  id: string
  option_key: string
  option_text: string
}

export interface Question {
  id: string
  question_number: number
  question_text: string
  question_type: string
  points: number
  options: AnswerOption[]
}

export interface Exam {
  id: string
  title: string
  description: string
  duration_seconds: number
  status: string
  questions: Question[]
  created_at: string
}

export interface ExamListItem {
  id: string
  title: string
  description: string
  duration_seconds: number
  status: string
  created_at: string
}

export interface ExamSession {
  id: string
  student_id: string
  exam_id: string
  status: 'NOT_STARTED' | 'IN_PROGRESS' | 'SUBMITTING' | 'SUBMITTED' | 'RECOVERING' | 'FAILED'
  started_at: string | null
  submitted_at: string | null
  last_activity_at: string | null
  version: number
  created_at: string
  updated_at: string
}

export interface EventTrace {
  id: string
  event_id: string
  event_type: string
  sequence_number: number
  status: 'RECEIVED' | 'PROCESSED' | 'DUPLICATE' | 'REJECTED' | 'FAILED'
  occurred_at: string
  received_at: string
  delay_ms: number
  correlation_id: string
  causation_id: string | null
  payload: Record<string, unknown>
  processed_at: string | null
  error_message: string | null
}

export interface PagedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
}
