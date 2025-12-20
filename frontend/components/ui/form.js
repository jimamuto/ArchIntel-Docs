import * as React from "react"
import { motion, AnimatePresence } from "framer-motion"

export function Form({ children, onSubmit, className, ...props }) {
  const handleSubmit = (e) => {
    e.preventDefault()
    if (onSubmit) onSubmit(e)
  }

  return (
    <form onSubmit={handleSubmit} className={`space-y-4 ${className || ''}`} {...props}>
      {children}
    </form>
  )
}

export function FormField({ 
  label, 
  error, 
  helpText, 
  required, 
  children, 
  className 
}) {
  return (
    <div className={`space-y-2 ${className || ''}`}>
      {label && (
        <label className="flex items-center gap-2 text-sm font-medium text-slate-300">
          {label}
          {required && <span className="text-rose-400">*</span>}
        </label>
      )}
      <AnimatePresence mode="wait">
        {children}
      </AnimatePresence>
      {error ? (
        <motion.p
          initial={{ opacity: 0, y: -5 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-sm text-rose-400"
        >
          {error}
        </motion.p>
      ) : helpText ? (
        <motion.p
          initial={{ opacity: 0, y: -5 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-sm text-slate-400"
        >
          {helpText}
        </motion.p>
      ) : null}
    </div>
  )
}

export function Input({ 
  type = "text", 
  placeholder, 
  value, 
  onChange, 
  className, 
  icon,
  error,
  ...props 
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 5 }}
      animate={{ opacity: 1, y: 0 }}
      className="relative"
    >
      {icon && (
        <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400">
          {icon}
        </div>
      )}
      <input
        type={type}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        className={`w-full px-4 py-3 rounded-lg border border-slate-700/50 bg-slate-800/30 text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/30 focus:border-cyan-500/50 transition-all duration-200 ${
          icon ? 'pl-10' : ''
        } ${error ? 'border-rose-500/50 ring-rose-500/20' : ''} ${className || ''}`}
        {...props}
      />
    </motion.div>
  )
}

export function Textarea({ 
  placeholder, 
  value, 
  onChange, 
  rows = 4, 
  className, 
  error,
  ...props 
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 5 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <textarea
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        rows={rows}
        className={`w-full px-4 py-3 rounded-lg border border-slate-700/50 bg-slate-800/30 text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/30 focus:border-cyan-500/50 transition-all duration-200 resize-none ${error ? 'border-rose-500/50 ring-rose-500/20' : ''} ${className || ''}`}
        {...props}
      />
    </motion.div>
  )
}

export function Select({ 
  children, 
  value, 
  onChange, 
  className, 
  error,
  ...props 
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 5 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <select
        value={value}
        onChange={onChange}
        className={`w-full px-4 py-3 rounded-lg border border-slate-700/50 bg-slate-800/30 text-slate-200 focus:outline-none focus:ring-2 focus:ring-cyan-500/30 focus:border-cyan-500/50 transition-all duration-200 appearance-none ${error ? 'border-rose-500/50 ring-rose-500/20' : ''} ${className || ''}`}
        {...props}
      >
        {children}
      </select>
      <div className="absolute right-3 top-1/2 transform -translate-y-1/2 pointer-events-none">
        <svg className="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </div>
    </motion.div>
  )
}

export function Checkbox({ 
  checked, 
  onChange, 
  label, 
  className, 
  ...props 
}) {
  return (
    <motion.label
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      className={`flex items-center gap-3 cursor-pointer ${className || ''}`}
      {...props}
    >
      <motion.input
        type="checkbox"
        checked={checked}
        onChange={onChange}
        className="w-4 h-4 rounded border border-slate-600 bg-slate-800 text-cyan-500 focus:ring-2 focus:ring-cyan-500/30 focus:ring-offset-0 transition-colors"
      />
      <span className="text-sm text-slate-300">{label}</span>
    </motion.label>
  )
}

export function RadioGroup({ 
  options, 
  value, 
  onChange, 
  className, 
  ...props 
}) {
  return (
    <div className={`space-y-2 ${className || ''}`} {...props}>
      {options.map((option, index) => (
        <motion.label
          key={index}
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: index * 0.1 }}
          className="flex items-center gap-3 cursor-pointer"
        >
          <motion.input
            type="radio"
            name="radio-group"
            value={option.value}
            checked={value === option.value}
            onChange={() => onChange(option.value)}
            className="w-4 h-4 border border-slate-600 bg-slate-800 text-cyan-500 focus:ring-2 focus:ring-cyan-500/30 focus:ring-offset-0 transition-colors"
          />
          <div>
            <div className="text-sm font-medium text-slate-300">{option.label}</div>
            {option.description && (
              <div className="text-xs text-slate-400">{option.description}</div>
            )}
          </div>
        </motion.label>
      ))}
    </div>
  )
}

export function Toggle({ 
  enabled, 
  setEnabled, 
  label, 
  className, 
  ...props 
}) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      className={`flex items-center gap-3 ${className || ''}`}
      {...props}
    >
      <button
        type="button"
        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors duration-200 ${
          enabled ? 'bg-cyan-500/20 border border-cyan-500/30' : 'bg-slate-700/30 border border-slate-600'
        }`}
        onClick={() => setEnabled(!enabled)}
      >
        <motion.span
          layout
          transition={{ type: "spring", stiffness: 500, damping: 30 }}
          className={`h-4 w-4 rounded-full ${
            enabled ? 'bg-gradient-to-r from-cyan-500 to-emerald-500' : 'bg-slate-300'
          }`}
        />
      </button>
      {label && (
        <span className="text-sm text-slate-300">{label}</span>
      )}
    </motion.div>
  )
}

export function FormActions({ children, className }) {
  return (
    <div className={`flex items-center justify-between gap-3 ${className || ''}`}>
      {children}
    </div>
  )
}
