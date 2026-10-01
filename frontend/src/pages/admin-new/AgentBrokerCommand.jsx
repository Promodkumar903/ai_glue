import React, { useState, useEffect } from 'react';
import { PageHeader, Card, DataTable, Badge, Tabs, Alert, ProgressBar } from '../../components/ui/Components';
import { agentAPI, brokerAPI, adminAPI, referralAPI } from '../../services/api';
import GradeBadge from '../../components/GradeBadge';

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

export default function AgentBrokerCommand() {
  const [tab, setTab] = useState('agents');
  const [agents, setAgents] = useState([]);
  const [brokers, setBrokers] = useState([]);
  const [agentPerf, setAgentPerf] = useState([]);
  const [clients, setClients] = useState([]);
  const [referralLb, setReferralLb] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let cancelled = false;
    setLoading(true);

    Promise.allSettled([
      adminAPI.users(),
      brokerAPI.agentPerformance(),
      brokerAPI.clients(),
      referralAPI.leaderboard(),
    ]).then(([u, ap, cl, rl]) => {
      if (cancelled) return;

      if (u.status === 'fulfilled') {
        const all = safeArr(u.value?.data);
        const getUserRoles = (x) => {
          const roles = Array.isArray(x?.roles) ? x.roles : (x?.role ? [x.role] : []);
          return roles.map((r) => String(r).toUpperCase().replace('-', '_'));
        };
        setAgents(all.filter((x) => getUserRoles(x).includes('AGENT')));
        setBrokers(all.filter((x) => getUserRoles(x).includes('BROKER')));
      }
      if (ap.status === 'fulfilled') setAgentPerf(safeArr(ap.value?.data));
      if (cl.status === 'fulfilled') setClients(safeArr(cl.value?.data));
      if (rl.status === 'fulfilled') setReferralLb(safeArr(rl.value?.data));

      if (u.status === 'rejected' && ap.status === 'rejected' && cl.status === 'rejected') {
        setError('Failed to load agent/broker data — check backend');
      }
      setLoading(false);
    }).catch(() => {
      if (!cancelled) { setError('Unexpected error'); setLoading(false); }
    });

    return () => { cancelled = true; };
  }, []);

  // Sort leaderboard by success / commission
  const sortedAgents = [...agentPerf].sort((a, b) =>
    safeNum(b?.commission_earned ?? b?.offers ?? 0) - safeNum(a?.commission_earned ?? a?.offers ?? 0)
  );

  const totalEarned = agentPerf.reduce((s, a) => s + safeNum(a?.commission_earned ?? 0), 0);
  const totalPending = agentPerf.reduce((s, a) => s + safeNum(a?.commission_pending ?? 0), 0);
  const totalCandidates = agentPerf.reduce((s, a) => s + safeNum(a?.total_apps ?? a?.candidates ?? 0), 0);
  const totalHired = agentPerf.reduce((s, a) => s + safeNum(a?.joined ?? a?.hired ?? 0), 0);

  return (
    <div className="p-6">
      <PageHeader
        icon="🤝"
        title="Agent & Broker Command Center"
        subtitle="Performance, Commission, Ranking & Clients — Full Control"
        image="https://images.unsplash.com/photo-1552664730-d307ca884978?w=1600&q=80"
      />

      {error && <Alert type="danger" title="API Error" onClose={() => setError('')}>{error}</Alert>}

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <Card title="Total Agents" value={agents.length} icon="🤝" color="blue" />
        <Card title="Total Brokers" value={brokers.length} icon="🏢" color="purple" />
        <Card title="Commission Earned" value={`$${totalEarned.toLocaleString()}`} icon="💰" color="green" />
        <Card title="Commission Pending" value={`$${totalPending.toLocaleString()}`} icon="⏳" color="orange" />
      </div>

      <Tabs
        active={tab}
        onChange={setTab}
        tabs={[
          { id: 'agents', label: 'Agent Leaderboard', icon: '🏆' },
          { id: 'brokers', label: 'Brokers', icon: '🏢', count: brokers.length },
          { id: 'clients', label: 'Client Distribution', icon: '👥', count: clients.length },
          { id: 'referral', label: 'Referral Leaderboard', icon: '🎯', count: referralLb.length },
        ]}
      />

      {/* AGENTS — Leaderboard */}
      {tab === 'agents' && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <Card title="Total Candidates" value={totalCandidates} icon="👥" color="indigo" />
            <Card title="Total Hired" value={totalHired} icon="✅" color="green" />
            <Card title="Avg per Agent" value={agents.length ? Math.round(totalCandidates / agents.length) : 0} icon="📊" color="teal" />
          </div>

          <h3 className="text-lg font-bold mb-3">🏆 Agent Performance Leaderboard</h3>
          <DataTable
            loading={loading}
            empty="No agent performance data yet"
            columns={[
              {
                key: 'rank', label: '#',
                render: (_, i) => {
                  const medal = ['🥇', '🥈', '🥉'][i] || `#${i + 1}`;
                  return <span className="font-bold text-lg">{medal}</span>;
                },
                width: '60px',
              },
              { key: 'agent_name', label: 'Agent', render: (r) => <span className="font-semibold">{safeStr(r.agent_name || r.name || r.agent_id)}</span> },
              {
                key: 'grade', label: 'Grade',
                render: (r) => <GradeBadge grade={r.grade || 'C'} trend={r.trend} size="sm" />,
                width: '100px',
              },
              { key: 'total_apps', label: 'Applications', render: (r) => safeNum(r.total_apps ?? r.candidates ?? 0) },
              { key: 'shortlisted', label: 'Shortlisted', render: (r) => safeNum(r.shortlisted ?? 0) },
              { key: 'offers', label: 'Offers', render: (r) => safeNum(r.offers ?? 0) },
              { key: 'joined', label: 'Joined', render: (r) => <Badge color="green">{safeNum(r.joined ?? r.hired ?? 0)}</Badge> },
              {
                key: 'commission_earned', label: 'Earned',
                render: (r) => <span className="text-emerald-600 font-bold">${safeNum(r.commission_earned ?? 0).toLocaleString()}</span>
              },
              {
                key: 'commission_pending', label: 'Pending',
                render: (r) => <span className="text-orange-600 font-semibold">${safeNum(r.commission_pending ?? 0).toLocaleString()}</span>
              },
            ]}
            data={sortedAgents}
          />

          <h3 className="text-lg font-bold mt-8 mb-3">👥 All Agents ({agents.length})</h3>
          <DataTable
            loading={loading}
            empty="No agents registered"
            columns={[
              { key: 'full_name', label: 'Name', render: (r) => safeStr(r.full_name || r.name) },
              {
                key: 'grade', label: 'Grade',
                render: (r) => <GradeBadge grade={r.grade || 'C'} trend={r.trend} size="sm" showLabel />,
                width: '140px',
              },
              { key: 'email', label: 'Email', render: (r) => safeStr(r.email) },
              { key: 'phone', label: 'Phone', render: (r) => safeStr(r.phone) },
              { key: 'status', label: 'Status', render: (r) => <Badge color={r.status === 'active' ? 'green' : 'gray'}>{safeStr(r.status, 'active')}</Badge> },
            ]}
            data={agents}
          />
        </>
      )}

      {/* BROKERS */}
      {tab === 'brokers' && (
        <>
          <h3 className="text-lg font-bold mb-3">🏢 All Brokers ({brokers.length})</h3>
          <DataTable
            loading={loading}
            empty="No brokers registered"
            columns={[
              { key: 'full_name', label: 'Name', render: (r) => safeStr(r.full_name || r.name) },
              {
                key: 'grade', label: 'Grade',
                render: (r) => <GradeBadge grade={r.grade || 'C'} trend={r.trend} size="sm" showLabel />,
                width: '140px',
              },
              { key: 'email', label: 'Email', render: (r) => safeStr(r.email) },
              { key: 'phone', label: 'Phone', render: (r) => safeStr(r.phone) },
              { key: 'status', label: 'Status', render: (r) => <Badge color={r.status === 'active' ? 'green' : 'gray'}>{safeStr(r.status, 'active')}</Badge> },
            ]}
            data={brokers}
          />
        </>
      )}

      {/* CLIENTS */}
      {tab === 'clients' && (
        <>
          <h3 className="text-lg font-bold mb-3">👥 Client Distribution</h3>
          <DataTable
            loading={loading}
            empty="No client data"
            columns={[
              { key: 'client_name', label: 'Client', render: (r) => safeStr(r.client_name || r.name) },
              { key: 'total_apps', label: 'Applications', render: (r) => safeNum(r.total_apps ?? 0) },
              { key: 'shortlisted', label: 'Shortlisted', render: (r) => safeNum(r.shortlisted ?? 0) },
              { key: 'hired', label: 'Hired', render: (r) => <Badge color="green">{safeNum(r.hired ?? 0)}</Badge> },
            ]}
            data={clients}
          />
        </>
      )}

      {/* REFERRAL LEADERBOARD */}
      {tab === 'referral' && (
        <>
          <h3 className="text-lg font-bold mb-3">🎯 Referral Leaderboard</h3>
          <DataTable
            loading={loading}
            empty="No referral data"
            columns={[
              { key: 'rank', label: '#', render: (_, i) => <span className="font-bold">{['🥇','🥈','🥉'][i] || `#${i+1}`}</span>, width: '60px' },
              { key: 'user_name', label: 'User', render: (r) => safeStr(r.user_name || r.name || r.user_id) },
              { key: 'total_referrals', label: 'Referrals', render: (r) => safeNum(r.total_referrals ?? r.count ?? 0) },
              { key: 'conversions', label: 'Conversions', render: (r) => safeNum(r.conversions ?? r.converted ?? 0) },
              { key: 'reward', label: 'Reward', render: (r) => `$${safeNum(r.reward ?? 0).toLocaleString()}` },
            ]}
            data={referralLb}
          />
        </>
      )}
    </div>
  );
}