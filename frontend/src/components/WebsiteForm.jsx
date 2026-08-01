import { useState } from 'react';
import { AlertCircle, Globe, Loader2, PlusCircle, X } from 'lucide-react';

export default function WebsiteForm({ onSubmit, onCancel }) {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    let targetUrl = url.trim();
    if (!targetUrl) {
      setError('Please enter a valid website URL');
      return;
    }
    if (!targetUrl.startsWith('http://') && !targetUrl.startsWith('https://')) {
      targetUrl = 'https://' + targetUrl;
    }

    try {
      setLoading(true);
      await onSubmit(targetUrl);
    } catch (err) {
      setError(err.message || 'Failed to submit website');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5 animate-slide-up">
      {error && (
        <div className="p-4 bg-rose-500/10 border border-rose-500/30 text-rose-300 rounded-xl flex items-center gap-3 text-sm">
          <AlertCircle className="w-5 h-5 flex-shrink-0 text-rose-400" />
          <span>{error}</span>
        </div>
      )}

      <div>
        <label className="block text-xs font-semibold uppercase tracking-wider text-gray-400 mb-2">
          Target Website URL
        </label>
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-gray-400">
            <Globe className="w-5 h-5" />
          </div>
          <input
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="e.g. docs.python.org or https://fastapi.tiangolo.com"
            disabled={loading}
            className="w-full pl-11 pr-4 py-3 bg-gray-900/80 text-gray-100 placeholder-gray-500 rounded-xl border border-gray-700/80 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 focus:outline-none transition-all disabled:opacity-50 text-sm"
          />
        </div>
      </div>

      {/* Preset Example Quick Pills */}
      <div className="flex flex-wrap items-center gap-2 text-xs">
        <span className="text-gray-400">Try examples:</span>
        {['python.org', 'fastapi.tiangolo.com', 'sqlite.org'].map((example) => (
          <button
            key={example}
            type="button"
            onClick={() => setUrl(example)}
            className="px-2.5 py-1 rounded-lg bg-gray-800/60 hover:bg-gray-800 text-gray-300 hover:text-blue-400 border border-gray-700/50 transition-colors"
          >
            {example}
          </button>
        ))}
      </div>

      <div className="flex gap-3 pt-2">
        <button
          type="submit"
          disabled={loading || !url.trim()}
          className="flex-1 px-5 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-semibold text-sm rounded-xl shadow-lg shadow-blue-500/20 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Submitting Task...</span>
            </>
          ) : (
            <>
              <PlusCircle className="w-4 h-4" />
              <span>Start Indexing</span>
            </>
          )}
        </button>

        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2.5 bg-gray-800 hover:bg-gray-700 text-gray-300 font-semibold text-sm rounded-xl border border-gray-700 transition-colors flex items-center gap-1.5"
        >
          <X className="w-4 h-4" />
          <span>Cancel</span>
        </button>
      </div>

      <p className="text-xs text-gray-400 flex items-center gap-1.5">
        <span>ℹ️</span>
        <span>The pipeline will recursively crawl, chunk, and embed pages in the background.</span>
      </p>
    </form>
  );
}
