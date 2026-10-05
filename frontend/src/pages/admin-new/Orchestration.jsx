import React, { useState, useEffect } from 'react';
import { PageHeader, Card, Badge, Button, Input, Dropdown, Alert } from '../../components/ui/Components';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const ENTITY_TYPES = [
  { value: 'jobs', label: '💼 Jobs' },
  { value: 'students', label: '🎓 Student Candidates' },
  { value: 'education_agents', label: '🎓 Education Agents' },
  { value: 'job_agents', label: '💼 Job Recruitment Agents' },
  { value: 'education_brokers', label: '🎓 Education Brokers' },
  { value: 'job_brokers', label: '💼 Job Brokers' },
  { value: 'vendor_agents', label: '🏪 Vendor Agents' },
  { value: 'visa_agents', label: '🛂 Visa Agents' },
  { value: 'companies', label: '🏢 Companies' },
  { value: 'vendors', label: '🏪 Vendors' },
  { value: 'colleges', label: '🎓 Colleges' },
];

const COUNTRIES = [
  { value: '', label: '🌍 Worldwide' },
  { value: 'Germany', label: '🇩🇪 Germany' },
  { value: 'India', label: '🇮🇳 India' },
  { value: 'USA', label: '🇺🇸 USA' },
  { value: 'UK', label: '🇬🇧 UK' },
  { value: 'Canada', label: '🇨🇦 Canada' },
  { value: 'UAE', label: '🇦🇪 UAE' },
  { value: 'Oman', label: '🇴🇲 Oman' },
  { value: 'Singapore', label: '🇸🇬 Singapore' },
];

export default function Orchestration() {
  const [entityType, setEntityType] = useState('jobs');
  const [country, setCountry] = useState('');
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [history, setHistory] = useState([]);

  const fetchHistory = async () => {
    try {
      const res = await fetch(`${API_BASE}/orchestration/history?limit=20`);
      const data = await res.json();
      setHistory(data.history || []);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const handleRun = async () => {
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const res = await fetch(`${API_BASE}/orchestration/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          entity_type: entityType,
          country: country,
          query: query,
          limit: 10,
          auto_notify: true,
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Orchestration failed');
      setResult(data);
      fetchHistory();
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6">
      <PageHeader
        icon="🤖"
        title="AI Orchestration"
        subtitle="Discover, verify, and connect entities from anywhere"
        image="https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=1600&q=80"
      />

      {error && <Alert type="danger" onClose={() => setError('')}>{error}</Alert>}

      <div className="bg-gradient-to-r from-purple-50 to-indigo-50 rounded-xl shadow p-5 mb-6 border border-purple-200">
        <div className="flex items-center gap-2 mb-4">
          <span className="text-2xl">🤖</span>
          <div>
            <h3 className="font-bold text-gray-800">Master Orchestrator</h3>
            <p className="text-xs text-gray-600">
              AI will search, verify, and add entities automatically
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <Dropdown
            label="What to find?"
            value={entityType}
            onChange={setEntityType}
            options={ENTITY_TYPES}
          />
          <Dropdown
            label="Where?"
            value={country}
            onChange={setCountry}
            options={COUNTRIES}
          />
          <Input
            label="Search query (optional)"
            value={query}
            onChange={setQuery}
            placeholder="e.g. software engineers, hotels..."
          />
        </div>

        <div className="mt-3">
          <Button onClick={handleRun} loading={loading} fullWidth>
            🚀 Run Orchestration
          </Button>
        </div>
      </div>

      {result && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <Card title="Found" value={result.found?.length || 0} icon="🔍" color="blue" />
          <Card title="Verified" value={result.verified?.length || 0} icon="✅" color="green" />
          <Card title="Notified" value={result.notified?.length || 0} icon="🔔" color="purple" />
          <Card title="Errors" value={result.errors?.length || 0} icon="❌" color="red" />
        </div>
      )}

      {result?.ai_note && (
        <div className="mb-6 p-4 bg-purple-50 border border-purple-200 rounded-lg text-sm text-purple-800">
          <strong>🤖 AI Insights:</strong> {result.ai_note}
        </div>
      )}

      {result?.found?.length > 0 && (
        <div className="bg-white rounded-xl shadow mb-6">
          <h3 className="font-bold p-4 border-b">🎯 Discovered ({result.found.length})</h3>
          <div className="divide-y">
            {result.found.map((e, i) => (
              <div key={i} className="p-4 hover:bg-gray-50">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h4 className="font-semibold text-gray-800">{e.name}</h4>
                      {e.verified ? (
                        <Badge color="green">✅ Verified</Badge>
                      ) : (
                        <Badge color="yellow">⚠️ Unverified</Badge>
                      )}
                    </div>
                    <p className="text-xs text-gray-500">📍 {e.location}</p>
                    {e.website && (
                      <a
                        href={e.website}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs text-blue-600 hover:underline"
                      >
                        🌐 {e.website}
                      </a>
                    )}
                    {e.description && (
                      <p className="text-sm text-gray-600 mt-1">{e.description}</p>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="bg-white rounded-xl shadow">
        <div className="flex justify-between items-center p-4 border-b">
          <h3 className="font-bold">📜 Recent Orchestration History</h3>
          <button
            onClick={fetchHistory}
            className="text-xs bg-gray-100 hover:bg-gray-200 px-3 py-1.5 rounded font-medium"
          >
            🔄 Refresh
          </button>
        </div>
        {history.length === 0 ? (
          <div className="text-center py-8 text-gray-400">No runs yet</div>
        ) : (
          <div className="divide-y">
            {history.map((h, i) => (
              <div key={i} className="p-3 flex justify-between items-center text-sm">
                <div>
                  <Badge color="purple">{h.type}</Badge>
                  <span className="ml-2 font-medium">{h.name}</span>
                  {h.country && <span className="ml-2 text-gray-500">— {h.country}</span>}
                </div>
                <span className="text-xs text-gray-400">
                  {new Date(h.created_at).toLocaleString()}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}