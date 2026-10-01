import { useEffect, useState } from 'react';
import { FileText, Calendar } from 'lucide-react';
import axios from '../../utils/axios';
import Hero from '../../components/Hero';

export default function JobSeekerApplications() {
  const [apps, setApps] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get('/applications').catch(() => ({ data: [] }))
      .then(res => setApps(Array.isArray(res.data) ? res.data : []))
      .finally(() => setLoading(false));
  }, []);

  const getStatusStyle = (status) => ({
    'DRAFT': 'bg-gray-100 text-gray-700',
    'SUBMITTED': 'bg-blue-100 text-blue-700',
    'SHORTLISTED': 'bg-green-100 text-green-700',
    'INTERVIEW': 'bg-yellow-100 text-yellow-700',
    'OFFERED': 'bg-purple-100 text-purple-700',
    'JOINED': 'bg-emerald-100 text-emerald-700',
    'REJECTED': 'bg-red-100 text-red-700',
  }[status] || 'bg-gray-100 text-gray-700');

  return (
    <div className="p-6">
      <Hero
        title="📋 My Applications"
        subtitle={`${apps.length} applications submitted`}
        imageUrl="https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=1600&q=80"
      />

      {loading ? (
        <div className="text-center py-12 text-slate-400">Loading...</div>
      ) : apps.length === 0 ? (
        <div className="bg-white p-12 rounded-xl shadow-sm text-center">
          <FileText className="w-14 h-14 text-slate-300 mx-auto mb-3" />
          <p className="text-slate-500">No applications yet</p>
        </div>
      ) : (
        <div className="space-y-3">
          {apps.map((app, i) => (
            <div key={i} className="bg-white p-5 rounded-xl shadow-sm border hover:shadow-md transition flex justify-between items-center">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center">
                  <FileText className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="font-bold text-slate-800">Application #{app.id?.slice(0, 8)}</h3>
                  <p className="text-sm text-slate-500 flex items-center gap-2">
                    <Calendar className="w-3 h-3" /> {app.submitted_at || 'Not submitted'}
                  </p>
                </div>
              </div>
              <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusStyle(app.status)}`}>
                {app.status}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}