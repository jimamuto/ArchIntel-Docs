import * as React from "react"

// Toast context
const ToastContext = React.createContext()

export function useToast() {
  const context = React.useContext(ToastContext)
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider')
  }
  return context
}

// Toast provider
export function ToastProvider({ children }) {
  const [toasts, setToasts] = React.useState([])

  const addToast = React.useCallback((toast) => {
    const id = toast.id || Math.random().toString(36).substr(2, 9)
    const newToast = {
      id,
      type: toast.type || 'info',
      title: toast.title,
      message: toast.message,
      duration: toast.duration || 5000,
      persistent: toast.persistent || false
    }

    setToasts(prev => [...prev, newToast])

    if (!newToast.persistent) {
      setTimeout(() => {
        removeToast(id)
      }, newToast.duration)
    }

    return id
  }, [])

  const removeToast = React.useCallback((id) => {
    setToasts(prev => prev.filter(toast => toast.id !== id))
  }, [])

  const success = React.useCallback((title, message, options = {}) => {
    return addToast({ type: 'success', title, message, ...options })
  }, [addToast])

  const error = React.useCallback((title, message, options = {}) => {
    return addToast({ type: 'error', title, message, ...options })
  }, [addToast])

  const warning = React.useCallback((title, message, options = {}) => {
    return addToast({ type: 'warning', title, message, ...options })
  }, [addToast])

  const info = React.useCallback((title, message, options = {}) => {
    return addToast({ type: 'info', title, message, ...options })
  }, [addToast])

  const value = {
    toasts,
    addToast,
    removeToast,
    success,
    error,
    warning,
    info
  }

  return (
    <ToastContext.Provider value={value}>
      {children}
      <ToastContainer toasts={toasts} onDismiss={removeToast} />
    </ToastContext.Provider>
  )
}

// Toast container component
function ToastContainer({ toasts, onDismiss }) {
  return (
    <div className="fixed top-4 right-4 z-50 space-y-3">
      {toasts.map((toast) => (
        <ToastItem key={toast.id} toast={toast} onDismiss={onDismiss} />
      ))}
    </div>
  )
}

// Individual toast item
function ToastItem({ toast, onDismiss }) {
  const getToastStyles = (type) => {
    switch (type) {
      case 'success':
        return {
          bg: 'bg-emerald-500/10',
          border: 'border-emerald-500/20',
          text: 'text-emerald-300',
          icon: '✓'
        }
      case 'error':
        return {
          bg: 'bg-rose-500/10',
          border: 'border-rose-500/20',
          text: 'text-rose-300',
          icon: '✗'
        }
      case 'warning':
        return {
          bg: 'bg-amber-500/10',
          border: 'border-amber-500/20',
          text: 'text-amber-300',
          icon: '⚠'
        }
      default:
        return {
          bg: 'bg-slate-800/50',
          border: 'border-slate-700/50',
          text: 'text-slate-300',
          icon: '•'
        }
    }
  }

  const styles = getToastStyles(toast.type)

  return (
    <div
      className={`p-4 rounded-lg border backdrop-blur-sm ${styles.bg} ${styles.border} ${styles.text} shadow-lg shadow-black/20`}
    >
      <div className="flex items-start gap-3">
        <div className={`w-6 h-6 rounded-full bg-gradient-to-br from-cyan-500/20 to-emerald-500/20 flex items-center justify-center text-xs font-bold ${toast.type === 'error' ? 'from-rose-500/20 to-rose-400/20' : ''} ${toast.type === 'warning' ? 'from-amber-500/20 to-amber-400/20' : ''}`}>
          {toast.type === 'success' ? '✓' : 
           toast.type === 'error' ? '✗' : 
           toast.type === 'warning' ? '⚠' : '•'}
        </div>
        <div className="flex-1">
          <div className="font-medium">{toast.title}</div>
          {toast.message && (
            <div className="text-sm opacity-80 mt-1">{toast.message}</div>
          )}
        </div>
        <button
          onClick={() => onDismiss(toast.id)}
          className="ml-2 p-1 rounded-md hover:bg-slate-700/50 transition-colors"
          aria-label="Close notification"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>
  )
}

// Toast hook for easy use
export function useNotifications() {
  const { success, error, warning, info } = useToast()

  return {
    success,
    error,
    warning,
    info
  }
}
