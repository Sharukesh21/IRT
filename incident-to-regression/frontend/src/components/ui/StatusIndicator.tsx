import React from 'react'
import { cn } from '@/lib/utils'

export type Status = 'operational' | 'degraded' | 'unavailable' | 'checking' | 'connected' | 'disconnected'

interface StatusIndicatorProps {
  status: Status
  label?: string
  className?: string
}

export const StatusIndicator: React.FC<StatusIndicatorProps> = ({ status, label, className }) => {
  const getStatusColor = () => {
    switch (status) {
      case 'operational':
      case 'connected':
        return 'bg-status-operational'
      case 'degraded':
        return 'bg-status-degraded'
      case 'unavailable':
      case 'disconnected':
        return 'bg-status-unavailable'
      case 'checking':
        return 'bg-status-checking'
      default:
        return 'bg-slate-400'
    }
  }

  const isPulsing = status === 'operational' || status === 'connected' || status === 'checking'

  return (
    <div className={cn('flex items-center space-x-2', className)}>
      <span className="relative flex h-3 w-3">
        {isPulsing && (
          <span className={cn('animate-ping absolute inline-flex h-full w-full rounded-full opacity-75', getStatusColor())} />
        )}
        <span className={cn('relative inline-flex rounded-full h-3 w-3', getStatusColor())} />
      </span>
      {label && <span className="text-sm font-medium text-slate-700 capitalize">{label || status}</span>}
    </div>
  )
}
