import React from 'react'
import { Loader2, CheckCircle2, XCircle, Clock } from 'lucide-react'

interface Props {
  status: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED'
  elapsed?: number
  className?: string
}

export const JobStatusBadge: React.FC<Props> = ({ status, elapsed, className = '' }) => {
  const config = {
    PENDING:   { color: 'bg-yellow-100 text-yellow-800', icon: <Clock className="w-3 h-3" />, label: 'Pending' },
    RUNNING:   { color: 'bg-blue-100 text-blue-800',   icon: <Loader2 className="w-3 h-3 animate-spin" />, label: 'Running' },
    COMPLETED: { color: 'bg-green-100 text-green-800', icon: <CheckCircle2 className="w-3 h-3" />, label: 'Completed' },
    FAILED:    { color: 'bg-red-100 text-red-800',     icon: <XCircle className="w-3 h-3" />, label: 'Failed' },
  }[status]
  
  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${config.color} ${className}`}>
      {config.icon}
      {config.label}
      {elapsed !== undefined && <span className="opacity-70">({elapsed}s)</span>}
    </span>
  )
}
