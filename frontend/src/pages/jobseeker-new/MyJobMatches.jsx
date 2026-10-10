import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../services/api';

export default function MyJobMatches() {
  const navigate = useNavigate();
  const [jobs, setJobs] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [profile, setProfile] = useState(null);
  const [filters, setFilters] = useState({ country: '', minScore: 30 });

  // Try to get user_id from localStorage (multiple possible keys)
  const userId =
    localStorage.getItem('user_id') ||
    localStorage.getItem('userId') ||
    'test_student_001';

  useEffect(() => {
    loadMatches();
  }, []);

  const loadMatches = async () => {
    try {
      setLoading(true);
      const r = await api.get('/admin/oie/my-matches', {
        params: {
          user_id: userId,
          limit: 50,
          min_score: filters.minScore,
          country: filters.country,
        },
      });
      setJobs(r.data.jobs || []);
      setTotal(r.data.total || 0);
      setProfile(r.data.profile);
    } catch (e) {
      console.error('Failed to load matches:', e);
    } finally {
      setLoading(false);
    }
  };

  const applyFilter = () => loadMatches();

  const resetFilter = () => {
    setFilters({ country: '', minScore: 30 });
    setTimeout(loadMatches, 100);
  };

  const getInitials = (name) => {
    const words = (name || '').split(' ').filter((w) => w);
    if (words.length >= 2) return (words[0][0] + words[1][0]).toUpperCase();
    return (words[0]?.slice(0, 2) || 'CO').toUpperCase();
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="text-center">
          <div className="animate-spin w-8 h-8 border-4 border-purple-500 border-t-transparent rounded-full mx-auto mb-3"></div>
          <div className="text-slate-500">Finding your best matches...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-slate-900 flex items-center gap-2">
            <span>🎯</span> My Job Matches
          </h1>
          <p className="text-slate-500 mt-1">
            Personalized jobs verified from official sources
          </p>
          {profile && (
            <div className="mt-3 flex gap-3 text-sm flex-wrap">
              <span className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full font-medium">
                Target: {profile.target_countries || 'Any'}
              </span>
              <span className="px-3 py-1 bg-indigo-100 text-indigo-700 rounded-full font-medium">
                {total} matches found
              </span>
            </div>
          )}
        </div>

        {/* Filters */}
        <div className="bg-white rounded-xl border border-slate-200 p-4 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
            <div>
              <label className="text-xs text-slate-500 font-medium">Country</label>
              <select
                value={filters.country}
                onChange={(e) => setFilters({ ...filters, country: e.target.value })}
                className="w-full mt-1 px-3 py-2 border border-slate-300 rounded-lg text-sm"
              >
                <option value="">All Countries</option>
                <option value="Germany">🇩🇪 Germany</option>
                <option value="Austria">🇦🇹 Austria</option>
                <option value="Netherlands">🇳🇱 Netherlands</option>
                <option value="France">🇫🇷 France</option>
                <option value="Sweden">🇸🇪 Sweden</option>
                <option value="Norway">🇳🇴 Norway</option>
                <option value="Denmark">🇩🇰 Denmark</option>
                <option value="UAE">🇦🇪 UAE</option>
                <option value="Saudi Arabia">🇸🇦 Saudi Arabia</option>
                <option value="Qatar">🇶🇦 Qatar</option>
                <option value="Kuwait">🇰🇼 Kuwait</option>
              </select>
            </div>
            <div>
              <label className="text-xs text-slate-500 font-medium">Min Match Score</label>
              <select
                value={filters.minScore}
                onChange={(e) => setFilters({ ...filters, minScore: parseInt(e.target.value) })}
                className="w-full mt-1 px-3 py-2 border border-slate-300 rounded-lg text-sm"
              >
                <option value="30">30%+ (All)</option>
                <option value="50">50%+ (Good)</option>
                <option value="70">70%+ (Strong)</option>
                <option value="90">90%+ (Perfect)</option>
              </select>
            </div>
            <div className="flex items-end gap-2 md:col-span-2">
              <button
                onClick={applyFilter}
                className="px-6 py-2 bg-purple-600 text-white rounded-lg text-sm font-medium hover:bg-purple-700 transition"
              >
                Apply Filters
              </button>
              <button
                onClick={resetFilter}
                className="px-6 py-2 bg-slate-100 text-slate-700 rounded-lg text-sm hover:bg-slate-200 transition"
              >
                Reset
              </button>
            </div>
          </div>
        </div>

        {/* Jobs Grid */}
        {jobs.length === 0 ? (
          <div className="bg-white rounded-xl border border-slate-200 p-12 text-center">
            <div className="text-5xl mb-4">🔍</div>
            <div className="text-lg font-semibold mb-2">No matches found</div>
            <div className="text-sm text-slate-500">
              Try lowering the minimum score or removing the country filter
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {jobs.map((job) => (
              <div
                key={job.id}
                className="bg-white rounded-xl border border-slate-200 p-5 hover:border-purple-400 hover:shadow-lg transition cursor-pointer"
                onClick={() => navigate(`/jobs/${job.id}`)}
              >
                <div className="flex items-start gap-4">
                  <div className="w-14 h-14 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-xl flex items-center justify-center text-white font-bold text-lg flex-shrink-0 shadow-sm">
                    {getInitials(job.company_name)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="font-bold text-slate-900 truncate text-base">
                      {job.job_title}
                    </h3>
                    <p className="text-sm text-slate-600 truncate mt-0.5">
                      {job.company_name}
                    </p>
                    <div className="flex items-center gap-2 mt-2 flex-wrap">
                      <span className="text-xs px-2 py-0.5 bg-slate-100 text-slate-700 rounded-full">
                        📍 {job.country}
                      </span>
                      <span className="text-xs px-2 py-0.5 bg-purple-100 text-purple-700 rounded-full font-semibold">
                        {job.match_score}% match
                      </span>
                    </div>
                  </div>
                </div>

                {/* Benefits row */}
                <div className="flex gap-4 mt-3 pt-3 border-t border-slate-100 text-xs">
                  <span
                    className={
                      job.free_visa ? 'text-green-600 font-medium' : 'text-slate-300'
                    }
                  >
                    {job.free_visa ? '✅' : '○'} Visa
                  </span>
                  <span
                    className={
                      job.free_ticket ? 'text-green-600 font-medium' : 'text-slate-300'
                    }
                  >
                    {job.free_ticket ? '✅' : '○'} Ticket
                  </span>
                  <span
                    className={
                      job.accommodation ? 'text-green-600 font-medium' : 'text-slate-300'
                    }
                  >
                    {job.accommodation ? '✅' : '○'} Stay
                  </span>
                  <span
                    className={
                      job.no_commission ? 'text-green-600 font-medium' : 'text-slate-300'
                    }
                  >
                    {job.no_commission ? '✅' : '○'} No Fee
                  </span>
                </div>

                {/* Apply Button */}
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    navigate(`/jobs/${job.id}`);
                  }}
                  className="mt-4 w-full py-2 bg-purple-600 text-white rounded-lg text-sm font-medium hover:bg-purple-700 transition"
                >
                  View & Apply →
                </button>
              </div>
            ))}
          </div>
        )}

        {/* Footer */}
        {jobs.length > 0 && (
          <div className="text-center mt-8 text-xs text-slate-400">
            Showing top {jobs.length} of {total} matches · Powered by AI Glue
          </div>
        )}
      </div>
    </div>
  );
}