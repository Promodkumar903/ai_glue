import React, { useState, useEffect } from 'react';
import { PageHeader, Card, DataTable, Badge, Button, Alert, Input, Modal, Dropdown } from '../../components/ui/Components';
import { housingAPI } from '../../services/api';
import { useDebounce } from '../../hooks/useFetch';

const safeArr = (v) => {
  if (Array.isArray(v)) return v;
  if (v && typeof v === 'object') {
    if (Array.isArray(v.items)) return v.items;
    if (Array.isArray(v.data)) return v.data;
  }
  return [];
};
const safeStr = (v, fb = '—') => (v == null || v === '') ? fb : String(v);

export default function Accommodation() {
  const [listings, setListings] = useState([]);
  const [myHousing, setMyHousing] = useState([]);
  const [loading, setLoading] = useState(true);
  const [city, setCity] = useState('');
  const [maxRent, setMaxRent] = useState('');
  const [msg, setMsg] = useState(null);
  const [selected, setSelected] = useState(null);
  const debouncedCity = useDebounce(city, 500);

  const load = () => {
    setLoading(true);
    const params = {};
    if (debouncedCity) params.city = debouncedCity;
    if (maxRent) params.max_rent = maxRent;
    Promise.allSettled([housingAPI.search(params), housingAPI.my()])
      .then(([s, m]) => {
        if (s.status === 'fulfilled') setListings(safeArr(s.value.data));
        if (m.status === 'fulfilled') setMyHousing(safeArr(m.value.data));
        setLoading(false);
      });
  };

  useEffect(() => { load(); }, [debouncedCity, maxRent]);

  const handleRequest = async (housing) => {
    try {
      await housingAPI.updateStatus(housing.id, { status: 'requested' });
      setMsg({ type: 'success', text: '✅ Request sent to owner!' });
      setSelected(null);
      load();
    } catch (e) {
      setMsg({ type: 'danger', text: '❌ ' + (e.response?.data?.detail || e.message) });
    }
  };

  const avgRent = listings.length ? Math.round(listings.reduce((s, l) => s + Number(l.rent || 0), 0) / listings.length) : 0;
  const cities = [...new Set(listings.map((l) => l.city).filter(Boolean))];

  return (
    <div className="p-6">
      <PageHeader
        icon="🏠"
        title="Accommodation"
        subtitle="Find housing near your workplace — verified listings"
        image="https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=1600&q=80"
      />

      {msg && <Alert type={msg.type} onClose={() => setMsg(null)}>{msg.text}</Alert>}

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <Card title="Available" value={listings.length} icon="🏠" color="blue" />
        <Card title="My Requests" value={myHousing.length} icon="📋" color="purple" />
        <Card title="Cities" value={cities.length} icon="🌍" color="indigo" />
        <Card title="Avg Rent" value={`$${avgRent}`} icon="💰" color="green" />
      </div>

      <div className="bg-white rounded-xl shadow p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <Input label="City" value={city} onChange={setCity} placeholder="Search city..." />
          <Input label="Max Rent ($)" type="number" value={maxRent} onChange={setMaxRent} placeholder="e.g. 1000" />
          <div className="flex items-end">
            <Button variant="ghost" fullWidth onClick={() => { setCity(''); setMaxRent(''); }}>Clear Filters</Button>
          </div>
        </div>
      </div>

      {myHousing.length > 0 && (
        <>
          <h3 className="text-lg font-bold mb-3">📋 My Housing Requests</h3>
          <DataTable
            columns={[
              { key: 'title', label: 'Property', render: (r) => safeStr(r.title || r.property_name) },
              { key: 'city', label: 'City', render: (r) => safeStr(r.city) },
              { key: 'rent', label: 'Rent', render: (r) => `$${Number(r.rent || 0).toLocaleString()}` },
              { key: 'status', label: 'Status', render: (r) => <Badge color={r.status === 'approved' ? 'green' : 'yellow'}>{safeStr(r.status, 'pending')}</Badge> },
            ]}
            data={myHousing}
          />
        </>
      )}

      <h3 className="text-lg font-bold mt-6 mb-3">🏠 Available Listings ({listings.length})</h3>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {loading && <p className="col-span-3 text-center py-8 text-gray-500">⏳ Loading...</p>}
        {!loading && listings.length === 0 && (
          <div className="col-span-3 text-center py-12 text-gray-400">
            <p className="text-4xl mb-2">🏚️</p>
            <p>Koi listing nahi mili — filter change karo</p>
          </div>
        )}
        {!loading && listings.map((h, i) => (
          <div key={h.id ?? i} className="bg-white rounded-xl shadow p-4 hover:shadow-lg transition">
            <div className="h-32 bg-gradient-to-br from-blue-100 to-indigo-100 rounded-lg flex items-center justify-center mb-3">
              <span className="text-5xl">🏠</span>
            </div>
            <h4 className="font-bold text-gray-800">{safeStr(h.title || h.property_name, 'Property')}</h4>
            <p className="text-sm text-gray-500 mb-2">{safeStr(h.city)} {h.address && `· ${h.address}`}</p>
            <div className="flex justify-between items-center mb-3">
              <span className="text-lg font-bold text-emerald-600">${Number(h.rent || 0).toLocaleString()}<span className="text-xs text-gray-400">/mo</span></span>
              <Badge color={h.status === 'available' ? 'green' : 'gray'}>{safeStr(h.status, 'available')}</Badge>
            </div>
            <Button fullWidth onClick={() => setSelected(h)}>📩 Request This</Button>
          </div>
        ))}
      </div>

      <Modal open={!!selected} onClose={() => setSelected(null)} title="Request Accommodation">
        {selected && (
          <>
            <div className="bg-gray-50 rounded-lg p-4 mb-4">
              <h4 className="font-bold">{safeStr(selected.title || selected.property_name)}</h4>
              <p className="text-sm text-gray-600">{safeStr(selected.city)}</p>
              <p className="text-lg font-bold text-emerald-600 mt-2">${Number(selected.rent || 0).toLocaleString()}/month</p>
            </div>
            <p className="text-sm text-gray-600 mb-3">Send a request to the owner? They will contact you via platform messages.</p>
            <div className="flex gap-2">
              <Button onClick={() => handleRequest(selected)} fullWidth>📩 Send Request</Button>
              <Button variant="ghost" onClick={() => setSelected(null)}>Cancel</Button>
            </div>
          </>
        )}
      </Modal>
    </div>
  );
}