import React, { useState, useEffect } from 'react';
import { PageHeader, Card, DataTable, Badge, ProgressBar, Alert } from '../../components/ui/Components';
import { reconciliationAPI, dealsAPI } from '../../services/api';

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

export default function BrokerCommissionTracker() {
  const [summary, setSummary] = useState({});
  const [deals, setDeals] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.allSettled([reconciliationAPI.summary(), dealsAPI.myDeals()])
      .then(([s, d]) => {
        if (s.status === 'fulfilled') setSummary(typeof s.value.data === 'object' ? s.value.data : {});
        if (d.status === 'fulfilled') setDeals(safeArr(d.value.data));
        setLoading(false);
      });
  }, []);

  const earned = safeNum(summary.total_earned ?? summary.earned);
  const pending = safeNum(summary.total_pending ?? summary.pending);
  const total = earned + pending;

  return (
    <div className="p-6">
      <PageHeader icon="💰" title="Commission Tracker" subtitle="Track earnings across all agents"
        image="https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=1600&q=80"
      />

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <Card title="Total Earned" value={`$${earned.toLocaleString()}`} icon="💰" color="green" />
        <Card title="Pending" value={`$${pending.toLocaleString()}`} icon="⏳" color="orange" />
        <Card title="Total Deals" value={deals.length} icon="🤝" color="blue" />
        <Card title="Closed" value={deals.filter((d) => (d.status || '').toLowerCase() === 'closed').length} icon="✅" color="purple" />
      </div>

      <div className="bg-white rounded-xl shadow p-5 mb-6">
        <h3 className="font-bold mb-4">📊 Overall Progress</h3>
        <ProgressBar label="Received" value={earned} max={total || 1} color="green" />
        <div className="mt-3">
          <ProgressBar label="Pending" value={pending} max={total || 1} color="yellow" />
        </div>
      </div>

      <DataTable
        loading={loading}
        empty="Koi deal data nahi"
        columns={[
          { key: 'id', label: 'Deal ID', render: (r) => <span className="font-mono text-xs">{safeStr(r.id || r.deal_id)}</span> },
          { key: 'agent', label: 'Agent', render: (r) => safeStr(r.agent_name || r.agent_id) },
          { key: 'candidate', label: 'Candidate', render: (r) => safeStr(r.candidate_name || r.candidate_id) },
          { key: 'amount', label: 'Amount', render: (r) => <span className="font-bold">${safeNum(r.amount ?? r.commission).toLocaleString()}</span> },
          {
            key: 'status', label: 'Status',
            render: (r) => <Badge color={r.status === 'closed' ? 'green' : r.status === 'pending' ? 'yellow' : 'blue'}>{safeStr(r.status)}</Badge>,
          },
          { key: 'created_at', label: 'Date', render: (r) => r.created_at ? new Date(r.created_at).toLocaleDateString() : '—' },
        ]}
        data={deals}
      />
    </div>
  );
}