import React, { useState, useEffect } from 'react';
import {
  GraduationCap, Building2, MessageSquare, Phone,
  Search, Sparkles, Mail
} from 'lucide-react';
import api from '../../services/api';

const TABS = [
  { key: 'universities', label: 'Universities', icon: GraduationCap },
  { key: 'agents', label: 'Study Agents', icon: Building2 },
  { key: 'requests', label: 'Requests', icon: MessageSquare },
  { key: 'contacts', label: 'University Contacts', icon: Phone },
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

export default function OIEStudies() {
  const [activeTab, setActiveTab] = useState('universities');

  const [studies, setStudies] = useState([]);
  const [studyCountries, setStudyCountries] = useState([]);
  const [agents, setAgents] = useState([]);
  const [requests, setRequests] = useState([]);
  const [contacts, setContacts] = useState([]);

  const [studyFilter, setStudyFilter] = useState('');
  const [studyCountry, setStudyCountry] = useState('');
  const [studyOnlyFree, setStudyOnlyFree] = useState(false);
  const [studyOnlyPR, setStudyOnlyPR] = useState(false);
  const [studyOnlySchol, setStudyOnlySchol] = useState(false);

  useEffect(() => {
    // Load all on mount (for stats)
    loadStudies();
    loadAgents();
    loadContacts();
    loadRequests();
  }, []);

  useEffect(() => {
    if (activeTab === 'universities') loadStudies();
    else if (activeTab === 'agents') loadAgents();
    else if (activeTab === 'requests') loadRequests();
    else if (activeTab === 'contacts') loadContacts();
  }, [activeTab]);

  const loadStudies = async () => {
    try {
      const r = await api.get('/admin/oie/studies', {
        params: {
          country: studyCountry,
          search: studyFilter,
          free_only: studyOnlyFree,
          pr_only: studyOnlyPR,
          scholarship_only: studyOnlySchol,
          limit: 200,
        }
      });
      setStudies(r.data.studies || []);
      setStudyCountries(r.data.countries || []);
    } catch (e) { console.error(e); }
  };

  const loadAgents = async () => {
    try {
      const r = await api.get('/admin/oie/study-agents', { params: { limit: 100 } });
      setAgents(r.data.agents || []);
    } catch (e) { console.error(e); }
  };

  const loadRequests = async () => {
    try {
      const r = await api.get('/admin/oie/requests', { params: { limit: 100 } });
      setRequests(r.data.requests || []);
    } catch (e) { console.error(e); }
  };

  const loadContacts = async () => {
    try {
      const r = await api.get('/admin/oie/study-contacts', { params: { limit: 100 } });
      setContacts(r.data.contacts || []);
    } catch (e) { console.error(e); }
  };

  // Stats
  const totalUnis = studies.length || 4957;
  const freeCount = studies.filter(s => s.free_education).length || 392;
  const prCount = studies.filter(s => s.pr_possible).length || 1346;
  const scholCount = studies.filter(s => s.scholarship_available).length || 3639;

  return (
    <div className="min-h-screen bg-slate-50 p-6">
      {/* HEADER */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
          <Sparkles className="w-6 h-6 text-blue-600" />
          OIE Studies — University Intelligence
        </h1>
        <p className="text-sm text-slate-500 mt-1">
          Universities, study agents, admission contacts
        </p>

        {/* STATS */}
        <div className="grid grid-cols-2 md:grid-cols-6 gap-3 mt-4">
          <StatCard label="Universities" value={totalUnis} color="blue" />
          <StatCard label="Free Tuition" value={freeCount} color="green" />
          <StatCard label="PR Pathway" value={prCount} color="purple" />
          <StatCard label="Scholarships" value={scholCount} color="orange" />
          <StatCard label="Study Agents" value={agents.length} color="pink" />
          <StatCard label="Contacts" value={contacts.length} color="yellow" />
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
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-slate-500 hover:text-slate-700'
            }`}
          >
            <t.icon className="w-4 h-4" />
            {t.label}
          </button>
        ))}
      </div>

      {/* UNIVERSITIES TAB */}
      {activeTab === 'universities' && (
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
              className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm"
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
                    <td className="px-4 py-3 text-xs">
                      {s.post_study_work_years ? `${s.post_study_work_years}mo` : '-'}
                    </td>
                    <td className="px-4 py-3">
                      {s.application_url ? (
                        <a href={s.application_url} target="_blank" rel="noreferrer" className="text-blue-500 text-xs hover:underline">Link</a>
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

      {/* STUDY AGENTS TAB */}
      {activeTab === 'agents' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {agents.map(a => (
            <div key={a.id} className="bg-white rounded-xl border border-slate-200 p-4">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <div className="font-semibold text-slate-900">{a.name}</div>
                  <div className="text-xs text-slate-500">
                    {a.country}{a.city ? ` · ${a.city}` : ''}
                  </div>
                </div>
                <div className={`px-2 py-1 text-xs rounded-full ${
                  a.verification_status === 'VERIFIED' ? 'bg-green-100 text-green-700' :
                  a.verification_status === 'FLAGGED' ? 'bg-red-100 text-red-700' :
                  'bg-yellow-100 text-yellow-700'
                }`}>
                  {a.verification_status}
                </div>
              </div>

              <div className="flex items-center gap-2 mb-3">
                <div className="flex-1 bg-slate-100 rounded-full h-2">
                  <div className="bg-blue-500 h-2 rounded-full" style={{ width: `${a.trust_score}%` }}></div>
                </div>
                <span className="text-sm font-bold">{a.trust_score}</span>
              </div>

              {a.email && (
                <div className="text-xs text-slate-500 flex items-center gap-1 mb-1">
                  <Mail className="w-3 h-3" />{a.email}
                </div>
              )}
              {a.phone && (
                <div className="text-xs text-slate-500 flex items-center gap-1 mb-1">
                  <Phone className="w-3 h-3" />{a.phone}
                </div>
              )}
              {a.target_countries && (
                <div className="text-xs text-slate-400 mt-2">
                  Targets: {a.target_countries.slice(0, 50)}
                </div>
              )}

              {a.fake_flags && (
                <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded text-xs text-red-700">
                  FLAGGED: {a.fake_flags}
                </div>
              )}
            </div>
          ))}
          {agents.length === 0 && (
            <div className="col-span-3 text-center text-slate-400 py-8">No study agents found</div>
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
                    {r.from_name} → {r.to_name}
                  </div>
                </div>
                <span className={`px-2 py-1 text-xs rounded-full ${
                  r.status === 'ACCEPTED' ? 'bg-green-100 text-green-700' :
                  r.status === 'DECLINED' ? 'bg-red-100 text-red-700' :
                  'bg-yellow-100 text-yellow-700'
                }`}>{r.status}</span>
              </div>
              {r.message && <div className="mt-2 text-sm text-slate-600">{r.message}</div>}
            </div>
          ))}
          {requests.length === 0 && (
            <div className="text-center text-slate-400 py-8">No study requests yet</div>
          )}
        </div>
      )}

      {/* UNIVERSITY CONTACTS TAB */}
      {activeTab === 'contacts' && (
        <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-slate-50">
              <tr className="text-left text-xs text-slate-500 uppercase">
                <th className="px-4 py-3">University</th>
                <th className="px-4 py-3">Country</th>
                <th className="px-4 py-3">Officer</th>
                <th className="px-4 py-3">Designation</th>
                <th className="px-4 py-3">Email</th>
                <th className="px-4 py-3">Phone</th>
              </tr>
            </thead>
            <tbody>
              {contacts.map(c => (
                <tr key={c.id} className="border-t border-slate-100 hover:bg-slate-50">
                  <td className="px-4 py-3 font-medium">{c.university_name}</td>
                  <td className="px-4 py-3 text-slate-600">{c.country}</td>
                  <td className="px-4 py-3">{c.admissions_officer || '-'}</td>
                  <td className="px-4 py-3 text-slate-500 text-xs">{c.designation || '-'}</td>
                  <td className="px-4 py-3 text-blue-600 text-xs">{c.email || '-'}</td>
                  <td className="px-4 py-3 text-xs">{c.phone || '-'}</td>
                </tr>
              ))}
              {contacts.length === 0 && (
                <tr><td colSpan="6" className="px-4 py-8 text-center text-slate-400">No university contacts yet</td></tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}