import { useEffect, useState } from 'react';
import { Users, CheckCircle, XCircle } from 'lucide-react';
import axios from '../../utils/axios';
import Hero from '../../components/Hero';

export default function EmployerApplicants() {
  const [applicants, setApplicants] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get('/company/applicants/all').catch(() => ({ data: [] }))
      .then(res => setApplicants(Array.isArray(res.data) ? res.data : []))
      .finally(() => setLoading(false));
  }, []);

  const getStatusColor = (status) => ({
    'SHORTLISTED': 'bg-green-100 text-green-700',
    'INTERVIEW': 'bg-blue-100 text-blue-700',
    'OFFERED': 'bg-yellow-100 text-yellow-700',
    'JOINED': 'bg-purple-100 text-purple-700',
    'REJECTED': 'bg-red-100 text-red-700',
  }[status] || 'bg-gray-100 text-gray-700');

  return (
    <div className="p-6">
      <Hero
        title="👥 All Applicants"
        subtitle={`${applicants.length} candidates applied to your vacancies`}
        imageUrl="https://images.unsplash.com/photo-1560250097-0b93528c311a?w=1600&q=80"
      />

      {loading ? (
        <div className="text-center py-12 text-slate-400">Loading...</div>
      ) : applicants.length === 0 ? (
        <div className="bg-white p-12 rounded-xl shadow-sm text-center">
          <Users className="w-14 h-14 text-slate-300 mx-auto mb-3" />
          <p className="text-slate-500">No applicants yet</p>
        </div>
      ) : (
        <div className="space-y-3">
          {applicants.map((a, i) => (
            <div key={i} className="bg-white p-5 rounded-xl shadow-sm border flex items-center justify-between hover:shadow-md transition">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center text-white font-bold">
                  {(a.candidate_id || 'C')[0].toUpperCase()}
                </div>
                <div>
                  <p className="font-semibold text-slate-800">Candidate {a.candidate_id?.slice(0, 6)}</p>
                  <p className="text-xs text-slate-500">Match Score: {a.match_score || 0}%</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusColor(a.status)}`}>
                  {a.status}
                </span>
                <button className="p-2 text-green-600 hover:bg-green-50 rounded-lg"><CheckCircle className="w-5 h-5" /></button>
                <button className="p-2 text-red-600 hover:bg-red-50 rounded-lg"><XCircle className="w-5 h-5" /></button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}