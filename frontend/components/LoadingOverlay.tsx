import * as React from "react"
import { motion } from 'framer-motion';
import { Loader2 } from 'lucide-react';
import { cn } from '../lib/utils';

interface LoadingOverlayProps {
  isLoading: boolean;
  text?: string;
  progress?: number;
  className?: string
}

export function LoadingOverlay({ isLoading, text, progress, className }: LoadingOverlayProps) {
  if (!isLoading) return null;

  return (
    <div className={cn("fixed inset-0 z-50 flex items-center justify-center bg-black/90 backdrop-blur-md", className)} role="status" aria-live="polite">
      <div className="flex flex-col items-center space-y-4">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          className="relative"
        >
          <div className="w-16 h-16 border-4 border-white/10 rounded-full" />
          <div className="absolute inset-0 w-16 h-16 border-4 border-transparent border-t-aurora-purple rounded-full" />
        </motion.div>

        {text && (
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-white font-medium"
          >
            {text}
          </motion.p>
        )}

        {progress !== undefined && (
          <div className="w-64 space-y-2">
            <div className="flex justify-between text-xs text-gray-400">
              <span>Progress</span>
              <span>{Math.round(progress)}%</span>
            </div>
            <div className="h-2 bg-white/10 rounded-full overflow-hidden">
              <motion.div
                className="h-full bg-gradient-to-r from-aurora-purple to-aurora-cyan"
                initial={{ width: 0 }}
                animate={{ width: `${progress}%` }}
                transition={{ duration: 0.3 }}
              />
            </div>
          </div>
        )}
      </div>

      <span className="sr-only">{text || 'Loading...'}</span>
    </div>
  );
}

interface LoadingButtonProps {
  isLoading: boolean;
  children: React.ReactNode;
  className?: string;
  loadingText?: string;
  variant?: 'default' | 'outline' | 'ghost';
}

export function LoadingButton({ isLoading, children, className, loadingText, variant = 'default' }: LoadingButtonProps) {
  return (
    <button
      disabled={isLoading}
      className={cn(
        "relative inline-flex items-center justify-center rounded-xl font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed h-12 px-6",
        variant === 'default' && "bg-aurora-purple hover:bg-aurora-purple/80 text-white",
        variant === 'outline' && "border border-white/[0.08] bg-white/[0.02] hover:bg-white/[0.05] text-gray-400",
        variant === 'ghost' && "hover:bg-white/[0.05] text-gray-400",
        className
      )}
    >
      {isLoading ? (
        <>
          <Loader2 className="w-4 h-4 animate-spin mr-2" />
          {loadingText || 'Loading...'}
        </>
      ) : (
        children
      )}
    </button>
  );
}

interface InlineLoadingProps {
  isLoading: boolean;
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export function InlineLoading({ isLoading, children, fallback }: InlineLoadingProps) {
  return (
    <>
      {isLoading ? (
        <div className="flex items-center justify-center p-8">
          <Loader2 className="w-8 h-8 text-aurora-purple animate-spin" />
        </div>
      ) : (
        children || fallback
      )}
    </>
  );
}
