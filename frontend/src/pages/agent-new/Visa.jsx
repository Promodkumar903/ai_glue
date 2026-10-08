import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { PageHeader, Card, Badge, Alert, Button } from '../../components/ui/Components';
import { crmAPI } from '../../services/api';

const STATUS_TABS = [
  { id: 'all', label: 'All', icon: '📋' },
  { id: 'NOT_STARTED', label: 'Not Started', icon: '⚪' },
  { id: 'DOCS_PENDING', label: 'Docs Pending', icon: '📄' },
  { id: 'APPLIED', label: 'Applied', icon: '📤' },
  { id: 'UNDER_REVIEW', label: 'Under Review', icon: '🔍' },
  { id: 'APPROVED', label: 'Approved', icon: '✅' },
  { id: 'REJECTED', label: 'Rejected', icon: '❌' },
];

const STATUS_COLORS = {
  NOT_STARTED: 'gray',
  DOCS_PENDING: 'orange',
  APPLIED: 'blue',
  UNDER_REVIEW: 'purple',
  APPROVED: 'green',
  REJECTED: 'red',
  EXPIRED: 'red',
};

const TRUST_BADGES = {
  VERIFIED: { color: 'green', icon: '🟢' },
  REPORTED: { color: 'orange', icon: '🟡' },
  UNVERIFIED: { color: 'red', icon: '🔴' },
};

const SORT_OPTIONS = [
  { id: 'recent', label: 'Recent First' },
  { id: 'oldest', label: 'Oldest First' },
  { id: 'days_pending', label: 'Longest Pending' },
  { id: 'name', label: 'Candidate Name' },
];

export default function Visa() {
  const [data, setData] = useState({ cases: [], counts_by_status: {}, upcoming_appointments: [], role: null });
  const [regions, setRegions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState('all');
  const [search, setSearch] = useState('');
  const [regionFilter, setRegionFilter] = useState('');
  const [countryFilter, setCountryFilter] = useState('');
  const [sortBy, setSortBy] = useState('recent');
  const [error, setError] = useState('');
  const [showFilters, setShowFilters] = useState(false);

  const load = () => {
    setLoading(true);
    const params = {};
    if (tab !== 'all') params.status = tab;
    if (regionFilter) params.region = regionFilter;
    if (countryFilter) params.country = countryFilter;
    if (search) params.search = search;
    if (sortBy) params.sort = sortBy;

    crmAPI.getVisaCases(params)
      .then((r) => setData(r.data || {}))
      .catch((e) => setError(e.response?.data?.detail || 'Failed to load visa cases'))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    crmAPI.getRegions()
      .then((r) => setRegions(r.data?.regions || []))
      .catch(() => setRegions([]));
  }, []);

  useEffect(() => {
    const t = setTimeout(load, 300);
    return () => clearTimeout(t);
    // eslint-disable-next-line
  }, [tab, regionFilter, countryFilter, search, sortBy]);

  const cases = data.cases || [];
  const counts = data.counts_by_status || {};
  const appts = data.upcoming_appointments || [];
  const total = Object.values(counts).reduce((a, b) => a + b, 0);

  // Selected region's countries for dropdown
  const selectedRegion = regions.find((r) => r.code === regionFilter);
  const regionCountries = selectedRegion?.countries || [];

  const clearFilters = () => {
    setSearch('');
    setRegionFilter('');
    setCountryFilter('');
    setSortBy('recent');
    setTab('all');
  };

  const hasFilters = search || regionFilter || countryFilter || sortBy !== 'recent' || tab !== 'all';

  return (
    <div className="p-6">
      <div className="flex justify-between items-start flex-wrap gap-3">
        <PageHeader
          icon="🛂"
          title={
            data.role === 'STUDENT' ? 'My Student Visa' :
            data.role === 'JOB_SEEKER' ? 'My Work Visa' :
            data.role === 'AGENT' ? 'Visa Tracking' :
            data.role === 'ADMIN' ? 'Platform Visa Cases' :
            'Visa Tracking'
          }
          subtitle={
            data.role === 'AGENT' ? 'All candidates visa' :
            data.role === 'ADMIN' ? 'All visa cases on platform' :
            'Track your visa application'
          }
        />
        <Link to="/agent/leads">
          <Button>➕ New Visa Case</Button>
        </Link>
      </div>

      {error && <div className="mb-3"><Alert type="danger" onClose={() => setError('')}>{error}</Alert></div>}

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
        <Card title="Total" value={total} icon="🛂" color="blue" />
        <Card title="Docs Pending" value={counts.DOCS_PENDING || 0} icon="📄" color="orange" />
        <Card title="Applied" value={counts.APPLIED || 0} icon="📤" color="purple" />
        <Card title="Approved" value={counts.APPROVED || 0} icon="✅" color="green" />
        <Card title="Rejected" value={counts.REJECTED || 0} icon="❌" color="red" />
      </div>

      {/* Upcoming Appointments */}
      {appts.length > 0 && (
        <div className="mb-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="font-semibold text-blue-900 mb-2">📅 Upcoming Appointments ({appts.length})</h3>
          <div className="space-y-2">
            {appts.slice(0, 5).map((a) => (
              <div key={a.id} className="flex justify-between items-center bg-white rounded px-3 py-2 text-sm">
                <span><strong>{a.candidate_name}</strong> — {a.country}</span>
                <span className="text-blue-700">
                  {a.scheduled_at ? new Date(a.scheduled_at).toLocaleString() : '—'}
                  {a.location && ` • ${a.location}`}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Search + Filter Bar */}
      <div className="bg-white rounded-lg border p-4 mb-4">
        <div className="flex gap-2 flex-wrap">
          {/* Search */}
          <div className="flex-1 min-w-[250px] relative">
            <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">🔍</span>
            <input
              type="text"
              placeholder="Search by candidate name, email, country..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-3 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Region dropdown */}
          <select
            value={regionFilter}
            onChange={(e) => { setRegionFilter(e.target.value); setCountryFilter(''); }}
            className="border rounded-lg px-3 py-2 text-sm bg-white"
          >
            <option value="">🌍 All Regions</option>
            {regions.map((r) => (
              <option key={r.code} value={r.code}>{r.label}</option>
            ))}
          </select>

          {/* Country dropdown (only if region selected) */}
          {regionFilter && regionCountries.length > 0 && (
            <select
              value={countryFilter}
              onChange={(e) => setCountryFilter(e.target.value)}
              className="border rounded-lg px-3 py-2 text-sm bg-white"
            >
              <option value="">All Countries</option>
              {regionCountries.map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          )}

          {/* Sort dropdown */}
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="border rounded-lg px-3 py-2 text-sm bg-white"
          >
            {SORT_OPTIONS.map((s) => (
              <option key={s.id} value={s.id}>↕ {s.label}</option>
            ))}
          </select>

          {hasFilters && (
            <button
              onClick={clearFilters}
              className="px-3 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg border border-red-200"
            >
              ✖ Clear
            </button>
          )}
        </div>
      </div>

      {/* Status Tabs */}
      <div className="flex gap-2 mb-6 border-b overflow-x-auto">
        {STATUS_TABS.map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`px-4 py-2 text-sm font-medium border-b-2 whitespace-nowrap transition ${
              tab === t.id
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            {t.icon} {t.label}
            {t.id !== 'all' && counts[t.id] > 0 && (
              <span className="ml-1 text-xs bg-gray-200 rounded px-1.5">{counts[t.id]}</span>
            )}
          </button>
        ))}
      </div>

      {/* Table */}
      {loading ? (
        <p className="text-center py-10 text-gray-500">Loading...</p>
      ) : cases.length === 0 ? (
        <div className="text-center py-16">
          <p className="text-5xl mb-4">🛂</p>
          <p className="text-gray-500">
            {hasFilters ? 'Koi match nahi mila — filters clear karo' : 'Koi visa case nahi mila'}
          </p>
          <p className="text-xs text-gray-400 mt-2">
            {hasFilters ? 'Filters try karo' : 'Candidate ke saath visa case create karo'}
          </p>
        </div>
      ) : (
        <div className="bg-white rounded-lg border overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="text-left px-4 py-3 text-xs font-semibold text-gray-600">Candidate</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-gray-600">Country</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-gray-600">Type</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-gray-600">Status</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-gray-600">Trust</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-gray-600">Applied</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-gray-600">Days</th>
              </tr>
            </thead>
            <tbody>
              {cases.map((c) => {
                const trust = TRUST_BADGES[c.trust_level] || TRUST_BADGES.REPORTED;
                return (
                  <tr key={c.id} className={`border-t hover:bg-gray-50 ${c.alert ? 'bg-red-50' : ''}`}>
                    <td className="px-4 py-3">
                      <Link to={`/agent/visa/${c.id}`} className="text-sm font-medium text-blue-600 hover:underline">
                        {c.candidate_name || 'Unknown'}
                      </Link>
                      <p className="text-xs text-gray-400">{c.candidate_email || ''}</p>
                    </td>
                    <td className="px-4 py-3 text-sm">{c.country}</td>
                    <td className="px-4 py-3 text-xs text-gray-600">{c.visa_type}</td>
                    <td className="px-4 py-3">
                      <Badge color={STATUS_COLORS[c.status] || 'gray'}>
                        {c.status || 'NOT_STARTED'}
                      </Badge>
                      {c.alert && (
                        <span className="ml-1 text-xs bg-red-100 text-red-700 px-1.5 py-0.5 rounded">
                          {c.alert === 'OVERDUE' ? '⚠️ Overdue' : '🔴 Stuck'}
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      <Badge color={trust.color}>{trust.icon}</Badge>
                    </td>
                    <td className="px-4 py-3 text-xs text-gray-500">
                      {c.applied_at ? new Date(c.applied_at).toLocaleDateString() : '—'}
                    </td>
                    <td className="px-4 py-3 text-xs">
                      <span className={`font-semibold ${
                        c.days_pending > 60 ? 'text-red-600' :
                        c.days_pending > 30 ? 'text-orange-600' : 'text-gray-600'
                      }`}>
                        {c.days_pending || 0}d
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}