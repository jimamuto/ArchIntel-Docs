import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import {
  Plus,
  Trash2,
  GitBranch,
  Search,
  MoreHorizontal,
  Folder,
  ArrowRight,
  Clock,
  CheckCircle2,
  AlertCircle,
  Loader2,
  LayoutDashboard,
  Settings,
  Bell,
  Filter,
  ArrowUpDown,
  Code2,
  Database,
  Activity,
  Terminal,
  ChevronDown,
  Github,
  Zap,
  RefreshCw,
  X
} from 'lucide-react';
import { useToast } from '../lib/toast';
import { cn } from '../lib/utils';
import { authenticatedFetch, getSession } from '../lib/auth_utils';
import Head from 'next/head';

// --- Background Component ---
const BlueprintBackground = () => (
  <div className="absolute inset-0 -z-10 overflow-hidden pointer-events-none">
    <div className="absolute inset-0 bg-aurora-bg" />
    <div
      className="absolute inset-0 opacity-[0.05]"
      style={{
        backgroundImage: `linear-gradient(#232329 1px, transparent 1px), linear-gradient(to right, #232329 1px, transparent 1px)`,
        backgroundSize: '3rem 3rem',
        maskImage: 'radial-gradient(ellipse at center, white 20%, transparent 80%)'
      }}
    />
  </div>
);

const UserNav = () => (
  <div className="h-8 w-8 rounded-full bg-gradient-to-tr from-aurora-purple to-aurora-cyan border border-white/10 shadow-inner flex items-center justify-center text-[10px] font-bold text-white">
    JD
  </div>
);

interface Project {
  id: number;
  name: string;
  repo_url: string;
  status: 'active' | 'analyzing' | 'error' | 'archived' | 'ready';
  created_at?: string;
  last_analyzed?: string;
  file_count?: number;
  languages?: string[];
}

export default function DashboardPage() {
  const router = useRouter();
  const { success: showToast, error: showError } = useToast();
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState({ projects: true, submission: false, syncing: false });
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [showCLIModal, setShowCLIModal] = useState(false);
  const [syncingIds, setSyncingIds] = useState<Set<number>>(new Set());

  async function handleSync(id: number) {
    setSyncingIds(prev => new Set(prev).add(id));
    try {
      const project = projects.find(p => p.id === id);
      if (!project) return;

      const res = await authenticatedFetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/projects/${id}/sync`, {
        method: 'POST'
      });

      if (res.ok) {
        showToast(`Synchronization initialized for ${project.name}.`);
        // Refresh project list after a short delay to see status changes
        setTimeout(async () => {
          const refresh = await authenticatedFetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/projects`);
          const refreshData = await refresh.json();
          setProjects(refreshData.projects || []);
        }, 1000);
      } else {
        showError("Sync failed.");
      }
    } catch (err) {
      showError("Connection lost.");
    } finally {
      setSyncingIds(prev => {
        const next = new Set(prev);
        next.delete(id);
        return next;
      });
    }
  }

  async function deleteProject(id: number) {
    if (!confirm('Are you sure you want to terminate this node?')) return;
    try {
      const res = await authenticatedFetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/projects/${id}`, { method: 'DELETE' });
      if (res.ok) {
        setProjects(projects.filter(p => p.id !== id));
        showToast("Node terminated.");
      } else {
        showError("Termination failed.");
      }
    } catch (err) {
      showError("Connection lost.");
    }
  }

  // Form State
  const [name, setName] = useState('');
  const [repoUrl, setRepoUrl] = useState('');
  const [githubToken, setGithubToken] = useState('');
  const [userRepos, setUserRepos] = useState<any[]>([]);
  const [loadingRepos, setLoadingRepos] = useState(false);

  // Filter State
  const [filter, setFilter] = useState('');

  // Authentication and Fetch projects
  useEffect(() => {
    async function checkAuthAndFetch() {
      const session = await getSession();
      if (!session) {
        router.push('/login');
        return;
      }

      // Automatically fetch GitHub repos if provider token is available
      if (session.provider_token) {
        setGithubToken(session.provider_token);
        setLoadingRepos(true);
        try {
          const res = await fetch('https://api.github.com/user/repos?sort=updated&per_page=100', {
            headers: { Authorization: `token ${session.provider_token}` }
          });
          const repos = await res.json();
          setUserRepos(Array.isArray(repos) ? repos : []);
        } catch (e) {
          console.error("Failed to fetch repos", e);
        } finally {
          setLoadingRepos(false);
        }
      }

      setLoading(prev => ({ ...prev, projects: true }));
      try {
        const res = await authenticatedFetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/projects`);
        if (!res.ok) throw new Error('Failed to fetch');
        const data = await res.json();
        setProjects(data.projects || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(prev => ({ ...prev, projects: false }));
      }
    }

    if (router.isReady) {
      checkAuthAndFetch();
    }
  }, [router.isReady]);

  // Legacy OAuth listener (can be kept for manual linking if needed, but primary flow is now session-based)
  useEffect(() => {
    const handleMessage = async (event: MessageEvent) => {
      if (event.data?.type === 'GITHUB_AUTH_SUCCESS' && event.data?.token) {
        setGithubToken(event.data.token);
        showToast("GitHub Connected Successfully");

        setLoadingRepos(true);
        try {
          const res = await fetch('https://api.github.com/user/repos?sort=updated&per_page=100', {
            headers: { Authorization: `token ${event.data.token}` }
          });
          const repos = await res.json();
          setUserRepos(Array.isArray(repos) ? repos : []);
        } catch (e) {
          console.error("Failed to fetch repos", e);
        } finally {
          setLoadingRepos(false);
        }
      }
    };
    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, [showToast]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(prev => ({ ...prev, submission: true }));
    try {
      const res = await authenticatedFetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/projects`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name,
          repo_url: repoUrl,
          github_token: githubToken || undefined
        })
      });
      if (!res.ok) throw new Error('Failed to create');
      const data = await res.json();

      // Background clone
      authenticatedFetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/projects/${data.project.id}/clone`, { method: 'POST' }).catch(() => { });

      showToast('Project created successfully');
      setShowCreateForm(false);
      setName(''); setRepoUrl(''); setGithubToken('');

      // Refresh
      const refresh = await authenticatedFetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/projects`);
      const refreshData = await refresh.json();
      setProjects(refreshData.projects || []);
    } catch (err) {
      showError('Failed to create project');
    } finally {
      setLoading(prev => ({ ...prev, submission: false }));
    }
  }

  return (
    <div className="min-h-screen flex flex-col bg-aurora-bg text-slate-200 font-sans selection:bg-aurora-purple/30">
      <Head>
        <title>Dashboard | ArchIntel</title>
      </Head>

      <BlueprintBackground />

      {/* 1. Specialized Technical Navbar */}
      <header className="h-16 border-b border-aurora-border bg-[#0A0C10]/80 backdrop-blur-md sticky top-0 z-50">
        <div className="container mx-auto h-full px-6 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <h2 className="text-sm font-bold uppercase tracking-widest text-white/50 font-mono">Registry</h2>
            <div className="h-4 w-px bg-white/[0.1]" />
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-gray-500" />
              <input
                type="text"
                placeholder="Search resources..."
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
                className="w-64 bg-[#15171B] border border-white/[0.08] rounded-full pl-9 pr-4 py-1.5 text-xs text-gray-300 focus:outline-none focus:border-aurora-purple/50 transition-all"
              />
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-[10px] font-mono text-gray-500 uppercase">
              <div className="w-2 h-2 rounded-full bg-green-500 shadow-glow shadow-green-500/50" />
              <span>Node Active</span>
            </div>
          </div>
        </div>
      </header>

      {/* 2. Main Workspace */}
      <main className="flex-1 max-w-7xl mx-auto w-full p-6 md:p-10 space-y-10 relative">

        {/* Page Header Area */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
          <div className="space-y-1">
            <div className="flex items-center gap-2 text-aurora-cyan text-[10px] uppercase font-bold tracking-[0.2em] font-mono mb-2">
              <Activity className="w-3 h-3" />
              Architectural Registry
            </div>
            <h1 className="text-4xl font-bold text-white tracking-tight">System Index</h1>
            <p className="text-gray-500 max-w-lg">
              Manage your system knowledge graphs and structural analysis projects from a centralized intelligence hub.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <Button
              variant="outline"
              onClick={() => setShowCLIModal(true)}
              className="border-white/[0.08] bg-white/[0.02] hover:bg-white/[0.05] text-gray-400 rounded-xl group"
            >
              <Terminal className="w-4 h-4 mr-2 group-hover:text-aurora-purple transition-colors" />
              CLI Access
            </Button>
            <Button onClick={() => setShowCreateForm(true)} className="bg-aurora-purple hover:bg-aurora-purple/80 text-white shadow-glow rounded-xl px-6 font-bold">
              <Plus className="mr-2 h-4 w-4" /> New Repository
            </Button>
          </div>
        </div>

        {/* 3. High-End Projects Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {loading.projects ? (
            [1, 2, 3].map(i => (
              <div key={i} className="h-48 rounded-2xl border border-white/[0.05] bg-white/[0.02] animate-pulse" />
            ))
          ) : projects.length === 0 ? (
            <div className="col-span-full space-y-6">
              {/* Welcome Card */}
              <div className="p-8 rounded-3xl bg-gradient-to-br from-aurora-purple/10 via-transparent to-aurora-cyan/10 border border-white/[0.1] relative overflow-hidden">
                <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGRlZnM+PHBhdHRlcm4gaWQ9ImdyaWQiIHdpZHRoPSI0MCIgaGVpZ2h0PSI0MCIgcGF0dGVyblVuaXRzPSJ1c2VyU3BhY2VPblVzZSI+PHBhdGggZD0iTSAwIDEwIEwgNDAgMTAgTSAxMCAwIEwgMTAgNDAgTSAwIDIwIEwgNDAgMjAgTSAyMCAwIEwgMjAgNDAgTSAwIDMwIEwgNDAgMzAgTSAzMCAwIEwgMzAgNDAiIGZpbGw9Im5vbmUiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS1vcGFjaXR5PSIwLjAzIiBzdHJva2Utd2lkdGg9IjEiLz48L3BhdHRlcm4+PC9kZWZzPjxyZWN0IHdpZHRoPSIxMDAlIiBoZWlnaHQ9IjEwMCUiIGZpbGw9InVybCgjZ3JpZCkiLz48L3N2Zz4=')] opacity-40" />
                <div className="relative z-10">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="w-12 h-12 rounded-xl bg-aurora-purple/20 border border-aurora-purple/30 flex items-center justify-center">
                      <Zap className="w-6 h-6 text-aurora-purple" />
                    </div>
                    <div>
                      <h2 className="text-2xl font-bold text-white">Welcome to ArchIntel</h2>
                      <p className="text-sm text-gray-400">Structural Intelligence Platform</p>
                    </div>
                  </div>
                  <p className="text-gray-300 leading-relaxed max-w-2xl">
                    Transform your codebase into actionable intelligence. Start by registering a repository to unlock AST-powered documentation, dependency graphs, and AI-driven architectural insights.
                  </p>
                </div>
              </div>

              {/* Getting Started Steps */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-6 rounded-2xl bg-[#0A0C10] border border-white/[0.08] hover:border-aurora-purple/30 transition-all group">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="w-8 h-8 rounded-lg bg-aurora-purple/10 border border-aurora-purple/20 flex items-center justify-center text-aurora-purple font-bold text-sm">
                      1
                    </div>
                    <h3 className="font-bold text-white">Register Repository</h3>
                  </div>
                  <p className="text-sm text-gray-400 leading-relaxed mb-4">
                    Click <span className="text-aurora-purple font-semibold">"New Repository"</span> above to add a GitHub URL. We'll clone and analyze the structure.
                  </p>
                  <Button
                    onClick={() => setShowCreateForm(true)}
                    className="w-full bg-aurora-purple/10 hover:bg-aurora-purple/20 text-aurora-purple border border-aurora-purple/30 rounded-xl"
                  >
                    <Plus className="w-4 h-4 mr-2" /> Add Repository
                  </Button>
                </div>

                <div className="p-6 rounded-2xl bg-[#0A0C10] border border-white/[0.08] opacity-60">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="w-8 h-8 rounded-lg bg-gray-700/20 border border-gray-700/30 flex items-center justify-center text-gray-500 font-bold text-sm">
                      2
                    </div>
                    <h3 className="font-bold text-gray-400">Explore Intelligence</h3>
                  </div>
                  <p className="text-sm text-gray-500 leading-relaxed">
                    Once analyzed, click <span className="font-semibold">"Explorer"</span> to view documentation, dependency graphs, and architectural insights.
                  </p>
                </div>

                <div className="p-6 rounded-2xl bg-[#0A0C10] border border-white/[0.08] opacity-60">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="w-8 h-8 rounded-lg bg-gray-700/20 border border-gray-700/30 flex items-center justify-center text-gray-500 font-bold text-sm">
                      3
                    </div>
                    <h3 className="font-bold text-gray-400">Query Architecture</h3>
                  </div>
                  <p className="text-sm text-gray-500 leading-relaxed">
                    Press <span className="font-mono font-semibold">Cmd+K</span> in Explorer to ask questions like "Where is authentication?" or "List all APIs".
                  </p>
                </div>
              </div>
            </div>
          ) : (
            projects
              .filter(p =>
                p.name.toLowerCase().includes(filter.toLowerCase()) ||
                p.repo_url.toLowerCase().includes(filter.toLowerCase())
              )
              .map((project) => (
                <div
                  key={project.id}
                  onClick={() => router.push(`/docs?project=${project.id}`)}
                  className="group relative bg-[#0A0C10] border border-white/[0.08] rounded-2xl p-6 hover:border-aurora-purple/50 transition-all cursor-pointer overflow-hidden shadow-sm"
                >
                  {/* Subtle Glow Background */}
                  <div className="absolute top-0 right-0 w-32 h-32 bg-aurora-purple/5 blur-3xl -translate-y-1/2 translate-x-1/2 group-hover:bg-aurora-purple/10 transition-colors" />

                  <div className="relative z-10 space-y-4">
                    <div className="flex items-start justify-between">
                      <div className="w-10 h-10 rounded-lg bg-[#15171B] border border-white/[0.05] flex items-center justify-center group-hover:border-aurora-purple/30 transition-colors">
                        <GitBranch className="w-5 h-5 text-gray-400 group-hover:text-aurora-purple transition-colors" />
                      </div>
                      <div className={cn(
                        "px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider flex items-center gap-1.5",
                        project.status === 'active' ? "bg-green-500/10 text-green-500 border border-green-500/20" :
                          project.status === 'analyzing' ? "bg-yellow-500/10 text-yellow-500 border border-yellow-500/20" :
                            "bg-white/[0.05] text-gray-500 border border-white/[0.05]"
                      )}>
                        <div className={cn("w-1.5 h-1.5 rounded-full", project.status === 'active' ? "bg-green-500" : "bg-yellow-500")} />
                        {project.status || 'Ready'}
                      </div>
                    </div>

                    <div>
                      <h3 className="text-lg font-bold text-white group-hover:text-aurora-cyan transition-colors truncate">
                        {project.name}
                      </h3>
                      <p className="text-xs text-gray-500 font-mono mt-1 opacity-60 truncate">
                        {project.repo_url.replace('https://github.com/', '')}
                      </p>
                    </div>

                    <div className="pt-4 flex items-center justify-between border-t border-white/[0.03]">
                      <div className="flex flex-col">
                        <span className="text-[10px] uppercase text-gray-600 font-bold tracking-tight">Last Analysis</span>
                        <span className="text-xs text-gray-400 font-mono">
                          {project.last_analyzed ? new Date(project.last_analyzed).toLocaleDateString() : 'Pending'}
                        </span>
                      </div>
                      <div className="flex items-center gap-1 relative z-20">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={(e) => { e.stopPropagation(); handleSync(project.id); }}
                          className="h-8 w-8 p-0 text-gray-500 hover:text-white"
                          title="Sync Analysis"
                        >
                          <RefreshCw className={cn("w-3.5 h-3.5", syncingIds.has(project.id) && "animate-spin")} />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={(e) => { e.stopPropagation(); deleteProject(project.id); }}
                          className="h-8 w-8 p-0 text-gray-500 hover:text-red-500"
                          title="Terminate Node"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </Button>
                        <Button variant="ghost" size="sm" className="h-8 group/btn text-gray-500 hover:text-aurora-cyan text-[10px] gap-2 px-2">
                          Explorer <ArrowRight className="w-3 h-3 transition-transform group-hover/btn:translate-x-1" />
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>
              ))
          )}
        </div>

        {/* 4. Stats Footer Bar */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-8 rounded-3xl bg-[#0A0C10] border border-white/[0.05] shadow-inner relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-r from-aurora-purple/5 via-transparent to-aurora-cyan/5 opacity-50" />

          <div className="relative z-10 flex flex-col">
            <span className="text-[10px] uppercase font-bold text-gray-600 tracking-widest mb-1">Total Nodes</span>
            <span className="text-3xl font-bold text-white font-mono">{projects.length}</span>
          </div>
          <div className="relative z-10 flex flex-col">
            <span className="text-[10px] uppercase font-bold text-gray-600 tracking-widest mb-1">Active Sync</span>
            <span className="text-3xl font-bold text-aurora-cyan font-mono">{projects.filter(p => p.status === 'active' || p.status === 'ready').length}</span>
          </div>
          <div className="relative z-10 flex flex-col">
            <span className="text-[10px] uppercase font-bold text-gray-600 tracking-widest mb-1">Languages</span>
            <span className="text-3xl font-bold text-white font-mono">
              {(() => {
                const allLanguages = new Set();
                projects.forEach(p => {
                  if (p.languages) p.languages.forEach(lang => allLanguages.add(lang));
                });
                return allLanguages.size || 0;
              })()}
            </span>
          </div>
          <div className="relative z-10 flex flex-col">
            <span className="text-[10px] uppercase font-bold text-gray-600 tracking-widest mb-1">Up-Time</span>
            <span className="text-3xl font-bold text-aurora-pink font-mono">
              {projects.length > 0 ? ((projects.filter(p => p.status !== 'error').length / projects.length) * 100).toFixed(1) : '100.0'}%
            </span>
          </div>
        </div>
      </main>

      {/* Form Modal (Aurora Dialog Style) */}
      {showCreateForm && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/95 backdrop-blur-sm animate-in fade-in duration-300">
          <div className="w-full max-w-lg bg-[#0A0C10] border border-aurora-border rounded-2xl shadow-2xl p-8 relative overflow-hidden">
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-aurora-purple via-aurora-cyan to-aurora-pink" />

            <button
              onClick={() => setShowCreateForm(false)}
              className="absolute top-4 right-4 text-gray-500 hover:text-white transition-colors"
            >
              <Plus className="w-6 h-6 rotate-45" />
            </button>

            <div className="space-y-2 mb-8">
              <h2 className="text-2xl font-bold text-white tracking-tight">Register Node</h2>
              <p className="text-sm text-gray-500">Inject a repository into the ArchIntel structural engine.</p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="space-y-4">
                <div className="grid gap-2">
                  <label className="text-xs font-bold uppercase tracking-wider text-gray-500 font-mono">Project Identifier</label>
                  <input
                    required
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="flex h-12 w-full rounded-xl border border-white/[0.08] bg-[#15171B] px-4 text-sm transition-all focus:border-aurora-purple/50 focus:ring-1 focus:ring-aurora-purple/20 text-white placeholder:text-gray-700"
                    placeholder="e.g. CORE-SYSTEM-V2"
                  />
                </div>
                <div className="grid gap-2">
                  <label className="text-xs font-bold uppercase tracking-wider text-gray-500 font-mono">Repository Source (GIT)</label>
                  <div className="relative">
                    <Github className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-600" />

                    {githubToken && userRepos.length > 0 ? (
                      <select
                        required
                        value={repoUrl}
                        onChange={(e) => {
                          setRepoUrl(e.target.value);
                          // Auto-fill name if empty
                          if (!name) {
                            const repo = userRepos.find(r => r.html_url === e.target.value || r.clone_url === e.target.value);
                            if (repo) setName(repo.name.toUpperCase());
                          }
                        }}
                        className="flex h-12 w-full appearance-none rounded-xl border border-white/[0.08] bg-[#15171B] pl-12 pr-4 text-sm transition-all focus:border-aurora-purple/50 focus:ring-1 focus:ring-aurora-purple/20 text-white placeholder:text-gray-700"
                      >
                        <option value="">Select a repository...</option>
                        {userRepos.map(repo => (
                          <option key={repo.id} value={repo.clone_url}>
                            {repo.full_name} ({repo.private ? 'Private' : 'Public'})
                          </option>
                        ))}
                      </select>
                    ) : (
                      <input
                        required
                        type="url"
                        value={repoUrl}
                        onChange={(e) => setRepoUrl(e.target.value)}
                        className="flex h-12 w-full rounded-xl border border-white/[0.08] bg-[#15171B] pl-12 pr-4 text-sm transition-all focus:border-aurora-purple/50 focus:ring-1 focus:ring-aurora-purple/20 text-white placeholder:text-gray-700"
                        placeholder="https://github.com/organization/repo"
                      />
                    )}
                  </div>
                  {githubToken && loadingRepos && <p className="text-[10px] text-gray-500 pl-1">Loading repositories...</p>}
                </div>

                <div className="grid gap-2">
                  <label className="text-xs font-bold uppercase tracking-wider text-gray-500 font-mono">
                    GitHub Access
                  </label>

                  {githubToken ? (
                    <div className="flex items-center justify-between p-3 rounded-xl bg-green-500/10 border border-green-500/20">
                      <div className="flex items-center gap-2">
                        <CheckCircle2 className="w-4 h-4 text-green-500" />
                        <span className="text-sm text-green-400 font-bold">GitHub Connected</span>
                      </div>
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => setGithubToken('')}
                        className="text-gray-500 hover:text-white h-6 px-2"
                      >
                        Disconnect
                      </Button>
                    </div>
                  ) : (
                    <div className="space-y-2">
                      <Button
                        type="button"
                        onClick={() => {
                          const width = 600;
                          const height = 700;
                          const left = (window.screen.width - width) / 2;
                          const top = (window.screen.height - height) / 2;
                          window.open(
                            `${process.env.NEXT_PUBLIC_API_BASE_URL}/auth/github/login`,
                            'github_oauth',
                            `width=${width},height=${height},top=${top},left=${left}`
                          );
                        }}
                        className="w-full bg-[#24292F] hover:bg-[#24292F]/80 text-white border border-white/10 rounded-xl flex items-center justify-center gap-2"
                      >
                        <Github className="w-4 h-4" />
                        Connect GitHub Account
                      </Button>
                      <p className="text-[10px] text-gray-500 text-center">
                        Required for private repositories. Grants read-only access.
                      </p>
                    </div>
                  )}
                </div>
              </div>

              <div className="flex flex-col gap-3 pt-4">
                <Button type="submit" disabled={loading.submission} className="h-12 bg-aurora-purple hover:bg-aurora-purple/80 text-white font-bold rounded-xl shadow-glow">
                  {loading.submission ? (
                    <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                  ) : (
                    <Zap className="mr-2 h-4 w-4 fill-current" />
                  )}
                  Initialize Core Analysis
                </Button>
                <div className="flex items-center justify-center gap-2 text-[10px] text-gray-600 font-mono uppercase tracking-widest">
                  <AlertCircle className="w-3 h-3 text-aurora-cyan" />
                  Stateless secure analysis active
                </div>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* CLI Access Modal */}
      {showCLIModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/80 backdrop-blur-md" onClick={() => setShowCLIModal(false)} />
          <div className="relative w-full max-w-lg bg-[#0A0C10] border border-white/[0.1] rounded-2xl shadow-2xl p-8">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-aurora-purple/10 border border-aurora-purple/20">
                  <Terminal className="w-5 h-5 text-aurora-purple" />
                </div>
                <h3 className="text-xl font-bold text-white">CLI Configuration</h3>
              </div>
              <button onClick={() => setShowCLIModal(false)} className="text-gray-500 hover:text-white transition-colors">
                <X className="w-6 h-6" />
              </button>
            </div>

            <div className="space-y-6">
              <div className="space-y-3">
                <span className="text-[10px] font-bold text-gray-500 uppercase tracking-widest">Base Command</span>
                <div className="p-4 rounded-xl bg-black border border-white/[0.05] font-mono text-sm text-aurora-cyan">
                  python backend/cli.py --help
                </div>
              </div>

              <div className="space-y-4">
                <span className="text-[10px] font-bold text-gray-500 uppercase tracking-widest">Global Operations</span>
                {[
                  { cmd: 'list', desc: 'List all architectural nodes' },
                  { cmd: 'analyze <url>', desc: 'Initialize node analysis' },
                  { cmd: 'query <id> <text>', desc: 'Interactive arch intelligence' }
                ].map(item => (
                  <div key={item.cmd} className="flex items-center justify-between p-3 rounded-xl bg-white/[0.02] border border-white/[0.05]">
                    <code className="text-xs text-aurora-purple">cli.py {item.cmd}</code>
                    <span className="text-[10px] text-gray-500 font-mono">{item.desc}</span>
                  </div>
                ))}
              </div>

              <p className="text-[10px] text-gray-600 italic">
                Ensure the backend server is running at http://localhost:8000 before executing CLI commands.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
