import { useState, useEffect } from 'react';
import { Button } from '../components/ui/button';
import { Card } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Input } from '../components/ui/input';

interface Project {
  id: number;
  name: string;
  repo_url: string;
  status?: string;
  created_at?: string;
}

export default function Projects() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [name, setName] = useState('');
  const [repoUrl, setRepoUrl] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState<string | null>(null);
  const [deletingProject, setDeletingProject] = useState<string | null>(null);

  useEffect(() => {
    async function fetchProjects() {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/projects`);
        if (!res.ok) throw new Error('Failed to fetch projects');
        const data = await res.json();
        setProjects(data.projects || []);
      } catch (err) {
        setError((err as Error).message);
      } finally {
        setLoading(false);
      }
    }
    fetchProjects();
  }, [success]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    setSuccess(null);
    try {
      // First register the project
      const registerRes = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/projects`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, repo_url: repoUrl })
      });
      if (!registerRes.ok) throw new Error('Failed to register project');

      const registerData = await registerRes.json();
      const projectId = registerData.project.id;

      // Then automatically clone and ingest the repository
      try {
        const cloneRes = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/projects/${projectId}/clone`, {
          method: 'POST'
        });

        if (cloneRes.ok) {
          const cloneData = await cloneRes.json();
          setSuccess(`Project registered and ${cloneData.message.split(' ')[3]} files ingested!`);
        } else {
          setSuccess('Project registered! Repository cloning may take a moment - check back soon.');
        }
      } catch (cloneErr) {
        setSuccess('Project registered! Repository cloning may take a moment - check back soon.');
      }

      setName('');
      setRepoUrl('');
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setSubmitting(false);
    }
  }

  async function handleDelete(projectId: string | number) {
    if (!confirm('Are you sure you want to delete this project? This action cannot be undone.')) {
      return;
    }

    setDeletingProject(projectId.toString());
    setError(null);
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/projects/${projectId}`, {
        method: 'DELETE'
      });
      if (!res.ok) throw new Error('Failed to delete project');

      // Remove the project from the list
      setProjects(projects.filter(p => p.id !== projectId));
      setSuccess('Project deleted successfully!');
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setDeletingProject(null);
    }
  }

  return (
    <main className="min-h-screen bg-slate-950 px-4 py-8">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-slate-50 mb-2">Projects</h1>
            <p className="text-sm text-slate-400">Manage and explore your codebase documentation</p>
          </div>
          <Button
            variant="default"
            className="h-10 rounded-lg bg-emerald-500 px-6 text-sm font-medium text-slate-950 shadow-sm hover:bg-emerald-400 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500/70 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950"
          >
            New Project
          </Button>
        </div>

        <Card className="bg-slate-900/60 backdrop-blur-sm border-slate-800/50 p-6 mb-8">
          <div className="flex flex-col sm:flex-row gap-4">
            <Input
              type="text"
              placeholder="Project Name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              className="flex-1 bg-slate-800 border-slate-700 text-slate-50 placeholder:text-slate-400 focus:border-emerald-500"
            />
            <Input
              type="url"
              placeholder="Repository URL"
              value={repoUrl}
              onChange={(e) => setRepoUrl(e.target.value)}
              required
              className="flex-1 bg-slate-800 border-slate-700 text-slate-50 placeholder:text-slate-400 focus:border-emerald-500"
            />
            <Button type="submit" disabled={submitting} onClick={handleSubmit} className="bg-emerald-500 hover:bg-emerald-400 text-slate-950 px-6">
              {submitting ? 'Creating...' : 'Create Project'}
            </Button>
          </div>
          {success && (
            <div className="mt-4 p-3 bg-emerald-500/10 border border-emerald-500/30 rounded-lg">
              <p className="text-emerald-400 text-sm">{success}</p>
            </div>
          )}
          {error && (
            <div className="mt-4 p-3 bg-rose-500/10 border border-rose-500/30 rounded-lg">
              <p className="text-rose-400 text-sm">{error}</p>
            </div>
          )}
        </Card>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[...Array(6)].map((_, i) => (
              <Card key={i} className="flex flex-col gap-2 rounded-xl border border-slate-800 bg-slate-900/80 px-4 py-3">
                <div className="flex items-center justify-between gap-2">
                  <div className="h-4 bg-slate-700 rounded animate-pulse w-3/4"></div>
                  <div className="h-5 bg-slate-700 rounded animate-pulse w-16"></div>
                </div>
                <div className="h-3 bg-slate-700 rounded animate-pulse w-full mb-1"></div>
                <div className="h-3 bg-slate-700 rounded animate-pulse w-2/3"></div>
                <div className="flex items-center gap-3 mt-2">
                  <div className="h-3 bg-slate-700 rounded animate-pulse w-20"></div>
                  <div className="h-1 w-1 bg-slate-600 rounded-full"></div>
                  <div className="h-3 bg-slate-700 rounded animate-pulse w-24"></div>
                </div>
              </Card>
            ))}
          </div>
        ) : projects.length === 0 ? (
          <Card className="bg-slate-900/60 backdrop-blur-sm border-slate-800/50 p-12 text-center">
            <div className="w-16 h-16 bg-slate-800 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl">📁</span>
            </div>
            <h3 className="text-lg font-semibold text-slate-50 mb-2">No projects yet</h3>
            <p className="text-slate-400 mb-6 max-w-md mx-auto">
              Get started by creating your first project. Connect a Git repository to generate AI-powered documentation.
            </p>
            <Button className="bg-emerald-500 hover:bg-emerald-400 text-slate-950">
              Create Your First Project
            </Button>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {projects.map((p) => (
              <Card key={p.id} className="group relative flex flex-col gap-3 rounded-xl border border-slate-800 bg-slate-900/80 px-5 py-4 shadow-sm shadow-black/40 transition-all duration-200 ease-out hover:-translate-y-[2px] hover:border-slate-700 hover:bg-slate-900 hover:shadow-lg hover:shadow-black/60 cursor-pointer">
                <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-emerald-500/60 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-200" />
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1 min-w-0">
                    <h3 className="text-base font-semibold text-slate-50 truncate mb-1">
                      {p.name}
                    </h3>
                    <p className="text-xs text-slate-500 truncate">{p.repo_url}</p>
                  </div>
                  <Badge variant="outline" className="border-emerald-500/40 bg-emerald-500/10 text-emerald-300 shrink-0">
                    Active
                  </Badge>
                </div>
                <p className="text-sm text-slate-400 leading-relaxed">
                  Intelligent documentation with real-time code analysis and team collaboration insights.
                </p>
                <div className="flex items-center justify-between text-xs text-slate-500 mt-auto">
                  <div className="flex items-center gap-3">
                    <span>Last updated 2h ago</span>
                    <span className="h-1 w-1 rounded-full bg-slate-600"></span>
                    <span>12 modules • 145 files</span>
                  </div>
                  <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-7 px-2 text-xs text-rose-400 hover:text-rose-300 hover:bg-rose-500/10"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDelete(p.id);
                      }}
                      disabled={deletingProject === p.id.toString()}
                    >
                      {deletingProject === p.id.toString() ? '...' : '🗑️'}
                    </Button>
                    <Button variant="ghost" size="sm" className="h-7 px-2 text-xs text-slate-400 hover:text-slate-50">
                      View →
                    </Button>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </main>
  );
}
