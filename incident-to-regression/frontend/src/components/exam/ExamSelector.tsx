import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/services/api'
import { ExamListItem, PagedResponse } from '@/types/domain'
import { Card, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Skeleton } from '@/components/ui/Skeleton'
import { ErrorState } from '@/components/ui/ErrorState'
import { Clock, BookOpen, ArrowRight } from 'lucide-react'

interface ExamSelectorProps {
  onExamSelected: (examId: string, studentId: string) => void
}

const fetchExams = async () => {
  const { data } = await apiClient.get<PagedResponse<ExamListItem>>('/api/v1/exams')
  return data
}

const fetchStudents = async () => {
  const { data } = await apiClient.get<PagedResponse<{ id: string; name: string; email: string }>>('/api/v1/students')
  return data
}

export const ExamSelector: React.FC<ExamSelectorProps> = ({ onExamSelected }) => {
  const [selectedStudentId, setSelectedStudentId] = useState<string>('')

  const examsQuery = useQuery({ queryKey: ['exams'], queryFn: fetchExams })
  const studentsQuery = useQuery({ queryKey: ['students'], queryFn: fetchStudents })

  if (examsQuery.isLoading || studentsQuery.isLoading) {
    return (
      <div className="space-y-4 max-w-2xl mx-auto pt-12">
        <Skeleton className="h-8 w-1/2 mb-6" />
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-32 w-full" />
      </div>
    )
  }

  if (examsQuery.isError || studentsQuery.isError) {
    return <ErrorState message="Unable to load exams. Please ensure the backend is running." />
  }

  const exams = examsQuery.data?.items ?? []
  const students = studentsQuery.data?.items ?? []

  return (
    <div className="max-w-2xl mx-auto pt-12 px-4 space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-slate-900 tracking-tight">Online Examination Portal</h1>
        <p className="mt-2 text-slate-500">Select your identity and choose an examination to begin.</p>
      </div>

      {/* Student Selector */}
      <div className="space-y-2">
        <label className="block text-sm font-semibold text-slate-700">Select Student</label>
        <select
          value={selectedStudentId}
          onChange={e => setSelectedStudentId(e.target.value)}
          className="w-full rounded-lg border border-slate-300 glass px-3 py-2.5 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500"
        >
          <option value="">— Choose a student —</option>
          {students.map(s => (
            <option key={s.id} value={s.id}>{s.name} ({s.email})</option>
          ))}
        </select>
      </div>

      {/* Exam List */}
      <div className="space-y-3">
        <label className="block text-sm font-semibold text-slate-700">Available Examinations</label>
        {exams.length === 0 ? (
          <div className="rounded-lg border border-dashed border-slate-300 p-8 text-center">
            <BookOpen className="mx-auto h-8 w-8 text-slate-400 mb-2" />
            <p className="text-slate-500 text-sm">No exams available. Run <code className="bg-white/50 backdrop-blur-lg px-1 py-0.5 rounded text-xs">make seed</code> to add sample data.</p>
          </div>
        ) : (
          exams.map(exam => (
            <Card key={exam.id} className="hover:border-brand-300 hover:shadow-card-hover transition-all">
              <CardContent className="p-5 flex items-center justify-between">
                <div className="flex-1">
                  <h3 className="font-semibold text-slate-900">{exam.title}</h3>
                  {exam.description && (
                    <p className="text-sm text-slate-500 mt-0.5 line-clamp-2">{exam.description}</p>
                  )}
                  <div className="flex items-center space-x-4 mt-2 text-xs text-slate-400">
                    <span className="flex items-center"><Clock className="w-3 h-3 mr-1" />{Math.round(exam.duration_seconds / 60)} min</span>
                    <span className="capitalize">{exam.status.toLowerCase()}</span>
                  </div>
                </div>
                <Button
                  variant="primary"
                  size="sm"
                  disabled={!selectedStudentId}
                  onClick={() => onExamSelected(exam.id, selectedStudentId)}
                  className="ml-4 flex-shrink-0"
                >
                  Start <ArrowRight className="ml-1 w-4 h-4" />
                </Button>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  )
}
