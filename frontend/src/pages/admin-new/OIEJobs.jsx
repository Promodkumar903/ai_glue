import React, { useState, useEffect } from 'react';
import {
  Briefcase, Building2, MessageSquare, CheckCircle, XCircle,
  Phone, Mail, MapPin, Star, Search, AlertCircle, Sparkles
} from 'lucide-react';
import api from '../../services/api';

const TABS = [
  { key: 'jobs', label: 'Jobs', icon: Briefcase },
  { key: 'registry', label: 'Job Agents', icon: Building2 },
  { key: 'requests', label: 'Requests', icon: MessageSquare },
  { key: 'log', label: 'HR Contact Log', icon: Phone },
];

function StatCard({ label, value, color }) {
  const colors = {
    blue: 'text-blue-600', green: 'text-green-600', yellow: 'text-yellow-600',
    purple: 'text-purple-600', orange: 'text-orange-600', pink: 'text-pink-600',
  };
  return (
    <div className="bg-white rounded-xl border border-slate-200 p-3">
      <div className="text-xs text-slate-500">{label}</div>
      <div className={`text-2xl font-bold ${colors[color] || colors.blue}`}>
        {value !== undefined && value !== null ? value : 0}
      </div>
    </div>
  );
}

export default function OIEJobs() {
  const [activeTab, setActiveTab] = useState('jobs');
  const [stats, setStats] = useState({});
  const [jobs, setJobs] = useState([]);
  const [registry, setRegistry] = useState([]);
  const [requests, setRequests] = useState([]);
  const [log, setLog] = useState([]);
  const [filter, setFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [selectedJob, setSelectedJob] = useState(null);
  const [jobDetail, setJobDetail] = useState(null);

  useEffect(() => { loadStats(); }, []);
  useEffect(() => {
    if (activeTab === 'jobs') loadJobs();
    else if (activeTab === 'registry') loadRegistry();
    else if (activeTab === 'requests') loadRequests();
    else if (activeTab === 'log') loadLog();
  }, [activeTab, statusFilter]);

  const loadStats = async () => {
    try { const r = await api.get('/admin/oie/stats/jobs'); setStats(r.data || {}); } catch (e) {}
  };
  const loadJobs = async () => {
    try {
      const r = await api.get('/admin/oie/jobs', { params: { status: statusFilter, limit: 100 } });
      setJobs(r.data.jobs || []);
    } catch (e) {}
  };
  const loadRegistry = async () => {
    try { const r = await api.get('/admin/oie/job-registry', { params: { limit: 100 } }); setRegistry(r.data.entities || []); } catch (e) {}
  };
  const loadRequests = async () => {
    try { const r = await api.get('/admin/oie/job-requests', { params: { limit: 100 } }); setRequests(r.data.requests || []); } catch (e) {}
  };
  const loadLog = async () => {
    try { const r = await api.get('/admin/oie/job-contacts', { params: { limit: 100 } }); setLog(r.data.log || []); } catch (e) {}
  };
  const openJobDetail = async (jobId) => {
    setSelectedJob(jobId);
    try { const r = await api.get(`/admin/oie/job-detail/${jobId}`); setJobDetail(r.data); } catch (e) {}
  };
  const verifyCompany = async (company) => {
    const notes = prompt(`Notes for verifying ${company}?`);
    if (!notes) return;
    try { await api.post(`/admin/oie/verify/${company}`, { admin_id: 'admin', notes }); loadJobs(); loadStats(); } catch (e) { alert('Failed'); }
  };
  const rejectCompany = async (company) => {
    const reason = prompt(`Reason for rejecting ${company}?`);
    if (!reason) return;
    try { await api.post(`/admin/oie/reject/${company}`, { admin_id: 'admin', notes: reason }); loadJobs(); loadStats(); } catch (e) { alert('Failed'); }
  };

  const filteredJobs = jobs.filter(j =>
    !filter ||
    j.company_name?.toLowerCase().includes(filter.toLowerCase()) ||
    j.job_title?.toLowerCase().includes(filter.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-slate-50 p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
          <Sparkles className="w-6 h-6 text-purple-600" />
          OIE Jobs — Opportunity Intelligence
        </h1>
        <p className="text-sm text-slate-500 mt-1">Verified jobs, agents, HR contacts</p>

        <div className="grid grid-cols-2 md:grid-cols-6 gap-3 mt-4">
          <StatCard label="Total Jobs" value={stats.total_jobs} color="blue" />
          <StatCard label="Verified" value={stats.verified_jobs} color="green" />
          <StatCard label="Pending" value={stats.pending_jobs} color="yellow" />
          <StatCard label="Job Agents" value={stats.registry_total} color="purple" />
          <StatCard label="Requests" value={stats.requests_pending} color="orange" />
          <StatCard label="HR Contacts" value={stats.contact_attempts} color="pink" />
        </div>
      </div>

      <div className="flex gap-1 border-b border-slate-200 mb-4 overflow-x-auto">
        {TABS.map(t => (
          <button key={t.key} onClick={() => setActiveTab(t.key)}
            className={`flex items-center gap-2 px-4 py-2 text-sm font-medium border-b-2 transition ${
              activeTab === t.key ? 'border-purple-600 text-purple-600' : 'border-transparent text-slate-500'
            }`}>
            <t.icon className="w-4 h-4" />{t.label}
          </button>
        ))}
      </div>

      {activeTab === 'jobs' && (
        <>
          <div className="flex gap-2 mb-4">
            <div className="flex-1 relative">
              <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
              <input type="text" placeholder="Search company or job..." value={filter}
                onChange={e => setFilter(e.target.value)}
                className="w-full pl-9 pr-4 py-2 border border-slate-300 rounded-lg text-sm" />
            </div>
            <select value={statusFilter} onChange={e => setStatusFilter(e.target.value)}
              className="px-3 py-2 border border-slate-300 rounded-lg text-sm">
              <option value="">All Status</option>
              <option value="VERIFIED">Verified</option>
              <option value="PENDING">Pending</option>
              <option value="REJECTED">Rejected</option>
            </select>
          </div>

          <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-slate-50">
                <tr className="text-left text-xs text-slate-500 uppercase">
                  <th className="px-4 py-3">Company</th>
                  <th className="px-4 py-3">Job Title</th>
                  <th className="px-4 py-3">Country</th>
                  <th className="px-4 py-3">Benefits</th>
                  <th className="px-4 py-3">HR Email</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredJobs.map(j => (
                  <tr key={j.id} className="border-t border-slate-100 hover:bg-slate-50">
                    <td className="px-4 py-3 font-medium">{j.company_name}</td>
                    <td className="px-4 py-3 text-slate-600">{j.job_title}</td>
                    <td className="px-4 py-3"><span className="flex items-center gap-1 text-xs"><MapPin className="w-3 h-3" />{j.country}</span></td>
                    <td className="px-4 py-3">
                      <div className="flex gap-1 text-xs">
                        {j.visa_free ? <span className="px-1.5 py-0.5 bg-green-100 text-green-700 rounded">Visa</span> : null}
                        {j.ticket_free ? <span className="px-1.5 py-0.5 bg-blue-100 text-blue-700 rounded">Ticket</span> : null}
                        {j.accommodation ? <span className="px-1.5 py-0.5 bg-purple-100 text-purple-700 rounded">Stay</span> : null}
                        {j.overtime_available ? <span className="px-1.5 py-0.5 bg-orange-100 text-orange-700 rounded">OT</span> : null}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-xs text-slate-500">{(j.hr_email || 'N/A').slice(0, 22)}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 text-xs rounded-full font-medium ${
                        j.verification_status === 'VERIFIED' ? 'bg-green-100 text-green-700' :
                        j.verification_status === 'REJECTED' ? 'bg-red-100 text-red-700' :
                        'bg-yellow-100 text-yellow-700'
                      }`}>{j.verification_status || 'PENDING'}</span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex gap-1">
                        <button onClick={() => openJobDetail(j.id)} className="px-2 py-1 text-xs bg-slate-100 text-slate-700 rounded">View</button>
                        {j.verification_status !== 'VERIFIED' && (
                          <button onClick={() => verifyCompany(j.company_name)} className="px-2 py-1 text-xs bg-green-100 text-green-700 rounded">
                            <CheckCircle className="w-3 h-3" />
                          </button>
                        )}
                        {j.verification_status !== 'REJECTED' && (
                          <button onClick={() => rejectCompany(j.company_name)} className="px-2 py-1 text-xs bg-red-100 text-red-700 rounded">
                            <XCircle className="w-3 h-3" />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
                {filteredJobs.length === 0 && (
                  <tr><td colSpan="7" className="px-4 py-8 text-center text-slate-400">No jobs</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </>
      )}

      {activeTab === 'registry' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {registry.map(e => (
            <div key={e.id} className="bg-white rounded-xl border border-slate-200 p-4">
              <div className="font-semibold">{e.name}</div>
              <div className="text-xs text-slate-500">{e.entity_type} · {e.country}</div>
              <div className="flex items-center gap-2 mt-3">
                <div className="flex-1 bg-slate-100 rounded-full h-2">
                  <div className="bg-purple-500 h-2 rounded-full" style={{ width: `${e.trust_score}%` }}></div>
                </div>
                <span className="text-sm font-bold">{e.trust_score}</span>
              </div>
            </div>
          ))}
          {registry.length === 0 && <div className="col-span-3 text-center text-slate-400 py-8">No job agents yet</div>}
        </div>
      )}

      {activeTab === 'requests' && (
        <div className="space-y-3">
          {requests.map(r => (
            <div key={r.id} className="bg-white rounded-xl border border-slate-200 p-4">
              <div className="font-semibold">{r.subject}</div>
              <div className="text-xs text-slate-500">{r.from_name} → {r.to_name}</div>
              <div className="text-sm text-slate-600 mt-2">{r.message}</div>
            </div>
          ))}
          {requests.length === 0 && <div className="text-center text-slate-400 py-8">No job requests</div>}
        </div>
      )}

      {activeTab === 'log' && (
        <div className="space-y-2">
          {log.map(l => (
            <div key={l.id} className="bg-white rounded-lg border border-slate-200 p-3">
              <div className="flex items-center gap-2">
                <span className="font-semibold text-sm">{l.company_name}</span>
                <span className="text-xs px-2 py-0.5 bg-slate-100 rounded">{l.attempt_type}</span>
                <span className={`text-xs px-2 py-0.5 rounded ${
                  l.outcome === 'VERIFIED' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'
                }`}>{l.outcome}</span>
              </div>
              {l.notes && <div className="text-sm text-slate-600 mt-1">{l.notes}</div>}
            </div>
          ))}
          {log.length === 0 && <div className="text-center text-slate-400 py-8">No HR contacts logged</div>}
        </div>
      )}

      {selectedJob && jobDetail && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4"
          onClick={() => { setSelectedJob(null); setJobDetail(null); }}>
          <div className="bg-white rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto"
            onClick={e => e.stopPropagation()}>
            <div className="sticky top-0 bg-white border-b p-4 flex items-center justify-between">
              <h2 className="text-lg font-bold">{jobDetail.company_name} — {jobDetail.job_title}</h2>
              <button onClick={() => { setSelectedJob(null); setJobDetail(null); }}>
                <XCircle className="w-5 h-5" />
              </button>
            </div>
            <div className="p-6 space-y-4">
              <div className="text-sm">Legal: {jobDetail.company_legal_name} | Industry: {jobDetail.industry}</div>
              <div className="text-sm">Hours: {jobDetail.hours_per_day}h × {jobDetail.days_per_week}d | Off: {jobDetail.off_days}</div>
              <div className="text-sm">HR: {jobDetail.hr_name} — {jobDetail.hr_email} — {jobDetail.hr_phone}</div>
              {jobDetail.company_health && (
                <div className="text-sm">Health: {jobDetail.company_health.revenue_usd} ({jobDetail.company_health.credit_rating})</div>
              )}
              {jobDetail.visa_stats && (
                <div className="text-sm">Visa: {jobDetail.visa_stats.visa_type} — {jobDetail.visa_stats.approval_rate}% approval</div>
              )}
              {jobDetail.reviews && (
                <div className="text-sm">Reviews: {jobDetail.reviews.overall_rating}/5 ({jobDetail.reviews.total_reviews})</div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}