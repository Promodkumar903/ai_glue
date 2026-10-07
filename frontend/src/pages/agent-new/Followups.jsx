import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { PageHeader, Card, Badge, Alert, Button } from '../../components/ui/Components';
import { crmAPI } from '../../services/api';

const TABS = [
  { id: 'today', label: '📅 Aaj', icon: '📅' },
  { id: 'overdue', label: '⚠️ Overdue', icon: '⚠️' },
  { id: 'upcoming', label: '🔜 Upcoming', icon: '🔜' },
  { id: 'all', label: '📋 All', icon: '📋' },
];

export default function Followups() {
  const [data, setData] = useState({ followups: [], count: 0 });
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState('today');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const load = (filterType = tab) => {
    setLoading(true);
    crmAPI.listFollowups(filterType)
      .then((r) => setData(r.data))
      .catch((e) => setError(e.response?.data?.detail || 'Failed to load follow-ups'))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(tab); }, [tab]);

  const completeFollowup = async (leadId) => {
    try {
      await crmAPI.completeFollowup(leadId, null, '');
      setSuccess('Follow-up complete — next auto-set for 7 days later');
      load(tab);
    } catch (e) {
      setError('Failed: ' + (e.response?.data?.detail || e.message));
    }
  };

  const snoozeFollowup = async (leadId, days) => {
    const d = new Date();
    d.setDate(d.getDate() + days);
    const isoDate = d.toISOString().slice(0, 10);
    try {
      await crmAPI.setFollowup(leadId, isoDate);
      setSuccess(`Snoozed ${days} days — ${isoDate}`);
      load(tab);
    } catch (e) {
      setError('Failed: ' + (e.response?.data?.detail || e.message));
    }
  };

  const followups = data.followups || [];

  return (
    <div className="p-6">
      <PageHeader icon="📞" title="Follow-ups" subtitle="Aaj ke reminders aur overdue follow-ups" />

      {error && <div className="mb-3"><Alert type="danger" onClose={() => setError('')}>{error}</Alert></div>}
      {success && <div className="mb-3"><Alert type="success" onClose={() => setSuccess('')}>{success}</Alert></div>}

      {/* Tab bar */}
      <div className="flex gap-2 mb-6 border-b">
        {TABS.map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition ${
              tab === t.id
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            {t.label}
          </button>
        ))}
        <div className="ml-auto flex items-center gap-2">
          <span className="text-sm text-gray-500">{data.count} total</span>
          <Button onClick={() => load(tab)}>Refresh</Button>
        </div>
      </div>

      {/* List */}
      {loading ? (
        <p className="text-center py-10 text-gray-500">Loading...</p>
      ) : followups.length === 0 ? (
        <div className="text-center py-16">
          <p className="text-5xl mb-4">🎉</p>
          <p className="text-gray-500">
            {tab === 'today' && 'Aaj koi follow-up nahi hai!'}
            {tab === 'overdue' && 'Koi overdue follow-up nahi hai!'}
            {tab === 'upcoming' && 'Koi upcoming follow-up nahi hai.'}
            {tab === 'all' && 'Koi follow-up set nahi hai.'}
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {followups.map((f) => (
            <div key={f.id} className="bg-white border rounded-lg p-4 hover:shadow-md transition">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <Link to={`/agent/leads/${f.id}`} className="font-semibold text-blue-600 hover:underline">
                      {f.student_name}
                    </Link>
                    <Badge color={
                      f.priority === 'HIGH' ? 'red' :
                      f.priority === 'MEDIUM' ? 'orange' : 'gray'
                    }>{f.priority}</Badge>
                    <Badge color="blue">{f.stage}</Badge>
                  </div>
                  <p className="text-xs text-gray-500">
                    {f.phone || '—'} • {f.country || '—'} • {f.course || '—'}
                  </p>
                  {f.notes && (
                    <p className="text-xs text-gray-600 mt-1 italic">"{f.notes}"</p>
                  )}
                </div>

                <div className="text-right">
                  <p className="text-xs text-gray-500 mb-1">Follow-up:</p>
                  <p className={`text-sm font-semibold ${
                    new Date(f.next_followup) < new Date() ? 'text-red-600' : 'text-blue-600'
                  }`}>
                    {f.next_followup ? new Date(f.next_followup).toLocaleDateString() : '—'}
                  </p>
                </div>
              </div>

              <div className="flex gap-2 mt-3 pt-3 border-t">
                <button
                  onClick={() => completeFollowup(f.id)}
                  className="text-xs px-3 py-1.5 bg-green-50 text-green-700 rounded hover:bg-green-100 font-medium"
                >
                  ✅ Complete (+7 days)
                </button>
                <button
                  onClick={() => snoozeFollowup(f.id, 1)}
                  className="text-xs px-3 py-1.5 bg-yellow-50 text-yellow-700 rounded hover:bg-yellow-100 font-medium"
                >
                  ⏰ Snooze 1 day
                </button>
                <button
                  onClick={() => snoozeFollowup(f.id, 3)}
                  className="text-xs px-3 py-1.5 bg-orange-50 text-orange-700 rounded hover:bg-orange-100 font-medium"
                >
                  📅 +3 days
                </button>
                <Link
                  to={`/agent/leads/${f.id}`}
                  className="text-xs px-3 py-1.5 bg-blue-50 text-blue-700 rounded hover:bg-blue-100 font-medium ml-auto"
                >
                  👁 Open Lead
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}