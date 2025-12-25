import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';
import { motion } from 'framer-motion';
import { Loader2, AlertCircle, CheckCircle } from 'lucide-react';
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || '';
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || '';
const supabase = supabaseUrl && supabaseKey ? createClient(supabaseUrl, supabaseKey) : null;

export default function AuthCallback() {
    const router = useRouter();
    const [status, setStatus] = useState('loading');
    const [error, setError] = useState(null);

    useEffect(() => {
        const handleCallback = async () => {
            if (!supabase) {
                setStatus('error');
                setError('Supabase not configured');
                return;
            }

            try {
                // Parse the hash fragment for OAuth tokens
                const hash = window.location.hash;
                
                if (hash && hash.includes('access_token')) {
                    // Supabase will automatically handle the session from the hash
                    // Just need to wait for it to process
                    const { data: { session }, error } = await supabase.auth.getSession();
                    
                    if (error) {
                        setStatus('error');
                        setError(error.message);
                        return;
                    }
                    
                    if (session) {
                        setStatus('success');
                        // Redirect to projects after a short delay
                        setTimeout(() => {
                            router.push('/projects');
                        }, 1000);
                    } else {
                        // Check if we're using PKCE flow with code
                        const params = new URLSearchParams(hash.substring(1));
                        const code = params.get('code');
                        
                        if (code) {
                            // Supabase JS SDK will handle the code exchange
                            // Wait for session to be established
                            const maxAttempts = 10;
                            let attempts = 0;
                            
                            const checkSession = setInterval(async () => {
                                attempts++;
                                const { data: { session } } = await supabase.auth.getSession();
                                
                                if (session || attempts >= maxAttempts) {
                                    clearInterval(checkSession);
                                    
                                    if (session) {
                                        setStatus('success');
                                        setTimeout(() => {
                                            router.push('/projects');
                                        }, 1000);
                                    } else {
                                        setStatus('error');
                                        setError('Unable to establish session. Please try again.');
                                    }
                                }
                            }, 500);
                        }
                    }
                } else if (hash.includes('error')) {
                    // Handle OAuth errors
                    const params = new URLSearchParams(hash.substring(1));
                    const errorDesc = params.get('error_description') || 'Authentication failed';
                    setStatus('error');
                    setError(errorDesc);
                } else {
                    // No hash, might be a direct redirect from email verification
                    const { data: { session } } = await supabase.auth.getSession();
                    
                    if (session) {
                        setStatus('success');
                        setTimeout(() => {
                            router.push('/projects');
                        }, 1000);
                    } else {
                        setStatus('error');
                        setError('No authentication session found');
                    }
                }
            } catch (err) {
                setStatus('error');
                setError(err.message || 'An error occurred during authentication');
            }
        };

        handleCallback();
    }, [router]);

    if (status === 'loading') {
        return (
            <div className="min-h-screen bg-[#060608] flex items-center justify-center p-6">
                <Head>
                    <title>Authenticating | ArchIntel</title>
                </Head>
                
                <div className="text-center">
                    <motion.div
                        animate={{ rotate: 360 }}
                        transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                        className="w-16 h-16 mx-auto mb-6"
                    >
                        <div className="w-16 h-16 rounded-full border-2 border-white/10" />
                        <div className="absolute top-0 left-0 w-16 h-16 rounded-full border-2 border-transparent border-t-aurora-purple" />
                    </motion.div>
                    <p className="text-white font-medium">Authenticating...</p>
                </div>
            </div>
        );
    }

    if (status === 'error') {
        return (
            <div className="min-h-screen bg-[#060608] flex items-center justify-center p-6">
                <Head>
                    <title>Authentication Error | ArchIntel</title>
                </Head>
                
                <div className="max-w-md w-full">
                    <div className="bg-[#0d1117]/80 backdrop-blur-xl border border-white/[0.08] rounded-3xl p-8 shadow-2xl text-center">
                        <div className="w-16 h-16 rounded-2xl bg-red-500/10 border border-red-500/20 flex items-center justify-center mx-auto mb-6">
                            <AlertCircle className="w-8 h-8 text-red-500" />
                        </div>
                        
                        <h2 className="text-2xl font-bold text-white mb-2">Authentication Failed</h2>
                        <p className="text-gray-400 mb-6">{error}</p>
                        
                        <button
                            onClick={() => router.push('/login')}
                            className="w-full h-12 bg-aurora-purple hover:bg-aurora-purple/80 text-white rounded-xl font-bold transition-all"
                        >
                            Return to Login
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    if (status === 'success') {
        return (
            <div className="min-h-screen bg-[#060608] flex items-center justify-center p-6">
                <Head>
                    <title>Authentication Successful | ArchIntel</title>
                </Head>
                
                <div className="text-center">
                    <div className="w-16 h-16 rounded-2xl bg-green-500/10 border border-green-500/20 flex items-center justify-center mx-auto mb-6">
                        <CheckCircle className="w-8 h-8 text-green-500" />
                    </div>
                    
                    <h2 className="text-2xl font-bold text-white mb-2">Authentication Successful</h2>
                    <p className="text-gray-400">Redirecting you to your dashboard...</p>
                </div>
            </div>
        );
    }

    return null;
}
