import Link from 'next/link';
import Head from 'next/head';
import { Search, Hexagon, ArrowLeft } from 'lucide-react';
import { Button } from '../components/ui/button';

export default function Custom404() {
    return (
        <div className="min-h-screen bg-aurora-bg flex items-center justify-center p-6 text-slate-200">
            <Head>
                <title>Node Not Found | ArchIntel</title>
            </Head>

            {/* Background Decorative */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-aurora-purple/10 rounded-full blur-[120px]" />
            </div>

            <div className="max-w-md w-full text-center space-y-8 relative z-10">
                <div className="relative inline-block">
                    <Hexagon className="w-24 h-24 text-aurora-purple/20 fill-aurora-purple/5 animate-pulse" />
                    <Search className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-8 h-8 text-aurora-purple" />
                </div>

                <div className="space-y-4">
                    <h1 className="text-6xl font-black tracking-tighter text-white font-mono">404</h1>
                    <h2 className="text-xl font-bold text-slate-300">Architectural Node Not Found</h2>
                    <p className="text-slate-500 text-sm leading-relaxed max-w-xs mx-auto">
                        The resource you are looking for does not exist in the current system graph or has been deprioritized.
                    </p>
                </div>

                <div className="pt-8">
                    <Link href="/projects">
                        <Button className="bg-aurora-purple hover:bg-aurora-purple/80 text-white rounded-xl gap-2 px-8">
                            <ArrowLeft className="w-4 h-4" />
                            Return to Registry
                        </Button>
                    </Link>
                </div>
            </div>
        </div>
    );
}
