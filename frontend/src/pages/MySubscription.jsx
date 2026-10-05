import React, { useState, useEffect } from 'react';
import { useAuth } from '../lib/auth-context';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function MySubscription() {
  const { user } = useAuth();
  const [subscription, setSubscription] = useState(null);
  const [invoices, setInvoices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const load = () => {
    if (!user?.id) return;
    setLoading(true);
    Promise.all([
      fetch(`${API_BASE}/subscriptions/me/${user.id}`).then((r) => r.json()),
      fetch(`${API_BASE}/subscriptions/invoices/${user.id}`).then((r) => r.json()),
    ])
      .then(([sub, inv]) => {
        setSubscription(sub.subscription);
        setInvoices(inv.invoices || []);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  };

  useEffect(load, [user?.id]);

  const handleCancel = async () => {
    if (!window.confirm('Cancel your subscription? You will lose access at the end of the billing period.')) return;
    try {
      const res = await fetch(`${API_BASE}/subscriptions/cancel/${user.id}`, { method: 'POST' });
      if (!res.ok) throw new Error('Cancel failed');
      setSuccess('Subscription cancelled');
      load();
    } catch (e) {
      setError(e.message);
    }
  };

  const daysLeft = (end) => {
    if (!end) return 0;
    const diff = new Date(end) - new Date();
    return Math.max(0, Math.ceil(diff / (1000 * 60 * 60 * 24)));
  };

  if (loading) return <div className="p-6 text-center text-slate-500">Loading...</div>;

  return (
    <div className="min-h-screen bg-slate-50 p-6">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-slate-800 mb-6">💳 My Subscription</h1>

        {error && <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-lg">{error}</div>}
        {success && <div className="mb-4 p-3 bg-green-100 text-green-700 rounded-lg">{success}</div>}

        {subscription ? (
          <div className="bg-white rounded-2xl shadow-lg p-6 mb-6">
            <div className="flex justify-between items-start flex-wrap gap-4">
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-2xl font-bold text-slate-800">{subscription.plan.name}</span>
                  <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                    subscription.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                  }`}>
                    {subscription.status.toUpperCase()}
                  </span>
                </div>
                <p className="text-slate-500 text-sm">{subscription.plan.description}</p>
              </div>
              <button
                onClick={handleCancel}
                className="px-4 py-2 bg-red-50 hover:bg-red-100 text-red-600 rounded-lg text-sm font-medium"
              >
                Cancel Subscription
              </button>
            </div>

            <div className="grid grid-cols-3 gap-4 mt-6">
              <div className="bg-slate-50 rounded-lg p-4">
                <div className="text-xs text-slate-500 uppercase">Started</div>
                <div className="font-semibold text-slate-800">
                  {subscription.start_date ? new Date(subscription.start_date).toLocaleDateString() : '—'}
                </div>
              </div>
              <div className="bg-slate-50 rounded-lg p-4">
                <div className="text-xs text-slate-500 uppercase">Ends</div>
                <div className="font-semibold text-slate-800">
                  {subscription.end_date ? new Date(subscription.end_date).toLocaleDateString() : '—'}
                </div>
              </div>
              <div className="bg-slate-50 rounded-lg p-4">
                <div className="text-xs text-slate-500 uppercase">Days Left</div>
                <div className="font-semibold text-purple-600">{daysLeft(subscription.end_date)} days</div>
              </div>
            </div>

            <div className="mt-6">
              <h3 className="font-bold text-slate-700 mb-3">Features Included</h3>
              <ul className="grid grid-cols-2 gap-2">
                {(subscription.plan.features || []).map((f, i) => (
                  <li key={i} className="flex items-center gap-2 text-sm text-slate-600">
                    <span className="text-green-500">✓</span>{f}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        ) : (
          <div className="bg-white rounded-2xl shadow p-8 text-center mb-6">
            <div className="text-4xl mb-2">📦</div>
            <div className="text-slate-700 font-medium">No active subscription</div>
            <a href="/pricing" className="inline-block mt-3 text-purple-600 hover:underline text-sm">
              View plans →
            </a>
          </div>
        )}

        {/* Invoices */}
        <div className="bg-white rounded-2xl shadow">
          <div className="p-4 border-b">
            <h3 className="font-bold text-slate-800">🧾 Payment History</h3>
          </div>
          {invoices.length === 0 ? (
            <div className="p-8 text-center text-slate-400 text-sm">No invoices yet</div>
          ) : (
            <table className="w-full text-sm">
              <thead className="bg-slate-50 text-slate-500 text-xs uppercase">
                <tr>
                  <th className="text-left p-3">Invoice #</th>
                  <th className="text-left p-3">Description</th>
                  <th className="text-right p-3">Amount</th>
                  <th className="text-center p-3">Status</th>
                  <th className="text-right p-3">Date</th>
                </tr>
              </thead>
              <tbody>
                {invoices.map((inv) => (
                  <tr key={inv.id} className="border-b hover:bg-slate-50">
                    <td className="p-3 font-mono text-xs">{inv.invoice_number || '—'}</td>
                    <td className="p-3">{inv.description || '—'}</td>
                    <td className="p-3 text-right font-semibold">₹{inv.amount}</td>
                    <td className="p-3 text-center">
                      <span className={`text-xs px-2 py-1 rounded-full ${
                        inv.status === 'paid' ? 'bg-green-100 text-green-700'
                        : inv.status === 'free' ? 'bg-blue-100 text-blue-700'
                        : 'bg-yellow-100 text-yellow-700'
                      }`}>
                        {inv.status}
                      </span>
                    </td>
                    <td className="p-3 text-right text-slate-500">
                      {inv.issued_at ? new Date(inv.issued_at).toLocaleDateString() : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}