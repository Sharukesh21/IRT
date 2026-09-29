import React from 'react'
import { PageHeader } from '@/components/ui/PageHeader'
import { MetricCard } from '@/components/ui/MetricCard'
import { Badge } from '@/components/ui/Badge'
import { EmptyState } from '@/components/ui/EmptyState'
import { SystemStatusCard } from '@/components/dashboard/SystemStatus'
import { PipelineStatus } from '@/components/dashboard/PipelineStatus'
import { AlertTriangle, CheckSquare, CheckCircle2, Percent, ListPlus } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/services/api'
import { Skeleton } from '@/components/ui/Skeleton'

interface DashboardData {
  incidents: { total: number; open: number; critical: number }
  regressions: { total_tests: number; passing: number; failing: number }
  ci: { runs: number; pass_rate: number }
  escapes: { total: number; last_30_days: number }
}

export const OverviewPage: React.FC = () => {
  const { data, isLoading } = useQuery({
    queryKey: ['dashboard_overview'],
    queryFn: async () => {
      const res = await apiClient.get<DashboardData>('/api/v1/dashboard/overview')
      return res.data
    }
  })

  return (
    <div className="space-y-6">
      <PageHeader 
        title="Overview" 
        description="System health and pipeline status"
        badge={<Badge variant="info" className="ml-3">Phase 1 — Foundation</Badge>}
      />

      {/* Metrics Row - Fetched from backend */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {isLoading ? (
          <>
            <Skeleton className="h-32 rounded-xl" />
            <Skeleton className="h-32 rounded-xl" />
            <Skeleton className="h-32 rounded-xl" />
            <Skeleton className="h-32 rounded-xl" />
          </>
        ) : (
          <>
            <MetricCard 
              metric={{ label: 'Total Incidents', value: data?.incidents.total || 0, subtitle: `${data?.incidents.open || 0} open incidents` }}
              icon={<AlertTriangle className="h-5 w-5" />}
            />
            <MetricCard 
              metric={{ label: 'Regression Tests', value: data?.regressions.total_tests || 0, subtitle: 'Tests generated' }}
              icon={<CheckSquare className="h-5 w-5" />}
            />
            <MetricCard 
              metric={{ label: 'Passing Tests', value: data?.regressions.passing || 0, subtitle: `${data?.regressions.failing || 0} failing` }}
              icon={<CheckCircle2 className="h-5 w-5" />}
            />
            <MetricCard 
              metric={{ label: 'CI Pass Rate', value: `${((data?.ci.pass_rate || 0) * 100).toFixed(1)}%`, subtitle: `${data?.ci.runs || 0} total runs` }}
              icon={<Percent className="h-5 w-5" />}
            />
          </>
        )}
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Pipeline & Activity */}
        <div className="lg:col-span-2 space-y-6">
          <PipelineStatus />
          
          <div className="glass rounded-lg border border-slate-200 p-6 shadow-sm">
            <h3 className="text-lg font-semibold text-slate-900 mb-4">Recent Activity</h3>
            <EmptyState 
              icon={<ListPlus className="h-6 w-6" />}
              title="No recent activity"
              description="Start by capturing your first incident in the system."
              className="border-none shadow-none bg-white/40 backdrop-blur-md"
            />
          </div>
        </div>

        {/* Right Column: System Status */}
        <div className="space-y-6">
          <SystemStatusCard />
        </div>
      </div>
    </div>
  )
}
