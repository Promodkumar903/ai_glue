import React, { useState } from 'react';
import { PageHeader, Card, Badge, Button, Input, Alert } from '../../components/ui/Components';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function MatchJobSeeker() {
  const [userId, setUserId] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handleMatch = async () => {
    if (!userId.trim()) {
      setError('Please enter a user ID');
      return;
    }
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const cleanId = userId.trim().split(' ')[0].split('(')[0].trim();
      const res = await fetch(`${API_BASE}/ai/match/job-seeker/${cleanId}`, {
        method: 'POST',
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Match failed');
      setResult(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6">
      <PageHeader
        icon="🎯"
        title="AI Match — Job Seeker"
        subtitle="Match a job seeker with relevant jobs using AI"
        image="https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=1600&q=80"
      />

      {error && <Alert type="danger" onClose={() => setError('')}>{error}</Alert>}

      <div className="bg-white rounded-xl shadow p-6 mb-6">
        <h3 className="font-bold mb-4">👤 Job Seeker User ID</h3>
        <Input
          label="User ID"
          value={userId}
          onChange={setUserId}
          placeholder="e.g. f64802bf-f215-4d17-8cd7-faceb5d1f0ba"
        />
        <div className="mt-3">
          <Button onClick={handleMatch} loading={loading} fullWidth>
            🎯 Find Matches
          </Button>
        </div>
      </div>

      {loading && (
        <div className="text-center py-12 text-gray-400">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mb-3"></div>
          <p>AI matching jobs...</p>
          <p className="text-xs mt-2">This may take 10-15 seconds</p>
        </div>
      )}

      {result && (
        <>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
            <Card title="Candidate" value={result.user?.name || 'N/A'} icon="👤" color="blue" />
            <Card title="Matches" value={result.total || 0} icon="🎯" color="green" />
            <Card title="Status" value={result.total > 0 ? 'Found' : 'None'} icon="✅" color="purple" />
          </div>

          {result.ai_note && (
            <div className="mb-6 p-4 bg-purple-50 border border-purple-200 rounded-lg text-sm text-purple-800">
              <strong>🤖 AI Note:</strong> {result.ai_note}
            </div>
          )}

          {result.matches?.length > 0 ? (
            <div className="bg-white rounded-xl shadow">
              <h3 className="font-bold p-4 border-b">🎯 Top Matches ({result.matches.length})</h3>
              <div className="divide-y">
                {result.matches.map((m, i) => (
                  <div key={i} className="p-4 hover:bg-gray-50">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <h4 className="font-semibold text-gray-800">{m.title}</h4>
                          <Badge color="green">{m.match_score}% match</Badge>
                        </div>
                        <p className="text-xs text-gray-500">
                          🏢 {m.company} | 📍 {m.country} | 💼 {m.type}
                        </p>
                        {m.salary && <p className="text-sm text-emerald-600 font-medium mt-1">{m.salary}</p>}
                        <p className="text-sm text-gray-600 mt-2">{m.reason}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="bg-white rounded-xl shadow p-12 text-center text-gray-400">
              No matches found — try a different user
            </div>
          )}
        </>
      )}
    </div>
  );
}