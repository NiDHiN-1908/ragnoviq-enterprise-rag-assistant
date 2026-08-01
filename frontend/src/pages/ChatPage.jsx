import { useState, useRef, useEffect } from 'react';
import { Send, Loader2, AlertCircle, Trash2, Sparkles, Database, ArrowRight, MessageSquare } from 'lucide-react';
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
      const errorMsg = err.response?.data?.detail || 'Backend API is offline or failed to generate answer. Ensure backend server is running on http://localhost:8000.';
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
    "What are the main features and services described?",
    "Summarize the key information from the indexed documents",
    "What technology stack or requirements are mentioned?",
  ];

  return (
    <div className="flex flex-col h-full bg-[#0b0f19] text-gray-100 relative">
      {/* Top Header Bar */}
      <div className="px-6 py-3.5 border-b border-gray-800/80 glass-panel flex justify-between items-center z-10">
        <div className="flex items-center gap-3">
          <div className="p-1.5 rounded-lg bg-blue-500/10 text-blue-400">
            <MessageSquare className="w-4 h-4" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-gray-100 flex items-center gap-2">
              <span>AI Knowledge Assistant</span>
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            </h2>
            <p className="text-xs text-gray-400">Grounded RAG Answer Generator</p>
          </div>

          {websites.length > 0 && (
            <span className="hidden sm:inline-flex items-center gap-1.5 text-xs bg-blue-500/10 text-blue-400 border border-blue-500/20 px-2.5 py-1 rounded-full font-semibold ml-2">
              <Database className="w-3 h-3" />
              {websites.length} Active {websites.length === 1 ? 'Source' : 'Sources'}
            </span>
          )}
        </div>

        {messages.length > 0 && (
          <button
            onClick={handleClearSession}
            className="px-3.5 py-1.5 bg-gray-800/80 hover:bg-rose-500/15 text-gray-400 hover:text-rose-300 text-xs font-semibold rounded-xl border border-gray-700/80 hover:border-rose-500/30 transition-all flex items-center gap-1.5"
            title="Clear Chat Conversation"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span>Clear Session</span>
          </button>
        )}
      </div>

      {/* Messages Feed */}
      <div className="flex-1 overflow-y-auto p-4 md:p-8 space-y-6">
        {messages.length === 0 && (
          <div className="flex items-center justify-center min-h-[70vh]">
            <div className="text-center max-w-xl p-6">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-blue-600 via-indigo-500 to-purple-600 flex items-center justify-center mx-auto mb-6 shadow-xl shadow-blue-500/20 glow-blue">
                <Sparkles className="w-8 h-8 text-white animate-pulse" />
              </div>
              <h2 className="text-3xl font-extrabold mb-3 tracking-tight gradient-text">
                Ask your Knowledge Base
              </h2>
              <p className="text-gray-400 text-sm mb-8 leading-relaxed">
                RAGNoviq uses hybrid vector retrieval and LLaMA 3.3 / Gemini to synthesize precise, cited answers from your crawled websites.
              </p>

              {websites.length === 0 ? (
                <div className="glass-card p-6 rounded-2xl border border-amber-500/30 text-amber-300 text-sm shadow-xl text-left flex items-start gap-3">
                  <AlertCircle className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="font-bold text-amber-200">No websites indexed yet!</p>
                    <p className="text-xs text-amber-300/80 mt-1">
                      Navigate to the <span className="font-semibold text-white">Dashboard</span> tab to add your first website URL. Once indexed, you can ask questions here.
                    </p>
                  </div>
                </div>
              ) : (
                <div className="space-y-3 text-left">
                  <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider text-center mb-4">
                    Suggested Quick Prompts:
                  </p>
                  <div className="grid grid-cols-1 gap-2.5">
                    {suggestedPrompts.map((prompt, idx) => (
                      <button
                        key={idx}
                        onClick={() => executeSend(prompt)}
                        className="glass-card px-4 py-3.5 rounded-xl text-xs font-medium text-gray-300 hover:text-white hover:border-blue-500/40 transition-all flex items-center justify-between group"
                      >
                        <span>{prompt}</span>
                        <ArrowRight className="w-3.5 h-3.5 text-blue-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div key={idx} className="space-y-3">
            {msg.type === 'user' && <ChatMessage user={true} message={msg} />}
            {msg.type === 'assistant' && (
              <>
                <ChatMessage user={false} message={msg} />
                {msg.sources && msg.sources.length > 0 && (
                  <div className="ml-12 pl-2 space-y-2 max-w-3xl">
                    <p className="text-xs font-bold text-gray-400 uppercase tracking-wider flex items-center gap-2">
                      <span>Retrieved Context Sources</span>
                      <span className="text-[10px] bg-blue-500/10 text-blue-400 border border-blue-500/20 px-2 py-0.5 rounded-full font-mono">
                        {msg.sources.length} Chunks
                      </span>
                    </p>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      {msg.sources.map((source, i) => (
                        <SourceCard key={i} source={source} />
                      ))}
                    </div>
                  </div>
                )}
              </>
            )}
            {msg.type === 'error' && (
              <div className="p-4 bg-rose-500/10 border border-rose-500/30 text-rose-200 rounded-2xl my-3 text-sm flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <AlertCircle className="w-5 h-5 text-rose-400 flex-shrink-0" />
                  <p>{msg.content}</p>
                </div>
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex items-center gap-3 ml-2 my-4">
            <div className="w-9 h-9 rounded-xl bg-blue-500/10 border border-blue-500/30 flex items-center justify-center text-blue-400">
              <Loader2 className="w-4 h-4 animate-spin" />
            </div>
            <p className="text-xs font-medium text-gray-400 animate-pulse">
              Retrieving FAISS context & generating LLaMA 3.3 response...
            </p>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Bar */}
      <div className="p-4 md:p-6 border-t border-gray-800/80 glass-panel">
        <form onSubmit={handleSendMessage} className="flex gap-3 max-w-5xl mx-auto">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={websites.length === 0 ? "Add a website from Dashboard to ask questions..." : "Ask a question about your indexed knowledge..."}
            disabled={loading || websites.length === 0}
            className="flex-1 px-5 py-3.5 bg-gray-900/90 text-gray-100 placeholder-gray-500 rounded-2xl border border-gray-800 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 focus:outline-none disabled:opacity-50 text-sm shadow-inner transition-all"
          />
          <button
            type="submit"
            disabled={loading || !input.trim() || websites.length === 0}
            className="px-6 py-3.5 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-bold rounded-2xl disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 shadow-lg shadow-blue-500/25 transition-all flex-shrink-0"
          >
            <Send className="w-4 h-4" />
            <span className="hidden sm:inline">Ask</span>
          </button>
        </form>
      </div>
    </div>
  );
}
