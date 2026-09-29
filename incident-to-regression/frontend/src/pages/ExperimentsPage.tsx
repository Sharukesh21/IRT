import React from 'react'
import { PageHeader } from '@/components/ui/PageHeader'
import { EmptyState } from '@/components/ui/EmptyState'
import { FlaskConical } from 'lucide-react'

export const ExperimentsPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <PageHeader 
        title="Experiments" 
        description="Run evaluation experiments against historical baselines."
      />
      <EmptyState 
        icon={<FlaskConical className="h-6 w-6" />}
        title="No Experiments"
        description="Create an evaluation experiment to see data."
      />
    </div>
  )
}
