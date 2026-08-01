import { Trash2, CheckCircle2, AlertCircle, RefreshCw, ExternalLink, Layers, FileText } from 'lucide-react';

export default function WebsiteCard({ website, onDelete }) {
  const statusConfig = {
    indexed: {
      badgeBg: 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400',
      dotBg: 'bg-emerald-400',
      icon: CheckCircle2,
      label: 'Indexed & Ready',
    },
    indexing: {
      badgeBg: 'bg-amber-500/10 border-amber-500/30 text-amber-400',
      dotBg: 'bg-amber-400 animate-ping',
      icon: RefreshCw,
      label: 'Crawling & Indexing...',
    },
    pending: {
      badgeBg: 'bg-blue-500/10 border-blue-500/30 text-blue-400',
      dotBg: 'bg-blue-400 animate-pulse',
      icon: RefreshCw,
      label: 'Queued for Crawl',
    },
    failed: {
      badgeBg: 'bg-rose-500/10 border-rose-500/30 text-rose-400',
      dotBg: 'bg-rose-400',
      icon: AlertCircle,
      label: 'Indexing Failed',
    },
  };

  const currentStatus = statusConfig[website.status] || statusConfig.pending;
  const StatusIcon = currentStatus.icon;

  return (
    <div className="glass-card rounded-2xl p-6 relative overflow-hidden group flex flex-col justify-between">
      {/* Subtle background gradient glow */}
      <div className="absolute -right-10 -top-10 w-32 h-32 bg-blue-500/5 rounded-full blur-2xl group-hover:bg-blue-500/10 transition-all duration-300 pointer-events-none" />

      <div>
        {/* Top Header & Actions */}
        <div className="flex items-start justify-between gap-4 mb-3">
          <div className="flex-1 min-w-0">
            <h3 className="font-bold text-lg text-gray-100 truncate group-hover:text-blue-400 transition-colors">
              {website.title || website.url}
            </h3>
            <a
              href={website.url}
              target="_blank"
              rel="noreferrer"
              className="text-xs text-gray-400 hover:text-blue-400 transition-colors flex items-center gap-1 mt-1 truncate"
            >
              <span className="truncate">{website.url}</span>
              <ExternalLink className="w-3 h-3 flex-shrink-0" />
            </a>
          </div>

          <button
            onClick={() => onDelete(website.id)}
            className="p-2 hover:bg-rose-500/15 text-gray-400 hover:text-rose-400 rounded-xl transition-all flex-shrink-0 border border-transparent hover:border-rose-500/20"
            title="Delete Website"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>

        {/* Status Badge */}
        <div className="mb-6 flex items-center">
          <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-semibold border ${currentStatus.badgeBg}`}>
            <span className={`w-2 h-2 rounded-full ${currentStatus.dotBg}`} />
            <StatusIcon className={`w-3.5 h-3.5 ${website.status === 'indexing' ? 'animate-spin' : ''}`} />
            <span>{currentStatus.label}</span>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 gap-3 p-3 bg-gray-900/60 rounded-xl border border-gray-800/80">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-blue-500/10 text-blue-400">
              <FileText className="w-4 h-4" />
            </div>
            <div>
              <p className="text-[11px] font-medium uppercase tracking-wider text-gray-400">Pages</p>
              <p className="text-base font-bold text-gray-100">{website.pages ?? website.total_pages ?? 0}</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-purple-500/10 text-purple-400">
              <Layers className="w-4 h-4" />
            </div>
            <div>
              <p className="text-[11px] font-medium uppercase tracking-wider text-gray-400">Chunks</p>
              <p className="text-base font-bold text-gray-100">{website.chunks ?? website.total_chunks ?? 0}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Footer Timestamp */}
      {website.created_at && (
        <p className="mt-4 pt-3 border-t border-gray-800/50 text-[11px] text-gray-400 flex items-center justify-between">
          <span>Added</span>
          <span className="font-mono text-gray-300">{new Date(website.created_at).toLocaleDateString()}</span>
        </p>
      )}
    </div>
  );
}
