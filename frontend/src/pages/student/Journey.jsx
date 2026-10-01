import { useEffect, useState } from 'react';
import { Sparkles, CheckCircle, Clock } from 'lucide-react';
import axios from '../../utils/axios';
import Hero from '../../components/Hero';

export default function StudentJourney() {
  const [journey, setJourney] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get('/journey/me').catch(() => ({ data: null }))
      .then(res => setJourney(res.data))
      .finally(() => setLoading(false));
  }, []);

  const stages = [
    { key: 'DISCOVERY', label: 'Discovery', desc: 'Exploring universities' },
    { key: 'APPLIED', label: 'Applied', desc: 'Applications submitted' },
    { key: 'OFFER', label: 'Offer Received', desc: 'Admission letter' },
    { key: 'VISA', label: 'Visa Processing', desc: 'Documents & appointment' },
    { key: 'ENROLLED', label: 'Enrolled', desc: 'Course started' },
  ];

  const currentStage = journey?.state || 'DISCOVERY';
  const currentIdx = stages.findIndex(s => s.key === currentStage);

  return (
    <div className="p-6">
      <Hero
        title="🗺️ My Journey"
        subtitle="Track your study abroad journey"
        imageUrl="https://images.unsplash.com/photo-1523050854058-8df90110c9f1?w=1600&q=80"
      />

      {loading ? (
        <div className="text-center py-12 text-slate-400">Loading...</div>
      ) : (
        <div className="bg-white p-8 rounded-xl shadow-sm border">
          <div className="flex items-center justify-between">
            {stages.map((stage, idx) => {
              const isDone = idx <= currentIdx;
              const isCurrent = idx === currentIdx;
              return (
                <div key={stage.key} className="flex-1 flex flex-col items-center relative">
                  <div className={`w-12 h-12 rounded-full flex items-center justify-center mb-3 ${
                    isDone ? 'bg-blue-600 text-white' : 'bg-slate-200 text-slate-400'
                  } ${isCurrent ? 'ring-4 ring-blue-200' : ''}`}>
                    {isDone ? <CheckCircle className="w-6 h-6" /> : <Clock className="w-6 h-6" />}
                  </div>
                  <p className={`text-sm font-semibold ${isDone ? 'text-blue-700' : 'text-slate-500'}`}>
                    {stage.label}
                  </p>
                  <p className="text-xs text-slate-400 text-center mt-1">{stage.desc}</p>
                  {idx < stages.length - 1 && (
                    <div className={`absolute top-6 left-1/2 w-full h-1 ${isDone ? 'bg-blue-500' : 'bg-slate-200'}`} style={{ zIndex: -1 }} />
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}