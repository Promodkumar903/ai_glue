import { useState, useEffect } from 'react';
import { useAuth } from '../lib/auth-context';
import { Users, UserCheck, TrendingUp, DollarSign } from 'lucide-react';
import axios from '../utils/axios';

export default function BrokerDashboard() {
  const { user, logout } = useAuth();
  const [agents, setAgents] = useState([]);
  const [kpi, setKpi] = useState({
    total_candidates: 0,
    shortlisted: 0,
    interviews: 0,
    offers: 0,
    joined: 0,
    revenue: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // 1. Agent Performance
        const agentRes = await axios.get('/broker/agents/performance').catch(() => ({ data: { agents: [] } }));
        const agentList = agentRes.data?.agents || [];
        setAgents(agentList);

        // 2. KPI Stats — Broker Dashboard
        if (user?.id) {
          const kpiRes = await axios.get(`/broker/dashboard/${user.id}`).catch(() => ({ data: {} }));
          setKpi({
            total_candidates: kpiRes.data?.total_candidates || 0,
            shortlisted: kpiRes.data?.shortlisted || 0,
            interviews: kpiRes.data?.interviews || 0,
            offers: kpiRes.data?.offers || 0,
            joined: kpiRes.data?.joined || 0,
            revenue: kpiRes.data?.revenue || 0,
          });
        }
      } catch (e) {
        console.error('Broker data fetch error:', e);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [user]);

  const insights = [
    { title: 'Agent Ravi outperforming by 34%', action: 'View', priority: 'high' },
    { title: 'Revenue up 12% this month', action: 'Details', priority: 'medium' },
  ];

  // Total candidates = sum of agent total_apps (ya KPI से)
  const totalCandidates = kpi.total_candidates || agents.reduce((sum, a) => sum + (a.total_apps || 0), 0);
  const totalRevenue = kpi.revenue || 0;
  const totalCommission = Math.round(totalRevenue * 0.10); // 10% commission estimate

  return (
    <div className="min-h-screen bg-slate-50 p-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">
            🏢 Broker Dashboard, {user?.full_name || user?.email?.split('@')[0] || 'Broker'}
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Agency Health, Revenue, Agent Performance
          </p>
        </div>
        <button
          onClick={logout}
          className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg transition"
        >
          Logout
        </button>
      </div>

      {/* AI Insights */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 mb-6">
        <h2 className="text-lg font-semibold text-slate-800 mb-4">🧠 AI Glue Insights</h2>
        <div className="space-y-3">
          {insights.map((item, i) => (
            <div key={i} className="flex justify-between items-center border-b pb-2 last:border-0">
              <p className="text-sm text-slate-700">
                {item.priority === 'high' ? '🔴' : '🟡'} {item.title}
              </p>
              <button className="text-blue-600 hover:text-blue-800 text-sm font-medium">
                {item.action} →
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <StatCard icon={<Users />} label="Agents" value={agents.length} color="blue" />
        <StatCard icon={<UserCheck />} label="Candidates" value={totalCandidates} color="green" />
        <StatCard icon={<TrendingUp />} label="Revenue" value={`$${totalRevenue.toLocaleString()}`} color="orange" />
        <StatCard icon={<DollarSign />} label="Commission" value={`$${totalCommission.toLocaleString()}`} color="purple" />
      </div>

      {/* Agent Performance Table */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
        <h3 className="font-semibold text-gray-700 mb-4">👥 Agent Performance</h3>
        {loading ? (
          <p className="text-gray-400">Loading...</p>
        ) : agents.length === 0 ? (
          <p className="text-gray-400">No agents yet.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-slate-500">
                  <th className="py-2">Agent Name</th>
                  <th className="py-2">Total Apps</th>
                  <th className="py-2">Shortlisted</th>
                  <th className="py-2">Interviews</th>
                  <th className="py-2">Offers</th>
                  <th className="py-2">Joined</th>
                </tr>
              </thead>
              <tbody>
                {agents.map((a, i) => (
                  <tr key={i} className="border-b last:border-0">
                    <td className="py-3 font-medium text-slate-800">{a.agent_name}</td>
                    <td className="py-3">{a.total_apps}</td>
                    <td className="py-3 text-green-600">{a.shortlisted}</td>
                    <td className="py-3 text-blue-600">{a.interviews}</td>
                    <td className="py-3 text-yellow-600">{a.offers}</td>
                    <td className="py-3 text-purple-600">{a.joined}</td>
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

const StatCard = ({ icon, label, value, color }) => {
  const colors = {
    blue: 'border-blue-200 bg-blue-50 text-blue-700',
    green: 'border-green-200 bg-green-50 text-green-700',
    orange: 'border-orange-200 bg-orange-50 text-orange-700',
    purple: 'border-purple-200 bg-purple-50 text-purple-700',
  };
  return (
    <div className={`p-4 rounded-xl border ${colors[color] || colors.blue} flex items-center gap-3`}>
      <div className="text-2xl">{icon}</div>
      <div>
        <p className="text-sm">{label}</p>
        <p className="text-xl font-bold">{value}</p>
      </div>
    </div>
  );
};