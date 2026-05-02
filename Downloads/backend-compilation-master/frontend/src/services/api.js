import axios from 'axios';

const API_URL = 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getZones = () => api.get('/zones');
export const getZonesStatus = () => api.get('/zones/status');
export const getCapteurs = () => api.get('/capteurs');
export const getMesures = (limit = 50) => api.get(`/mesures?limit=${limit}`);
export const getInterventions = () => api.get('/interventions');
export const getVehicules = () => api.get('/vehicules');
export const getTechniciens = () => api.get('/techniciens');
export const getCitoyens = () => api.get('/citoyens');
export const getDashboardKPIs = () => api.get('/kpis/dashboard');
export const generateAIReport = (type = 'global') => api.post('/ia/rapport', { type });
export const getAISuggestions = () => api.get('/ia/suggestions');
export const chatWithAI = (message) => api.post('/ia/chat', { message });

export const nlQuery = (query) => api.post('/nl/query', { query });
