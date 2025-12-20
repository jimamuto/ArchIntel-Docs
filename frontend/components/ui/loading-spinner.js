import * as React from "react"
import { motion } from "framer-motion"

export function LoadingSpinner({ 
  size = "md", 
  className, 
  text,
  variant = "dots"
}) {
  const sizeClasses = {
    sm: "w-4 h-4",
    md: "w-6 h-6", 
    lg: "w-8 h-8"
  }

  if (variant === "dots") {
    return (
      <div className={`flex items-center gap-2 ${className || ''}`}>
        <div className="flex gap-1">
          {[0, 1, 2].map((i) => (
            <motion.div
              key={i}
              className={`w-2 h-2 rounded-full bg-gradient-to-r from-cyan-500 to-emerald-500`}
              animate={{ 
                y: [0, -8, 0],
                opacity: [0.3, 1, 0.3]
              }}
              transition={{
                duration: 0.6,
                ease: "easeInOut",
                delay: i * 0.15,
                repeat: Infinity
              }}
            />
          ))}
        </div>
        {text && <span className="text-sm text-slate-400">{text}</span>}
      </div>
    )
  }

  if (variant === "ring") {
    return (
      <div className={`flex items-center gap-3 ${className || ''}`}>
        <motion.div
          className={`rounded-full border-2 border-slate-700 border-t-cyan-500 ${sizeClasses[size]}`}
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
        />
        {text && <span className="text-sm text-slate-400">{text}</span>}
      </div>
    )
  }

  if (variant === "pulse") {
    return (
      <div className={`flex items-center gap-3 ${className || ''}`}>
        <motion.div
          className={`w-3 h-3 rounded-full bg-cyan-500`}
          animate={{ 
            scale: [1, 2, 1],
            opacity: [1, 0.3, 1]
          }}
          transition={{
            duration: 1.5,
            ease: "easeInOut",
            repeat: Infinity
          }}
        />
        {text && <span className="text-sm text-slate-400">{text}</span>}
      </div>
    )
  }

  return null
}

export function Skeleton({ 
  className, 
  variant = "rounded",
  animation = "pulse"
}) {
  const baseClasses = "bg-slate-800/50"
  const variantClasses = {
    rounded: "rounded-lg",
    circle: "rounded-full",
    none: ""
  }
  const animationClasses = {
    pulse: "animate-pulse",
    wave: "bg-gradient-to-r from-transparent via-slate-700/50 to-transparent bg-[length:200%_100%] animate-[shimmer_2s_infinite]",
    none: ""
  }

  return (
    <div 
      className={`${baseClasses} ${variantClasses[variant]} ${animationClasses[animation]} ${className || ''}`}
      style={{
        animation: animation === "wave" ? "shimmer 2s infinite" : undefined
      }}
    />
  )
}

export function ProgressRing({ 
  progress = 0, 
  size = 80, 
  strokeWidth = 8,
  className 
}) {
  const radius = (size - strokeWidth) / 2
  const circumference = radius * 2 * Math.PI

  return (
    <div className={`relative ${className || ''}`} style={{ width: size, height: size }}>
      <svg className="rotate-[-90deg]" width={size} height={size}>
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="rgba(255, 255, 255, 0.1)"
          strokeWidth={strokeWidth}
          fill="transparent"
        />
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="url(#gradient)"
          strokeWidth={strokeWidth}
          fill="transparent"
          strokeLinecap="round"
          initial={{ strokeDasharray: `${circumference} ${circumference}`, strokeDashoffset: circumference }}
          animate={{ 
            strokeDasharray: `${circumference} ${circumference}`,
            strokeDashoffset: circumference * (1 - Math.min(Math.max(progress, 0), 1))
          }}
          transition={{ duration: 0.8, ease: "easeOut" }}
        />
        <defs>
          <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#06b6d4" />
            <stop offset="50%" stopColor="#10b981" />
            <stop offset="100%" stopColor="#06b6d4" />
          </linearGradient>
        </defs>
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        <span className="text-sm font-semibold text-slate-300">{Math.round(progress * 100)}%</span>
      </div>
    </div>
  )
}

export function ToastContainer({ toasts, onDismiss }) {
  return (
    <div className="fixed top-4 right-4 z-50 space-y-3">
      {toasts.map((toast) => (
        <motion.div
          key={toast.id}
          initial={{ opacity: 0, x: 100, scale: 0.95 }}
          animate={{ opacity: 1, x: 0, scale: 1 }}
          exit={{ opacity: 0, x: 100, scale: 0.95 }}
          transition={{ type: "spring", damping: 25, stiffness: 300 }}
          className={`p-4 rounded-lg border border-slate-700/50 backdrop-blur-sm ${
            toast.type === "success" ? "bg-emerald-500/10 text-emerald-300" :
            toast.type === "error" ? "bg-rose-500/10 text-rose-300" :
            toast.type === "warning" ? "bg-amber-500/10 text-amber-300" :
            "bg-slate-800/50 text-slate-300"
          }`}
        >
          <div className="flex items-center gap-3">
            <div className={`w-2 h-2 rounded-full ${
              toast.type === "success" ? "bg-emerald-500" :
              toast.type === "error" ? "bg-rose-500" :
              toast.type === "warning" ? "bg-amber-500" :
              "bg-cyan-500"
            }`} />
            <div className="flex-1">
              <div className="font-medium">{toast.title}</div>
              {toast.message && <div className="text-sm opacity-80 mt-1">{toast.message}</div>}
            </div>
            <button
              onClick={() => onDismiss(toast.id)}
              className="ml-2 p-1 rounded-md hover:bg-slate-700/50 transition-colors"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </motion.div>
      ))}
    </div>
  )
}
