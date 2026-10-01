import React, { useEffect, useState } from 'react';
import { PageHeader } from '../../components/ui/Components';
import api from '../../services/api';

export default function Deals() {
  const [deals, setDeals] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/deals/my/deals')
      .then((r) => setDeals(Array.isArray(r.data) ? r.data : []))
      .catch(() => setDeals([]))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <PageHeader title="Deals" subtitle="Track your job deals and placements"
        image="https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=1600&q=80"
      />
      {loading ? <div className="text-slate-400 py-10 text-center">Loading...</div> : deals.length === 0 ? (
        <div className="text-center py-10 text-slate-400 bg-white rounded-xl border border-slate-200">
          No deals yet
        </div>
      ) : (
        <div className="space-y-3">
          {deals.map((d) => (
            <div key={d.id} className="bg-white p-5 rounded-xl border border-slate-200">
              <p className="font-bold text-slate-800">Deal {d.id?.slice(0, 8)}</p>
              <p className="text-sm text-slate-500 mt-1">Status: {d.status}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
