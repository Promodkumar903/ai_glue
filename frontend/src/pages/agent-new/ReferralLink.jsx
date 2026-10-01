import React, { useState, useEffect } from 'react';
import { PageHeader, Card, DataTable, Badge, Button, Alert } from '../../components/ui/Components';
import { referralAPI } from '../../services/api';

const safeArr = (v) => {
  if (Array.isArray(v)) return v;
  if (v && typeof v === 'object') {
    if (Array.isArray(v.items)) return v.items;
    if (Array.isArray(v.data)) return v.data;
  }
  return [];
};
const safeStr = (v, fb = '—') => (v == null || v === '') ? fb : String(v);

export default function ReferralLink() {
  const [link, setLink] = useState('');
  const [stats, setStats] = useState({});
  const [leaderboard, setLeaderboard] = useState([]);
  const [loading, setLoading] = useState(true);
  const [msg, setMsg] = useState(null);

  const userId = JSON.parse(localStorage.getItem('user') || '{}')?.id;

  useEffect(() => {
    if (!userId) { setLoading(false); return; }
    Promise.allSettled([referralAPI.link(userId), referralAPI.stats(userId), referralAPI.leaderboard()])
      .then(([l, s, lb]) => {
        if (l.status === 'fulfilled') setLink(l.value.data?.link || l.value.data?.url || '');
        if (s.status === 'fulfilled') setStats(typeof s.value.data === 'object' ? s.value.data : {});
        if (lb.status === 'fulfilled') setLeaderboard(safeArr(lb.value.data));
        setLoading(false);
      });
  }, [userId]);

  const copyLink = () => {
    if (!link) return;
    navigator.clipboard.writeText(link);
    setMsg({ type: 'success', text: '✅ Link copied to clipboard!' });
    setTimeout(() => setMsg(null), 2000);
  };

  return (
    <div className="p-6">
      <PageHeader icon="🔗" title="Referral Program" subtitle="Share your link, earn rewards"
        image="https://images.unsplash.com/photo-1556761175-b413da4baf72?w=1600&q=80"
      />

      {msg && <Alert type={msg.type} onClose={() => setMsg(null)}>{msg.text}</Alert>}

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <Card title="Total Referrals" value={stats.total_referrals || 0} icon="👥" color="blue" />
        <Card title="Conversions" value={stats.conversions || stats.converted || 0} icon="✅" color="green" />
        <Card title="Reward Earned" value={`$${(stats.reward || 0).toLocaleString()}`} icon="💰" color="purple" />
        <Card title="Pending" value={stats.pending || 0} icon="⏳" color="orange" />
      </div>

      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl shadow p-6 mb-6 text-white">
        <h3 className="font-bold mb-3">🎯 Your Referral Link</h3>
        <div className="flex gap-2 items-center">
          <input
            value={link || 'Link generate ho raha hai...'}
            readOnly
            className="flex-1 px-4 py-2 rounded-lg text-gray-800 font-mono text-sm"
          />
          <Button variant="success" onClick={copyLink} disabled={!link}>📋 Copy</Button>
        </div>
        <p className="text-xs opacity-80 mt-3">Share this link — har successful referral pe reward milega!</p>
      </div>

      <h3 className="text-lg font-bold mb-3">🏆 Top Referrers</h3>
      <DataTable
        loading={loading}
        empty="Koi referral data nahi"
        columns={[
          { key: 'rank', label: '#', render: (_, i) => <span className="font-bold">{['🥇','🥈','🥉'][i] || `#${i+1}`}</span>, width: '60px' },
          { key: 'user_name', label: 'User', render: (r) => safeStr(r.user_name || r.name || r.user_id) },
          { key: 'total_referrals', label: 'Referrals', render: (r) => r.total_referrals || r.count || 0 },
          { key: 'conversions', label: 'Conversions', render: (r) => r.conversions || 0 },
          { key: 'reward', label: 'Reward', render: (r) => `$${(r.reward || 0).toLocaleString()}` },
        ]}
        data={leaderboard}
      />
    </div>
  );
}