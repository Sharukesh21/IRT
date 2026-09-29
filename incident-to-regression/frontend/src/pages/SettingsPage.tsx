import React from 'react'
import { PageHeader } from '@/components/ui/PageHeader'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { useSystemStatus } from '@/hooks/useSystemStatus'

export const SettingsPage: React.FC = () => {
  const { environment } = useSystemStatus()

  return (
    <div className="space-y-6">
      <PageHeader title="Settings" description="System configuration and environment details" />

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Environment Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4 border-b border-slate-100 pb-4">
              <span className="text-sm font-medium text-slate-500">Current Environment</span>
              <span className="text-sm text-slate-900 capitalize font-medium">{environment}</span>
            </div>
            <div className="grid grid-cols-2 gap-4 border-b border-slate-100 pb-4">
              <span className="text-sm font-medium text-slate-500">API Endpoint</span>
              <span className="text-sm text-slate-900 font-mono truncate">
                {import.meta.env.VITE_API_URL || 'http://localhost:8000'}
              </span>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <span className="text-sm font-medium text-slate-500">Frontend Version</span>
              <span className="text-sm text-slate-900 font-mono">0.1.0</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Project Phases</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center space-x-2">
              <div className="h-2 w-2 rounded-full bg-emerald-500" />
              <span className="text-sm font-medium">Phase 1: Foundation (Current)</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="h-2 w-2 rounded-full bg-slate-300" />
              <span className="text-sm text-slate-500">Phase 2: Exam Simulator + Events</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="h-2 w-2 rounded-full bg-slate-300" />
              <span className="text-sm text-slate-500">Phase 3: Incident Engine + Tests</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="h-2 w-2 rounded-full bg-slate-300" />
              <span className="text-sm text-slate-500">Phase 4: Evaluation + Metrics</span>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
