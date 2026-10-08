import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { PageHeader, Card, Badge, Alert } from '../../components/ui/Components';
import { crmAPI } from '../../services/api';

const STATUS_TABS = [
  { id: 'all', label: 'All', icon: '📋' },
  { id: 'NOT_STARTED', label: 'Not Started', icon: '⚪' },
  { id: 'DOCS_PENDING', label: 'Docs Pending', icon: '📄' },
  { id: 'APPLIED', label: 'Applied', icon: '📤' },
  { id: 'UNDER_REVIEW', label: 'Under Review', icon: '🔍' },
  { id: 'APPROVED', label: 'Approved', icon: '✅' },
  { id: 'REJECTED', label: 'Rejected', icon: '❌' },
];

const STATUS_COLORS = {
  NOT_STARTED: 'gray',
  DOCS_PENDING: 'orange',
  APPLIED: 'blue',
  UNDER_REVIEW: 'purple',
  APPROVED: 'green',
  REJECTED: 'red',
  EXPIRED: 'red',
};

export default function Visa() {
  const [data, setData] = useState({ cases: [], counts_by_status: {}, upcoming_appointments: [] });
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState('all');
  const [error, setError] = useState('');

  const load = (filterStatus = tab) => {
    setLoading(true);
    const params = filterStatus === 'all' ? {} : { status: filterStatus };
    crmAPI.getVisaCases(params)
      .then((r) => setData(r.data || {}))
      .catch((e) => setError(e.response?.data?.detail || 'Failed to load visa cases'))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(tab); }, [tab]);

  const cases = data.cases || [];
  const counts = data.counts_by_status || {};
  const appts = data.upcoming_appointments || [];
  const total = Object.values(counts).reduce((a, b) => a + b, 0);

  return (
    <div className="p-6">
     <PageHeader
       icon="🛂"
       title={
         data.role === 'STUDENT' ? 'My Student Visa' :
         data.role === 'JOB_SEEKER' ? 'My Work Visa' :
         data.role === 'AGENT' ? 'Visa Tracking' :
         data.role === 'ADMIN' ? 'Platform Visa Cases' :
         'Visa Tracking'
      }
      subtitle={
        data.role === 'AGENT' ? 'All candidates visa' :
        data.role === 'ADMIN' ? 'All visa cases on platform' :
        'Track your visa application'
      }
    />

      {error && <div className="mb-3"><Alert type="danger" onClose={() => setError('')}>{error}</Alert></div>}

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
        <Card title="Total" value={total} icon="🛂" color="blue" />
        <Card title="Docs Pending" value={counts.DOCS_PENDING || 0} icon="📄" color="orange" />
        <Card title="Applied" value={counts.APPLIED || 0} icon="📤" color="purple" />
        <Card title="Approved" value={counts.APPROVED || 0} icon="✅" color="green" />
        <Card title="Rejected" value={counts.REJECTED || 0} icon="❌" color="red" />
      </div>

      {/* Upcoming Appointments */}
      {appts.length > 0 && (
        <div className="mb-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="font-semibold text-blue-900 mb-2">📅 Upcoming Appointments ({appts.length})</h3>
          <div className="space-y-2">
            {appts.slice(0, 5).map((a) => (
              <div key={a.id} className="flex justify-between items-center bg-white rounded px-3 py-2 text-sm">
                <span><strong>{a.candidate_name}</strong> — {a.country}</span>
                <span className="text-blue-700">
                  {new Date(a.scheduled_at).toLocaleString()}
                  {a.location && ` • ${a.location}`}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-2 mb-6 border-b overflow-x-auto">
        {STATUS_TABS.map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`px-4 py-2 text-sm font-medium border-b-2 whitespace-nowrap transition ${
              tab === t.id
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            {t.icon} {t.label}
            {t.id !== 'all' && counts[t.id] > 0 && (
              <span className="ml-1 text-xs bg-gray-200 rounded px-1.5">{counts[t.id]}</span>
            )}
          </button>
        ))}
      </div>

      {/* Table */}
      {loading ? (
        <p className="text-center py-10 text-gray-500">Loading...</p>
      ) : cases.length === 0 ? (
        <div className="text-center py-16">
          <p className="text-5xl mb-4">🛂</p>
          <p className="text-gray-500">Koi visa case nahi mila</p>
          <p className="text-xs text-gray-400 mt-2">Candidate ke saath visa case create karo</p>
        </div>
      ) : (
        <div className="bg-white rounded-lg border overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="text-left px-4 py-3 text-xs font-semibold text-gray-600">Candidate</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-gray-600">Country</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-gray-600">Visa Type</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-gray-600">Status</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-gray-600">Applied</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-gray-600">Decision</th>
              </tr>
            </thead>
            <tbody>
              {cases.map((c) => (
                <tr key={c.id} className="border-t hover:bg-gray-50">
                  <td className="px-4 py-3">
                    <Link to={`/agent/visa/${c.id}`} className="text-sm font-medium text-blue-600 hover:underline">
                      {c.candidate_name || 'Unknown'}
                    </Link>
                    <p className="text-xs text-gray-400">{c.candidate_email || ''}</p>
                  </td>
                  <td className="px-4 py-3 text-sm">{c.country}</td>
                  <td className="px-4 py-3 text-xs text-gray-600">{c.visa_type}</td>
                  <td className="px-4 py-3">
                    <Badge color={STATUS_COLORS[c.status] || 'gray'}>
                      {c.status || 'NOT_STARTED'}
                    </Badge>
                  </td>
                  <td className="px-4 py-3 text-xs text-gray-500">
                    {c.applied_at ? new Date(c.applied_at).toLocaleDateString() : '—'}
                  </td>
                  <td className="px-4 py-3 text-xs text-gray-500">
                    {c.decision_at ? new Date(c.decision_at).toLocaleDateString() : '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}