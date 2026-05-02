import { useState } from 'react';
import { Send, Terminal, Database, Code, CornerDownRight, AlertTriangle } from 'lucide-react';
import GlassCard from '../components/ui/GlassCard';
import { motion } from 'framer-motion';
import { api } from '../services/api';

const NLQuery = () => {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([
    { role: 'system', content: 'Neo-Sousse Natural Language Interface v1.0. Ready for queries.' }
  ]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    const userMsg = query;
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setQuery('');
    setIsLoading(true);

    try {
      const response = await api.post('/nl/query', { phrase: userMsg });
      
      if (response.data.success) {
        setMessages(prev => [
          ...prev, 
          { 
            role: 'assistant', 
            content: `Requête compilée avec succès !`,
            sql: response.data.sql,
            data: response.data.data
          }
        ]);
      } else {
        setMessages(prev => [
          ...prev, 
          { 
            role: 'assistant', 
            content: `Erreur de compilation : ${response.data.error}`,
            isError: true
          }
        ]);
      }
    } catch (error) {
      setMessages(prev => [
        ...prev, 
        { 
          role: 'assistant', 
          content: `Erreur de connexion au compilateur : ${error.message}`,
          isError: true
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto h-[calc(100vh-120px)] flex flex-col gap-6">
      <div className="flex items-center gap-3">
        <Terminal className="text-neo-primary w-8 h-8" />
        <div>
          <h1 className="text-2xl font-bold">Natural Language Data Query</h1>
          <p className="text-gray-400 text-sm">Ask questions about city data in plain English</p>
        </div>
      </div>

      <GlassCard className="flex-1 flex flex-col p-0 overflow-hidden border border-gray-700 shadow-[0_0_30px_rgba(59,130,246,0.1)]">
        {/* Chat History */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6 custom-scrollbar">
          {messages.map((msg, i) => (
            <motion.div 
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              key={i} 
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`max-w-[80%] rounded-xl p-4 ${
                msg.role === 'user' 
                  ? 'bg-neo-primary/20 border border-neo-primary/30 text-white rounded-tr-sm' 
                  : msg.role === 'system'
                    ? 'bg-gray-900/50 border border-gray-800 text-gray-500 font-mono text-xs w-full text-center'
                    : 'bg-gray-800/60 border border-gray-700 text-gray-200 rounded-tl-sm'
              }`}>
                {msg.role === 'user' && (
                  <p className="text-lg">{msg.content}</p>
                )}
                
                {msg.role === 'assistant' && (
                  <div className="space-y-4">
                    {msg.isError ? (
                      <p className="text-neo-danger flex items-center gap-2"><AlertTriangle className="w-4 h-4"/> {msg.content}</p>
                    ) : (
                      <p className="text-gray-300">{msg.content}</p>
                    )}
                    
                    {msg.sql && (
                      <div className="bg-black/50 rounded-lg p-3 font-mono text-sm border border-gray-700">
                        <div className="flex items-center gap-2 mb-2 text-neo-primary text-xs border-b border-gray-800 pb-2">
                          <Code className="w-3 h-3" /> Generated SQL
                        </div>
                        <pre className="text-gray-400 overflow-x-auto custom-scrollbar pb-2">{msg.sql}</pre>
                      </div>
                    )}
                    
                    {msg.data && (
                      <div className="bg-gray-900 rounded-lg p-3 border border-gray-700">
                        <div className="flex items-center gap-2 mb-3 text-neo-success text-xs border-b border-gray-800 pb-2">
                          <Database className="w-3 h-3" /> Query Results
                        </div>
                        <table className="w-full text-sm text-left">
                          <thead className="text-gray-400 border-b border-gray-800">
                            <tr>
                              {Object.keys(msg.data[0]).map(k => (
                                <th key={k} className="py-2 px-3 uppercase tracking-wider">{k}</th>
                              ))}
                            </tr>
                          </thead>
                          <tbody>
                            {msg.data.map((row, idx) => (
                              <tr key={idx} className="border-b border-gray-800/50 hover:bg-gray-800/30">
                                {Object.values(row).map((val, vIdx) => (
                                  <td key={vIdx} className="py-2 px-3 font-medium text-gray-200">{val}</td>
                                ))}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </motion.div>
          ))}
          {isLoading && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex justify-start">
              <div className="bg-gray-800/60 border border-gray-700 rounded-xl p-4 rounded-tl-sm flex items-center gap-3 text-neo-primary">
                <div className="w-2 h-2 bg-neo-primary rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-neo-primary rounded-full animate-bounce delay-100"></div>
                <div className="w-2 h-2 bg-neo-primary rounded-full animate-bounce delay-200"></div>
              </div>
            </motion.div>
          )}
        </div>

        {/* Input Area */}
        <div className="p-4 border-t border-gray-800 bg-gray-900/50">
          <form onSubmit={handleSubmit} className="relative flex items-center">
            <CornerDownRight className="absolute left-4 text-gray-500 w-5 h-5" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g., Show me the zones with pollution level higher than 60..."
              className="w-full bg-black/40 border border-gray-700 rounded-xl py-4 pl-12 pr-16 text-white placeholder-gray-600 focus:outline-none focus:border-neo-primary focus:ring-1 focus:ring-neo-primary transition-all shadow-inner"
            />
            <button 
              type="submit"
              disabled={!query.trim() || isLoading}
              className="absolute right-2 p-2 bg-neo-primary hover:bg-blue-500 disabled:bg-gray-700 disabled:text-gray-500 text-white rounded-lg transition-colors"
            >
              <Send className="w-5 h-5" />
            </button>
          </form>
        </div>
      </GlassCard>
    </div>
  );
};

export default NLQuery;
