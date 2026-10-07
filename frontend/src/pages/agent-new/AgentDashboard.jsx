import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { PageHeader, Card } from '../../components/ui/Components';
import { crmAPI } from '../../services/api';

export default function AgentDashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    crmAPI.dashboard()
      .then((r) => setData(r.data))
      .catch((e) => setError(e.response?.data?.detail || 'Dashboard load failed'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="p-6">Loading dashboard...</div>;
  if (error) return <div className="p-6 text-red-600">{error}</div>;
  if (!data) return <div className="p-6">No data</div>;

  const stages = data.by_stage || {};
  const followups = data.followups_today || [];

  return (
    <div className="p-6">
      <PageHeader icon="📊" title="Agent Dashboard" subtitle="Aaj ka plan aur business overview" />

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <Card title="Total Leads" value={data.total_leads || 0} icon="📋" color="blue" />
        <Card title="Follow-ups Today" value={data.followups_today_count || 0} icon="📞" color="green" />
        <Card title="Overdue" value={data.overdue_followups || 0} icon="⚠️" color="red" />
        <Card title="Docs Missing" value={data.documents_missing || 0} icon="📄" color="orange" />
      </div>

      {/* Pipeline */}
      <div className="mb-6 bg-white rounded-lg border p-4">
        <h2 className="font-semibold mb-3">🔄 Pipeline</h2>
        <div className="grid grid-cols-3 md:grid-cols-5 gap-3">
          {['NEW', 'CONTACTED', 'INTERESTED', 'PROFILE_READY', 'DOCUMENTS', 'APPLICATION', 'OFFER', 'VISA', 'ENROLLED', 'LOST'].map((s) => (
            <div key={s} className="bg-gray-50 rounded p-3 text-center">
              <p className="text-xs text-gray-600 mb-1">{s}</p>
              <p className="text-xl font-bold text-blue-600">{stages[s] || 0}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Today's Follow-ups */}
      <div className="bg-white rounded-lg border p-4">
        <h2 className="font-semibold mb-3">📞 Aaj Ke Follow-ups ({followups.length})</h2>

        {followups.length === 0 ? (
          <p className="text-sm text-gray-500 text-center py-6">
            Aaj koi follow-up nahi hai. 🎉
          </p>
        ) : (
          <div className="space-y-2">
            {followups.map((f) => (
              <Link
                key={f.id}
                to={`/agent/leads/${f.id}`}
                className="block border rounded px-4 py-3 hover:bg-blue-50 transition"
              >
                <div className="flex justify-between items-center">
                  <div>
                    <p className="font-semibold">{f.student_name}</p>
                    <p className="text-xs text-gray-500">
                      {f.phone} • {f.country || '—'} • {f.course || '—'}
                    </p>
                  </div>
                  <div className="text-right">
                    <span className={`text-xs px-2 py-1 rounded ${
                      f.priority === 'HIGH' ? 'bg-red-100 text-red-700' :
                      f.priority === 'MEDIUM' ? 'bg-orange-100 text-orange-700' :
                      'bg-gray-100 text-gray-700'
                    }`}>
                      {f.priority}
                    </span>
                    <p className="text-xs text-gray-400 mt-1">
                      {f.next_followup ? new Date(f.next_followup).toLocaleDateString() : '—'}
                    </p>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}