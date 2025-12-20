import React, { useState, useEffect } from 'react';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import {
  GitBranch,
  Github,
  Slack,
  Webhook,
  Settings,
  Plus,
  CheckCircle,
  ExternalLink,
  X,
  Loader2
} from 'lucide-react';

export default function Integrations() {
  const [integrationsState, setIntegrationsState] = useState({
    github: { status: 'available', configured: false, data: null },
    slack: { status: 'available', configured: false, data: null },
    webhooks: { status: 'available', configured: false, data: null }
  });

  const [activeModal, setActiveModal] = useState(null);
  const [formData, setFormData] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Load state from localStorage on mount
    const savedState = localStorage.getItem('archintel_integrations_state');
    if (savedState) {
      setIntegrationsState(JSON.parse(savedState));
    }
  }, []);

  const saveState = (newState) => {
    setIntegrationsState(newState);
    localStorage.setItem('archintel_integrations_state', JSON.stringify(newState));
  };

  const STATIC_INFO = {
    github: {
      name: 'GitHub',
      description: 'Connect repositories and sync code changes automatically',
      icon: <Github className="w-6 h-6" />,
      modalTitle: 'Connect GitHub',
      modalDescription: 'Enter a Personal Access Token (classic) to sync your repositories.',
      placeholder: 'ghp_xxxxxxxxxxxx',
      inputType: 'password'
    },
    slack: {
      name: 'Slack',
      description: 'Receive notifications and collaborate on documentation',
      icon: <Slack className="w-6 h-6" />,
      modalTitle: 'Connect Slack',
      modalDescription: 'Enter your Slack Webhook URL to receive notifications.',
      placeholder: 'https://hooks.slack.com/services/...',
      inputType: 'text'
    },
    webhooks: {
      name: 'Webhooks',
      description: 'Custom integrations via webhooks',
      icon: <Webhook className="w-6 h-6" />,
      modalTitle: 'Add Webhook',
      modalDescription: 'Enter the URL where you want to receive payloads.',
      placeholder: 'https://api.yourapp.com/webhooks/...',
      inputType: 'text'
    }
  };

  const handleConnect = (id) => {
    setActiveModal(id);
    setFormData('');
  };

  const handleDisconnect = (id) => {
    const newState = {
      ...integrationsState,
      [id]: { status: 'available', configured: false, data: null }
    };
    saveState(newState);
  };

  const handleSubmit = () => {
    if (!formData) return;
    
    setLoading(true);
    
    // Simulate API call
    setTimeout(() => {
      const newState = {
        ...integrationsState,
        [activeModal]: { 
          status: 'connected', 
          configured: true, 
          data: formData // In a real app we might not store secrets in plain state/localStorage
        }
      };
      saveState(newState);
      setLoading(false);
      setActiveModal(null);
    }, 1500);
  };

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

      <div className="flex-1 overflow-y-auto p-10 relative">
        {/* Header */}
        <div className="mb-10 max-w-7xl mx-auto">
          <div className="flex items-center gap-2 text-aurora-cyan text-[10px] uppercase font-bold tracking-[0.2em] font-mono mb-2">
            <Webhook className="w-3 h-3" />
            External Ecosystem
          </div>
          <h1 className="text-4xl font-bold text-white tracking-tight mb-3">Service Marketplace</h1>
          <p className="text-gray-500 max-w-lg">
            Connect external tools and services to enhance your documentation workflow.
          </p>
        </div>

        {/* Available Integrations */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-7xl mx-auto">
          {Object.keys(integrationsState).map((key) => {
            const state = integrationsState[key];
            const info = STATIC_INFO[key];
            const isConnected = state.status === 'connected';

            return (
              <Card
                key={key}
                className="bg-[#15171B] border-white/[0.05] rounded-2xl p-6 hover:border-aurora-purple/30 transition-all duration-300 group"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${isConnected
                      ? 'bg-emerald-500/20 text-emerald-400'
                      : 'bg-slate-800 text-slate-400'
                      }`}>
                      {info.icon}
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-slate-50">{info.name}</h3>
                      <div className={`flex items-center gap-1.5 text-xs px-2 py-1 rounded-full ${isConnected
                        ? 'bg-emerald-500/10 text-emerald-300'
                        : 'bg-slate-700/50 text-slate-400'
                        }`}>
                        {isConnected ? (
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
                    {isConnected ? (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleDisconnect(key)}
                        className="border-slate-700 text-slate-300 hover:bg-red-500/10 hover:text-red-400 hover:border-red-500/50"
                      >
                        Disconnect
                      </Button>
                    ) : (
                      <Button
                        size="sm"
                        onClick={() => handleConnect(key)}
                        className="bg-gradient-to-r from-cyan-500 to-emerald-500 text-slate-950 hover:scale-105 transition-all duration-200"
                      >
                        <Plus className="w-4 h-4 mr-2" />
                        Connect
                      </Button>
                    )}
                  </div>
                </div>

                <p className="text-slate-400 text-sm mb-4">
                  {info.description}
                </p>

                <div className="pt-4 border-t border-slate-800/30">
                  <div className="flex items-center justify-between text-xs text-slate-500">
                    <span>Status: {isConnected ? 'Active' : 'Ready to connect'}</span>
                    <span className="flex items-center gap-1">
                      Docs
                      <ExternalLink className="w-3 h-3" />
                    </span>
                  </div>
                </div>
              </Card>
            );
          })}
        </div>

        {/* Integration Request - Kept for aesthetics but active */}
        <Card className="bg-gradient-to-br from-slate-900/30 to-slate-950/30 border border-slate-800/30 rounded-2xl p-8 mt-8 max-w-7xl mx-auto">
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
              className="bg-slate-800 text-white hover:bg-slate-700"
            >
              Request Integration
            </Button>
          </div>
        </Card>

        {/* Configuration Modal */}
        {activeModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
            <div className="bg-[#15171B] border border-slate-700 w-full max-w-md rounded-2xl p-6 shadow-2xl relative">
              <button 
                onClick={() => setActiveModal(null)}
                className="absolute top-4 right-4 text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
              
              <div className="flex items-center gap-4 mb-6">
                <div className="w-12 h-12 bg-slate-800 rounded-xl flex items-center justify-center text-slate-300">
                  {STATIC_INFO[activeModal].icon}
                </div>
                <div>
                  <h3 className="text-xl font-bold text-white">{STATIC_INFO[activeModal].modalTitle}</h3>
                  <p className="text-slate-400 text-sm">Configuration</p>
                </div>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    {STATIC_INFO[activeModal].modalDescription}
                  </label>
                  {/* Using standard input as fallback if UI component behaves unexpectedly, 
                      but attempting to import Input from components earlier */}
                  <input
                    type={STATIC_INFO[activeModal].inputType}
                    value={formData}
                    onChange={(e) => setFormData(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-aurora-cyan transition-colors"
                    placeholder={STATIC_INFO[activeModal].placeholder}
                    autoFocus
                  />
                </div>

                <div className="flex justify-end gap-3 mt-6">
                  <Button
                    variant="ghost"
                    onClick={() => setActiveModal(null)}
                    className="text-slate-400 hover:text-white"
                  >
                    Cancel
                  </Button>
                  <Button
                    onClick={handleSubmit}
                    disabled={!formData || loading}
                    className="bg-gradient-to-r from-cyan-500 to-emerald-500 text-slate-950"
                  >
                    {loading ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Connecting...
                      </>
                    ) : (
                      'Save Integration'
                    )}
                  </Button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
