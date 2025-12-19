import Link from 'next/link';
import { useState, useEffect } from 'react';
import { Button } from '../components/ui/button';
import { Card } from '../components/ui/card';

export default function Home() {
  const [isScrolled, setIsScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <div className="min-h-screen bg-slate-950">
      {/* Header/Navigation */}
      <header className={`fixed top-0 w-full z-50 transition-all duration-300 ${
        isScrolled
          ? 'bg-slate-950/80 backdrop-blur-md border-b border-slate-800/50'
          : 'bg-transparent'
      }`}>
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-br from-emerald-500 to-emerald-400 rounded-lg flex items-center justify-center">
                <span className="text-slate-950 text-sm font-bold">A</span>
              </div>
              <span className="text-xl font-bold text-slate-50">ArchIntel Docs</span>
            </div>

            <nav className="hidden md:flex items-center gap-8">
              <a href="#product" className="text-sm text-slate-300 hover:text-slate-50 transition-colors">Product</a>
              <a href="#how-it-works" className="text-sm text-slate-300 hover:text-slate-50 transition-colors">How it works</a>
              <a href="#features" className="text-sm text-slate-300 hover:text-slate-50 transition-colors">Features</a>
              <Link href="/docs">
                <Button variant="outline" size="sm" className="border-slate-700 text-slate-300 hover:bg-slate-800">
                  Docs
                </Button>
              </Link>
              <Link href="/projects">
                <Button size="sm" className="bg-emerald-500 hover:bg-emerald-400 text-slate-950">
                  Get started
                </Button>
              </Link>
            </nav>

            {/* Mobile menu button */}
            <Button variant="ghost" size="sm" className="md:hidden">
              <span className="sr-only">Menu</span>
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </Button>
          </div>
        </div>
      </header>

      <main>
        {/* Hero Section */}
        <section className="relative pt-32 pb-16 sm:pt-40 sm:pb-20">
          <div className="absolute inset-0 opacity-20">
            <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl"></div>
            <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl"></div>
          </div>

          <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
              <div>
                <h1 className="text-3xl sm:text-4xl font-semibold tracking-tight text-slate-50 mb-6">
                  Architecture-aware AI documentation for complex codebases
                </h1>
                <p className="text-base text-slate-300 mb-8 leading-relaxed">
                  Transform your codebase into living, intelligent documentation. Understand how your code evolved, capture team rationale, and keep docs synchronized with every change.
                </p>
                <div className="flex flex-col sm:flex-row gap-4">
                  <Link href="/projects">
                    <Button className="w-full sm:w-auto bg-emerald-500 hover:bg-emerald-400 text-slate-950 px-8 py-3 text-base font-medium shadow-lg shadow-emerald-500/25 hover:shadow-emerald-500/40 transition-all duration-300 hover:scale-[1.02]">
                      Get started
                    </Button>
                  </Link>
                  <Button variant="outline" className="w-full sm:w-auto border-slate-700 text-slate-300 hover:bg-slate-800 px-8 py-3">
                    View live demo
                  </Button>
                </div>
              </div>

              {/* Hero Visual */}
              <div className="lg:ml-auto">
                <div className="relative">
                  <div className="bg-slate-900/60 backdrop-blur-sm border border-slate-800/50 rounded-xl p-6 shadow-2xl">
                    <div className="space-y-4">
                      {/* Mock dashboard preview */}
                      <div className="flex items-center gap-3 mb-4">
                        <div className="w-3 h-3 bg-emerald-400 rounded-full"></div>
                        <span className="text-sm text-slate-300">ArchIntel Docs Dashboard</span>
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="bg-slate-800/50 rounded-lg p-3">
                          <div className="w-8 h-8 bg-emerald-500/20 rounded mb-2"></div>
                          <div className="h-2 bg-slate-700 rounded mb-1"></div>
                          <div className="h-2 bg-slate-700 rounded w-2/3"></div>
                        </div>
                        <div className="bg-slate-800/50 rounded-lg p-3">
                          <div className="w-8 h-8 bg-cyan-500/20 rounded mb-2"></div>
                          <div className="h-2 bg-slate-700 rounded mb-1"></div>
                          <div className="h-2 bg-slate-700 rounded w-3/4"></div>
                        </div>
                      </div>
                      <div className="bg-slate-800/50 rounded-lg p-4">
                        <div className="flex items-center gap-2 mb-2">
                          <span className="text-xs text-slate-400">📄</span>
                          <span className="text-sm text-slate-300">Documentation</span>
                        </div>
                        <div className="h-2 bg-slate-700 rounded mb-1"></div>
                        <div className="h-2 bg-slate-700 rounded w-4/5"></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Key Benefits / Value Props */}
        <section className="py-16 bg-slate-950/95">
          <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
              <h2 className="text-xl font-semibold text-slate-50 mb-4">Why teams choose ArchIntel</h2>
              <p className="text-slate-300 max-w-2xl mx-auto">Built for modern engineering teams who need documentation that stays current with their evolving codebase.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <Card className="bg-slate-900/60 backdrop-blur-sm border-slate-800/50 p-6 hover:bg-slate-900/80 hover:border-emerald-500/30 transition-all duration-300">
                <div className="w-12 h-12 bg-emerald-500/20 rounded-lg flex items-center justify-center mb-4">
                  <span className="text-emerald-400 text-xl">🏗️</span>
                </div>
                <h3 className="text-sm font-semibold text-slate-50 mb-2">Understands Architecture</h3>
                <p className="text-xs text-slate-400">Deep analysis of code structure, dependencies, and design patterns.</p>
              </Card>

              <Card className="bg-slate-900/60 backdrop-blur-sm border-slate-800/50 p-6 hover:bg-slate-900/80 hover:border-emerald-500/30 transition-all duration-300">
                <div className="w-12 h-12 bg-emerald-500/20 rounded-lg flex items-center justify-center mb-4">
                  <span className="text-emerald-400 text-xl">📈</span>
                </div>
                <h3 className="text-sm font-semibold text-slate-50 mb-2">Tracks Evolution</h3>
                <p className="text-xs text-slate-400">Git history integration shows how and why code changed over time.</p>
              </Card>

              <Card className="bg-slate-900/60 backdrop-blur-sm border-slate-800/50 p-6 hover:bg-slate-900/80 hover:border-emerald-500/30 transition-all duration-300">
                <div className="w-12 h-12 bg-emerald-500/20 rounded-lg flex items-center justify-center mb-4">
                  <span className="text-emerald-400 text-xl">💬</span>
                </div>
                <h3 className="text-sm font-semibold text-slate-50 mb-2">Captures Rationale</h3>
                <p className="text-xs text-slate-400">Preserves team discussions, decisions, and architectural reasoning.</p>
              </Card>

              <Card className="bg-slate-900/60 backdrop-blur-sm border-slate-800/50 p-6 hover:bg-slate-900/80 hover:border-emerald-500/30 transition-all duration-300">
                <div className="w-12 h-12 bg-emerald-500/20 rounded-lg flex items-center justify-center mb-4">
                  <span className="text-emerald-400 text-xl">🔄</span>
                </div>
                <h3 className="text-sm font-semibold text-slate-50 mb-2">Stays in Sync</h3>
                <p className="text-xs text-slate-400">CI/CD integration keeps documentation current with every deployment.</p>
              </Card>
            </div>
          </div>
        </section>

        {/* How It Works */}
        <section className="py-16 bg-slate-950">
          <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
              <h2 className="text-xl font-semibold text-slate-50 mb-4">How it works</h2>
              <p className="text-slate-300">Four simple steps to transform your codebase into intelligent documentation.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
              <div className="text-center">
                <div className="w-16 h-16 bg-emerald-500/20 rounded-full flex items-center justify-center mx-auto mb-4 text-2xl">1</div>
                <h3 className="text-sm font-semibold text-slate-50 mb-2">Connect Repository</h3>
                <p className="text-xs text-slate-400">Link your Git repository with a single command or API call.</p>
              </div>

              <div className="text-center">
                <div className="w-16 h-16 bg-emerald-500/20 rounded-full flex items-center justify-center mx-auto mb-4 text-2xl">2</div>
                <h3 className="text-sm font-semibold text-slate-50 mb-2">AI Analysis</h3>
                <p className="text-xs text-slate-400">Deep learning models analyze code structure, patterns, and evolution.</p>
              </div>

              <div className="text-center">
                <div className="w-16 h-16 bg-emerald-500/20 rounded-full flex items-center justify-center mx-auto mb-4 text-2xl">3</div>
                <h3 className="text-sm font-semibold text-slate-50 mb-2">Generate Docs</h3>
                <p className="text-xs text-slate-400">Create comprehensive documentation with context and rationale.</p>
              </div>

              <div className="text-center">
                <div className="w-16 h-16 bg-emerald-500/20 rounded-full flex items-center justify-center mx-auto mb-4 text-2xl">4</div>
                <h3 className="text-sm font-semibold text-slate-50 mb-2">Ask Questions</h3>
                <p className="text-xs text-slate-400">Interactive Q&A system answers questions about your codebase.</p>
              </div>
            </div>
          </div>
        </section>

        {/* Social Proof / Trust */}
        <section className="py-16 bg-slate-950/95">
          <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
              <h2 className="text-xl font-semibold text-slate-50 mb-4">Trusted by engineering teams</h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
              <Card className="bg-slate-900/60 backdrop-blur-sm border-slate-800/50 p-6">
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 bg-slate-800 rounded-full flex items-center justify-center">
                    <span className="text-slate-400 text-lg">👤</span>
                  </div>
                  <div>
                    <p className="text-sm text-slate-300 mb-4 italic">
                      "ArchIntel transformed how our team documents complex systems. The AI understands our architecture better than any human could."
                    </p>
                    <div className="text-xs text-slate-500">
                      <div className="font-medium text-slate-400">Sarah Chen</div>
                      <div>Engineering Lead, TechCorp</div>
                    </div>
                  </div>
                </div>
              </Card>

              <Card className="bg-slate-900/60 backdrop-blur-sm border-slate-800/50 p-6">
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 bg-slate-800 rounded-full flex items-center justify-center">
                    <span className="text-slate-400 text-lg">👤</span>
                  </div>
                  <div>
                    <p className="text-sm text-slate-300 mb-4 italic">
                      "Finally, documentation that stays current. No more outdated wikis or missing context about why decisions were made."
                    </p>
                    <div className="text-xs text-slate-500">
                      <div className="font-medium text-slate-400">Marcus Rodriguez</div>
                      <div>Senior Developer, StartupXYZ</div>
                    </div>
                  </div>
                </div>
              </Card>
            </div>
          </div>
        </section>

        {/* Feature Highlights */}
        <section className="py-16 bg-slate-950">
          <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
              <div>
                <h2 className="text-xl font-semibold text-slate-50 mb-4">Interactive Documentation Explorer</h2>
                <p className="text-slate-300 mb-6">
                  Browse your codebase with an intuitive file tree, view AI-generated documentation for any component, and understand how your code evolved through comprehensive history tracking.
                </p>
                <ul className="space-y-2 text-sm text-slate-400">
                  <li>• Real-time code analysis and insights</li>
                  <li>• Interactive file tree navigation</li>
                  <li>• Context-aware documentation generation</li>
                  <li>• Git history integration</li>
                </ul>
              </div>
              <div className="lg:ml-auto">
                <Card className="bg-slate-900/60 backdrop-blur-sm border-slate-800/50 p-6 max-w-md">
                  <div className="space-y-4">
                    <div className="flex items-center gap-2">
                      <span className="text-emerald-400">📁</span>
                      <span className="text-sm text-slate-300">src/components</span>
                    </div>
                    <div className="bg-slate-800/50 rounded p-3">
                      <div className="text-xs text-slate-400 mb-2">Documentation</div>
                      <div className="text-sm text-slate-300">This component handles user authentication flow with OAuth integration...</div>
                    </div>
                    <div className="flex items-center gap-2 text-xs text-slate-500">
                      <span>📈</span>
                      <span>12 commits • 3 contributors</span>
                    </div>
                  </div>
                </Card>
              </div>
            </div>
          </div>
        </section>

        {/* Final CTA */}
        <section className="py-16 bg-gradient-to-r from-emerald-500/5 via-transparent to-cyan-500/5">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h2 className="text-xl font-semibold text-slate-50 mb-4">Ready to transform your documentation?</h2>
            <p className="text-slate-300 mb-8">Join engineering teams who have already revolutionized how they document and understand their codebases.</p>
            <Link href="/projects">
              <Button className="bg-emerald-500 hover:bg-emerald-400 text-slate-950 px-8 py-3 text-base font-medium shadow-lg shadow-emerald-500/25 hover:shadow-emerald-500/40 transition-all duration-300 hover:scale-[1.02]">
                Get started for free
              </Button>
            </Link>
            <p className="text-xs text-slate-500 mt-4">No credit card required • 14-day free trial</p>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-slate-950 border-t border-slate-900 py-12">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <div className="w-8 h-8 bg-gradient-to-br from-emerald-500 to-emerald-400 rounded-lg flex items-center justify-center">
                  <span className="text-slate-950 text-sm font-bold">A</span>
                </div>
                <span className="text-lg font-bold text-slate-50">ArchIntel Docs</span>
              </div>
              <p className="text-xs text-slate-500 leading-relaxed">
                AI-powered documentation that understands your codebase architecture, evolution, and team context.
              </p>
            </div>

            <div>
              <h3 className="text-sm font-semibold text-slate-50 mb-4">Product</h3>
              <ul className="space-y-2 text-xs text-slate-500">
                <li><a href="#" className="hover:text-slate-300 transition-colors">Features</a></li>
                <li><a href="#" className="hover:text-slate-300 transition-colors">Pricing</a></li>
                <li><a href="#" className="hover:text-slate-300 transition-colors">Integrations</a></li>
                <li><a href="#" className="hover:text-slate-300 transition-colors">API</a></li>
              </ul>
            </div>

            <div>
              <h3 className="text-sm font-semibold text-slate-50 mb-4">Resources</h3>
              <ul className="space-y-2 text-xs text-slate-500">
                <li><a href="#" className="hover:text-slate-300 transition-colors">Documentation</a></li>
                <li><a href="#" className="hover:text-slate-300 transition-colors">Help Center</a></li>
                <li><a href="#" className="hover:text-slate-300 transition-colors">Community</a></li>
                <li><a href="#" className="hover:text-slate-300 transition-colors">Blog</a></li>
              </ul>
            </div>

            <div>
              <h3 className="text-sm font-semibold text-slate-50 mb-4">Company</h3>
              <ul className="space-y-2 text-xs text-slate-500">
                <li><a href="#" className="hover:text-slate-300 transition-colors">About</a></li>
                <li><a href="#" className="hover:text-slate-300 transition-colors">Careers</a></li>
                <li><a href="#" className="hover:text-slate-300 transition-colors">Contact</a></li>
                <li><a href="#" className="hover:text-slate-300 transition-colors">Privacy</a></li>
              </ul>
            </div>
          </div>

          <div className="border-t border-slate-900 mt-8 pt-8 flex flex-col sm:flex-row justify-between items-center">
            <p className="text-xs text-slate-500">© 2025 ArchIntel Docs. All rights reserved.</p>
            <div className="flex items-center gap-4 mt-4 sm:mt-0">
              <a href="#" className="text-xs text-slate-500 hover:text-slate-300 transition-colors">Terms</a>
              <a href="#" className="text-xs text-slate-500 hover:text-slate-300 transition-colors">Privacy</a>
              <a href="#" className="text-xs text-slate-500 hover:text-slate-300 transition-colors">Cookies</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
