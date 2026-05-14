import { useState } from 'react';
import { AlertCircle } from 'lucide-react';

export default function WebsiteForm({ onSubmit, onCancel }) {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    if (!url.trim()) {
      setError('Please enter a valid URL');
      return;
    }

    try {
      setLoading(true);
      await onSubmit(url);
    } catch (err) {
      setError(err.message || 'Failed to add website');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="p-3 bg-red-900 text-red-100 rounded flex gap-3">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <p className="text-sm">{error}</p>
        </div>
      )}

      <div>
        <label className="block text-sm font-medium mb-2">Website URL</label>
        <input
          type="url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://example.com"
          disabled={loading}
          className="w-full px-4 py-2 bg-gray-700 text-white rounded-lg border border-gray-600 focus:border-blue-500 focus:outline-none disabled:opacity-50"
        />
      </div>

      <div className="flex gap-3">
        <button
          type="submit"
          disabled={loading || !url.trim()}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg disabled:opacity-50"
        >
          {loading ? 'Adding...' : 'Add Website'}
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg"
        >
          Cancel
        </button>
      </div>

      <p className="text-xs text-gray-400">
        The website will be crawled and indexed. This may take a few minutes for large sites.
      </p>
    </form>
  );
}
