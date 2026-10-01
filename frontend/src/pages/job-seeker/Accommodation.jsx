import { useState } from 'react';
import { MapPin, Search, ShieldCheck } from 'lucide-react';
import Hero from '../../components/Hero';

export default function JobSeekerAccommodation() {
  const [search, setSearch] = useState('');

  const listings = [
    { id: 1, title: 'Single Room - City Center', city: 'Berlin', price: 650, type: 'Apartment', verified: true },
    { id: 2, title: 'Shared Flat - Near Office', city: 'Munich', price: 480, type: 'Shared', verified: true },
    { id: 3, title: 'Studio Apartment', city: 'Frankfurt', price: 850, type: 'Studio', verified: false },
  ];

  const filtered = listings.filter(l =>
    !search || l.title.toLowerCase().includes(search.toLowerCase()) || l.city.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="p-6">
      <Hero
        title="🏨 Work Accommodation"
        subtitle="Verified stays near your workplace"
        imageUrl="https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=1600&q=80"
      />

      <div className="bg-white rounded-xl shadow-sm border p-4 mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search by city..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 border rounded-xl focus:ring-2 focus:ring-emerald-500 outline-none"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {filtered.map(l => (
          <div key={l.id} className="bg-white rounded-xl shadow-sm border overflow-hidden hover:shadow-lg transition">
            <div className="relative">
              <img src="https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=400&q=80" alt={l.title} className="w-full h-40 object-cover" />
              {l.verified && (
                <div className="absolute top-2 right-2 bg-green-500 text-white px-2 py-1 rounded-full text-xs font-semibold flex items-center gap-1">
                  <ShieldCheck className="w-3 h-3" /> Verified
                </div>
              )}
            </div>
            <div className="p-4">
              <h3 className="font-bold text-slate-800">{l.title}</h3>
              <p className="text-sm text-slate-500 flex items-center gap-1 mt-1"><MapPin className="w-3 h-3" /> {l.city}</p>
              <div className="flex justify-between items-center mt-3">
                <p className="text-lg font-bold text-emerald-600">€{l.price}/mo</p>
                <button className="bg-gradient-to-b from-emerald-500 to-teal-600 text-white px-4 py-1.5 rounded-lg text-sm font-semibold">Book</button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}