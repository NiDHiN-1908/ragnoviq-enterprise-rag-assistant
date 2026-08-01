import { Link, useLocation } from 'react-router-dom';
import { Menu, X, MessageSquare, LayoutDashboard, Database, Sparkles, Activity } from 'lucide-react';
import { useState, useEffect } from 'react';
import api from '../services/api';

export default function Layout({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [apiConnected, setApiConnected] = useState(true);
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  useEffect(() => {
    const checkHealth = async () => {
      try {
        await api.get('/api/v1/health');
        setApiConnected(true);
      } catch {
        setApiConnected(false);
      }
    };
    checkHealth();
    const interval = setInterval(checkHealth, 15000);
    return () => clearInterval(interval);
  }, []);

  const navItems = [
    { path: '/', label: 'AI Chat', icon: MessageSquare },
    { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/sources', label: 'Sources', icon: Database },
  ];

  return (
    <div className="flex h-screen bg-[#0b0f19] text-gray-100 antialiased selection:bg-blue-500 selection:text-white">
      {/* Sidebar */}
      <aside className={`${
        sidebarOpen ? 'translate-x-0' : '-translate-x-full'
      } md:translate-x-0 transition-transform duration-300 ease-in-out fixed md:relative w-64 glass-panel border-r border-gray-800/60 p-6 h-screen z-40 flex flex-col justify-between`}>
        <div>
          {/* Brand Header */}
          <div className="mb-8 flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 via-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-blue-500/20">
              <Sparkles className="w-5 h-5 text-white animate-pulse" />
            </div>
            <div>
              <h1 className="text-xl font-extrabold tracking-tight gradient-text">
                RAGNoviq
              </h1>
              <p className="text-xs text-gray-400 font-medium">Enterprise RAG Platform</p>
            </div>
          </div>

          {/* Navigation Items */}
          <nav className="space-y-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              const active = isActive(item.path);
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={() => setSidebarOpen(false)}
                  className={`flex items-center gap-3 px-4 py-3 rounded-xl font-medium text-sm transition-all duration-200 ${
                    active
                      ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg shadow-blue-500/25 font-semibold'
                      : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800/50'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${active ? 'text-white' : 'text-gray-400'}`} />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Backend Connectivity Status Indicator */}
        <div className="pt-4 border-t border-gray-800/80">
          <div className="flex items-center justify-between px-3 py-2 rounded-lg bg-gray-900/60 border border-gray-800 text-xs">
            <div className="flex items-center gap-2">
              <span className="relative flex h-2 w-2">
                <span className={`animate-ping absolute inline-flex h-full w-full rounded-full ${apiConnected ? 'bg-emerald-400' : 'bg-rose-400'} opacity-75`}></span>
                <span className={`relative inline-flex rounded-full h-2 w-2 ${apiConnected ? 'bg-emerald-500' : 'bg-rose-500'}`}></span>
              </span>
              <span className="text-gray-300 font-medium">
                {apiConnected ? 'API Connected' : 'API Offline'}
              </span>
            </div>
            <Activity className={`w-3.5 h-3.5 ${apiConnected ? 'text-emerald-400' : 'text-rose-400'}`} />
          </div>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-hidden flex flex-col relative">
        {/* Mobile Header */}
        <header className="bg-gray-900/80 backdrop-blur-md border-b border-gray-800 p-4 flex items-center justify-between md:hidden z-20">
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-blue-400" />
            <h1 className="font-extrabold text-lg gradient-text">RAGNoviq</h1>
          </div>
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 hover:bg-gray-800/80 rounded-lg text-gray-300"
          >
            {sidebarOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </header>

        {/* Page Content */}
        <div className="flex-1 overflow-auto bg-[#0b0f19]">
          {children}
        </div>
      </main>

      {/* Mobile Backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/60 backdrop-blur-sm md:hidden z-30 animate-fade-in"
          onClick={() => setSidebarOpen(false)}
        />
      )}
    </div>
  );
}
