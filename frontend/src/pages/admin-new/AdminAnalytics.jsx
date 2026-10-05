import React, { useState, useEffect } from 'react';
import { PageHeader, Card, Badge, Button, Alert } from '../../components/ui/Components';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function AdminAnalytics() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [days, setDays] = useState(7);

  const fetchSummary = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await fetch(`${API_BASE}/admin/analytics/summary?days=${days}`);
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Failed to load analytics');
      setSummary(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSummary();
  }, [days]);

  return (
    <div className="p-6">
      <PageHeader
        icon="📊"
        title="Analytics & Traffic"
        subtitle="Visitor tracking, page views, clicks, and downloads"
        image="https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=1600&q=80"
      />

      {error && <Alert type="danger" onClose={() => setError('')}>{error}</Alert>}

      {/* Period Selector */}
      <div className="flex gap-2 mb-6">
        {[7, 14, 30, 90].map((d) => (
          <button
            key={d}
            onClick={() => setDays(d)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
              days === d
                ? 'bg-blue-600 text-white'
                : 'bg-white border border-gray-200 hover:border-blue-400'
            }`}
          >
            Last {d} days
          </button>
        ))}
        <button
          onClick={fetchSummary}
          className="px-4 py-2 rounded-lg text-sm font-medium bg-gray-100 hover:bg-gray-200 ml-auto"
        >
          🔄 Refresh
        </button>
      </div>

      {loading ? (
        <div className="text-center py-12 text-gray-400">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mb-3"></div>
          <p>Loading analytics...</p>
        </div>
      ) : summary ? (
        <>
          {/* Stats Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <Card title="Total Events" value={summary.total_events} icon="📊" color="blue" />
            <Card title="Unique Visitors" value={summary.unique_visitors} icon="👥" color="purple" />
            <Card title="Event Types" value={summary.by_type?.length || 0} icon="🎯" color="indigo" />
            <Card title="Top Pages" value={summary.top_pages?.length || 0} icon="📄" color="green" />
          </div>

          {/* Daily Trend */}
          <div className="bg-white rounded-xl shadow p-5 mb-6">
            <h3 className="font-bold mb-4">📈 Daily Trend</h3>
            {summary.daily_trend?.length > 0 ? (
              <div className="space-y-2">
                {summary.daily_trend.map((d, i) => {
                  const maxCount = Math.max(...summary.daily_trend.map((x) => x.count));
                  const width = maxCount > 0 ? (d.count / maxCount) * 100 : 0;
                  return (
                    <div key={i} className="flex items-center gap-3">
                      <span className="text-xs text-gray-500 w-24">{d.date}</span>
                      <div className="flex-1 bg-gray-100 rounded-full h-6 relative">
                        <div
                          className="bg-gradient-to-r from-blue-500 to-indigo-600 h-6 rounded-full transition-all"
                          style={{ width: `${width}%` }}
                        />
                      </div>
                      <span className="text-xs font-bold text-gray-700 w-12 text-right">{d.count}</span>
                    </div>
                  );
                })}
              </div>
            ) : (
              <p className="text-center text-gray-400 py-4">No data yet</p>
            )}
          </div>

          {/* Event Types + Top Pages */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white rounded-xl shadow p-5">
              <h3 className="font-bold mb-4">🎯 Events by Type</h3>
              {summary.by_type?.length > 0 ? (
                <div className="space-y-2">
                  {summary.by_type.map((t, i) => (
                    <div key={i} className="flex justify-between items-center py-2 border-b">
                      <span className="text-sm text-gray-700">{t.event_type}</span>
                      <Badge color="blue">{t.count}</Badge>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-center text-gray-400 py-4">No events yet</p>
              )}
            </div>

            <div className="bg-white rounded-xl shadow p-5">
              <h3 className="font-bold mb-4">📄 Top Pages</h3>
              {summary.top_pages?.length > 0 ? (
                <div className="space-y-2">
                  {summary.top_pages.map((p, i) => (
                    <div key={i} className="flex justify-between items-center py-2 border-b">
                      <span className="text-sm text-gray-700 truncate">{p.page}</span>
                      <Badge color="purple">{p.count}</Badge>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-center text-gray-400 py-4">No page views yet</p>
              )}
            </div>
          </div>
        </>
      ) : null}
    </div>
  );
}