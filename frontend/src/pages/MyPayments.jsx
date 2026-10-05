import React, { useState, useEffect } from 'react';
import { useAuth } from '../lib/auth-context';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function MyPayments() {
  const { user } = useAuth();
  const [payments, setPayments] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = () => {
    if (!user?.id) return;
    setLoading(true);
    fetch(`${API_BASE}/payments/my/${user.id}`)
      .then(r => r.json())
      .then(d => setPayments(d.payments || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(load, [user?.id]);

  const statusColor = (s) => {
    if (s === 'approved') return 'bg-green-100 text-green-700';
    if (s === 'rejected') return 'bg-red-100 text-red-700';
    return 'bg-yellow-100 text-yellow-700';
  };

  const statusLabel = (s) => {
    if (s === 'approved') return '✅ Approved';
    if (s === 'rejected') return '❌ Rejected';
    return '⏳ Pending';
  };

  return (
    <div className="min-h-screen bg-slate-50 p-6">
      <div className="max-w-4xl mx-auto">
        <div className="mb-6 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-slate-800">💳 My Payments</h1>
            <p className="text-sm text-slate-500 mt-1">Track your manual payment submissions</p>
          </div>
          <button onClick={load} className="text-xs bg-slate-100 hover:bg-slate-200 px-3 py-1.5 rounded">🔄 Refresh</button>
        </div>

        {loading ? (
          <div className="text-center py-12 text-slate-500">Loading...</div>
        ) : payments.length === 0 ? (
          <div className="bg-white rounded-2xl shadow p-12 text-center">
            <div className="text-5xl mb-3">📭</div>
            <div className="text-slate-700 font-medium mb-2">No payments yet</div>
            <p className="text-sm text-slate-500 mb-4">Jab aap manual UPI/eSewa/PayPal se payment karenge, woh yahan dikhega</p>
            <a href="/pricing" className="inline-block bg-purple-600 hover:bg-purple-700 text-white px-6 py-2 rounded-lg font-medium text-sm">
              View Plans →
            </a>
          </div>
        ) : (
          <div className="space-y-3">
            {payments.map((p) => (
              <div key={p.id} className="bg-white rounded-xl shadow p-4 border border-slate-200">
                <div className="flex justify-between items-start flex-wrap gap-3">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-bold text-slate-800">{p.plan_name}</span>
                      <span className="text-xs text-slate-400">({p.billing_cycle})</span>
                      <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${statusColor(p.status)}`}>
                        {statusLabel(p.status)}
                      </span>
                    </div>
                    <div className="text-sm text-slate-600">
                      {p.currency} {p.amount} via <span className="font-medium uppercase">{p.method}</span>
                    </div>
                    <div className="text-xs text-slate-400 mt-1">
                      UTR: <span className="font-mono">{p.utr_number || '—'}</span>
                    </div>
                    <div className="text-xs text-slate-400 mt-0.5">
                      Submitted: {new Date(p.created_at).toLocaleString()}
                    </div>
                    {p.admin_note && (
                      <div className="text-xs text-slate-500 mt-2 bg-slate-50 p-2 rounded">
                        <b>Admin note:</b> {p.admin_note}
                      </div>
                    )}
                  </div>
                </div>

                {p.status === 'pending' && (
                  <div className="mt-3 pt-3 border-t text-xs text-slate-500">
                    ⏳ Admin 24 ghante mein verify karega. Ref ID: <span className="font-mono">{p.id.slice(0, 8)}</span>
                  </div>
                )}
                {p.status === 'approved' && (
                  <div className="mt-3 pt-3 border-t text-xs text-green-600">
                    ✅ Subscription activated! <a href="/my-subscription" className="underline">View subscription →</a>
                  </div>
                )}
                {p.status === 'rejected' && (
                  <div className="mt-3 pt-3 border-t text-xs text-red-600">
                    ❌ Payment rejected. Contact support for help.
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}