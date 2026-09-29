import React from 'react'
import { useToast } from '@/hooks/useToast'

export const ToastContainer: React.FC = () => {
  const { toasts } = useToast()
  
  if (toasts.length === 0) return null
  
  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2">
      {toasts.map(toast => {
        const bg = {
          success: 'bg-green-100 border-green-200 text-green-800',
          error: 'bg-red-100 border-red-200 text-red-800',
          warning: 'bg-yellow-100 border-yellow-200 text-yellow-800',
          info: 'bg-blue-100 border-blue-200 text-blue-800'
        }[toast.type]
        
        return (
          <div key={toast.id} className={`px-4 py-3 rounded-lg border shadow-sm flex items-center min-w-[300px] ${bg}`}>
            <span className="text-sm font-medium">{toast.message}</span>
          </div>
        )
      })}
    </div>
  )
}
