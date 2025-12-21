import React, { useEffect, useState } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { motion } from 'framer-motion';
import { CheckCircle, XCircle, Loader2 } from 'lucide-react';
import { Button } from '../components/ui/button';

export default function VerifyEmail() {
    const router = useRouter();
    const [status, setStatus] = useState('verifying'); // verifying, success, error
    const [message, setMessage] = useState('Verifying your email...');

    useEffect(() => {
        const verifyEmail = async () => {
            try {
                const { supabase } = await import('../lib/auth_utils');

                if (!supabase) {
                    setStatus('error');
                    setMessage('Supabase not configured');
                    return;
                }

                // Supabase automatically handles email verification via the URL hash
                const { error } = await supabase.auth.getSession();

                if (error) {
                    setStatus('error');
                    setMessage(error.message || 'Email verification failed');
                } else {
                    setStatus('success');
                    setMessage('Email verified successfully!');
                    setTimeout(() => router.push('/login'), 3000);
                }
            } catch (err) {
                setStatus('error');
                setMessage(err.message || 'An error occurred');
            }
        };

        verifyEmail();
    }, [router]);

    return (
        <div className="min-h-screen bg-gradient-to-br from-[#0A0C10] via-[#0d1117] to-[#0A0C10] flex items-center justify-center p-6">
            <Head>
                <title>Verify Email | ArchIntel Docs</title>
            </Head>

            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="w-full max-w-md"
            >
                <div className="bg-[#0d1117]/80 backdrop-blur-xl border border-white/[0.08] rounded-3xl p-8 shadow-2xl text-center">
                    <div className="flex flex-col items-center mb-6">
                        {status === 'verifying' && (
                            <div className="w-16 h-16 rounded-2xl bg-aurora-cyan/10 border border-aurora-cyan/30 flex items-center justify-center mb-4">
                                <Loader2 className="w-8 h-8 text-aurora-cyan animate-spin" />
                            </div>
                        )}
                        {status === 'success' && (
                            <div className="w-16 h-16 rounded-2xl bg-green-500/10 border border-green-500/30 flex items-center justify-center mb-4">
                                <CheckCircle className="w-8 h-8 text-green-500" />
                            </div>
                        )}
                        {status === 'error' && (
                            <div className="w-16 h-16 rounded-2xl bg-red-500/10 border border-red-500/30 flex items-center justify-center mb-4">
                                <XCircle className="w-8 h-8 text-red-500" />
                            </div>
                        )}

                        <h2 className="text-2xl font-bold text-white mb-2">
                            {status === 'verifying' && 'Verifying Email'}
                            {status === 'success' && 'Email Verified!'}
                            {status === 'error' && 'Verification Failed'}
                        </h2>
                        <p className={`text-sm ${status === 'error' ? 'text-red-400' : 'text-gray-400'}`}>
                            {message}
                        </p>
                    </div>

                    {status === 'success' && (
                        <p className="text-xs text-gray-500 mb-6">
                            Redirecting to login page...
                        </p>
                    )}

                    {status === 'error' && (
                        <Link href="/login">
                            <Button className="w-full h-12 bg-gradient-to-r from-aurora-purple to-aurora-cyan hover:opacity-90 text-white rounded-xl font-bold">
                                Go to Login
                            </Button>
                        </Link>
                    )}
                </div>
            </motion.div>
        </div>
    );
}
