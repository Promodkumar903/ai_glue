import React, { useState, useEffect, useMemo } from 'react';
import { PageHeader, Card, Badge, Alert } from '../../components/ui/Components';
import { educationAPI, vendorAPI } from '../../services/api';

const safeArr = (v) => {
  if (Array.isArray(v)) return v;
  if (v && typeof v === 'object') {
    if (Array.isArray(v.items)) return v.items;
    if (Array.isArray(v.data)) return v.data;
  }
  return [];
};
const safeStr = (v, fb = '—') => (v == null || v === '') ? fb : String(v);

const FLAGS = { DE: '🇩🇪', US: '🇺🇸', GB: '🇬🇧', CA: '🇨🇦', AU: '🇦🇺', NZ: '🇳🇿', FR: '🇫🇷', IE: '🇮🇪', NL: '🇳🇱', SE: '🇸🇪' };

export default function StudyAbroad() {
  const [countries, setCountries] = useState([]);
  const [universities, setUniversities] = useState([]);
  const [courses, setCourses] = useState([]);
  const [vendors, setVendors] = useState([]);
  const [selectedCountry, setSelectedCountry] = useState(null);
  const [selectedUniv, setSelectedUniv] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    setLoading(true);
    Promise.allSettled([
      educationAPI.countries(),
      educationAPI.universities(),
      educationAPI.courses(),
      vendorAPI.list(),
    ]).then(([c, u, co, v]) => {
      if (c.status === 'fulfilled') setCountries(safeArr(c.value?.data));
      if (u.status === 'fulfilled') setUniversities(safeArr(u.value?.data));
      if (co.status === 'fulfilled') setCourses(safeArr(co.value?.data));
      if (v.status === 'fulfilled') setVendors(safeArr(v.value?.data));
      setLoading(false);
    }).catch(() => {
      setError('Failed to load study data');
      setLoading(false);
    });
  }, []);

  const filteredUnis = useMemo(() => {
    if (!selectedCountry) return universities;
    return universities.filter((u) => u.country_id === selectedCountry.id);
  }, [universities, selectedCountry]);

  const univCourses = useMemo(() => {
    if (!selectedUniv) return [];
    return courses.filter((c) => c.university_id === selectedUniv.id);
  }, [courses, selectedUniv]);

  const univVendors = useMemo(() => {
    // Vendors in the same country (fallback: all)
    if (!selectedCountry) return vendors.slice(0, 6);
    return vendors.slice(0, 6);
  }, [vendors, selectedCountry]);

  const countryName = (id) => countries.find((c) => c.id === id)?.name || '—';
  const countryFlag = (id) => {
    const c = countries.find((x) => x.id === id);
    return FLAGS[c?.iso_code] || '🌍';
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <PageHeader
        icon="🎓"
        title="Study Abroad"
        subtitle="Country → University → Course → Hostel → Vendors → Apply"
        image="https://images.unsplash.com/photo-1523050854058-8df90110c9f1?w=1600&q=80"
      />

      {error && <Alert type="danger" title="Error" onClose={() => setError('')}>{error}</Alert>}

      {/* Step 1: Country Selector */}
      <div className="mb-6">
        <h3 className="text-sm font-semibold text-slate-600 uppercase mb-3">
          Step 1 — Choose Country
        </h3>
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setSelectedCountry(null)}
            className={`px-4 py-2 rounded-lg border transition-all ${
              !selectedCountry
                ? 'bg-blue-600 text-white border-blue-600 shadow-lg'
                : 'bg-white text-slate-700 border-slate-200 hover:border-blue-400'
            }`}
          >
            🌍 All Countries
          </button>
          {countries.map((c) => (
            <button
              key={c.id}
              onClick={() => { setSelectedCountry(c); setSelectedUniv(null); }}
              className={`px-4 py-2 rounded-lg border transition-all ${
                selectedCountry?.id === c.id
                  ? 'bg-blue-600 text-white border-blue-600 shadow-lg'
                  : 'bg-white text-slate-700 border-slate-200 hover:border-blue-400'
              }`}
            >
              {FLAGS[c.iso_code] || '🌍'} {c.name}
            </button>
          ))}
        </div>
      </div>

      {/* Step 2: Universities */}
      <div className="mb-6">
        <h3 className="text-sm font-semibold text-slate-600 uppercase mb-3">
          Step 2 — Choose University ({filteredUnis.length} available)
        </h3>

        {loading ? (
          <div className="text-center py-10 text-slate-400">Loading…</div>
        ) : filteredUnis.length === 0 ? (
          <div className="text-center py-10 text-slate-400 bg-white rounded-xl border border-slate-200">
            No universities found
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredUnis.map((u) => (
              <div
                key={u.id}
                onClick={() => setSelectedUniv(u)}
                className={`p-5 bg-white rounded-xl border-2 cursor-pointer transition-all hover:shadow-lg ${
                  selectedUniv?.id === u.id
                    ? 'border-blue-500 shadow-lg'
                    : 'border-slate-200 hover:border-blue-300'
                }`}
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="text-3xl">{countryFlag(u.country_id)}</div>
                  {u.ranking_global && (
                    <Badge color="blue">Rank #{u.ranking_global}</Badge>
                  )}
                </div>
                <h4 className="font-bold text-slate-800 mb-1 leading-tight">{u.name}</h4>
                <p className="text-sm text-slate-500 mb-3">{countryName(u.country_id)}</p>
                <button className="text-sm text-blue-600 font-medium hover:underline">
                  View details →
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Step 3: Selected University Details */}
      {selectedUniv && (
        <div className="mb-6 grid grid-cols-1 lg:grid-cols-3 gap-4">
          {/* Courses */}
          <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200 p-5">
            <h3 className="font-bold text-slate-800 mb-3">
              📚 Courses at {selectedUniv.name}
            </h3>
            {univCourses.length === 0 ? (
              <p className="text-slate-400 text-sm py-4">No courses listed yet</p>
            ) : (
              <div className="space-y-2">
                {univCourses.map((c) => (
                  <div key={c.id} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                    <div>
                      <p className="font-medium text-slate-800">{safeStr(c.name)}</p>
                      <p className="text-xs text-slate-500">
                        {safeStr(c.degree_type || c.level)} · {safeStr(c.duration_months || c.duration)} months
                      </p>
                    </div>
                    <button className="px-3 py-1.5 bg-blue-600 text-white text-xs rounded-lg hover:bg-blue-700 font-medium">
                      Apply
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Vendors */}
          <div className="bg-white rounded-xl border border-slate-200 p-5">
            <h3 className="font-bold text-slate-800 mb-3">🛒 Nearby Vendors</h3>
            <div className="space-y-2">
              {univVendors.map((v) => (
                <div key={v.id} className="flex items-center gap-3 p-2 hover:bg-slate-50 rounded-lg">
                  <div className="text-2xl">
                    {v.category === 'hotel' ? '🏨' : v.category === 'book' ? '📚' : '🏪'}
                  </div>
                  <div className="min-w-0">
                    <p className="text-sm font-medium text-slate-800 truncate">{safeStr(v.name)}</p>
                    <p className="text-xs text-slate-500">{safeStr(v.location)}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Progress */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-4 border border-blue-200">
        <p className="text-sm text-slate-700">
          <strong>Progress:</strong>{' '}
          {!selectedCountry ? 'Select a country' :
           !selectedUniv ? 'Select a university' :
           'Ready to apply 🎯'}
        </p>
      </div>
    </div>
  );
}