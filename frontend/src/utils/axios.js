import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' },
});

// âœ… Request interceptor â€” token har request mein bhejo
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// âœ… Response interceptor â€” 401 pe refresh karo, phir retry
api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config;
    const status = error.response?.status;

    // Agar 401 aaya aur abhi retry nahi kiya
    if (status === 401 && !original._retry) {
      original._retry = true;
      const refresh = localStorage.getItem('refresh_token');

      if (refresh) {
        try {
          const res = await axios.post(
            `${api.defaults.baseURL}/auth/refresh`,
            null,
            { params: { refresh_token: refresh } }
          );
          const newToken = res.data.access_token;
          localStorage.setItem('access_token', newToken);
          if (res.data.refresh_token) {
            localStorage.setItem('refresh_token', res.data.refresh_token);
          }
          original.headers.Authorization = `Bearer ${newToken}`;
          return api(original);
        } catch (e) {
          // Refresh bhi fail â€” logout
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          localStorage.removeItem('user');
          localStorage.removeItem('role');
          if (window.location.pathname !== '/login') {
            window.location.href = '/login';
          }
        }
      } else {
        // Refresh token nahi hai â€” logout
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        localStorage.removeItem('role');
        if (window.location.pathname !== '/login') {
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);

export default api;
