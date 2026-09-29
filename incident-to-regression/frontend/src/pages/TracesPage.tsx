import React from 'react'
import { PageHeader } from '@/components/ui/PageHeader'
import { EmptyState } from '@/components/ui/EmptyState'
import { Activity } from 'lucide-react'

export const TracesPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <PageHeader 
        title="Event Traces" 
        description="View end-to-end event traces and observability data."
      />
      <EmptyState 
        icon={<Activity className="h-6 w-6" />}
        title="No Event Traces"
        description="Connect tracing infrastructure or run a test to see event logs."
      />
    </div>
  )
}
