import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { ExamSession, EventTrace } from '@/types/domain'
import { useSessionTraces } from '@/services/examService'
import { PageHeader } from '@/components/ui/PageHeader'
import { Badge } from '@/components/ui/Badge'
import { Skeleton } from '@/components/ui/Skeleton'
import { cn } from '@/lib/utils'
import { apiClient } from '@/services/api'

const fetchSessions = async (): Promise<{ items: ExamSession[] }> => {
  const { data } = await apiClient.get<{ items: ExamSession[] }>('/api/v1/sessions')
  return data
}

const statusBadge = (status: string) => {
  if (status === 'PROCESSED') return <Badge variant="success">PROCESSED</Badge>
  if (status === 'DUPLICATE') return <Badge variant="warning">DUPLICATE</Badge>
  if (status === 'REJECTED' || status === 'FAILED') return <Badge variant="danger">{status}</Badge>
  return <Badge variant="neutral">{status}</Badge>
}

export const EventTracePage: React.FC = () => {
  const [selectedSessionId, setSelectedSessionId] = useState<string>('')

  const sessionsQuery = useQuery({
    queryKey: ['sessions'],
    queryFn: fetchSessions,
    refetchInterval: 5000,
  })

  const tracesQuery = useSessionTraces(selectedSessionId)

  const sessions = sessionsQuery.data?.items ?? []
  const events = tracesQuery.data?.items ?? []

  return (
    <div className="space-y-6">
      <PageHeader
        title="Event Traces"
        description="Inspect the complete event history for any exam session."
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Session List */}
        <div className="space-y-2">
          <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wide">Sessions</h3>
          {sessionsQuery.isLoading ? (
            <div className="space-y-2">
              <Skeleton className="h-16 w-full" />
              <Skeleton className="h-16 w-full" />
            </div>
          ) : sessions.length === 0 ? (
            <div className="rounded-lg border border-dashed border-slate-300 p-6 text-center">
              <p className="text-sm text-slate-400">No sessions yet. Start an exam.</p>
            </div>
          ) : (
            sessions.map((s) => (
              <div
                key={s.id}
                onClick={() => setSelectedSessionId(s.id)}
                className={cn(
                  'rounded-lg border p-3 cursor-pointer transition-all',
                  selectedSessionId === s.id
                    ? 'border-brand-500 bg-brand-50 shadow-sm'
                    : 'border-slate-200 glass hover:border-slate-300'
                )}
              >
                <div className="flex items-center justify-between mb-1">
                  <Badge variant={s.status === 'SUBMITTED' ? 'success' : s.status === 'FAILED' ? 'danger' : 'info'}>
                    {s.status}
                  </Badge>
                  <span className="text-xs text-slate-400">v{s.version}</span>
                </div>
                <p className="text-xs font-mono text-slate-500 truncate">{s.id}</p>
              </div>
            ))
          )}
        </div>

        {/* Event Trace Table */}
        <div className="lg:col-span-2">
          {!selectedSessionId ? (
            <div className="rounded-lg border border-dashed border-slate-300 p-12 text-center">
              <p className="text-slate-400 text-sm">Select a session to inspect its event trace.</p>
            </div>
          ) : tracesQuery.isLoading ? (
            <div className="space-y-2">
              <Skeleton className="h-12 w-full" />
              <Skeleton className="h-12 w-full" />
              <Skeleton className="h-12 w-full" />
            </div>
          ) : events.length === 0 ? (
            <div className="rounded-lg border border-dashed border-slate-300 p-8 text-center">
              <p className="text-sm text-slate-400">No events found for this session.</p>
            </div>
          ) : (
            <div className="rounded-lg border border-slate-200 overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-white/40 backdrop-blur-md border-b border-slate-200">
                  <tr>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">#</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Event</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Status</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Occurred</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Delay</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {events.map((ev: EventTrace) => (
                    <tr
                      key={ev.event_id}
                      className={cn(
                        'hover:bg-white/40 backdrop-blur-md transition-colors',
                        ev.status === 'DUPLICATE' && 'bg-amber-50/70',
                        (ev.status === 'REJECTED' || ev.status === 'FAILED') && 'bg-rose-50/70'
                      )}
                    >
                      <td className="px-4 py-3 text-xs font-mono text-slate-400">{ev.sequence_number}</td>
                      <td className="px-4 py-3">
                        <span className="font-medium text-slate-800">{ev.event_type}</span>
                        {ev.error_message && (
                          <p className="text-xs text-rose-500 mt-0.5 truncate max-w-xs">{ev.error_message}</p>
                        )}
                      </td>
                      <td className="px-4 py-3">{statusBadge(ev.status)}</td>
                      <td className="px-4 py-3 text-xs font-mono text-slate-500">
                        {new Date(ev.occurred_at).toLocaleTimeString()}
                      </td>
                      <td className="px-4 py-3 text-xs font-mono text-slate-500">
                        {ev.delay_ms > 0 ? `${ev.delay_ms}ms` : '< 1ms'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
