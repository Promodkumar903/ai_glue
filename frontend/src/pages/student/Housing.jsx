import { useEffect, useState } from 'react';
import { Home, MapPin, Search, Sparkles } from 'lucide-react';
import axios from '../../utils/axios';
import Hero from '../../components/Hero';

const HOUSING_TYPES = [
  { id: 'student_hostel', label: '🏫 Student Hostel / Dorm' },
  { id: 'shared_flat', label: '🏢 Shared Flat (WG)' },
  { id: 'private_apartment', label: '🏡 Private Apartment' },
  { id: 'pg', label: '🛏️ PG / Paying Guest' },
  { id: 'homestay', label: '👨‍👩‍👧 Homestay' },
  { id: 'temporary', label: '🏨 Temporary Stay' },
];

export default function StudentHousing() {
  const [listings, setListings] = useState([]);
  const [loading, setLoading] = useState(true);

  // AI Suggest state
  const [housingType, setHousingType] = useState('student_hostel');
  const [city, setCity] = useState('');
  const [country, setCountry] = useState('Germany');
  const [maxRent, setMaxRent] = useState('');
  const [aiLoading, setAiLoading] = useState(false);
  const [aiResult, setAiResult] = useState(null);
  const [aiError, setAiError] = useState('');

  useEffect(() => {
    axios.get('/housing/my').catch(() => ({ data: [] }))
      .then(res => setListings(Array.isArray(res.data) ? res.data : []))
      .finally(() => setLoading(false));
  }, []);

  const handleAiSuggest = async () => {
    setAiLoading(true);
    setAiError('');
    setAiResult(null);
    try {
      const res = await axios.post('/housing/ai-suggest', {
        city,
        country,
        housing_type: housingType,
        max_rent: parseFloat(maxRent) || 0,
      });
      setAiResult(res.data);
    } catch (err) {
      setAiError(err.response?.data?.detail || 'AI suggestion failed');
    } finally {
      setAiLoading(false);
    }
  };

  return (
    <div className="p-6">
      <Hero
        title="🏠 Housing & Accommodation"
        subtitle="Find verified stays near your campus"
        imageUrl="https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=1600&q=80"
      />

      {/* AI Suggest Box */}
      <div className="bg-gradient-to-r from-blue-50 to-cyan-50 border border-blue-200 rounded-2xl p-6 mb-6">
        <div className="flex items-center gap-3 mb-4">
          <Sparkles className="w-6 h-6 text-blue-600" />
          <h2 className="text-lg font-bold text-slate-800">Find Accommodation</h2>
        </div>
        <p className="text-sm text-slate-600 mb-4">
          Pehle humare <strong>verified partners</strong> se search karenge, phir AI suggestions denge.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
          <select
            value={housingType}
            onChange={(e) => setHousingType(e.target.value)}
            className="p-3 border-2 border-blue-200 rounded-xl bg-white focus:outline-none focus:border-blue-500"
          >
            {HOUSING_TYPES.map((t) => (
              <option key={t.id} value={t.id}>{t.label}</option>
            ))}
          </select>

          <input
            type="text"
            value={city}
            onChange={(e) => setCity(e.target.value)}
            placeholder="City (e.g. Berlin)"
            className="p-3 border-2 border-blue-200 rounded-xl bg-white focus:outline-none focus:border-blue-500"
          />

          <input
            type="text"
            value={country}
            onChange={(e) => setCountry(e.target.value)}
            placeholder="Country"
            className="p-3 border-2 border-blue-200 rounded-xl bg-white focus:outline-none focus:border-blue-500"
          />

          <input
            type="number"
            value={maxRent}
            onChange={(e) => setMaxRent(e.target.value)}
            placeholder="Max rent (optional)"
            className="p-3 border-2 border-blue-200 rounded-xl bg-white focus:outline-none focus:border-blue-500"
          />
        </div>

        <div className="mt-4">
          <button
            onClick={handleAiSuggest}
            disabled={aiLoading}
            className="bg-gradient-to-r from-blue-600 to-cyan-600 text-white px-6 py-3 rounded-xl font-semibold hover:opacity-90 disabled:opacity-50 flex items-center justify-center gap-2"
          >
            <Search className="w-4 h-4" />
            {aiLoading ? 'Searching...' : 'Search Housing'}
          </button>
        </div>

        {aiError && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
            {aiError}
          </div>
        )}

        {/* Results */}
        {aiResult && (
          <div className="mt-6">
            {/* Source badge */}
            <div className="mb-4 flex items-center gap-2">
              {aiResult.source === 'internal' ? (
                <span className="bg-emerald-100 text-emerald-700 px-3 py-1 rounded-full text-xs font-bold">
                  ✅ {aiResult.count} verified partner listings
                </span>
              ) : (
                <span className="bg-amber-100 text-amber-700 px-3 py-1 rounded-full text-xs font-bold">
                  🤖 AI Suggested ({aiResult.count})
                </span>
              )}
            </div>

            {aiResult.ai_note && (
              <p className="text-sm text-slate-600 italic mb-4">💡 {aiResult.ai_note}</p>
            )}

            {aiResult.items?.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {aiResult.items.map((item, i) => (
                  <div key={i} className="bg-white rounded-xl p-4 border border-blue-100 shadow-sm hover:shadow-md transition">
                    <h3 className="font-bold text-slate-800">{item.name || item.title}</h3>
                    <p className="text-sm text-slate-600 mt-1">
                      {item.description || item.address || item.location}
                    </p>
                    <div className="flex items-center justify-between mt-3 flex-wrap gap-2">
                      {(item.rent_range || item.monthly_rent) && (
                        <span className="text-xs bg-emerald-100 text-emerald-700 px-2 py-1 rounded-full font-medium">
                          {item.rent_range || `€${item.monthly_rent}/mo`}
                        </span>
                      )}
                      {item.link && (
                        <a
                          href={item.link}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xs text-blue-600 hover:underline font-medium"
                        >
                          View →
                        </a>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="bg-white p-6 rounded-xl text-center text-slate-500 text-sm">
                No results found. Try different filters.
              </div>
            )}
          </div>
        )}
      </div>

      {/* Existing Listings (from agents) */}
      <div className="mt-8">
        <h2 className="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">
          <Home className="w-5 h-5 text-blue-600" /> Listings from Agents ({listings.length})
        </h2>

        {loading ? (
          <div className="text-center py-12 text-slate-400">Loading...</div>
        ) : listings.length === 0 ? (
          <div className="bg-white p-12 rounded-xl shadow-sm text-center">
            <Home className="w-14 h-14 text-slate-300 mx-auto mb-3" />
            <p className="text-slate-500">No housing listings yet</p>
            <p className="text-sm text-slate-400 mt-1">
              Listings will appear here once added by agents
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {listings.map((h, i) => (
              <div key={i} className="bg-white rounded-xl shadow-sm border overflow-hidden hover:shadow-md transition">
                <img
                  src="https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=400&q=80"
                  alt="Housing"
                  className="w-full h-40 object-cover"
                />
                <div className="p-4">
                  <h3 className="font-semibold text-slate-800">{h.title || 'Apartment'}</h3>
                  <p className="text-sm text-slate-500 flex items-center gap-1 mt-1">
                    <MapPin className="w-3 h-3" /> {h.city || h.location || 'Unknown'}
                  </p>
                  <p className="text-lg font-bold text-blue-600 mt-2">
                    €{h.rent || h.monthly_rent || '0'}/mo
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}