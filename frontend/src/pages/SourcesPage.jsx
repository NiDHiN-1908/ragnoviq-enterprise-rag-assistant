import { useEffect, useState } from 'react';
import { RefreshCw, AlertCircle } from 'lucide-react';
import api from '../services/api';

export default function SourcesPage() {
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(true);
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
      setError('Failed to load sources');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Indexed Sources</h1>
        <button
          onClick={fetchSources}
          className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg flex items-center gap-2"
        >
          <RefreshCw className="w-4 h-4" />
          Refresh
        </button>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-900 text-red-100 rounded-lg flex gap-3">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <p>{error}</p>
        </div>
      )}

      {loading ? (
        <div className="text-center py-12">
          <p className="text-gray-400">Loading sources...</p>
        </div>
      ) : sources.length === 0 ? (
        <div className="text-center py-12 bg-gray-800 rounded-lg border border-gray-700">
          <p className="text-gray-400">No indexed sources found</p>
        </div>
      ) : (
        <div className="space-y-4">
          {sources.map(source => (
            <div
              key={source.id}
              className="p-6 bg-gray-800 border border-gray-700 rounded-lg hover:border-gray-600 transition"
            >
              <a
                href={source.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-lg font-semibold text-blue-400 hover:text-blue-300 truncate"
              >
                {source.title}
              </a>
              <p className="text-sm text-gray-400 mt-1 truncate">{source.url}</p>
              <div className="flex gap-6 mt-4 text-sm">
                <div>
                  <span className="text-gray-400">Pages:</span>
                  <span className="ml-2 font-semibold">{source.pages_indexed}</span>
                </div>
                <div>
                  <span className="text-gray-400">Chunks:</span>
                  <span className="ml-2 font-semibold">{source.chunks_created}</span>
                </div>
                <div>
                  <span className="text-gray-400">Indexed:</span>
                  <span className="ml-2 font-semibold">
                    {new Date(source.indexed_at).toLocaleDateString()}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
