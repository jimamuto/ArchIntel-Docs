import { useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X } from 'lucide-react';
import { cn } from '../lib/utils';

function useFocusTrap(active) {
    const containerRef = useRef(null);
    const lastFocusedRef = useRef(null);

    useEffect(() => {
        if (!active) return;

        const container = containerRef.current;
        if (!container) return;

        const focusableElements = container.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];

        lastFocusedRef.current = document.activeElement;

        const handleTab = (e) => {
            if (e.key !== 'Tab') return;

            if (e.shiftKey) {
                if (document.activeElement === firstElement) {
                    e.preventDefault();
                    lastElement.focus();
                }
            } else {
                if (document.activeElement === lastElement) {
                    e.preventDefault();
                    firstElement.focus();
                }
            }
        };

        container.addEventListener('keydown', handleTab);

        if (firstElement) {
            setTimeout(() => firstElement.focus(), 0);
        }

        return () => {
            container.removeEventListener('keydown', handleTab);
            if (lastFocusedRef.current) {
                lastFocusedRef.current.focus();
            }
        };
    }, [active]);

    return containerRef;
}

export function Modal({
    isOpen,
    onClose,
    title,
    children,
    size = 'md',
    showClose = true,
    className
}) {
    const containerRef = useFocusTrap(isOpen);

    const handleEscape = useCallback((e) => {
        if (e.key === 'Escape') {
            onClose();
        }
    }, [onClose]);

    useEffect(() => {
        if (isOpen) {
            document.body.style.overflow = 'hidden';
            document.addEventListener('keydown', handleEscape);
        }

        return () => {
            document.body.style.overflow = '';
            document.removeEventListener('keydown', handleEscape);
        };
    }, [isOpen, handleEscape]);

    const sizeClasses = {
        sm: 'max-w-sm',
        md: 'max-w-lg',
        lg: 'max-w-xl',
        xl: 'max-w-2xl'
    };

    if (!isOpen) return null;

    return (
        <AnimatePresence>
            {isOpen && (
                <>
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 z-50 bg-black/90 backdrop-blur-md"
                        onClick={onClose}
                        aria-hidden="true"
                    />
                    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                        <motion.div
                            ref={containerRef}
                            initial={{ opacity: 0, scale: 0.95, y: 10 }}
                            animate={{ opacity: 1, scale: 1, y: 0 }}
                            exit={{ opacity: 0, scale: 0.95, y: 10 }}
                            transition={{ duration: 0.2 }}
                            className={cn(
                                `w-full ${sizeClasses[size]} bg-[#0A0C10] border border-white/[0.1] rounded-2xl shadow-2xl relative overflow-hidden`,
                                className
                            )}
                            role="dialog"
                            aria-modal="true"
                            aria-labelledby={title ? 'modal-title' : undefined}
                        >
                            {title && (
                                <div className="flex items-center justify-between px-6 py-4 border-b border-white/[0.08]">
                                    <h2 id="modal-title" className="text-lg font-bold text-white">
                                        {title}
                                    </h2>
                                    {showClose && (
                                        <button
                                            onClick={onClose}
                                            className="text-gray-500 hover:text-white transition-colors rounded-lg p-1 focus:outline-none focus:ring-2 focus:ring-aurora-purple/50"
                                            aria-label="Close dialog"
                                        >
                                            <X className="w-5 h-5" />
                                        </button>
                                    )}
                                </div>
                            )}
                            <div className="p-6">
                                {children}
                            </div>
                        </motion.div>
                    </div>
                </>
            )}
        </AnimatePresence>
    );
}
