import { Trash2, CheckCircle, AlertCircle, Clock } from 'lucide-react';

export default function WebsiteCard({ website, onDelete }) {
  const getStatusColor = () => {
    switch (website.status) {
      case 'indexed':
        return 'text-green-400';
      case 'indexing':
        return 'text-yellow-400';
      case 'failed':
        return 'text-red-400';
      default:
        return 'text-gray-400';
    }
  };

  const getStatusIcon = () => {
    switch (website.status) {
      case 'indexed':
        return <CheckCircle className="w-5 h-5" />;
      case 'indexing':
        return <Clock className="w-5 h-5 animate-spin" />;
      case 'failed':
        return <AlertCircle className="w-5 h-5" />;
      default:
        return null;
    }
  };

  return (
    <div className="p-6 bg-gray-800 border border-gray-700 rounded-lg hover:border-gray-600 transition">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-lg truncate">{website.title || website.url}</h3>
          <p className="text-sm text-gray-400 mt-1 truncate">{website.url}</p>
        </div>
        <button
          onClick={() => onDelete(website.id)}
          className="ml-4 p-2 hover:bg-red-900 text-red-400 rounded transition flex-shrink-0"
          title="Delete website"
        >
          <Trash2 className="w-5 h-5" />
        </button>
      </div>

      <div className="flex items-center gap-2 mb-4">
        <div className={getStatusColor()}>
          {getStatusIcon()}
        </div>
        <span className="text-sm capitalize">{website.status}</span>
      </div>

      <div className="grid grid-cols-2 gap-4 text-sm">
        <div>
          <p className="text-gray-400">Pages</p>
          <p className="text-lg font-semibold">{website.pages}</p>
        </div>
        <div>
          <p className="text-gray-400">Chunks</p>
          <p className="text-lg font-semibold">{website.chunks}</p>
        </div>
      </div>

      {website.created_at && (
        <p className="mt-4 text-xs text-gray-500">
          Added {new Date(website.created_at).toLocaleDateString()}
        </p>
      )}
    </div>
  );
}
