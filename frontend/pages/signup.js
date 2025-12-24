import React, { useState } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { motion } from 'framer-motion';
import { Github, Mail, ArrowLeft, Zap, Shield, Lock, Sparkles, Check, Search } from 'lucide-react';
import { Button } from '../components/ui/button';

const BlueprintBackground = () => (
    <div className="absolute inset-0 z-0 overflow-hidden pointer-events-none opacity-10">
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:40px_40px] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)]" />
    </div>
);

export default function Signup() {
    const router = useRouter();
    const [isLoading, setIsLoading] = useState(false);
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState(null);
    const [isSuccess, setIsSuccess] = useState(false);

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

    const handleGitHubSignup = async () => {
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

    const handleGoogleSignup = async () => {
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

    const handleEmailSignup = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        setError(null);

        try {
            const { signUpWithEmail } = await import('../lib/auth_utils');
            await signUpWithEmail(email, password);

            setError(null);
            setIsSuccess(true);
        } catch (err) {
            setError(err.message || 'Failed to create account. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-[#0A0C10] via-[#0d1117] to-[#0A0C10] flex items-center justify-center p-6 relative overflow-hidden">
            <Head>
                <title>Create Account | ArchIntel Docs</title>
            </Head>

            <BlueprintBackground />

            {/* Animated gradient orbs */}
            <div className="absolute top-0 left-1/4 w-96 h-96 bg-aurora-purple/20 blur-[120px] rounded-full animate-pulse" />
            <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-aurora-cyan/20 blur-[120px] rounded-full animate-pulse" style={{ animationDelay: '1s' }} />

            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6 }}
                className="w-full max-w-6xl z-10 grid md:grid-cols-2 gap-12 items-center"
            >
                {/* Left side - Branding & Features */}
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
                            Start analyzing your<br />
                            <span className="bg-gradient-to-r from-aurora-purple to-aurora-cyan bg-clip-text text-transparent">
                                codebase today
                            </span>
                        </h2>
                        <p className="text-gray-400 leading-relaxed mb-8">
                            Join thousands of engineering teams using AI-powered architectural analysis to understand, document, and improve their systems.
                        </p>

                        <div className="space-y-4">
                            {[
                                'Instant AST-powered documentation',
                                'Real-time Git history mining',
                                'AI-driven design rationale',
                                'Dependency graph visualization'
                            ].map((feature, i) => (
                                <div key={i} className="flex items-center gap-3">
                                    <div className="w-6 h-6 rounded-full bg-aurora-purple/10 border border-aurora-purple/30 flex items-center justify-center">
                                        <Check className="w-3.5 h-3.5 text-aurora-purple" />
                                    </div>
                                    <span className="text-sm text-gray-300">{feature}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Right side - Signup Form */}
                <div className="w-full">
                    <div className="bg-[#0d1117]/80 backdrop-blur-xl border border-white/[0.08] rounded-3xl p-8 shadow-2xl">
                        <div className="mb-8">
                            <h3 className="text-2xl font-bold text-white mb-2">Create your account</h3>
                            <p className="text-sm text-gray-400">
                                Already have an account?{' '}
                                <Link href="/login" className="text-aurora-cyan hover:text-aurora-cyan/80 font-medium transition-colors">
                                    Sign in
                                </Link>
                            </p>
                        </div>

                        {error && (
                            <div className="mb-6 p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
                                {error}
                            </div>
                        )}

                        <div className="space-y-4">
                            {isSuccess ? (
                                <motion.div
                                    initial={{ opacity: 0, scale: 0.95 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    className="text-center py-8"
                                >
                                    <div className="w-20 h-20 rounded-2xl bg-aurora-cyan/10 border border-aurora-cyan/30 flex items-center justify-center mx-auto mb-6">
                                        <Mail className="w-10 h-10 text-aurora-cyan animate-pulse" />
                                    </div>
                                    <h3 className="text-2xl font-bold text-white mb-2">Check your inbox</h3>
                                    <p className="text-gray-400 text-sm mb-8 leading-relaxed">
                                        We've sent a verification link to <span className="text-white font-medium">{email}</span>.
                                        Please click the link to activate your account.
                                    </p>
                                    <Link href="/login">
                                        <Button className="w-full h-12 bg-white/5 hover:bg-white/10 text-white border border-white/10 rounded-xl transition-all">
                                            Return to Sign In
                                        </Button>
                                    </Link>
                                </motion.div>
                            ) : (
                                <>
                                    {/* GitHub Signup */}
                                    <Button
                                        onClick={handleGitHubSignup}
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

                                    {/* Google Signup */}
                                    <Button
                                        onClick={handleGoogleSignup}
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

                                    {/* Email Signup Form */}
                                    <form onSubmit={handleEmailSignup} className="space-y-4">
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
                                            <label className="block text-xs font-medium text-gray-400 mb-2">Password</label>
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
                                            Create Account
                                        </Button>
                                    </form>

                                    <p className="text-xs text-center text-gray-500 mt-6">
                                        By signing up, you agree to our{' '}
                                        <a href="#" className="text-gray-400 hover:text-white transition-colors">Terms of Service</a>
                                        {' '}and{' '}
                                        <a href="#" className="text-gray-400 hover:text-white transition-colors">Privacy Policy</a>
                                    </p>
                                </>
                            )}
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
