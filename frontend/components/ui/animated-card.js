import * as React from "react"
import { motion, AnimatePresence } from "framer-motion"

export function AnimatedCard({ 
  children, 
  className, 
  hoverable = true, 
  onClick,
  initial = { opacity: 0, y: 20 },
  animate = { opacity: 1, y: 0 },
  transition = { duration: 0.4, ease: "easeOut" },
  ...props 
}) {
  const CardComponent = hoverable ? motion.div : 'div'
  
  return (
    <CardComponent
      className={`relative overflow-hidden rounded-xl border border-slate-800/30 bg-slate-900/20 backdrop-blur-sm ${className || ''}`}
      initial={initial}
      animate={animate}
      transition={transition}
      whileHover={hoverable ? { scale: 1.02, y: -2 } : undefined}
      whileTap={hoverable ? { scale: 0.98 } : undefined}
      onClick={onClick}
      {...props}
    >
      <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/5 via-emerald-500/5 to-cyan-400/5 opacity-0 hover:opacity-100 transition-opacity duration-300" />
      <div className="relative p-6">
        {children}
      </div>
    </CardComponent>
  )
}

export function AnimatedGrid({ children, className, ...props }) {
  return (
    <div className={`grid gap-6 ${className || ''}`} {...props}>
      <AnimatePresence>
        {React.Children.map(children, (child, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ 
              duration: 0.5, 
              ease: "easeOut",
              delay: index * 0.1 
            }}
          >
            {child}
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  )
}

export function FloatingButton({ children, className, ...props }) {
  return (
    <motion.button
      className={`relative inline-flex items-center gap-2 px-4 py-2 rounded-lg border border-slate-700/50 bg-slate-900/30 text-slate-200 hover:text-cyan-300 transition-all duration-200 ${className || ''}`}
      whileHover={{ scale: 1.05, y: -2 }}
      whileTap={{ scale: 0.95 }}
      {...props}
    >
      <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/10 to-emerald-500/10 opacity-0 hover:opacity-100 rounded-lg transition-opacity duration-200" />
      {children}
    </motion.button>
  )
}
