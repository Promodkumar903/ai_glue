import React, { useState, useEffect } from 'react';
import { PageHeader, Card, DataTable, Badge, Tabs, Alert, ProgressBar } from '../../components/ui/Components';
import { reportingAPI, adminAPI, reconciliationAPI, paymentsAPI } from '../../services/api';

const safeArr = (v) => {
  if (Array.isArray(v)) return v;
  if (v && typeof v === 'object') {
    if (Array.isArray(v.items)) return v.items;
    if (Array.isArray(v.data)) return v.data;
    if (Array.isArray(v.results)) return v.results;
  }
  return [];
};
const safeNum = (v) => { const n = Number(v); return isFinite(n) ? n : 0; };
const safeStr = (v, fb = '—') => (v == null || v === '') ? fb : String(v);

export default function RevenueAnalytics() {
  const [tab, setTab] = useState('overview');
  const [revenue, setRevenue] = useState(null);
  const [payments, setPayments] = useState(null);
  const [recon, setRecon] = useState(null);
  const [conversion, setConversion] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    Promise.allSettled([
      reportingAPI.revenue(),
      adminAPI.paymentsSummary(),
      reconciliationAPI.summary(),
      reportingAPI.conversion(),
    ]).then(([r, p, rc, cv]) => {
      if (cancelled) return;
      setRevenue(r.status === 'fulfilled' ? r.value?.data || {} : {});
      setPayments(p.status === 'fulfilled' ? p.value?.data || {} : {});
      setRecon(rc.status === 'fulfilled' ? rc.value?.data || {} : {});
      setConversion(cv.status === 'fulfilled' ? cv.value?.data || {} : {});
      if (r.status === 'rejected' && p.status === 'rejected') {
        setError('Failed to load revenue data');
      }
      setLoading(false);
    }).catch(() => { if (!cancelled) { setError('Unexpected error'); setLoading(false); } });
    return () => { cancelled = true; };
  }, []);

  const totalRevenue = safeNum(revenue?.total ?? revenue?.total_revenue ?? payments?.total ?? 0);
  const pendingPayments = safeNum(payments?.pending ?? recon?.pending ?? 0);
  const collectedPayments = safeNum(payments?.collected ?? recon?.collected ?? 0);
  const totalCommission = safeNum(recon?.total_commission ?? 0);
  const pendingCommission = safeNum(recon?.pending_commission ?? 0);

  const conversionStages = safeArr(conversion?.stages ?? conversion?.funnel ?? []);
  const paymentItems = safeArr(payments?.items ?? payments?.transactions ?? []);
  const reconItems = safeArr(recon?.items ?? recon?.commissions ?? []);

  return (
    <div className="p-6">
      <PageHeader
        icon="💰"
        title="Revenue & Reports"
        subtitle="Payments, Commission, Conversion & Financial Analytics"
        image="https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=1600&q=80"
      />

      {error && <Alert type="danger" onClose={() => setError('')}>{error}</Alert>}

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <Card title="Total Revenue" value={`$${totalRevenue.toLocaleString()}`} icon="💵" color="green" />
        <Card title="Collected" value={`$${collectedPayments.toLocaleString()}`} icon="✅" color="blue" />
        <Card title="Pending Payments" value={`$${pendingPayments.toLocaleString()}`} icon="⏳" color="orange" />
        <Card title="Commission Pending" value={`$${pendingCommission.toLocaleString()}`} icon="💸" color="red" />
      </div>

      <Tabs
        active={tab}
        onChange={setTab}
        tabs={[
          { id: 'overview', label: 'Overview', icon: '📊' },
          { id: 'payments', label: 'Payments', icon: '💳', count: paymentItems.length },
          { id: 'commission', label: 'Commission', icon: '💰', count: reconItems.length },
          { id: 'conversion', label: 'Conversion', icon: '📈' },
        ]}
      />

      {/* OVERVIEW */}
      {tab === 'overview' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-white rounded-xl shadow p-5">
            <h3 className="font-bold mb-3">💵 Revenue Breakdown</h3>
            <div className="space-y-3">
              <ProgressBar label="Collected" value={collectedPayments} max={totalRevenue || 1} color="green" />
              <ProgressBar label="Pending" value={pendingPayments} max={totalRevenue || 1} color="yellow" />
              <ProgressBar label="Total Commission" value={totalCommission} max={totalRevenue || 1} color="blue" />
            </div>
          </div>
          <div className="bg-white rounded-xl shadow p-5">
            <h3 className="font-bold mb-3">📈 Platform Metrics</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between py-2 border-b"><span className="text-gray-600">Total Transactions</span><span className="font-bold">{paymentItems.length}</span></div>
              <div className="flex justify-between py-2 border-b"><span className="text-gray-600">Commission Events</span><span className="font-bold">{reconItems.length}</span></div>
              <div className="flex justify-between py-2"><span className="text-gray-600">Collected %</span><span className="font-bold text-emerald-600">{totalRevenue ? Math.round((collectedPayments / totalRevenue) * 100) : 0}%</span></div>
            </div>
          </div>
        </div>
      )}

      {/* PAYMENTS */}
      {tab === 'payments' && (
        <DataTable
          loading={loading}
          empty="No payments yet"
          columns={[
            { key: 'id', label: 'Payment ID', render: (r) => <span className="font-mono text-xs">{safeStr(r.id || r.payment_id)}</span> },
            { key: 'user', label: 'User', render: (r) => safeStr(r.user_name || r.user_id) },
            { key: 'amount', label: 'Amount', render: (r) => <span className="font-bold text-emerald-600">${safeNum(r.amount).toLocaleString()}</span> },
            { key: 'currency', label: 'Currency', render: (r) => safeStr(r.currency, 'USD') },
            {
              key: 'status', label: 'Status',
              render: (r) => {
                const st = String(r.status || '').toLowerCase();
                const c = { success: 'green', completed: 'green', pending: 'yellow', failed: 'red' }[st] || 'gray';
                return <Badge color={c}>{safeStr(r.status, 'N/A')}</Badge>;
              },
            },
            { key: 'created_at', label: 'Date', render: (r) => r.created_at ? new Date(r.created_at).toLocaleDateString() : '—' },
          ]}
          data={paymentItems}
        />
      )}

      {/* COMMISSION */}
      {tab === 'commission' && (
        <DataTable
          loading={loading}
          empty="No commission records"
          columns={[
            { key: 'agent', label: 'Agent/Broker', render: (r) => safeStr(r.agent_name || r.user_name || r.user_id) },
            { key: 'deal_id', label: 'Deal', render: (r) => safeStr(r.deal_id) },
            { key: 'amount', label: 'Amount', render: (r) => <span className="font-bold">${safeNum(r.amount).toLocaleString()}</span> },
            {
              key: 'status', label: 'Status',
              render: (r) => <Badge color={r.status === 'paid' ? 'green' : r.status === 'pending' ? 'yellow' : 'gray'}>{safeStr(r.status)}</Badge>,
            },
            { key: 'created_at', label: 'Date', render: (r) => r.created_at ? new Date(r.created_at).toLocaleDateString() : '—' },
          ]}
          data={reconItems}
        />
      )}

      {/* CONVERSION */}
      {tab === 'conversion' && (
        <div className="bg-white rounded-xl shadow p-5">
          <h3 className="font-bold mb-4">📈 Conversion Funnel</h3>
          {conversionStages.length === 0 ? (
            <p className="text-gray-500 text-sm text-center py-6">📭 No conversion data</p>
          ) : (
            <div className="space-y-3">
              {conversionStages.map((s, i) => {
                const stage = typeof s === 'object' ? safeStr(s.stage || s.name || `Stage ${i+1}`) : safeStr(s);
                const count = typeof s === 'object' ? safeNum(s.count ?? s.value ?? 0) : 0;
                const max = typeof conversionStages[0] === 'object' ? safeNum(conversionStages[0].count ?? 100) || 100 : 100;
                return <ProgressBar key={i} label={stage} value={count} max={max} color={['blue','purple','yellow','green'][i%4]} />;
              })}
            </div>
          )}
        </div>
      )}
    </div>
  );
}