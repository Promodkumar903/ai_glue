import { useEffect, useState } from 'react';
import { Users, TrendingUp } from 'lucide-react';
import axios from '../../utils/axios';
import Hero from '../../components/Hero';

export default function BrokerAgents() {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get('/broker/agents/performance').catch(() => ({ data: { agents: [] } }))
      .then(res => setAgents(res.data?.agents || []))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="p-6">
      <Hero
        title="👥 Agent Performance"
        subtitle="Track your team's placements and commissions"
        imageUrl="https://images.unsplash.com/photo-1600880292203-757bb62b4baf?w=1600&q=80"
      />

      {loading ? (
        <div className="text-center py-12 text-slate-400">Loading...</div>
      ) : agents.length === 0 ? (
        <div className="bg-white p-12 rounded-xl shadow-sm text-center">
          <Users className="w-14 h-14 text-slate-300 mx-auto mb-3" />
          <p className="text-slate-500">No agents in your team yet</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {agents.map((a, i) => (
            <div key={i} className="bg-white p-5 rounded-xl shadow-sm border hover:shadow-md transition">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center text-white font-bold">
                  {(a.agent_name || 'A')[0].toUpperCase()}
                </div>
                <div>
                  <h3 className="font-semibold text-slate-800">{a.agent_name}</h3>
                  <p className="text-xs text-slate-500">Agent ID: {a.agent_id?.slice(0, 8)}</p>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div><span className="text-slate-500">Total:</span> <strong>{a.total_apps}</strong></div>
                <div><span className="text-slate-500">Shortlisted:</span> <strong className="text-green-600">{a.shortlisted}</strong></div>
                <div><span className="text-slate-500">Interviews:</span> <strong className="text-blue-600">{a.interviews}</strong></div>
                <div><span className="text-slate-500">Joined:</span> <strong className="text-purple-600">{a.joined}</strong></div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}