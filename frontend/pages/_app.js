import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import { ToastProvider } from '../lib/toast'
import { motion, AnimatePresence } from 'framer-motion'
import Sidebar from '../components/Sidebar'
import '../styles/globals.css'

export default function App({ Component, pageProps }) {
  const router = useRouter()
  const [isTransitioning, setIsTransitioning] = useState(false)

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
        <Sidebar />
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
