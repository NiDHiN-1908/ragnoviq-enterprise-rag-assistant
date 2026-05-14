import { ExternalLink } from 'lucide-react';

export default function ChatMessage({ user, message }) {
  return (
    <div className={`flex ${user ? 'justify-end' : 'justify-start'} animate-slide-up`}>
      <div className={`max-w-2xl px-6 py-4 rounded-lg ${
        user
          ? 'bg-blue-600 text-white'
          : 'bg-gray-800 text-gray-100 border border-gray-700'
      }`}>
        <p className="whitespace-pre-wrap">{message.content}</p>
        {!user && message.responseTime && (
          <div className="mt-3 text-xs text-gray-400 flex gap-4">
            <span>⏱️ {message.responseTime.toFixed(2)}s</span>
            {message.tokens && <span>🔤 {message.tokens} tokens</span>}
          </div>
        )}
      </div>
    </div>
  );
}
