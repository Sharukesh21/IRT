import React from 'react'
import { Question } from '@/types/domain'
import { cn } from '@/lib/utils'

interface AnswerNavigatorProps {
  questions: Question[]
  currentIndex: number
  answers: Record<string, string>
  onNavigate: (index: number) => void
}

export const AnswerNavigator: React.FC<AnswerNavigatorProps> = ({
  questions,
  currentIndex,
  answers,
  onNavigate
}) => {
  const answeredCount = Object.keys(answers).length

  return (
    <div className="w-64 flex-shrink-0 border-l border-slate-200 bg-white/40 backdrop-blur-md p-5 flex flex-col">
      <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-4">Question Navigator</h3>

      <div className="grid grid-cols-5 gap-1.5 mb-6">
        {questions.map((q, idx) => {
          const isAnswered = !!answers[q.id]
          const isCurrent = currentIndex === idx
          return (
            <button
              key={q.id}
              onClick={() => onNavigate(idx)}
              title={`Question ${q.question_number}`}
              className={cn(
                'w-9 h-9 rounded-md text-xs font-semibold transition-all border',
                isCurrent
                  ? 'bg-brand-600 text-white border-brand-600 shadow-sm'
                  : isAnswered
                  ? 'bg-emerald-50 text-emerald-700 border-emerald-300'
                  : 'glass text-slate-500 border-slate-200 hover:border-brand-300'
              )}
            >
              {q.question_number}
            </button>
          )
        })}
      </div>

      {/* Legend */}
      <div className="mt-auto space-y-2 text-xs text-slate-500">
        <div className="flex items-center space-x-2">
          <div className="w-4 h-4 rounded bg-brand-600" />
          <span>Current</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-4 h-4 rounded bg-emerald-50 border border-emerald-300" />
          <span>Answered</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-4 h-4 rounded glass border border-slate-200" />
          <span>Unanswered</span>
        </div>
      </div>

      <div className="mt-4 pt-4 border-t border-slate-200">
        <p className="text-xs text-slate-500">
          <span className="font-semibold text-slate-700">{answeredCount}</span> of{' '}
          <span className="font-semibold text-slate-700">{questions.length}</span> answered
        </p>
      </div>
    </div>
  )
}
