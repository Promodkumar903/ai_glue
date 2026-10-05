import React, { useState, useEffect } from 'react';
import { PageHeader, Card, DataTable, Badge, Button, Input, Dropdown, Alert } from '../../components/ui/Components';
import { searchAPI, applicationsAPI } from '../../services/api';
import { useDebounce } from '../../hooks/useFetch';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const safeArr = (v) => {
  if (Array.isArray(v)) return v;
  if (v && typeof v === 'object') {
    if (Array.isArray(v.items)) return v.items;
    if (Array.isArray(v.data)) return v.data;
    if (Array.isArray(v.results)) return v.results;
  }
  return [];
};
const safeStr = (v, fb = '—') => (v == null || v === '') ? fb : String(v);

const JOB_TYPES = ['Full-time', 'Part-time', 'Contract', 'Internship', 'Freelance', 'Remote'];

export default function JobSearch() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [query, setQuery] = useState('');
  const [region, setRegion] = useState('');
  const [country, setCountry] = useState('');
  const [type, setType] = useState('');
  const [applied, setApplied] = useState({});
  const [applying, setApplying] = useState(null);
  const [regions, setRegions] = useState({});
  const [loadingRegions, setLoadingRegions] = useState(true);
  const [aiJobs, setAiJobs] = useState([]);
  const [aiNote, setAiNote] = useState('');
  const [aiLoading, setAiLoading] = useState(false);
  const [showCompanyModal, setShowCompanyModal] = useState(false);
  const [companyInfo, setCompanyInfo] = useState(null);
  const [companyLoading, setCompanyLoading] = useState(false);
  const [selectedCompany, setSelectedCompany] = useState('');
  const debouncedQuery = useDebounce(query, 500);

  // Load regions
  useEffect(() => {
    fetch(`${API_BASE}/jobs/regions`)
      .then((r) => r.json())
      .then((d) => setRegions(d || {}))
      .catch(() => setRegions({}))
      .finally(() => setLoadingRegions(false));
  }, []);

  // DB search
  useEffect(() => {
    setLoading(true);
    setError('');
    const filters = {};
    if (country) filters.country = country;
    if (type) filters.type = type;
    searchAPI.opportunities(debouncedQuery, filters)
      .then((r) => setJobs(safeArr(r.data)))
      .catch(() => setJobs([]))
      .finally(() => setLoading(false));
  }, [debouncedQuery, country, type]);

  // AI search
  const handleAISearch = async () => {
    if (!query.trim()) {
      setError('Please enter a search query for AI');
      return;
    }
    setAiLoading(true);
    setError('');
    setAiJobs([]);
    setAiNote('');

    try {
      const res = await fetch(`${API_BASE}/ai/job-search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: query,
          region: region,
          country: country,
          job_type: type,
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'AI search failed');
      setAiJobs(data.jobs || []);
      setAiNote(data.ai_note || '');
    } catch (e) {
      setError(e.message);
    } finally {
      setAiLoading(false);
    }
  };

  // Company research
  const handleCompanyResearch = async (companyName) => {
    setSelectedCompany(companyName);
    setShowCompanyModal(true);
    setCompanyLoading(true);
    setCompanyInfo(null);

    try {
      const res = await fetch(`${API_BASE}/ai/company-info`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          company_name: companyName,
          country: country || '',
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Company info failed');
      setCompanyInfo(data);
    } catch (e) {
      setCompanyInfo({ error: e.message });
    } finally {
      setCompanyLoading(false);
    }
  };

  const handleApply = async (job) => {
    const jobId = job.id || job.apply_url;
    setApplying(jobId);
    try {
      if (job.id) {
        await applicationsAPI.create({ opportunity_id: job.id });
        setApplied((p) => ({ ...p, [job.id]: true }));
      } else if (job.apply_url) {
        window.open(job.apply_url, '_blank');
        setApplied((p) => ({ ...p, [jobId]: true }));
      }
    } catch (e) {
      alert('❌ ' + (e.response?.data?.detail || e.message));
    } finally {
      setApplying(null);
    }
  };

  const regionOptions = Object.keys(regions).map((r) => ({
    value: r,
    label: `${regions[r].flag || ''} ${r}`,
  }));

  const countryOptions = region && regions[region]
    ? regions[region].countries.map((c) => ({ value: c, label: c }))
    : [];

  const uniqueCountries = [...new Set(jobs.map((j) => j.country).filter(Boolean))];
  const types = [...new Set(jobs.map((j) => j.type).filter(Boolean))];

  const allJobs = aiJobs.length > 0 ? aiJobs : jobs;

  return (
    <div className="p-6">
      <PageHeader
        icon="🔍"
        title="Find Jobs & Opportunities"
        subtitle="AI-powered search — jobs across Asia, Middle East, Europe, and beyond"
        image="https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d?w=1600&q=80"
      />

      {error && <Alert type="danger" onClose={() => setError('')}>{error}</Alert>}

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <Card title="Available Jobs" value={allJobs.length} icon="💼" color="blue" />
        <Card title="Countries" value={uniqueCountries.length} icon="🌍" color="purple" />
        <Card title="AI Jobs" value={aiJobs.length} icon="🤖" color="indigo" />
        <Card title="Applied" value={Object.keys(applied).length} icon="✅" color="green" />
      </div>

      {/* AI Search Section */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl shadow p-4 mb-4 border border-blue-200">
        <div className="flex items-center gap-2 mb-3">
          <span className="text-2xl">🤖</span>
          <div>
            <h3 className="font-bold text-gray-800">AI Job Search</h3>
            <p className="text-xs text-gray-600">Search any job, any country — AI finds real openings</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
          <div className="md:col-span-2">
            <Input
              label="What job are you looking for?"
              value={query}
              onChange={setQuery}
              placeholder="e.g. labor jobs, Python developer, hotel manager..."
            />
          </div>
          <Dropdown
            label="Region"
            value={region}
            onChange={(v) => { setRegion(v); setCountry(''); }}
            options={loadingRegions ? [] : regionOptions}
            placeholder={loadingRegions ? 'Loading...' : 'All Regions'}
          />
          <Dropdown
            label="Country"
            value={country}
            onChange={setCountry}
            options={countryOptions}
            placeholder={!region ? 'Region first' : 'All Countries'}
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-3 mt-3">
          <Dropdown
            label="Job Type"
            value={type}
            onChange={setType}
            options={JOB_TYPES.map((t) => ({ value: t, label: t }))}
            placeholder="All Types"
          />
          <div className="md:col-span-3 flex items-end gap-2">
            <Button onClick={handleAISearch} loading={aiLoading} fullWidth>
              🤖 Search with AI
            </Button>
            <Button
              onClick={() => { setQuery(''); setRegion(''); setCountry(''); setType(''); setAiJobs([]); setAiNote(''); }}
              variant="ghost"
            >
              🔄 Reset
            </Button>
          </div>
        </div>
      </div>

      {/* AI Note */}
      {aiNote && (
        <div className="mb-4 p-3 bg-purple-50 border border-purple-200 rounded-lg text-sm text-purple-800">
          <strong>🤖 AI Insights:</strong> {aiNote}
        </div>
      )}

      {/* Active Filters */}
      {(region || country || type || query) && (
        <div className="flex gap-2 mb-4 flex-wrap">
          {region && <Badge color="blue">🌍 {region}</Badge>}
          {country && <Badge color="purple">📍 {country}</Badge>}
          {type && <Badge color="indigo">💼 {type}</Badge>}
          {query && <Badge color="green">🔍 "{query}"</Badge>}
        </div>
      )}

      <h3 className="text-lg font-bold mb-3">
        {aiJobs.length > 0 ? '🤖 AI-Recommended Jobs' : '💼 Job Openings'} ({allJobs.length})
      </h3>

      {/* AI Jobs Cards */}
      {aiJobs.length > 0 ? (
        <div className="space-y-3">
          {aiJobs.map((job, idx) => (
            <div key={idx} className="bg-white p-5 rounded-xl shadow border hover:shadow-md transition">
              <div className="flex justify-between items-start mb-3 flex-wrap gap-2">
                <div className="flex-1">
                  <h4 className="font-bold text-lg text-gray-800">{job.title}</h4>
                  <div className="flex items-center gap-3 mt-1 flex-wrap">
                    <button
                      onClick={() => handleCompanyResearch(job.company)}
                      className="text-sm text-blue-600 hover:text-blue-800 hover:underline font-medium"
                    >
                      🏢 {job.company}
                    </button>
                    <span className="text-xs text-gray-500">📍 {job.location}</span>
                    <Badge color="blue">{job.job_type}</Badge>
                    <Badge color="purple">{job.experience_level}</Badge>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-bold text-emerald-600">{job.salary}</p>
                  <p className="text-xs text-gray-400">{job.posted_date}</p>
                </div>
              </div>

              {job.description && (
                <p className="text-sm text-gray-600 mb-2">{job.description}</p>
              )}

              {job.requirements && job.requirements.length > 0 && (
                <ul className="text-xs text-gray-600 mb-3 space-y-0.5">
                  {job.requirements.slice(0, 5).map((req, i) => (
                    <li key={i}>• {req}</li>
                  ))}
                </ul>
              )}

              <div className="flex gap-2 flex-wrap">
                <Button
                  size="sm"
                  variant={applied[job.apply_url] ? 'success' : 'primary'}
                  disabled={applied[job.apply_url]}
                  onClick={() => handleApply(job)}
                >
                  {applied[job.apply_url] ? '✅ Applied' : '📨 Apply'}
                </Button>
                <button
                  onClick={() => handleCompanyResearch(job.company)}
                  className="text-xs bg-gray-100 hover:bg-gray-200 px-3 py-1.5 rounded font-medium"
                >
                  🔍 Research Company
                </button>
                {job.company_website && (
                  <a
                    href={job.company_website}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs bg-blue-50 hover:bg-blue-100 text-blue-700 px-3 py-1.5 rounded font-medium"
                  >
                    🌐 Website
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <DataTable
          loading={loading}
          empty="Koi job nahi mili — AI search try karo"
          columns={[
            {
              key: 'title', label: 'Job Title',
              render: (r) => (
                <div>
                  <p className="font-semibold text-gray-800">{safeStr(r.title || r.name)}</p>
                  {r.company && <p className="text-xs text-gray-500">{safeStr(r.company)}</p>}
                </div>
              ),
            },
            { key: 'country', label: 'Country', render: (r) => safeStr(r.country) },
            { key: 'type', label: 'Type', render: (r) => <Badge color="blue">{safeStr(r.type, 'N/A')}</Badge> },
            { key: 'salary', label: 'Salary', render: (r) => safeStr(r.salary, '—') },
            {
              key: 'actions', label: 'Action',
              render: (r) => (
                <Button
                  size="sm"
                  variant={applied[r.id] ? 'success' : 'primary'}
                  disabled={applied[r.id] || applying === r.id}
                  loading={applying === r.id}
                  onClick={() => handleApply(r)}
                >
                  {applied[r.id] ? '✅ Applied' : '📨 Apply'}
                </Button>
              ),
            },
          ]}
          data={jobs}
        />
      )}

      {/* Company Info Modal */}
      {showCompanyModal && (
        <div
          className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4"
          onClick={() => setShowCompanyModal(false)}
        >
          <div
            className="bg-white rounded-xl max-w-2xl w-full max-h-[85vh] overflow-y-auto p-6"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex justify-between items-center mb-4">
              <h3 className="font-bold text-lg">🏢 {selectedCompany}</h3>
              <button
                onClick={() => setShowCompanyModal(false)}
                className="text-gray-400 hover:text-gray-700 text-2xl leading-none"
              >
                ×
              </button>
            </div>

            {companyLoading && (
              <div className="text-center py-12 text-gray-400">
                <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mb-3"></div>
                <p>AI researching company...</p>
              </div>
            )}

            {companyInfo && !companyLoading && companyInfo.error && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-800">
                {companyInfo.error}
              </div>
            )}

            {companyInfo && !companyLoading && !companyInfo.error && (
              <div className="space-y-4 text-sm">
                <div>
                  <h4 className="font-semibold text-gray-700 mb-1">📖 Overview</h4>
                  <p className="text-gray-600">{companyInfo.overview}</p>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  {companyInfo.industry && (
                    <div><span className="text-gray-500">Industry:</span> <strong>{companyInfo.industry}</strong></div>
                  )}
                  {companyInfo.founded && (
                    <div><span className="text-gray-500">Founded:</span> <strong>{companyInfo.founded}</strong></div>
                  )}
                  {companyInfo.headquarters && (
                    <div><span className="text-gray-500">HQ:</span> <strong>{companyInfo.headquarters}</strong></div>
                  )}
                  {companyInfo.employees && (
                    <div><span className="text-gray-500">Employees:</span> <strong>{companyInfo.employees}</strong></div>
                  )}
                  {companyInfo.rating && (
                    <div><span className="text-gray-500">Rating:</span> <strong>⭐ {companyInfo.rating}</strong></div>
                  )}
                  {companyInfo.website && (
                    <div>
                      <span className="text-gray-500">Website:</span>{' '}
                      <a href={companyInfo.website} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                        {companyInfo.website}
                      </a>
                    </div>
                  )}
                </div>

                {companyInfo.pros && companyInfo.pros.length > 0 && (
                  <div>
                    <h4 className="font-semibold text-emerald-700 mb-1">✅ Pros</h4>
                    <ul className="list-disc list-inside text-gray-600 space-y-0.5">
                      {companyInfo.pros.map((p, i) => <li key={i}>{p}</li>)}
                    </ul>
                  </div>
                )}

                {companyInfo.cons && companyInfo.cons.length > 0 && (
                  <div>
                    <h4 className="font-semibold text-red-700 mb-1">⚠️ Cons</h4>
                    <ul className="list-disc list-inside text-gray-600 space-y-0.5">
                      {companyInfo.cons.map((c, i) => <li key={i}>{c}</li>)}
                    </ul>
                  </div>
                )}

                {companyInfo.culture && (
                  <div>
                    <h4 className="font-semibold text-gray-700 mb-1">🏢 Culture</h4>
                    <p className="text-gray-600">{companyInfo.culture}</p>
                  </div>
                )}

                {companyInfo.salary_insights && (
                  <div>
                    <h4 className="font-semibold text-gray-700 mb-1">💰 Salary Insights</h4>
                    <p className="text-gray-600">{companyInfo.salary_insights}</p>
                  </div>
                )}

                {companyInfo.hiring_process && (
                  <div>
                    <h4 className="font-semibold text-gray-700 mb-1">📋 Hiring Process</h4>
                    <p className="text-gray-600">{companyInfo.hiring_process}</p>
                  </div>
                )}

                {companyInfo.ai_note && (
                  <div className="p-3 bg-purple-50 border border-purple-200 rounded-lg text-xs text-purple-800">
                    💡 {companyInfo.ai_note}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}