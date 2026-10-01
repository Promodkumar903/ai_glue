import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../utils/axios';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    const savedRole = localStorage.getItem('role');

    if (token) {
      api.get('/profile/me')
        .then(res => {
          // Profile में Role Add करो (localStorage से)
          const userData = res.data;
          userData.role = savedRole || 'STUDENT';
          setUser(userData);
        })
        .catch(() => {
          localStorage.removeItem('token');
          localStorage.removeItem('role');
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
    
    // ✅ Role को localStorage में Save करो
    if (role) {
      localStorage.setItem('role', role);
    }

    // User Object बनाओ — Role के साथ
    if (res.data.user) {
      const userData = res.data.user;
      userData.role = role || localStorage.getItem('role') || 'STUDENT';
      setUser(userData);
    } else {
      const profile = await api.get('/profile/me');
      const userData = profile.data;
      userData.role = role || localStorage.getItem('role') || 'STUDENT';
      setUser(userData);
    }
    return res.data;
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);