import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { PageHeader, Card, Badge, Alert } from '../../components/ui/Components';
import { crmAPI } from '../../services/api';

const STATUS_TABS = [
  { id: 'all', label: 'All', icon: '📋' },
  { id: 'DRAFT', label: 'Draft', icon: '📝' },
  { id: 'SUBMITTED', label: 'Submitted', icon: '📤' },
  { id: 'UNDER_REVIEW', label: 'Under Review', icon: '🔍' },
  { id: 'OFFER', label: 'Offer', icon: '🎉' },
  { id: 'VISA', label: 'Visa', icon: '🛂' },
  { id: 'ENROLLED', label: 'Enrolled', icon: '🎓' },
  { id: 'REJECTED', label: 'Rejected', icon: '❌' },
];

const STATUS_COLORS = {
  DRAFT: 'gray',
  SUBMITTED: 'blue',
  UNDER_REVIEW: 'purple',
  ADDITIONAL_DOCUMENTS: 'orange',
  OFFER: 'green',
  VISA: 'green',
  ENROLLED: 'green',
  REJECTED: 'red',
  WITHDRAWN: 'gray',
};

export default function Applications() {
  const [apps, setApps] = useState([]);
  const [counts, setCounts] = useState({});
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState('all');
  const [error, setError] = useState('');

  const load = (filterStatus = tab) => {
    setLoading(true);
    const params = filterStatus === 'all' ? {} : { status: filterStatus };
    crmAPI.listApplications(params)
      .then((r) => {
        setApps(r.data.applications || []);
        setCounts(r.data.counts_by_status || {});
      })
      .catch((e) => setError(e.response?.data?.detail || 'Failed to load applications'))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(tab); }, [tab]);

  const total = Object.values(counts).reduce((a, b) => a + b, 0);

  return (
    <div className="p-6">
      <PageHeader icon="📝" title="Applications" subtitle="All applications across your candidates" />

      {error && <div className="mb-3"><Alert type="danger" onClose={() => setError('')}>{error}</Alert></div>}

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <Card title="Total" value={total} icon="📋" color="blue" />
        <Card title="Submitted" value={counts.SUBMITTED || 0} icon="📤" color="purple" />
        <Card title="Offers" value={counts.OFFER || 0} icon="🎉" color="green" />
        <Card title="Enrolled" value={counts.ENROLLED || 0} icon="🎓" color="green" />
      </div>

      {/* Status Tabs */}
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
      ) : apps.length === 0 ? (
        <div className="text-center py-16">
          <p className="text-5xl mb-4">📝</p>
          <p className="text-gray-500">Koi application nahi mili</p>
          <p className="text-xs text-gray-400 mt-2">Pehle lead se application banao</p>
        </div>
      ) : (
        <div className="bg-white rounded-lg border overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="text-left px-4 py-3 text-xs font-semibold text-gray-600">Candidate</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-gray-600">Opportunity</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-gray-600">Type</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-gray-600">Status</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-gray-600">Match</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-gray-600">Submitted</th>
              </tr>
            </thead>
            <tbody>
              {apps.map((a) => (
                <tr key={a.id} className="border-t hover:bg-gray-50">
                  <td className="px-4 py-3">
                    <Link to={`/agent/leads/${a.candidate_id}`} className="text-sm font-medium text-blue-600 hover:underline">
                      {a.candidate_name || 'Unknown'}
                    </Link>
                    <p className="text-xs text-gray-400">{a.candidate_email || ''}</p>
                  </td>
                  <td className="px-4 py-3 text-sm">{a.opportunity_title || '—'}</td>
                  <td className="px-4 py-3 text-xs text-gray-600">{a.opportunity_type || '—'}</td>
                  <td className="px-4 py-3">
                    <Badge color={STATUS_COLORS[a.status] || 'gray'}>
                      {a.status || 'DRAFT'}
                    </Badge>
                  </td>
                  <td className="px-4 py-3 text-sm font-semibold text-emerald-600">
                    {a.match_score ? `${a.match_score}%` : '—'}
                  </td>
                  <td className="px-4 py-3 text-xs text-gray-500">
                    {a.submitted_at ? new Date(a.submitted_at).toLocaleDateString() : '—'}
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