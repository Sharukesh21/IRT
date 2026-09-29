import React from 'react'
import { PageHeader } from '@/components/ui/PageHeader'
import { EmptyState } from '@/components/ui/EmptyState'
import { Badge } from '@/components/ui/Badge'
import { AlertTriangle, Activity, CheckSquare, PlayCircle, Zap, FlaskConical, BarChart3 } from 'lucide-react'

const createPlaceholderPage = (title: string, icon: React.ReactNode, phase: string) => {
  const Placeholder: React.FC = () => (
    <div className="space-y-6">
      <PageHeader 
        title={title} 
        badge={<Badge variant="neutral" className="ml-3">{phase} Feature</Badge>}
      />
      <EmptyState 
        icon={icon}
        title={`${title} not yet available`}
        description={`The ${title.toLowerCase()} system will be implemented in ${phase}.`}
        className="mt-8"
      />
    </div>
  )
  return Placeholder
}

export const IncidentsPage = createPlaceholderPage('Incidents', <AlertTriangle className="h-6 w-6" />, 'Phase 2')
export const TracesPage = createPlaceholderPage('Event Traces', <Activity className="h-6 w-6" />, 'Phase 2')
export const RegressionTestsPage = createPlaceholderPage('Regression Tests', <CheckSquare className="h-6 w-6" />, 'Phase 3')
export const TestRunsPage = createPlaceholderPage('Test Runs', <PlayCircle className="h-6 w-6" />, 'Phase 3')
export const SimulatorPage = createPlaceholderPage('Failure Simulator', <Zap className="h-6 w-6" />, 'Phase 2')
export const ExperimentsPage = createPlaceholderPage('Experiments', <FlaskConical className="h-6 w-6" />, 'Phase 4')
export const MetricsPage = createPlaceholderPage('Metrics', <BarChart3 className="h-6 w-6" />, 'Phase 4')
