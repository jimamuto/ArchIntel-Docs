import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import {
  GitBranch,
  Github,
  Slack,
  Webhook,
  Settings,
  Plus,
  CheckCircle,
  AlertCircle,
  ExternalLink
} from 'lucide-react';

export default function Integrations() {
  const integrations = [
    {
      id: 'github',
      name: 'GitHub',
      description: 'Connect repositories and sync code changes automatically',
      icon: <Github className="w-6 h-6" />,
      status: 'connected',
      configured: true
    },
    {
      id: 'slack',
      name: 'Slack',
      description: 'Receive notifications and collaborate on documentation',
      icon: <Slack className="w-6 h-6" />,
      status: 'available',
      configured: false
    },
    {
      id: 'webhooks',
      name: 'Webhooks',
      description: 'Custom integrations via webhooks',
      icon: <Webhook className="w-6 h-6" />,
      status: 'available',
      configured: false
    }
  ];

  return (
    <div className="h-screen flex flex-col bg-aurora-bg text-gray-200 font-sans overflow-hidden">
      <header className="h-16 border-b border-aurora-border flex items-center justify-between px-6 bg-[#0A0C10]/80 backdrop-blur-md relative z-20 shadow-sm">
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-4">
            <h2 className="text-sm font-bold uppercase tracking-widest text-white/50 font-mono">Integrations</h2>
            <div className="h-4 w-px bg-white/[0.1]" />
          </div>
        </div>
      </header>

      <div className="flex-1 overflow-y-auto p-10">
        {/* Header */}
        <div className="mb-10 max-w-7xl mx-auto">
          <div className="flex items-center gap-2 text-aurora-cyan text-[10px] uppercase font-bold tracking-[0.2em] font-mono mb-2">
            <Webhook className="w-3 h-3" />
            External Ecosystem
          </div>
          <h1 className="text-4xl font-bold text-white tracking-tight mb-3">Service Marketplace</h1>
          <p className="text-gray-500 max-w-lg">
            Connect external tools and services to enhance your documentation workflow.
            <span className="text-aurora-purple font-medium ml-1">Coming soon.</span>
          </p>
        </div>

        {/* Coming Soon Notice */}
        <Card className="bg-aurora-purple/5 border-aurora-purple/20 rounded-2xl p-8 mb-8">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 bg-aurora-purple/20 rounded-xl flex items-center justify-center flex-shrink-0">
              <AlertCircle className="w-6 h-6 text-aurora-purple" />
            </div>
            <div className="flex-1">
              <h3 className="text-xl font-semibold text-aurora-purple mb-2">Integrations Coming Soon</h3>
              <p className="text-slate-300 mb-4">
                We're working on powerful integrations to connect ArchIntel with your favorite tools.
                This feature is currently in development.
              </p>
              <div className="text-sm text-gray-500">
                Expected features:
                <ul className="list-disc list-inside mt-2 space-y-1">
                  <li>GitHub repository synchronization</li>
                  <li>Slack notifications for documentation updates</li>
                  <li>Webhook support for custom workflows</li>
                  <li>Jira integration for project tracking</li>
                  <li>Discord community channels</li>
                </ul>
              </div>
            </div>
          </div>
        </Card>

        {/* Available Integrations */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {integrations.map((integration) => (
            <Card
              key={integration.id}
              className="bg-[#15171B] border-white/[0.05] rounded-2xl p-6 hover:border-aurora-purple/30 transition-all duration-300 group"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${integration.status === 'connected'
                    ? 'bg-emerald-500/20 text-emerald-400'
                    : 'bg-slate-800 text-slate-400'
                    }`}>
                    {integration.icon}
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-slate-50">{integration.name}</h3>
                    <div className={`flex items-center gap-1.5 text-xs px-2 py-1 rounded-full ${integration.status === 'connected'
                      ? 'bg-emerald-500/10 text-emerald-300'
                      : 'bg-slate-700/50 text-slate-400'
                      }`}>
                      {integration.status === 'connected' ? (
                        <>
                          <CheckCircle className="w-3 h-3" />
                          Connected
                        </>
                      ) : (
                        'Available'
                      )}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {integration.configured ? (
                    <Button
                      variant="outline"
                      size="sm"
                      className="border-slate-700 text-slate-300 hover:bg-slate-800/50"
                    >
                      <Settings className="w-4 h-4 mr-2" />
                      Configure
                    </Button>
                  ) : (
                    <Button
                      size="sm"
                      className="bg-gradient-to-r from-cyan-500 to-emerald-500 text-slate-950 hover:scale-105 transition-all duration-200"
                      disabled
                    >
                      <Plus className="w-4 h-4 mr-2" />
                      Connect
                    </Button>
                  )}
                </div>
              </div>

              <p className="text-slate-400 text-sm mb-4">
                {integration.description}
              </p>

              <div className="pt-4 border-t border-slate-800/30">
                <div className="flex items-center justify-between text-xs text-slate-500">
                  <span>Status: {integration.status === 'connected' ? 'Active' : 'Coming Soon'}</span>
                  <span className="flex items-center gap-1">
                    Learn more
                    <ExternalLink className="w-3 h-3" />
                  </span>
                </div>
              </div>
            </Card>
          ))}
        </div>

        {/* Call to Action */}
        <Card className="bg-gradient-to-br from-slate-900/30 to-slate-950/30 border border-slate-800/30 rounded-2xl p-8 mt-8">
          <div className="text-center">
            <div className="w-16 h-16 bg-gradient-to-br from-cyan-500/20 to-emerald-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
              <GitBranch className="w-8 h-8 text-cyan-400" />
            </div>
            <h3 className="text-xl font-semibold text-slate-50 mb-2">Want a Specific Integration?</h3>
            <p className="text-slate-400 mb-6 max-w-md mx-auto">
              Have a tool or service you'd like to see integrated? Let us know what integrations
              would be most valuable for your workflow.
            </p>
            <Button
              className="bg-gradient-to-r from-cyan-500 to-emerald-500 text-slate-950 hover:scale-105 transition-all duration-200"
              disabled
            >
              Request Integration
            </Button>
          </div>
        </Card>
      </div>
    </div>
  );
}
