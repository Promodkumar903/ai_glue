const login = async (email, password) => {
  const res = await api.post('/auth/login', { email, password });
  localStorage.setItem('token', res.data.access_token);
  
  // अगर Backend से user Object नहीं आ रहा – तो `/profile/me` से Fetch करो
  if (res.data.user) {
    setUser(res.data.user);
  } else {
    const profile = await api.get('/profile/me');
    setUser(profile.data);
  }
  return res.data;
};