import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../utils/axios';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    try {
      const saved = localStorage.getItem('user');
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    const savedRole = localStorage.getItem('role');

    if (token) {
      api.get('/profile/me')
        .then(res => {
          const userData = res.data;
          userData.role = savedRole || 'STUDENT';
          localStorage.setItem('user', JSON.stringify(userData));
          setUser(userData);
        })
        .catch(() => {
          localStorage.removeItem('token');
          localStorage.removeItem('role');
          localStorage.removeItem('user');
          localStorage.removeItem('refresh_token');
          setUser(null);
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (email, password, role) => {
    const res = await api.post('/auth/login', { email, password, role });

    localStorage.setItem('token', res.data.access_token);
    if (res.data.refresh_token) {
      localStorage.setItem('refresh_token', res.data.refresh_token);
    }
    if (role) {
      localStorage.setItem('role', role);
    }

    let userData;
    if (res.data.user) {
      userData = res.data.user;
      userData.role = role || localStorage.getItem('role') || 'STUDENT';
    } else {
      const profile = await api.get('/profile/me');
      userData = profile.data;
      userData.role = role || localStorage.getItem('role') || 'STUDENT';
    }

    localStorage.setItem('user', JSON.stringify(userData));
    setUser(userData);
    return res.data;
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    localStorage.removeItem('user');
    localStorage.removeItem('refresh_token');
    setUser(null);
    window.location.href = '/login';
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);