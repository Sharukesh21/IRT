import React from 'react'
import { cn } from '@/lib/utils'

interface PageHeaderProps extends React.HTMLAttributes<HTMLDivElement> {
  title: string
  description?: string
  badge?: React.ReactNode
  actions?: React.ReactNode
}

export const PageHeader: React.FC<PageHeaderProps> = ({
  title,
  description,
  badge,
  actions,
  className,
  ...props
}) => {
  return (
    <div className={cn('flex flex-col sm:flex-row sm:items-center sm:justify-between pb-6 mb-6 border-b border-slate-200', className)} {...props}>
      <div className="flex-1 min-w-0">
        <div className="flex items-center space-x-3 mb-1">
          <h1 className="text-2xl font-bold leading-7 text-slate-900 sm:truncate sm:tracking-tight">
            {title}
          </h1>
          {badge && <div>{badge}</div>}
        </div>
        {description && (
          <p className="text-sm text-slate-500">
            {description}
          </p>
        )}
      </div>
      {actions && (
        <div className="mt-4 flex sm:mt-0 sm:ml-4 space-x-3">
          {actions}
        </div>
      )}
    </div>
  )
}
