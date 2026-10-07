import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token') || localStorage.getItem('access_token');
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.clear();
      if (window.location.pathname !== '/login') window.location.href = '/login';
    }
    return Promise.reject(err);
  }
);

export default api;

export const authAPI = {
  login: (data) => api.post('/auth/login', data),
  register: (data) => api.post('/auth/register', data),
  logout: () => api.post('/auth/logout'),
  refresh: () => api.post('/auth/refresh'),
};

export const profileAPI = {
  me: () => api.get('/profile/me'),
  create: (data) => api.post('/profile/create', data),
  update: (data) => api.put('/profile/update', data),
  get: (userId) => api.get(`/profile/${userId}`),
};

export const adminAPI = {
  metrics: () => api.get('/admin/dashboard/metrics'),
  users: () => api.get('/admin/users-v2'),
  organizations: () => api.get('/admin/organizations'),
  connectors: () => api.get('/admin/connectors'),
  audit: () => api.get('/admin/audit'),
  paymentsSummary: () => api.get('/admin/payments/summary'),
};

export const educationAPI = {
  countries: () => api.get('/education/countries'),
  createCountry: (data) => api.post('/education/countries', data),
  universities: (countryId) => api.get(`/education/universities${countryId ? `?country_id=${countryId}` : ''}`),
  createUniversity: (data) => api.post('/education/universities', data),
  courses: (univId) => api.get(`/education/courses${univId ? `?university_id=${univId}` : ''}`),
  createCourse: (data) => api.post('/education/courses', data),
  intakeSeats: (courseId) => api.get(`/education/intake-seats/${courseId}`),
  createIntakeSeat: (data) => api.post('/education/intake-seats', data),
  cities: () => api.get('/education/cities'),
  createCity: (data) => api.post('/education/cities', data),
};

export const vendorAPI = {
  list: () => api.get('/vendors/vendors'),
  categories: () => api.get('/vendors/categories'),
  create: (data) => {
    const token = localStorage.getItem('token') || localStorage.getItem('access_token') || '';
    return api.post(`/vendors/create?token=${encodeURIComponent(token)}`, data);
  },
  get: (id) => api.get(`/vendors/vendors/${id}`),
  nearby: (lat, lng) => api.get(`/vendors/nearby?lat=${lat}&lng=${lng}`),
};

export const documentsAPI = {
  upload: (formData) => api.post('/documents/upload', formData, { headers: { 'Content-Type': 'multipart/form-data' } }),
  my: () => api.get('/documents/my'),
  get: (id) => api.get(`/documents/${id}`),
  update: (id, data) => api.put(`/documents/${id}`, data),
  expiringSoon: () => api.get('/documents/expiring/soon'),
  verify: (id) => api.post(`/documents/verify/${id}`),
};

export const applicationsAPI = {
  create: (data) => api.post('/applications/create', data),
  submit: (data) => api.post('/applications/submit', data),
  status: (id) => api.get(`/applications/${id}/status`),
};

export const offersAPI = {
  create: (data) => api.post('/offers/create', data),
  send: (data) => api.post('/offers/send', data),
  accept: (data) => api.post('/offers/accept', data),
  decline: (data) => api.post('/offers/decline', data),
  status: (id) => api.get(`/offers/${id}/status`),
};

export const visaAPI = {
  create: (data) => api.post('/visa/create', data),
  updateStatus: (id, data) => api.put(`/visa/${id}/status`, data),
  get: (id) => api.get(`/visa/${id}`),
  cases: () => api.get('/visa/cases'),
  funnel: () => api.get('/visa/funnel'),
};

export const companyAPI = {
  vacancies: () => api.get('/company/vacancy'),
  createVacancy: (data) => api.post('/company/vacancy', data),
  updateVacancyStatus: (data) => api.put('/company/vacancy/status', data),
  allApplicants: () => api.get('/company/applicants/all'),
  applicants: (vacancyId) => api.get(`/company/applicants/${vacancyId}`),
  updateApplicantStatus: (appId, data) => api.put(`/company/applicants/${appId}/status`, data),
};

export const paymentsAPI = {
  initiate: (data) => api.post('/payments/initiate', data),
  status: (id) => api.get(`/payments/${id}/status`),
};

export const referralAPI = {
  link: (userId) => api.get(`/referral/link/${userId}`),
  track: (data) => api.post('/referral/track', data),
  stats: (userId) => api.get(`/referral/stats/${userId}`),
  leaderboard: () => api.get('/referral/leaderboard'),
};

export const studentLifeAPI = {
  jobs: () => api.get('/student-life/jobs'),
  books: () => api.get('/student-life/books'),
  returnBook: (bookId) => api.put(`/student-life/books/${bookId}/return`),
  me: () => api.get('/student-life/me'),
};

export const dealsAPI = {
  create: (data) => api.post('/deals/create', data),
  get: (id) => api.get(`/deals/${id}`),
  updateStatus: (id, data) => api.put(`/deals/${id}/status`, data),
  myDeals: () => api.get('/deals/my/deals'),
};

export const housingAPI = {
  add: (data) => api.post('/housing/add', data),
  my: () => api.get('/housing/my'),
  updateStatus: (id, data) => api.put(`/housing/${id}/status`, data),
  search: (params = {}) => api.get('/housing/search', { params }),
};

export const agentAPI = {
  candidates: () => api.get('/agent/candidates'),
  funnel: () => api.get('/agent/funnel'),
};

export const brokerAPI = {
  dashboard: (brokerId) => api.get(`/broker/dashboard/${brokerId}`),
  agentPerformance: () => api.get('/broker/agents/performance'),
  clients: () => api.get('/broker/clients'),
};

export const journeyAPI = {
  me: () => api.get('/journey/me'),
  update: (data) => api.post('/journey/update', data),
};

export const notificationsAPI = {
  list: () => api.get('/notifications'),
  markRead: (id) => api.put(`/notifications/${id}/read`),
};

export const searchAPI = {
  opportunities: (q = '', filters = {}) => api.get('/search/opportunities', { params: { q, ...filters } }),
};

export const reportingAPI = {
  funnel: () => api.get('/reporting/funnel'),
  conversion: () => api.get('/reporting/conversion'),
  revenue: () => api.get('/reporting/revenue'),
  activity: () => api.get('/reporting/activity'),
};

export const bulkAPI = {
  exportUsers: () => api.get('/bulk/users/export', { responseType: 'blob' }),
  exportApplications: () => api.get('/bulk/applications/export', { responseType: 'blob' }),
  importOpportunities: (formData) => api.post('/bulk/opportunities/import', formData, { headers: { 'Content-Type': 'multipart/form-data' } }),
};
export const reconciliationAPI = {
  calculate: () => api.get('/reconciliation/calculate'),
  createCommission: (data) => api.post('/reconciliation/commission', data),
  summary: () => api.get('/reconciliation/summary'),
};

export const subscriptionAPI = {
  createPlan: (data) => api.post('/subscription/plan', data),
  assign: (data) => api.post('/subscription/assign', data),
  getUserPlan: (userId) => api.get(`/subscription/${userId}`),
};

export const schedulerAPI = {
  scheduleJob: (data) => api.post('/scheduler/job', data),
  run: () => api.post('/scheduler/run'),
  pending: () => api.get('/scheduler/pending'),
};

export const workflowAPI = {
  definition: (entityType) => api.get(`/workflow/definition/${entityType}`),
  transition: (data) => api.post('/workflow/transition', data),
};

export const contractsAPI = {
  create: (data) => api.post('/contracts/create', data),
  sign: (id) => api.put(`/contracts/${id}/sign`),
};

export const communicationAPI = {
  send: (data) => api.post('/communication/messages/send', data),
  inbox: () => api.get('/communication/messages/inbox'),
  policy: () => api.get('/communication/policy'),
};

export const authExtraAPI = {
  forgotPassword: (data) => api.post('/auth/forgot-password', data),
  resetPassword: (data) => api.post('/auth/reset-password', data),
};
export const publicAPI = {
  directory: () => api.get('/public/directory'),
  jobs: () => api.get('/public/jobs'),
};

export const aiAPI = {
  universityInfo: (data) => api.post('/ai/university-info', data),
  universitiesByCountry: (country) => api.post('/ai/universities-by-country', { country }),
};


export const crmAPI = {
  listLeads: (params = {}) => api.get('/agent/leads', { params }),
  createLead: (data) => api.post('/agent/leads', data),
  getLead: (id) => api.get(`/agent/leads/${id}`),
  updateLead: (id, data) => api.put(`/agent/leads/${id}`, data),
  changeStage: (id, stage) => api.patch(`/agent/leads/${id}/stage`, { stage }),
  addNote: (id, note) => api.post(`/agent/leads/${id}/note`, { note }),
  convertLead: (id, userId) => api.post(`/agent/leads/${id}/convert`, { user_id: userId }),
  addDocument: (id, data) => api.post(`/agent/leads/${id}/documents`, data),
  updateDocStatus: (docId, status, reason = '') => api.patch(`/agent/documents/${docId}/status`, { status, reason }),
  dashboard: () => api.get('/agent/dashboard'),
  uploadDocument: (leadId, documentType, file) => {
    const fd = new FormData();
    fd.append('document_type', documentType);
    fd.append('file', file);
    return api.post(`/agent/leads/${leadId}/documents/upload`, fd, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },
  aiVerify: (docId) => api.post(`/agent/documents/${docId}/ai-verify`),
  listFollowups: (filterType = 'today') => api.get(`/agent/followups?filter_type=${filterType}`),
  setFollowup: (leadId, date) => api.patch(`/agent/leads/${leadId}/followup`, { date }),
  completeFollowup: (leadId, nextDate, note) => api.post(`/agent/leads/${leadId}/followup/complete`, { next_date: nextDate, note }),
  docCheckerCountries: () => api.get('/agent/document-checker/countries'),
  docCheckerRequirements: (code) => api.get(`/agent/document-checker/requirements/${code}`),
  docCheckLead: (leadId) => api.get(`/agent/leads/${leadId}/document-check`),
};