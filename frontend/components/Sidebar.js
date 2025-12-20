import Link from 'next/link';
import { useRouter } from 'next/router';
import {
    LayoutDashboard,
    Search,
    Zap,
    Settings,
    Code2,
    Activity,
    Box
} from 'lucide-react';
import { cn } from '../lib/utils';

const SidebarItem = ({ icon: Icon, href, active, label }) => (
    <Link
        href={href}
        className={cn(
            "group relative flex items-center justify-center h-12 w-12 rounded-xl transition-all duration-300 mb-2",
            active
                ? "bg-aurora-purple/10 text-aurora-purple shadow-glow shadow-aurora-purple/20"
                : "text-gray-500 hover:text-gray-300 hover:bg-white/[0.05]"
        )}
        title={label}
    >
        <Icon className={cn("w-5 h-5", active && "scale-110")} />
        {active && (
            <div className="absolute left-0 w-1 h-6 bg-aurora-purple rounded-r-full" />
        )}
    </Link>
);

export default function Sidebar() {
    const router = useRouter();

    // Don't show sidebar on landing page if you prefer, 
    // but the user asked for navigation through pages.
    // We can hide it on '/' if we want, but let's keep it for now as a global app scaffold.
    if (router.pathname === '/') return null;

    const navItems = [
        { icon: LayoutDashboard, href: '/projects', label: 'Dashboard' },
        { icon: Search, href: '/docs', label: 'Explorer' },
        { icon: Box, href: '/integrations', label: 'Integrations' },
    ];

    return (
        <aside className="w-[68px] h-screen bg-[#0A0C10] border-r border-aurora-border flex flex-col items-center py-6 flex-shrink-0 z-50">
            {/* Logo */}
            <Link href="/" className="mb-8 group">
                <div className="w-10 h-10 rounded-xl bg-[#15171B] border border-white/[0.08] flex items-center justify-center group-hover:border-aurora-purple/50 transition-all duration-500 shadow-lg">
                    <Code2 className="w-6 h-6 text-aurora-purple group-hover:scale-110 transition-transform" />
                </div>
            </Link>

            {/* Navigation */}
            <div className="flex-1 flex flex-col items-center w-full">
                {navItems.map((item) => (
                    <SidebarItem
                        key={item.href}
                        {...item}
                        active={router.pathname === item.href || (item.href === '/projects' && router.pathname.startsWith('/projects/'))}
                    />
                ))}
            </div>

            {/* Bottom Actions */}
            <div className="flex flex-col items-center gap-4">
                <Link href="/activity" className={cn(
                    "h-10 w-10 flex items-center justify-center transition-colors rounded-xl",
                    router.pathname === '/activity' ? "text-aurora-cyan bg-aurora-cyan/10" : "text-gray-500 hover:text-white"
                )}>
                    <Activity className="w-5 h-5" />
                </Link>
                <Link href="/settings" className={cn(
                    "h-10 w-10 flex items-center justify-center transition-colors rounded-xl",
                    router.pathname === '/settings' ? "text-aurora-purple bg-aurora-purple/10" : "text-gray-500 hover:text-white"
                )}>
                    <Settings className="w-5 h-5" />
                </Link>
                <div className="h-8 w-8 rounded-full bg-gradient-to-tr from-aurora-purple to-aurora-cyan border border-white/10 shadow-inner flex items-center justify-center text-[10px] font-bold text-white cursor-pointer">
                    JD
                </div>
            </div>
        </aside>
    );
}
