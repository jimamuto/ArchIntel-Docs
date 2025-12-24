import Head from 'next/head';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { useState, useEffect } from 'react';
import { getSession } from '@/lib/auth_utils';
import { motion, useScroll, useTransform, useSpring, AnimatePresence } from 'framer-motion';
import {
  ArrowRight,
  Terminal,
  GitBranch,
  Shield,
  Zap,
  Search,
  Code2,
  Cpu,
  Database,
  Layers,
  Activity,
  Github,
  Globe,
  Check,
  Hexagon,
  Sparkles,
  Command,
  Bell
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';

// --- GitHub Style Background ---
const EnhancedBackground = () => (
  <div className="absolute inset-0 -z-10 overflow-hidden pointer-events-none">
    <div className="absolute inset-0 bg-[#060608]" />

    {/* Radial Aurora Glows */}
    <div className="github-glow top-[-200px] left-[-200px] opacity-40 scale-150" />
    <div className="github-glow bottom-[-100px] right-[-100px] opacity-20 scale-125 bg-aurora-cyan" />

    {/* Grid / Lines */}
    <div
      className="absolute inset-0 opacity-[0.05]"
      style={{
        backgroundImage: `linear-gradient(to right, #444 1px, transparent 1px), linear-gradient(to bottom, #444 1px, transparent 1px)`,
        backgroundSize: '80px 80px',
        maskImage: 'radial-gradient(circle at center, black, transparent 80%)'
      }}
    />

    {/* Vertical Connector Line (GitHub Style) */}
    <div className="absolute left-1/2 top-0 bottom-0 w-px bg-gradient-to-b from-transparent via-white/10 to-transparent" />
  </div>
);

// --- Code Diff Mockup ---
const DiffMockup = () => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    whileInView={{ opacity: 1, y: 0 }}
    viewport={{ once: true }}
    className="w-full max-w-lg rounded-2xl overflow-hidden border border-white/10 bg-[#0d1117] shadow-2xl font-mono text-xs"
  >
    <div className="px-4 py-2 border-b border-white/5 bg-white/[0.02] flex items-center justify-between">
      <div className="flex gap-1.5">
        <div className="w-2.5 h-2.5 rounded-full bg-red-500/50" />
        <div className="w-2.5 h-2.5 rounded-full bg-yellow-500/50" />
        <div className="w-2.5 h-2.5 rounded-full bg-green-500/50" />
      </div>
      <span className="text-gray-500">ast_parser.rs — 74% optimized</span>
    </div>
    <div className="p-4 space-y-1">
      <div className="flex bg-red-500/10 -mx-4 px-4"><span className="w-4 text-red-500">-</span><span className="text-gray-500">fn legacy_handler(req: Request) {'{'}</span></div>
      <div className="flex bg-green-500/10 -mx-4 px-4"><span className="w-4 text-green-500">+</span><span className="text-gray-300">fn intelligent_proxy(req: Request) {'{'}</span></div>
      <div className="flex px-4"><span className="w-4"> </span><span className="text-gray-500">  // Inferred architectural node</span></div>
      <div className="flex px-4"><span className="w-4"> </span><span className="text-aurora-purple">  let</span> <span className="text-white">ctx = Context::analyze(req);</span></div>
    </div>
  </motion.div>
);

export default function LandingPage() {
  const router = useRouter();
  const [isScrolled, setIsScrolled] = useState(false);
  const [showWaitlist, setShowWaitlist] = useState(false);
  const [email, setEmail] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isJoined, setIsJoined] = useState(false);
  const [user, setUser] = useState(null);

  useEffect(() => {
    async function checkUser() {
      const session = await getSession();
      if (session) {
        setUser(session.user);
        router.push('/projects');
      }
    }
    checkUser();
  }, [router]);

  const handleWaitlist = (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    // Simulate API call
    setTimeout(() => {
      setIsSubmitting(false);
      setIsJoined(true);
      setTimeout(() => setShowWaitlist(false), 2000);
    }, 1500);
  };

  useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 50);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <div className="min-h-screen bg-[#0d1117] text-white selection:bg-aurora-purple/30 font-sans overflow-x-hidden">
      <Head>
        <title>ArchIntel | The Future of Code Intelligence</title>
        <meta name="description" content="AI-powered architectural analysis and documentation." />
      </Head>

      <EnhancedBackground />

      {/* Navigation */}
      <nav className={cn(
        "fixed top-0 w-full z-50 transition-all duration-500 border-b",
        isScrolled ? "bg-black/60 backdrop-blur-xl border-white/[0.08] py-4" : "bg-transparent border-transparent py-8"
      )}>
        <div className="container mx-auto px-6 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Hexagon className="w-8 h-8 text-aurora-purple fill-aurora-purple/10" />
            <span className="font-bold text-xl tracking-tight font-mono">ArchIntel</span>
          </div>
          <div className="hidden lg:flex items-center gap-8 text-sm font-medium text-gray-400">
            <Link href="#features" className="hover:text-white transition-colors">OS Analysis</Link>
            <Link href="#architecture" className="hover:text-white transition-colors">Knowledge Graph</Link>
            <Link href="/docs" className="hover:text-white transition-colors">Docs Explorer</Link>
          </div>
          <div className="flex items-center gap-4">
            <button
              onClick={() => setShowWaitlist(true)}
              className="text-gray-400 hover:text-white transition-colors text-sm font-medium mr-4 hidden sm:block"
            >
              Waitlist
            </button>
            <Link href="/projects">
              <Button className="bg-aurora-purple hover:bg-aurora-purple/80 text-white rounded-full px-6 py-5 font-bold text-sm shadow-glow transition-all hover:scale-105">
                Get Started
              </Button>
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative pt-48 pb-32 flex flex-col items-center text-center px-6">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 1.2, ease: "easeOut" }}
          className="absolute top-20 w-[800px] h-[800px] pointer-events-none opacity-40 blur-[150px] bg-aurora-purple/20 rounded-full"
        />

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="z-10"
        >
          <div className="inline-flex items-center gap-2 px-4 py-1 rounded-full border border-white/10 bg-white/5 text-[10px] font-bold uppercase tracking-[0.2em] mb-10 text-aurora-cyan shadow-inner">
            <Sparkles className="w-3 h-3" />
            Next-Gen Codebase Mapping
          </div>

          <h1 className="text-massive mb-8">
            The future of <br />
            <span className="aurora-gradient-text">code intelligence.</span>
          </h1>

          <p className="text-xl text-gray-400 max-w-2xl mx-auto mb-12 leading-relaxed font-medium">
            ArchIntel transforms your chaotic repositories into high-fidelity knowledge graphs. Understand every relationship, dependency, and design pattern in seconds.
          </p>

          <div className="flex flex-wrap items-center justify-center gap-6">
            <Link href="/signup">
              <Button size="lg" className="h-14 px-10 rounded-full bg-aurora-purple hover:bg-aurora-purple/80 text-white font-black text-lg shadow-glow">
                Start Analysis
              </Button>
            </Link>
            <Button size="lg" variant="outline" className="h-14 px-10 rounded-full border-white/10 bg-white/5 hover:bg-white/10 text-white gap-3 group transition-all">
              <Command className="w-5 h-5 text-gray-500 group-hover:text-white" />
              Documentation
            </Button>
          </div>
        </motion.div>

        {/* Intelligence Node Visualization */}
        <motion.div
          initial={{ opacity: 0, y: 100 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1.5, delay: 0.4 }}
          className="mt-24 relative group"
        >
          <div className="absolute inset-0 bg-aurora-purple/20 blur-[100px] rounded-full group-hover:bg-aurora-purple/30 transition-all duration-1000" />
          <img
            src="/images/hero-node.png"
            alt="Architectural node"
            className="w-full max-w-4xl relative z-10 drop-shadow-[0_0_50px_rgba(178,110,247,0.3)] select-none pointer-events-none"
          />
          {/* Floating HUD elements */}
          <motion.div
            animate={{ y: [0, -10, 0] }}
            transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
            className="absolute -right-10 top-20 p-4 aurora-glass rounded-2xl z-20 hidden lg:block"
          >
            <div className="flex items-center gap-3">
              <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
              <span className="text-[10px] uppercase font-black text-white/70">Scanning Modules</span>
            </div>
          </motion.div>
        </motion.div>
      </section>

      {/* Bento Grid Section */}
      <section id="features" className="py-32 relative px-6">
        <div className="container mx-auto">
          <div className="mb-20 text-center lg:text-left">
            <h2 className="text-4xl md:text-5xl font-black tracking-tighter mb-4">Engineered for Devs.</h2>
            <p className="text-gray-500 max-w-xl text-lg font-medium">ArchIntel doesn't just read code; it understands the engineering intent behind it.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 md:grid-rows-2 gap-6 min-h-[700px]">
            {/* Main Feature - AST Analysis */}
            <div className="bento-card md:col-span-2 md:row-span-2 flex flex-col justify-between group">
              <div>
                <div className="w-12 h-12 rounded-2xl bg-aurora-purple/10 flex items-center justify-center mb-6">
                  <Layers className="w-6 h-6 text-aurora-purple" />
                </div>
                <h3 className="text-2xl font-black mb-4 group-hover:text-aurora-purple transition-colors">AST Deep-Dive Analysis</h3>
                <p className="text-gray-400 leading-relaxed text-sm">
                  We parse the raw Abstract Syntax Tree of your project to detect architectural patterns, design smells, and hidden dependencies that traditional scanners miss.
                </p>
              </div>
              <div className="mt-8 pt-8 border-t border-white/5">
                <DiffMockup />
              </div>
            </div>

            {/* Feature 2 - Intelligence Node */}
            <div className="bento-card md:col-span-2 group">
              <div className="flex items-start justify-between">
                <div className="max-w-[180px]">
                  <h3 className="text-xl font-black mb-2">The Oracle Search</h3>
                  <p className="text-xs text-gray-500 leading-relaxed">Ask "Where is auth handled?" and get a structural graph response instead of text results.</p>
                </div>
                <div className="w-24 h-24 rounded-full bg-aurora-cyan/10 flex items-center justify-center group-hover:scale-110 transition-transform">
                  <Search className="w-10 h-10 text-aurora-cyan" />
                </div>
              </div>
            </div>

            {/* Feature 3 - Live Sync */}
            <div className="bento-card group">
              <div className="h-full flex flex-col justify-between">
                <Activity className="w-8 h-8 text-orange-500" />
                <div>
                  <h3 className="text-lg font-black mb-1">Mirror Sync</h3>
                  <p className="text-[10px] text-gray-400">Real-time GitHub webhooks.</p>
                </div>
              </div>
            </div>

            {/* Feature 4 - Export */}
            <div className="bento-card group h-full">
              <div className="h-full flex flex-col justify-between">
                <Database className="w-8 h-8 text-aurora-pink" />
                <div>
                  <h3 className="text-lg font-black mb-1">System Export</h3>
                  <p className="text-[10px] text-gray-400">PDF, Markdown & JSON.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Final Section - GitHub Style Gradient Bar */}
      <section className="py-40 relative flex flex-col items-center justify-center text-center overflow-hidden">
        <div className="absolute top-0 w-[400px] h-[400px] bg-aurora-purple/30 blur-[150px] opacity-20" />
        <h2 className="text-5xl md:text-7xl font-black tracking-tighter mb-10 z-10 leading-[0.9]">Ready to see <br />the full graph?</h2>
        <Link href="/signup" className="z-10 mt-6">
          <Button size="lg" className="h-16 px-14 rounded-full bg-aurora-purple hover:bg-aurora-purple/80 text-white font-black text-xl shadow-glow transition-all hover:scale-105">
            Start Free Trial
          </Button>
        </Link>
        <button
          onClick={() => setShowWaitlist(true)}
          className="mt-8 text-aurora-cyan hover:text-white transition-colors font-mono text-xs uppercase tracking-[0.3em] font-bold z-10"
        >
          Join Exclusive Beta Waitlist →
        </button>
        <p className="mt-8 text-gray-600 font-mono text-xs uppercase tracking-widest z-10">Trusted by modern engineering teams.</p>
      </section>

      {/* Waitlist Modal */}
      <AnimatePresence>
        {showWaitlist && (
          <div className="fixed inset-0 z-[100] flex items-center justify-center p-6">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setShowWaitlist(false)}
              className="absolute inset-0 bg-black/90 backdrop-blur-md"
            />
            <motion.div
              initial={{ scale: 0.9, opacity: 0, y: 20 }}
              animate={{ scale: 1, opacity: 1, y: 0 }}
              exit={{ scale: 0.9, opacity: 0, y: 20 }}
              className="w-full max-w-lg bg-[#0d1117] border border-white/10 rounded-[2rem] p-10 relative z-10 shadow-3xl overflow-hidden"
            >
              <div className="absolute top-0 inset-x-0 h-1 bg-gradient-to-r from-aurora-purple via-aurora-cyan to-aurora-pink" />

              <div className="text-center">
                <div className="w-16 h-16 rounded-2xl bg-aurora-purple/10 border border-aurora-purple/20 flex items-center justify-center mx-auto mb-6">
                  <Bell className="w-8 h-8 text-aurora-purple animate-pulse" />
                </div>
                <h2 className="text-3xl font-black tracking-tighter text-white mb-2">Secure your spot.</h2>
                <p className="text-gray-400 mb-8 font-medium">Join 500+ engineers waiting to unlock structural codebase intelligence.</p>

                {isJoined ? (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="p-6 rounded-2xl bg-green-500/10 border border-green-500/20 text-green-500 font-bold"
                  >
                    You're on the list! We'll reach out soon.
                  </motion.div>
                ) : (
                  <form onSubmit={handleWaitlist} className="space-y-4">
                    <input
                      required
                      type="email"
                      placeholder="name@company.com"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="w-full h-14 bg-black border border-white/10 rounded-2xl px-6 font-medium text-white focus:outline-none focus:border-aurora-purple/50 transition-all font-mono"
                    />
                    <Button
                      type="submit"
                      disabled={isSubmitting}
                      className="w-full h-14 bg-aurora-purple hover:bg-aurora-purple/80 text-white font-black text-lg rounded-2xl shadow-glow"
                    >
                      {isSubmitting ? "Processing..." : "Join Phase 1 Beta"}
                    </Button>
                  </form>
                )}

                <p className="mt-8 text-[10px] text-gray-600 font-mono uppercase tracking-widest">
                  Zero Spam. Only Architectural Updates.
                </p>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* Footer */}
      <footer className="py-20 border-t border-white/5 bg-[#060608] px-6">
        <div className="container mx-auto flex flex-col md:flex-row justify-between items-center gap-8">
          <div className="flex items-center gap-3">
            <Hexagon className="w-6 h-6 text-gray-700" />
            <span className="font-bold text-gray-600 font-mono text-sm tracking-widest uppercase">ArchIntel Engine</span>
          </div>
          <div className="flex items-center gap-10 text-xs font-mono text-gray-600 uppercase tracking-tighter">
            <span>© 2025 Neural Fabric</span>
            <Link href="#" className="hover:text-white transition-colors">Privacy</Link>
            <Link href="#" className="hover:text-white transition-colors">Security</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
