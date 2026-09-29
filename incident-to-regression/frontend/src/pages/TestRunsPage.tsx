import React from 'react'
import { PageHeader } from '@/components/ui/PageHeader'
import { EmptyState } from '@/components/ui/EmptyState'
import { PlayCircle } from 'lucide-react'

export const TestRunsPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <PageHeader 
        title="Test Runs" 
        description="History and status of all regression test executions."
      />
      <EmptyState 
        icon={<PlayCircle className="h-6 w-6" />}
        title="No Test Runs"
        description="Execute a regression test to see results here."
      />
    </div>
  )
}
