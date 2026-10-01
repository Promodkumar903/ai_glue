import React, { useEffect, useState } from 'react';
import { PageHeader } from '../../components/ui/Components';
import api from '../../services/api';

export default function Education() {
  const [countries, setCountries] = useState([]);
  const [unis, setUnis] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.allSettled([
      api.get('/education/countries'),
      api.get('/education/universities'),
    ]).then(([c, u]) => {
      if (c.status === 'fulfilled') setCountries(Array.isArray(c.value.data) ? c.value.data : []);
      if (u.status === 'fulfilled') setUnis(Array.isArray(u.value.data) ? u.value.data : []);
      setLoading(false);
    });
  }, []);

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <PageHeader title="Education" subtitle="Countries and universities for study abroad"
        image="https://images.unsplash.com/photo-1523050854058-8df90110c9f1?w=1600&q=80"
      />
      {loading ? <div className="text-slate-400 py-10 text-center">Loading...</div> : (
        <>
          <h3 className="font-bold text-slate-700 mb-3">Countries ({countries.length})</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-8">
            {countries.map((c) => (
              <div key={c.id} className="bg-white p-4 rounded-xl border border-slate-200">
                <p className="font-bold text-slate-800">{c.name}</p>
                <p className="text-xs text-slate-500">{c.iso_code}</p>
              </div>
            ))}
          </div>
          <h3 className="font-bold text-slate-700 mb-3">Universities ({unis.length})</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {unis.map((u) => (
              <div key={u.id} className="bg-white p-5 rounded-xl border border-slate-200">
                <p className="font-bold text-slate-800">{u.name}</p>
                {u.ranking_global && <p className="text-xs text-slate-500 mt-1">Rank #{u.ranking_global}</p>}
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
