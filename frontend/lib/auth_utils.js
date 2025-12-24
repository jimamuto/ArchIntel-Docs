import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || '';
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || '';

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
            redirectTo: `${process.env.NEXT_PUBLIC_SITE_URL || window.location.origin}/projects`,
        }
    });

    if (error) throw error;
};

export const signInWithGoogle = async () => {
    if (!supabase) throw new Error('Supabase not configured');

    const { error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
            redirectTo: `${process.env.NEXT_PUBLIC_SITE_URL || window.location.origin}/projects`,
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

// Email Authentication Functions
export const signUpWithEmail = async (email, password) => {
    if (!supabase) throw new Error('Supabase not configured');

    const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
            emailRedirectTo: `${window.location.origin}/verify-email`,
        }
    });

    if (error) throw error;
    return data;
};

export const signInWithEmail = async (email, password) => {
    if (!supabase) throw new Error('Supabase not configured');

    const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password,
    });

    if (error) throw error;
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
