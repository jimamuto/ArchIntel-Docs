import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import { ToastProvider } from '../lib/toast'
import { motion, AnimatePresence } from 'framer-motion'
import Sidebar from '../components/Sidebar'
import '../styles/globals.css'

export default function App({ Component, pageProps }) {
  const router = useRouter()
  const [isTransitioning, setIsTransitioning] = useState(false)

  // Determine if we should show the sidebar
  const showSidebar = !['/login', '/signup'].includes(router.pathname)

  // Handle route transitions
  useEffect(() => {
    const handleStart = () => setIsTransitioning(true)
    const handleComplete = () => setIsTransitioning(false)

    router.events.on('routeChangeStart', handleStart)
    router.events.on('routeChangeComplete', handleComplete)
    router.events.on('routeChangeError', handleComplete)

    return () => {
      router.events.off('routeChangeStart', handleStart)
      router.events.off('routeChangeComplete', handleComplete)
      router.events.off('routeChangeError', handleComplete)
    }
  }, [router])

  return (
    <ToastProvider>
      <div className="flex h-screen bg-aurora-bg text-slate-200 font-sans overflow-hidden">
        {/* Reddit-style loading bar */}
        <AnimatePresence>
          {isTransitioning && (
            <motion.div
              initial={{ width: "0%", opacity: 0 }}
              animate={{ width: "100%", opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{
                width: { duration: 2, ease: "easeOut" },
                opacity: { duration: 0.2 }
              }}
              className="fixed top-0 left-0 h-[3px] bg-gradient-to-r from-aurora-purple via-[#5DE6FA] to-aurora-purple z-[9999] shadow-[0_0_10px_rgba(178,110,247,0.5)]"
            />
          )}
        </AnimatePresence>

        {showSidebar && <Sidebar />}
        <div className="flex-1 flex flex-col min-w-0 relative overflow-hidden">
          <AnimatePresence mode="wait">
            <motion.div
              key={router.route}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.3 }}
              className="flex-1 overflow-y-auto"
            >
              <Component {...pageProps} />
            </motion.div>
          </AnimatePresence>
        </div>
      </div>
    </ToastProvider>
  )
}
