import { useState } from 'react';
import { Play, CheckCircle, AlertTriangle, ShieldAlert, Zap, Server, Activity, Wrench } from 'lucide-react';
import GlassCard from '../components/ui/GlassCard';
import { motion, AnimatePresence } from 'framer-motion';

const TestScenarios = () => {
  const [isRunning, setIsRunning] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [logs, setLogs] = useState([]);

  const addLog = (message, type = 'info') => {
    setLogs(prev => [...prev, { time: new Date().toLocaleTimeString(), message, type }]);
  };

  const steps = [
    { title: "Inject Anomaly", icon: Zap, color: "text-neo-warning" },
    { title: "Sensor Statut → SIGNALÉ", icon: AlertTriangle, color: "text-neo-danger" },
    { title: "Create Intervention (DEMANDE)", icon: Wrench, color: "text-neo-primary" },
    { title: "Tech Assigned & Validated", icon: ShieldAlert, color: "text-blue-400" },
    { title: "AI Validation & Resolution", icon: CheckCircle, color: "text-neo-success" }
  ];

  const runSimulation = () => {
    if (isRunning) return;
    setIsRunning(true);
    setCurrentStep(0);
    setLogs([]);
    
    addLog("Simulation started: Sensor Anomaly Workflow", "info");

    const delays = [1500, 3000, 4500, 6500, 8500];

    // Step 1
    setTimeout(() => {
      setCurrentStep(1);
      addLog("Injected extreme pollution spike (AQI > 200) into Capteur #42 data stream.", "warning");
    }, delays[0]);

    // Step 2
    setTimeout(() => {
      setCurrentStep(2);
      addLog("Backend trigger activated. Capteur #42 FSM transitioned from ACTIF to SIGNALÉ.", "error");
    }, delays[1]);

    // Step 3
    setTimeout(() => {
      setCurrentStep(3);
      addLog("Automated Intervention TKT-99 created with priority HAUTE.", "info");
      addLog("Intervention FSM state: DEMANDE.", "info");
    }, delays[2]);

    // Step 4
    setTimeout(() => {
      setCurrentStep(4);
      addLog("Tech 1 (Ali) dispatched to Zone 14.", "info");
      addLog("Intervention FSM state: TECH1_ASSIGNE → TECH2_VALIDE.", "success");
    }, delays[3]);

    // Step 5
    setTimeout(() => {
      setCurrentStep(5);
      addLog("AI Engine validated repair logs. Intervention FSM state: IA_VALIDE → TERMINE.", "success");
      addLog("Capteur #42 FSM transitioned back to ACTIF.", "success");
      addLog("Workflow execution complete.", "info");
      setIsRunning(false);
    }, delays[4]);
  };

  return (
    <div className="flex flex-col gap-6 h-full">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3 text-white">
            <ShieldAlert className="text-red-500 w-8 h-8" />
            Test Scenarios & Control Room
          </h1>
          <p className="text-gray-400 mt-2 text-sm">Simulate complex smart city workflows and validate full-stack behavior</p>
        </div>
        
        <button 
          onClick={runSimulation}
          disabled={isRunning}
          className={`px-6 py-3 rounded-lg font-bold flex items-center gap-2 transition-all ${
            isRunning 
              ? 'bg-gray-800 text-gray-500 cursor-not-allowed' 
              : 'bg-red-500 hover:bg-red-600 text-white shadow-[0_0_20px_rgba(239,68,68,0.4)]'
          }`}
        >
          {isRunning ? (
            <><Activity className="w-5 h-5 animate-pulse" /> Executing...</>
          ) : (
            <><Play className="w-5 h-5" /> Run Scenario: Sensor Anomaly</>
          )}
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 flex-1">
        {/* Visual Pipeline */}
        <GlassCard className="flex flex-col relative overflow-hidden">
          <div className="absolute top-0 right-0 w-64 h-64 bg-red-500/10 blur-[100px] rounded-full pointer-events-none"></div>
          
          <h3 className="text-xl font-bold text-white mb-8 border-b border-gray-800 pb-4">Execution Pipeline</h3>
          
          <div className="flex-1 flex flex-col justify-center px-8 relative">
            {/* Connecting Line */}
            <div className="absolute left-[45px] top-[10%] bottom-[10%] w-0.5 bg-gray-800 z-0"></div>
            
            <div className="space-y-10">
              {steps.map((step, idx) => {
                const isPast = currentStep > idx;
                const isActive = currentStep === idx && isRunning;
                const isPending = currentStep <= idx && !isActive && !isPast;
                const Icon = step.icon;
                
                return (
                  <div key={idx} className="relative z-10 flex items-center gap-6">
                    <div className={`w-12 h-12 rounded-full flex items-center justify-center border-2 transition-all duration-500 ${
                      isActive ? `bg-gray-900 border-red-500 shadow-[0_0_15px_rgba(239,68,68,0.5)]` :
                      isPast ? `bg-gray-800 border-gray-600` :
                      `bg-black border-gray-800 opacity-50`
                    }`}>
                      {isPast ? <CheckCircle className="w-5 h-5 text-gray-400" /> : <Icon className={`w-5 h-5 ${isActive ? step.color : 'text-gray-600'}`} />}
                    </div>
                    
                    <div className={`flex-1 transition-all duration-500 ${isActive ? 'opacity-100 scale-105' : isPending ? 'opacity-40' : 'opacity-60'}`}>
                      <h4 className={`font-bold ${isActive ? 'text-white' : 'text-gray-400'}`}>{step.title}</h4>
                      {isActive && <p className="text-xs text-red-400 mt-1 animate-pulse">Processing step in backend...</p>}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </GlassCard>

        {/* Live Terminal Logs */}
        <GlassCard className="flex flex-col bg-[#0a0b10] border-gray-800">
          <div className="flex items-center gap-3 border-b border-gray-800 pb-4 mb-4">
            <Server className="w-5 h-5 text-gray-400" />
            <h3 className="text-xl font-bold text-gray-200">System Logs</h3>
          </div>
          
          <div className="flex-1 bg-black/50 rounded-xl border border-gray-800 p-4 font-mono text-sm overflow-y-auto custom-scrollbar flex flex-col gap-2">
            <AnimatePresence>
              {logs.map((log, i) => (
                <motion.div 
                  key={i}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="flex items-start gap-3"
                >
                  <span className="text-gray-600 shrink-0">[{log.time}]</span>
                  <span className={`${
                    log.type === 'error' ? 'text-red-400' :
                    log.type === 'warning' ? 'text-yellow-400' :
                    log.type === 'success' ? 'text-green-400' :
                    'text-blue-300'
                  }`}>
                    {log.message}
                  </span>
                </motion.div>
              ))}
            </AnimatePresence>
            
            {logs.length === 0 && !isRunning && (
              <div className="text-gray-600 italic mt-4 text-center">
                Waiting for simulation to start...
              </div>
            )}
            
            {isRunning && (
              <div className="flex items-center gap-2 mt-2 text-gray-500">
                <span className="w-2 h-2 rounded-full bg-gray-500 animate-pulse"></span>
                Waiting for backend events...
              </div>
            )}
          </div>
        </GlassCard>
      </div>
    </div>
  );
};

export default TestScenarios;
