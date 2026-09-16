import axios from 'axios';

/**
 * Shared Axios instance for OpenIRM API communication.
 * Base URL is driven by VITE_API_BASE_URL (defaults to /api/v1 if unset).
 */
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || '/api/v1';

export const apiClient = axios.create({
  baseURL: apiBaseUrl,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
});

// Response interceptor for unified logging and error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      'An unexpected network error occurred.';
    return Promise.reject(new Error(message));
  }
);

export default apiClient;
