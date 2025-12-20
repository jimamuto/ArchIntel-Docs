import Link from 'next/link';
import Head from 'next/head';
import { AlertCircle, ZapOff, RefreshCw } from 'lucide-react';
import { Button } from '../components/ui/button';

export default function Custom500() {
    return (
        <div className="min-h-screen bg-aurora-bg flex items-center justify-center p-6 text-slate-200">
            <Head>
                <title>Intelligence Overflow | ArchIntel</title>
            </Head>

            {/* Background Decorative */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-red-500/10 rounded-full blur-[120px]" />
            </div>

            <div className="max-w-md w-full text-center space-y-8 relative z-10">
                <div className="relative inline-block">
                    <AlertCircle className="w-24 h-24 text-red-500/20 fill-red-500/5" />
                    <ZapOff className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-8 h-8 text-red-500" />
                </div>

                <div className="space-y-4">
                    <h1 className="text-6xl font-black tracking-tighter text-white font-mono uppercase">500</h1>
                    <h2 className="text-xl font-bold text-slate-300">Intelligence Node Failure</h2>
                    <p className="text-slate-500 text-sm leading-relaxed max-w-xs mx-auto">
                        The core analysis engine has encountered an unhandled exception. Our systems are currently re-initializing the kernel.
                    </p>
                </div>

                <div className="pt-8">
                    <Button
                        onClick={() => window.location.reload()}
                        className="bg-white/5 border border-white/10 hover:bg-white/10 text-white rounded-xl gap-2 px-8"
                    >
                        <RefreshCw className="w-4 h-4" />
                        Retry Connection
                    </Button>
                </div>
            </div>
        </div>
    );
}
