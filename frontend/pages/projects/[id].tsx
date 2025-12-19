import { useState } from 'react';
import { useRouter } from 'next/router';
import { Button } from '../../components/ui/button';
import { Card } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import { ScrollArea } from '../../components/ui/scroll-area';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '../../components/ui/tabs';

interface Project {
  id: number;
  name: string;
  status?: string;
}

export default function ProjectWorkspace() {
  const router = useRouter();
  const { id } = router.query;
  const [activeTab, setActiveTab] = useState('overview');

  // Mock data - replace with API call
  const project: Project = { id: Number(id), name: 'ArchIntel Docs', status: 'Ready' };

  const navigation = [
    { id: 'overview', label: 'Overview' },
    { id: 'docs', label: 'Docs' },
    { id: 'history', label: 'History' },
    { id: 'rationale', label: 'Rationale' },
    { id: 'qa', label: 'Q&A' },
  ];

  return (
    <div className="min-h-screen bg-slate-950 flex">
      {/* Sidebar */}
      <div className="w-64 bg-slate-950 border-r border-slate-800 flex flex-col">
        <div className="p-4 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <h2 className="text-sm font-semibold text-slate-50 truncate">{project.name}</h2>
            <Badge variant="outline" className="border-emerald-500/40 bg-emerald-500/10 text-emerald-300 text-xs">
              {project.status}
            </Badge>
          </div>
        </div>

        <ScrollArea className="flex-1">
          <nav className="p-2 space-y-1">
            {navigation.map((item) => (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`group flex w-full items-center gap-2 rounded-lg px-2.5 py-2 text-xs font-medium text-slate-400 transition-all duration-150 ease-out hover:bg-slate-900 hover:text-slate-50 ${
                  activeTab === item.id
                    ? 'bg-slate-900 text-slate-50 border-l-2 border-emerald-500'
                    : ''
                }`}
              >
                <span className={`flex h-6 w-6 items-center justify-center rounded-md bg-slate-900 text-slate-500 transition-colors group-hover:bg-slate-800 ${
                  activeTab === item.id ? 'bg-emerald-500/15 text-emerald-400' : ''
                }`}>
                  {/* Placeholder for icons */}
                  {item.id === 'overview' && '📊'}
                  {item.id === 'docs' && '📄'}
                  {item.id === 'history' && '📈'}
                  {item.id === 'rationale' && '💡'}
                  {item.id === 'qa' && '💬'}
                </span>
                <span className="truncate">{item.label}</span>
              </button>
            ))}
          </nav>
        </ScrollArea>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        <div className="p-4 border-b border-slate-800">
          <h1 className="text-lg font-semibold text-slate-50">{project.name}</h1>
        </div>

        <div className="flex-1 p-4">
          {activeTab === 'overview' && (
            <Card className="group relative bg-slate-900 border-slate-800 p-6">
              <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-emerald-500/60 to-transparent" />
              <h3 className="text-base font-semibold text-slate-50 mb-4">Project Overview</h3>
              <p className="text-sm text-slate-300">
                Code-aware documentation with Git history and design rationale.
              </p>
            </Card>
          )}

          {activeTab === 'docs' && (
            <div className="flex h-full gap-4">
              {/* File Tree Panel */}
              <div className="w-72 bg-slate-900 border border-slate-800 rounded-xl p-4">
                <h3 className="text-sm font-semibold text-slate-50 mb-4">Files</h3>
                <ScrollArea className="h-[calc(100vh-12rem)]">
                  <div className="space-y-1">
                    {/* Mock file tree */}
                    <button className="w-full text-left px-2 py-1 text-sm text-slate-300 hover:bg-slate-800 rounded">
                      src/
                    </button>
                    <button className="w-full text-left px-4 py-1 text-sm text-slate-300 hover:bg-slate-800 rounded">
                      main.py
                    </button>
                    <button className="w-full text-left px-4 py-1 text-sm text-slate-300 hover:bg-slate-800 rounded">
                      utils.py
                    </button>
                    <button className="w-full text-left px-2 py-1 text-sm text-slate-300 hover:bg-slate-800 rounded">
                      tests/
                    </button>
                    <button className="w-full text-left px-4 py-1 text-sm text-slate-300 hover:bg-slate-800 rounded">
                      test_main.py
                    </button>
                  </div>
                </ScrollArea>
              </div>

              {/* Document Viewer */}
              <div className="flex-1 bg-slate-900 border border-slate-800 rounded-xl p-4">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-sm font-semibold text-slate-50">src/main.py</h3>
                    <p className="text-xs text-slate-400">Last updated 2 hours ago</p>
                  </div>
                  <Button variant="outline" size="sm">
                    Regenerate Docs
                  </Button>
                </div>

                <Tabs defaultValue="overview" className="w-full">
                  <TabsList className="grid w-full grid-cols-4">
                    <TabsTrigger value="overview">Overview</TabsTrigger>
                    <TabsTrigger value="history">History</TabsTrigger>
                    <TabsTrigger value="rationale">Rationale</TabsTrigger>
                    <TabsTrigger value="api">API</TabsTrigger>
                  </TabsList>
                  <TabsContent value="overview" className="mt-4">
                    <div className="prose prose-sm prose-slate max-w-none">
                      <h4 className="text-base font-semibold text-slate-50">Main Module</h4>
                      <p className="text-sm text-slate-300">
                        This is the main entry point for the ArchIntel Docs application.
                        It handles the initialization of the FastAPI server and routes.
                      </p>
                      <h5 className="text-sm font-semibold text-slate-50 mt-4">Key Functions</h5>
                      <ul className="text-sm text-slate-300 list-disc list-inside">
                        <li>Initialize database connections</li>
                        <li>Set up API endpoints</li>
                        <li>Handle project ingestion</li>
                      </ul>
                    </div>
                  </TabsContent>
                  <TabsContent value="history" className="mt-4">
                    <p className="text-sm text-slate-300">Version history and changes...</p>
                  </TabsContent>
                  <TabsContent value="rationale" className="mt-4">
                    <p className="text-sm text-slate-300">Design decisions and trade-offs...</p>
                  </TabsContent>
                  <TabsContent value="api" className="mt-4">
                    <p className="text-sm text-slate-300">API documentation...</p>
                  </TabsContent>
                </Tabs>
              </div>
            </div>
          )}

          {activeTab === 'history' && (
            <div className="text-slate-300">History timeline here</div>
          )}

          {activeTab === 'rationale' && (
            <div className="text-slate-300">Rationale cards here</div>
          )}

          {activeTab === 'qa' && (
            <div className="text-slate-300">Q&A chat here</div>
          )}
        </div>
      </div>
    </div>
  );
}
