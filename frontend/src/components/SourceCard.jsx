import { ExternalLink } from 'lucide-react';

export default function SourceCard({ source }) {
  return (
    <a
      href={source.url}
      target="_blank"
      rel="noopener noreferrer"
      className="block p-3 bg-gray-800 border border-gray-700 rounded hover:border-blue-500 transition group"
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-blue-400 group-hover:text-blue-300 truncate">
            {source.title}
          </p>
          <p className="text-xs text-gray-500 mt-1 truncate">{source.url}</p>
        </div>
        <ExternalLink className="w-4 h-4 text-gray-500 flex-shrink-0 group-hover:text-blue-400" />
      </div>
      <div className="mt-2 text-xs text-gray-400">
        Relevance: {(source.relevance * 100).toFixed(0)}%
      </div>
    </a>
  );
}
