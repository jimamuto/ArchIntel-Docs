import React, { useState, useEffect, useRef } from 'react';
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
  ArrowDownLeft,
  Edit2,
  Save,
  Ban,
  Sparkles,
  Loader2
} from 'lucide-react';
import { cn } from '../lib/utils';
import { authenticatedFetch, logout, getSession } from '../lib/auth_utils';
import Link from 'next/link';
import { useToast } from '../lib/toast';
import Head from 'next/head';
import { motion, AnimatePresence } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import mermaid from 'mermaid';
import DOMPurify from 'dompurify';

// Initialize mermaid
if (typeof window !== 'undefined') {
  mermaid.initialize({
    startOnLoad: true,
    theme: 'dark',
    securityLevel: 'loose',
    fontFamily: 'Inter, sans-serif',
  });
}

// Enhanced chart validation function
const validateMermaidContent = (chartContent) => {
  if (!chartContent || typeof chartContent !== 'string') {
    throw new Error('Invalid chart content');
  }

  // Check for common XSS patterns
  const dangerousPatterns = [
    /<script[\s\S]*?>[\s\S]*?<\/script>/gi,
    /javascript:/gi,
    /data:\s*text\/javascript/gi,
    /on\w+\s*=/gi,
    /<iframe[\s\S]*?>[\s\S]*?<\/iframe>/gi,
    /<object[\s\S]*?>[\s\S]*?<\/object>/gi,
    /<embed[\s\S]*?>[\s\S]*?<\/embed>/gi,
    /<form[\s\S]*?>[\s\S]*?<\/form>/gi,
    /<input[\s\S]*?>/gi
  ];

  for (const pattern of dangerousPatterns) {
    if (pattern.test(chartContent)) {
      throw new Error('Potentially malicious content detected in chart');
    }
  }

  // Limit content size to prevent DoS
  if (chartContent.length > 50000) {
    throw new Error('Chart content too large');
  }

  // Validate Mermaid syntax (basic check)
  const mermaidKeywords = ['graph', 'flowchart', 'sequenceDiagram', 'classDiagram', 'stateDiagram', 'erDiagram', 'journey', 'gantt', 'pie', 'requirementDiagram'];
  const trimmed = chartContent.trim();
  const hasValidKeyword = mermaidKeywords.some(keyword => 
    trimmed.toLowerCase().startsWith(keyword.toLowerCase())
  );

  if (!hasValidKeyword && !trimmed.startsWith('%%')) {
    throw new Error('Invalid Mermaid syntax');
  }

  return true;
};

// Secure SVG rendering with sanitization
const sanitizeAndRenderSVG = (svgContent) => {
  try {
    // Configure DOMPurify for SVG content
    const config = {
      USE_PROFILES: { svg: true, svgFilters: true },
      ADD_ATTR: ['target'], // Allow safe attributes
      FORBID_ATTR: [
        'onerror', 'onload', 'onclick', 'onmouseover', 'onmouseout',
        'onfocus', 'onblur', 'onkeydown', 'onkeyup', 'onkeypress'
      ], // Explicitly forbid dangerous attributes
      ADD_TAGS: ['foreignobject'], // Allow SVG foreignObject if needed
    };
    
    // Sanitize the SVG content
    const cleanSVG = DOMPurify.sanitize(svgContent, config);
    
    // Additional validation for SVG structure
    if (!cleanSVG.includes('<svg') || !cleanSVG.includes('</svg>')) {
      throw new Error('Invalid SVG structure');
    }
    
    return cleanSVG;
  } catch (error) {
    console.error('SVG sanitization failed:', error);
    throw new Error('Failed to sanitize SVG content');
  }
};

// Secure error handling function
const handleMermaidError = (error) => {
  console.error('Mermaid rendering error:', error);
  
  // Don't expose detailed error information to users
  if (error?.message?.includes('malicious') || 
      error?.message?.includes('script') || 
      error?.message?.includes('XSS')) {
    return 'Failed to render diagram: Invalid content detected';
  }
  
  if (error?.message?.includes('syntax') || 
      error?.message?.includes('parse')) {
    return 'Failed to render diagram: Please check the syntax';
  }
  
  return 'Failed to render diagram: Please try again';
};

// --- Mermaid Component ---
const Mermaid = ({ chart }) => {
  const ref = useRef(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (ref.current && chart) {
      setError(null);
      ref.current.removeAttribute('data-processed');

      // Pre-process chart to remove potential LLM mess-ups
      let cleanedChart = String(chart).trim();

      // Remove markdown code fences if they were accidentally included by LLM or parser
      cleanedChart = cleanedChart.replace(/^```mermaid\n?/, '').replace(/\n?```$/, '');

      // Fix common LLM arrow syntax errors: -->|label|> should be -->|"label"|
      // This regex matches patterns like -->|text|> and converts to -->|"text"|
      cleanedChart = cleanedChart.replace(/-->\|([^|]+)\|>/g, '-->|"$1"|');

      // Also fix the variant without the initial arrow: --|text|>
      cleanedChart = cleanedChart.replace(/--\|([^|]+)\|>/g, '--|"$1"|');

      // Validate content before processing
      try {
        validateMermaidContent(cleanedChart);
      } catch (validationError) {
        setError(validationError.message);
        return;
      }

      // Ensure the chart starts with a valid Mermaid keyword (ignoring comments)
      const validKeywords = ['graph', 'flowchart', 'sequenceDiagram', 'classDiagram', 'stateDiagram', 'erDiagram', 'journey', 'gantt', 'pie', 'requirementDiagram'];
      const lines = cleanedChart.split('\n');
      const firstLine = lines[0].trim();
      const hasKeyword = validKeywords.some(keyword => firstLine.toLowerCase().startsWith(keyword.toLowerCase()));

      if (!hasKeyword && !firstLine.startsWith('%%')) {
        // If no keyword, try to fix it if it looks like a flowchart
        if (cleanedChart.includes('-->')) {
          cleanedChart = 'graph TD\n' + cleanedChart;
        }
      }

      console.log('Rendering Mermaid chart:', cleanedChart);

      const uniqueId = `mermaid-${Math.random().toString(36).substr(2, 9)}`;

      try {
        mermaid.render(uniqueId, cleanedChart)
          .then(({ svg }) => {
            if (ref.current) {
              const sanitizedSVG = sanitizeAndRenderSVG(svg);
              ref.current.innerHTML = sanitizedSVG;
            }
          })
          .catch((err) => {
            console.error('Mermaid async error:', err);
            setError(handleMermaidError(err));
          });
      } catch (err) {
        console.error('Mermaid sync error:', err);
        setError(handleMermaidError(err));
      }
    }
  }, [chart]);

  if (error) {
    return (
      <div className="my-6 p-6 rounded-xl border border-red-500/20 bg-red-500/5 text-center">
        <p className="text-sm text-red-400 font-medium mb-1">Visual Generation Error</p>
        <p className="text-xs text-red-400/70 font-mono">{handleMermaidError(new Error(error))}</p>
        <details className="mt-3 text-left">
          <summary className="text-[10px] text-gray-500 cursor-pointer hover:text-gray-400 underline uppercase tracking-widest">Show Source Code</summary>
          <pre className="mt-2 p-3 bg-black/40 rounded text-[10px] text-gray-400 overflow-x-auto border border-white/5">
            {chart}
          </pre>
        </details>
      </div>
    );
  }

  return <div ref={ref} className="mermaid flex justify-center py-6 bg-black/20 rounded-xl my-6 border border-white/5" />;
};

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

// --- Progress Loader Component ---
const ProgressLoader = ({ message, percent }) => (
  <div className="flex flex-col items-center justify-center py-20 animate-in fade-in duration-500">
    <div className="w-full max-w-sm space-y-6">
      <div className="flex justify-between items-end">
        <span className="text-sm font-medium text-aurora-cyan animate-pulse">
          {message || 'Processing...'}
        </span>
        <span className="text-xs font-mono text-gray-500">{percent}%</span>
      </div>

      <div className="h-1.5 w-full bg-white/[0.05] rounded-full overflow-hidden border border-white/[0.05]">
        <div
          className="h-full bg-gradient-to-r from-aurora-purple via-aurora-cyan to-aurora-purple bg-[length:200%_100%] animate-[shimmer_2s_infinite]"
          style={{ width: `${percent}%`, transition: 'width 0.5s ease-out' }}
        />
      </div>

      <div className="flex justify-center gap-1.5 pt-2">
        {[...Array(3)].map((_, i) => (
          <div
            key={i}
            className="w-1 h-1 rounded-full bg-aurora-purple/50 animate-bounce"
            style={{ animationDelay: `${i * 0.15}s` }}
          />
        ))}
      </div>
    </div>
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
  const [loadingProgress, setLoadingProgress] = useState({ message: '', percent: 0 });
  const { success: showToast, error: showError } = useToast();
  const [error, setError] = useState(null);
  const [showCode, setShowCode] = useState(false);

  const [expandedFolders, setExpandedFolders] = useState(new Set());
  const [isEditing, setIsEditing] = useState(false);
  const [fileSearchQuery, setFileSearchQuery] = useState('');
  const [editContent, setEditContent] = useState('');


  // History Tab State
  const [showHistory, setShowHistory] = useState(false);
  const [historyFilter, setHistoryFilter] = useState({ author: '', dateFrom: '', dateTo: '' });
  const [expandedCommits, setExpandedCommits] = useState(new Set());
  const [commits, setCommits] = useState([]);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [authorStats, setAuthorStats] = useState([]);
  const [commitDiffs, setCommitDiffs] = useState({}); // { commitHash: diffText }
  const [loadingDiff, setLoadingDiff] = useState(null); // commitHash

  // Rationale Tab State
  const [showRationale, setShowRationale] = useState(false);
  const [rationaleData, setRationaleData] = useState({ rationale: '', discussions_count: 0 });
  const [discussions, setDiscussions] = useState([]);
  const [loadingRationale, setLoadingRationale] = useState(false);
  const [isIngesting, setIsIngesting] = useState(false);

  // Fetch Git history when History tab is opened
  useEffect(() => {
    if (showHistory && selectedFile && selectedProjectData) {
      fetchFileHistory();
      fetchAuthorStats();
    }
  }, [showHistory, selectedFile]);

  const fetchFileHistory = async () => {
    if (!selectedFile || !selectedProjectData) return;

    setLoadingHistory(true);
    try {
      const repoName = selectedProjectData.repo_url.split('/').pop().replace('.git', '');
      let repoPath = repoName === 'ArchIntel-Docs' ? '.' : `repos/${repoName}`;
      const url = `${process.env.NEXT_PUBLIC_API_BASE_URL}/docs/${selectedProject}/history/${selectedFile}?repo_path=${encodeURIComponent(repoPath)}`;

      const response = await authenticatedFetch(url);
      if (response.ok) {
        const data = await response.json();
        setCommits(data.commits || []);
      }
    } catch (error) {
      console.error('Error fetching file history:', error);
    } finally {
      setLoadingHistory(false);
    }
  };

  const fetchAuthorStats = async () => {
    if (!selectedFile || !selectedProjectData) return;
    try {
      const repoName = selectedProjectData.repo_url.split('/').pop().replace('.git', '');
      let repoPath = repoName === 'ArchIntel-Docs' ? '.' : `repos/${repoName}`;
      const url = `${process.env.NEXT_PUBLIC_API_BASE_URL}/docs/${selectedProject}/history/stats?path=${encodeURIComponent(selectedFile)}&repo_path=${encodeURIComponent(repoPath)}`;
      const response = await authenticatedFetch(url);
      if (response.ok) {
        const data = await response.json();
        setAuthorStats(data.stats || []);
      }
    } catch (error) {
      console.error('Error fetching author stats:', error);
    }
  };

  const fetchCommitDiff = async (commitHash) => {
    if (commitDiffs[commitHash] || !selectedProjectData) return;

    setLoadingDiff(commitHash);
    try {
      const repoName = selectedProjectData.repo_url.split('/').pop().replace('.git', '');
      let repoPath = repoName === 'ArchIntel-Docs' ? '.' : `repos/${repoName}`;
      const url = `${process.env.NEXT_PUBLIC_API_BASE_URL}/docs/${selectedProject}/history/diff?commit_hash=${commitHash}&file_path=${encodeURIComponent(selectedFile)}&repo_path=${encodeURIComponent(repoPath)}`;
      const response = await authenticatedFetch(url);
      if (response.ok) {
        const data = await response.json();
        setCommitDiffs(prev => ({ ...prev, [commitHash]: data.diff }));
      }
    } catch (error) {
      console.error('Error fetching commit diff:', error);
    } finally {
      setLoadingDiff(null);
    }
  };

  // Fetch Rationale & Discussions
  useEffect(() => {
    if (showRationale && selectedProject) {
      fetchRationale();
      fetchDiscussions();
    }
  }, [showRationale, selectedProject]);

  const fetchRationale = async () => {
    if (!selectedProject) return;
    setLoadingRationale(true);
    try {
      const response = await authenticatedFetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/context/${selectedProject}/rationale`);
      if (response.ok) {
        const data = await response.json();
        setRationaleData(data);
      }
    } catch (error) {
      console.error('Error fetching rationale:', error);
    } finally {
      setLoadingRationale(false);
    }
  };

  const fetchDiscussions = async () => {
    if (!selectedProject) return;
    try {
      const response = await authenticatedFetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/context/${selectedProject}/discussions`);
      if (response.ok) {
        const data = await response.json();
        setDiscussions(data.discussions || []);
      }
    } catch (error) {
      console.error('Error fetching discussions:', error);
    }
  };

  const handleIngestDiscussions = async () => {
    if (!selectedProject || isIngesting) return;
    setIsIngesting(true);
    try {
      showToast("Ingesting discussions from GitHub...");
      const response = await authenticatedFetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/context/${selectedProject}/ingest/discussions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ limit: 30 })
      });
      if (response.ok) {
        const data = await response.json();
        showToast(data.message);
        fetchRationale();
        fetchDiscussions();
      } else {
        showError("Failed to ingest discussions.");
      }
    } catch (error) {
      showError("Error connecting to server.");
    } finally {
      setIsIngesting(false);
    }
  };


  // MVP Features State
  const [showSearch, setShowSearch] = useState(false);
  const [query, setQuery] = useState('');
  const [queryResponse, setQueryResponse] = useState('');
  const [isQuerying, setIsQuerying] = useState(false);
  const [graphData, setGraphData] = useState({ nodes: [], edges: [] });
  const [searchResults, setSearchResults] = useState({ files: [], documentation: [] });
  const [viewMode, setViewMode] = useState('doc'); // 'doc' or 'graph'
  const [sidebarWidth, setSidebarWidth] = useState(288);
  const [isResizing, setIsResizing] = useState(false);

  // Initialize sidebar width from localStorage
  useEffect(() => {
    const savedWidth = localStorage.getItem('archintel_sidebar_width');
    if (savedWidth) {
      setSidebarWidth(parseInt(savedWidth, 10));
    }
  }, []);

  const handleMouseDown = (e) => {
    e.preventDefault();
    setIsResizing(true);
  };

  useEffect(() => {
    const handleMouseMove = (e) => {
      if (!isResizing) return;
      const newWidth = Math.max(200, Math.min(600, e.clientX));
      setSidebarWidth(newWidth);
    };

    const handleMouseUp = () => {
      if (isResizing) {
        setIsResizing(false);
        localStorage.setItem('archintel_sidebar_width', sidebarWidth.toString());
      }
    };

    if (isResizing) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
    }

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isResizing, sidebarWidth]);

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
    setSearchResults({ files: [], documentation: [] });

    try {
      // 1. Perform Neural Query (AI)
      const repoName = selectedProjectData.repo_url.split('/').pop().replace('.git', '');
      let repoPath = repoName === 'ArchIntel-Docs' ? '.' : `repos/${repoName}`;

      const aiPromise = authenticatedFetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/docs/${selectedProject}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, repo_path: repoPath })
      }).then(res => res.json());

      // 2. Perform Keyword Search
      const searchPromise = authenticatedFetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/docs/${selectedProject}/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
      }).then(res => res.json());

      const [aiData, searchData] = await Promise.all([aiPromise, searchPromise]);

      setQueryResponse(aiData.response);
      setSearchResults(searchData);
    } catch (err) {
      console.error("Search error:", err);
      setQueryResponse('Error connecting to intelligence nodes.');
    } finally {
      setIsQuerying(false);
    }
  }

  async function generateDiagram(type) {
    if (!selectedFile || !selectedProject) return;
    setLoading(prev => ({ ...prev, content: true }));
    try {
      const repoName = selectedProjectData.repo_url.split('/').pop().replace('.git', '');
      let repoPath = repoName === 'ArchIntel-Docs' ? '.' : `repos/${repoName}`;

      const res = await authenticatedFetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/docs/${selectedProject}/file/diagram?type=${type}&path=${encodeURIComponent(selectedFile)}&repo_path=${encodeURIComponent(repoPath)}`
      );
      const diagram = await res.text();

      if (diagram.startsWith('Error')) {
        showError(diagram);
        return;
      }

      // Append the diagram to the current docs
      const newDocs = `${docs}\n\n## AI Visual: ${type.charAt(0).toUpperCase() + type.slice(1)}\n${diagram}`;
      setDocs(newDocs);
      setEditContent(newDocs); // Keep edit content in sync
      showToast(`${type.charAt(0).toUpperCase() + type.slice(1)} diagram added!`);
    } catch (err) {
      showError('Failed to generate diagram');
    } finally {
      setLoading(prev => ({ ...prev, content: false }));
    }
  }

  async function fetchGraph() {
    if (!selectedProject || !selectedProjectData) return;
    if (graphData.nodes.length > 0) return;

    try {
      const repoName = selectedProjectData.repo_url.split('/').pop().replace('.git', '');
      let repoPath = repoName === 'ArchIntel-Docs' ? '.' : `repos/${repoName}`;
      const res = await authenticatedFetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/docs/${selectedProject}/graph?repo_path=${encodeURIComponent(repoPath)}`);
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

      const res = await authenticatedFetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/docs/${selectedProject}/system/doc?repo_path=${encodeURIComponent(repoPath)}`);
      const text = await res.text();
      setSystemDoc(text);
    } catch (err) {
      console.error(err);
      setSystemDoc('# Error\nFailed to load system documentation.');
    } finally {
      setLoading(prev => ({ ...prev, content: false }));
    }
  }

  async function handleSave() {
    if (!selectedProject || !selectedFile) return;

    setLoading(prev => ({ ...prev, content: true }));
    try {
      const res = await authenticatedFetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/docs/${selectedProject}/file/doc`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: selectedFile, content: editContent })
      });

      if (res.ok) {
        showToast("Documentation saved successfully.");
        setDocs(editContent);
        setIsEditing(false);
      } else {
        showError("Failed to save documentation.");
      }
    } catch (err) {
      showError("Error saving documentation.");
    } finally {
      setLoading(prev => ({ ...prev, content: false }));
    }
  }

  // Authentication and Project Fetching
  useEffect(() => {
    async function checkAuthAndFetch() {
      const session = await getSession();
      if (!session) {
        router.push('/login');
        return;
      }

      try {
        setLoading(prev => ({ ...prev, projects: true }));
        const res = await authenticatedFetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/projects`);
        const data = await res.json();
        const projectsList = data.projects || [];
        setProjects(projectsList);
        setError(null);

        // Selection Logic
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
      checkAuthAndFetch();
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
        const structureRes = await authenticatedFetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/projects/${selectedProject}/structure`);
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
    if (!selectedProject || !selectedFile || !selectedProjectData) return;

    async function fetchFileContent() {
      // Find if selected path is a folder in the tree
      const tree = getFileStructure();
      const parts = selectedFile.split('/');
      let current = tree;
      let isFolder = false;
      for (let i = 0; i < parts.length; i++) {
        if (current[parts[i]]) {
          if (i === parts.length - 1) {
            isFolder = current[parts[i]].isFolder;
          }
          current = current[parts[i]].children;
        }
      }

      if (isFolder) {
        setDocs(null);
        setCode(null);
        setLoading(prev => ({ ...prev, content: false }));
        return;
      }

      setLoading(prev => ({ ...prev, content: true }));
      setLoadingProgress({ message: 'Initializing analysis...', percent: 10 });
      setError(null);

      try {
        const repoName = selectedProjectData.repo_url.split('/').pop().replace('.git', '');
        let repoPath = repoName === 'ArchIntel-Docs' ? '.' : `repos/${repoName}`;

        setLoadingProgress({ message: 'Generating architectural documentation...', percent: 40 });
        const docRes = await authenticatedFetch(
          `${process.env.NEXT_PUBLIC_API_BASE_URL}/docs/${selectedProject}/file/doc?path=${encodeURIComponent(selectedFile)}&repo_path=${encodeURIComponent(repoPath)}`
        );
        const docText = docRes.ok ? await docRes.text() : '// Documentation generation in progress...';
        setDocs(docText);
        setEditContent(docText);
        setIsEditing(false);

        setLoadingProgress({ message: 'Fetching source code...', percent: 80 });
        const codeRes = await authenticatedFetch(
          `${process.env.NEXT_PUBLIC_API_BASE_URL}/projects/${selectedProject}/file/code?path=${encodeURIComponent(selectedFile)}&repo_path=${encodeURIComponent(repoPath)}`
        );
        const codeText = codeRes.ok ? await codeRes.text() : '// Could not fetch source code';
        setCode(codeText);

        setLoadingProgress({ message: 'Finalizing...', percent: 100 });
      } catch (err) {
        setError('Failed to load file content');
      } finally {
        setTimeout(() => {
          setLoading(prev => ({ ...prev, content: false }));
          setLoadingProgress({ message: '', percent: 0 });
        }, 500); // Small delay to show 100% completion
      }
    }

    fetchFileContent();
  }, [selectedProject, selectedFile]);

  const isSelectedPathFolder = () => {
    if (!selectedFile) return false;
    const tree = getFileStructure();
    const parts = selectedFile.split('/');
    let current = tree;
    for (let i = 0; i < parts.length; i++) {
      if (current[parts[i]]) {
        if (i === parts.length - 1) return current[parts[i]].isFolder;
        current = current[parts[i]].children;
      }
    }
    return false;
  };

  const getFolderContents = (path) => {
    if (!path) return [];
    const tree = getFileStructure();
    const parts = path.split('/');
    let current = tree;
    for (const part of parts) {
      if (current[part]) {
        current = current[part].children;
      } else {
        return [];
      }
    }
    return Object.entries(current).map(([name, data]) => ({
      name,
      ...data
    }));
  };

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
    const query = fileSearchQuery.toLowerCase();

    // Filter structure based on query
    const filteredStructure = query
      ? structure.filter(f => f.path.toLowerCase().includes(query))
      : structure;

    filteredStructure.forEach(file => {
      // Split by either forward slash or backslash for cross-platform robustness
      const parts = file.path.split(/[/\\]/);
      let current = tree;
      parts.forEach((part, index) => {
        if (!current[part]) {
          current[part] = {
            isFolder: index < parts.length - 1,
            children: {},
            fullPath: parts.slice(0, index + 1).join('/')
          };
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
        // Automatically expand if we're searching
        const isExpanded = expandedFolders.has(currentPath) || (fileSearchQuery && Object.keys(data.children).length > 0);
        const isFolderSelected = selectedFile === currentPath;

        return (
          <div key={currentPath} className="select-none">
            <div className={cn(
              "w-full flex items-center gap-1.5 px-3 py-1.5 text-[13px] transition-colors rounded-sm group",
              isFolderSelected ? "bg-aurora-purple/10 text-aurora-purple" : (isExpanded ? "text-white" : "text-gray-400 hover:text-gray-200 hover:bg-white/[0.04]")
            )}>
              <button
                onClick={(e) => { e.stopPropagation(); toggleFolder(currentPath); }}
                className="text-gray-600 hover:text-gray-400 p-0.5 rounded transition-colors"
                title={isExpanded ? "Collapse" : "Expand"}
              >
                {isExpanded ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
              </button>
              <button
                onClick={() => setSelectedFile(currentPath)}
                className="flex items-center gap-1.5 flex-1 truncate text-left"
              >
                <FolderTree className={cn("w-3.5 h-3.5 transition-colors", isExpanded || isFolderSelected ? "text-aurora-purple" : "text-gray-500 group-hover:text-aurora-purple/70")} />
                <span className="truncate font-medium">{name}</span>
              </button>
            </div>
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
                ? "bg-aurora-cyan/10 text-aurora-cyan border-aurora-cyan"
                : "border-transparent text-gray-500 hover:text-gray-300 hover:bg-white/[0.02]"
            )}
          >
            <FileText className="w-3.5 h-3.5 opacity-70" />
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
        <aside
          className="bg-[#0A0C10] border-r border-aurora-border flex flex-col relative z-10"
          style={{ width: `${sidebarWidth}px` }}
        >
          <div className="py-2 px-4 shadow-[0_1px_0_0_rgba(255,255,255,0.02)]">
            <span className="text-[10px] font-bold uppercase tracking-wider text-gray-500 font-mono">Project Files</span>
          </div>

          {/* File Search */}
          {selectedProject && structure.length > 0 && (
            <div className="px-3 py-2 border-b border-white/[0.05]">
              <div className="relative">
                <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-gray-500" />
                <input
                  type="text"
                  placeholder="Search files..."
                  value={fileSearchQuery}
                  onChange={(e) => setFileSearchQuery(e.target.value)}
                  className="w-full pl-8 pr-3 py-1.5 text-xs bg-[#15171B] border border-white/[0.08] rounded-lg text-gray-300 placeholder:text-gray-600 focus:outline-none focus:border-aurora-cyan/50 focus:ring-1 focus:ring-aurora-cyan/20"
                />
                {fileSearchQuery && (
                  <button
                    onClick={() => setFileSearchQuery('')}
                    className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300"
                  >
                    <X className="w-3 h-3" />
                  </button>
                )}
              </div>
            </div>
          )}

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

        {/* Resize Handle */}
        <div
          onMouseDown={handleMouseDown}
          className={cn(
            "w-1 bg-[#1A1D23] hover:bg-aurora-purple/50 cursor-col-resize transition-colors z-20 relative",
            isResizing && "bg-aurora-purple shadow-[0_0_10px_rgba(168,85,247,0.5)]"
          )}
        />

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
                  onClick={() => { setShowCode(false); setShowSystemDoc(false); setShowHistory(false); setIsEditing(false); }}
                  className={cn(
                    "flex items-center gap-2 px-4 py-2 text-xs font-medium border-t border-l border-r rounded-t-lg transition-all relative top-[1px]",
                    !showCode && !showSystemDoc && !showHistory
                      ? "bg-[#0F1117] border-aurora-border text-aurora-cyan shadow-sm z-10"
                      : "border-transparent text-gray-500 hover:text-gray-300 hover:bg-white/[0.02]"
                  )}
                >
                  <FileText className="w-3.5 h-3.5" /> Documentation
                </button>
                <button
                  onClick={() => { setShowCode(true); setShowSystemDoc(false); setShowHistory(false); }}
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
                  onClick={() => { setShowHistory(true); setShowCode(false); setShowSystemDoc(false); }}
                  className={cn(
                    "flex items-center gap-2 px-4 py-2 text-xs font-medium border-t border-l border-r rounded-t-lg transition-all relative top-[1px]",
                    showHistory
                      ? "bg-[#0F1117] border-aurora-border text-green-400 shadow-sm z-10"
                      : "border-transparent text-gray-500 hover:text-gray-300 hover:bg-white/[0.02]"
                  )}
                >
                  <Activity className="w-3.5 h-3.5" /> History
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
                <button
                  onClick={() => { setShowRationale(true); setShowHistory(false); setShowCode(false); setShowSystemDoc(false); }}
                  className={cn(
                    "flex items-center gap-2 px-4 py-2 text-xs font-medium border-t border-l border-r rounded-t-lg transition-all relative top-[1px]",
                    showRationale
                      ? "bg-[#0F1117] border-aurora-border text-aurora-cyan shadow-sm z-10"
                      : "border-transparent text-gray-500 hover:text-gray-300 hover:bg-white/[0.02]"
                  )}
                >
                  <Sparkles className="w-3.5 h-3.5" /> Rationale
                </button>

                <div className="flex-1 border-b border-aurora-border" />

                {selectedFile && selectedProjectData && (
                  <div className="pb-2 pr-4">
                    <a
                      href={`${selectedProjectData.repo_url.replace('.git', '')}/${isSelectedPathFolder() ? 'tree' : 'blob'}/main/${selectedFile}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-1.5 px-3 py-1 rounded-md bg-white/[0.03] border border-white/[0.08] text-[10px] font-mono text-gray-400 hover:text-white hover:bg-white/[0.08] transition-all"
                    >
                      <Share2 className="w-3 h-3" />
                      View on GitHub
                    </a>
                  </div>
                )}
              </div>

              {/* Breadcrumbs */}
              <div className="px-8 lg:px-12 pt-6 flex items-center gap-2 text-[11px] font-mono text-gray-500">
                <button
                  onClick={() => setSelectedFile(null)}
                  className="hover:text-aurora-cyan transition-colors"
                >
                  <Database className="w-3 h-3 inline mr-1" />
                  {selectedProjectData?.name}
                </button>
                {selectedFile?.split('/').map((part, i, arr) => (
                  <React.Fragment key={i}>
                    <ChevronRight className="w-3 h-3 text-gray-700" />
                    <button
                      onClick={() => setSelectedFile(arr.slice(0, i + 1).join('/'))}
                      className={cn(
                        "hover:text-white transition-colors",
                        i === arr.length - 1 && "text-gray-300 font-bold"
                      )}
                    >
                      {part}
                    </button>
                  </React.Fragment>
                ))}
              </div>

              {/* Content Panel */}
              <div className="flex-1 overflow-y-auto p-8 lg:p-12 scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent">
                <div className="max-w-5xl mx-auto">
                  {isSelectedPathFolder() ? (
                    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
                      <div>
                        <h1 className="text-3xl font-bold text-white mb-2 flex items-center gap-3">
                          <FolderTree className="w-8 h-8 text-aurora-purple" />
                          {selectedFile.split('/').pop()}
                        </h1>
                        <p className="text-gray-500 font-mono text-xs">{selectedFile}</p>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {getFolderContents(selectedFile).map((item, i) => (
                          <button
                            key={i}
                            onClick={() => {
                              setSelectedFile(item.fullPath);
                              if (item.isFolder) toggleFolder(item.fullPath);
                            }}
                            className="p-4 rounded-xl bg-white/[0.02] border border-white/[0.05] hover:border-aurora-purple/30 hover:bg-white/[0.04] transition-all text-left flex items-center gap-4 group"
                          >
                            <div className={cn(
                              "w-10 h-10 rounded-lg flex items-center justify-center transition-colors",
                              item.isFolder ? "bg-aurora-purple/10 text-aurora-purple group-hover:bg-aurora-purple/20" : "bg-aurora-cyan/10 text-aurora-cyan group-hover:bg-aurora-cyan/20"
                            )}>
                              {item.isFolder ? <FolderTree className="w-5 h-5" /> : <FileText className="w-5 h-5" />}
                            </div>
                            <div className="truncate">
                              <p className="text-sm font-bold text-gray-200 truncate">{item.name}</p>
                              <p className="text-[10px] text-gray-500 font-mono italic">
                                {item.isFolder ? 'Directory' : 'Source File'}
                              </p>
                            </div>
                          </button>
                        ))}
                      </div>
                    </div>
                  ) : loading.content ? (
                    <ProgressLoader message={loadingProgress.message} percent={loadingProgress.percent} />
                  ) : showRationale ? (
                    // --- Rationale View ---
                    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
                      <div className="bg-gradient-to-br from-aurora-cyan/10 to-transparent border border-aurora-cyan/20 rounded-2xl p-8 relative overflow-hidden group">
                        <div className="absolute top-0 right-0 p-8 opacity-5 group-hover:opacity-10 transition-opacity">
                          <Sparkles className="w-32 h-32 text-aurora-cyan" />
                        </div>
                        <div className="relative z-10">
                          <div className="flex items-center justify-between mb-4">
                            <div className="flex items-center gap-3">
                              <div className="p-2 rounded-xl bg-aurora-cyan/10 border border-aurora-cyan/20">
                                <Sparkles className="w-6 h-6 text-aurora-cyan" />
                              </div>
                              <h1 className="text-3xl font-bold text-white">Project Rationale</h1>
                            </div>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={handleIngestDiscussions}
                              disabled={isIngesting}
                              className="border-aurora-cyan/30 bg-black/20 text-aurora-cyan hover:bg-aurora-cyan hover:text-black transition-all rounded-xl font-bold"
                            >
                              {isIngesting ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <RefreshCw className="w-4 h-4 mr-2" />}
                              Sync GitHub Context
                            </Button>
                          </div>
                          <p className="text-gray-400 max-w-2xl leading-relaxed">
                            AI-synthesized design rationale and trade-offs derived from Pull Requests, Issues, and architectural discussions.
                          </p>
                        </div>
                      </div>

                      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                        {/* Left: AI Rationale */}
                        <div className="lg:col-span-2 space-y-6">
                          <div className="aurora-card p-8 min-h-[400px]">
                            {loadingRationale ? (
                              <div className="flex flex-col items-center justify-center h-[300px] text-gray-500">
                                <Loader2 className="w-10 h-10 animate-spin text-aurora-cyan/50 mb-4" />
                                <p className="font-mono text-sm animate-pulse">Synthesizing Architectural Rationale...</p>
                              </div>
                            ) : (
                              <div className="prose prose-invert prose-p:text-gray-300 prose-headings:font-bold prose-pre:bg-[#0A0C10] max-w-none">
                                <ReactMarkdown
                                  components={{
                                    h1: ({ node, ...props }) => <h1 className="text-2xl font-bold text-white mb-6 border-b border-white/[0.1] pb-4" {...props} />,
                                    h2: ({ node, ...props }) => <h2 className="text-xl mt-8 mb-4 text-aurora-cyan font-mono" {...props} />,
                                    h3: ({ node, ...props }) => <h3 className="text-lg font-bold mt-6 mb-2 text-aurora-purple" {...props} />,
                                    p: ({ node, ...props }) => <p className="leading-relaxed mb-4 text-gray-300/90" {...props} />,
                                    ul: ({ node, ...props }) => <ul className="list-disc ml-6 space-y-2 mb-4 text-gray-300" {...props} />,
                                    li: ({ node, ...props }) => <li className="leading-relaxed" {...props} />,
                                    strong: ({ node, ...props }) => <strong className="text-white font-bold" {...props} />,
                                  }}
                                >
                                  {rationaleData.rationale || "# No Rationale Available\n\nIngest GitHub discussions to generate an AI synthesis of the project's design decisions."}
                                </ReactMarkdown>
                              </div>
                            )}
                          </div>
                        </div>

                        {/* Right: Raw Discussions */}
                        <div className="space-y-4">
                          <h3 className="text-xs font-bold text-gray-500 uppercase tracking-widest px-1">Source Context ({discussions.length})</h3>
                          <ScrollArea className="h-[600px] pr-4">
                            <div className="space-y-3">
                              {discussions.length === 0 ? (
                                <div className="p-8 text-center border border-dashed border-white/[0.05] rounded-2xl text-gray-600 italic text-xs">
                                  No discussions ingested yet.
                                </div>
                              ) : (
                                discussions.map((disc, i) => (
                                  <a
                                    key={i}
                                    href={disc.url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="block p-4 rounded-xl bg-white/[0.02] border border-white/[0.05] hover:border-aurora-cyan/30 hover:bg-white/[0.04] transition-all group"
                                  >
                                    <div className="flex items-start gap-3">
                                      {disc.source === 'github_pr' ? (
                                        <GitPullRequest className="w-4 h-4 text-aurora-purple mt-0.5" />
                                      ) : (
                                        <MessageSquare className="w-4 h-4 text-aurora-cyan mt-0.5" />
                                      )}
                                      <div className="flex-1 min-w-0">
                                        <p className="text-xs font-bold text-gray-200 line-clamp-2 group-hover:text-white transition-colors">{disc.title}</p>
                                        <div className="flex items-center gap-2 mt-2">
                                          <span className="text-[10px] text-gray-500 font-mono">#{disc.external_id}</span>
                                          <span className="w-1 h-1 rounded-full bg-gray-700" />
                                          <span className="text-[10px] text-gray-500 truncate">@{disc.author}</span>
                                        </div>
                                      </div>
                                    </div>
                                  </a>
                                ))
                              )}
                            </div>
                          </ScrollArea>
                        </div>
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
                            <div className="prose prose-invert prose-p:text-gray-300 prose-headings:font-bold prose-pre:bg-[#0A0C10] prose-pre:border prose-pre:border-aurora-border max-w-none">
                              <ReactMarkdown
                                components={{
                                  h1: ({ node, ...props }) => <h1 className="text-3xl font-bold text-white mb-6 border-b border-white/[0.1] pb-4" {...props} />,
                                  h2: ({ node, ...props }) => <h2 className="text-xl mt-12 mb-6 text-aurora-cyan font-mono flex items-center gap-2" {...props} />,
                                  h3: ({ node, ...props }) => <h3 className="text-lg font-bold mt-8 mb-3 text-aurora-purple" {...props} />,
                                  p: ({ node, ...props }) => <p className="leading-7 mb-4 text-gray-300/90" {...props} />,
                                  ul: ({ node, ...props }) => <ul className="list-none space-y-2 ml-4 mb-4" {...props} />,
                                  li: ({ node, ...props }) => (
                                    <div className="flex gap-3 items-start">
                                      <div className="w-1.5 h-1.5 rounded-full bg-aurora-cyan mt-2.5 flex-shrink-0" />
                                      <li className="leading-relaxed text-gray-300" {...props} />
                                    </div>
                                  ),
                                  code: ({ node, inline, className, children, ...props }) => {
                                    const match = /language-(\w+)/.exec(className || '');
                                    const isMermaid = match && match[1] === 'mermaid';

                                    if (isMermaid && !inline) {
                                      return <Mermaid chart={String(children).replace(/\n$/, '')} />;
                                    }

                                    return inline
                                      ? <code className="px-1.5 py-0.5 rounded bg-white/[0.05] border border-white/[0.1] text-aurora-cyan font-mono text-xs" {...props}>{children}</code>
                                      : <code className={className} {...props}>{children}</code>
                                  },
                                  pre: ({ node, ...props }) => (
                                    <pre className="my-4 p-4 rounded-lg bg-[#0A0C10] border border-white/[0.08] font-mono text-[13px] text-gray-300 overflow-x-auto" {...props} />
                                  ),
                                }}
                              >
                                {systemDoc}
                              </ReactMarkdown>
                            </div>
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
                  ) : showHistory ? (
                    // --- History View ---
                    <div className="space-y-6">
                      {/* Header */}
                      <div className="bg-gradient-to-br from-green-500/10 to-transparent border border-green-500/20 rounded-xl p-6">
                        <div className="flex items-center justify-between">
                          <div>
                            <h2 className="text-xl font-bold text-white mb-1">File History</h2>
                            <p className="text-sm text-gray-400">Git commit timeline for {selectedFile}</p>
                          </div>
                          <div className="flex items-center gap-2 text-xs text-gray-500">
                            <Activity className="w-4 h-4" />
                            <span>{commits.length} commits</span>
                          </div>
                        </div>
                      </div>

                      {/* History Header & Stats */}
                      <div className="flex flex-col gap-6">
                        <div className="flex items-center justify-between">
                          <h1 className="text-3xl font-bold text-white flex items-center gap-3">
                            <Activity className="w-8 h-8 text-green-500" />
                            History Timeline
                          </h1>
                          <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-green-500/5 border border-green-500/10">
                            <code className="text-[10px] text-green-500 font-mono uppercase font-bold tracking-widest">
                              {commits.length} commits traced
                            </code>
                          </div>
                        </div>

                        {/* Author Stats Mini-Dashboard */}
                        {authorStats.length > 0 && (
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="p-4 rounded-xl bg-white/[0.02] border border-white/[0.05]">
                              <span className="text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-3 block">Top Contributors</span>
                              <div className="space-y-3">
                                {authorStats.slice(0, 3).map((stat, i) => (
                                  <div key={i} className="space-y-1">
                                    <div className="flex justify-between text-xs">
                                      <span className="text-gray-300 font-medium">{stat.name}</span>
                                      <span className="text-gray-500">{stat.commits} commits</span>
                                    </div>
                                    <div className="h-1.5 w-full bg-white/[0.05] rounded-full overflow-hidden">
                                      <div
                                        className="h-full bg-green-500/50 rounded-full"
                                        style={{ width: `${(stat.commits / authorStats[0].commits) * 100}%` }}
                                      />
                                    </div>
                                  </div>
                                ))}
                              </div>
                            </div>
                            <div className="p-4 rounded-xl bg-white/[0.02] border border-white/[0.05] flex flex-col justify-center">
                              <span className="text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-2 block">Code Churn</span>
                              <div className="flex items-end gap-1 mb-1">
                                <span className="text-2xl font-bold text-white">
                                  {authorStats.reduce((acc, s) => acc + s.additions + s.deletions, 0).toLocaleString()}
                                </span>
                                <span className="text-[10px] text-gray-500 font-mono mb-1.5 uppercase">lines modified</span>
                              </div>
                              <p className="text-[11px] text-gray-600 leading-relaxed italic">
                                Analysis based on target path metadata and git logs.
                              </p>
                            </div>
                          </div>
                        )}

                        <div className="flex gap-3 items-center p-4 bg-[#0A0C10]/50 border border-white/[0.05] rounded-xl">
                          <input
                            type="text"
                            placeholder="Filter by author..."
                            className="flex-1 bg-[#15171B] border border-white/[0.08] rounded-lg px-3 py-2 text-xs text-gray-300 focus:outline-none focus:border-green-500/50 focus:ring-1 focus:ring-green-500/20"
                            value={historyFilter.author}
                            onChange={(e) => setHistoryFilter({ ...historyFilter, author: e.target.value })}
                          />
                          <div className="h-4 w-px bg-white/[0.05]" />
                          <span className="text-[10px] font-bold text-gray-600 uppercase tracking-tighter">Timeline Focus</span>
                        </div>
                      </div>

                      {/* Timeline */}
                      <div className="relative">
                        {/* Vertical line */}
                        <div className="absolute left-6 top-0 bottom-0 w-px bg-gradient-to-b from-green-500/50 via-green-500/20 to-transparent" />

                        {/* Loading State */}
                        {loadingHistory ? (
                          <div className="flex flex-col items-center justify-center py-12">
                            <Loader2 className="w-8 h-8 text-green-400 animate-spin mb-3" />
                            <p className="text-sm text-gray-400">Loading commit history...</p>
                          </div>
                        ) : commits.length === 0 ? (
                          <div className="flex flex-col items-center justify-center py-12">
                            <Activity className="w-12 h-12 text-gray-600 mb-3" />
                            <p className="text-sm text-gray-400">No commit history found for this file</p>
                            <p className="text-xs text-gray-600 mt-1">This file may not be tracked by Git</p>
                          </div>
                        ) : (
                          /* Commits */
                          <div className="space-y-6">
                            {commits
                              .filter(commit => {
                                if (historyFilter.author && !commit.author.toLowerCase().includes(historyFilter.author.toLowerCase())) return false;
                                return true;
                              })
                              .map((commit, index) => {
                                const isExpanded = expandedCommits.has(commit.id);
                                const commitDate = new Date(commit.date);

                                return (
                                  <div key={commit.id} className="relative pl-16">
                                    {/* Timeline dot */}
                                    <div className="absolute left-[21px] top-6 w-3 h-3 rounded-full bg-green-500 border-2 border-[#0F1117] shadow-lg shadow-green-500/50" />

                                    {/* Commit card */}
                                    <div className={cn(
                                      "bg-[#0A0C10] border rounded-xl overflow-hidden transition-all",
                                      isExpanded ? "border-green-500/30" : "border-white/[0.05] hover:border-white/[0.1]"
                                    )}>
                                      <button
                                        onClick={() => {
                                          const newExpanded = new Set(expandedCommits);
                                          if (isExpanded) {
                                            newExpanded.delete(commit.id);
                                          } else {
                                            newExpanded.add(commit.id);
                                          }
                                          setExpandedCommits(newExpanded);
                                        }}
                                        className="w-full p-4 text-left hover:bg-white/[0.02] transition-colors"
                                      >
                                        <div className="flex items-start justify-between gap-4">
                                          <div className="flex-1 min-w-0">
                                            <div className="flex items-center gap-2 mb-2">
                                              <code className="px-2 py-0.5 rounded bg-white/[0.05] border border-white/[0.1] text-green-400 font-mono text-xs">
                                                {commit.hash}
                                              </code>
                                              <span className="text-xs text-gray-500">
                                                {commitDate.toLocaleDateString()} at {commitDate.toLocaleTimeString()}
                                              </span>
                                            </div>
                                            <p className="text-sm text-white font-medium mb-1">{commit.message}</p>
                                            <div className="flex items-center gap-3 text-xs text-gray-500">
                                              <span>{commit.author}</span>
                                              <span>•</span>
                                              <span>{commit.filesChanged} files</span>
                                              <span className="text-green-400">+{commit.additions}</span>
                                              <span className="text-red-400">-{commit.deletions}</span>
                                            </div>
                                          </div>
                                          <ChevronDown className={cn(
                                            "w-4 h-4 text-gray-500 transition-transform flex-shrink-0",
                                            isExpanded && "rotate-180"
                                          )} />
                                        </div>
                                      </button>

                                      {/* Expanded details */}
                                      {isExpanded && (
                                        <div className="border-t border-white/[0.05] p-4 bg-black/20">
                                          <div className="flex items-center justify-between mb-3 mt-4">
                                            <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider">Affected Entities</h4>
                                            <button
                                              onClick={() => fetchCommitDiff(commit.id)}
                                              className="flex items-center gap-1.5 px-2 py-1 rounded bg-green-500/10 border border-green-500/20 text-[10px] font-bold text-green-400 hover:bg-green-500/20 transition-all uppercase tracking-tighter"
                                            >
                                              {loadingDiff === commit.id ? <Loader2 className="w-3 h-3 animate-spin" /> : <Terminal className="w-3 h-3" />}
                                              View Source Changes
                                            </button>
                                          </div>

                                          <div className="space-y-2">
                                            {commit.files.map((file, idx) => (
                                              <div key={idx} className="flex items-center justify-between p-2 rounded bg-white/[0.02] border border-white/[0.05]">
                                                <div className="flex items-center gap-2 flex-1 min-w-0">
                                                  <div className={cn(
                                                    "w-1.5 h-1.5 rounded-full flex-shrink-0",
                                                    file.changeType === 'added' && "bg-green-500",
                                                    file.changeType === 'modified' && "bg-yellow-500",
                                                    file.changeType === 'deleted' && "bg-red-500"
                                                  )} />
                                                  <code className="text-xs font-mono text-gray-300 truncate">{file.path}</code>
                                                </div>
                                                <div className="flex items-center gap-2 text-xs flex-shrink-0">
                                                  <span className="text-green-400">+{file.additions}</span>
                                                  <span className="text-red-400">-{file.deletions}</span>
                                                </div>
                                              </div>
                                            ))}
                                          </div>

                                          {commitDiffs[commit.id] && (
                                            <div className="mt-4 p-4 rounded-xl bg-black/40 border border-white/[0.05] overflow-x-auto max-h-[400px]">
                                              <pre className="text-[11px] font-mono leading-relaxed text-gray-400">
                                                {commitDiffs[commit.id].split('\n').map((line, i) => (
                                                  <div
                                                    key={i}
                                                    className={cn(
                                                      "whitespace-pre",
                                                      line.startsWith('+') && !line.startsWith('+++') ? "text-green-400 bg-green-400/5" :
                                                        line.startsWith('-') && !line.startsWith('---') ? "text-red-400 bg-red-400/5" :
                                                          line.startsWith('@@') ? "text-aurora-cyan/70 bg-aurora-cyan/5 my-1" : ""
                                                    )}
                                                  >
                                                    {line}
                                                  </div>
                                                ))}
                                              </pre>
                                            </div>
                                          )}
                                        </div>
                                      )}
                                    </div>
                                  </div>
                                );
                              })}
                          </div>
                        )}
                      </div>
                    </div>
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
                      <div className="mb-10 pb-6 border-b border-white/[0.1] relative">
                        <div className="flex items-center gap-3 mb-2 text-aurora-cyan">
                          <FileText className="w-5 h-5" />
                          <span className="text-xs font-mono uppercase tracking-widest font-bold">Generated Documentation</span>
                        </div>
                        <h1 className="text-4xl font-bold text-white mb-2">{selectedFile?.split('/').pop()}</h1>
                        <p className="text-gray-500 text-lg">Automated analysis of {selectedFile}</p>
                        <div className="absolute right-0 top-0 flex gap-2">
                          {!isEditing && (
                            <div className="relative group">
                              <Button size="sm" variant="outline" className="border-aurora-cyan/30 bg-aurora-cyan/5 text-aurora-cyan hover:bg-aurora-cyan hover:text-black transition-all rounded-xl">
                                <Sparkles className="w-4 h-4 mr-2" /> Visual AI
                              </Button>
                              <div className="absolute top-full right-0 pt-2 opacity-0 group-hover:opacity-100 pointer-events-none group-hover:pointer-events-auto transition-all z-50">
                                <div className="w-48 bg-[#0A0C10] border border-white/[0.1] rounded-xl shadow-2xl overflow-hidden">
                                  <button
                                    onClick={() => generateDiagram('flowchart')}
                                    className="w-full text-left px-4 py-3 text-[11px] font-mono text-gray-400 hover:text-white hover:bg-white/[0.05] border-b border-white/[0.05] transition-colors"
                                  >
                                    GENERATE FLOWCHART
                                  </button>
                                  <button
                                    onClick={() => generateDiagram('sequence')}
                                    className="w-full text-left px-4 py-3 text-[11px] font-mono text-gray-400 hover:text-white hover:bg-white/[0.05] transition-colors"
                                  >
                                    GENERATE SEQUENCE
                                  </button>
                                </div>
                              </div>
                            </div>
                          )}
                          {isEditing ? (
                            <>
                              <Button size="sm" variant="ghost" className="text-gray-400 hover:text-white" onClick={() => { setIsEditing(false); setEditContent(docs); }}>
                                <Ban className="w-4 h-4 mr-2" /> Cancel
                              </Button>
                              <Button size="sm" className="bg-aurora-purple text-white hover:bg-aurora-purple/80" onClick={handleSave}>
                                <Save className="w-4 h-4 mr-2" /> Save Changes
                              </Button>
                            </>
                          ) : (
                            <Button size="sm" variant="ghost" className="text-gray-400 hover:text-white" onClick={() => setIsEditing(true)}>
                              <Edit2 className="w-4 h-4 mr-2" /> Edit Docs
                            </Button>
                          )}
                        </div>
                      </div>

                      {/* Content Area */}
                      {isEditing ? (
                        <div className="w-full">
                          <textarea
                            value={editContent}
                            onChange={(e) => setEditContent(e.target.value)}
                            className="w-full h-[60vh] bg-[#050608] border border-aurora-border rounded-lg p-6 font-mono text-sm text-gray-300 focus:outline-none focus:border-aurora-purple/50 resize-none font-sans leading-relaxed"
                            spellCheck={false}
                          />
                        </div>
                      ) : (
                        /* Markdown Content */
                        <div className="space-y-3 prose prose-invert prose-p:text-gray-300 prose-headings:font-bold prose-pre:bg-[#0A0C10] prose-pre:border prose-pre:border-aurora-border max-w-none">
                          <ReactMarkdown
                            components={{
                              h1: ({ node, ...props }) => <h1 className="text-4xl font-bold text-white mb-6 border-b border-white/[0.1] pb-4" {...props} />,
                              h2: ({ node, ...props }) => <h2 className="text-2xl mt-12 mb-6 text-white font-semibold flex items-center gap-2" {...props} />,
                              h3: ({ node, ...props }) => <h3 className="text-lg font-bold mt-8 mb-3 text-aurora-purple" {...props} />,
                              p: ({ node, ...props }) => <div className="leading-7 mb-4 text-gray-300/90" {...props} />,
                              ul: ({ node, ...props }) => <ul className="list-none space-y-2 ml-4 mb-4" {...props} />,
                              li: ({ node, ...props }) => (
                                <div className="flex gap-3 items-start">
                                  <div className="w-1.5 h-1.5 rounded-full bg-aurora-cyan mt-2.5 flex-shrink-0" />
                                  <li className="leading-relaxed text-gray-300" {...props} />
                                </div>
                              ),
                              code: ({ node, inline, className, children, ...props }) => {
                                const match = /language-(\w+)/.exec(className || '');
                                const isMermaid = match && match[1] === 'mermaid';

                                if (isMermaid && !inline) {
                                  return <Mermaid chart={String(children).replace(/\n$/, '')} />;
                                }

                                return inline
                                  ? <code className="px-1.5 py-0.5 rounded bg-white/[0.05] border border-white/[0.1] text-aurora-cyan font-mono text-xs" {...props}>{children}</code>
                                  : <pre className="my-4 p-4 rounded-lg bg-[#0A0C10] border border-white/[0.08] font-mono text-[13px] text-gray-300 overflow-x-auto"><code className={className} {...props}>{children}</code></pre>
                              },
                            }}
                          >
                            {docs}
                          </ReactMarkdown>
                        </div>
                      )}
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

                    {/* Search Results Sections */}
                    {(searchResults?.files?.length > 0 || searchResults?.documentation?.length > 0) && (
                      <div className="mt-8 pt-8 border-t border-white/[0.05] space-y-6">
                        {searchResults?.files?.length > 0 && (
                          <div className="space-y-3">
                            <div className="flex items-center gap-2 text-aurora-purple uppercase text-[10px] font-bold tracking-widest font-mono">
                              <File className="w-3.5 h-3.5" />
                              <span>File Matches</span>
                            </div>
                            <div className="grid grid-cols-1 gap-2">
                              {searchResults.files.map((file, i) => (
                                <button
                                  key={i}
                                  onClick={() => {
                                    setSelectedFile(file.path);
                                    setShowSearch(false);
                                  }}
                                  className="flex items-center gap-3 p-3 rounded-xl bg-white/[0.02] border border-white/[0.05] hover:border-aurora-purple/30 transition-all text-left group"
                                >
                                  <div className="w-8 h-8 rounded-lg bg-aurora-purple/10 flex items-center justify-center text-aurora-purple group-hover:bg-aurora-purple/20 transition-colors">
                                    <FileText className="w-4 h-4" />
                                  </div>
                                  <div>
                                    <p className="text-sm text-gray-200 font-mono">{file.path.split('/').pop()}</p>
                                    <p className="text-[10px] text-gray-500 font-mono">{file.path}</p>
                                  </div>
                                </button>
                              ))}
                            </div>
                          </div>
                        )}

                        {searchResults?.documentation?.length > 0 && (
                          <div className="space-y-3">
                            <div className="flex items-center gap-2 text-aurora-cyan uppercase text-[10px] font-bold tracking-widest font-mono">
                              <Search className="w-3.5 h-3.5" />
                              <span>Documentation Matches</span>
                            </div>
                            <div className="space-y-2">
                              {searchResults.documentation.map((doc, i) => (
                                <button
                                  key={i}
                                  onClick={() => {
                                    setSelectedFile(doc.path);
                                    setShowSearch(false);
                                  }}
                                  className="w-full p-4 rounded-xl bg-white/[0.02] border border-white/[0.05] hover:border-aurora-cyan/30 transition-all text-left"
                                >
                                  <div className="flex items-center justify-between mb-2">
                                    <span className="text-[10px] font-mono text-aurora-cyan bg-aurora-cyan/10 px-2 py-0.5 rounded">{doc.path}</span>
                                    <ArrowUpRight className="w-3 h-3 text-gray-600" />
                                  </div>
                                  <p className="text-xs text-gray-400 leading-relaxed italic line-clamp-2">
                                    {doc.snippet}
                                  </p>
                                </button>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    )}
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

