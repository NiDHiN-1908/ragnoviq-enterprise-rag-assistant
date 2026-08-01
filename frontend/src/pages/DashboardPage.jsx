import { useEffect, useState } from 'react';
import { Plus, RefreshCw, AlertCircle, Search, Globe, CheckCircle2, Clock, Layers, Sparkles } from 'lucide-react';
import api from '../services/api';
import WebsiteForm from '../components/WebsiteForm';
import WebsiteCard from '../components/WebsiteCard';
import { useStore } from '../store';

export default function DashboardPage() {
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [error, setError] = useState(null);
  const { websites, setWebsites } = useStore();

  useEffect(() => {
    fetchWebsites();
  }, []);

  const fetchWebsites = async () => {
    setLoading(true);
    try {
      const response = await api.get('/api/v1/ingest/websites');
      setWebsites(response.data.websites || []);
      setError(null);
    } catch (err) {
      const errorMsg = (err.code === 'ERR_NETWORK' || !err.response)
        ? 'Backend API is offline. Make sure to run backend server at http://localhost:8000.'
        : 'Failed to load websites';
      setError(errorMsg);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddWebsite = async (url) => {
    try {
      await api.post('/api/v1/ingest/website', { url });
      setShowForm(false);
      fetchWebsites();
    } catch (err) {
      const detail = err.response?.data?.detail;
      const msg = typeof detail === 'string' ? detail : (Array.isArray(detail) ? detail[0]?.msg : 'Failed to add website');
      setError(msg || 'Failed to add website');
    }
  };

  const handleDelete = async (websiteId) => {
    if (!confirm('Are you sure you want to delete this website? All stored embeddings will be removed.')) return;

    try {
      await api.delete(`/api/v1/ingest/website/${websiteId}`);
      fetchWebsites();
    } catch (err) {
      setError('Failed to delete website');
    }
  };

  const filteredWebsites = websites.filter(w =>
    (w.title || w.url).toLowerCase().includes(searchQuery.toLowerCase()) ||
    w.url.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const indexedCount = websites.filter(w => w.status === 'indexed').length;
  const indexingCount = websites.filter(w => w.status === 'indexing' || w.status === 'pending').length;
  const totalChunks = websites.reduce((acc, curr) => acc + (curr.chunks ?? curr.total_chunks ?? 0), 0);

  return (
    <div className="max-w-7xl mx-auto p-6 md:p-8 space-y-8 animate-fade-in">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-gray-100 flex items-center gap-3">
            <span>Knowledge Base Dashboard</span>
            <span className="text-xs px-2.5 py-1 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20 font-semibold">
              Live Index
            </span>
          </h1>
          <p className="text-sm text-gray-400 mt-1">
            Manage crawled domain sources, vector chunking, and background ingestion tasks.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={fetchWebsites}
            disabled={loading}
            className="px-4 py-2.5 bg-gray-800/80 hover:bg-gray-800 text-gray-300 font-semibold text-sm rounded-xl border border-gray-700/80 transition-all flex items-center gap-2"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-blue-400' : ''}`} />
            <span>Refresh</span>
          </button>

          <button
            onClick={() => setShowForm(true)}
            className="px-5 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-semibold text-sm rounded-xl shadow-lg shadow-blue-500/20 transition-all flex items-center gap-2"
          >
            <Plus className="w-4 h-4" />
            <span>Add Website</span>
          </button>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="p-4 bg-rose-500/10 border border-rose-500/30 text-rose-200 rounded-2xl flex items-center gap-3 text-sm animate-slide-up">
          <AlertCircle className="w-5 h-5 text-rose-400 flex-shrink-0" />
          <p className="flex-1">{error}</p>
        </div>
      )}

      {/* Modal / Form Container */}
      {showForm && (
        <div className="glass-panel p-6 md:p-8 rounded-2xl border border-blue-500/20 shadow-2xl relative">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-blue-400" />
              <h2 className="text-xl font-bold text-gray-100">Index New Website</h2>
            </div>
          </div>
          <WebsiteForm
            onSubmit={handleAddWebsite}
            onCancel={() => setShowForm(false)}
          />
        </div>
      )}

      {/* Metrics Banner */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="glass-card p-5 rounded-2xl flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-blue-500/10 text-blue-400 flex items-center justify-center font-bold">
            <Globe className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-gray-400">Total Sources</p>
            <p className="text-2xl font-extrabold text-gray-100">{websites.length}</p>
          </div>
        </div>

        <div className="glass-card p-5 rounded-2xl flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center font-bold">
            <CheckCircle2 className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-gray-400">Indexed</p>
            <p className="text-2xl font-extrabold text-emerald-400">{indexedCount}</p>
          </div>
        </div>

        <div className="glass-card p-5 rounded-2xl flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-amber-500/10 text-amber-400 flex items-center justify-center font-bold">
            <Clock className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-gray-400">In Progress</p>
            <p className="text-2xl font-extrabold text-amber-400">{indexingCount}</p>
          </div>
        </div>

        <div className="glass-card p-5 rounded-2xl flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-purple-500/10 text-purple-400 flex items-center justify-center font-bold">
            <Layers className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-gray-400">Total Vector Chunks</p>
            <p className="text-2xl font-extrabold text-purple-400">{totalChunks.toLocaleString()}</p>
          </div>
        </div>
      </div>

      {/* Filter / Search Bar */}
      {websites.length > 0 && (
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-gray-400">
            <Search className="w-4 h-4" />
          </div>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search indexed websites by title or URL..."
            className="w-full pl-10 pr-4 py-2.5 bg-gray-900/70 text-gray-100 placeholder-gray-500 rounded-xl border border-gray-800 focus:border-blue-500 focus:outline-none text-sm transition-all"
          />
        </div>
      )}

      {/* Websites Grid */}
      {loading ? (
        <div className="text-center py-16 glass-card rounded-2xl">
          <div className="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-sm font-medium text-gray-400">Fetching knowledge base status...</p>
        </div>
      ) : filteredWebsites.length === 0 ? (
        <div className="text-center py-16 glass-panel rounded-2xl border border-dashed border-gray-800">
          <Globe className="w-12 h-12 text-gray-600 mx-auto mb-4" />
          <p className="text-lg font-bold text-gray-200">
            {searchQuery ? 'No websites match your search' : 'No websites indexed yet'}
          </p>
          <p className="text-sm text-gray-400 mt-1 mb-6 max-w-sm mx-auto">
            Add a website URL to crawl pages, extract content, and build vector embeddings for AI answers.
          </p>
          <button
            onClick={() => setShowForm(true)}
            className="px-6 py-2.5 bg-blue-600 hover:bg-blue-500 text-white font-semibold text-sm rounded-xl shadow-lg shadow-blue-500/20 transition-all inline-flex items-center gap-2"
          >
            <Plus className="w-4 h-4" />
            <span>Add First Website</span>
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredWebsites.map((website) => (
            <WebsiteCard key={website.id} website={website} onDelete={handleDelete} />
          ))}
        </div>
      )}
    </div>
  );
}
