import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';
import { motion } from 'framer-motion';
import { ArrowLeft, Mail, Shield, CheckCircle, ArrowRight, Loader2 } from 'lucide-react';
import { Button } from '../components/ui/button';

const BlueprintBackground = () => (
    <div className="absolute inset-0 z-0 overflow-hidden pointer-events-none opacity-10">
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:40px_40px] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)]" />
    </div>
);

export default function Verify2FA() {
    const router = useRouter();
    const [isLoading, setIsLoading] = useState(false);
    const [code, setCode] = useState('');
    const [error, setError] = useState(null);
    const [timeLeft, setTimeLeft] = useState(600);
    const [isResending, setIsResending] = useState(false);
    const [resendSuccess, setResendSuccess] = useState(false);

    const email = router.query.email || '';

    useEffect(() => {
        if (!email) {
            router.push('/login');
        }

        const timer = setInterval(() => {
            setTimeLeft((prev) => {
                if (prev <= 1) {
                    clearInterval(timer);
                    return 0;
                }
                return prev - 1;
            });
        }, 1000);

        return () => clearInterval(timer);
    }, [email, router]);

    const formatTime = (seconds) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    };

    const handleCodeChange = (e) => {
        const value = e.target.value.replace(/\D/g, '').slice(0, 6);
        setCode(value);
    };

    const handleVerify = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        setError(null);

        if (code.length !== 6) {
            setError('Please enter the full 6-digit code');
            setIsLoading(false);
            return;
        }

        try {
            const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/auth/verify-2fa`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email,
                    code
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error?.message || data.message || 'Verification failed');
            }

            // Store tokens in localStorage for use with Supabase
            if (data.access_token) {
                localStorage.setItem('supabase_access_token', data.access_token);
            }
            if (data.refresh_token) {
                localStorage.setItem('supabase_refresh_token', data.refresh_token);
            }

            // Redirect to projects page
            router.push('/projects');
        } catch (err) {
            setError(err.message || 'Invalid verification code. Please try again.');
            setCode('');
        } finally {
            setIsLoading(false);
        }
    };

    const handleResend = async () => {
        setIsResending(true);
        setError(null);

        try {
            const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/auth/resend-2fa`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error?.message || data.message || 'Failed to resend code');
            }

            setResendSuccess(true);
            setTimeLeft(600);
            setCode('');

            setTimeout(() => {
                setResendSuccess(false);
            }, 3000);
        } catch (err) {
            setError(err.message || 'Failed to resend verification code');
        } finally {
            setIsResending(false);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-[#0A0C10] via-[#0d1117] to-[#0A0C10] flex items-center justify-center p-6 relative overflow-hidden">
            <Head>
                <title>Verify Your Email | ArchIntel Docs</title>
            </Head>

            <BlueprintBackground />

            <div className="absolute top-0 right-1/4 w-96 h-96 bg-aurora-purple/20 blur-[120px] rounded-full animate-pulse" />
            <div className="absolute bottom-0 left-1/4 w-96 h-96 bg-aurora-cyan/20 blur-[120px] rounded-full animate-pulse" style={{ animationDelay: '1s' }} />

            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6 }}
                className="w-full max-w-md z-10"
            >
                <div className="mb-8">
                    <button
                        onClick={() => router.push('/login')}
                        className="inline-flex items-center gap-2 text-gray-400 hover:text-white transition-colors group"
                    >
                        <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
                        <span className="text-sm font-medium">Back to login</span>
                    </button>
                </div>

                <div className="bg-[#0d1117]/80 backdrop-blur-xl border border-white/[0.08] rounded-3xl p-8 shadow-2xl">
                    <div className="text-center mb-8">
                        <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-aurora-purple to-aurora-cyan p-0.5 mx-auto mb-6">
                            <div className="w-full h-full bg-[#0A0C10] rounded-[14px] flex items-center justify-center">
                                <Mail className="w-10 h-10 text-white" />
                            </div>
                        </div>

                        <h2 className="text-2xl font-bold text-white mb-2">
                            Verify your email
                        </h2>
                        <p className="text-sm text-gray-400">
                            We sent a 6-digit code to{' '}
                            <span className="text-white font-medium">{email}</span>
                        </p>
                    </div>

                    {error && (
                        <div className="mb-6 p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
                            {error}
                        </div>
                    )}

                    {resendSuccess && (
                        <motion.div
                            initial={{ opacity: 0, y: -10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="mb-6 p-4 rounded-xl bg-green-500/10 border border-green-500/20 text-green-400 text-sm flex items-center gap-2"
                        >
                            <CheckCircle className="w-4 h-4" />
                            New code sent successfully
                        </motion.div>
                    )}

                    <form onSubmit={handleVerify} className="space-y-6" noValidate>
                        <div>
                            <label className="block text-xs font-medium text-gray-400 mb-3 text-center">
                                Enter verification code
                            </label>
                            <div className="flex justify-center gap-2">
                                {[0, 1, 2, 3, 4, 5].map((index) => (
                                    <input
                                        key={index}
                                        type="text"
                                        inputMode="numeric"
                                        maxLength="1"
                                        value={code[index] || ''}
                                        onChange={(e) => {
                                            const newCode = code.split('');
                                            newCode[index] = e.target.value;
                                            const updated = newCode.join('');
                                            setCode(updated);
                                            
                                            if (e.target.value && index < 5) {
                                                const nextInput = document.getElementById(`code-${index + 1}`);
                                                if (nextInput) nextInput.focus();
                                            }
                                        }}
                                        onKeyDown={(e) => {
                                            if (e.key === 'Backspace' && !code[index] && index > 0) {
                                                const prevInput = document.getElementById(`code-${index - 1}`);
                                                if (prevInput) prevInput.focus();
                                            }
                                        }}
                                        id={`code-${index}`}
                                        className="w-12 h-14 bg-[#0A0C10] border-2 border-white/[0.08] rounded-xl text-center text-2xl font-bold text-white focus:outline-none focus:border-aurora-purple/50 focus:ring-2 focus:ring-aurora-purple/50 transition-all"
                                        required
                                    />
                                ))}
                            </div>
                        </div>

                        <div className="text-center">
                            <p className="text-sm text-gray-400 mb-2">
                                Code expires in{' '}
                                <span className={`font-medium ${timeLeft <= 60 ? 'text-red-400' : 'text-white'}`}>
                                    {formatTime(timeLeft)}
                                </span>
                            </p>
                            <button
                                type="button"
                                onClick={handleResend}
                                disabled={isResending || timeLeft > 540}
                                className="text-sm text-aurora-cyan hover:text-aurora-cyan/80 disabled:text-gray-600 disabled:cursor-not-allowed transition-colors"
                            >
                                {isResending ? 'Sending...' : 'Resend code'}
                            </button>
                        </div>

                        <Button
                            type="submit"
                            disabled={isLoading || code.length !== 6}
                            className="w-full h-12 bg-gradient-to-r from-aurora-purple to-aurora-cyan hover:opacity-90 disabled:opacity-50 text-white rounded-xl font-bold transition-all shadow-lg shadow-aurora-purple/20 flex items-center justify-center gap-2"
                        >
                            {isLoading ? (
                                <>
                                    <Loader2 className="w-5 h-5 animate-spin" />
                                    Verifying...
                                </>
                            ) : (
                                <>
                                    Verify
                                    <ArrowRight className="w-5 h-5" />
                                </>
                            )}
                        </Button>
                    </form>

                    <div className="mt-6 p-4 rounded-xl bg-white/[0.02] border border-white/[0.05]">
                        <div className="flex items-start gap-3">
                            <Shield className="w-5 h-5 text-aurora-purple flex-shrink-0 mt-0.5" />
                            <div className="text-xs text-gray-400 leading-relaxed">
                                <p className="font-medium text-white mb-1">Security Tip</p>
                                <p>Never share your verification code with anyone. Our team will never ask for it.</p>
                            </div>
                        </div>
                    </div>
                </div>
            </motion.div>
        </div>
    );
}