import { useEffect, useState } from 'react';
import { Plus, Trash2, RefreshCw, AlertCircle } from 'lucide-react';
import api from '../services/api';
import WebsiteForm from '../components/WebsiteForm';
import WebsiteCard from '../components/WebsiteCard';
import { useStore } from '../store';

export default function DashboardPage() {
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(true);
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
      setError('Failed to load websites');
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
    if (!confirm('Are you sure you want to delete this website?')) return;

    try {
      await api.delete(`/api/v1/ingest/website/${websiteId}`);
      fetchWebsites();
    } catch (err) {
      setError('Failed to delete website');
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <div className="flex gap-3">
          <button
            onClick={fetchWebsites}
            className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg flex items-center gap-2"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
          <button
            onClick={() => setShowForm(true)}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg flex items-center gap-2"
          >
            <Plus className="w-4 h-4" />
            Add Website
          </button>
        </div>
      </div>

      {/* Error message */}
      {error && (
        <div className="mb-6 p-4 bg-red-900 text-red-100 rounded-lg flex gap-3">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <p>{error}</p>
        </div>
      )}

      {/* Add Website Form */}
      {showForm && (
        <div className="mb-8 p-6 bg-gray-800 rounded-lg border border-gray-700">
          <h2 className="text-xl font-semibold mb-4">Add Website</h2>
          <WebsiteForm
            onSubmit={handleAddWebsite}
            onCancel={() => setShowForm(false)}
          />
        </div>
      )}

      {/* Stats */}
      {!loading && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
            <p className="text-gray-400 text-sm">Total Websites</p>
            <p className="text-3xl font-bold">{websites.length}</p>
          </div>
          <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
            <p className="text-gray-400 text-sm">Indexed</p>
            <p className="text-3xl font-bold text-green-400">
              {websites.filter(w => w.status === 'indexed').length}
            </p>
          </div>
          <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
            <p className="text-gray-400 text-sm">Indexing</p>
            <p className="text-3xl font-bold text-yellow-400">
              {websites.filter(w => w.status === 'indexing').length}
            </p>
          </div>
        </div>
      )}

      {/* Websites List */}
      {loading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin text-blue-400 text-3xl">⏳</div>
          <p className="mt-4 text-gray-400">Loading websites...</p>
        </div>
      ) : websites.length === 0 ? (
        <div className="text-center py-12 bg-gray-800 rounded-lg border border-gray-700">
          <p className="text-gray-400 mb-4">No websites indexed yet</p>
          <button
            onClick={() => setShowForm(true)}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg"
          >
            Add First Website
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {websites.map(website => (
            <div key={website.id}>
              <WebsiteCard website={website} onDelete={handleDelete} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
