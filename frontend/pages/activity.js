import { useState, useEffect } from 'react';
import Head from 'next/head';
import {
    Activity as ActivityIcon,
    Terminal,
    CheckCircle2,
    AlertCircle,
    Search,
    RefreshCw,
    Cpu,
    Layers
} from 'lucide-react';
import { cn } from '../lib/utils';
import { formatDistanceToNow } from 'date-fns';

export default function ActivityPage() {
    const [logs, setLogs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('');

    useEffect(() => {
        fetchLogs();
    }, []);

    const fetchLogs = async () => {
        try {
            const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/system/activity`);
            const data = await res.json();
            setLogs(data.logs || []);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const getIcon = (type) => {
        switch (type) {
            case 'success': return <CheckCircle2 className="w-4 h-4 text-green-500" />;
            case 'error': return <AlertCircle className="w-4 h-4 text-red-500" />;
            case 'system': return <Cpu className="w-4 h-4 text-aurora-purple" />;
            default: return <Layers className="w-4 h-4 text-aurora-cyan" />;
        }
    };

    const filteredLogs = logs.filter(l =>
        l.event.toLowerCase().includes(filter.toLowerCase()) ||
        l.message.toLowerCase().includes(filter.toLowerCase())
    );

    return (
        <div className="h-screen flex flex-col bg-aurora-bg text-gray-200 font-sans overflow-hidden">
            <Head>
                <title>Activity | ArchIntel</title>
            </Head>

            <header className="h-16 border-b border-aurora-border flex items-center justify-between px-6 bg-[#0A0C10]/80 backdrop-blur-md relative z-20 shadow-sm">
                <div className="flex items-center gap-6">
                    <div className="flex items-center gap-4">
                        <h2 className="text-sm font-bold uppercase tracking-widest text-white/50 font-mono">System Activity</h2>
                        <div className="h-4 w-px bg-white/[0.1]" />
                    </div>
                    <div className="relative">
                        <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3 h-3 text-gray-500" />
                        <input
                            type="text"
                            placeholder="Filter logs..."
                            value={filter}
                            onChange={(e) => setFilter(e.target.value)}
                            className="bg-[#15171B] border border-white/[0.08] rounded-full pl-8 pr-4 py-1 text-[10px] text-gray-300 focus:outline-none focus:border-aurora-purple/50 transition-all font-mono"
                        />
                    </div>
                </div>
                <button
                    onClick={fetchLogs}
                    className="p-2 hover:bg-white/5 rounded-lg transition-colors"
                >
                    <RefreshCw className={cn("w-4 h-4 text-gray-500", loading && "animate-spin")} />
                </button>
            </header>

            <div className="flex-1 overflow-y-auto p-10">
                <div className="max-w-5xl mx-auto">
                    {/* Header */}
                    <div className="mb-10">
                        <div className="flex items-center gap-2 text-aurora-cyan text-[10px] uppercase font-bold tracking-[0.2em] font-mono mb-2">
                            <Terminal className="w-3 h-3" />
                            Audit Trail
                        </div>
                        <h1 className="text-4xl font-bold text-white tracking-tight">System Events</h1>
                        <p className="text-gray-500 mt-2">Historical log of all architectural scans and synchronized nodes.</p>
                    </div>

                    {loading ? (
                        <div className="flex flex-col items-center justify-center py-20 gap-4">
                            <RefreshCw className="w-8 h-8 text-aurora-purple animate-spin" />
                            <span className="text-sm font-mono text-gray-500 uppercase tracking-tighter">Querying logs table...</span>
                        </div>
                    ) : (
                        <div className="space-y-4">
                            {filteredLogs.map((log, idx) => (
                                <div
                                    key={log.id}
                                    className="group relative flex items-start gap-4 p-4 bg-[#111318] border border-white/[0.05] rounded-xl hover:bg-[#15171B] transition-all"
                                >
                                    <div className="mt-1">
                                        {getIcon(log.type)}
                                    </div>
                                    <div className="flex-1 min-w-0">
                                        <div className="flex items-center justify-between mb-1">
                                            <h3 className="text-sm font-bold text-white group-hover:text-aurora-purple transition-colors">
                                                {log.event}
                                            </h3>
                                            <span className="text-[10px] text-gray-600 font-mono">
                                                {formatDistanceToNow(new Date(log.timestamp))} ago
                                            </span>
                                        </div>
                                        <p className="text-xs text-gray-500 truncate">{log.message}</p>
                                        <div className="flex items-center gap-3 mt-3">
                                            <span className="text-[9px] uppercase font-bold text-gray-600 font-mono flex items-center gap-1">
                                                <Search className="w-2.5 h-2.5" />
                                                User: {log.user}
                                            </span>
                                        </div>
                                    </div>
                                    {idx < filteredLogs.length - 1 && (
                                        <div className="absolute left-6 top-12 bottom-[-16px] w-px bg-white/[0.03]" />
                                    )}
                                </div>
                            ))}
                            {filteredLogs.length === 0 && (
                                <div className="text-center py-20 border border-dashed border-white/10 rounded-2xl">
                                    <p className="text-gray-500 font-mono text-sm">No events found matching your filter.</p>
                                </div>
                            )}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
