import { useState } from 'react';
import { Copy, Check, Bot, User, Clock, Zap } from 'lucide-react';

export default function ChatMessage({ user, message, onRetry }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    if (message?.content) {
      navigator.clipboard.writeText(message.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  // Helper to format basic markdown elements safely
  const renderFormattedText = (text) => {
    if (!text) return null;
    
    // Split into paragraphs / lines
    const lines = text.split('\n');
    return lines.map((line, idx) => {
      // Bold formatting
      let formattedLine = line;
      if (line.startsWith('### ')) {
        return <h3 key={idx} className="text-lg font-bold text-blue-300 mt-2 mb-1">{line.replace('### ', '')}</h3>;
      }
      if (line.startsWith('## ')) {
        return <h2 key={idx} className="text-xl font-bold text-blue-400 mt-3 mb-2">{line.replace('## ', '')}</h2>;
      }
      if (line.startsWith('* ') || line.startsWith('- ')) {
        return (
          <li key={idx} className="ml-4 list-disc text-gray-200 my-1">
            {line.replace(/^[\*\-]\s+/, '')}
          </li>
        );
      }
      if (line.startsWith('> ')) {
        return (
          <blockquote key={idx} className="border-l-4 border-blue-500 pl-3 py-1 italic bg-gray-900/50 my-2 rounded text-gray-300">
            {line.replace(/^>\s+/, '')}
          </blockquote>
        );
      }
      if (line.trim() === '') {
        return <div key={idx} className="h-2" />;
      }
      return <p key={idx} className="leading-relaxed mb-1">{formattedLine}</p>;
    });
  };

  return (
    <div className={`flex gap-3 ${user ? 'justify-end' : 'justify-start'} animate-slide-up my-3`}>
      {!user && (
        <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-600 to-cyan-600 flex items-center justify-center text-white shadow-lg flex-shrink-0 mt-1">
          <Bot className="w-5 h-5" />
        </div>
      )}

      <div className={`group relative max-w-3xl px-5 py-4 rounded-2xl shadow-md ${
        user
          ? 'bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-tr-none'
          : 'bg-gray-800/90 text-gray-100 border border-gray-700/80 rounded-tl-none backdrop-blur-sm'
      }`}>
        <div className="text-sm">
          {renderFormattedText(message.content)}
        </div>

        {!user && (
          <div className="mt-3 pt-2 border-t border-gray-700/50 text-xs text-gray-400 flex items-center justify-between">
            <div className="flex items-center gap-3">
              {message.responseTime && (
                <span className="flex items-center gap-1">
                  <Clock className="w-3.5 h-3.5 text-blue-400" />
                  {message.responseTime.toFixed(2)}s
                </span>
              )}
              {message.tokens > 0 && (
                <span className="flex items-center gap-1">
                  <Zap className="w-3.5 h-3.5 text-yellow-400" />
                  {message.tokens} tokens
                </span>
              )}
              {message.model && (
                <span className="bg-gray-900/80 px-2 py-0.5 rounded text-[10px] text-gray-400 font-mono">
                  {message.model}
                </span>
              )}
            </div>

            <button
              onClick={handleCopy}
              className="p-1.5 hover:bg-gray-700/80 rounded text-gray-400 hover:text-white transition flex items-center gap-1"
              title="Copy answer"
            >
              {copied ? (
                <>
                  <Check className="w-3.5 h-3.5 text-green-400" />
                  <span className="text-[11px] text-green-400">Copied</span>
                </>
              ) : (
                <>
                  <Copy className="w-3.5 h-3.5" />
                  <span className="text-[11px]">Copy</span>
                </>
              )}
            </button>
          </div>
        )}
      </div>

      {user && (
        <div className="w-9 h-9 rounded-xl bg-gray-700 flex items-center justify-center text-gray-300 flex-shrink-0 mt-1">
          <User className="w-5 h-5" />
        </div>
      )}
    </div>
  );
}

