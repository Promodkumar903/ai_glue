import React, { useState, useEffect } from 'react';
import { PageHeader, Card, Badge, Button, Input, Dropdown, Alert } from '../../components/ui/Components';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const TYPES = [
  { value: 'all', label: '🔍 All' },
  { value: 'user', label: '👤 Users' },
  { value: 'agent', label: '🤝 Agents' },
  { value: 'broker', label: '🏢 Brokers' },
  { value: 'student', label: '🎓 Students' },
  { value: 'job_seeker', label: '💼 Job Seekers' },
  { value: 'employer', label: '🏛️ Employers' },
  { value: 'admin', label: '⚙️ Admins' },
  { value: 'organization', label: '🏢 Organizations' },
  { value: 'job', label: '💼 Jobs' },
  { value: 'opportunity', label: '📋 Opportunities' },
];

export default function AdminSearch() {
  const [query, setQuery] = useState('');
  const [type, setType] = useState('all');
  const [country, setCountry] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [total, setTotal] = useState(0);
  const [pageSize, setPageSize] = useState(10);
  const [currentPage, setCurrentPage] = useState(1);

  const search = async () => {
    setLoading(true);
    setError('');
    try {
      const params = new URLSearchParams({
        q: query,
        type: type,
        country: country,
        limit: pageSize,
        offset: (currentPage - 1) * pageSize,
      });
      const res = await fetch(`${API_BASE}/admin/search?${params}`);
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Search failed');
      setResults(data.results || []);
      setTotal(data.total || 0);
    } catch (e) {
      setError(e.message);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    search();
  }, [type, country, pageSize, currentPage]);

  const totalPages = Math.ceil(total / pageSize);

  const handleReset = () => {
    setQuery('');
    setType('all');
    setCountry('');
    setCurrentPage(1);
    setResults([]);
    setTotal(0);
  };

  return (
    <div className="p-6">
      <PageHeader
        icon="🔍"
        title="Universal Search"
        subtitle="Search across users, agents, brokers, students, jobs, and organizations"
        image="https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=1600&q=80"
      />

      {error && <Alert type="danger" onClose={() => setError('')}>{error}</Alert>}

      {/* Search Bar */}
      <div className="bg-white rounded-xl shadow p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
          <div className="md:col-span-2">
            <Input
              label="Search Query"
              value={query}
              onChange={setQuery}
              placeholder="Name, email, phone, company..."
            />
          </div>
          <Dropdown
            label="Type"
            value={type}
            onChange={(v) => { setType(v); setCurrentPage(1); }}
            options={TYPES}
            placeholder="All Types"
          />
          <Dropdown
            label="Country"
            value={country}
            onChange={(v) => { setCountry(v); setCurrentPage(1); }}
            options={[
              { value: 'India', label: 'India' },
              { value: 'Germany', label: 'Germany' },
              { value: 'USA', label: 'USA' },
              { value: 'UK', label: 'UK' },
              { value: 'Canada', label: 'Canada' },
              { value: 'UAE', label: 'UAE' },
            ]}
            placeholder="All Countries"
          />
        </div>

        <div className="flex gap-2 mt-3">
          <Button onClick={() => { setCurrentPage(1); search(); }} loading={loading} fullWidth>
            🔍 Search
          </Button>
          <Button onClick={handleReset} variant="ghost">🔄 Reset</Button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <Card title="Total Results" value={total} icon="📊" color="blue" />
        <Card title="Current Page" value={`${currentPage}/${totalPages || 1}`} icon="📄" color="purple" />
        <Card title="Page Size" value={pageSize} icon="📋" color="indigo" />
        <Card title="Showing" value={results.length} icon="✅" color="green" />
      </div>

      {/* Results */}
      <div className="bg-white rounded-xl shadow">
        <div className="flex justify-between items-center p-4 border-b">
          <h3 className="font-bold">Results ({total})</h3>
          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-500">Show:</span>
            <select
              value={pageSize}
              onChange={(e) => { setPageSize(Number(e.target.value)); setCurrentPage(1); }}
              className="border rounded-lg px-2 py-1 text-sm"
            >
              <option value={10}>10</option>
              <option value={25}>25</option>
              <option value={50}>50</option>
              <option value={100}>100</option>
            </select>
          </div>
        </div>

        {loading ? (
          <div className="text-center py-12 text-gray-400">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mb-3"></div>
            <p>Searching...</p>
          </div>
        ) : results.length === 0 ? (
          <div className="text-center py-12 text-gray-400">
            {query ? 'No results found' : 'Enter a search query above'}
          </div>
        ) : (
          <div className="divide-y">
            {results.map((r, i) => (
              <div key={i} className="p-4 hover:bg-gray-50 transition">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <Badge color={
                        r.entity_type === 'user' ? 'blue' :
                        r.entity_type === 'organization' ? 'purple' :
                        'green'
                      }>
                        {r.entity_type}
                      </Badge>
                      {r.role && <Badge color="indigo">{r.role}</Badge>}
                    </div>
                    <h4 className="font-semibold text-gray-800">{r.title}</h4>
                    {r.subtitle && <p className="text-sm text-gray-600">{r.subtitle}</p>}
                    {r.meta && <p className="text-xs text-gray-400 mt-1">{r.meta}</p>}
                  </div>
                  <div className="text-xs font-mono text-gray-400">
                    {r.id?.slice(0, 8)}...
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Pagination */}
        {total > pageSize && (
          <div className="flex justify-between items-center p-4 border-t">
            <button
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className="px-3 py-1.5 text-sm bg-gray-100 hover:bg-gray-200 rounded disabled:opacity-50"
            >
              ← Previous
            </button>
            <div className="text-sm text-gray-600">
              Page {currentPage} of {totalPages}
            </div>
            <button
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
              className="px-3 py-1.5 text-sm bg-gray-100 hover:bg-gray-200 rounded disabled:opacity-50"
            >
              Next →
            </button>
          </div>
        )}
      </div>
    </div>
  );
}