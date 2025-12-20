import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/router';
import { Button } from '../components/ui/button';
import { ScrollArea } from '../components/ui/scroll-area';
import {
  Download,
  FileText,
  Code2,
  Database,
  RefreshCw,
  FolderTree,
  Cpu,
  File,
  ChevronRight,
  ChevronDown,
  LayoutTemplate,
  Terminal,
  Search,
  Zap,
  Activity,
  Share2,
  Network,
  X,
  ArrowUpRight,
  ArrowDownLeft
} from 'lucide-react';
import { cn } from '../lib/utils';
import Link from 'next/link';
import { useToast } from '../lib/toast';
import Head from 'next/head';
import { motion, AnimatePresence } from 'framer-motion';

// --- Background Component ---
const BlueprintBackground = () => (
  <div className="absolute inset-0 -z-10 overflow-hidden pointer-events-none">
    <div className="absolute inset-0 bg-aurora-bg" />
    <div
      className="absolute inset-0 opacity-[0.06]"
      style={{
        backgroundImage: `linear-gradient(#232329 1px, transparent 1px), linear-gradient(to right, #232329 1px, transparent 1px)`,
        backgroundSize: '3rem 3rem',
        maskImage: 'radial-gradient(ellipse at center, white 20%, transparent 80%)'
      }}
    />
  </div>
);

export default function Docs() {
  const router = useRouter();
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState('');
  const [selectedProjectData, setSelectedProjectData] = useState(null);
  const [structure, setStructure] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [docs, setDocs] = useState(null);
  const [code, setCode] = useState(null);
  const [systemDoc, setSystemDoc] = useState(null);
  const [showSystemDoc, setShowSystemDoc] = useState(false);
  const [loading, setLoading] = useState({
    projects: true,
    structure: false,
    content: false,
    cloning: false,
    syncing: false
  });
  const { success: showToast, error: showError } = useToast();
  const [error, setError] = useState(null);
  const [showCode, setShowCode] = useState(false);
  const [expandedFolders, setExpandedFolders] = useState(new Set());

  // MVP Features State
  const [showSearch, setShowSearch] = useState(false);
  const [query, setQuery] = useState('');
  const [queryResponse, setQueryResponse] = useState('');
  const [isQuerying, setIsQuerying] = useState(false);
  const [graphData, setGraphData] = useState({ nodes: [], edges: [] });
  const [viewMode, setViewMode] = useState('doc'); // 'doc' or 'graph'

  // Shortcut for Command Palette
  useEffect(() => {
    const down = (e) => {
      if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setShowSearch(prev => !prev);
      }
    };
    document.addEventListener('keydown', down);
    return () => document.removeEventListener('keydown', down);
  }, []);

  async function handleQuery(e) {
    if (e) e.preventDefault();
    if (!query.trim() || !selectedProject) return;

    setIsQuerying(true);
    setQueryResponse('');
    try {
      const repoName = selectedProjectData.repo_url.split('/').pop().replace('.git', '');
      let repoPath = repoName === 'ArchIntel-Docs' ? '.' : `repos/${repoName}`;

      const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/docs/${selectedProject}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, repo_path: repoPath })
      });
      const data = await res.json();
      setQueryResponse(data.response);
    } catch (err) {
      setQueryResponse('Error connecting to architecture node.');
    } finally {
      setIsQuerying(false);
    }
  }

  async function fetchGraph() {
    if (!selectedProject || !selectedProjectData) return;
    if (graphData.nodes.length > 0) return;

    try {
      const repoName = selectedProjectData.repo_url.split('/').pop().replace('.git', '');
      let repoPath = repoName === 'ArchIntel-Docs' ? '.' : `repos/${repoName}`;
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/docs/${selectedProject}/graph?repo_path=${encodeURIComponent(repoPath)}`);
      const data = await res.json();
      setGraphData(data);
    } catch (err) {
      console.error("Failed to fetch graph", err);
    }
  }

  // Function to fetch system docs
  async function fetchSystemDoc() {
    if (!selectedProject || !selectedProjectData) return;

    setShowSystemDoc(true);
    if (systemDoc) return; // return if already fetched

    setLoading(prev => ({ ...prev, content: true }));
    try {
      const repoName = selectedProjectData.repo_url.split('/').pop().replace('.git', '');
      let repoPath = repoName === 'ArchIntel-Docs' ? '.' : `repos/${repoName}`;

      const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/docs/${selectedProject}/system/doc?repo_path=${encodeURIComponent(repoPath)}`);
      const text = await res.text();
      setSystemDoc(text);
    } catch (err) {
      console.error(err);
      setSystemDoc('# Error\nFailed to load system documentation.');
    } finally {
      setLoading(prev => ({ ...prev, content: false }));
    }
  }

  // Fetch projects on mount and restore last selection
  useEffect(() => {
    async function fetchProjects() {
      try {
        setLoading(prev => ({ ...prev, projects: true }));
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/projects`);
        const data = await res.json();
        const projectsList = data.projects || [];
        setProjects(projectsList);
        setError(null);

        // Selection Logic:
        // 1. Check Query Param
        // 2. Check LocalStorage
        // 3. Fallback to only project
        if (router.query.project) {
          setSelectedProject(router.query.project);
        } else if (!selectedProject) {
          const lastProject = localStorage.getItem('archintel_last_project');
          if (lastProject && projectsList.find(p => String(p.id) === String(lastProject))) {
            setSelectedProject(lastProject);
          } else if (projectsList.length === 1) {
            setSelectedProject(projectsList[0].id);
          }
        }
      } catch (err) {
        setError('Failed to load projects');
      } finally {
        setLoading(prev => ({ ...prev, projects: false }));
      }
    }

    if (router.isReady) {
      fetchProjects();
    }
  }, [router.isReady, router.query.project]);

  // Handle project selection and persist to localStorage
  useEffect(() => {
    if (!selectedProject) {
      setSelectedProjectData(null);
      setStructure([]);
      return;
    }

    // Save to localStorage for persistence
    localStorage.setItem('archintel_last_project', selectedProject);

    const project = projects.find(p => p.id === selectedProject);
    setSelectedProjectData(project);

    async function fetchProjectData() {
      setLoading(prev => ({ ...prev, structure: true }));
      setError(null);
      try {
        const structureRes = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/projects/${selectedProject}/structure`);
        const structureData = await structureRes.json();
        setStructure(structureData.structure || []);
      } catch (err) {
        console.error('Failed to load project data');
      } finally {
        setLoading(prev => ({ ...prev, structure: false }));
      }
    }

    fetchProjectData();
  }, [selectedProject, projects]);

  // Handle file selection
  useEffect(() => {
    if (!selectedProject || !selectedFile) return;

    async function fetchFileContent() {
      setLoading(prev => ({ ...prev, content: true }));
      setError(null);
      try {
        const repoName = selectedProjectData.repo_url.split('/').pop().replace('.git', '');
        let repoPath = repoName === 'ArchIntel-Docs' ? '.' : `repos/${repoName}`;

        const docRes = await fetch(
          `${process.env.NEXT_PUBLIC_API_BASE_URL}/docs/${selectedProject}/file/doc?path=${encodeURIComponent(selectedFile)}&repo_path=${encodeURIComponent(repoPath)}`
        );
        const docText = docRes.ok ? await docRes.text() : '// Documentation generation in progress...';
        setDocs(docText);

        const codeRes = await fetch(
          `${process.env.NEXT_PUBLIC_API_BASE_URL}/projects/${selectedProject}/file/code?path=${encodeURIComponent(selectedFile)}&repo_path=${encodeURIComponent(repoPath)}`
        );
        const codeText = codeRes.ok ? await codeRes.text() : '// Could not fetch source code';
        setCode(codeText);
      } catch (err) {
        setError('Failed to load file content');
      } finally {
        setLoading(prev => ({ ...prev, content: false }));
      }
    }

    fetchFileContent();
  }, [selectedProject, selectedFile, selectedProjectData]);

  const toggleFolder = (path) => {
    const newExpanded = new Set(expandedFolders);
    if (newExpanded.has(path)) {
      newExpanded.delete(path);
    } else {
      newExpanded.add(path);
    }
    setExpandedFolders(newExpanded);
  };

  const getFileStructure = () => {
    const tree = {};
    structure.forEach(file => {
      const parts = file.path.split('/');
      let current = tree;
      parts.forEach((part, index) => {
        if (!current[part]) {
          current[part] = { isFolder: index < parts.length - 1, children: {} };
        }
        current = current[part].children;
      });
    });
    return tree;
  };

  const renderFileTree = (node, path = '') => {
    return Object.entries(node).map(([name, data]) => {
      const currentPath = path ? `${path}/${name}` : name;
      const isSelected = selectedFile === currentPath;

      if (data.isFolder) {
        const isExpanded = expandedFolders.has(currentPath);
        return (
          <div key={currentPath} className="select-none">
            <button
              onClick={() => toggleFolder(currentPath)}
              className={cn(
                "w-full flex items-center gap-1.5 px-3 py-1.5 text-[13px] transition-colors rounded-sm group",
                isExpanded ? "text-white" : "text-gray-400 hover:text-gray-200 hover:bg-white/[0.04]"
              )}
            >
              <div className="text-gray-600 group-hover:text-gray-400">
                {isExpanded ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
              </div>
              <FolderTree className={cn("w-3.5 h-3.5 transition-colors", isExpanded ? "text-aurora-purple" : "text-gray-500 group-hover:text-aurora-purple/70")} />
              <span className="truncate font-medium">{name}</span>
            </button>
            {isExpanded && (
              <div className="ml-3 pl-3 border-l border-white/[0.05]">
                {renderFileTree(data.children, currentPath)}
              </div>
            )}
          </div>
        );
      } else {
        return (
          <button
            key={currentPath}
            onClick={() => setSelectedFile(currentPath)}
            className={cn(
              "w-full flex items-center gap-2 px-3 py-1.5 text-[13px] ml-3 transition-colors rounded-r-md border-l-2",
              isSelected
                ? "bg-aurora-purple/10 text-aurora-purple border-aurora-purple"
                : "border-transparent text-gray-500 hover:text-gray-300 hover:bg-white/[0.02]"
            )}
          >
            <File className="w-3.5 h-3.5 opacity-70" />
            <span className="truncate font-mono">{name}</span>
          </button>
        );
      }
    });
  };

  return (
    <div className="h-screen flex flex-col bg-aurora-bg text-gray-200 font-sans overflow-hidden">
      <Head>
        <title>Explorer | ArchIntel</title>
      </Head>
      <header className="h-16 border-b border-aurora-border flex items-center justify-between px-6 bg-[#0A0C10]/80 backdrop-blur-md relative z-20 shadow-sm">
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-4">
            <h2 className="text-sm font-bold uppercase tracking-widest text-white/50 font-mono">Explorer</h2>
            <div className="h-4 w-px bg-white/[0.1]" />
          </div>

          <div className="relative group min-w-[240px]">
            <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-gray-500" />
            <select
              onChange={(e) => setSelectedProject(e.target.value)}
              value={selectedProject || ''}
              className="w-full appearance-none bg-[#15171B] border border-white/[0.08] rounded-lg pl-8 pr-8 py-1.5 text-xs text-gray-300 focus:outline-none focus:border-aurora-purple/50 focus:ring-1 focus:ring-aurora-purple/20 transition-all cursor-pointer font-mono shadow-inner text-white"
            >
              <option value="" disabled>Select Repository...</option>
              {projects.map(p => (
                <option key={p.id} value={p.id}>{p.name}</option>
              ))}
            </select>
            <ChevronDown className="absolute right-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-gray-500 pointer-events-none" />
          </div>

          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowSearch(true)}
            className="h-8 border-white/[0.08] bg-white/[0.02] text-gray-500 hover:text-white hover:bg-white/[0.05] rounded-full px-4 text-[10px] font-mono flex gap-2"
          >
            <Zap className="w-3 h-3 text-aurora-purple fill-current" />
            <span className="hidden sm:inline">Command Palette</span>
            <kbd className="hidden sm:inline-flex h-4 items-center gap-1 rounded border border-white/[0.1] bg-white/[0.05] px-1.5 font-mono text-[8px] font-medium text-gray-400">
              <span className="text-[10px]">⌘</span>K
            </kbd>
          </Button>
        </div>

        <div className="flex items-center gap-3">
          {selectedProject && (
            <>
              <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-green-500/5 border border-green-500/10">
                <div className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
                <span className="text-[10px] uppercase font-bold tracking-wider text-green-500/80">System Online</span>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={async () => {
                  if (!selectedProject || loading.syncing) return;
                  setLoading(prev => ({ ...prev, syncing: true }));
                  try {
                    showToast("Initializing system re-scan...");
                    const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/projects/${selectedProject}/sync`, { method: 'POST' });
                    if (res.ok) {
                      showToast("System re-scan complete.");
                      window.location.reload();
                    } else {
                      showError("Re-scan failed.");
                    }
                  } catch (e) {
                    showError("Connection error.");
                  } finally {
                    setLoading(prev => ({ ...prev, syncing: false }));
                  }
                }}
                className="h-8 w-8 p-0 text-gray-500 hover:text-aurora-cyan hover:bg-white/[0.05] rounded-lg transition-colors"
                title="Sync System Nodes"
              >
                <RefreshCw className={cn("w-4 h-4", loading.syncing && "animate-spin")} />
              </Button>
            </>
          )}
        </div>
      </header>

      <div className="flex-1 flex overflow-hidden">
        {/* Component-Based Sidebar (File Explorer) */}
        <aside className="w-72 bg-[#0A0C10] border-r border-aurora-border flex flex-col relative z-10">
          <div className="py-2 px-4 shadow-[0_1px_0_0_rgba(255,255,255,0.02)]">
            <span className="text-[10px] font-bold uppercase tracking-wider text-gray-500 font-mono">Project Files</span>
          </div>

          <ScrollArea className="flex-1">
            {!selectedProject ? (
              <div className="flex flex-col items-center justify-center h-48 text-gray-600 p-6 text-center">
                <div className="w-12 h-12 rounded-xl bg-white/[0.02] flex items-center justify-center mb-3">
                  <FolderTree className="w-6 h-6 opacity-40" />
                </div>
                <span className="text-xs font-medium">No repository selected</span>
                <p className="text-[10px] mt-1 text-gray-700">Select a project from the header to inspect its structure.</p>
              </div>
            ) : structure.length === 0 ? (
              <div className="p-4 space-y-3">
                {[1, 2, 3].map(i => (
                  <div key={i} className="animate-pulse flex items-center gap-3">
                    <div className="w-3 h-3 bg-white/[0.05] rounded-sm" />
                    <div className="h-3 w-3/4 bg-white/[0.05] rounded-sm" />
                  </div>
                ))}

                <div className="mt-8 pt-4 border-t border-white/[0.05]">
                  <p className="text-[10px] text-gray-500 mb-2 text-center">Is this your first time?</p>
                  <Button
                    size="sm"
                    variant="secondary"
                    className="w-full text-xs bg-white/[0.05] hover:bg-white/[0.1] text-gray-300 border-0"
                    onClick={async () => {
                      setLoading(prev => ({ ...prev, cloning: true }));
                      try {
                        await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/projects/${selectedProject}/clone`, { method: 'POST' });
                        window.location.reload();
                      } catch (e) { }
                    }}
                  >
                    {loading.cloning ? 'Syncing Repository...' : 'Initialize Analysis'}
                  </Button>
                </div>
              </div>
            ) : (
              <div className="p-2 pb-10">
                {renderFileTree(getFileStructure())}
              </div>
            )}
          </ScrollArea>
        </aside>

        {/* Main Workspace */}
        <main className="flex-1 flex flex-col bg-[#0F1117] relative isolate">
          <BlueprintBackground />

          {!selectedProject || !selectedFile ? (
            <div className="flex-1 flex items-center justify-center flex-col z-10 px-8 max-w-3xl mx-auto">
              <div className="relative group cursor-default mb-8">
                <div className="absolute inset-0 bg-aurora-purple/20 blur-3xl rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-1000" />
                <LayoutTemplate className="w-24 h-24 text-white/[0.05] relative z-10" />
              </div>

              <h2 className="text-2xl font-bold text-white mb-3 font-mono tracking-tight">EXPLORER WORKSPACE</h2>
              <p className="text-sm text-gray-500 mb-8 text-center max-w-md">
                {!selectedProject
                  ? "Select a repository from the dropdown above to begin structural analysis."
                  : "Choose a file from the sidebar to view its intelligence report."}
              </p>

              {/* Feature Cards */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 w-full mt-4">
                <div className="p-4 rounded-xl bg-white/[0.02] border border-white/[0.05] hover:border-aurora-purple/30 transition-all">
                  <div className="flex items-center gap-2 mb-2">
                    <div className="w-6 h-6 rounded-md bg-aurora-purple/10 border border-aurora-purple/20 flex items-center justify-center">
                      <FileText className="w-3.5 h-3.5 text-aurora-purple" />
                    </div>
                    <h3 className="text-xs font-bold text-white uppercase tracking-wider">Documentation</h3>
                  </div>
                  <p className="text-[11px] text-gray-500 leading-relaxed">
                    Auto-generated docs with AST-powered structural analysis
                  </p>
                </div>

                <div className="p-4 rounded-xl bg-white/[0.02] border border-white/[0.05] hover:border-aurora-cyan/30 transition-all">
                  <div className="flex items-center gap-2 mb-2">
                    <div className="w-6 h-6 rounded-md bg-aurora-cyan/10 border border-aurora-cyan/20 flex items-center justify-center">
                      <Network className="w-3.5 h-3.5 text-aurora-cyan" />
                    </div>
                    <h3 className="text-xs font-bold text-white uppercase tracking-wider">Dependency Graph</h3>
                  </div>
                  <p className="text-[11px] text-gray-500 leading-relaxed">
                    Visual map of imports and module relationships
                  </p>
                </div>

                <div className="p-4 rounded-xl bg-white/[0.02] border border-white/[0.05] hover:border-aurora-purple/30 transition-all">
                  <div className="flex items-center gap-2 mb-2">
                    <div className="w-6 h-6 rounded-md bg-aurora-purple/10 border border-aurora-purple/20 flex items-center justify-center">
                      <Zap className="w-3.5 h-3.5 text-aurora-purple" />
                    </div>
                    <h3 className="text-xs font-bold text-white uppercase tracking-wider">AI Search</h3>
                  </div>
                  <p className="text-[11px] text-gray-500 leading-relaxed">
                    Press <kbd className="px-1.5 py-0.5 rounded bg-white/[0.05] border border-white/[0.1] text-[10px] font-mono">Cmd+K</kbd> to query architecture
                  </p>
                </div>
              </div>
            </div>
          ) : (
            <>
              {/* Workspace Tabs */}
              <div className="h-11 border-b border-aurora-border flex items-end px-4 gap-1 bg-[#0A0C10]/50 backdrop-blur-sm z-20">
                <button
                  onClick={() => { setShowCode(false); setShowSystemDoc(false); }}
                  className={cn(
                    "flex items-center gap-2 px-4 py-2 text-xs font-medium border-t border-l border-r rounded-t-lg transition-all relative top-[1px]",
                    !showCode && !showSystemDoc
                      ? "bg-[#0F1117] border-aurora-border text-aurora-cyan shadow-sm z-10"
                      : "border-transparent text-gray-500 hover:text-gray-300 hover:bg-white/[0.02]"
                  )}
                >
                  <FileText className="w-3.5 h-3.5" /> Documentation
                </button>
                <button
                  onClick={() => { setShowCode(true); setShowSystemDoc(false); }}
                  className={cn(
                    "flex items-center gap-2 px-4 py-2 text-xs font-medium border-t border-l border-r rounded-t-lg transition-all relative top-[1px]",
                    showCode
                      ? "bg-[#0F1117] border-aurora-border text-aurora-purple shadow-sm z-10"
                      : "border-transparent text-gray-500 hover:text-gray-300 hover:bg-white/[0.02]"
                  )}
                >
                  <Code2 className="w-3.5 h-3.5" /> Source Code
                </button>
                <button
                  onClick={() => fetchSystemDoc()}
                  className={cn(
                    "flex items-center gap-2 px-4 py-2 text-xs font-medium border-t border-l border-r rounded-t-lg transition-all relative top-[1px]",
                    showSystemDoc
                      ? "bg-[#0F1117] border-aurora-border text-aurora-pink shadow-sm z-10"
                      : "border-transparent text-gray-500 hover:text-gray-300 hover:bg-white/[0.02]"
                  )}
                >
                  <Database className="w-3.5 h-3.5" /> System Architecture
                </button>

                <div className="flex-1 border-b border-aurora-border" />
              </div>

              {/* Content Panel */}
              <div className="flex-1 overflow-y-auto p-8 lg:p-12 scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent">
                <div className="max-w-5xl mx-auto">
                  {loading.content ? (
                    <div className="space-y-6 animate-pulse p-4">
                      <div className="h-8 w-1/3 bg-white/[0.05] rounded-lg" />
                      <div className="space-y-3 pt-4">
                        <div className="h-4 w-full bg-white/[0.03] rounded" />
                        <div className="h-4 w-5/6 bg-white/[0.03] rounded" />
                        <div className="h-4 w-4/6 bg-white/[0.03] rounded" />
                      </div>
                    </div>
                  ) : showSystemDoc ? (
                    // --- System Doc View ---
                    <article className="prose prose-invert prose-p:text-gray-400 prose-headings:font-bold prose-pre:bg-[#0A0C10] prose-pre:border prose-pre:border-aurora-border max-w-none">
                      <div className="bg-gradient-to-br from-aurora-purple/10 to-transparent border border-aurora-purple/20 rounded-xl p-6 mb-8 flex items-center justify-between">
                        <div>
                          <h2 className="text-xl font-bold text-white mb-1 mt-0">Architecture Governance</h2>
                          <div className="flex gap-2 mt-2">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => setViewMode('doc')}
                              className={cn("h-7 px-3 text-[10px] rounded-md", viewMode === 'doc' ? "bg-aurora-purple text-white" : "text-gray-500")}
                            >
                              Documentation
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => { setViewMode('graph'); fetchGraph(); }}
                              className={cn("h-7 px-3 text-[10px] rounded-md", viewMode === 'graph' ? "bg-aurora-cyan text-black font-bold" : "text-gray-500")}
                            >
                              Structural Graph
                            </Button>
                          </div>
                        </div>
                        <Button variant="outline" size="sm" className="border-aurora-purple/30 bg-black/20 text-aurora-purple hover:bg-aurora-purple hover:text-white transition-all rounded-xl" onClick={() => window.open(`${process.env.NEXT_PUBLIC_API_BASE_URL}/docs/${selectedProject}/system/doc/download?repo_path=${encodeURIComponent(selectedProjectData?.repo_url.split('/').pop().replace('.git', '') === 'ArchIntel-Docs' ? '.' : `repos/${selectedProjectData?.repo_url.split('/').pop().replace('.git', '')}`)}`)}>
                          <Download className="w-4 h-4 mr-2" /> Export PDF
                        </Button>
                      </div>

                      {viewMode === 'doc' ? (
                        <div className="bg-[#0A0C10]/50 backdrop-blur-sm border border-aurora-border rounded-xl p-8 shadow-sm">
                          {systemDoc ? (
                            systemDoc.split('\n').map((line, i) => {
                              if (line.startsWith('# ')) return <h1 key={i} className="text-3xl mb-6 text-white pb-4 border-b border-white/[0.1]">{line.substring(2)}</h1>;
                              if (line.startsWith('## ')) return <h2 key={i} className="text-xl mt-10 mb-4 text-aurora-cyan font-mono flex items-center gap-2"><span className="text-gray-600">##</span> {line.substring(3)}</h2>;
                              if (line.startsWith('### ')) return <h3 key={i} className="text-lg font-semibold mt-8 mb-2 text-aurora-purple">{line.substring(4)}</h3>;
                              if (line.startsWith('- ')) return <li key={i} className="ml-4 text-gray-300 list-disc marker:text-gray-600 mb-2 pl-1">{line.substring(2)}</li>;
                              if (!line.trim()) return <div key={i} className="h-4" />;
                              return <p key={i} className="leading-7 mb-4">{line}</p>;
                            })
                          ) : (
                            <div className="text-center py-20 text-gray-500 italic">Analysis pending. Click system architecture to generate.</div>
                          )}
                        </div>
                      ) : (
                        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                          {graphData.nodes.length > 0 ? graphData.nodes.map(node => {
                            const outEdges = graphData.edges.filter(e => e.source === node.id);
                            const inEdges = graphData.edges.filter(e => e.target === node.id);
                            return (
                              <div key={node.id} className="aurora-card p-4 hover:border-aurora-purple/50 transition-all group relative overflow-hidden">
                                <div className="absolute top-0 right-0 p-2 opacity-10 group-hover:opacity-100 transition-opacity">
                                  <Network className="w-3 h-3 text-aurora-purple" />
                                </div>
                                <div className="flex flex-col gap-3">
                                  <div className="flex items-center gap-2">
                                    <div className="p-1.5 rounded-md bg-white/[0.03] border border-white/[0.05]">
                                      <File className="w-4 h-4 text-gray-400 group-hover:text-aurora-cyan" />
                                    </div>
                                    <span className="text-[11px] font-bold text-gray-300 truncate font-mono">{node.label}</span>
                                  </div>

                                  <div className="flex items-center gap-2">
                                    <div className="flex items-center gap-1 px-2 py-0.5 rounded-full bg-aurora-purple/10 border border-aurora-purple/20 text-[9px] text-aurora-purple">
                                      <ArrowUpRight className="w-2.5 h-2.5" />
                                      {outEdges.length} Deps
                                    </div>
                                    <div className="flex items-center gap-1 px-2 py-0.5 rounded-full bg-aurora-cyan/10 border border-aurora-cyan/20 text-[9px] text-aurora-cyan">
                                      <ArrowDownLeft className="w-2.5 h-2.5" />
                                      {inEdges.length} Reqs
                                    </div>
                                  </div>
                                </div>
                              </div>
                            );
                          }) : (
                            <div className="col-span-full py-20 text-center border border-dashed border-white/[0.05] rounded-3xl">
                              <Network className="w-10 h-10 text-gray-700 mx-auto mb-4 animate-pulse" />
                              <p className="text-gray-500 text-sm">Mapping structural dependencies...</p>
                            </div>
                          )}
                        </div>
                      )}
                    </article>
                  ) : showCode ? (
                    // --- Source Code View ---
                    <div className="rounded-xl border border-aurora-border bg-[#050608] shadow-2xl overflow-hidden">
                      <div className="px-4 py-2 border-b border-aurora-border bg-white/[0.02] flex justify-between items-center">
                        <span className="text-xs text-gray-500 font-mono">{selectedFile}</span>
                        <span className="text-[10px] text-gray-700 font-mono uppercase">Read-Only</span>
                      </div>
                      <div className="p-4 overflow-x-auto">
                        <pre className="font-mono text-[13px] leading-6 text-gray-300 tab-4">
                          {code?.split('\n').map((line, i) => (
                            <div key={i} className="table-row hover:bg-white/[0.02] transition-colors w-full block">
                              <span className="table-cell text-right pr-6 text-gray-700 select-none w-10 border-r border-white/[0.05] mr-4">{i + 1}</span>
                              <span className="table-cell pl-4">{line}</span>
                            </div>
                          ))}
                        </pre>
                      </div>
                    </div>
                  ) : (
                    // --- Documentation View ---
                    <article className="prose prose-invert prose-p:text-gray-300 prose-headings:font-bold prose-pre:bg-[#0A0C10] prose-pre:border prose-pre:border-aurora-border max-w-none">
                      {/* Header Card */}
                      <div className="mb-10 pb-6 border-b border-white/[0.1]">
                        <div className="flex items-center gap-3 mb-2 text-aurora-cyan">
                          <FileText className="w-5 h-5" />
                          <span className="text-xs font-mono uppercase tracking-widest font-bold">Generated Documentation</span>
                        </div>
                        <h1 className="text-4xl font-bold text-white mb-2">{selectedFile?.split('/').pop()}</h1>
                        <p className="text-gray-500 text-lg">Automated analysis of {selectedFile}</p>
                      </div>

                      {/* Markdown Content */}
                      <div className="space-y-3">
                        {docs?.split('\n').map((line, i) => {
                          // Skip title (handled in header)
                          if (line.startsWith('# ')) return null;

                          // Headers
                          if (line.startsWith('## ')) {
                            return <h2 key={i} className="text-2xl mt-12 mb-6 text-white font-semibold flex items-center gap-2">
                              <span className="w-1 h-6 bg-aurora-cyan rounded-full" />
                              {line.substring(3)}
                            </h2>;
                          }
                          if (line.startsWith('### ')) {
                            return <h3 key={i} className="text-lg font-bold mt-8 mb-3 text-aurora-purple">
                              {line.substring(4)}
                            </h3>;
                          }

                          // Bullet lists with *
                          if (line.trim().startsWith('* ')) {
                            const content = line.trim().substring(2);
                            // Handle bold text with **
                            const parts = content.split('**');
                            return (
                              <div key={i} className="flex gap-3 ml-4 mb-2 text-gray-300 items-start">
                                <div className="w-1.5 h-1.5 rounded-full bg-aurora-cyan mt-2 flex-shrink-0" />
                                <span className="leading-relaxed">
                                  {parts.map((part, idx) =>
                                    idx % 2 === 1 ? <strong key={idx} className="text-white font-semibold">{part}</strong> : part
                                  )}
                                </span>
                              </div>
                            );
                          }

                          // Bullet lists with + (nested)
                          if (line.trim().startsWith('+ ')) {
                            return (
                              <div key={i} className="flex gap-3 ml-8 mb-2 text-gray-400 items-start">
                                <div className="w-1 h-1 rounded-full bg-gray-600 mt-2 flex-shrink-0" />
                                <span className="leading-relaxed text-sm">{line.trim().substring(2)}</span>
                              </div>
                            );
                          }

                          // Bullet lists with -
                          if (line.trim().startsWith('- ')) {
                            return (
                              <div key={i} className="flex gap-3 ml-4 mb-2 text-gray-300 items-start">
                                <div className="w-1.5 h-1.5 rounded-full bg-gray-600 mt-2 flex-shrink-0" />
                                <span className="leading-relaxed">{line.trim().substring(2)}</span>
                              </div>
                            );
                          }

                          // Numbered lists
                          const numberedMatch = line.trim().match(/^(\d+)\.\s+(.+)/);
                          if (numberedMatch) {
                            return (
                              <div key={i} className="flex gap-3 ml-4 mb-2 text-gray-300 items-start">
                                <span className="text-aurora-purple font-bold text-sm w-6 flex-shrink-0">{numberedMatch[1]}.</span>
                                <span className="leading-relaxed">{numberedMatch[2]}</span>
                              </div>
                            );
                          }

                          // Code blocks
                          if (line.startsWith('```')) {
                            return <div key={i} className="my-4 p-4 rounded-lg bg-[#0A0C10] border border-white/[0.08] font-mono text-xs text-gray-400">Code Block</div>;
                          }

                          // Inline code and bold text in paragraphs
                          if (line.includes('`') || line.includes('**')) {
                            let processedLine = line;
                            const elements = [];
                            let lastIndex = 0;

                            // Simple parser for inline code and bold
                            const codeRegex = /`([^`]+)`/g;
                            const boldRegex = /\*\*([^*]+)\*\*/g;

                            // Replace inline code
                            processedLine = line.replace(codeRegex, (match, code) => `<code>${code}</code>`);
                            // Replace bold
                            processedLine = processedLine.replace(boldRegex, (match, bold) => `<strong>${bold}</strong>`);

                            return (
                              <p key={i} className="leading-7 mb-4 text-gray-300/90" dangerouslySetInnerHTML={{
                                __html: processedLine
                                  .replace(/<code>/g, '<code class="px-1.5 py-0.5 rounded bg-white/[0.05] border border-white/[0.1] text-aurora-cyan font-mono text-xs">')
                                  .replace(/<strong>/g, '<strong class="text-white font-semibold">')
                              }} />
                            );
                          }

                          // Empty lines
                          if (!line.trim()) return <div key={i} className="h-2" />;

                          // Regular paragraphs
                          return <p key={i} className="leading-7 mb-4 text-gray-300/90">{line}</p>;
                        })}
                      </div>
                    </article>
                  )}
                </div>
              </div>
            </>
          )}
        </main>
      </div>
      {/* Command Palette Modal */}
      <AnimatePresence>
        {showSearch && (
          <div className="fixed inset-0 z-[100] flex items-start justify-center pt-[15vh]">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setShowSearch(false)}
              className="absolute inset-0 bg-black/60 backdrop-blur-sm"
            />
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: -20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: -20 }}
              className="w-full max-w-2xl bg-[#0A0C10] border border-white/[0.1] rounded-2xl shadow-2xl overflow-hidden relative z-10"
            >
              <form onSubmit={handleQuery} className="p-6 border-b border-white/[0.05] space-y-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-aurora-purple/10 border border-aurora-purple/20">
                    <Zap className="w-5 h-5 text-aurora-purple animate-pulse" />
                  </div>
                  <input
                    autoFocus
                    placeholder="Ask architecture: 'Where is auth?' or 'List main APIs'..."
                    className="flex-1 bg-transparent border-none outline-none text-white placeholder:text-gray-600 font-medium text-lg"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                  />
                </div>
                <div className="flex items-center justify-between pl-11">
                  <div className="flex items-center gap-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-green-500 shadow-glow shadow-green-500/50" />
                    <span className="text-[9px] text-gray-500 font-mono uppercase tracking-widest">Oracle Node: MI-8X7B-V2-ACTIVE</span>
                  </div>
                  <span className="text-[10px] text-gray-600 font-mono bg-white/[0.03] px-2 py-1 rounded border border-white/[0.05]">COMMAND+ENTER TO SYNTHESIZE</span>
                </div>
              </form>

              <div className="max-h-[60vh] overflow-y-auto p-6 scrollbar-thin scrollbar-thumb-white/10">
                {isQuerying ? (
                  <div className="flex flex-col items-center justify-center py-10 text-gray-500 gap-4">
                    <RefreshCw className="w-8 h-8 animate-spin text-aurora-purple/50" />
                    <span className="text-xs font-mono animate-pulse">Consulting Architecture Node...</span>
                  </div>
                ) : queryResponse ? (
                  <div className="max-h-[50vh] overflow-y-auto">
                    <div className="flex items-center gap-2 mb-6 text-aurora-cyan uppercase text-[10px] font-bold tracking-widest font-mono">
                      <Activity className="w-3.5 h-3.5" />
                      <span>Technical Intelligence Report</span>
                    </div>
                    <div className="space-y-3">
                      {queryResponse.split('\n').map((line, i) => {
                        // Headers
                        if (line.startsWith('### ')) {
                          return <h4 key={i} className="text-base font-bold text-white mt-6 mb-3 flex items-center gap-2">
                            <div className="w-1 h-4 bg-aurora-purple rounded-full" />
                            {line.substring(4)}
                          </h4>;
                        }
                        if (line.startsWith('## ')) {
                          return <h3 key={i} className="text-lg font-bold text-aurora-cyan uppercase tracking-wide mt-8 mb-4 border-b border-white/[0.1] pb-2">
                            {line.substring(3)}
                          </h3>;
                        }
                        if (line.startsWith('# ')) {
                          return <h2 key={i} className="text-xl font-bold text-white mb-4">{line.substring(2)}</h2>;
                        }

                        // Lists with bullets (*)
                        if (line.trim().startsWith('* ')) {
                          const content = line.trim().substring(2);
                          // Check if it contains bold text with **
                          const parts = content.split('**');
                          return (
                            <div key={i} className="flex gap-3 text-sm text-gray-300 items-start ml-4 mb-2">
                              <div className="w-1.5 h-1.5 rounded-full bg-aurora-cyan mt-1.5 flex-shrink-0" />
                              <span className="leading-relaxed">
                                {parts.map((part, idx) =>
                                  idx % 2 === 1 ? <strong key={idx} className="text-white font-semibold">{part}</strong> : part
                                )}
                              </span>
                            </div>
                          );
                        }

                        // Lists with dashes (-)
                        if (line.trim().startsWith('- ')) {
                          return (
                            <div key={i} className="flex gap-3 text-sm text-gray-300 items-start ml-2 mb-2">
                              <div className="w-1 h-1 rounded-full bg-aurora-purple/50 mt-2 flex-shrink-0" />
                              <span className="leading-relaxed">{line.trim().substring(2)}</span>
                            </div>
                          );
                        }

                        // Numbered lists
                        const numberedMatch = line.trim().match(/^(\d+)\.\s+(.+)/);
                        if (numberedMatch) {
                          return (
                            <div key={i} className="flex gap-3 text-sm text-gray-300 items-start ml-2 mb-2">
                              <span className="text-aurora-purple font-bold text-xs w-5 flex-shrink-0">{numberedMatch[1]}.</span>
                              <span className="leading-relaxed">{numberedMatch[2]}</span>
                            </div>
                          );
                        }

                        // Code blocks (inline backticks)
                        if (line.includes('`') && !line.startsWith('```')) {
                          const parts = line.split('`');
                          return (
                            <p key={i} className="text-sm text-gray-400 leading-relaxed mb-2">
                              {parts.map((part, idx) =>
                                idx % 2 === 1
                                  ? <code key={idx} className="px-1.5 py-0.5 rounded bg-white/[0.05] border border-white/[0.1] text-aurora-cyan font-mono text-xs">{part}</code>
                                  : part
                              )}
                            </p>
                          );
                        }

                        // Empty lines
                        if (!line.trim()) return <div key={i} className="h-2" />;

                        // Regular paragraphs
                        return <p key={i} className="text-sm text-gray-400 leading-relaxed mb-2">{line}</p>;
                      })}
                    </div>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <span className="text-[10px] font-bold text-gray-500 uppercase tracking-widest">Suggested Queries</span>
                    <div className="grid grid-cols-2 gap-2">
                      {[
                        "What is the core purpose of this microservice?",
                        "Identify all external API integrations",
                        "Trace the data flow for user registration",
                        "Suggest architectural improvements"
                      ].map(s => (
                        <button
                          key={s}
                          onClick={() => { setQuery(s); }}
                          className="text-left px-4 py-3 rounded-xl bg-white/[0.02] border border-white/[0.05] text-xs text-gray-400 hover:text-white hover:border-aurora-purple/30 transition-all"
                        >
                          {s}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

    </div>
  );
}

