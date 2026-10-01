import { useEffect, useState } from 'react';
import { Shield, Calendar, MapPin, CheckCircle, Clock, AlertCircle } from 'lucide-react';
import axios from '../../utils/axios';
import Hero from '../../components/Hero';

export default function StudentVisa() {
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get('/visa/cases').catch(() => ({ data: [] }))
      .then(res => setCases(Array.isArray(res.data) ? res.data : []))
      .finally(() => setLoading(false));
  }, []);

  const getStageIndex = (status) => {
    const stages = ['NOT_STARTED', 'DOCUMENTS_PENDING', 'APPLIED', 'INTERVIEW', 'APPROVED'];
    return stages.indexOf(status);
  };

  const stages = ['Start', 'Documents', 'Applied', 'Interview', 'Approved'];

  return (
    <div className="p-6">
      <Hero
        title="🛂 Visa Status"
        subtitle="Track your visa application progress"
        imageUrl="https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=1600&q=80"
      />

      {loading ? (
        <div className="text-center py-12 text-slate-400">Loading...</div>
      ) : cases.length === 0 ? (
        <div className="bg-white p-12 rounded-xl shadow-sm text-center">
          <Shield className="w-14 h-14 text-slate-300 mx-auto mb-3" />
          <p className="text-slate-500">No visa cases found</p>
        </div>
      ) : (
        cases.map((c, i) => (
          <div key={i} className="bg-white p-6 rounded-xl shadow-sm border mb-4">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="font-bold text-lg text-slate-800">{c.country} - {c.visa_type}</h3>
                <p className="text-sm text-slate-500">Case ID: {c.id?.slice(0, 8)}</p>
              </div>
              <span className="px-3 py-1 bg-blue-100 text-blue-700 text-xs font-semibold rounded-full">
                {c.status}
              </span>
            </div>

            {/* Timeline */}
            <div className="flex items-center justify-between">
              {stages.map((stage, idx) => {
                const currentIdx = getStageIndex(c.status);
                const isDone = idx <= currentIdx;
                return (
                  <div key={stage} className="flex-1 flex items-center">
                    <div className="flex flex-col items-center">
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                        isDone ? 'bg-blue-600 text-white' : 'bg-slate-200 text-slate-400'
                      }`}>
                        {isDone ? <CheckCircle className="w-4 h-4" /> : idx + 1}
                      </div>
                      <span className="text-xs text-slate-500 mt-1">{stage}</span>
                    </div>
                    {idx < stages.length - 1 && (
                      <div className={`flex-1 h-1 mx-1 ${isDone ? 'bg-blue-600' : 'bg-slate-200'}`} />
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        ))
      )}
    </div>
  );
}
