import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || '';
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || '';
const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

// Create a Supabase client only if credentials are provided
export const supabase = supabaseUrl && supabaseKey
    ? createClient(supabaseUrl, supabaseKey)
    : null;

export const getSession = async () => {
    if (!supabase) {
        console.warn('Supabase not configured. Please set NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY');
        return null;
    }

    try {
        // Check for stored tokens from 2FA flow
        const storedAccessToken = localStorage.getItem('supabase_access_token');
        const storedRefreshToken = localStorage.getItem('supabase_refresh_token');

        if (storedAccessToken && storedRefreshToken) {
            try {
                // Set the session using stored tokens
                const { data: { session }, error } = await supabase.auth.setSession({
                    access_token: storedAccessToken,
                    refresh_token: storedRefreshToken
                });

                if (!error && session) {
                    // Clear stored tokens after setting session
                    localStorage.removeItem('supabase_access_token');
                    localStorage.removeItem('supabase_refresh_token');
                    return session;
                }
            } catch (setSessionError) {
                console.error('Error setting session from stored tokens:', setSessionError);
                // Clear invalid tokens
                localStorage.removeItem('supabase_access_token');
                localStorage.removeItem('supabase_refresh_token');
            }
        }

        // Fall back to existing session
        const { data: { session }, error } = await supabase.auth.getSession();
        if (error) return null;
        return session;
    } catch (error) {
        console.error('Error getting session:', error);
        return null;
    }
};

export const logout = async () => {
    if (supabase) {
        await supabase.auth.signOut();
    }
    window.location.href = '/login';
};

export const signInWithGitHub = async () => {
    if (!supabase) throw new Error('Supabase not configured');

    const { error } = await supabase.auth.signInWithOAuth({
        provider: 'github',
        options: {
            redirectTo: `${process.env.NEXT_PUBLIC_SITE_URL || window.location.origin}/auth-callback`,
        }
    });

    if (error) throw error;
};

export const signInWithGoogle = async () => {
    if (!supabase) throw new Error('Supabase not configured');

    const { error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
            redirectTo: `${process.env.NEXT_PUBLIC_SITE_URL || window.location.origin}/auth-callback`,
        }
    });

    if (error) throw error;
};

export const authenticatedFetch = async (url, options = {}) => {
    const session = await getSession();
    const headers = {
        ...options.headers,
        'Authorization': `Bearer ${session?.access_token}`,
    };

    return fetch(url, { ...options, headers });
};

// Email Authentication Functions with 2FA
export const signUpWithEmail = async (email, password) => {
    const response = await fetch(`${apiBaseUrl}/auth/signup`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password })
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.error?.message || data.message || 'Failed to create account');
    }

    return data;
};

export const signInWithEmail = async (email, password) => {
    const response = await fetch(`${apiBaseUrl}/auth/login`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password })
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.error?.message || data.message || 'Invalid email or password');
    }

    return data;
};

export const verify2FACode = async (email, code) => {
    const response = await fetch(`${apiBaseUrl}/auth/verify-2fa`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, code })
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.error?.message || data.message || 'Invalid verification code');
    }

    return data;
};

export const resend2FACode = async (email) => {
    const response = await fetch(`${apiBaseUrl}/auth/resend-2fa`, {
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

    return data;
};

export const resetPassword = async (email) => {
    if (!supabase) throw new Error('Supabase not configured');

    const { error } = await supabase.auth.resetPasswordForEmail(email, {
        redirectTo: `${window.location.origin}/reset-password`,
    });

    if (error) throw error;
};

export const updatePassword = async (newPassword) => {
    if (!supabase) throw new Error('Supabase not configured');

    const { error } = await supabase.auth.updateUser({
        password: newPassword,
    });

    if (error) throw error;
};

// Two-Factor Authentication Functions
export const enrollMFA = async () => {
    if (!supabase) throw new Error('Supabase not configured');

    const { data, error } = await supabase.auth.mfa.enroll({
        factorType: 'totp',
    });

    if (error) throw error;
    return data;
};

export const verifyMFA = async (factorId, code) => {
    if (!supabase) throw new Error('Supabase not configured');

    const { data, error } = await supabase.auth.mfa.challengeAndVerify({
        factorId,
        code,
    });

    if (error) throw error;
    return data;
};

export const unenrollMFA = async (factorId) => {
    if (!supabase) throw new Error('Supabase not configured');

    const { error } = await supabase.auth.mfa.unenroll({
        factorId,
    });

    if (error) throw error;
};

export const getMFAFactors = async () => {
    if (!supabase) throw new Error('Supabase not configured');

    const { data, error } = await supabase.auth.mfa.listFactors();

    if (error) throw error;
    return data;
};
