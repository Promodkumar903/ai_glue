import React, { useState, useEffect } from 'react';
import { PageHeader, Card, DataTable, Badge, Tabs, Alert, ProgressBar } from '../../components/ui/Components';
import { applicationsAPI } from '../../services/api';

const safeArr = (v) => {
  if (Array.isArray(v)) return v;
  if (v && typeof v === 'object') {
    if (Array.isArray(v.items)) return v.items;
    if (Array.isArray(v.data)) return v.data;
  }
  return [];
};
const safeNum = (v) => { const n = Number(v); return isFinite(n) ? n : 0; };
const safeStr = (v, fb = '—') => (v == null || v === '') ? fb : String(v);

const STATUS_COLORS = { applied: 'blue', submitted: 'blue', shortlisted: 'purple', interviewed: 'yellow', selected: 'green', accepted: 'green', rejected: 'red', pending: 'orange' };

export default function StudentMyApplications() {
  const [apps, setApps] = useState([]);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState('all');
  const [error, setError] = useState('');

  useEffect(() => {
    setLoading(true);
    applicationsAPI.status('me')
      .then((r) => setApps(safeArr(r.data)))
      .catch(() => setError('Failed to load — check backend'))
      .finally(() => setLoading(false));
  }, []);

  const filtered = tab === 'all' ? apps : apps.filter((a) => {
    const st = (a.status || '').toLowerCase();
    return tab === 'active' ? !['rejected', 'selected', 'accepted'].includes(st) : st === tab;
  });

  const counts = {
    all: apps.length,
    applied: apps.filter((a) => ['applied', 'submitted'].includes((a.status || '').toLowerCase())).length,
    shortlisted: apps.filter((a) => (a.status || '').toLowerCase() === 'shortlisted').length,
    interviewed: apps.filter((a) => (a.status || '').toLowerCase() === 'interviewed').length,
    accepted: apps.filter((a) => ['selected', 'accepted'].includes((a.status || '').toLowerCase())).length,
    rejected: apps.filter((a) => (a.status || '').toLowerCase() === 'rejected').length,
  };

  const funnel = [
    { label: 'Applied', value: counts.applied, color: 'blue' },
    { label: 'Shortlisted', value: counts.shortlisted, color: 'purple' },
    { label: 'Interviewed', value: counts.interviewed, color: 'yellow' },
    { label: 'Accepted', value: counts.accepted, color: 'green' },
  ];
  const maxF = Math.max(...funnel.map((f) => f.value), 1);

  return (
    <div className="p-6">
      <PageHeader
        icon="📚"
        title="My College Applications"
        subtitle="Track your applications to universities & programs"
        image="https://images.unsplash.com/photo-1450101499163-c8848c66ca85?w=1600&q=80"
      />

      {error && <Alert type="danger" onClose={() => setError('')}>{error}</Alert>}

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <Card title="Total Applied" value={counts.all} icon="📨" color="blue" />
        <Card title="Shortlisted" value={counts.shortlisted} icon="⭐" color="purple" />
        <Card title="Accepted" value={counts.accepted} icon="✅" color="green" />
        <Card title="Rejected" value={counts.rejected} icon="❌" color="red" />
      </div>

      <div className="bg-white rounded-xl shadow p-5 mb-6">
        <h3 className="font-bold mb-4">📊 Admission Funnel</h3>
        <div className="space-y-3">
          {funnel.map((s) => <ProgressBar key={s.label} label={s.label} value={s.value} max={maxF} color={s.color} />)}
        </div>
      </div>

      <Tabs
        active={tab}
        onChange={setTab}
        tabs={[
          { id: 'all', label: 'All', icon: '📋', count: counts.all },
          { id: 'applied', label: 'Applied', icon: '📤', count: counts.applied },
          { id: 'shortlisted', label: 'Shortlisted', icon: '⭐', count: counts.shortlisted },
          { id: 'interviewed', label: 'Interviewed', icon: '🎤', count: counts.interviewed },
          { id: 'accepted', label: 'Accepted', icon: '✅', count: counts.accepted },
          { id: 'rejected', label: 'Rejected', icon: '❌', count: counts.rejected },
        ]}
      />

      <DataTable
        loading={loading}
        empty="Koi application nahi — Apply to College se shuru karo"
        columns={[
          { key: 'id', label: 'ID', render: (r) => <span className="font-mono text-xs">{safeStr(r.id || r.application_id)}</span> },
          { key: 'program', label: 'Program', render: (r) => safeStr(r.opportunity_title || r.program_name || r.title) },
          { key: 'university', label: 'University', render: (r) => safeStr(r.university_name || r.organization_name) },
          {
            key: 'status', label: 'Status',
            render: (r) => {
              const st = (r.status || '').toLowerCase();
              return <Badge color={STATUS_COLORS[st] || 'gray'}>{safeStr(r.status, 'N/A')}</Badge>;
            },
          },
          { key: 'match_score', label: 'Match', render: (r) => r.match_score ? <span className="font-bold text-emerald-600">{safeNum(r.match_score)}%</span> : '—' },
          { key: 'submitted_at', label: 'Applied On', render: (r) => (r.submitted_at || r.created_at) ? new Date(r.submitted_at || r.created_at).toLocaleDateString() : '—' },
        ]}
        data={filtered}
      />
    </div>
  );
}