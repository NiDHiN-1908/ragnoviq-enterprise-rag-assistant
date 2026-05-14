import { Link, useLocation } from 'react-router-dom';
import { Menu, X, Sun, Moon } from 'lucide-react';
import { useState } from 'react';

export default function Layout({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [darkMode, setDarkMode] = useState(true);
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  return (
    <div className="flex h-screen bg-gray-950 text-gray-100">
      {/* Sidebar */}
      <aside className={`${
        sidebarOpen ? 'block' : 'hidden'
      } md:block w-64 bg-gray-900 border-r border-gray-800 p-6 fixed md:relative md:w-64 h-screen z-40`}>
        <div className="mb-8">
          <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
            RAGNoviq
          </h1>
          <p className="text-sm text-gray-400 mt-1">Enterprise RAG Assistant</p>
        </div>

        <nav className="space-y-3">
          <Link
            to="/"
            className={`block px-4 py-3 rounded-lg transition ${
              isActive('/')
                ? 'bg-blue-600 text-white'
                : 'text-gray-400 hover:bg-gray-800'
            }`}
          >
            Chat
          </Link>
          <Link
            to="/dashboard"
            className={`block px-4 py-3 rounded-lg transition ${
              isActive('/dashboard')
                ? 'bg-blue-600 text-white'
                : 'text-gray-400 hover:bg-gray-800'
            }`}
          >
            Dashboard
          </Link>
          <Link
            to="/sources"
            className={`block px-4 py-3 rounded-lg transition ${
              isActive('/sources')
                ? 'bg-blue-600 text-white'
                : 'text-gray-400 hover:bg-gray-800'
            }`}
          >
            Sources
          </Link>
        </nav>

        <div className="absolute bottom-6 left-6 right-6">
          <button
            onClick={() => setDarkMode(!darkMode)}
            className="w-full px-4 py-3 bg-gray-800 hover:bg-gray-700 rounded-lg flex items-center justify-center gap-2"
          >
            {darkMode ? (
              <Sun className="w-4 h-4" />
            ) : (
              <Moon className="w-4 h-4" />
            )}
            <span className="text-sm">{darkMode ? 'Light' : 'Dark'}</span>
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-auto flex flex-col">
        {/* Top bar */}
        <header className="bg-gray-900 border-b border-gray-800 p-4 flex items-center justify-between md:hidden">
          <h1 className="font-bold text-xl">RAGNoviq</h1>
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 hover:bg-gray-800 rounded-lg"
          >
            {sidebarOpen ? (
              <X className="w-6 h-6" />
            ) : (
              <Menu className="w-6 h-6" />
            )}
          </button>
        </header>

        {/* Page content */}
        {children}
      </main>

      {/* Sidebar overlay on mobile */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 md:hidden z-30"
          onClick={() => setSidebarOpen(false)}
        />
      )}
    </div>
  );
}
