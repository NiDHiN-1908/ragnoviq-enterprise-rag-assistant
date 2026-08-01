import { useState, useRef, useEffect } from 'react';
import { Send, Loader, AlertCircle, Trash2, Sparkles, RefreshCw } from 'lucide-react';
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
      setSessionId('sess_' + Math.random().toString(36).substr(2, 9));
    }
  }, [sessionId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleClearSession = async () => {
    if (!messages.length) return;
    try {
      if (sessionId) {
        await api.delete(`/api/v1/chat/session/${sessionId}`);
      }
      setMessages([]);
      setError(null);
    } catch (err) {
      console.error('Failed to clear session:', err);
      setMessages([]);
    }
  };

  const executeSend = async (userMessage) => {
    if (!userMessage.trim() || loading) return;

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
      const errorMsg = err.response?.data?.detail || 'Failed to generate response. Please verify backend service.';
      setError(errorMsg);
      setMessages(prev => [...prev, {
        type: 'error',
        content: errorMsg,
        timestamp: new Date(),
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleSendMessage = (e) => {
    e.preventDefault();
    const queryText = input;
    setInput('');
    executeSend(queryText);
  };

  const suggestedPrompts = [
    "What is the main topic of the indexed site?",
    "Summarize key features and services mentioned",
    "List contact or documentation details",
  ];

  return (
    <div className="flex flex-col h-screen bg-gray-950 text-gray-100">
      {/* Top Header Controls */}
      <div className="px-6 py-3 border-b border-gray-800/80 bg-gray-900/60 backdrop-blur-md flex justify-between items-center">
        <div className="flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-blue-400" />
          <h2 className="text-sm font-semibold text-gray-200">AI Knowledge Chat</h2>
          {websites.length > 0 && (
            <span className="text-xs bg-blue-900/60 text-blue-300 border border-blue-700/50 px-2 py-0.5 rounded-full">
              {websites.length} {websites.length === 1 ? 'Source' : 'Sources'} Active
            </span>
          )}
        </div>

        {messages.length > 0 && (
          <button
            onClick={handleClearSession}
            className="px-3 py-1.5 bg-gray-800 hover:bg-red-900/60 hover:text-red-300 text-gray-400 text-xs rounded-lg border border-gray-700 hover:border-red-700/60 transition flex items-center gap-1.5"
            title="Clear Chat Conversation"
          >
            <Trash2 className="w-3.5 h-3.5" />
            Clear Chat
          </button>
        )}
      </div>

      {/* Messages Feed */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.length === 0 && (
          <div className="flex items-center justify-center h-full">
            <div className="text-center max-w-lg">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-blue-600 to-cyan-500 flex items-center justify-center mx-auto mb-6 shadow-xl shadow-blue-500/10">
                <Sparkles className="w-8 h-8 text-white animate-pulse" />
              </div>
              <h2 className="text-3xl font-bold mb-2 bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
                What would you like to know?
              </h2>
              <p className="text-gray-400 text-sm mb-8">
                Ask anything based on your indexed websites knowledge base.
              </p>

              {websites.length === 0 ? (
                <div className="bg-yellow-900/40 border border-yellow-700/50 text-yellow-200 p-4 rounded-xl text-sm shadow-inner">
                  <p>No websites indexed yet. Head over to the Dashboard to add your first website URL!</p>
                </div>
              ) : (
                <div className="space-y-2">
                  <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold mb-3">Try asking:</p>
                  <div className="flex flex-col gap-2">
                    {suggestedPrompts.map((prompt, idx) => (
                      <button
                        key={idx}
                        onClick={() => executeSend(prompt)}
                        className="px-4 py-2.5 bg-gray-900/80 hover:bg-gray-800 text-gray-300 text-xs text-left rounded-xl border border-gray-800 hover:border-blue-500/50 transition flex items-center justify-between group"
                      >
                        <span>{prompt}</span>
                        <Send className="w-3 h-3 opacity-0 group-hover:opacity-100 text-blue-400 transition" />
                      </button>
                    ))}
                  </div>
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
                  <div className="ml-12 mt-2 space-y-2 max-w-2xl">
                    <p className="text-xs font-medium text-gray-400 flex items-center gap-1.5">
                      <span>CITED SOURCES</span>
                      <span className="text-[10px] bg-gray-800 px-1.5 py-0.5 rounded text-gray-400">{msg.sources.length}</span>
                    </p>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                      {msg.sources.map((source, i) => (
                        <SourceCard key={i} source={source} />
                      ))}
                    </div>
                  </div>
                )}
              </>
            )}
            {msg.type === 'error' && (
              <div className="flex gap-3 p-4 bg-red-950/60 border border-red-800/60 text-red-200 rounded-xl my-3 text-sm items-center justify-between">
                <div className="flex items-center gap-2">
                  <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
                  <p>{msg.content}</p>
                </div>
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex items-center gap-3 ml-2 my-4">
            <div className="w-8 h-8 rounded-xl bg-blue-600/20 border border-blue-500/30 flex items-center justify-center">
              <Loader className="w-4 h-4 text-blue-400 animate-spin" />
            </div>
            <p className="text-xs text-gray-400 animate-pulse">RAGNoviq is searching context and generating answer...</p>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Bar */}
      <div className="border-t border-gray-800/80 p-5 bg-gray-900/80 backdrop-blur-md">
        {error && (
          <div className="mb-3 p-3 bg-red-900/50 border border-red-700/50 text-red-200 rounded-xl text-xs flex items-center justify-between">
            <span>{error}</span>
            <button onClick={() => setError(null)} className="text-red-400 hover:text-white font-bold ml-2">✕</button>
          </div>
        )}

        <form onSubmit={handleSendMessage} className="flex gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={websites.length === 0 ? "Index a website first..." : "Ask a question about the indexed knowledge..."}
            disabled={loading || websites.length === 0}
            className="flex-1 px-4 py-3 bg-gray-950 text-gray-100 rounded-xl border border-gray-800 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none disabled:opacity-50 text-sm shadow-inner placeholder-gray-500"
          />
          <button
            type="submit"
            disabled={loading || !input.trim() || websites.length === 0}
            className="px-6 py-3 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white font-medium rounded-xl disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 shadow-lg shadow-blue-600/20 transition"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
}

