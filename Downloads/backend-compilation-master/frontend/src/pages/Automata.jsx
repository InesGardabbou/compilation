import { useState, useEffect, useRef } from 'react';
import { Share2, Activity, Truck, Wrench, Search, Info } from 'lucide-react';
import { api } from '../services/api';

// ─── FSM Data ────────────────────────────────────────────────────────────────

const DATA = {
  capteur: {
    title: "Cycle de vie d'un capteur",
    viewBox: '0 0 560 320',
    nodes: [
      { id: 'INACTIF', label: 'INACTIF', x: 30, y: 138, w: 110, h: 44 },
      { id: 'ACTIF', label: 'ACTIF', x: 195, y: 138, w: 90, h: 44 },
      { id: 'SIGNALÉ', label: 'SIGNALÉ', x: 345, y: 58, w: 105, h: 44 },
      { id: 'MAINTENANCE', label: 'MAINTENANCE', x: 415, y: 138, w: 130, h: 44 },
      { id: 'HORS SERVICE', label: 'HORS SERVICE', x: 330, y: 218, w: 125, h: 44 },
    ],
    edges: [
      { from: 'INACTIF', to: 'ACTIF', label: 'installation', path: 'M140,160 L195,160', lx: 167, ly: 150 },
      { from: 'ACTIF', to: 'SIGNALÉ', label: 'anomalie', path: 'M270,148 Q310,85 345,80', lx: 300, ly: 95 },
      { from: 'ACTIF', to: 'HORS SERVICE', label: 'panne', path: 'M248,182 Q285,230 330,240', lx: 278, ly: 235 },
      { from: 'SIGNALÉ', to: 'MAINTENANCE', label: 'intervention', path: 'M450,80 Q482,100 482,138', lx: 494, ly: 112 },
      { from: 'MAINTENANCE', to: 'ACTIF', label: 'réparation', path: 'M415,148 Q350,105 285,148', lx: 345, ly: 110 },
      { from: 'MAINTENANCE', to: 'HORS SERVICE', label: 'panne', path: 'M482,182 Q482,218 455,240', lx: 495, ly: 218 },
    ],
    transitions: [
      { from: 'INACTIF', event: "installation", to: 'ACTIF' },
      { from: 'ACTIF', event: "détection d'anomalie", to: 'SIGNALÉ' },
      { from: 'ACTIF', event: "panne", to: 'HORS SERVICE' },
      { from: 'SIGNALÉ', event: "intervention", to: 'MAINTENANCE' },
      { from: 'MAINTENANCE', event: "réparation", to: 'ACTIF' },
      { from: 'MAINTENANCE', event: "panne", to: 'HORS SERVICE' },
    ],
    statusMap: {
      'INACTIF': 'INACTIF', 'ACTIF': 'ACTIF',
      'SIGNALE': 'SIGNALÉ', 'SIGNALÉ': 'SIGNALÉ',
      'EN_MAINTENANCE': 'MAINTENANCE', 'MAINTENANCE': 'MAINTENANCE',
      'HORS_SERVICE': 'HORS SERVICE', 'HORS SERVICE': 'HORS SERVICE',
    },
  },

  intervention: {
    title: "Processus de validation d'intervention",
    viewBox: '0 0 560 310',
    nodes: [
      { id: 'DEMANDE', label: 'DEMANDE', x: 20, y: 130, w: 100, h: 44 },
      { id: 'TECH1', label: ['TECH1', 'ASSIGNÉ'], x: 150, y: 130, w: 100, h: 50 },
      { id: 'TECH2', label: ['TECH2', 'VALIDÉ'], x: 285, y: 130, w: 100, h: 50 },
      { id: 'IA_VALIDE', label: 'IA VALIDÉ', x: 415, y: 130, w: 105, h: 44 },
      { id: 'TERMINÉ', label: 'TERMINÉ', x: 430, y: 240, w: 95, h: 44 },
    ],
    edges: [
      { from: 'DEMANDE', to: 'TECH1', label: 'assignation', path: 'M120,152 L150,152', lx: 135, ly: 142 },
      { from: 'TECH1', to: 'TECH2', label: 'vérification', path: 'M250,155 L285,155', lx: 267, ly: 145 },
      { from: 'TECH2', to: 'IA_VALIDE', label: 'approbation IA', path: 'M385,152 L415,152', lx: 400, ly: 142 },
      { from: 'IA_VALIDE', to: 'TERMINÉ', label: 'clôture', path: 'M467,174 Q467,212 467,240', lx: 450, ly: 215 },
    ],
    transitions: [
      { from: 'DEMANDE', event: 'assignation tech 1', to: 'TECH1_ASSIGNÉ' },
      { from: 'TECH1_ASSIGNÉ', event: 'vérification tech 2', to: 'TECH2_VALIDE' },
      { from: 'TECH2_VALIDE', event: 'approbation IA', to: 'IA_VALIDE' },
      { from: 'IA_VALIDE', event: 'clôture', to: 'TERMINÉ' },
    ],
    statusMap: {
      'DEMANDE': 'DEMANDE', 'PLANIFIÉE': 'DEMANDE', 'PLANIFIE': 'DEMANDE',
      'TECH1_ASSIGNE': 'TECH1', 'EN_COURS': 'TECH1',
      'TECH2_VALIDE': 'TECH2',
      'IA_VALIDE': 'IA_VALIDE',
      'TERMINE': 'TERMINÉ', 'TERMINÉ': 'TERMINÉ', 'ANNULE': 'TERMINÉ',
    },
  },

  vehicle: {
    title: "Trajet d'un véhicule autonome",
    viewBox: '0 0 560 320',
    nodes: [
      { id: 'STATIONNÉ', label: 'STATIONNÉ', x: 30, y: 148, w: 115, h: 44 },
      { id: 'EN_ROUTE', label: 'EN ROUTE', x: 215, y: 58, w: 110, h: 44 },
      { id: 'EN_PANNE', label: 'EN PANNE', x: 215, y: 240, w: 110, h: 44 },
      { id: 'ARRIVÉ', label: 'ARRIVÉ', x: 400, y: 148, w: 100, h: 44 },
    ],
    edges: [
      { from: 'STATIONNÉ', to: 'EN_ROUTE', label: 'démarrage', path: 'M120,158 Q168,100 215,80', lx: 158, ly: 105 },
      { from: 'EN_ROUTE', to: 'ARRIVÉ', label: 'destination', path: 'M325,80 Q365,100 400,158', lx: 372, ly: 105 },
      { from: 'EN_ROUTE', to: 'EN_PANNE', label: 'problème', path: 'M270,102 L270,240', lx: 278, ly: 175 },
      { from: 'EN_PANNE', to: 'STATIONNÉ', label: 'remorquage', path: 'M215,262 Q130,282 95,192', lx: 148, ly: 288 },
      { from: 'ARRIVÉ', to: 'STATIONNÉ', label: 'stationnement', path: 'M400,170 Q290,245 145,178', lx: 288, ly: 232 },
    ],
    transitions: [
      { from: 'STATIONNÉ', event: 'démarrage', to: 'EN_ROUTE' },
      { from: 'EN_ROUTE', event: 'atteint destination', to: 'ARRIVÉ' },
      { from: 'EN_ROUTE', event: 'problème technique', to: 'EN_PANNE' },
      { from: 'EN_PANNE', event: 'remorquage', to: 'STATIONNÉ' },
      { from: 'ARRIVÉ', event: 'stationnement', to: 'STATIONNÉ' },
    ],
    statusMap: {
      'STATIONNE': 'STATIONNÉ', 'STATIONNÉ': 'STATIONNÉ', 'PLANIFIE': 'STATIONNÉ',
      'EN_ROUTE': 'EN_ROUTE', 'EN ROUTE': 'EN_ROUTE', 'ACTIF': 'EN_ROUTE',
      'EN_PANNE': 'EN_PANNE', 'EN PANNE': 'EN_PANNE', 'MAINTENANCE': 'EN_PANNE',
      'ARRIVE': 'ARRIVÉ', 'ARRIVÉ': 'ARRIVÉ', 'TERMINE': 'ARRIVÉ',
    },
  },
};

// ─── Style Helpers ────────────────────────────────────────────────────────────

function getNodeStyle(nodeId, currentNodeId, currentFSM) {
  const hasSelection = currentNodeId !== null;
  if (!hasSelection) return { fill: '#1a1e28', stroke: '#374151', sw: 1, textColor: '#94a3b8', opacity: 1, glow: false, dashed: false };
  if (nodeId === currentNodeId) return { fill: '#0d2d1e', stroke: '#00d4aa', sw: 2, textColor: '#00d4aa', opacity: 1, glow: true, dashed: false, glowId: 'glow-teal' };
  const isNext = DATA[currentFSM].edges.some(e => e.from === currentNodeId && e.to === nodeId);
  if (isNext) return { fill: '#1a1530', stroke: '#7c6aff', sw: 2, textColor: '#a78bfa', opacity: 1, glow: true, dashed: true, glowId: 'glow-purple' };
  return { fill: '#13161d', stroke: '#1e2130', sw: 1, textColor: '#374151', opacity: 0.3, glow: false };
}

function getEdgeStyle(edge, currentNodeId) {
  const hasSelection = currentNodeId !== null;
  if (!hasSelection) return { stroke: '#2d3448', opacity: 1, animated: false, width: 1.5, textColor: '#3d4560' };
  if (edge.from === currentNodeId) return { stroke: '#7c6aff', opacity: 1, animated: true, width: 2, textColor: '#7c6aff' };
  return { stroke: '#1e2130', opacity: 0.15, animated: false, width: 1, textColor: '#252a38' };
}

// ─── FSM Diagram SVG ─────────────────────────────────────────────────────────

function FsmDiagram({ fsmKey, currentNodeId }) {
  const fsm = DATA[fsmKey];

  return (
    <svg
      viewBox={fsm.viewBox}
      className="w-full h-full"
      xmlns="http://www.w3.org/2000/svg"
      style={{ display: 'block' }}
    >
      <defs>
        <marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">
          <path d="M1 1L9 5L1 9" fill="none" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" stroke="#2d3448" />
        </marker>
        <marker id="arr-active" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">
          <path d="M1 1L9 5L1 9" fill="none" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" stroke="#7c6aff" />
        </marker>
        <filter id="glow-teal">
          <feGaussianBlur stdDeviation="3" result="b" />
          <feMerge><feMergeNode in="b" /><feMergeNode in="SourceGraphic" /></feMerge>
        </filter>
        <filter id="glow-purple">
          <feGaussianBlur stdDeviation="3" result="b" />
          <feMerge><feMergeNode in="b" /><feMergeNode in="SourceGraphic" /></feMerge>
        </filter>
        <style>{`
          @keyframes dash { to { stroke-dashoffset: -20; } }
          .fsm-animated { stroke-dasharray: 5 4; animation: dash 1.2s linear infinite; }
          .fsm-text { font-family: 'JetBrains Mono', monospace; }
          .fsm-label { font-family: 'Space Grotesk', sans-serif; }
        `}</style>
      </defs>

      {/* Edges */}
      {fsm.edges.map((edge, i) => {
        const s = getEdgeStyle(edge, currentNodeId);
        const marker = edge.from === currentNodeId ? 'url(#arr-active)' : 'url(#arr)';
        return (
          <g key={i} opacity={s.opacity}>
            <path
              d={edge.path}
              fill="none"
              stroke={s.stroke}
              strokeWidth={s.width}
              markerEnd={marker}
              className={s.animated ? 'fsm-animated' : ''}
            />
            <text
              x={edge.lx}
              y={edge.ly}
              textAnchor="middle"
              fontSize="9"
              fill={s.textColor}
              className="fsm-label"
            >
              {edge.label}
            </text>
          </g>
        );
      })}

      {/* Nodes */}
      {fsm.nodes.map((node) => {
        const s = getNodeStyle(node.id, currentNodeId, fsmKey);
        const cx = node.x + node.w / 2;
        const cy = node.y + node.h / 2;
        const lines = Array.isArray(node.label) ? node.label : [node.label];
        return (
          <g
            key={node.id}
            opacity={s.opacity}
            filter={s.glow ? `url(#${s.glowId})` : undefined}
          >
            <rect
              x={node.x} y={node.y}
              width={node.w} height={node.h}
              rx="8"
              fill={s.fill}
              stroke={s.stroke}
              strokeWidth={s.sw}
              strokeDasharray={s.dashed ? '5 3' : undefined}
            />
            {lines.length === 1 ? (
              <text
                x={cx} y={cy}
                textAnchor="middle"
                dominantBaseline="central"
                fontSize="12"
                fontWeight="600"
                fill={s.textColor}
                className="fsm-text"
              >
                {lines[0]}
              </text>
            ) : (
              <>
                <text x={cx} y={cy - 9} textAnchor="middle" dominantBaseline="central" fontSize="11" fontWeight="600" fill={s.textColor} className="fsm-text">{lines[0]}</text>
                <text x={cx} y={cy + 9} textAnchor="middle" dominantBaseline="central" fontSize="11" fontWeight="600" fill={s.textColor} className="fsm-text">{lines[1]}</text>
              </>
            )}
            {node.id === currentNodeId && (
              <circle cx={node.x + node.w - 10} cy={node.y + 10} r="4" fill="#00d4aa" />
            )}
          </g>
        );
      })}
    </svg>
  );
}

// ─── Main Component ───────────────────────────────────────────────────────────

const Automata = () => {
  const [activeFSM, setActiveFSM] = useState('capteur');
  const [items, setItems] = useState([]);
  const [selectedItem, setSelectedItem] = useState(null);
  const [currentNodeId, setCurrentNodeId] = useState(null);
  const [loading, setLoading] = useState(false);

  // Fetch items when FSM changes
  useEffect(() => {
    const fetchItems = async () => {
      setLoading(true);
      setSelectedItem(null);
      setCurrentNodeId(null);
      try {
        const endpoints = { capteur: '/capteurs', intervention: '/interventions', vehicle: '/vehicules' };
        const res = await api.get(endpoints[activeFSM]);
        setItems(res?.data || []);
      } catch {
        setItems([]);
      } finally {
        setLoading(false);
      }
    };
    fetchItems();
  }, [activeFSM]);

  const handleSelectItem = (value) => {
    if (!value) { setSelectedItem(null); setCurrentNodeId(null); return; }
    const item = JSON.parse(value);
    setSelectedItem(item);
    const statusMap = DATA[activeFSM].statusMap;
    const key = item.statut?.toUpperCase().trim();
    setCurrentNodeId(statusMap[key] || statusMap[key?.replace(/ /g, '_')] || null);
  };

  const getItemId = (item) => item.id_capteur || item.id_intervention || item.id_vehicule || item.id;

  const nextStates = currentNodeId
    ? DATA[activeFSM].transitions.filter(t => t.from === currentNodeId)
    : [];

  const tabs = [
    { key: 'capteur', label: 'Capteurs', icon: <Activity className="w-3 h-3" /> },
    { key: 'intervention', label: 'Interventions', icon: <Wrench className="w-3 h-3" /> },
    { key: 'vehicle', label: 'Véhicules', icon: <Truck className="w-3 h-3" /> },
  ];

  return (
    <div style={{ fontFamily: "'Space Grotesk', sans-serif" }} className="flex flex-col gap-4 h-[calc(100vh-100px)] p-1">

      {/* ── Header ── */}
      <div className="flex flex-wrap justify-between items-start gap-3">
        <div>
          <h1 className="text-2xl font-semibold flex items-center gap-2" style={{ color: '#e2e8f0' }}>
            <Share2 style={{ color: '#7c6aff' }} className="w-5 h-5" />
            1.1 Automates à États Finis
          </h1>
          <p className="text-xs mt-1" style={{ color: '#64748b' }}>
            Modélisation DFA des processus opérationnels
          </p>
        </div>

        {/* Tabs */}
        <div className="flex gap-1 p-1 rounded-xl border" style={{ background: '#1a1e28', borderColor: '#252a38' }}>
          {tabs.map(tab => (
            <button
              key={tab.key}
              onClick={() => setActiveFSM(tab.key)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-200"
              style={activeFSM === tab.key
                ? { background: '#7c6aff', color: '#fff', boxShadow: '0 0 14px rgba(124,106,255,0.4)' }
                : { background: 'transparent', color: '#64748b' }
              }
            >
              {tab.icon} {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* ── Instance selector ── */}
      <div className="flex items-center gap-2">
        <Search className="w-3.5 h-3.5 shrink-0" style={{ color: '#64748b' }} />
        <select
          className="flex-1 rounded-lg text-xs px-3 py-2 outline-none transition-colors"
          style={{ background: '#1a1e28', color: '#e2e8f0', border: '1px solid #252a38', fontFamily: "'Space Grotesk', sans-serif" }}
          value={selectedItem ? JSON.stringify(selectedItem) : ''}
          onChange={e => handleSelectItem(e.target.value)}
          disabled={loading}
        >
          <option value="">— Inspecter une instance réelle —</option>
          {items.map((item, idx) => {
            const id = getItemId(item);
            return (
              <option key={idx} value={JSON.stringify(item)}>
                {activeFSM.toUpperCase()} #{id} — Statut: {item.statut}
              </option>
            );
          })}
        </select>

        {currentNodeId && (
          <span
            className="shrink-0 text-xs px-3 py-1 rounded-full font-mono font-semibold"
            style={{ background: 'rgba(0,212,170,0.12)', color: '#00d4aa', border: '1px solid rgba(0,212,170,0.25)' }}
          >
            ◉ {currentNodeId}
          </span>
        )}
      </div>

      {/* ── Main Layout ── */}
      <div className="flex flex-col xl:flex-row gap-4 flex-1 min-h-0">

        {/* Diagram panel */}
        <div
          className="flex-1 rounded-xl border flex flex-col overflow-hidden relative min-h-[500px]"
          style={{ background: '#13161d', borderColor: '#252a38' }}
        >
          {/* Panel header */}
          <div
            className="flex items-center justify-between px-5 py-3 border-b shrink-0"
            style={{ borderColor: '#252a38' }}
          >
            <span className="text-sm font-bold uppercase tracking-widest" style={{ color: '#64748b' }}>
              {DATA[activeFSM].title}
            </span>
            {/* Legend */}
            <div className="flex items-center gap-5">
              <div className="flex items-center gap-2 text-sm" style={{ color: '#64748b' }}>
                <span className="w-2.5 h-2.5 rounded-full inline-block" style={{ background: '#00d4aa', boxShadow: '0 0 8px #00d4aa' }} />
                État actuel
              </div>
              <div className="flex items-center gap-2 text-sm" style={{ color: '#64748b' }}>
                <span className="w-2.5 h-2.5 rounded-full inline-block" style={{ background: '#7c6aff', boxShadow: '0 0 8px #7c6aff' }} />
                États suivants
              </div>
              <div className="flex items-center gap-2 text-sm" style={{ color: '#64748b' }}>
                <span className="w-2.5 h-2.5 rounded-full inline-block" style={{ background: '#374151' }} />
                Inactif
              </div>
            </div>
          </div>

          {/* SVG Diagram */}
          <div className="flex-1 flex items-center justify-center p-8 min-h-0" style={{ background: '#0d0f14' }}>
            <FsmDiagram fsmKey={activeFSM} currentNodeId={currentNodeId} />
          </div>
        </div>

        {/* Right column */}
        <div className="flex flex-col gap-4 min-h-0 w-full xl:w-[450px] shrink-0">

          {/* Info card */}
          {selectedItem && (
            <div
              className="rounded-xl border px-5 py-4 flex items-start gap-3 shrink-0 transition-colors"
              style={{ background: currentNodeId ? 'rgba(0,212,170,0.05)' : '#1a1e28', borderColor: currentNodeId ? 'rgba(0,212,170,0.3)' : '#252a38' }}
            >
              <Info className="w-5 h-5 shrink-0 mt-0.5" style={{ color: currentNodeId ? '#00d4aa' : '#64748b' }} />
              <p className="text-sm leading-relaxed" style={{ color: '#e2e8f0' }}>
                {currentNodeId
                  ? nextStates.length > 0
                    ? <span>État actuel : <strong style={{color:'#00d4aa'}}>{currentNodeId}</strong> — {nextStates.length} transition(s) disponible(s).</span>
                    : <span>État actuel : <strong style={{color:'#00d4aa'}}>{currentNodeId}</strong> — État terminal.</span>
                  : 'Statut non mappé dans l\'automate.'
                }
              </p>
            </div>
          )}

          {/* Transition table */}
          <div className="rounded-xl border flex flex-col flex-1 overflow-hidden" style={{ background: '#13161d', borderColor: '#252a38' }}>
            <div className="px-5 py-3 border-b shrink-0" style={{ borderColor: '#252a38' }}>
              <h3 className="text-sm font-semibold uppercase tracking-widest" style={{ color: '#e2e8f0' }}>
                Table de Transition δ(Q, Σ) → Q'
              </h3>
            </div>

            {/* Table header */}
            <div
              className="grid grid-cols-3 border-b shrink-0"
              style={{ borderColor: '#252a38', background: '#1a1e28' }}
            >
              {['État (Q)', 'Événement', 'Suivant (Q\')'].map(h => (
                <div key={h} className="px-4 py-3 text-xs font-semibold uppercase tracking-wider" style={{ color: '#64748b' }}>
                  {h}
                </div>
              ))}
            </div>

            {/* Table rows */}
            <div className="flex-1 overflow-y-auto custom-scrollbar">
              {DATA[activeFSM].transitions.map((row, idx) => {
                const isHighlighted = currentNodeId && row.from === currentNodeId;
                return (
                  <div
                    key={idx}
                    className="grid grid-cols-3 border-b transition-all duration-200"
                    style={{
                      borderColor: '#1e2130',
                      background: isHighlighted ? 'rgba(124,106,255,0.08)' : 'transparent',
                      borderLeft: isHighlighted ? '3px solid #7c6aff' : '3px solid transparent',
                    }}
                  >
                    <div className="px-4 py-3.5 text-sm font-mono" style={{ color: '#60a5fa' }}>{row.from}</div>
                    <div className="px-4 py-3.5 text-sm italic" style={{ color: '#94a3b8', fontFamily: "'Space Grotesk', sans-serif" }}>{row.event}</div>
                    <div className="px-4 py-3.5 text-sm font-mono" style={{ color: '#00d4aa' }}>{row.to}</div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Automata;