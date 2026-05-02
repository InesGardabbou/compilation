import { useState, useRef } from 'react';
import { Brain, Sparkles, FileText, Download, Zap, MessageSquare, Send, Bot, User } from 'lucide-react';
import GlassCard from '../components/ui/GlassCard';
import { motion } from 'framer-motion';
import { generateAIReport, getAISuggestions, chatWithAI } from '../services/api';
import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';

const AIInsights = () => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [report, setReport] = useState(null);
  
  // Chatbot state
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [isChatting, setIsChatting] = useState(false);
  
  const reportRef = useRef(null);

  const downloadPDF = async () => {
    if (!reportRef.current) return;
    try {
      const canvas = await html2canvas(reportRef.current, { scale: 2 });
      const imgData = canvas.toDataURL('image/png');
      const pdf = new jsPDF('p', 'mm', 'a4');
      const pdfWidth = pdf.internal.pageSize.getWidth();
      const pdfHeight = (canvas.height * pdfWidth) / canvas.width;
      
      pdf.addImage(imgData, 'PNG', 0, 0, pdfWidth, pdfHeight);
      pdf.save('neo-sousse-report.pdf');
    } catch (error) {
      console.error("Error generating PDF", error);
    }
  };

  const handleChat = async (e) => {
    e.preventDefault();
    if (!chatInput.trim()) return;
    
    const userMsg = chatInput;
    setChatMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setChatInput('');
    setIsChatting(true);
    
    try {
      const res = await chatWithAI(userMsg);
      if (res.data.success) {
        setChatMessages(prev => [...prev, { role: 'bot', content: res.data.response }]);
      } else {
        const errorMsg = res.data.error || "Erreur inconnue";
        setChatMessages(prev => [...prev, { role: 'bot', content: `Erreur: ${errorMsg}. (Vérifiez votre clé API et redémarrez le backend)` }]);
      }
    } catch (error) {
      setChatMessages(prev => [...prev, { role: 'bot', content: "Erreur de connexion au serveur. Assurez-vous que le backend est lancé." }]);
    } finally {
      setIsChatting(false);
    }
  };

  const generateReport = async () => {
    setIsGenerating(true);
    try {
      const [reportRes, suggestionsRes] = await Promise.all([
        generateAIReport('global'),
        getAISuggestions()
      ]);

      if (reportRes.data.success) {
        setReport({
          title: "City Intelligence Report",
          date: new Date().toLocaleDateString(),
          summary: reportRes.data.resume,
          score: reportRes.data.score,
          suggestions: suggestionsRes.data.success ? suggestionsRes.data.suggestions : []
        });
      }
    } catch (error) {
      console.error("Error generating report", error);
      setReport({
        title: "Error Generating Report",
        date: new Date().toLocaleDateString(),
        summary: "Failed to connect to AI Engine.",
        suggestions: []
      });
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto h-full flex flex-col">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <Brain className="text-neo-purple w-8 h-8" />
            AI Insights Engine
          </h1>
          <p className="text-gray-400 mt-2">Powered by Neo-Sousse Core Intelligence</p>
        </div>
        
        <button 
          onClick={generateReport}
          disabled={isGenerating}
          className="bg-gradient-to-r from-neo-purple to-neo-primary hover:from-purple-500 hover:to-blue-500 text-white px-6 py-3 rounded-lg font-medium flex items-center gap-2 transition-all shadow-[0_0_20px_rgba(139,92,246,0.4)] hover:shadow-[0_0_30px_rgba(139,92,246,0.6)] disabled:opacity-50"
        >
          {isGenerating ? (
            <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1, ease: "linear" }}>
              <Sparkles className="w-5 h-5" />
            </motion.div>
          ) : (
            <FileText className="w-5 h-5" />
          )}
          {isGenerating ? 'Compiling Data...' : 'Generate New Report'}
        </button>
      </div>

      <div className="flex-1 grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-2 flex flex-col h-full min-h-[400px]">
          {report ? (
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex-1"
            >
              <GlassCard className="h-full">
                <div ref={reportRef} className="p-2">
                  <div className="flex justify-between items-start mb-6">
                    <div>
                      <h2 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-white to-gray-400">{report.title}</h2>
                      <p className="text-neo-primary font-mono text-sm mt-1">{report.date}</p>
                    </div>
                    <button onClick={downloadPDF} className="p-2 bg-gray-800 rounded hover:bg-neo-primary hover:text-white transition-colors text-gray-300 shadow-md" title="Télécharger PDF">
                      <Download className="w-5 h-5" />
                    </button>
                  </div>
                  
                  <div className="prose prose-invert max-w-none">
                    <h3 className="text-lg font-semibold text-neo-purple flex items-center gap-2">
                      <Sparkles className="w-4 h-4" /> Executive Summary & Analysis
                    </h3>
                    <p className="text-gray-300 leading-relaxed text-sm bg-gray-900/50 p-4 rounded-lg border border-gray-800 whitespace-pre-line">
                      {report.summary}
                    </p>

                    {report.suggestions && report.suggestions.length > 0 && (
                      <div className="mt-6">
                        <h3 className="text-lg font-semibold text-blue-400 flex items-center gap-2 mb-3">
                          <Zap className="w-4 h-4" /> Actionable Suggestions
                        </h3>
                        <div className="grid grid-cols-1 gap-2">
                          {report.suggestions.map((sug, idx) => (
                            <div key={idx} className="bg-blue-900/10 border border-blue-800/30 p-2 rounded-lg flex items-start gap-3">
                              <div className="bg-blue-500/20 p-1.5 rounded-md mt-0.5">
                                <FileText className="w-3 h-3 text-blue-400" />
                              </div>
                              <div>
                                <p className="text-gray-200 text-xs leading-relaxed">
                                  <strong>{sug.type || "Action"}:</strong> {sug.message} <br/>
                                  <span className="text-blue-300">Recommandation: {sug.action}</span>
                                </p>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </GlassCard>
            </motion.div>
          ) : (
            <div className="flex-1 flex items-center justify-center bg-gray-900/20 rounded-xl border border-gray-800/50">
              <div className="text-center">
                <Brain className="w-24 h-24 text-gray-800 mx-auto mb-6" />
                <p className="text-gray-500 text-lg">System standing by. Generate a report to run the AI analysis.</p>
              </div>
            </div>
          )}
        </div>

        <div className="md:col-span-1 flex flex-col gap-6">
          {/* Chatbot Interface - ALWAYS VISIBLE */}
          <GlassCard className="flex flex-col h-[400px]">
            <div className="flex items-center gap-2 mb-4 shrink-0">
              <MessageSquare className="text-neo-primary w-6 h-6" />
              <h3 className="text-lg font-bold text-white">Assistant Virtuel</h3>
            </div>
            
            <div className="flex-1 overflow-y-auto mb-4 bg-gray-900/50 rounded-lg p-3 border border-gray-800 flex flex-col gap-3">
              {chatMessages.length === 0 ? (
                <p className="text-gray-500 text-center my-auto text-sm">Posez-moi vos questions sur Neo-Sousse.</p>
              ) : (
                chatMessages.map((msg, idx) => (
                  <div key={idx} className={`flex gap-2 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                    {msg.role === 'bot' && <div className="w-6 h-6 rounded-full bg-neo-purple/20 flex items-center justify-center shrink-0"><Bot className="w-4 h-4 text-neo-purple" /></div>}
                    <div className={`p-2 rounded-xl text-sm max-w-[85%] ${msg.role === 'user' ? 'bg-neo-primary text-white rounded-tr-none' : 'bg-gray-800 text-gray-200 rounded-tl-none whitespace-pre-line'}`}>
                      {msg.content}
                    </div>
                  </div>
                ))
              )}
              {isChatting && (
                <div className="flex gap-2 justify-start">
                  <div className="w-6 h-6 rounded-full bg-neo-purple/20 flex items-center justify-center shrink-0"><Bot className="w-4 h-4 text-neo-purple" /></div>
                  <div className="p-2 rounded-xl bg-gray-800 text-gray-400 rounded-tl-none flex items-center gap-1">
                    <motion.div animate={{ opacity: [0.5, 1, 0.5] }} transition={{ repeat: Infinity, duration: 1.5 }}>•</motion.div>
                    <motion.div animate={{ opacity: [0.5, 1, 0.5] }} transition={{ repeat: Infinity, duration: 1.5, delay: 0.2 }}>•</motion.div>
                    <motion.div animate={{ opacity: [0.5, 1, 0.5] }} transition={{ repeat: Infinity, duration: 1.5, delay: 0.4 }}>•</motion.div>
                  </div>
                </div>
              )}
            </div>
            
            <form onSubmit={handleChat} className="flex gap-2 shrink-0">
              <input 
                type="text" 
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                placeholder="Question..." 
                className="flex-1 min-w-0 bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-neo-primary text-sm"
                disabled={isChatting}
              />
              <button 
                type="submit" 
                disabled={isChatting || !chatInput.trim()}
                className="bg-neo-primary hover:bg-blue-600 text-white p-2 rounded-lg transition-colors disabled:opacity-50 flex items-center justify-center"
              >
                <Send className="w-4 h-4" />
              </button>
            </form>
          </GlassCard>

          {/* Recommended Actions */}
          {report && report.suggestions && report.suggestions.length > 0 && (
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
              <GlassCard className="border-t-4 border-t-neo-warning">
                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  <Zap className="text-neo-warning w-5 h-5" /> 
                  Actions Recommandées
                </h3>
                <ul className="space-y-3">
                  {report.suggestions.map((sug, i) => (
                    <li key={i} className="flex flex-col gap-1 text-sm text-gray-300 bg-gray-900/40 p-2 rounded border border-gray-800 hover:border-neo-warning/50 transition-colors cursor-default">
                      <div className="flex gap-2 items-start">
                        <span className="text-neo-warning font-bold mt-0.5">{i + 1}.</span>
                        <div className="flex flex-col">
                          <span className="font-semibold text-white">{typeof sug === 'string' ? sug : sug.action}</span>
                          {typeof sug !== 'string' && (
                            <span className="text-gray-400 text-xs mt-0.5">
                              {sug.type} • {sug.entite}
                            </span>
                          )}
                        </div>
                      </div>
                    </li>
                  ))}
                </ul>
                <button className="w-full mt-4 py-2 bg-neo-warning/10 hover:bg-neo-warning/20 text-neo-warning text-sm border border-neo-warning/30 rounded font-medium transition-colors">
                  Appliquer Toutes
                </button>
              </GlassCard>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AIInsights;
