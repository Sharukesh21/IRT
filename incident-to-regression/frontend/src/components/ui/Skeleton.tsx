import React from 'react'
import { cn } from '@/lib/utils'

export type SkeletonProps = React.HTMLAttributes<HTMLDivElement>

export const Skeleton: React.FC<SkeletonProps> = ({ className, ...props }) => {
  return (
    <div
      className={cn('animate-pulse rounded-md bg-slate-200', className)}
      {...props}
    />
  )
}

export const SkeletonText: React.FC<{ lines?: number; className?: string }> = ({ lines = 1, className }) => (
  <div className={cn('space-y-2', className)}>
    {Array.from({ length: lines }).map((_, i) => (
      <Skeleton key={i} className={cn('h-4 w-full', i === lines - 1 && lines > 1 ? 'w-2/3' : '')} />
    ))}
  </div>
)

export const SkeletonCard: React.FC<{ className?: string }> = ({ className }) => (
  <div className={cn('rounded-lg border border-slate-200 p-6 shadow-sm', className)}>
    <Skeleton className="h-6 w-1/3 mb-4" />
    <SkeletonText lines={3} />
  </div>
)

export const SkeletonMetricCard: React.FC<{ className?: string }> = ({ className }) => (
  <div className={cn('rounded-lg border border-slate-200 p-6 shadow-sm flex flex-col', className)}>
    <Skeleton className="h-4 w-1/2 mb-2" />
    <Skeleton className="h-8 w-1/3 mb-1" />
    <Skeleton className="h-3 w-2/3 mt-auto" />
  </div>
)
