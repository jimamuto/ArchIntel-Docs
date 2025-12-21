import React, { useState } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { motion } from 'framer-motion';
import { Mail, ArrowLeft, CheckCircle } from 'lucide-react';
import { Button } from '../components/ui/button';
import { resetPassword } from '../lib/auth_utils';

export default function ResetPassword() {
    const router = useRouter();
    const [email, setEmail] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [success, setSuccess] = useState(false);
    const [error, setError] = useState(null);

    const handleReset = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        setError(null);

        try {
            await resetPassword(email);
            setSuccess(true);
        } catch (err) {
            setError(err.message || 'Failed to send reset email');
        } finally {
            setIsLoading(false);
        }
    };

    if (success) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-[#0A0C10] via-[#0d1117] to-[#0A0C10] flex items-center justify-center p-6">
                <Head>
                    <title>Check Your Email | ArchIntel Docs</title>
                </Head>

                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="w-full max-w-md"
                >
                    <div className="bg-[#0d1117]/80 backdrop-blur-xl border border-white/[0.08] rounded-3xl p-8 shadow-2xl text-center">
                        <div className="w-16 h-16 rounded-2xl bg-green-500/10 border border-green-500/30 flex items-center justify-center mx-auto mb-6">
                            <CheckCircle className="w-8 h-8 text-green-500" />
                        </div>
                        <h2 className="text-2xl font-bold text-white mb-2">Check your email</h2>
                        <p className="text-sm text-gray-400 mb-6">
                            We've sent a password reset link to <span className="text-white font-medium">{email}</span>
                        </p>
                        <Link href="/login">
                            <Button className="w-full h-12 bg-gradient-to-r from-aurora-purple to-aurora-cyan hover:opacity-90 text-white rounded-xl font-bold">
                                Back to Login
                            </Button>
                        </Link>
                    </div>
                </motion.div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-[#0A0C10] via-[#0d1117] to-[#0A0C10] flex items-center justify-center p-6">
            <Head>
                <title>Reset Password | ArchIntel Docs</title>
            </Head>

            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="w-full max-w-md"
            >
                <div className="bg-[#0d1117]/80 backdrop-blur-xl border border-white/[0.08] rounded-3xl p-8 shadow-2xl">
                    <div className="mb-8">
                        <h2 className="text-2xl font-bold text-white mb-2">Reset your password</h2>
                        <p className="text-sm text-gray-400">
                            Enter your email address and we'll send you a link to reset your password
                        </p>
                    </div>

                    {error && (
                        <div className="mb-6 p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
                            {error}
                        </div>
                    )}

                    <form onSubmit={handleReset} className="space-y-6">
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

                        <Button
                            type="submit"
                            disabled={isLoading}
                            className="w-full h-12 bg-gradient-to-r from-aurora-purple to-aurora-cyan hover:opacity-90 text-white rounded-xl font-bold transition-all shadow-lg shadow-aurora-purple/20"
                        >
                            {isLoading ? 'Sending...' : 'Send Reset Link'}
                        </Button>
                    </form>

                    <div className="mt-6 text-center">
                        <Link href="/login" className="inline-flex items-center gap-2 text-sm text-gray-400 hover:text-white transition-colors">
                            <ArrowLeft className="w-4 h-4" />
                            Back to login
                        </Link>
                    </div>
                </div>
            </motion.div>
        </div>
    );
}
