import * as React from "react"
import { motion, AnimatePresence } from "framer-motion"
import { X } from "lucide-react"

export function Sheet({ 
  children, 
  open, 
  onOpenChange, 
  side = "left",
  ...props 
}) {
  return (
    <AnimatePresence>
      {open && (
        <>
          {/* Overlay */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50"
            onClick={() => onOpenChange(false)}
          />
          
          {/* Sheet */}
          <motion.div
            initial={{ 
              x: side === "left" ? "-100%" : "100%",
              opacity: 0
            }}
            animate={{ 
              x: 0,
              opacity: 1
            }}
            exit={{ 
              x: side === "left" ? "-100%" : "100%",
              opacity: 0
            }}
            transition={{ type: "spring", damping: 30, stiffness: 300 }}
            className={`fixed top-0 ${side === "left" ? "left-0" : "right-0"} h-full w-full max-w-sm bg-card border-border shadow-xl z-50 overflow-y-auto`}
            {...props}
          >
            {children}
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}

export function SheetTrigger({ children, onClick, ...props }) {
  return (
    <div onClick={onClick} {...props}>
      {children}
    </div>
  )
}

export function SheetContent({ 
  children, 
  className, 
  onClose,
  ...props 
}) {
  return (
    <div className={`flex flex-col h-full ${className || ''}`} {...props}>
      {children}
    </div>
  )
}

export function SheetHeader({ children, ...props }) {
  return (
    <div className="flex items-center justify-between px-6 py-4 border-b border-border" {...props}>
      {children}
    </div>
  )
}

export function SheetTitle({ children, ...props }) {
  return (
    <h2 className="text-lg font-semibold" {...props}>
      {children}
    </h2>
  )
}

export function SheetDescription({ children, ...props }) {
  return (
    <p className="text-sm text-muted-foreground" {...props}>
      {children}
    </p>
  )
}

export function SheetBody({ children, className, ...props }) {
  return (
    <div className={`flex-1 overflow-y-auto ${className || ''}`} {...props}>
      {children}
    </div>
  )
}

export function SheetFooter({ children, ...props }) {
  return (
    <div className="flex items-center justify-end gap-3 px-6 py-4 border-t border-border" {...props}>
      {children}
    </div>
  )
}
