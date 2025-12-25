import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { motion } from 'framer-motion';
import { Github, Mail, ArrowLeft, Zap, Shield, Lock, Sparkles, Check, Search, AlertCircle, XCircle } from 'lucide-react';
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
    const [confirmPassword, setConfirmPassword] = useState('');
    const [error, setError] = useState(null);
    const [isSuccess, setIsSuccess] = useState(false);
    const [validation, setValidation] = useState({
        email: null,
        password: null,
        confirmPassword: null
    });

    const checkPasswordStrength = (pwd) => {
        let strength = 0;
        if (!pwd) return { score: 0, message: '' };

        if (pwd.length >= 8) strength++;
        if (pwd.length >= 12) strength++;
        if (/[a-z]/.test(pwd) && /[A-Z]/.test(pwd)) strength++;
        if (/\d/.test(pwd)) strength++;
        if (/[^a-zA-Z0-9]/.test(pwd)) strength++;

        const messages = ['', 'Weak', 'Fair', 'Good', 'Strong', 'Very Strong'];
        const colors = ['', 'bg-red-500', 'bg-orange-500', 'bg-yellow-500', 'bg-emerald-500', 'bg-emerald-400'];

        return { score: strength, message: messages[strength], color: colors[strength] };
    };

    const passwordStrength = checkPasswordStrength(password);

    useEffect(() => {
        let isMounted = true;
        async function checkAuth() {
            const { getSession } = await import('../lib/auth_utils');
            const session = await getSession();
            if (session && isMounted) {
                router.push('/projects');
            }
        }
        checkAuth();
        return () => {
            isMounted = false;
        };
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

        // Validation
        const errors = {
            email: !email ? 'Email is required' : !/\S+@\S+\.\S+/.test(email) ? 'Please enter a valid email' : null,
            password: !password ? 'Password is required' : password.length < 8 ? 'Password must be at least 8 characters' : null,
            confirmPassword: !confirmPassword ? 'Please confirm your password' : password !== confirmPassword ? 'Passwords do not match' : null
        };

        setValidation(errors);

        if (errors.email || errors.password || errors.confirmPassword) {
            setIsLoading(false);
            return;
        }

        try {
            const { signUpWithEmail } = await import('../lib/auth_utils');
            const result = await signUpWithEmail(email, password);

            if (result.requires_2fa) {
                router.push({
                    pathname: '/verify-2fa',
                    query: { email: email }
                });
            } else {
                setError(null);
                setIsSuccess(true);
            }
        } catch (err) {
            setError(err.message || 'Failed to create account. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    const validateEmail = (email) => {
        if (!email) return null;
        return /\S+@\S+\.\S+/.test(email) ? null : 'Please enter a valid email address';
    };

    const validatePassword = (pwd) => {
        if (!pwd) return null;
        if (pwd.length < 8) return 'Password must be at least 8 characters';
        return null;
    };

    const validateConfirmPassword = (confirm) => {
        if (!confirm) return null;
        if (!password) return null;
        return confirm === password ? null : 'Passwords do not match';
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
                                         <p className="text-accessible-subtle leading-relaxed mb-8">
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
                                    <span className="text-sm text-accessible-muted">{feature}</span>
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
                            <p className="text-sm text-accessible-subtle">
                                Already have an account?{' '}
                                <Link href="/login" className="text-aurora-cyan hover:text-aurora-cyan/80 font-medium transition-colors focus:outline-none focus:underline focus:underline-offset-2">
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
                                    <p className="text-accessible-subtle text-sm mb-8 leading-relaxed">
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
                                        aria-live="polite"
                                    >
                                        {isLoading ? (
                                            <>
                                                <div className="w-5 h-5 border-2 border-white/20 border-t-white rounded-full animate-spin" aria-hidden="true" />
                                                <span className="sr-only">Connecting to GitHub...</span>
                                            </>
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
                                        aria-live="polite"
                                    >
                                        {isLoading ? (
                                            <>
                                                <div className="w-5 h-5 border-2 border-gray-200 border-t-gray-600 rounded-full animate-spin" aria-hidden="true" />
                                                <span className="sr-only">Connecting to Google...</span>
                                            </>
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
                                    <form onSubmit={handleEmailSignup} className="space-y-4" noValidate>
                                         <div>
                                            <label className="block text-xs font-medium text-accessible-subtle mb-2" htmlFor="signup-email">Email address</label>
                                            <div className="relative">
                                                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-accessible-subtle" />
                                                <input
                                                    id="signup-email"
                                                    type="email"
                                                    value={email}
                                                    onChange={(e) => {
                                                        setEmail(e.target.value);
                                                        setValidation({ ...validation, email: validateEmail(e.target.value) });
                                                    }}
                                                    placeholder="you@company.com"
                                                    className={`w-full h-12 bg-[#0A0C10] border rounded-xl pl-10 pr-4 text-white placeholder:text-gray-600 focus:outline-none focus:ring-2 focus:ring-aurora-purple/50 transition-all ${validation.email ? 'border-red-500' : 'border-white/[0.08]'}`}
                                                    required
                                                />
                                            </div>
                                            {validation.email && (
                                                <div className="flex items-center gap-1.5 mt-1.5 text-red-400 text-[10px]">
                                                    <AlertCircle className="w-3 h-3" />
                                                    {validation.email}
                                                </div>
                                            )}
                                        </div>

                                        <div>
                                            <label className="block text-xs font-medium text-accessible-subtle mb-2" htmlFor="signup-password">Password</label>
                                            <div className="relative">
                                                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-accessible-subtle" />
                                                <input
                                                    id="signup-password"
                                                    type="password"
                                                    value={password}
                                                    onChange={(e) => {
                                                        setPassword(e.target.value);
                                                        setValidation({ ...validation, password: validatePassword(e.target.value) });
                                                        if (confirmPassword) {
                                                            setValidation(prev => ({ ...prev, confirmPassword: validateConfirmPassword(confirmPassword) }));
                                                        }
                                                    }}
                                                    placeholder="••••••••"
                                                    className={`w-full h-12 bg-[#0A0C10] border rounded-xl pl-10 pr-4 text-white placeholder:text-gray-600 focus:outline-none focus:ring-2 focus:ring-aurora-purple/50 transition-all ${validation.password ? 'border-red-500' : 'border-white/[0.08]'}`}
                                                    required
                                                />
                                            </div>
                                            {password && (
                                                <div className="mt-2 space-y-2">
                                                    <div className="flex items-center gap-2">
                                                        <div className="flex gap-1 flex-1">
                                                            {[1, 2, 3, 4, 5].map((level) => (
                                                                <div
                                                                    key={level}
                                                                    className={`h-1 flex-1 rounded-full transition-all ${
                                                                        level <= passwordStrength.score
                                                                            ? passwordStrength.color
                                                                            : 'bg-white/[0.1]'
                                                                    }`}
                                                                />
                                                            ))}
                                                        </div>
                                                        <span className={`text-[10px] font-medium ${
                                                            passwordStrength.score <= 1 ? 'text-red-400' :
                                                            passwordStrength.score <= 2 ? 'text-orange-400' :
                                                            passwordStrength.score <= 3 ? 'text-yellow-400' :
                                                            'text-emerald-400'
                                                        }`}>
                                                            {passwordStrength.message}
                                                        </span>
                                                    </div>
                                                    <div className="flex gap-3 text-[10px] text-accessible-subtle">
                                                        <span className={`flex items-center gap-1 ${password.length >= 8 ? 'text-emerald-400' : ''}`}>
                                                            {password.length >= 8 ? <Check className="w-3 h-3" /> : <div className="w-3 h-3 rounded-full border border-current" />}
                                                            8+ characters
                                                        </span>
                                                        <span className={`flex items-center gap-1 ${/[A-Z]/.test(password) ? 'text-emerald-400' : ''}`}>
                                                            {/[A-Z]/.test(password) ? <Check className="w-3 h-3" /> : <div className="w-3 h-3 rounded-full border border-current" />}
                                                            Uppercase
                                                        </span>
                                                        <span className={`flex items-center gap-1 {/\d/.test(password) ? 'text-emerald-400' : ''}`}>
                                                            {/\d/.test(password) ? <Check className="w-3 h-3" /> : <div className="w-3 h-3 rounded-full border border-current" />}
                                                            Number
                                                        </span>
                                                        <span className={`flex items-center gap-1 ${/[^a-zA-Z0-9]/.test(password) ? 'text-emerald-400' : ''}`}>
                                                            {/[^a-zA-Z0-9]/.test(password) ? <Check className="w-3 h-3" /> : <div className="w-3 h-3 rounded-full border border-current" />}
                                                            Symbol
                                                        </span>
                                                    </div>
                                                </div>
                                            )}
                                        </div>

                                        <div>
                                            <label className="block text-xs font-medium text-accessible-subtle mb-2" htmlFor="signup-confirm-password">Confirm Password</label>
                                            <div className="relative">
                                                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-accessible-subtle" />
                                                <input
                                                    id="signup-confirm-password"
                                                    type="password"
                                                    value={confirmPassword}
                                                    onChange={(e) => {
                                                        setConfirmPassword(e.target.value);
                                                        setValidation({ ...validation, confirmPassword: validateConfirmPassword(e.target.value) });
                                                    }}
                                                    placeholder="••••••••"
                                                    className={`w-full h-12 bg-[#0A0C10] border rounded-xl pl-10 pr-4 text-white placeholder:text-gray-600 focus:outline-none focus:ring-2 focus:ring-aurora-purple/50 transition-all ${validation.confirmPassword ? 'border-red-500' : 'border-white/[0.08]'}`}
                                                    required
                                                />
                                            </div>
                                            {validation.confirmPassword && (
                                                <div className="flex items-center gap-1.5 mt-1.5 text-red-400 text-[10px]">
                                                    <XCircle className="w-3 h-3" />
                                                    {validation.confirmPassword}
                                                </div>
                                            )}
                                        </div>

                                        <Button
                                            type="submit"
                                            disabled={isLoading}
                                            className="w-full h-12 bg-gradient-to-r from-aurora-purple to-aurora-cyan hover:opacity-90 text-white rounded-xl font-bold transition-all shadow-lg shadow-aurora-purple/20"
                                        >
                                            Create Account
                                        </Button>
                                    </form>

                                    <p className="text-xs text-center text-accessible-subtle mt-6">
                                        By signing up, you agree to our{' '}
                                        <a href="#" className="text-accessible-muted hover:text-white transition-colors focus:outline-none focus:underline focus:underline-offset-2">Terms of Service</a>
                                        {' '}and{' '}
                                        <a href="#" className="text-accessible-muted hover:text-white transition-colors focus:outline-none focus:underline focus:underline-offset-2">Privacy Policy</a>
                                    </p>
                                </>
                            )}
                        </div>
                    </div>

                    {/* Mobile back button */}
                    <Link href="/" className="md:hidden mt-6 inline-flex items-center gap-2 text-accessible-subtle hover:text-white transition-colors group focus:outline-none focus:ring-2 focus:ring-aurora-purple/50 rounded-md">
                        <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" aria-hidden="true" />
                        <span className="text-sm font-medium">Back to Home</span>
                    </Link>
                </div>
            </motion.div>
        </div>
    );
}
