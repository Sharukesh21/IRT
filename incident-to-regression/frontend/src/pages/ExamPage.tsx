import React, { useState, useCallback } from 'react'
import { useExam, saveAnswer, submitExam, startSession } from '@/services/examService'
import { apiClient } from '@/services/api'
import { ExamSession } from '@/types/domain'
import { ExamSelector } from '@/components/exam/ExamSelector'
import { QuestionWorkspace } from '@/components/exam/QuestionWorkspace'
import { AnswerNavigator } from '@/components/exam/AnswerNavigator'
import { SubmitDialog } from '@/components/exam/SubmitDialog'
import { StatusIndicator } from '@/components/ui/StatusIndicator'
import { Button } from '@/components/ui/Button'
import { Skeleton } from '@/components/ui/Skeleton'
import { ErrorState } from '@/components/ui/ErrorState'
import { ChevronLeft, ChevronRight } from 'lucide-react'

type ExamPageState = 'selecting' | 'in_progress' | 'submitted'

export const ExamPage: React.FC = () => {
  const [pageState, setPageState] = useState<ExamPageState>('selecting')
  const [selectedExamId, setSelectedExamId] = useState<string>('')
  const [session, setSession] = useState<ExamSession | null>(null)
  const [currentQuestionIdx, setCurrentQuestionIdx] = useState(0)
  const [answers, setAnswers] = useState<Record<string, string>>({})
  const [savingQuestionId, setSavingQuestionId] = useState<string | null>(null)
  const [saveErrorQuestionId, setSaveErrorQuestionId] = useState<string | null>(null)
  const [showSubmitDialog, setShowSubmitDialog] = useState(false)

  const examQuery = useExam(selectedExamId)

  const handleExamSelected = useCallback(async (examId: string, studentId: string) => {
    setSelectedExamId(examId)
    try {
      const newSession = await startSession(examId, studentId)
      setSession(newSession)
      setPageState('in_progress')
    } catch (err) {
      console.error('Failed to start session', err)
    }
  }, [])

  const handleAnswerSelected = useCallback(async (questionId: string, optionKey: string) => {
    if (!session) return
    setAnswers((prev) => ({ ...prev, [questionId]: optionKey }))
    setSavingQuestionId(questionId)
    setSaveErrorQuestionId(null)
    try {
      await saveAnswer(session.id, questionId, optionKey)
      const { data } = await apiClient.get<ExamSession>(`/api/v1/sessions/${session.id}`)
      setSession(data)
    } catch (err) {
      setSaveErrorQuestionId(questionId)
      console.error('Failed to save answer', err)
    } finally {
      setSavingQuestionId(null)
    }
  }, [session])

  const handleSubmit = useCallback(async () => {
    if (!session) throw new Error('No active session')
    await submitExam(session.id)
    const { data } = await apiClient.get<ExamSession>(`/api/v1/sessions/${session.id}`)
    setSession(data)
    setPageState('submitted')
    setShowSubmitDialog(false)
  }, [session])

  const resetExam = useCallback(() => {
    setPageState('selecting')
    setSession(null)
    setAnswers({})
    setCurrentQuestionIdx(0)
    setSelectedExamId('')
    setShowSubmitDialog(false)
  }, [])

  if (pageState === 'selecting') {
    return <ExamSelector onExamSelected={(examId, studentId) => { void handleExamSelected(examId, studentId) }} />
  }

  if (pageState === 'submitted' || session?.status === 'SUBMITTED') {
    return (
      <div className="flex flex-col items-center justify-center h-full text-center space-y-4 py-24">
        <div className="bg-emerald-100 rounded-full p-5 mb-2">
          <svg className="w-12 h-12 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <h1 className="text-2xl font-bold text-slate-900">Exam Submitted Successfully</h1>
        <p className="text-slate-500 max-w-md">
          Session version: <span className="font-mono">{session?.version}</span>
        </p>
        <Button variant="secondary" onClick={resetExam}>Return to Exam List</Button>
      </div>
    )
  }

  if (examQuery.isLoading) {
    return (
      <div className="space-y-4 p-8">
        <Skeleton className="h-12 w-full" />
        <Skeleton className="h-64 w-full" />
      </div>
    )
  }

  if (examQuery.isError || !examQuery.data) {
    return <ErrorState message="Failed to load exam data." />
  }

  const exam = examQuery.data
  const questions = exam.questions ?? []
  const currentQuestion = questions[currentQuestionIdx]

  if (!currentQuestion) {
    return <ErrorState message="No questions found in this exam." />
  }

  return (
    <div className="flex flex-col h-full glass rounded-xl border border-slate-200 shadow-sm overflow-hidden">
      {/* Top Bar */}
      <div className="flex items-center justify-between px-6 py-3 border-b border-slate-100 bg-white/40 backdrop-blur-md">
        <div className="flex items-center space-x-4">
          <h1 className="text-base font-semibold text-slate-900">{exam.title}</h1>
          <span className="hidden sm:block text-xs text-slate-400">|</span>
          <span className="hidden sm:block text-xs text-slate-500">{Math.round(exam.duration_seconds / 60)} min</span>
        </div>
        <div className="flex items-center space-x-4">
          <StatusIndicator status="connected" label="Connected" />
          <div className="hidden sm:flex items-center space-x-1 text-xs text-slate-500 glass border border-slate-200 rounded-md px-2 py-1">
            <span className="text-slate-400">Status:</span>
            <span className="font-medium text-slate-700">{session?.status ?? 'IN_PROGRESS'}</span>
            <span className="text-slate-300 mx-1">·</span>
            <span className="text-slate-400">v{session?.version ?? 1}</span>
          </div>
          <Button
            variant="primary"
            size="sm"
            onClick={() => setShowSubmitDialog(true)}
            disabled={(session?.status as any) === 'SUBMITTED'}
          >
            Submit
          </Button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex flex-1 overflow-hidden">
        <div className="flex-1 overflow-y-auto px-6 pb-6">
          <QuestionWorkspace
            question={currentQuestion}
            selectedOptionKey={answers[currentQuestion.id]}
            onAnswerSelected={(questionId, optionKey) => { void handleAnswerSelected(questionId, optionKey) }}
            isSaving={savingQuestionId === currentQuestion.id}
            saveError={saveErrorQuestionId === currentQuestion.id}
          />
        </div>
        <AnswerNavigator
          questions={questions}
          currentIndex={currentQuestionIdx}
          answers={answers}
          onNavigate={setCurrentQuestionIdx}
        />
      </div>

      {/* Bottom Nav */}
      <div className="flex items-center justify-between px-6 py-3 border-t border-slate-100 bg-white/40 backdrop-blur-md">
        <Button
          variant="ghost"
          size="sm"
          disabled={currentQuestionIdx === 0}
          onClick={() => setCurrentQuestionIdx((i) => i - 1)}
        >
          <ChevronLeft className="w-4 h-4 mr-1" /> Previous
        </Button>
        <span className="text-xs text-slate-500">
          Question {currentQuestionIdx + 1} of {questions.length}
        </span>
        <Button
          variant="ghost"
          size="sm"
          disabled={currentQuestionIdx >= questions.length - 1}
          onClick={() => setCurrentQuestionIdx((i) => i + 1)}
        >
          Next <ChevronRight className="w-4 h-4 ml-1" />
        </Button>
      </div>

      {showSubmitDialog && session && (
        <SubmitDialog
          session={session}
          totalQuestions={questions.length}
          answeredCount={Object.keys(answers).length}
          onConfirm={handleSubmit}
          onCancel={() => setShowSubmitDialog(false)}
        />
      )}
    </div>
  )
}
