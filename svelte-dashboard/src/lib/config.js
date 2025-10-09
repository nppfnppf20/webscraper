// Centralized API configuration
// This will use environment variable in production, localhost for development
let apiUrl;
try {
  apiUrl = import.meta.env.VITE_API_BASE_URL;
} catch (e) {
  apiUrl = undefined;
}

export const API_BASE_URL = apiUrl || 'http://127.0.0.1:8000/api';
export const API_BASE = API_BASE_URL.replace('/api', ''); // For direct endpoint access