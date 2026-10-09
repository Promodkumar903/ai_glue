import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  Briefcase, Building2, MessageSquare, CheckCircle, XCircle,
  Phone, Mail, Globe, MapPin, Star, Search, AlertCircle, Sparkles,
  GraduationCap
} from 'lucide-react';
import api from '../../services/api';

const TABS = [
  { key: 'jobs', label: 'Jobs', icon: Briefcase },
  { key: 'studies', label: 'Studies', icon: GraduationCap },
  { key: 'registry', label: 'Registry', icon: Building2 },
  { key: 'requests', label: 'Requests', icon: MessageSquare },
  { key: 'log', label: 'Contact Log', icon: Phone },
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

export default function OIEDashboard() {
  const [searchParams] = useSearchParams();
  const [activeTab, setActiveTab] = useState(searchParams.get('tab') || 'jobs');

  const [stats, setStats] = useState({});
  const [studyStats, setStudyStats] = useState({
    total: 4957, free: 392, pr: 1346, scholarship: 3639, countries: 25,
  });

  const [jobs, setJobs] = useState([]);
  const [studies, setStudies] = useState([]);
  const [studyCountries, setStudyCountries] = useState([]);
  const [registry, setRegistry] = useState([]);
  const [requests, setRequests] = useState([]);
  const [log, setLog] = useState([]);

  const [filter, setFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [studyFilter, setStudyFilter] = useState('');
  const [studyCountry, setStudyCountry] = useState('');
  const [studyOnlyFree, setStudyOnlyFree] = useState(false);
  const [studyOnlyPR, setStudyOnlyPR] = useState(false);
  const [studyOnlySchol, setStudyOnlySchol] = useState(false);

  const [selectedJob, setSelectedJob] = useState(null);
  const [jobDetail, setJobDetail] = useState(null);

  useEffect(() => {
    const tab = searchParams.get('tab');
    if (tab && TABS.find(t => t.key === tab)) {
      setActiveTab(tab);
    }
  }, [searchParams]);

  useEffect(() => {
    loadStats();
  }, []);

  useEffect(() => {
    if (activeTab === 'jobs') loadJobs();
    else if (activeTab === 'studies') loadStudies();
    else if (activeTab === 'registry') loadRegistry();
    else if (activeTab === 'requests') loadRequests();
    else if (activeTab === 'log') loadLog();
  }, [activeTab, statusFilter]);

  const loadStats = async () => {
    try {
      const r = await api.get('/admin/oie/stats');
      setStats(r.data || {});
    } catch (e) { console.error(e); }
  };

  const loadJobs = async () => {
    try {
      const r = await api.get('/admin/oie/jobs', { params: { status: statusFilter, limit: 100 } });
      setJobs(r.data.jobs || []);
    } catch (e) { console.error(e); }
  };

  const loadStudies = async () => {
    try {
      const r = await api.get('/admin/oie/studies', {
        params: {
          country: studyCountry, search: studyFilter,
          free_only: studyOnlyFree, pr_only: studyOnlyPR,
          scholarship_only: studyOnlySchol, limit: 200,
        }
      });
      const data = r.data.studies || [];
      setStudies(data);
      setStudyCountries(r.data.countries || []);
      setStudyStats({
        total: data.length || 4957,
        free: data.filter(s => s.free_education).length,
        pr: data.filter(s => s.pr_possible).length,
        scholarship: data.filter(s => s.scholarship_available).length,
        countries: (r.data.countries || []).length,
      });
    } catch (e) { console.error(e); }
  };

  const loadRegistry = async () => {
    try {
      const r = await api.get('/admin/oie/registry', { params: { limit: 100 } });
      setRegistry(r.data.entities || []);
    } catch (e) { console.error(e); }
  };

  const loadRequests = async () => {
    try {
      const r = await api.get('/admin/oie/requests', { params: { limit: 100 } });
      setRequests(r.data.requests || []);
    } catch (e) { console.error(e); }
  };

  const loadLog = async () => {
    try {
      const r = await api.get('/admin/oie/contact-log', { params: { limit: 100 } });
      setLog(r.data.log || []);
    } catch (e) { console.error(e); }
  };

  const openJobDetail = async (jobId) => {
    setSelectedJob(jobId);
    try {
      const r = await api.get(`/admin/oie/job-detail/${jobId}`);
      setJobDetail(r.data);
    } catch (e) { console.error(e); }
  };

  const verifyCompany = async (company) => {
    const notes = prompt(`Notes for verifying ${company}?`);
    if (!notes) return;
    try {
      await api.post(`/admin/oie/verify/${company}`, { admin_id: 'admin', notes });
      alert('Verified!');
      loadJobs();
      loadStats();
    } catch (e) { alert('Failed: ' + e.message); }
  };

  const rejectCompany = async (company) => {
    const reason = prompt(`Reason for rejecting ${company}?`);
    if (!reason) return;
    try {
      await api.post(`/admin/oie/reject/${company}`, { admin_id: 'admin', notes: reason });
      alert('Rejected');
      loadJobs();
      loadStats();
    } catch (e) { alert('Failed: ' + e.message); }
  };

  const filteredJobs = jobs.filter(j =>
    !filter ||
    j.company_name?.toLowerCase().includes(filter.toLowerCase()) ||
    j.job_title?.toLowerCase().includes(filter.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-slate-50 p-6">
      {/* HEADER */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
          <Sparkles className="w-6 h-6 text-purple-600" />
          OIE — Opportunity Intelligence Engine
        </h1>
        <p className="text-sm text-slate-500 mt-1">
          Verified jobs, universities, agent registry, and HR verification
        </p>

        {/* STATS — Changes by tab */}
        <div className="grid grid-cols-2 md:grid-cols-6 gap-3 mt-4">
          {activeTab === 'studies' ? (
            <>
              <StatCard label="Universities" value={studyStats.total} color="blue" />
              <StatCard label="Free Tuition" value={studyStats.free} color="green" />
              <StatCard label="PR Pathway" value={studyStats.pr} color="purple" />
              <StatCard label="Scholarships" value={studyStats.scholarship} color="orange" />
              <StatCard label="Countries" value={studyStats.countries} color="pink" />
              <StatCard label="Showing" value={studies.length} color="yellow" />
            </>
          ) : (
            <>
              <StatCard label="Total Jobs" value={stats.total_jobs} color="blue" />
              <StatCard label="Verified" value={stats.verified_jobs} color="green" />
              <StatCard label="Pending" value={stats.pending_jobs} color="yellow" />
              <StatCard label="Registry" value={stats.registry_total} color="purple" />
              <StatCard label="Requests" value={stats.requests_pending} color="orange" />
              <StatCard label="Contacts" value={stats.contact_attempts} color="pink" />
            </>
          )}
        </div>
      </div>

      {/* TABS */}
      <div className="flex gap-1 border-b border-slate-200 mb-4 overflow-x-auto">
        {TABS.map(t => (
          <button
            key={t.key}
            onClick={() => setActiveTab(t.key)}
            className={`flex items-center gap-2 px-4 py-2 text-sm font-medium border-b-2 transition ${
              activeTab === t.key
                ? 'border-purple-600 text-purple-600'
                : 'border-transparent text-slate-500 hover:text-slate-700'
            }`}
          >
            <t.icon className="w-4 h-4" />
            {t.label}
          </button>
        ))}
      </div>

      {/* JOBS TAB */}
      {activeTab === 'jobs' && (
        <>
          <div className="flex gap-2 mb-4">
            <div className="flex-1 relative">
              <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
              <input
                type="text"
                placeholder="Search company or job..."
                value={filter}
                onChange={e => setFilter(e.target.value)}
                className="w-full pl-9 pr-4 py-2 border border-slate-300 rounded-lg text-sm"
              />
            </div>
            <select
              value={statusFilter}
              onChange={e => setStatusFilter(e.target.value)}
              className="px-3 py-2 border border-slate-300 rounded-lg text-sm"
            >
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
                  <th className="px-4 py-3">HR Contact</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredJobs.map(j => (
                  <tr key={j.id} className="border-t border-slate-100 hover:bg-slate-50">
                    <td className="px-4 py-3 font-medium">{j.company_name}</td>
                    <td className="px-4 py-3 text-slate-600">{j.job_title}</td>
                    <td className="px-4 py-3">
                      <span className="flex items-center gap-1 text-xs">
                        <MapPin className="w-3 h-3" />{j.country}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex gap-1 text-xs">
                        {j.visa_free ? <span className="px-1.5 py-0.5 bg-green-100 text-green-700 rounded">Visa</span> : null}
                        {j.ticket_free ? <span className="px-1.5 py-0.5 bg-blue-100 text-blue-700 rounded">Ticket</span> : null}
                        {j.accommodation ? <span className="px-1.5 py-0.5 bg-purple-100 text-purple-700 rounded">Stay</span> : null}
                        {j.overtime_available ? <span className="px-1.5 py-0.5 bg-orange-100 text-orange-700 rounded">OT</span> : null}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-xs">
                      <div className="flex items-center gap-1 text-slate-500">
                        <Mail className="w-3 h-3" />{(j.hr_email || 'N/A').slice(0, 20)}
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 text-xs rounded-full font-medium ${
                        j.verification_status === 'VERIFIED' ? 'bg-green-100 text-green-700' :
                        j.verification_status === 'REJECTED' ? 'bg-red-100 text-red-700' :
                        'bg-yellow-100 text-yellow-700'
                      }`}>
                        {j.verification_status || 'PENDING'}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex gap-1">
                        <button
                          onClick={() => openJobDetail(j.id)}
                          className="px-2 py-1 text-xs bg-slate-100 text-slate-700 rounded hover:bg-slate-200"
                        >View</button>
                        {j.verification_status !== 'VERIFIED' && (
                          <button
                            onClick={() => verifyCompany(j.company_name)}
                            className="px-2 py-1 text-xs bg-green-100 text-green-700 rounded hover:bg-green-200"
                          ><CheckCircle className="w-3 h-3" /></button>
                        )}
                        {j.verification_status !== 'REJECTED' && (
                          <button
                            onClick={() => rejectCompany(j.company_name)}
                            className="px-2 py-1 text-xs bg-red-100 text-red-700 rounded hover:bg-red-200"
                          ><XCircle className="w-3 h-3" /></button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
                {filteredJobs.length === 0 && (
                  <tr><td colSpan="7" className="px-4 py-8 text-center text-slate-400">No jobs found</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </>
      )}

      {/* STUDIES TAB */}
      {activeTab === 'studies' && (
        <>
          <div className="flex flex-wrap gap-2 mb-4">
            <div className="flex-1 min-w-[200px] relative">
              <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
              <input
                type="text"
                placeholder="Search university..."
                value={studyFilter}
                onChange={e => setStudyFilter(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && loadStudies()}
                className="w-full pl-9 pr-4 py-2 border border-slate-300 rounded-lg text-sm"
              />
            </div>
            <select
              value={studyCountry}
              onChange={e => setStudyCountry(e.target.value)}
              className="px-3 py-2 border border-slate-300 rounded-lg text-sm"
            >
              <option value="">All Countries</option>
              {studyCountries.map(c => (
                <option key={c.country} value={c.country}>{c.country} ({c.cnt})</option>
              ))}
            </select>
            <button
              onClick={() => setStudyOnlyFree(!studyOnlyFree)}
              className={`px-3 py-2 rounded-lg text-sm border ${
                studyOnlyFree ? 'bg-green-500 text-white border-green-500' : 'bg-white border-slate-300'
              }`}
            >Free Tuition</button>
            <button
              onClick={() => setStudyOnlyPR(!studyOnlyPR)}
              className={`px-3 py-2 rounded-lg text-sm border ${
                studyOnlyPR ? 'bg-blue-500 text-white border-blue-500' : 'bg-white border-slate-300'
              }`}
            >PR Pathway</button>
            <button
              onClick={() => setStudyOnlySchol(!studyOnlySchol)}
              className={`px-3 py-2 rounded-lg text-sm border ${
                studyOnlySchol ? 'bg-purple-500 text-white border-purple-500' : 'bg-white border-slate-300'
              }`}
            >Scholarship</button>
            <button
              onClick={loadStudies}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg text-sm"
            >Apply</button>
          </div>

          <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-slate-50">
                <tr className="text-left text-xs text-slate-500 uppercase">
                  <th className="px-4 py-3">University</th>
                  <th className="px-4 py-3">Country</th>
                  <th className="px-4 py-3">Tuition</th>
                  <th className="px-4 py-3">Hostel/mo</th>
                  <th className="px-4 py-3">Scholarship</th>
                  <th className="px-4 py-3">PR</th>
                  <th className="px-4 py-3">Work</th>
                  <th className="px-4 py-3">Apply</th>
                </tr>
              </thead>
              <tbody>
                {studies.map(s => (
                  <tr key={s.id} className="border-t border-slate-100 hover:bg-slate-50">
                    <td className="px-4 py-3 font-medium">{s.university_name}</td>
                    <td className="px-4 py-3 text-slate-600">{s.country}</td>
                    <td className="px-4 py-3">
                      {s.free_education ? (
                        <span className="text-green-600 font-semibold">FREE</span>
                      ) : s.tuition_fee > 0 ? (
                        <span>${s.tuition_fee.toLocaleString()}/yr</span>
                      ) : (
                        <span className="text-slate-400">N/A</span>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      {s.hostel_cost_monthly_usd > 0 ? `$${Math.round(s.hostel_cost_monthly_usd)}` : '-'}
                    </td>
                    <td className="px-4 py-3">
                      {s.scholarship_available ? (
                        <span className="text-purple-600 font-semibold">
                          ${Math.round((s.scholarship_amount_usd || 0) / 1000)}K
                        </span>
                      ) : '-'}
                    </td>
                    <td className="px-4 py-3">
                      {s.pr_possible ? <span className="text-blue-600">Yes</span> : '-'}
                    </td>
                    <td className="px-4 py-3 text-xs text-slate-600">
                      {s.post_study_work_years ? `${s.post_study_work_years}mo` : '-'}
                    </td>
                    <td className="px-4 py-3">
                      {s.application_url ? (
                        <a href={s.application_url} target="_blank" rel="noreferrer"
                          className="text-blue-500 text-xs hover:underline">Link</a>
                      ) : '-'}
                    </td>
                  </tr>
                ))}
                {studies.length === 0 && (
                  <tr><td colSpan="8" className="px-4 py-8 text-center text-slate-400">No universities found</td></tr>
                )}
              </tbody>
            </table>
          </div>

          <div className="mt-3 text-xs text-slate-500 text-right">
            Showing {studies.length} universities
          </div>
        </>
      )}

      {/* REGISTRY TAB */}
      {activeTab === 'registry' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {registry.map(e => (
            <div key={e.id} className="bg-white rounded-xl border border-slate-200 p-4">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <div className="font-semibold text-slate-900">{e.name}</div>
                  <div className="text-xs text-slate-500">{e.entity_type} · {e.country}</div>
                </div>
                <div className={`px-2 py-1 text-xs rounded-full ${
                  e.is_verified ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'
                }`}>
                  {e.is_verified ? 'Verified' : 'Pending'}
                </div>
              </div>
              <div className="flex items-center gap-2 mb-3">
                <div className="flex-1 bg-slate-100 rounded-full h-2">
                  <div className="bg-purple-500 h-2 rounded-full" style={{ width: `${e.trust_score}%` }}></div>
                </div>
                <span className="text-sm font-bold">{e.trust_score}</span>
              </div>
              {e.website && (
                <a href={e.website} target="_blank" rel="noreferrer"
                  className="text-xs text-blue-500 flex items-center gap-1 mb-1">
                  <Globe className="w-3 h-3" /> {e.website.slice(0, 40)}
                </a>
              )}
              {e.fake_flags && (
                <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded text-xs text-red-700 flex items-start gap-1">
                  <AlertCircle className="w-3 h-3 mt-0.5" />
                  <span>Flags: {e.fake_flags}</span>
                </div>
              )}
            </div>
          ))}
          {registry.length === 0 && (
            <div className="col-span-3 text-center text-slate-400 py-8">No entities</div>
          )}
        </div>
      )}

      {/* REQUESTS TAB */}
      {activeTab === 'requests' && (
        <div className="space-y-3">
          {requests.map(r => (
            <div key={r.id} className="bg-white rounded-xl border border-slate-200 p-4">
              <div className="flex items-start justify-between">
                <div>
                  <div className="font-semibold">{r.subject}</div>
                  <div className="text-xs text-slate-500 mt-1">
                    From: {r.from_name} → To: {r.to_name}
                  </div>
                </div>
                <span className={`px-2 py-1 text-xs rounded-full ${
                  r.status === 'ACCEPTED' ? 'bg-green-100 text-green-700' :
                  r.status === 'DECLINED' ? 'bg-red-100 text-red-700' :
                  'bg-yellow-100 text-yellow-700'
                }`}>{r.status}</span>
              </div>
              {r.message && <div className="mt-2 text-sm text-slate-600">{r.message}</div>}
              <div className="mt-2 text-xs text-slate-400">{(r.created_at || '').slice(0, 16)}</div>
            </div>
          ))}
          {requests.length === 0 && (
            <div className="text-center text-slate-400 py-8">No requests</div>
          )}
        </div>
      )}

      {/* CONTACT LOG TAB */}
      {activeTab === 'log' && (
        <div className="space-y-2">
          {log.map(l => (
            <div key={l.id} className="bg-white rounded-lg border border-slate-200 p-3 flex items-start gap-3">
              <div className={`w-2 h-2 rounded-full mt-2 ${
                l.outcome === 'VERIFIED' ? 'bg-green-500' :
                l.outcome === 'DECLINED' ? 'bg-red-500' :
                l.outcome === 'CALL_BACK' ? 'bg-yellow-500' : 'bg-slate-300'
              }`}></div>
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <span className="font-semibold text-sm">{l.company_name}</span>
                  <span className="text-xs px-2 py-0.5 bg-slate-100 rounded">{l.attempt_type}</span>
                  <span className={`text-xs px-2 py-0.5 rounded font-medium ${
                    l.outcome === 'VERIFIED' ? 'bg-green-100 text-green-700' :
                    l.outcome === 'DECLINED' ? 'bg-red-100 text-red-700' :
                    'bg-yellow-100 text-yellow-700'
                  }`}>{l.outcome}</span>
                </div>
                {l.notes && <div className="text-sm text-slate-600 mt-1">{l.notes}</div>}
                <div className="text-xs text-slate-400 mt-1">
                  {(l.attempt_date || '').slice(0, 16)} · by {l.contacted_by}
                </div>
              </div>
            </div>
          ))}
          {log.length === 0 && (
            <div className="text-center text-slate-400 py-8">No contact attempts</div>
          )}
        </div>
      )}

      {/* JOB DETAIL MODAL */}
      {selectedJob && jobDetail && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4"
          onClick={() => { setSelectedJob(null); setJobDetail(null); }}>
          <div className="bg-white rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto"
            onClick={e => e.stopPropagation()}>
            <div className="sticky top-0 bg-white border-b p-4 flex items-center justify-between">
              <h2 className="text-lg font-bold">
                {jobDetail.company_name} — {jobDetail.job_title}
              </h2>
              <button onClick={() => { setSelectedJob(null); setJobDetail(null); }}>
                <XCircle className="w-5 h-5" />
              </button>
            </div>

            <div className="p-6 space-y-6">
              <div>
                <h3 className="text-sm font-semibold text-slate-500 uppercase mb-2">Company Profile</h3>
                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div><span className="text-slate-500">Legal Name:</span> {jobDetail.company_legal_name || 'N/A'}</div>
                  <div><span className="text-slate-500">Industry:</span> {jobDetail.industry || 'N/A'}</div>
                  <div><span className="text-slate-500">Size:</span> {jobDetail.company_size || 'N/A'}</div>
                  <div><span className="text-slate-500">Founded:</span> {jobDetail.founded_year || 'N/A'}</div>
                </div>
              </div>

              {jobDetail.salary_min_usd > 0 && (
                <div>
                  <h3 className="text-sm font-semibold text-slate-500 uppercase mb-2">Salary</h3>
                  <div className="text-2xl font-bold text-green-600">
                    {jobDetail.salary_currency} {jobDetail.salary_min_usd} - {jobDetail.salary_max_usd} / {jobDetail.salary_period}
                  </div>
                </div>
              )}

              <div>
                <h3 className="text-sm font-semibold text-slate-500 uppercase mb-2">Work Conditions</h3>
                <div className="grid grid-cols-3 gap-3 text-sm">
                  <div>{jobDetail.hours_per_day}h × {jobDetail.days_per_week}d</div>
                  <div>Off: {jobDetail.off_days}</div>
                  <div>OT: {jobDetail.overtime_available ? `Yes (${jobDetail.overtime_rate})` : 'No'}</div>
                </div>
              </div>

              <div>
                <h3 className="text-sm font-semibold text-slate-500 uppercase mb-2">Benefits</h3>
                <div className="flex flex-wrap gap-2">
                  {jobDetail.visa_free ? <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm">Free Visa</span> : null}
                  {jobDetail.ticket_free ? <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm">Free Ticket</span> : null}
                  {jobDetail.accommodation ? <span className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm">Accommodation</span> : null}
                  {jobDetail.food_lunch ? <span className="px-3 py-1 bg-yellow-100 text-yellow-700 rounded-full text-sm">Lunch</span> : null}
                  {jobDetail.medical_insurance ? <span className="px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm">Medical</span> : null}
                </div>
              </div>

              <div>
                <h3 className="text-sm font-semibold text-slate-500 uppercase mb-2">HR Contact</h3>
                <div className="bg-slate-50 rounded-lg p-3 space-y-1 text-sm">
                  <div><span className="text-slate-500">Name:</span> {jobDetail.hr_name || 'N/A'}</div>
                  <div className="flex items-center gap-2"><Mail className="w-4 h-4" /> {jobDetail.hr_email || 'N/A'}</div>
                  <div className="flex items-center gap-2"><Phone className="w-4 h-4" /> {jobDetail.hr_phone || 'N/A'}</div>
                </div>
              </div>

              {jobDetail.company_health && (
                <div>
                  <h3 className="text-sm font-semibold text-slate-500 uppercase mb-2">Company Health</h3>
                  <div className="grid grid-cols-2 gap-3 text-sm">
                    <div>Revenue: <span className="font-semibold">{jobDetail.company_health.revenue_usd}</span></div>
                    <div>Status: <span className="font-semibold">{jobDetail.company_health.profit_status}</span></div>
                    <div>Rating: <span className="font-semibold">{jobDetail.company_health.credit_rating}</span></div>
                    <div>Stock: <span className="font-semibold">{jobDetail.company_health.stock_symbol}</span></div>
                  </div>
                </div>
              )}

              {jobDetail.visa_stats && (
                <div>
                  <h3 className="text-sm font-semibold text-slate-500 uppercase mb-2">Visa Stats</h3>
                  <div className="grid grid-cols-3 gap-3 text-sm">
                    <div>Type: <span className="font-semibold">{jobDetail.visa_stats.visa_type}</span></div>
                    <div>Approval: <span className="font-semibold text-green-600">{jobDetail.visa_stats.approval_rate}%</span></div>
                    <div>Avg: <span className="font-semibold">{jobDetail.visa_stats.avg_processing_days}d</span></div>
                  </div>
                </div>
              )}

              {jobDetail.reviews && (
                <div>
                  <h3 className="text-sm font-semibold text-slate-500 uppercase mb-2">Employee Reviews</h3>
                  <div className="flex items-center gap-2 mb-2">
                    {[1,2,3,4,5].map(i => (
                      <Star key={i} className={`w-4 h-4 ${i <= Math.floor(jobDetail.reviews.overall_rating) ? 'text-yellow-400 fill-yellow-400' : 'text-slate-300'}`} />
                    ))}
                    <span className="text-sm font-semibold">{jobDetail.reviews.overall_rating}/5</span>
                    <span className="text-xs text-slate-500">({jobDetail.reviews.total_reviews} reviews)</span>
                  </div>
                  <div className="text-sm"><span className="text-green-600">Pros:</span> {jobDetail.reviews.pros}</div>
                  <div className="text-sm"><span className="text-red-600">Cons:</span> {jobDetail.reviews.cons}</div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}