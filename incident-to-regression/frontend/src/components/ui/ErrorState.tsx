import React from 'react'
import { AlertCircle } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from './Button'

interface ErrorStateProps extends React.HTMLAttributes<HTMLDivElement> {
  title?: string
  message: string
  onRetry?: () => void
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title = 'Something went wrong',
  message,
  onRetry,
  className,
  ...props
}) => {
  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center rounded-lg border border-red-200 bg-red-50 p-8 text-center',
        className
      )}
      {...props}
    >
      <AlertCircle className="h-10 w-10 text-red-500 mb-3" />
      <h3 className="text-lg font-medium text-red-900 mb-1">{title}</h3>
      <p className="text-sm text-red-700 max-w-md mb-5">{message}</p>
      {onRetry && (
        <Button variant="danger" size="sm" onClick={onRetry}>
          Try Again
        </Button>
      )}
    </div>
  )
}
