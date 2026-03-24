import axios from 'axios';
import type { ApiError } from '@/types';

const apiClient = axios.create({
  baseURL: (process.env.NEXT_PUBLIC_PROXY_URL || 'http://localhost:8000') + '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ─── Request Interceptor ───
apiClient.interceptors.request.use(
  (config) => config,
  (error) => Promise.reject(error)
);

// ─── Response Interceptor ───
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const apiError: ApiError = {
      message: error.response?.data?.message || error.response?.data?.error || error.message || 'An unexpected error occurred',
      status: error.response?.status || 500,
      details: error.response?.data?.details,
    };

    return Promise.reject(apiError);
  }
);

export default apiClient;
