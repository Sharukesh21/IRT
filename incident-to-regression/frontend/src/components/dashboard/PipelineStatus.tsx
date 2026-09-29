import React from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '../ui/Card'
import { Badge } from '../ui/Badge'
import { Activity, AlertTriangle, CheckSquare, PlayCircle, BarChart3, ArrowRight } from 'lucide-react'
import { cn } from '@/lib/utils'

const pipelineStages = [
  { id: 'incidents', name: 'Incident Capture', icon: AlertTriangle, status: 'pending', phase: 'Phase 2' },
  { id: 'events', name: 'Event Processing', icon: Activity, status: 'pending', phase: 'Phase 2' },
  { id: 'generation', name: 'Test Generation', icon: CheckSquare, status: 'pending', phase: 'Phase 3' },
  { id: 'execution', name: 'Test Execution', icon: PlayCircle, status: 'pending', phase: 'Phase 3' },
  { id: 'evaluation', name: 'Evaluation', icon: BarChart3, status: 'pending', phase: 'Phase 4' },
]

export const PipelineStatus: React.FC = () => {
  return (
    <Card>
      <CardHeader className="pb-4 border-b border-slate-100">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">Pipeline Architecture</CardTitle>
          <Badge variant="info">Implementation Roadmap</Badge>
        </div>
      </CardHeader>
      <CardContent className="pt-6 overflow-x-auto">
        <div className="flex items-center min-w-[700px] justify-between px-2">
          {pipelineStages.map((stage, index) => (
            <React.Fragment key={stage.id}>
              {/* Stage Card */}
              <div className="flex flex-col items-center flex-1">
                <div className={cn(
                  "h-14 w-14 rounded-2xl flex items-center justify-center shadow-sm mb-3 transition-colors",
                  "bg-white/50 backdrop-blur-lg text-slate-400 border border-slate-200"
                )}>
                  <stage.icon className="h-6 w-6" />
                </div>
                <span className="text-sm font-medium text-slate-700 text-center">{stage.name}</span>
                <span className="text-xs text-slate-400 mt-1">{stage.phase}</span>
              </div>

              {/* Connector */}
              {index < pipelineStages.length - 1 && (
                <div className="flex-1 flex justify-center mb-8">
                  <ArrowRight className="text-slate-300 h-5 w-5" />
                </div>
              )}
            </React.Fragment>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
