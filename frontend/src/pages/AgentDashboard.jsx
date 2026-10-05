import { useState, useEffect } from 'react';
import { useAuth } from '../lib/auth-context';
import { Users, UserCheck, Send, Award } from 'lucide-react';
import axios from '../utils/axios';
import ActiveBanner from '../components/ActiveBanner';

export default function AgentDashboard() {
  const { user, logout } = useAuth();
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await axios.get('/agent/candidates').catch(() => ({ data: [] }));
        setCandidates(Array.isArray(res.data) ? res.data : []);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const insights = [
    { title: '5 candidates need consent for submission', action: 'View Pending', priority: 'high' },
    { title: '2 client requirements expiring in 7 days', action: 'View Requirements', priority: 'medium' },
    { title: 'AI recommends 12 new matches', action: 'View Matches', priority: 'low' },
  ];

  return (
    <div className="min-h-screen bg-slate-50 p-6">
      <ActiveBanner />
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">
            🤝 Agent Dashboard, {user?.full_name || user?.email?.split('@')[0] || 'Agent'}
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Your recruitment cockpit — Candidates, Clients, Commissions
          </p>
        </div>
        <button onClick={logout} className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg">
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
                {item.priority === 'high' ? '🔴' : item.priority === 'medium' ? '🟡' : '🟢'} {item.title}
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
        <StatCard icon={<Users />} label="Candidates" value="847" color="blue" />
        <StatCard icon={<UserCheck />} label="Eligible" value="340" color="green" />
        <StatCard icon={<Send />} label="Sent to HR" value="245" color="orange" />
        <StatCard icon={<Award />} label="Shortlisted" value="87" color="purple" />
      </div>

      {/* Funnel */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 mb-6">
        <h3 className="font-semibold text-gray-700 mb-4">📊 Agent Funnel</h3>
        <div className="grid grid-cols-5 gap-2 text-center">
          <FunnelStep label="Applied" value="847" color="bg-blue-100 text-blue-700" />
          <FunnelStep label="Eligible" value="340" color="bg-green-100 text-green-700" />
          <FunnelStep label="Sent" value="245" color="bg-yellow-100 text-yellow-700" />
          <FunnelStep label="Shortlisted" value="87" color="bg-orange-100 text-orange-700" />
          <FunnelStep label="Offers" value="18" color="bg-purple-100 text-purple-700" />
        </div>
      </div>

      {/* Recent Candidates */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
        <h3 className="font-semibold text-gray-700 mb-4">👥 Recent Candidates</h3>
        {loading ? (
          <p className="text-gray-400">Loading...</p>
        ) : candidates.length === 0 ? (
          <p className="text-gray-400">No candidates yet.</p>
        ) : (
          <ul className="divide-y">
            {candidates.slice(0, 5).map((c, i) => (
              <li key={i} className="py-3 flex justify-between items-center">
                <span className="text-sm text-slate-700">
                  {c.name || c.full_name || 'Candidate'}
                </span>
                <span className="px-3 py-1 rounded-full text-xs font-semibold bg-blue-100 text-blue-700">
                  {c.status || 'Active'}
                </span>
              </li>
            ))}
          </ul>
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

const FunnelStep = ({ label, value, color }) => (
  <div className={`p-3 rounded-lg ${color}`}>
    <p className="text-xs font-medium">{label}</p>
    <p className="text-lg font-bold">{value}</p>
  </div>
);