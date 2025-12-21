import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { motion } from 'framer-motion';
import { Shield, ArrowLeft, Loader2 } from 'lucide-react';
import { Button } from '../components/ui/button';
import { verifyMFA } from '../lib/auth_utils';

export default function Verify2FA() {
    const router = useRouter();
    const [code, setCode] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleVerify = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        setError(null);

        try {
            const { getMFAFactors } = await import('../lib/auth_utils');
            const factors = await getMFAFactors();

            if (!factors || !factors.totp || factors.totp.length === 0) {
                throw new Error('No 2FA factor found');
            }

            const factorId = factors.totp[0].id;
            await verifyMFA(factorId, code);

            router.push('/projects');
        } catch (err) {
            setError(err.message || 'Invalid verification code');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-[#0A0C10] via-[#0d1117] to-[#0A0C10] flex items-center justify-center p-6">
            <Head>
                <title>Two-Factor Authentication | ArchIntel Docs</title>
            </Head>

            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="w-full max-w-md"
            >
                <div className="bg-[#0d1117]/80 backdrop-blur-xl border border-white/[0.08] rounded-3xl p-8 shadow-2xl">
                    <div className="flex flex-col items-center mb-8">
                        <div className="w-16 h-16 rounded-2xl bg-aurora-purple/10 border border-aurora-purple/30 flex items-center justify-center mb-4">
                            <Shield className="w-8 h-8 text-aurora-purple" />
                        </div>
                        <h2 className="text-2xl font-bold text-white mb-2">Two-Factor Authentication</h2>
                        <p className="text-sm text-gray-400 text-center">
                            Enter the 6-digit code from your authenticator app
                        </p>
                    </div>

                    {error && (
                        <div className="mb-6 p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
                            {error}
                        </div>
                    )}

                    <form onSubmit={handleVerify} className="space-y-6">
                        <div>
                            <input
                                type="text"
                                value={code}
                                onChange={(e) => setCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                                placeholder="000000"
                                className="w-full h-16 bg-[#0A0C10] border border-white/[0.08] rounded-xl text-center text-2xl font-mono text-white placeholder:text-gray-600 focus:outline-none focus:border-aurora-purple/50 focus:ring-1 focus:ring-aurora-purple/20 transition-all tracking-[0.5em]"
                                maxLength={6}
                                required
                                autoFocus
                            />
                        </div>

                        <Button
                            type="submit"
                            disabled={isLoading || code.length !== 6}
                            className="w-full h-12 bg-gradient-to-r from-aurora-purple to-aurora-cyan hover:opacity-90 text-white rounded-xl font-bold transition-all shadow-lg shadow-aurora-purple/20"
                        >
                            {isLoading ? (
                                <Loader2 className="w-5 h-5 animate-spin" />
                            ) : (
                                'Verify'
                            )}
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
