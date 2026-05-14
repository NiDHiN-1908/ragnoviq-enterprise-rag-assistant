import { useState, useRef, useEffect } from 'react';
import { Send, Loader, AlertCircle } from 'lucide-react';
import api from '../services/api';
import ChatMessage from '../components/ChatMessage';
import SourceCard from '../components/SourceCard';
import { useStore } from '../store';

export default function ChatPage() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const messagesEndRef = useRef(null);

  const { websites } = useStore();

  useEffect(() => {
    if (!sessionId) {
      setSessionId(Math.random().toString(36).substr(2, 9));
    }
  }, [sessionId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = input;
    setInput('');
    setError(null);

    // Add user message to UI
    setMessages(prev => [...prev, {
      type: 'user',
      content: userMessage,
      timestamp: new Date(),
    }]);

    setLoading(true);

    try {
      const response = await api.post('/api/v1/chat/query', {
        question: userMessage,
        session_id: sessionId,
        use_websites: websites.map(w => w.id),
      });

      setMessages(prev => [...prev, {
        type: 'assistant',
        content: response.data.answer,
        sources: response.data.sources,
        model: response.data.model_used,
        tokens: response.data.tokens_used,
        responseTime: response.data.response_time,
        timestamp: new Date(),
      }]);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to get response');
      setMessages(prev => [...prev, {
        type: 'error',
        content: 'Failed to get response. Please try again.',
        timestamp: new Date(),
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-950">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.length === 0 && (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <h2 className="text-3xl font-bold mb-4">Ask me anything</h2>
              <p className="text-gray-400 mb-8">Ask questions about the indexed websites</p>
              {websites.length === 0 && (
                <div className="bg-yellow-900 text-yellow-100 p-4 rounded">
                  <p>No websites indexed yet. Go to Dashboard to add websites.</p>
                </div>
              )}
            </div>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div key={idx}>
            {msg.type === 'user' && <ChatMessage user={true} message={msg} />}
            {msg.type === 'assistant' && (
              <>
                <ChatMessage user={false} message={msg} />
                {msg.sources && msg.sources.length > 0 && (
                  <div className="ml-4 mt-4 space-y-2">
                    <p className="text-sm font-semibold text-gray-400">Sources:</p>
                    {msg.sources.map((source, i) => (
                      <SourceCard key={i} source={source} />
                    ))}
                  </div>
                )}
              </>
            )}
            {msg.type === 'error' && (
              <div className="flex gap-3 animate-slide-up">
                <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
                <p className="text-red-400">{msg.content}</p>
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex gap-3">
            <Loader className="w-5 h-5 text-blue-400 animate-spin" />
            <p className="text-gray-400">Thinking...</p>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t border-gray-800 p-6 bg-gray-900">
        {error && (
          <div className="mb-4 p-3 bg-red-900 text-red-100 rounded text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSendMessage} className="flex gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question..."
            disabled={loading || websites.length === 0}
            className="flex-1 px-4 py-3 bg-gray-800 text-white rounded-lg border border-gray-700 focus:border-blue-500 focus:outline-none disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={loading || !input.trim() || websites.length === 0}
            className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>

        {websites.length === 0 && (
          <p className="mt-2 text-sm text-yellow-400">
            Index a website first to ask questions
          </p>
        )}
      </div>
    </div>
  );
}
