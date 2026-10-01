import { useState, useEffect } from 'react';
import { useAuth } from '../lib/auth-context';
import { Link } from 'react-router-dom';
import axios from '../utils/axios';

export default function StudentDashboard() {
  const { user, logout } = useAuth();
  const [profile, setProfile] = useState(null);

  useEffect(() => {
    axios.get('/profile/me')
      .then(res => setProfile(res.data))
      .catch(() => {});
  }, []);

  const name = user?.full_name || user?.email?.split('@')[0] || 'Student';

  return (
    <div className="min-h-screen bg-slate-50 p-6">
      {/* Header with Logout */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">
            🎓 Welcome back, {name}
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            India → Germany → TUM &nbsp;|&nbsp; Progress: 65%
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
          <div className="flex justify-between items-center border-b pb-2">
            <p className="text-sm text-slate-700">🔴 Your residence permit expires in 42 days.</p>
            <button className="text-blue-600 hover:text-blue-800 text-sm font-medium">Renew Now →</button>
          </div>
          <div className="flex justify-between items-center border-b pb-2">
            <p className="text-sm text-slate-700">🟡 New housing available near TUM campus</p>
            <button className="text-blue-600 hover:text-blue-800 text-sm font-medium">View →</button>
          </div>
          <div className="flex justify-between items-center">
            <p className="text-sm text-slate-700">🟢 Data Science 101 book required next semester</p>
            <button className="text-blue-600 hover:text-blue-800 text-sm font-medium">Buy →</button>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <StatCard title="Housing" value="2 Available" color="blue" link="/student/housing" />
        <StatCard title="Part Time Jobs" value="12 Matches" color="green" link="/student/jobs" />
        <StatCard title="Documents" value="5/8 Uploaded" color="yellow" link="/student/documents" />
        <StatCard title="Visa Status" value="In Progress" color="purple" link="/student/visa" />
      </div>
    </div>
  );
}

const StatCard = ({ title, value, color, link }) => {
  const colors = {
    blue: 'bg-blue-50 text-blue-700 border-blue-200',
    green: 'bg-green-50 text-green-700 border-green-200',
    yellow: 'bg-yellow-50 text-yellow-700 border-yellow-200',
    purple: 'bg-purple-50 text-purple-700 border-purple-200',
  };
  return (
    <Link to={link} className={`block p-6 rounded-xl border ${colors[color]} hover:shadow-lg transition`}>
      <p className="text-sm font-medium">{title}</p>
      <p className="text-2xl font-bold mt-2">{value}</p>
    </Link>
  );
};