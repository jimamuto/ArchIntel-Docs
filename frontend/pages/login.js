import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { motion } from 'framer-motion';
import { Github, Mail, ArrowLeft, Zap, Lock, Sparkles, Shield, Search } from 'lucide-react';
import { Button } from '../components/ui/button';

const BlueprintBackground = () => (
    <div className="absolute inset-0 z-0 overflow-hidden pointer-events-none opacity-10">
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:40px_40px] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)]" />
    </div>
);

export default function Login() {
    const router = useRouter();
    const [isLoading, setIsLoading] = useState(false);
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState(null);

    useEffect(() => {
        async function checkAuth() {
            const { getSession } = await import('../lib/auth_utils');
            const session = await getSession();
            if (session) {
                router.push('/projects');
            }
        }
        checkAuth();
    }, [router]);

    const handleGitHubLogin = async () => {
        setIsLoading(true);
        setError(null);
        try {
            const { signInWithGitHub } = await import('../lib/auth_utils');
            await signInWithGitHub();
        } catch (err) {
            setError(err.message || "Failed to initialize GitHub authentication.");
            setIsLoading(false);
        }
    };

    const handleGoogleLogin = async () => {
        setIsLoading(true);
        setError(null);
        try {
            const { signInWithGoogle } = await import('../lib/auth_utils');
            await signInWithGoogle();
        } catch (err) {
            setError(err.message || "Failed to initialize Google authentication.");
            setIsLoading(false);
        }
    };

    const handleEmailLogin = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        setError(null);

        try {
            const { signInWithEmail, getMFAFactors } = await import('../lib/auth_utils');
            await signInWithEmail(email, password);

            // Check if user has 2FA enabled
            const factors = await getMFAFactors();
            if (factors && factors.totp && factors.totp.length > 0) {
                router.push('/verify-2fa');
            } else {
                router.push('/projects');
            }
        } catch (err) {
            setError(err.message || 'Invalid email or password.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-[#0A0C10] via-[#0d1117] to-[#0A0C10] flex items-center justify-center p-6 relative overflow-hidden">
            <Head>
                <title>Sign In | ArchIntel Docs</title>
            </Head>

            <BlueprintBackground />

            {/* Animated gradient orbs */}
            <div className="absolute top-0 right-1/4 w-96 h-96 bg-aurora-cyan/20 blur-[120px] rounded-full animate-pulse" />
            <div className="absolute bottom-0 left-1/4 w-96 h-96 bg-aurora-purple/20 blur-[120px] rounded-full animate-pulse" style={{ animationDelay: '1s' }} />

            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6 }}
                className="w-full max-w-6xl z-10 grid md:grid-cols-2 gap-12 items-center"
            >
                {/* Left side - Branding */}
                <div className="hidden md:block space-y-8">
                    <Link href="/" className="inline-flex items-center gap-2 text-gray-400 hover:text-white transition-colors group">
                        <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
                        <span className="text-sm font-medium">Back to Home</span>
                    </Link>

                    <div>
                        <div className="flex items-center gap-3 mb-6">
                            <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-aurora-purple to-aurora-cyan p-0.5">
                                <div className="w-full h-full bg-[#0A0C10] rounded-[14px] flex items-center justify-center">
                                    <Zap className="w-7 h-7 text-white fill-current" />
                                </div>
                            </div>
                            <div>
                                <h1 className="text-2xl font-bold text-white">ArchIntel Docs</h1>
                                <p className="text-sm text-gray-500">Architectural Intelligence</p>
                            </div>
                        </div>

                        <h2 className="text-4xl font-bold text-white mb-4 leading-tight">
                            Welcome back to<br />
                            <span className="bg-gradient-to-r from-aurora-purple to-aurora-cyan bg-clip-text text-transparent">
                                ArchIntel
                            </span>
                        </h2>
                        <p className="text-gray-400 leading-relaxed mb-8">
                            Continue analyzing your codebase with AI-powered architectural intelligence.
                        </p>

                        <div className="space-y-4 p-6 rounded-2xl bg-white/[0.02] border border-white/[0.05]">
                            <div className="flex items-center gap-3">
                                <Shield className="w-5 h-5 text-aurora-cyan" />
                                <div>
                                    <p className="text-sm font-medium text-white">Enterprise Security</p>
                                    <p className="text-xs text-gray-500">Your code never leaves your infrastructure</p>
                                </div>
                            </div>
                            <div className="flex items-center gap-3">
                                <Lock className="w-5 h-5 text-aurora-purple" />
                                <div>
                                    <p className="text-sm font-medium text-white">End-to-End Encryption</p>
                                    <p className="text-xs text-gray-500">All data encrypted in transit and at rest</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Right side - Login Form */}
                <div className="w-full">
                    <div className="bg-[#0d1117]/80 backdrop-blur-xl border border-white/[0.08] rounded-3xl p-8 shadow-2xl">
                        <div className="mb-8">
                            <h3 className="text-2xl font-bold text-white mb-2">Sign in to your account</h3>
                            <p className="text-sm text-gray-400">
                                Don't have an account?{' '}
                                <Link href="/signup" className="text-aurora-cyan hover:text-aurora-cyan/80 font-medium transition-colors">
                                    Sign up
                                </Link>
                            </p>
                        </div>

                        {error && (
                            <div className="mb-6 p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
                                {error}
                            </div>
                        )}

                        <div className="space-y-4">
                            {/* GitHub Login */}
                            <Button
                                onClick={handleGitHubLogin}
                                disabled={isLoading}
                                className="w-full h-12 bg-[#24292F] hover:bg-[#24292F]/80 text-white border border-white/10 rounded-xl font-medium flex items-center justify-center gap-3 transition-all"
                            >
                                {isLoading ? (
                                    <div className="w-5 h-5 border-2 border-white/20 border-t-white rounded-full animate-spin" />
                                ) : (
                                    <>
                                        <Github className="w-5 h-5" />
                                        Continue with GitHub
                                    </>
                                )}
                            </Button>

                            {/* Google Login */}
                            <Button
                                onClick={handleGoogleLogin}
                                disabled={isLoading}
                                className="w-full h-12 bg-white hover:bg-white/90 text-gray-900 border border-white/10 rounded-xl font-medium flex items-center justify-center gap-3 transition-all"
                            >
                                {isLoading ? (
                                    <div className="w-5 h-5 border-2 border-gray-200 border-t-gray-600 rounded-full animate-spin" />
                                ) : (
                                    <>
                                        <Search className="w-5 h-5 text-red-500" />
                                        Continue with Google
                                    </>
                                )}
                            </Button>

                            <div className="relative">
                                <div className="absolute inset-0 flex items-center">
                                    <div className="w-full border-t border-white/[0.08]" />
                                </div>
                                <div className="relative flex justify-center text-xs uppercase">
                                    <span className="bg-[#0d1117] px-4 text-gray-500 font-medium">Or continue with email</span>
                                </div>
                            </div>

                            {/* Email Login Form */}
                            <form onSubmit={handleEmailLogin} className="space-y-4">
                                <div>
                                    <label className="block text-xs font-medium text-gray-400 mb-2">Email address</label>
                                    <div className="relative">
                                        <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                                        <input
                                            type="email"
                                            value={email}
                                            onChange={(e) => setEmail(e.target.value)}
                                            placeholder="you@company.com"
                                            className="w-full h-12 bg-[#0A0C10] border border-white/[0.08] rounded-xl pl-10 pr-4 text-white placeholder:text-gray-600 focus:outline-none focus:border-aurora-purple/50 focus:ring-1 focus:ring-aurora-purple/20 transition-all"
                                            required
                                        />
                                    </div>
                                </div>

                                <div>
                                    <div className="flex items-center justify-between mb-2">
                                        <label className="block text-xs font-medium text-gray-400">Password</label>
                                        <a href="#" className="text-xs text-aurora-cyan hover:text-aurora-cyan/80 transition-colors">
                                            Forgot password?
                                        </a>
                                    </div>
                                    <div className="relative">
                                        <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                                        <input
                                            type="password"
                                            value={password}
                                            onChange={(e) => setPassword(e.target.value)}
                                            placeholder="••••••••"
                                            className="w-full h-12 bg-[#0A0C10] border border-white/[0.08] rounded-xl pl-10 pr-4 text-white placeholder:text-gray-600 focus:outline-none focus:border-aurora-purple/50 focus:ring-1 focus:ring-aurora-purple/20 transition-all"
                                            required
                                        />
                                    </div>
                                </div>

                                <Button
                                    type="submit"
                                    disabled={isLoading}
                                    className="w-full h-12 bg-gradient-to-r from-aurora-purple to-aurora-cyan hover:opacity-90 text-white rounded-xl font-bold transition-all shadow-lg shadow-aurora-purple/20"
                                >
                                    Sign In
                                </Button>
                            </form>
                        </div>
                    </div>

                    {/* Mobile back button */}
                    <Link href="/" className="md:hidden mt-6 inline-flex items-center gap-2 text-gray-400 hover:text-white transition-colors group">
                        <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
                        <span className="text-sm font-medium">Back to Home</span>
                    </Link>
                </div>
            </motion.div>
        </div>
    );
}
