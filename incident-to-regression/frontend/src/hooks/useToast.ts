import { useState, useEffect } from 'react'

export type ToastType = 'success' | 'error' | 'warning' | 'info'

export interface Toast {
  id: string
  message: string
  type: ToastType
}

let toasts: Toast[] = []
let listeners: Array<() => void> = []

function emitChange() {
  for (const listener of listeners) {
    listener()
  }
}

export const toastService = {
  show(message: string, type: ToastType) {
    const id = Math.random().toString(36).substring(2, 9)
    toasts = [...toasts, { id, message, type }]
    emitChange()
    setTimeout(() => {
      this.remove(id)
    }, 5000)
  },
  remove(id: string) {
    toasts = toasts.filter(t => t.id !== id)
    emitChange()
  }
}

export function useToast() {
  const [state, setState] = useState<Toast[]>([])
  
  useEffect(() => {
    setState(toasts)
    const listener = () => setState(toasts)
    listeners.push(listener)
    return () => {
      listeners = listeners.filter(l => l !== listener)
    }
  }, [])
  
  return { toasts: state, showToast: toastService.show.bind(toastService) }
}
