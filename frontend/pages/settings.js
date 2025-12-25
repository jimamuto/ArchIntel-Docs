import { useState, useEffect } from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';
import {
    Settings as SettingsIcon,
    Cpu,
    EyeOff,
    ShieldCheck,
    Save,
    Database,
    RefreshCw,
    Clock,
    LogOut,
    X
} from 'lucide-react';
import { Button } from '../components/ui/button';
import { useToast } from '../lib/toast';
import { logout, authenticatedFetch } from '../lib/auth_utils';
import { Modal } from '../components/Modal';

export default function SettingsPage() {
    const router = useRouter();
    const { success: showToast, error: showError } = useToast();
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
    const [showUnsavedModal, setShowUnsavedModal] = useState(false);
    const [pendingRoute, setPendingRoute] = useState(null);
    const [originalSettings, setOriginalSettings] = useState({});
    const [settings, setSettings] = useState({
        ai_provider: 'Groq',
        model: 'llama-3.3-70b-versatile',
        exclusion_patterns: [],
        analytics_enabled: true,
        api_status: 'unknown'
    });

    useEffect(() => {
        fetchSettings();
    }, []);

    const fetchSettings = async () => {
        try {
            const res = await authenticatedFetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/system/settings`);
            const data = await res.json();
            setSettings(data);
            setOriginalSettings(data);
        } catch (err) {
            showError("Failed to load settings", "Unable to retrieve settings from the server. Please refresh and try again.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        setHasUnsavedChanges(JSON.stringify(settings) !== JSON.stringify(originalSettings));
    }, [settings, originalSettings]);

    useEffect(() => {
        const handleRouteChange = (url) => {
            if (hasUnsavedChanges) {
                setPendingRoute(url);
                setShowUnsavedModal(true);
                router.events.emit('routeChangeError');
                throw 'Aborted';
            }
        };

        router.events.on('routeChangeStart', handleRouteChange);

        return () => {
            router.events.off('routeChangeStart', handleRouteChange);
        };
    }, [hasUnsavedChanges, router]);

    const handleUnsavedDiscard = () => {
        setHasUnsavedChanges(false);
        setShowUnsavedModal(false);
        if (pendingRoute) {
            router.push(pendingRoute);
        }
    };

    const handleUnsavedSave = async () => {
        await handleSave();
        setShowUnsavedModal(false);
        if (pendingRoute) {
            router.push(pendingRoute);
        }
    };

    const handleSave = async () => {
        setSaving(true);
        try {
            const res = await authenticatedFetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/system/settings`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(settings)
            });
            if (res.ok) {
                showToast("Settings saved successfully", "Your changes have been applied.");
                setOriginalSettings({ ...settings });
            } else {
                const errorData = await res.json().catch(() => ({}));
                throw new Error(errorData.detail || errorData.message || 'Unable to save settings');
            }
        } catch (err) {
            showError("Failed to save settings", err.message || 'Please check your connection and try again.');
        } finally {
            setSaving(false);
        }
    };

    return (
        <div className="h-screen flex flex-col bg-aurora-bg text-gray-200 font-sans overflow-hidden">
            <Head>
                <title>Settings | ArchIntel</title>
            </Head>

            <header className="h-16 border-b border-aurora-border flex items-center justify-between px-6 bg-[#0A0C10]/80 backdrop-blur-md relative z-20 shadow-sm">
                <div className="flex items-center gap-6">
                    <div className="flex items-center gap-4">
                        <h2 className="text-sm font-bold uppercase tracking-widest text-white/50 font-mono">System Configuration</h2>
                        <div className="h-4 w-px bg-white/[0.1]" />
                    </div>
                </div>
                <Button
                    onClick={handleSave}
                    disabled={saving}
                    className="bg-aurora-purple hover:bg-aurora-purple/80 text-white rounded-xl flex gap-2"
                >
                    {saving ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
                    Save Changes
                </Button>
            </header>

            <div className="flex-1 overflow-y-auto p-10">
                <div className="max-w-4xl mx-auto space-y-12">
                    {/* Header */}
                    <div>
                        <div className="flex items-center gap-2 text-aurora-cyan text-[10px] uppercase font-bold tracking-[0.2em] font-mono mb-2">
                            <SettingsIcon className="w-3 h-3" />
                            Intelligence Node Control
                        </div>
                        <h1 className="text-4xl font-bold text-white tracking-tight">Core Settings</h1>
                        <p className="text-gray-500 mt-2">Manage your architectural engine parameters and system behavior.</p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                        {/* AI section */}
                        <section className="bg-[#111318] border border-white/[0.05] rounded-2xl p-6 space-y-6">
                            <div className="flex items-center gap-3 mb-2">
                                <div className="w-10 h-10 rounded-xl bg-aurora-purple/10 flex items-center justify-center">
                                    <Cpu className="w-5 h-5 text-aurora-purple" />
                                </div>
                                <div>
                                    <h3 className="font-bold text-white">AI Engine</h3>
                                    <p className="text-xs text-gray-500">Groq Infrastructure</p>
                                </div>
                            </div>

                            <div className="space-y-4">
                                <div className="space-y-1.5">
                                    <label className="text-[10px] uppercase font-bold text-gray-500 font-mono">Primary Model</label>
                                    <select
                                        value={settings.model}
                                        onChange={(e) => setSettings({ ...settings, model: e.target.value })}
                                        className="w-full bg-[#0A0C10] border border-white/[0.08] rounded-lg px-3 py-2 text-sm focus:border-aurora-purple outline-none"
                                    >
                                        <option value="llama-3.3-70b-versatile">Llama 3.3 70B (Versatile)</option>
                                        <option value="llama-3.1-8b-instant">Llama 3.1 8B (Speed)</option>
                                        <option value="mixtral-8x7b-32768">Mixtral 8x7B (Deep Context)</option>
                                    </select>
                                </div>

                                <div className="p-3 bg-aurora-purple/5 border border-aurora-purple/20 rounded-lg flex items-center justify-between">
                                    <div className="flex items-center gap-3">
                                        <ShieldCheck className="w-4 h-4 text-aurora-purple" />
                                        <span className="text-xs font-medium">API Connection Status</span>
                                    </div>
                                    <div className="flex items-center gap-1.5">
                                        <div className={`w-2 h-2 rounded-full ${settings.api_status === 'connected' ? 'bg-green-500' : 'bg-red-500'} shadow-glow shadow-current`} />
                                        <span className="text-[10px] font-mono uppercase text-gray-400">{settings.api_status}</span>
                                    </div>
                                </div>
                            </div>
                        </section>

                        {/* Ingestion Section */}
                        <section className="bg-[#111318] border border-white/[0.05] rounded-2xl p-6 space-y-6">
                            <div className="flex items-center gap-3 mb-2">
                                <div className="w-10 h-10 rounded-xl bg-aurora-cyan/10 flex items-center justify-center">
                                    <EyeOff className="w-5 h-5 text-aurora-cyan" />
                                </div>
                                <div>
                                    <h3 className="font-bold text-white">Ingestion Rules</h3>
                                    <p className="text-xs text-gray-500">Scanning & Filtering</p>
                                </div>
                            </div>

                            <div className="space-y-4">
                                <div className="space-y-1.5">
                                    <label className="text-[10px] uppercase font-bold text-gray-500 font-mono">Exclusion Patterns</label>
                                    <div className="flex flex-wrap gap-2 mb-2">
                                        {settings.exclusion_patterns.map(p => (
                                            <span key={p} className="px-2 py-1 bg-white/[0.03] border border-white/[0.08] rounded text-[10px] font-mono">
                                                {p}
                                            </span>
                                        ))}
                                    </div>
                                    <input
                                        type="text"
                                        placeholder="Add pattern (e.g. *.log)..."
                                        className="w-full bg-[#0A0C10] border border-white/[0.08] rounded-lg px-3 py-2 text-sm focus:border-aurora-purple outline-none"
                                        onKeyDown={(e) => {
                                            if (e.key === 'Enter') {
                                                setSettings({ ...settings, exclusion_patterns: [...settings.exclusion_patterns, e.target.value] });
                                                e.target.value = '';
                                            }
                                        }}
                                    />
                                </div>
                            </div>
                        </section>

                        {/* Storage Section */}
                        <section className="bg-[#111318] border border-white/[0.05] rounded-2xl p-6 space-y-6">
                            <div className="flex items-center gap-3 mb-2">
                                <div className="w-10 h-10 rounded-xl bg-orange-500/10 flex items-center justify-center">
                                    <Database className="w-5 h-5 text-orange-500" />
                                </div>
                                <div>
                                    <h3 className="font-bold text-white">Database</h3>
                                    <p className="text-xs text-gray-500">Supabase Connection</p>
                                </div>
                            </div>

                            <div className="space-y-4">
                                <div className="flex items-center justify-between p-3 bg-white/[0.02] rounded-lg">
                                    <span className="text-xs text-gray-400">Total Projects Indexed</span>
                                    <span className="text-sm font-bold text-white">12</span>
                                </div>
                                <div className="flex items-center justify-between p-3 bg-white/[0.02] rounded-lg">
                                    <span className="text-xs text-gray-400">Metadata Cache Size</span>
                                    <span className="text-sm font-bold text-white">24.5 MB</span>
                                </div>
                            </div>
                        </section>

                        {/* Account Section */}
                        <section className="bg-[#111318] border border-white/[0.05] rounded-2xl p-6 space-y-6">
                            <div className="flex items-center gap-3 mb-2">
                                <div className="w-10 h-10 rounded-xl bg-aurora-purple/10 flex items-center justify-center">
                                    <Clock className="w-5 h-5 text-aurora-purple" />
                                </div>
                                <div>
                                    <h3 className="font-bold text-white">Account Info</h3>
                                    <p className="text-xs text-gray-500">Session Management</p>
                                </div>
                            </div>
                            <div className="space-y-4">
                                <p className="text-sm text-gray-400">
                                    You are currently signed in. You can securely log out of your account here.
                                </p>
                                <Button
                                    onClick={logout}
                                    variant="outline"
                                    className="w-full border-red-500/50 text-red-500 hover:bg-red-500 hover:text-white transition-all flex gap-2"
                                >
                                    <LogOut className="w-4 h-4" />
                                    Sign Out
                                </Button>
                            </div>
                        </section>
                    </div>
                </div>
            </div>
        </div>

        {/* Unsaved Changes Modal */}
        <Modal
            isOpen={showUnsavedModal}
            onClose={() => setShowUnsavedModal(false)}
            title="Unsaved Changes"
            size="md"
        >
            <div className="space-y-4">
                <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center">
                        <RefreshCw className="w-6 h-6 text-amber-500" />
                    </div>
                    <div>
                        <p className="text-sm text-accessible-subtle">
                            You have unsaved changes. Would you like to save them before leaving?
                        </p>
                    </div>
                </div>

                <div className="grid grid-cols-2 gap-3 pt-4">
                    <Button
                        variant="outline"
                        onClick={handleUnsavedDiscard}
                        className="h-12 border-white/[0.08] bg-white/[0.02] hover:bg-white/[0.05] text-gray-400 rounded-xl font-bold"
                    >
                        Discard Changes
                    </Button>
                    <Button
                        onClick={handleUnsavedSave}
                        disabled={saving}
                        className="h-12 bg-aurora-purple hover:bg-aurora-purple/80 text-white font-bold rounded-xl"
                    >
                        {saving ? 'Saving...' : 'Save Changes'}
                    </Button>
                </div>
            </div>
        </Modal>
    );
}
