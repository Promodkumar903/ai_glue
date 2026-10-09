import React, { useState, useEffect } from 'react';
import {
  GraduationCap, Building2, MessageSquare, Phone,
  Search, Sparkles, Mail, MapPin
} from 'lucide-react';
import api from '../../services/api';

const TABS = [
  { key: 'universities', label: 'Universities', icon: GraduationCap },
  { key: 'registry', label: 'Study Agents', icon: Building2 },
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
  const [stats, setStats] = useState({});
  const [studies, setStudies] = useState([]);
  const [studyCountries, setStudyCountries] = useState([]);
  const [registry, setRegistry] = useState([]);
  const [requests, setRequests] = useState([]);
  const [contacts, setContacts] = useState([]);

  const [studyFilter, setStudyFilter] = useState('');
  const [studyCountry, setStudyCountry] = useState('');
  const [studyOnlyFree, setStudyOnlyFree] = useState(false);
  const [studyOnlyPR, setStudyOnlyPR] = useState(false);
  const [studyOnlySchol, setStudyOnlySchol] = useState(false);

  useEffect(() => { loadStats(); }, []);
  useEffect(() => {
    if (activeTab === 'universities') loadStudies();
    else if (activeTab === 'registry') loadRegistry();
    else if (activeTab === 'requests') loadRequests();
    else if (activeTab === 'contacts') loadContacts();
  }, [activeTab]);

  const loadStats = async () => {
    try { const r = await api.get('/admin/oie/stats/studies'); setStats(r.data || {}); } catch (e) {}
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
      setStudies(r.data.studies || []);
      setStudyCountries(r.data.countries || []);
    } catch (e) {}
  };
  const loadRegistry = async () => {
    try { const r = await api.get('/admin/oie/study-registry', { params: { limit: 100 } }); setRegistry(r.data.entities || []); } catch (e) {}
  };
  const loadRequests = async () => {
    try { const r = await api.get('/admin/oie/study-requests', { params: { limit: 100 } }); setRequests(r.data.requests || []); } catch (e) {}
  };
  const loadContacts = async () => {
    try { const r = await api.get('/admin/oie/study-contacts', { params: { limit: 100 } }); setContacts(r.data.log || []); } catch (e) {}
  };

  return (
    <div className="min-h-screen bg-slate-50 p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
          <Sparkles className="w-6 h-6 text-blue-600" />
          OIE Studies — University Intelligence
        </h1>
        <p className="text-sm text-slate-500 mt-1">Universities, study agents, admission contacts</p>

        <div className="grid grid-cols-2 md:grid-cols-6 gap-3 mt-4">
          <StatCard label="Universities" value={stats.total_universities} color="blue" />
          <StatCard label="Free Tuition" value={stats.free_tuition} color="green" />
          <StatCard label="PR Pathway" value={stats.pr_pathway} color="purple" />
          <StatCard label="Scholarships" value={stats.scholarships} color="orange" />
          <StatCard label="Study Agents" value={stats.study_agents} color="pink" />
          <StatCard label="Contacts" value={stats.contact_attempts} color="yellow" />
        </div>
      </div>

      <div className="flex gap-1 border-b border-slate-200 mb-4 overflow-x-auto">
        {TABS.map(t => (
          <button key={t.key} onClick={() => setActiveTab(t.key)}
            className={`flex items-center gap-2 px-4 py-2 text-sm font-medium border-b-2 transition ${
              activeTab === t.key ? 'border-blue-600 text-blue-600' : 'border-transparent text-slate-500'
            }`}>
            <t.icon className="w-4 h-4" />{t.label}
          </button>
        ))}
      </div>

      {activeTab === 'universities' && (
        <>
          <div className="flex flex-wrap gap-2 mb-4">
            <div className="flex-1 min-w-[200px] relative">
              <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
              <input type="text" placeholder="Search university..." value={studyFilter}
                onChange={e => setStudyFilter(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && loadStudies()}
                className="w-full pl-9 pr-4 py-2 border border-slate-300 rounded-lg text-sm" />
            </div>
            <select value={studyCountry} onChange={e => setStudyCountry(e.target.value)}
              className="px-3 py-2 border border-slate-300 rounded-lg text-sm">
              <option value="">All Countries</option>
              {studyCountries.map(c => <option key={c.country} value={c.country}>{c.country} ({c.cnt})</option>)}
            </select>
            <button onClick={() => setStudyOnlyFree(!studyOnlyFree)}
              className={`px-3 py-2 rounded-lg text-sm border ${studyOnlyFree ? 'bg-green-500 text-white border-green-500' : 'bg-white border-slate-300'}`}>
              Free Tuition
            </button>
            <button onClick={() => setStudyOnlyPR(!studyOnlyPR)}
              className={`px-3 py-2 rounded-lg text-sm border ${studyOnlyPR ? 'bg-blue-500 text-white border-blue-500' : 'bg-white border-slate-300'}`}>
              PR Pathway
            </button>
            <button onClick={() => setStudyOnlySchol(!studyOnlySchol)}
              className={`px-3 py-2 rounded-lg text-sm border ${studyOnlySchol ? 'bg-purple-500 text-white border-purple-500' : 'bg-white border-slate-300'}`}>
              Scholarship
            </button>
            <button onClick={loadStudies} className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm">Apply</button>
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
                      {s.free_education ? <span className="text-green-600 font-semibold">FREE</span> :
                       s.tuition_fee > 0 ? `$${s.tuition_fee.toLocaleString()}/yr` : <span className="text-slate-400">N/A</span>}
                    </td>
                    <td className="px-4 py-3">{s.hostel_cost_monthly_usd > 0 ? `$${Math.round(s.hostel_cost_monthly_usd)}` : '-'}</td>
                    <td className="px-4 py-3">
                      {s.scholarship_available ? <span className="text-purple-600 font-semibold">${Math.round((s.scholarship_amount_usd || 0) / 1000)}K</span> : '-'}
                    </td>
                    <td className="px-4 py-3">{s.pr_possible ? <span className="text-blue-600">Yes</span> : '-'}</td>
                    <td className="px-4 py-3 text-xs">{s.post_study_work_years ? `${s.post_study_work_years}mo` : '-'}</td>
                    <td className="px-4 py-3">
                      {s.application_url ? <a href={s.application_url} target="_blank" rel="noreferrer" className="text-blue-500 text-xs hover:underline">Link</a> : '-'}
                    </td>
                  </tr>
                ))}
                {studies.length === 0 && <tr><td colSpan="8" className="px-4 py-8 text-center text-slate-400">No universities</td></tr>}
              </tbody>
            </table>
          </div>
          <div className="mt-3 text-xs text-slate-500 text-right">Showing {studies.length} universities</div>
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
                  <div className="bg-blue-500 h-2 rounded-full" style={{ width: `${e.trust_score}%` }}></div>
                </div>
                <span className="text-sm font-bold">{e.trust_score}</span>
              </div>
            </div>
          ))}
          {registry.length === 0 && <div className="col-span-3 text-center text-slate-400 py-8">No study agents yet</div>}
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
          {requests.length === 0 && <div className="text-center text-slate-400 py-8">No study requests</div>}
        </div>
      )}

      {activeTab === 'contacts' && (
        <div className="space-y-2">
          {contacts.map(c => (
            <div key={c.id} className="bg-white rounded-lg border border-slate-200 p-3">
              <div className="font-semibold text-sm">{c.university_name}</div>
              <div className="text-xs text-slate-500">{c.admissions_officer} — {c.email}</div>
            </div>
          ))}
          {contacts.length === 0 && <div className="text-center text-slate-400 py-8">No university contacts yet</div>}
        </div>
      )}
    </div>
  );
}