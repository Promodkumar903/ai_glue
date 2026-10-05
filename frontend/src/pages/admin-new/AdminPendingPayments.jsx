import React, { useState, useEffect } from 'react';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function AdminPendingPayments() {
  const [payments, setPayments] = useState([]);
  const [status, setStatus] = useState('pending');
  const [loading, setLoading] = useState(true);
  const [msg, setMsg] = useState('');
  const [selected, setSelected] = useState(null);

  const load = () => {
    setLoading(true);
    fetch(`${API_BASE}/admin/payments/pending?status=${status}`)
      .then(r => r.json())
      .then(d => setPayments(d.payments || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(load, [status]);

  const approve = async (id) => {
    if (!window.confirm('Approve this payment? Subscription will activate.')) return;
    try {
      const res = await fetch(`${API_BASE}/admin/payments/${id}/approve`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ admin_note: 'Verified manually' }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail);
      setMsg(`✅ Approved! Subscription for ${data.plan} activated.`);
      setSelected(null);
      load();
    } catch (e) { setMsg(`❌ ${e.message}`); }
  };

  const reject = async (id) => {
    const reason = window.prompt('Rejection reason:');
    if (reason === null) return;
    try {
      const res = await fetch(`${API_BASE}/admin/payments/${id}/reject`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reject_reason: reason }),
      });
      if (!res.ok) throw new Error('Reject failed');
      setMsg('❌ Payment rejected');
      setSelected(null);
      load();
    } catch (e) { setMsg(`❌ ${e.message}`); }
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-800">💳 Pending Payments</h1>
        <p className="text-sm text-slate-500 mt-1">Verify manual UPI/eSewa/PayPal payments</p>
      </div>

      {msg && <div className="mb-4 p-3 bg-blue-100 text-blue-800 rounded-lg">{msg}</div>}

      <div className="flex gap-2 mb-4">
        {['pending', 'approved', 'rejected'].map(s => (
          <button key={s} onClick={() => setStatus(s)} className={`px-4 py-2 rounded-lg text-sm font-medium ${status === s ? 'bg-purple-600 text-white' : 'bg-white border hover:bg-slate-50'}`}>
            {s.charAt(0).toUpperCase() + s.slice(1)}
          </button>
        ))}
        <button onClick={load} className="ml-auto text-xs bg-slate-100 hover:bg-slate-200 px-3 py-1.5 rounded">🔄 Refresh</button>
      </div>

      {loading ? (
        <div className="text-center py-8 text-slate-500">Loading...</div>
      ) : payments.length === 0 ? (
        <div className="bg-white rounded-xl shadow p-8 text-center text-slate-500">
          No {status} payments
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 text-xs uppercase text-slate-500">
              <tr>
                <th className="text-left p-3">User</th>
                <th className="text-left p-3">Plan</th>
                <th className="text-left p-3">Method</th>
                <th className="text-right p-3">Amount</th>
                <th className="text-left p-3">UTR</th>
                <th className="text-right p-3">Date</th>
                <th className="text-center p-3">Actions</th>
              </tr>
            </thead>
            <tbody>
              {payments.map(p => (
                <tr key={p.id} className="border-t hover:bg-slate-50">
                  <td className="p-3"><div className="text-slate-700 text-xs">{p.user_email || p.user_id.slice(0, 12)}</div></td>
                  <td className="p-3"><span className="bg-purple-100 text-purple-700 px-2 py-1 rounded text-xs font-medium">{p.plan_name}</span></td>
                  <td className="p-3"><span className="bg-blue-100 text-blue-700 px-2 py-1 rounded text-xs font-medium">{p.method}</span></td>
                  <td className="p-3 text-right font-semibold">{p.currency} {p.amount}</td>
                  <td className="p-3 font-mono text-xs">{p.utr_number || '—'}</td>
                  <td className="p-3 text-right text-xs text-slate-500">{new Date(p.created_at).toLocaleString()}</td>
                  <td className="p-3">
                    {status === 'pending' && (
                      <div className="flex gap-2 justify-center">
                        <button onClick={() => approve(p.id)} className="text-xs bg-green-100 hover:bg-green-200 text-green-700 px-2 py-1 rounded">✓ Approve</button>
                        <button onClick={() => reject(p.id)} className="text-xs bg-red-100 hover:bg-red-200 text-red-700 px-2 py-1 rounded">✕ Reject</button>
                      </div>
                    )}
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