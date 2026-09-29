import React, { useState } from 'react'
import { AlertTriangle, CheckCircle2 } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { ExamSession } from '@/types/domain'

interface SubmitDialogProps {
  session: ExamSession
  totalQuestions: number
  answeredCount: number
  onConfirm: () => Promise<void>
  onCancel: () => void
}

export const SubmitDialog: React.FC<SubmitDialogProps> = ({
  session,
  totalQuestions,
  answeredCount,
  onConfirm,
  onCancel
}) => {
  const [submitting, setSubmitting] = useState(false)
  const [submitResult, setSubmitResult] = useState<'success' | 'duplicate' | 'error' | null>(null)
  const [errorMessage, setErrorMessage] = useState<string>('')

  const unanswered = totalQuestions - answeredCount

  const handleConfirm = async () => {
    setSubmitting(true)
    setSubmitResult(null)
    try {
      await onConfirm()
      setSubmitResult('success')
    } catch (err: unknown) {
      const errMsg = err instanceof Error ? err.message : 'Submission failed. Please retry.'
      setErrorMessage(errMsg)
      setSubmitResult('error')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm animate-fade-in">
      <div className="glass rounded-xl shadow-2xl w-full max-w-md mx-4 p-6">

        {/* Success State */}
        {submitResult === 'success' && (
          <div className="text-center py-6">
            <CheckCircle2 className="mx-auto h-14 w-14 text-emerald-500 mb-4" />
            <h2 className="text-xl font-bold text-slate-900 mb-2">Exam Submitted</h2>
            <p className="text-slate-500 text-sm">Your responses have been recorded. You may close this window.</p>
          </div>
        )}

        {/* Error State */}
        {submitResult === 'error' && (
          <div className="text-center py-4">
            <AlertTriangle className="mx-auto h-12 w-12 text-rose-500 mb-3" />
            <h2 className="text-xl font-bold text-slate-900 mb-2">Submission Failed</h2>
            <p className="text-sm text-slate-500 mb-6">{errorMessage}</p>
            <div className="flex space-x-3 justify-center">
              <Button variant="secondary" onClick={onCancel}>Cancel</Button>
              <Button variant="primary" onClick={() => { void handleConfirm() }} isLoading={submitting}>Retry</Button>
            </div>
          </div>
        )}

        {/* Confirm State */}
        {!submitResult && (
          <>
            <h2 className="text-xl font-bold text-slate-900 mb-1">Submit Examination?</h2>
            <p className="text-sm text-slate-500 mb-6">This action cannot be undone once confirmed.</p>

            {unanswered > 0 && (
              <div className="mb-5 flex items-start space-x-3 bg-amber-50 border border-amber-200 rounded-lg p-3">
                <AlertTriangle className="w-4 h-4 text-amber-600 mt-0.5 flex-shrink-0" />
                <p className="text-sm text-amber-800">
                  You have <strong>{unanswered}</strong> unanswered question{unanswered > 1 ? 's' : ''}.
                </p>
              </div>
            )}

            <div className="bg-white/40 backdrop-blur-md rounded-lg p-4 mb-6 text-sm text-slate-600 space-y-1">
              <div className="flex justify-between">
                <span>Answered</span>
                <span className="font-medium text-slate-900">{answeredCount} / {totalQuestions}</span>
              </div>
              <div className="flex justify-between">
                <span>Session version</span>
                <span className="font-mono text-slate-900">{session.version}</span>
              </div>
            </div>

            <div className="flex space-x-3">
              <Button variant="secondary" className="flex-1" onClick={onCancel} disabled={submitting}>Cancel</Button>
              <Button
                variant="primary"
                className="flex-1"
                onClick={() => { void handleConfirm() }}
                isLoading={submitting}
              >
                {submitting ? 'Submitting...' : 'Confirm Submit'}
              </Button>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
