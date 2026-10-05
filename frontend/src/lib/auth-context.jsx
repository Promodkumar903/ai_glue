import { createContext, useContext, useState, useEffect } from 'react';
import api from '../utils/axios';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Load user from localStorage on mount
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    const storedUser = localStorage.getItem('user');
    if (token && storedUser) {
      try {
        setUser(JSON.parse(storedUser));
      } catch (e) {
        console.error('Failed to parse stored user');
      }
    }
    setLoading(false);
  }, []);

  // Login
  const login = async (email, password, role = 'STUDENT') => {
    const res = await api.post('/auth/login', { email, password, role });

    const { access_token, refresh_token, role: returnedRole } = res.data;

    // Save tokens
    localStorage.setItem('access_token', access_token);
    localStorage.setItem('refresh_token', refresh_token);

    // Fetch user profile with the new token
    let userData = null;
    try {
      const profileRes = await api.get('/profile/me', {
        headers: { Authorization: `Bearer ${access_token}` }
      });
      userData = profileRes.data;
    } catch (e) {
      console.error('Failed to fetch profile');
    }

    // Build user object with role
    const finalUser = {
      ...(userData || {}),
      role: returnedRole || role,
    };

    setUser(finalUser);
    localStorage.setItem('user', JSON.stringify(finalUser));

    // Return role so Login.jsx can redirect correctly
    return { role: finalUser.role };
  };

  // Logout
  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}