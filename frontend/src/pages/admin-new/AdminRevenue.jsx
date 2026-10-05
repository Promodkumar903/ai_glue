import React, { useState, useEffect } from 'react';
import { PageHeader, Badge } from '../../components/ui/Components';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function AdminRevenue() {
  const [data, setData] = useState(null);
  const [subs, setSubs] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = () => {
    setLoading(true);
    Promise.all([
      fetch(`${API_BASE}/admin/revenue/dashboard`).then((r) => r.json()),
      fetch(`${API_BASE}/admin/subscriptions`).then((r) => r.json()),
    ])
      .then(([d, s]) => {
        setData(d);
        setSubs(s.subscriptions || []);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  if (loading) return <div className="p-6 text-center text-slate-500">Loading revenue data...</div>;
  if (!data) return <div className="p-6 text-center text-red-500">Failed to load</div>;

  const cards = [
    { label: 'Total Revenue', value: `₹${data.total_revenue.toLocaleString()}`, icon: '💰', color: 'from-green-500 to-emerald-600' },
    { label: 'This Month', value: `₹${data.month_revenue.toLocaleString()}`, icon: '📈', color: 'from-blue-500 to-cyan-600' },
    { label: 'Active Subs', value: data.active_subscriptions, icon: '👥', color: 'from-purple-500 to-pink-600' },
    { label: 'Active Plans', value: data.total_plans, icon: '📦', color: 'from-orange-500 to-red-600' },
  ];

  return (
    <div className="p-6">
      <PageHeader
        icon="💰"
        title="Revenue Dashboard"
        subtitle="Track subscriptions, payments, and revenue"
      />

      <div className="flex justify-end mb-4">
        <button
          onClick={load}
          className="text-xs bg-slate-100 hover:bg-slate-200 px-3 py-1.5 rounded"
        >
          🔄 Refresh
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {cards.map((c, i) => (
          <div key={i} className={`bg-gradient-to-br ${c.color} text-white rounded-2xl p-5 shadow-lg`}>
            <div className="flex justify-between items-start">
              <div className="text-3xl">{c.icon}</div>
            </div>
            <div className="mt-3 text-sm opacity-90">{c.label}</div>
            <div className="text-3xl font-bold mt-1">{c.value}</div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* By Plan */}
        <div className="bg-white rounded-2xl shadow p-5">
          <h3 className="font-bold text-slate-800 mb-4">📊 Subscriptions by Plan</h3>
          {data.by_plan.length === 0 ? (
            <div className="text-slate-400 text-sm text-center py-8">No subscriptions yet</div>
          ) : (
            <div className="space-y-3">
              {data.by_plan.map((p, i) => {
                const total = data.by_plan.reduce((a, b) => a + b.count, 0);
                const pct = total ? Math.round((p.count / total) * 100) : 0;
                return (
                  <div key={i}>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="font-medium text-slate-700">{p.plan}</span>
                      <span className="text-slate-500">{p.count} ({pct}%)</span>
                    </div>
                    <div className="w-full bg-slate-100 rounded-full h-2">
                      <div
                        className="bg-gradient-to-r from-purple-500 to-pink-500 h-2 rounded-full transition-all"
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Recent Payments */}
        <div className="bg-white rounded-2xl shadow p-5">
          <h3 className="font-bold text-slate-800 mb-4">💳 Recent Payments</h3>
          {data.recent_payments.length === 0 ? (
            <div className="text-slate-400 text-sm text-center py-8">No payments yet</div>
          ) : (
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {data.recent_payments.map((p) => (
                <div key={p.id} className="flex justify-between items-center p-2 border-b last:border-0 text-sm">
                  <div>
                    <div className="font-mono text-xs text-slate-500">{p.user_id?.slice(0, 8)}...</div>
                    <div className="text-xs text-slate-400">
                      {p.created_at ? new Date(p.created_at).toLocaleString() : ''}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="font-bold text-green-600">₹{p.amount}</div>
                    <Badge color={p.status === 'success' ? 'green' : 'red'}>{p.status}</Badge>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* All Subscriptions Table */}
      <div className="bg-white rounded-2xl shadow">
        <div className="p-4 border-b">
          <h3 className="font-bold text-slate-800">📋 All Subscriptions</h3>
        </div>
        {subs.length === 0 ? (
          <div className="p-8 text-center text-slate-400 text-sm">No subscriptions yet</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 text-slate-500 text-xs uppercase">
                <tr>
                  <th className="text-left p-3">User</th>
                  <th className="text-left p-3">Plan</th>
                  <th className="text-center p-3">Status</th>
                  <th className="text-right p-3">Start</th>
                  <th className="text-right p-3">End</th>
                </tr>
              </thead>
              <tbody>
                {subs.map((s) => (
                  <tr key={s.id} className="border-b hover:bg-slate-50">
                    <td className="p-3 text-slate-700">{s.email || s.user_id?.slice(0, 12)}</td>
                    <td className="p-3"><Badge color="purple">{s.plan}</Badge></td>
                    <td className="p-3 text-center">
                      <Badge color={s.status === 'active' ? 'green' : 'red'}>{s.status}</Badge>
                    </td>
                    <td className="p-3 text-right text-slate-500">
                      {s.start_date ? new Date(s.start_date).toLocaleDateString() : '—'}
                    </td>
                    <td className="p-3 text-right text-slate-500">
                      {s.end_date ? new Date(s.end_date).toLocaleDateString() : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}