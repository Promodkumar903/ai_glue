import { useState, useEffect } from 'react';
import { useAuth } from '../lib/auth-context';
import { Briefcase, Calendar, Award, UserCheck } from 'lucide-react';
import axios from '../utils/axios';
import ActiveBanner from '../components/ActiveBanner';

export default function JobSeekerDashboard() {
  const { user, logout } = useAuth();
  const [apps, setApps] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await axios.get('/applications').catch(() => ({ data: [] }));
        setApps(Array.isArray(res.data) ? res.data : []);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const insights = [
    { title: 'Your resume needs improvement for AI roles', action: 'Update Resume', priority: 'high' },
    { title: '12 new jobs match your profile', action: 'View Jobs', priority: 'medium' },
  ];

  return (
    <div className="min-h-screen bg-slate-50 p-6">
      <ActiveBanner />
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">
            💼 Career Dashboard, {user?.full_name || user?.email?.split('@')[0] || 'Seeker'}
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Your career cockpit — Skills, Applications, Interviews
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
        <StatCard icon={<Briefcase />} label="Applications" value="12" color="blue" />
        <StatCard icon={<Calendar />} label="Interviews" value="3" color="green" />
        <StatCard icon={<Award />} label="Offers" value="1" color="orange" />
        <StatCard icon={<UserCheck />} label="Profile Score" value="78%" color="purple" />
      </div>

      {/* Recent Applications */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
        <h3 className="font-semibold text-gray-700 mb-4">📋 Recent Applications</h3>
        {loading ? (
          <p className="text-gray-400">Loading...</p>
        ) : apps.length === 0 ? (
          <p className="text-gray-400">No applications yet.</p>
        ) : (
          <ul className="divide-y">
            {apps.slice(0, 5).map((app, i) => (
              <li key={i} className="py-3 flex justify-between items-center">
                <span className="text-sm text-slate-700">
                  {app.job_title || app.title || 'Application'}
                </span>
                <span className="px-3 py-1 rounded-full text-xs font-semibold bg-blue-100 text-blue-700">
                  {app.status || 'Pending'}
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