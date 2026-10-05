import React, { useState, useEffect } from 'react';
import { PageHeader, Badge, Alert } from '../../components/ui/Components';
import GradeBadge from '../../components/GradeBadge';
import { adminAPI, publicAPI } from '../../services/api';

const safeArr = (v) => {
  if (Array.isArray(v)) return v;
  if (v && typeof v === 'object') {
    if (Array.isArray(v.items)) return v.items;
    if (Array.isArray(v.data)) return v.data;
  }
  return [];
};
const safeStr = (v, fb = '—') => (v == null || v === '') ? fb : String(v);

export default function TrustDirectory() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filterRole, setFilterRole] = useState('all');

    useEffect(() => {
    setLoading(true);
    publicAPI.directory()
      .then((r) => {
        setUsers(safeArr(r.data));
        setLoading(false);
      })
      .catch(() => {
        setError('Failed to load directory');
        setLoading(false);
      });
  }, []);

  const getRoles = (u) => {
    if (Array.isArray(u.roles)) return u.roles.map((r) => String(r).toUpperCase());
    if (u.role) return [String(u.role).toUpperCase()];
    return [];
  };

  const agents = users.filter((u) => getRoles(u).includes('AGENT'));
  const brokers = users.filter((u) => getRoles(u).includes('BROKER'));

  const displayed = filterRole === 'agents' ? agents :
                    filterRole === 'brokers' ? brokers :
                    [...agents, ...brokers];

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <PageHeader
        icon="🛡"
        title="Trust Directory"
        subtitle="Verified agents and brokers with performance grades"
        image="https://images.unsplash.com/photo-1552664730-d307ca884978?w=1600&q=80"
      />

      {error && <Alert type="danger" title="Error" onClose={() => setError('')}>{error}</Alert>}

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-gradient-to-br from-yellow-400 to-yellow-600 rounded-xl p-4 text-white">
          <p className="text-sm opacity-90">Elite (A Grade)</p>
          <p className="text-3xl font-bold mt-1">0</p>
        </div>
        <div className="bg-gradient-to-br from-slate-400 to-slate-600 rounded-xl p-4 text-white">
          <p className="text-sm opacity-90">Trusted (B Grade)</p>
          <p className="text-3xl font-bold mt-1">0</p>
        </div>
        <div className="bg-gradient-to-br from-amber-600 to-amber-800 rounded-xl p-4 text-white">
          <p className="text-sm opacity-90">Verified (C Grade)</p>
          <p className="text-3xl font-bold mt-1">0</p>
        </div>
        <div className="bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl p-4 text-white">
          <p className="text-sm opacity-90">Total Agents + Brokers</p>
          <p className="text-3xl font-bold mt-1">{agents.length + brokers.length}</p>
        </div>
      </div>

      {/* Filter */}
      <div className="mb-4 flex gap-2">
        {[
          { id: 'all', label: `All (${agents.length + brokers.length})` },
          { id: 'agents', label: `Agents (${agents.length})` },
          { id: 'brokers', label: `Brokers (${brokers.length})` },
        ].map((t) => (
          <button
            key={t.id}
            onClick={() => setFilterRole(t.id)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              filterRole === t.id
                ? 'bg-blue-600 text-white shadow-lg'
                : 'bg-white border border-slate-200 hover:border-blue-400'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Directory */}
      {loading ? (
        <div className="text-center py-10 text-slate-400">Loading directory…</div>
      ) : displayed.length === 0 ? (
        <div className="text-center py-10 text-slate-400 bg-white rounded-xl border border-slate-200">
          No agents or brokers yet
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {displayed.map((u) => {
            const roles = getRoles(u);
            const isAgent = roles.includes('AGENT');
            return (
              <div key={u.id} className="bg-white p-5 rounded-xl border border-slate-200 hover:shadow-lg transition-all">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center text-white font-bold">
                      {safeStr(u.full_name || u.email).charAt(0).toUpperCase()}
                    </div>
                    <div>
                      <p className="font-bold text-slate-800">{safeStr(u.full_name)}</p>
                      <p className="text-xs text-slate-500">{isAgent ? 'Agent' : 'Broker'}</p>
                    </div>
                  </div>
                  <GradeBadge grade={u.grade || 'C'} trend={u.trend} size="sm" />
                </div>

                <div className="space-y-1 text-sm text-slate-600 mb-3">
                  <p>📧 {safeStr(u.email)}</p>
                  {u.phone && <p>📞 {safeStr(u.phone)}</p>}
                  <p className="text-xs">
                    Status: <Badge color={u.status === 'ACTIVE' ? 'green' : 'gray'}>{safeStr(u.status)}</Badge>
                  </p>
                </div>

                <button className="w-full py-2 bg-slate-100 hover:bg-slate-200 rounded-lg text-sm font-medium">
                  Contact
                </button>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}