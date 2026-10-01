import React, { useState, useEffect, useMemo } from 'react';
import { PageHeader, Card, Badge, Alert } from '../../components/ui/Components';
import { publicAPI } from '../../services/api';

const safeArr = (v) => {
  if (Array.isArray(v)) return v;
  if (v && typeof v === 'object') {
    if (Array.isArray(v.items)) return v.items;
    if (Array.isArray(v.data)) return v.data;
  }
  return [];
};
const safeStr = (v, fb = '—') => (v == null || v === '') ? fb : String(v);

export default function WorkAbroad() {
  const [tab, setTab] = useState('jobs');
  const [jobs, setJobs] = useState([]);
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchQ, setSearchQ] = useState('');
  const [filterCountry, setFilterCountry] = useState('');

  

  const countries = useMemo(() => {
    const set = new Set();
    jobs.forEach((j) => { if (j.country) set.add(j.country); });
    return Array.from(set);
  }, [jobs]);

  const filteredJobs = useMemo(() => {
    return jobs.filter((j) => {
      if (filterCountry && j.country !== filterCountry) return false;
      if (searchQ) {
        const q = searchQ.toLowerCase();
        return (
          String(j.title || '').toLowerCase().includes(q) ||
          String(j.description || '').toLowerCase().includes(q) ||
          String(j.organization_id || '').toLowerCase().includes(q)
        );
      }
      return true;
    });
  }, [jobs, filterCountry, searchQ]);

  const applyJob = (job) => {
    alert(`Application flow coming soon\nJob: ${job.title}`);
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <PageHeader
        icon="💼"
        title="Work Abroad"
        subtitle="Find jobs, verified agents & brokers — Apply directly"
        image="https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d?w=1600&q=80"
      />

      {error && <Alert type="danger" title="Error" onClose={() => setError('')}>{error}</Alert>}

      {/* Search bar */}
      <div className="mb-4 flex gap-2">
        <input
          type="text"
          placeholder="Search jobs by title, skill, company..."
          value={searchQ}
          onChange={(e) => setSearchQ(e.target.value)}
          className="flex-1 px-4 py-3 border border-slate-200 rounded-xl focus:outline-none focus:border-blue-500"
        />
        {filterCountry && (
          <button
            onClick={() => setFilterCountry('')}
            className="px-4 py-3 bg-slate-100 hover:bg-slate-200 rounded-xl text-sm font-medium"
          >
            Clear: {filterCountry}
          </button>
        )}
      </div>

      {/* Tabs */}
      <div className="mb-4 flex gap-2 border-b border-slate-200">
        <button
          onClick={() => setTab('jobs')}
          className={`px-4 py-2 font-medium text-sm border-b-2 transition-all ${
            tab === 'jobs'
              ? 'border-blue-600 text-blue-600'
              : 'border-transparent text-slate-500 hover:text-slate-700'
          }`}
        >
          💼 Jobs ({filteredJobs.length})
        </button>
        <button
          onClick={() => setTab('agents')}
          className={`px-4 py-2 font-medium text-sm border-b-2 transition-all ${
            tab === 'agents'
              ? 'border-blue-600 text-blue-600'
              : 'border-transparent text-slate-500 hover:text-slate-700'
          }`}
        >
          🤝 Agents & Brokers ({agents.length})
        </button>
        <button
          onClick={() => setTab('applied')}
          className={`px-4 py-2 font-medium text-sm border-b-2 transition-all ${
            tab === 'applied'
              ? 'border-blue-600 text-blue-600'
              : 'border-transparent text-slate-500 hover:text-slate-700'
          }`}
        >
          📄 My Applications
        </button>
      </div>

      {/* Jobs Tab */}
      {tab === 'jobs' && (
        <>
          {countries.length > 0 && (
            <div className="mb-4 flex flex-wrap gap-2">
              <button
                onClick={() => setFilterCountry('')}
                className={`px-3 py-1.5 rounded-lg text-sm ${
                  !filterCountry ? 'bg-blue-600 text-white' : 'bg-white border border-slate-200'
                }`}
              >
                All
              </button>
              {countries.map((c) => (
                <button
                  key={c}
                  onClick={() => setFilterCountry(c)}
                  className={`px-3 py-1.5 rounded-lg text-sm ${
                    filterCountry === c ? 'bg-blue-600 text-white' : 'bg-white border border-slate-200'
                  }`}
                >
                  {c}
                </button>
              ))}
            </div>
          )}

          {loading ? (
            <div className="text-center py-10 text-slate-400">Loading jobs…</div>
          ) : filteredJobs.length === 0 ? (
            <div className="text-center py-10 text-slate-400 bg-white rounded-xl border border-slate-200">
              No jobs found
            </div>
          ) : (
            <div className="space-y-3">
              {filteredJobs.map((j) => (
                <div key={j.id} className="bg-white p-5 rounded-xl border border-slate-200 hover:shadow-lg transition-all">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <h4 className="font-bold text-slate-800 mb-1">{safeStr(j.title)}</h4>
                      <p className="text-sm text-slate-500 mb-2">
                        {safeStr(j.country, 'Location N/A')} · {safeStr(j.type, 'Full time')}
                      </p>
                      {j.description && (
                        <p className="text-sm text-slate-600 line-clamp-2">{j.description}</p>
                      )}
                      <div className="flex gap-2 mt-3">
                        {j.visa_sponsorship && <Badge color="green">Visa Sponsorship</Badge>}
                        {j.remote && <Badge color="blue">Remote</Badge>}
                        {j.salary && <Badge color="purple">${j.salary}</Badge>}
                      </div>
                    </div>
                    <button
                      onClick={() => applyJob(j)}
                      className="px-5 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium whitespace-nowrap"
                    >
                      Apply →
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {/* Agents Tab */}
      {tab === 'agents' && (
        <>
          {loading ? (
            <div className="text-center py-10 text-slate-400">Loading agents…</div>
          ) : agents.length === 0 ? (
            <div className="text-center py-10 text-slate-400 bg-white rounded-xl border border-slate-200">
              No agents registered
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {agents.map((a) => (
                <div key={a.id || a.agent_id} className="bg-white p-5 rounded-xl border border-slate-200">
                  <div className="flex items-center gap-3 mb-3">
                    <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center text-white font-bold">
                      {safeStr(a.agent_name || a.full_name || a.name).charAt(0).toUpperCase()}
                    </div>
                    <div>
                      <p className="font-bold text-slate-800">
                        {safeStr(a.agent_name || a.full_name || a.name)}
                      </p>
                      <p className="text-xs text-slate-500">Verified Agent</p>
                    </div>
                  </div>
                  <div className="space-y-1 text-sm text-slate-600 mb-3">
                    <p>📊 Applications: {a.total_apps || a.candidates || 0}</p>
                    <p>✅ Joined: {a.joined || a.hired || 0}</p>
                  </div>
                  <button className="w-full py-2 bg-slate-100 hover:bg-slate-200 rounded-lg text-sm font-medium">
                    View Profile
                  </button>
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {/* Applied Tab */}
      {tab === 'applied' && (
        <div className="text-center py-10 text-slate-400 bg-white rounded-xl border border-slate-200">
          <p className="text-4xl mb-3">📄</p>
          <p className="font-medium">No applications yet</p>
          <p className="text-sm mt-1">Apply to jobs to track them here</p>
        </div>
      )}
    </div>
  );
}