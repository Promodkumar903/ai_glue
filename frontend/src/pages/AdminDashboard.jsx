import { useState, useEffect } from 'react';
import { useAuth } from '../lib/auth-context';
import { Users, Building2, DollarSign, Activity, Shield, AlertTriangle } from 'lucide-react';
import axios from '../utils/axios';
import ActiveBanner from '../components/ActiveBanner';

export default function AdminDashboard() {
  const { user, logout } = useAuth();
  const [metrics, setMetrics] = useState({
    total_users: 0,
    active_users: 0,
    total_organizations: 0,
    total_revenue: 0,
    total_placements: 0,
  });
  const [connectors, setConnectors] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // 1. Live Metrics
        const metricsRes = await axios.get('/admin/dashboard/metrics').catch(() => ({ data: {} }));
        setMetrics({
          total_users: metricsRes.data?.total_users || 0,
          active_users: metricsRes.data?.active_users || 0,
          total_organizations: metricsRes.data?.total_organizations || 0,
          total_revenue: metricsRes.data?.total_revenue || 0,
          total_placements: metricsRes.data?.total_placements || 0,
        });

        // 2. Connectors
        const connRes = await axios.get('/admin/connectors').catch(() => ({ data: [] }));
        setConnectors(Array.isArray(connRes.data) ? connRes.data : []);
      } catch (e) {
        console.error('Admin data fetch error:', e);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const alerts = [
    { title: '1 Connector Down (Germany Visa API)', action: 'Fix', priority: 'critical' },
    { title: 'Queue backlog: 234 pending jobs', action: 'Investigate', priority: 'warning' },
    { title: 'AI Model accuracy dropped 2%', action: 'Review', priority: 'warning' },
  ];

  const pendingVerifications = [
    { label: 'Organizations', value: 15 },
    { label: 'Agents', value: 8 },
    { label: 'Documents', value: 45 },
  ];

  return (
    <div className="min-h-screen bg-slate-50 p-6">
      <ActiveBanner />
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">
            ⚙️ Master Admin — War Room
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            System Health, Metrics, Governance
          </p>
        </div>
        <button
          onClick={logout}
          className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg transition"
        >
          Logout
        </button>
      </div>

      {/* System Health */}
      <div className="bg-green-50 border border-green-200 p-4 rounded-xl mb-6">
        <div className="flex items-center gap-3">
          <span className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></span>
          <p className="text-sm font-medium text-green-800">
            All Systems Operational — API 99.8% uptime, Avg Latency 45ms
          </p>
        </div>
      </div>

      {/* Critical Alerts */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 mb-6">
        <h2 className="text-lg font-semibold text-slate-800 mb-4">
          🚨 Alerts ({alerts.length})
        </h2>
        <div className="space-y-3">
          {alerts.map((item, i) => (
            <div key={i} className="flex justify-between items-center border-b pb-2 last:border-0">
              <p className="text-sm text-slate-700">
                {item.priority === 'critical' ? '🔴' : '🟡'} {item.title}
              </p>
              <button className="text-blue-600 hover:text-blue-800 text-sm font-medium">
                {item.action} →
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Main Stats */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
        <StatCard icon={<Users />} label="Total Users" value={metrics.total_users.toLocaleString()} color="blue" />
        <StatCard icon={<Activity />} label="Active Users" value={metrics.active_users.toLocaleString()} color="green" />
        <StatCard icon={<Building2 />} label="Organizations" value={metrics.total_organizations.toLocaleString()} color="orange" />
        <StatCard icon={<DollarSign />} label="Revenue" value={`$${metrics.total_revenue.toLocaleString()}`} color="purple" />
        <StatCard icon={<Shield />} label="Placements" value={metrics.total_placements.toLocaleString()} color="blue" />
      </div>

      {/* Pending Verifications + Connectors */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Pending Verifications */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <h3 className="font-semibold text-gray-700 mb-4">📋 Pending Verifications</h3>
          <div className="space-y-3">
            {pendingVerifications.map((item, i) => (
              <div key={i} className="flex justify-between items-center border-b pb-2 last:border-0">
                <span className="text-sm text-slate-700">{item.label}</span>
                <span className="px-3 py-1 rounded-full text-xs font-semibold bg-yellow-100 text-yellow-700">
                  {item.value}
                </span>
              </div>
            ))}
          </div>
          <button className="mt-4 w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg transition">
            Review All
          </button>
        </div>

        {/* Connectors Status */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <h3 className="font-semibold text-gray-700 mb-4">🔌 Connectors Status</h3>
          {loading ? (
            <p className="text-gray-400">Loading...</p>
          ) : connectors.length === 0 ? (
            <div className="space-y-2">
              <ConnectorRow name="Germany Visa API" status="down" />
              <ConnectorRow name="Canada IRCC" status="healthy" />
              <ConnectorRow name="UK Visa Portal" status="healthy" />
              <ConnectorRow name="AI Model API" status="healthy" />
              <ConnectorRow name="Payment Gateway" status="degraded" />
            </div>
          ) : (
            <div className="space-y-2">
              {connectors.map((c, i) => (
                <ConnectorRow
                  key={i}
                  name={c.name}
                  status={(c.status || 'healthy').toLowerCase()}
                />
              ))}
            </div>
          )}
        </div>
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
        <p className="text-xs font-medium">{label}</p>
        <p className="text-lg font-bold">{value}</p>
      </div>
    </div>
  );
};

const ConnectorRow = ({ name, status }) => {
  const statusColors = {
    healthy: 'bg-green-100 text-green-700',
    degraded: 'bg-yellow-100 text-yellow-700',
    down: 'bg-red-100 text-red-700',
  };
  const dots = {
    healthy: '🟢',
    degraded: '🟡',
    down: '🔴',
  };
  return (
    <div className="flex justify-between items-center py-2 border-b last:border-0">
      <span className="text-sm text-slate-700">{name}</span>
      <span className={`px-2 py-1 rounded-full text-xs font-semibold ${statusColors[status] || statusColors.healthy}`}>
        {dots[status] || '🟢'} {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    </div>
  );
};