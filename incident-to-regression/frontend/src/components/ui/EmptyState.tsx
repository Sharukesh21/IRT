import React from 'react'
import { cn } from '@/lib/utils'

interface EmptyStateProps extends React.HTMLAttributes<HTMLDivElement> {
  icon: React.ReactNode
  title: string
  description: string
  action?: React.ReactNode
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  icon,
  title,
  description,
  action,
  className,
  ...props
}) => {
  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center rounded-lg border border-dashed border-slate-300 p-12 text-center animate-fade-in',
        className
      )}
      {...props}
    >
      <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-white/50 backdrop-blur-lg text-slate-500 mb-4">
        {icon}
      </div>
      <h3 className="text-lg font-semibold text-slate-900 mb-1">{title}</h3>
      <p className="text-sm text-slate-500 max-w-md mb-6">{description}</p>
      {action && <div>{action}</div>}
    </div>
  )
}
