import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // 60 seconds
  headers: {
    'Content-Type': 'application/json',
  },
});

export const researchAPI = {
  // Start a new research job
  startResearch: async (researchData) => {
    const response = await api.post('/research', researchData);
    return response.data;
  },

  // Get research job status
  getResearchStatus: async (jobId) => {
    const response = await api.get(`/research/${jobId}`);
    return response.data;
  },

  // Get detailed progress for a research job
  getResearchProgress: async (jobId) => {
    const response = await api.get(`/research/${jobId}/progress`);
    return response.data;
  },

  // List all research jobs
  listJobs: async () => {
    const response = await api.get('/research');
    return response.data;
  },

  // Delete a research job
  deleteJob: async (jobId) => {
    const response = await api.delete(`/research/${jobId}`);
    return response.data;
  },

  // Health check
  healthCheck: async () => {
    const response = await api.get('/health');
    return response.data;
  },
};

// Request interceptor for debugging
api.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method.toUpperCase()} request to ${config.url}`);
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error);
    
    if (error.response) {
      // Server responded with error status
      const message = error.response.data?.detail || error.response.data?.message || 'Server error';
      throw new Error(`${error.response.status}: ${message}`);
    } else if (error.request) {
      // Network error
      throw new Error('Network error - please check if the server is running');
    } else {
      // Other error
      throw new Error(error.message || 'Unknown error occurred');
    }
  }
);

export default api;