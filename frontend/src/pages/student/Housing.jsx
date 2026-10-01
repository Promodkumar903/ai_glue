import { useEffect, useState } from 'react';
import { Home, MapPin, DollarSign, Search } from 'lucide-react';
import axios from '../../utils/axios';
import Hero from '../../components/Hero';

export default function StudentHousing() {
  const [listings, setListings] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get('/housing/my').catch(() => ({ data: [] }))
      .then(res => setListings(Array.isArray(res.data) ? res.data : []))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="p-6">
      <Hero
        title="🏠 Housing & Accommodation"
        subtitle="Find verified stays near your campus"
        imageUrl="https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=1600&q=80"
      />

      {loading ? (
        <div className="text-center py-12 text-slate-400">Loading...</div>
      ) : listings.length === 0 ? (
        <div className="bg-white p-12 rounded-xl shadow-sm text-center">
          <Home className="w-14 h-14 text-slate-300 mx-auto mb-3" />
          <p className="text-slate-500">No housing listings yet</p>
          <p className="text-sm text-slate-400 mt-1">Listings will appear here once added by agents</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {listings.map((h, i) => (
            <div key={i} className="bg-white rounded-xl shadow-sm border overflow-hidden hover:shadow-md transition">
              <img
                src={`https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=400&q=80`}
                alt="Housing"
                className="w-full h-40 object-cover"
              />
              <div className="p-4">
                <h3 className="font-semibold text-slate-800">{h.title || 'Apartment'}</h3>
                <p className="text-sm text-slate-500 flex items-center gap-1 mt-1">
                  <MapPin className="w-3 h-3" /> {h.city || 'Unknown'}
                </p>
                <p className="text-lg font-bold text-blue-600 mt-2">${h.rent || '0'}/mo</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}