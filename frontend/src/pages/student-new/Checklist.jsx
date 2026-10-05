import React, { useState, useEffect } from 'react';
import { PageHeader, Badge, Alert, Dropdown } from '../../components/ui/Components';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function Checklist() {
  const [countries, setCountries] = useState([]);
  const [selected, setSelected] = useState('');
  const [documents, setDocuments] = useState([]);
  const [checked, setChecked] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [serviceModal, setServiceModal] = useState(null);

  // Load countries
  useEffect(() => {
    fetch(`${API_BASE}/education/documents-list/countries`)
      .then((r) => r.json())
      .then((d) => setCountries(Array.isArray(d) ? d : []))
      .catch(() => setCountries([]));
  }, []);

  // Load documents when country changes
  useEffect(() => {
    if (!selected) return;
    setLoading(true);
    setError('');
    fetch(`${API_BASE}/education/documents/${selected}`)
      .then((r) => r.json())
      .then((d) => setDocuments(Array.isArray(d) ? d : []))
      .catch(() => setError('Failed to load documents'))
      .finally(() => setLoading(false));
  }, [selected]);

  const toggle = (id) => setChecked((prev) => ({ ...prev, [id]: !prev[id] }));
  const total = documents.length;
  const done = Object.values(checked).filter(Boolean).length;
  const pct = total ? Math.round((done / total) * 100) : 0;

  return (
    <div className="p-6">
      <PageHeader
        icon="📋"
        title="Document Checklist"
        subtitle="Country-wise required documents for study abroad"
        image="https://images.unsplash.com/photo-1450101499163-c8848c66ca85?w=1600&q=80"
      />

      {error && <Alert type="danger" onClose={() => setError('')}>{error}</Alert>}

      <div className="bg-white rounded-xl shadow p-6 mb-6">
        <Dropdown
          label="Select Country"
          value={selected}
          onChange={setSelected}
          options={countries.map((c) => ({ value: c, label: c }))}
          placeholder="Choose a country..."
        />

        {total > 0 && (
          <div className="mt-4">
            <div className="flex justify-between text-sm mb-2">
              <span className="font-medium text-gray-700">Progress</span>
              <span className="font-bold text-blue-600">{done}/{total} ({pct}%)</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className="bg-gradient-to-r from-blue-500 to-indigo-600 h-3 rounded-full transition-all"
                style={{ width: `${pct}%` }}
              />
            </div>
          </div>
        )}
      </div>

      {loading ? (
        <div className="text-center py-12 text-gray-400">Loading documents...</div>
      ) : total === 0 ? (
        <div className="bg-white p-12 rounded-xl shadow text-center text-gray-400">
          {selected ? 'No documents found for this country' : 'Select a country to see the checklist'}
        </div>
      ) : (
        <div className="space-y-3">
          {documents.map((d) => (
            <div
              key={d.id}
              className={`bg-white p-5 rounded-xl shadow border-2 transition cursor-pointer ${
                checked[d.id] ? 'border-emerald-400 bg-emerald-50' : 'border-transparent hover:border-blue-300'
              }`}
              onClick={() => toggle(d.id)}
            >
              <div className="flex items-start gap-4">
                <div
                  className={`w-6 h-6 rounded border-2 flex items-center justify-center shrink-0 ${
                    checked[d.id] ? 'bg-emerald-500 border-emerald-500' : 'border-gray-300'
                  }`}
                >
                  {checked[d.id] && <span className="text-white text-sm font-bold">✓</span>}
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 flex-wrap mb-1">
                    <h3 className={`font-bold ${checked[d.id] ? 'text-emerald-700 line-through' : 'text-gray-800'}`}>
                      {d.document_name}
                    </h3>
                    {d.is_mandatory && <Badge color="red">Mandatory</Badge>}
                    {!d.is_mandatory && <Badge color="gray">Optional</Badge>}
                    {d.estimated_days > 0 && <Badge color="blue">~{d.estimated_days} days</Badge>}
                  </div>
                  {d.description && <p className="text-sm text-gray-600">{d.description}</p>}
                  <div className="flex items-center gap-3 mt-1 flex-wrap">
                    {d.official_link && (
                      <a
                        href={d.official_link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs text-blue-600 hover:underline"
                        onClick={(e) => e.stopPropagation()}
                      >
                        🔗 Official Link
                      </a>
                    )}
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setServiceModal({ doc: d.document_name, country: selected });
                      }}
                      className="text-xs text-purple-600 hover:text-purple-700 hover:underline font-medium"
                    >
                      🎯 Find Service Provider
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {serviceModal && (
        <div
          className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4"
          onClick={() => setServiceModal(null)}
        >
          <div
            className="bg-white rounded-xl max-w-2xl w-full max-h-[80vh] overflow-y-auto p-6"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex justify-between items-center mb-4">
              <h3 className="font-bold text-lg">Service Providers — {serviceModal.doc}</h3>
              <button
                onClick={() => setServiceModal(null)}
                className="text-gray-400 hover:text-gray-700 text-2xl leading-none"
              >
                ×
              </button>
            </div>
            <ServiceList doc={serviceModal.doc} country={serviceModal.country} />
          </div>
        </div>
      )}
    </div>
  );
}

function ServiceList({ doc, country }) {
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    fetch(
      `${API_BASE}/education/document-services/${encodeURIComponent(doc)}?country=${encodeURIComponent(country || '')}`
    )
      .then((r) => r.json())
      .then((d) => setServices(Array.isArray(d) ? d : []))
      .catch(() => setServices([]))
      .finally(() => setLoading(false));
  }, [doc, country]);

  if (loading) return <div className="text-center py-8 text-gray-400">Loading services...</div>;
  if (services.length === 0)
    return <div className="text-center py-8 text-gray-400">Koi service provider nahi mila.</div>;

   const hasAI = services.some(s => s.source === 'ai');

  return (
    <div className="space-y-3">
      {hasAI && (
        <div className="p-3 bg-purple-50 border border-purple-200 rounded-lg text-xs text-purple-800 mb-3">
          ✨ <strong>AI-suggested services</strong> — verify karein. Official website pe confirm karo.
        </div>
      )}
      {services.map((s, i) => (
        <div key={i} className="border rounded-lg p-4 hover:shadow-md transition">
          <div className="flex justify-between items-start mb-2">
            <div>
              <h4 className="font-bold text-gray-800">{s.provider_name}</h4>
              <p className="text-xs text-gray-500">{s.service_type} • {s.city}</p>
            </div>
            <div className="text-right">
              <span className="text-yellow-500 font-bold">★ {s.rating}</span>
              {s.verified && (
                <span className="ml-2 text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded">
                  ✓ Verified
                </span>
              )}
            </div>
          </div>
          {s.price_range && <p className="text-sm text-gray-600 mb-2">💰 {s.price_range}</p>}
          <div className="flex gap-2">
            {s.website && (
              <a
                href={s.website}
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs bg-blue-600 text-white px-3 py-1.5 rounded hover:bg-blue-700"
              >
                🌐 Website
              </a>
            )}
            {s.phone && (
              <a
                href={`tel:${s.phone}`}
                className="text-xs bg-gray-100 text-gray-700 px-3 py-1.5 rounded hover:bg-gray-200"
              >
                📞 Call
              </a>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}