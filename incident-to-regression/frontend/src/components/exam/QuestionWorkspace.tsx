import React from 'react'
import { CheckCircle2, Circle, AlertCircle } from 'lucide-react'
import { Question } from '@/types/domain'
import { cn } from '@/lib/utils'

interface QuestionWorkspaceProps {
  question: Question
  selectedOptionKey?: string
  onAnswerSelected: (questionId: string, optionKey: string) => void
  isSaving: boolean
  saveError: boolean
}

export const QuestionWorkspace: React.FC<QuestionWorkspaceProps> = ({
  question,
  selectedOptionKey,
  onAnswerSelected,
  isSaving,
  saveError
}) => {
  return (
    <div className="flex flex-col h-full space-y-6 max-w-3xl mx-auto w-full pt-8">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-medium text-slate-800 tracking-tight">
          Question {question.question_number}
        </h2>
        
        {/* Save Status Indicator */}
        <div className="flex items-center space-x-2 text-sm">
          {saveError ? (
            <span className="flex items-center text-rose-600 animate-fade-in">
              <AlertCircle className="w-4 h-4 mr-1.5" />
              Save failed
            </span>
          ) : isSaving ? (
            <span className="flex items-center text-slate-500 animate-pulse-slow">
              <span className="w-2 h-2 rounded-full bg-slate-400 mr-2 animate-ping" />
              Saving...
            </span>
          ) : selectedOptionKey ? (
            <span className="flex items-center text-emerald-600 animate-fade-in">
              <CheckCircle2 className="w-4 h-4 mr-1.5" />
              Saved
            </span>
          ) : null}
        </div>
      </div>

      <div className="prose prose-slate max-w-none text-slate-700 font-medium text-lg leading-relaxed">
        {question.question_text}
      </div>

      <div className="space-y-3 mt-6">
        {question.options.map((opt) => {
          const isSelected = selectedOptionKey === opt.option_key
          return (
            <div
              key={opt.id}
              onClick={() => onAnswerSelected(question.id, opt.option_key)}
              className={cn(
                "relative flex items-start p-4 border rounded-xl cursor-pointer transition-all duration-200",
                "hover:border-brand-400 hover:bg-brand-50 group",
                isSelected ? "border-brand-500 bg-brand-50 ring-1 ring-brand-500" : "border-slate-200 glass"
              )}
            >
              <div className="flex items-center h-6">
                {isSelected ? (
                  <CheckCircle2 className="w-5 h-5 text-brand-600" />
                ) : (
                  <Circle className="w-5 h-5 text-slate-300 group-hover:text-brand-400" />
                )}
              </div>
              <div className="ml-3 flex flex-col">
                <span className={cn(
                  "block text-base font-medium",
                  isSelected ? "text-brand-900" : "text-slate-700 group-hover:text-slate-900"
                )}>
                  {opt.option_key}. {opt.option_text}
                </span>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
