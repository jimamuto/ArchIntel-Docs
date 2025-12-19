import Link from 'next/link';
import { useRouter } from 'next/router';

export default function Sidebar({ children }) {
  const router = useRouter();

  const isActive = (path) => {
    if (path === '/') {
      return router.pathname === '/';
    }
    return router.pathname.startsWith(path);
  };

  const navItems = [
    {
      href: '/',
      label: 'Home',
      icon: '🏠',
      description: 'Dashboard overview'
    },
    {
      href: '/projects',
      label: 'Projects',
      icon: '📁',
      description: 'Manage codebases'
    },
    {
      href: '/docs',
      label: 'Docs Explorer',
      icon: '📄',
      description: 'Browse documentation'
    }
  ];

  return (
    <aside className="w-64 bg-gradient-to-b from-slate-950 to-slate-900 border-r border-slate-800/50 min-h-screen flex flex-col relative overflow-hidden">
      {/* Subtle background pattern */}
      <div className="absolute inset-0 opacity-20">
        <div className="absolute top-0 left-0 w-full h-px bg-gradient-to-r from-transparent via-emerald-500/30 to-transparent"></div>
      </div>

      {/* Header */}
      <div className="relative flex-shrink-0 p-5 border-b border-slate-800/30">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-8 h-8 bg-gradient-to-br from-emerald-500 to-emerald-400 rounded-lg flex items-center justify-center shadow-lg shadow-emerald-500/20">
            <span className="text-slate-950 text-sm font-bold">A</span>
          </div>
          <div>
            <h2 className="text-sm font-bold text-slate-50">ArchIntel</h2>
            <p className="text-xs text-slate-400">Docs</p>
          </div>
        </div>
        <p className="text-xs text-slate-500 leading-tight">
          AI-powered documentation for modern development teams
        </p>
      </div>

      {/* Navigation */}
      <nav className="relative flex-shrink-0 p-3">
        <div className="mb-3">
          <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider px-3 mb-2">
            Navigation
          </h3>
        </div>
        <ul className="space-y-1">
          {navItems.map((item) => (
            <li key={item.href}>
              <Link
                href={item.href}
                className={`group relative flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${
                  isActive(item.href)
                    ? 'bg-emerald-500/10 text-emerald-300 border-l-2 border-emerald-500 shadow-sm shadow-emerald-500/10'
                    : 'text-slate-300 hover:bg-slate-800/80 hover:text-slate-50 hover:translate-x-1'
                }`}
              >
                <span className={`flex h-6 w-6 items-center justify-center rounded-md transition-all duration-200 ${
                  isActive(item.href)
                    ? 'bg-emerald-500/20 text-emerald-300'
                    : 'bg-slate-800 text-slate-500 group-hover:bg-slate-700'
                }`}>
                  {item.icon}
                </span>
                <div className="flex-1 min-w-0">
                  <div className="truncate">{item.label}</div>
                  <div className={`text-xs transition-opacity duration-200 ${
                    isActive(item.href) ? 'text-emerald-400/70' : 'text-slate-500 opacity-0 group-hover:opacity-100'
                  }`}>
                    {item.description}
                  </div>
                </div>
                {isActive(item.href) && (
                  <div className="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-pulse"></div>
                )}
              </Link>
            </li>
          ))}
        </ul>
      </nav>

      {/* Content Area - This should expand to fill remaining space */}
      <div className="relative flex-1 min-h-0 p-4">
        <div className="h-full rounded-lg bg-slate-900/30 backdrop-blur-sm border border-slate-800/30 p-4 overflow-hidden">
          {children || (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <div className="w-12 h-12 bg-slate-800 rounded-full flex items-center justify-center mb-3">
                <span className="text-slate-400">⚡</span>
              </div>
              <p className="text-xs text-slate-400 leading-tight">
                Quick actions and<br />recent activity
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Footer */}
      <div className="relative flex-shrink-0 p-4 border-t border-slate-800/30">
        <div className="flex items-center justify-between text-xs text-slate-500">
          <span>v1.0.0</span>
          <div className="flex items-center gap-1">
            <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></div>
            <span>Online</span>
          </div>
        </div>
      </div>
    </aside>
  );
}
