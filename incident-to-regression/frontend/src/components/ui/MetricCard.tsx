import React from 'react'
import { cn } from '@/lib/utils'
import { MetricCardData } from '@/types'
import { Card, CardContent } from './Card'

interface MetricCardProps extends React.HTMLAttributes<HTMLDivElement> {
  metric: MetricCardData
  icon?: React.ReactNode
}

export const MetricCard: React.FC<MetricCardProps> = ({ metric, icon, className, ...props }) => {
  const { label, value, subtitle, trend } = metric

  return (
    <Card className={cn('overflow-hidden', className)} {...props}>
      <CardContent className="p-6 flex flex-col h-full">
        <div className="flex items-center justify-between mb-4">
          <span className="text-sm font-medium text-slate-500 truncate pr-4">{label}</span>
          {icon && <div className="text-brand-500 bg-brand-50 p-2 rounded-lg flex-shrink-0">{icon}</div>}
        </div>
        
        <div className="mt-auto">
          <div className="text-3xl font-bold text-slate-900 tracking-tight">{value}</div>
          
          <div className="mt-2 flex items-center text-xs">
            {trend ? (
              <>
                <span className={cn('font-medium', trend.isPositive ? 'text-emerald-600' : 'text-rose-600')}>
                  {trend.isPositive ? '+' : '-'}{trend.value}%
                </span>
                <span className="text-slate-500 ml-1.5 line-clamp-1">{subtitle}</span>
              </>
            ) : (
              <span className="text-slate-500 line-clamp-1">{subtitle}</span>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
