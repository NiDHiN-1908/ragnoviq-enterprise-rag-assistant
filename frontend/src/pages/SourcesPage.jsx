import { useEffect, useState } from 'react';
import { RefreshCw, AlertCircle, Database, ExternalLink, Search, FileText, Layers, Calendar } from 'lucide-react';
import api from '../services/api';

export default function SourcesPage() {
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchSources();
  }, []);

  const fetchSources = async () => {
    setLoading(true);
    try {
      const response = await api.get('/api/v1/sources');
      setSources(response.data.sources || []);
      setError(null);
    } catch (err) {
      const errorMsg = (err.code === 'ERR_NETWORK' || !err.response)
        ? 'Backend API is offline. Make sure to run backend server at http://localhost:8000.'
        : 'Failed to load sources';
      setError(errorMsg);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const filteredSources = sources.filter(s =>
    (s.title || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
    (s.url || '').toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="max-w-6xl mx-auto p-6 md:p-8 space-y-8 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-gray-100 flex items-center gap-3">
            <span>Indexed Knowledge Sources</span>
            <span className="text-xs px-2.5 py-1 rounded-full bg-purple-500/10 text-purple-400 border border-purple-500/20 font-semibold">
              {sources.length} Domains
            </span>
          </h1>
          <p className="text-sm text-gray-400 mt-1">
            Browse all website domains, page statistics, and chunking totals in the FAISS vector index.
          </p>
        </div>

        <button
          onClick={fetchSources}
          disabled={loading}
          className="px-4 py-2.5 bg-gray-800/80 hover:bg-gray-800 text-gray-300 font-semibold text-sm rounded-xl border border-gray-700/80 transition-all flex items-center gap-2 self-start md:self-auto"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-blue-400' : ''}`} />
          <span>Refresh Sources</span>
        </button>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="p-4 bg-rose-500/10 border border-rose-500/30 text-rose-200 rounded-2xl flex items-center gap-3 text-sm animate-slide-up">
          <AlertCircle className="w-5 h-5 text-rose-400 flex-shrink-0" />
          <p className="flex-1">{error}</p>
        </div>
      )}

      {/* Search Bar */}
      {sources.length > 0 && (
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-gray-400">
            <Search className="w-4 h-4" />
          </div>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Filter sources by title or URL..."
            className="w-full pl-10 pr-4 py-2.5 bg-gray-900/70 text-gray-100 placeholder-gray-500 rounded-xl border border-gray-800 focus:border-purple-500 focus:outline-none text-sm transition-all"
          />
        </div>
      )}

      {/* Sources List */}
      {loading ? (
        <div className="text-center py-16 glass-card rounded-2xl">
          <div className="w-10 h-10 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-sm font-medium text-gray-400">Loading indexed source documents...</p>
        </div>
      ) : filteredSources.length === 0 ? (
        <div className="text-center py-16 glass-panel rounded-2xl border border-dashed border-gray-800">
          <Database className="w-12 h-12 text-gray-600 mx-auto mb-4" />
          <p className="text-lg font-bold text-gray-200">
            {searchQuery ? 'No sources match your filter' : 'No indexed sources found'}
          </p>
          <p className="text-sm text-gray-400 mt-1 max-w-sm mx-auto">
            Websites added from the Dashboard will appear here once crawling and vector embedding completes.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredSources.map((source) => (
            <div
              key={source.id}
              className="glass-card p-6 rounded-2xl border border-gray-800 hover:border-purple-500/30 transition-all flex flex-col md:flex-row md:items-center justify-between gap-4"
            >
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <h3 className="font-bold text-lg text-gray-100 truncate">
                    {source.title || source.url}
                  </h3>
                  <a
                    href={source.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="p-1 hover:bg-gray-800 text-gray-400 hover:text-purple-400 rounded-lg transition-colors flex-shrink-0"
                    title="Open Original Website"
                  >
                    <ExternalLink className="w-4 h-4" />
                  </a>
                </div>
                <p className="text-xs text-gray-400 truncate">{source.url}</p>
              </div>

              {/* Badges */}
              <div className="flex flex-wrap items-center gap-4 text-xs font-semibold">
                <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-blue-500/10 text-blue-400 border border-blue-500/20">
                  <FileText className="w-3.5 h-3.5" />
                  <span>{source.pages_indexed ?? source.pages ?? 0} Pages</span>
                </div>

                <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-purple-500/10 text-purple-400 border border-purple-500/20">
                  <Layers className="w-3.5 h-3.5" />
                  <span>{source.chunks_created ?? source.chunks ?? 0} Chunks</span>
                </div>

                {source.indexed_at && (
                  <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-gray-800 text-gray-400 border border-gray-700">
                    <Calendar className="w-3.5 h-3.5" />
                    <span>{new Date(source.indexed_at).toLocaleDateString()}</span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
