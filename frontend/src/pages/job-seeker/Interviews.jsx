import { useEffect, useState } from 'react';
import { Video, Calendar, Building2, Clock } from 'lucide-react';
import axios from '../../utils/axios';
import Hero from '../../components/Hero';

export default function JobSeekerInterviews() {
  const [interviews, setInterviews] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get('/applications').catch(() => ({ data: [] }))
      .then(res => {
        const all = Array.isArray(res.data) ? res.data : [];
        setInterviews(all.filter(a => a.status === 'INTERVIEW'));
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="p-6">
      <Hero
        title="🎥 Interviews"
        subtitle="Video interviews scheduled with HR"
        imageUrl="https://images.unsplash.com/photo-1587560699334-cc4ff634909a?w=1600&q=80"
      />

      {loading ? (
        <div className="text-center py-12 text-slate-400">Loading...</div>
      ) : interviews.length === 0 ? (
        <div className="bg-white p-12 rounded-xl shadow-sm text-center">
          <Video className="w-14 h-14 text-slate-300 mx-auto mb-3" />
          <p className="text-slate-500">No interviews scheduled yet</p>
        </div>
      ) : (
        <div className="space-y-4">
          {interviews.map((iv, i) => (
            <div key={i} className="bg-white p-6 rounded-xl shadow-sm border">
              <div className="flex justify-between items-start mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-gradient-to-br from-red-500 to-pink-600 rounded-full flex items-center justify-center">
                    <Building2 className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h3 className="font-bold text-slate-800">Interview #{iv.id?.slice(0, 8)}</h3>
                    <p className="text-sm text-slate-500">TechCorp GmbH</p>
                  </div>
                </div>
                <span className="px-3 py-1 bg-yellow-100 text-yellow-700 text-xs font-semibold rounded-full">
                  SCHEDULED
                </span>
              </div>
              <div className="bg-slate-50 p-4 rounded-lg mb-4 flex items-center justify-between text-sm text-slate-600">
                <span className="flex items-center gap-2"><Calendar className="w-4 h-4" /> 20 Sep 2026</span>
                <span className="flex items-center gap-2"><Clock className="w-4 h-4" /> 10:00 AM</span>
              </div>
              <button className="w-full bg-gradient-to-r from-blue-600 to-red-600 hover:brightness-110 text-white py-3 rounded-lg font-semibold shadow-lg flex items-center justify-center gap-2">
                <Video className="w-5 h-5" /> Join Video Interview
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}