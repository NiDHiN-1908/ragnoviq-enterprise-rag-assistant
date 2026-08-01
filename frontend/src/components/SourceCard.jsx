import { ExternalLink, Compass } from 'lucide-react';

export default function SourceCard({ source }) {
  const relevancePct = Math.round((source.relevance || source.similarity_score || 0.85) * 100);

  return (
    <a
      href={source.page_url || source.url}
      target="_blank"
      rel="noopener noreferrer"
      className="glass-card p-3.5 rounded-xl border border-gray-800 hover:border-blue-500/40 transition-all group flex flex-col justify-between block"
    >
      <div>
        <div className="flex items-start justify-between gap-2 mb-1.5">
          <div className="flex items-center gap-2 flex-1 min-w-0">
            <Compass className="w-3.5 h-3.5 text-blue-400 flex-shrink-0" />
            <h4 className="text-xs font-bold text-gray-200 group-hover:text-blue-300 transition-colors truncate">
              {source.page_title || source.title || source.url}
            </h4>
          </div>
          <ExternalLink className="w-3.5 h-3.5 text-gray-500 group-hover:text-blue-400 transition-colors flex-shrink-0" />
        </div>

        <p className="text-[11px] text-gray-400 truncate mb-3">
          {source.page_url || source.url}
        </p>
      </div>

      {/* Relevance Progress Bar */}
      <div className="pt-2 border-t border-gray-800/60 flex items-center justify-between gap-3 text-[10px]">
        <span className="text-gray-400 font-medium">Relevance Match</span>
        <div className="flex items-center gap-2">
          <div className="w-16 h-1.5 bg-gray-800 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full"
              style={{ width: `${Math.min(100, Math.max(10, relevancePct))}%` }}
            />
          </div>
          <span className="font-mono font-semibold text-blue-400">{relevancePct}%</span>
        </div>
      </div>
    </a>
  );
}
