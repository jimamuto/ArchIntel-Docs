import { useState, useEffect } from 'react';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { ScrollArea } from '../components/ui/scroll-area';

export default function Docs() {
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState('');
  const [selectedProjectData, setSelectedProjectData] = useState(null);
  const [structure, setStructure] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [docs, setDocs] = useState(null);
  const [code, setCode] = useState(null);
  const [showCode, setShowCode] = useState(false);
  const [testResults, setTestResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [ingestingCode, setIngestingCode] = useState(false);

  useEffect(() => {
    async function fetchProjects() {
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/projects`);
        const data = await res.json();
        setProjects(data.projects || []);
      } catch (err) {
        setError('Failed to load projects');
      }
    }
    fetchProjects();
  }, []);

  useEffect(() => {
    if (!selectedProject) {
      setSelectedProjectData(null);
      return;
    }
    const project = projects.find(p => p.id === selectedProject);
    setSelectedProjectData(project);
    async function fetchStructure() {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/projects/${selectedProject}/structure`);
        const data = await res.json();
        setStructure(data.structure || []);
      } catch (err) {
        setError('Failed to load structure');
      } finally {
        setLoading(false);
      }
    }
    fetchStructure();
  }, [selectedProject, projects]);

  useEffect(() => {
    if (!selectedProject || !selectedFile) return;
    async function fetchDocsAndCode() {
      setLoading(true);
      setError(null);
      try {
        // Fetch docs (AI-generated)
        const docsRes = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/docs/${selectedProject}?file=${encodeURIComponent(selectedFile)}`);
        const docsData = await docsRes.json();
        setDocs(docsData.docs || null);
      } catch (err) {
        setError('Failed to load docs');
      }
      try {
        // Fetch code (raw file content)
        if (selectedProjectData) {
          const repoPath = "../" + selectedProjectData.repo_url.split('/').pop().replace('.git', '');
          const codeRes = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/projects/${selectedProject}/file/code?path=${encodeURIComponent(selectedFile)}&repo_path=${encodeURIComponent(repoPath)}`);
          if (codeRes.ok) {
            const codeText = await codeRes.text();
            setCode(codeText);
          } else {
            setCode('// Could not fetch code. Repository may not be cloned locally.');
          }
        } else {
          setCode('// Project data not available.');
        }
      } catch (err) {
        setCode('// Failed to load code.');
      } finally {
        setLoading(false);
      }
    }
    fetchDocsAndCode();
  }, [selectedProject, selectedFile]);

  return (
    <main className="min-h-screen bg-slate-950 px-4 py-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-slate-50 mb-2">Documentation Explorer</h1>
            <p className="text-sm text-slate-400">Browse and explore AI-generated documentation for your codebase</p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline" size="sm" className="border-slate-700 text-slate-300 hover:bg-slate-800">
              Refresh
            </Button>
            <Button variant="outline" size="sm" className="border-slate-700 text-slate-300 hover:bg-slate-800">
              Export
            </Button>
          </div>
        </div>

        <div className="flex flex-col lg:flex-row gap-6">
          {/* Sidebar */}
          <div className="w-full lg:w-80">
            <Card className="bg-slate-900/60 backdrop-blur-sm border-slate-800/50 p-6">
              <div className="mb-4">
                <label htmlFor="project-select" className="block text-sm font-medium mb-3 text-slate-50">Select Project</label>
                <select
                  id="project-select"
                  onChange={(e) => setSelectedProject(e.target.value)}
                  value={selectedProject || ''}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-3 text-sm text-slate-50 focus:outline-none focus:ring-2 focus:ring-emerald-500/70 focus:border-emerald-500 transition-colors"
                >
                  <option value="" disabled>Select a project</option>
                  {projects.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
                </select>
              </div>

              {selectedProject && (
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-sm font-semibold text-slate-50">Project Actions</h3>
                  </div>
                  <div className="mb-6">
                    {structure.length === 0 && !loading && (
                      <Button
                        onClick={async () => {
                          setIngestingCode(true);
                          setError(null);
                          try {
                            const cloneRes = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/projects/${selectedProject}/clone`, {
                              method: 'POST'
                            });
                            if (cloneRes.ok) {
                              // Refresh structure after cloning
                              const structureRes = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/projects/${selectedProject}/structure`);
                              const data = await structureRes.json();
                              setStructure(data.structure || []);
                            } else {
                              setError('Failed to clone repository');
                            }
                          } catch (err) {
                            setError('Failed to clone repository');
                          } finally {
                            setIngestingCode(false);
                          }
                        }}
                        className="w-full bg-blue-500 hover:bg-blue-400 text-slate-950 mb-3"
                        size="sm"
                        disabled={ingestingCode}
                      >
                        {ingestingCode ? '📥 Cloning Repository...' : '📥 Clone Repository'}
                      </Button>
                    )}
                    <Button
                      onClick={async () => {
                        setLoading(true);
                        setError(null);
                        try {
                          const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/docs/${selectedProject}/test`, {
                            method: 'POST'
                          });
                          const data = await res.json();
                          setTestResults(data);
                        } catch (err) {
                          setError('Failed to run tests');
                        } finally {
                          setLoading(false);
                        }
                      }}
                      className="w-full bg-emerald-500 hover:bg-emerald-400 text-slate-950"
                      size="sm"
                      disabled={structure.length === 0}
                    >
                      🧪 Run Tests
                    </Button>
                  </div>

                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-sm font-semibold text-slate-50">File Structure</h3>
                    <Button variant="ghost" size="sm" className="h-7 px-2 text-xs text-slate-400 hover:text-slate-50">
                      Collapse All
                    </Button>
                  </div>

                  <ScrollArea className="h-[500px] pr-4">
                    {structure.length === 0 && !loading ? (
                      <div className="text-center py-8">
                        <div className="w-12 h-12 bg-slate-800 rounded-lg flex items-center justify-center mx-auto mb-3">
                          <span className="text-slate-500">📁</span>
                        </div>
                        <p className="text-xs text-slate-500">No files found</p>
                      </div>
                    ) : (
                      <ul className="space-y-1">
                        {structure.map(f => (
                          <li key={f.path}>
                            <Button
                              variant="ghost"
                              size="sm"
                              className={`w-full justify-start text-xs font-medium transition-all duration-150 ${
                                selectedFile === f.path
                                  ? 'bg-emerald-500/10 text-emerald-300 border-l-2 border-emerald-500'
                                  : 'text-slate-300 hover:bg-slate-800 hover:text-slate-50'
                              }`}
                              onClick={() => setSelectedFile(f.path)}
                            >
                              <span className="truncate">{f.path}</span>
                            </Button>
                          </li>
                        ))}
                      </ul>
                    )}
                  </ScrollArea>
                </div>
              )}
            </Card>
          </div>

          {/* Main Content */}
          <div className="flex-1">
            {!selectedProject ? (
              <Card className="bg-slate-900/60 backdrop-blur-sm border-slate-800/50 p-12 text-center">
                <div className="w-16 h-16 bg-slate-800 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">🔍</span>
                </div>
                <h3 className="text-lg font-semibold text-slate-50 mb-2">Select a Project</h3>
                <p className="text-slate-400 max-w-md mx-auto">
                  Choose a project from the sidebar to explore its documentation and codebase structure.
                </p>
              </Card>
            ) : loading ? (
              <Card className="bg-slate-900/60 backdrop-blur-sm border-slate-800/50 p-8">
                <div className="animate-pulse">
                  <div className="h-6 bg-slate-700 rounded w-1/3 mb-4"></div>
                  <div className="space-y-3">
                    <div className="h-4 bg-slate-700 rounded w-full"></div>
                    <div className="h-4 bg-slate-700 rounded w-5/6"></div>
                    <div className="h-4 bg-slate-700 rounded w-4/5"></div>
                    <div className="h-4 bg-slate-700 rounded w-3/4"></div>
                  </div>
                </div>
              </Card>
            ) : error ? (
              <Card className="bg-rose-500/10 border-rose-500/30 p-6">
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-8 h-8 bg-rose-500/20 rounded-full flex items-center justify-center">
                    <span className="text-rose-400">⚠️</span>
                  </div>
                  <h3 className="text-lg font-semibold text-rose-400">Error Loading Documentation</h3>
                </div>
                <p className="text-rose-300 mb-4">{error}</p>
                <Button variant="outline" size="sm" className="border-rose-500/30 text-rose-300 hover:bg-rose-500/10">
                  Try Again
                </Button>
              </Card>
            ) : docs || code ? (
              <Card className="group relative bg-slate-900/60 backdrop-blur-sm border-slate-800/50 p-6">
                <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-emerald-500/60 to-transparent"></div>
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h2 className="text-lg font-semibold text-slate-50 mb-1">{showCode ? 'Source Code' : 'Documentation'}</h2>
                    <p className="text-xs text-slate-500">{selectedFile}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      className={`border-slate-700 text-slate-300 hover:bg-slate-800 ${showCode ? 'bg-emerald-900/30' : ''}`}
                      onClick={() => setShowCode(!showCode)}
                    >
                      {showCode ? 'Show Docs' : 'Show Code'}
                    </Button>
                  </div>
                </div>
                <div className="prose prose-sm prose-slate max-w-none">
                  {showCode ? (
                    <pre className="whitespace-pre-wrap text-slate-300 text-sm leading-relaxed font-mono bg-slate-950/50 p-4 rounded-lg border border-slate-800 overflow-x-auto">{code || '// No code found.'}</pre>
                  ) : (
                    <div className="whitespace-pre-wrap text-slate-300 text-sm leading-relaxed bg-slate-950/50 p-4 rounded-lg border border-slate-800 overflow-x-auto" style={{fontFamily: 'monospace'}}>
                      {docs ? docs.split('\n').map((line, index) => (
                        <div key={index} className={line.startsWith('#') ? 'font-bold text-slate-100 mb-2' : line.startsWith('##') ? 'font-semibold text-slate-200 mb-1' : 'mb-1'}>
                          {line}
                        </div>
                      )) : '// No docs found.'}
                    </div>
                  )}
                </div>
              </Card>
            ) : (
              <Card className="bg-slate-900/60 backdrop-blur-sm border-slate-800/50 p-12 text-center">
                <div className="w-16 h-16 bg-slate-800 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">📄</span>
                </div>
                <h3 className="text-lg font-semibold text-slate-50 mb-2">No Documentation Selected</h3>
                <p className="text-slate-400 max-w-md mx-auto mb-6">
                  Select a file from the sidebar to view its AI-generated documentation and analysis.
                </p>
                <div className="flex justify-center gap-3">
                  <Button variant="outline" size="sm" className="border-slate-700 text-slate-300 hover:bg-slate-800">
                    Browse Files
                  </Button>
                  <Button size="sm" className="bg-emerald-500 hover:bg-emerald-400 text-slate-950">
                    Generate All Docs
                  </Button>
                </div>
              </Card>
            )}

            {/* Test Results Section */}
            {testResults && (
              <Card className="group relative bg-slate-900/60 backdrop-blur-sm border-slate-800/50 p-6 mt-6">
                <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-emerald-500/60 to-transparent"></div>
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h2 className="text-lg font-semibold text-slate-50 mb-1">🧪 Test Results</h2>
                    <p className="text-xs text-slate-500">{testResults.project_name}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      testResults.test_results.summary.test_status === 'PASSED'
                        ? 'bg-emerald-500/10 text-emerald-300'
                        : 'bg-rose-500/10 text-rose-300'
                    }`}>
                      {testResults.test_results.summary.test_status}
                    </span>
                  </div>
                </div>

                <div className="space-y-6">
                  {/* Summary */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="bg-slate-800/50 p-4 rounded-lg">
                      <div className="text-2xl font-bold text-emerald-400">{testResults.test_results.summary.total_files}</div>
                      <div className="text-xs text-slate-400">Total Files</div>
                    </div>
                    <div className="bg-slate-800/50 p-4 rounded-lg">
                      <div className="text-2xl font-bold text-blue-400">{testResults.test_results.summary.languages_detected}</div>
                      <div className="text-xs text-slate-400">Languages</div>
                    </div>
                    <div className="bg-slate-800/50 p-4 rounded-lg">
                      <div className="text-2xl font-bold text-purple-400">{Object.keys(testResults.test_results.language_breakdown).length}</div>
                      <div className="text-xs text-slate-400">File Types</div>
                    </div>
                  </div>

                  {/* Language Breakdown */}
                  <div>
                    <h3 className="text-sm font-semibold text-slate-50 mb-3">Language Breakdown</h3>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                      {Object.entries(testResults.test_results.language_breakdown).map(([lang, count]) => (
                        <div key={lang} className="bg-slate-800/30 p-3 rounded text-center">
                          <div className="text-lg font-bold text-slate-50">{count}</div>
                          <div className="text-xs text-slate-400 uppercase">{lang}</div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Test Details */}
                  <div>
                    <h3 className="text-sm font-semibold text-slate-50 mb-3">Test Details</h3>
                    <div className="space-y-3">
                      {testResults.test_results.tests.map((test, index) => (
                        <div key={index} className="bg-slate-800/30 p-4 rounded-lg">
                          <div className="flex items-center justify-between mb-2">
                            <h4 className="text-sm font-medium text-slate-50">{test.name}</h4>
                            <span className={`px-2 py-1 rounded text-xs font-medium ${
                              test.status === 'PASSED'
                                ? 'bg-emerald-500/10 text-emerald-300'
                                : 'bg-rose-500/10 text-rose-300'
                            }`}>
                              {test.status}
                            </span>
                          </div>
                          <p className="text-xs text-slate-400 mb-2">{test.description}</p>
                          <p className="text-xs text-slate-500">{test.details}</p>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Recommendations */}
                  <div>
                    <h3 className="text-sm font-semibold text-slate-50 mb-3">Recommendations</h3>
                    <ul className="space-y-2">
                      {testResults.test_results.recommendations.map((rec, index) => (
                        <li key={index} className="flex items-start gap-2 text-xs text-slate-400">
                          <span className="text-emerald-400 mt-1">•</span>
                          <span>{rec}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </Card>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}
