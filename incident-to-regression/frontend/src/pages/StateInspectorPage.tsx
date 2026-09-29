import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { ExamSession } from '@/types/domain'
import { PageHeader } from '@/components/ui/PageHeader'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Skeleton } from '@/components/ui/Skeleton'
import { StatusIndicator } from '@/components/ui/StatusIndicator'
import { cn } from '@/lib/utils'
import { apiClient } from '@/services/api'

const fetchSessions = async (): Promise<{ items: ExamSession[] }> => {
  const { data } = await apiClient.get<{ items: ExamSession[] }>('/api/v1/sessions')
  return data
}

const fetchSession = async (id: string): Promise<ExamSession> => {
  const { data } = await apiClient.get<ExamSession>(`/api/v1/sessions/${id}`)
  return data
}

export const StateInspectorPage: React.FC = () => {
  const [selectedId, setSelectedId] = useState<string>('')

  const sessionsQuery = useQuery({
    queryKey: ['sessions'],
    queryFn: fetchSessions,
    refetchInterval: 5000,
  })

  const sessionQuery = useQuery({
    queryKey: ['session', selectedId],
    queryFn: () => fetchSession(selectedId),
    enabled: !!selectedId,
    refetchInterval: 2000,
  })

  const sessions = sessionsQuery.data?.items ?? []
  const session = sessionQuery.data

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'SUBMITTED': return 'text-emerald-700 bg-emerald-50 border-emerald-200'
      case 'IN_PROGRESS': return 'text-brand-700 bg-brand-50 border-brand-200'
      case 'SUBMITTING': return 'text-amber-700 bg-amber-50 border-amber-200'
      case 'FAILED': return 'text-rose-700 bg-rose-50 border-rose-200'
      case 'RECOVERING': return 'text-violet-700 bg-violet-50 border-violet-200'
      default: return 'text-slate-700 bg-white/40 backdrop-blur-md border-slate-200'
    }
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="State Inspector"
        description="Live view of exam session state — proves integrity under failure conditions."
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Session List */}
        <div className="space-y-2">
          <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wide">Sessions</h3>
          {sessionsQuery.isLoading ? (
            <div className="space-y-2">
              <Skeleton className="h-14 w-full" />
              <Skeleton className="h-14 w-full" />
            </div>
          ) : (
            sessions.map((s) => (
              <div
                key={s.id}
                onClick={() => setSelectedId(s.id)}
                className={cn(
                  'rounded-lg border p-3 cursor-pointer transition-all',
                  selectedId === s.id ? 'border-brand-500 bg-brand-50' : 'border-slate-200 glass hover:border-slate-300'
                )}
              >
                <div className="flex items-center justify-between">
                  <Badge variant={s.status === 'SUBMITTED' ? 'success' : s.status === 'FAILED' ? 'danger' : 'info'}>
                    {s.status}
                  </Badge>
                  <span className="text-xs text-slate-400 font-mono">v{s.version}</span>
                </div>
                <p className="text-xs font-mono text-slate-400 mt-1 truncate">{s.id.slice(0, 18)}…</p>
              </div>
            ))
          )}
        </div>

        {/* State Detail */}
        <div className="lg:col-span-2">
          {!selectedId ? (
            <div className="rounded-lg border border-dashed border-slate-300 p-12 text-center">
              <p className="text-slate-400 text-sm">Select a session to inspect its state.</p>
            </div>
          ) : sessionQuery.isLoading ? (
            <Card><CardContent className="p-6"><Skeleton className="h-64 w-full" /></CardContent></Card>
          ) : session ? (
            <div className="space-y-4">
              <Card className={cn('border-2', getStatusColor(session.status))}>
                <CardContent className="p-6 text-center">
                  <p className="text-xs font-semibold uppercase tracking-wider mb-2 text-slate-500">Session Status</p>
                  <span className={cn('text-4xl font-bold tracking-tight', getStatusColor(session.status).split(' ')[0])}>
                    {session.status}
                  </span>
                </CardContent>
              </Card>

              <div className="grid grid-cols-2 gap-4">
                {[
                  { label: 'Version', value: String(session.version), mono: true },
                  { label: 'Session ID', value: session.id.slice(0, 18) + '…', mono: true },
                  { label: 'Started At', value: session.started_at ? new Date(session.started_at).toLocaleTimeString() : '—', mono: false },
                  { label: 'Submitted At', value: session.submitted_at ? new Date(session.submitted_at).toLocaleTimeString() : '—', mono: false },
                  { label: 'Last Activity', value: session.last_activity_at ? new Date(session.last_activity_at).toLocaleTimeString() : '—', mono: false },
                  { label: 'Updated At', value: new Date(session.updated_at).toLocaleTimeString(), mono: false },
                ].map((item) => (
                  <Card key={item.label}>
                    <CardContent className="p-4">
                      <p className="text-xs text-slate-500 mb-1">{item.label}</p>
                      <p className={cn('text-sm font-semibold text-slate-900', item.mono && 'font-mono')}>{item.value}</p>
                    </CardContent>
                  </Card>
                ))}
              </div>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm">Invariant Checks</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2 text-sm">
                  {[
                    { label: 'Session has active state', ok: session.status !== 'FAILED' },
                    { label: 'Can accept answers', ok: session.status === 'IN_PROGRESS' },
                    { label: 'Terminal state (submitted)', ok: session.status === 'SUBMITTED' },
                  ].map((check) => (
                    <div key={check.label} className="flex items-center justify-between py-1.5 border-b border-slate-100 last:border-0">
                      <span className="text-slate-500">{check.label}</span>
                      <StatusIndicator status={check.ok ? 'operational' : 'unavailable'} />
                    </div>
                  ))}
                </CardContent>
              </Card>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  )
}
