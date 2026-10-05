import React, { useState } from 'react';
import { PageHeader, Card, Badge, Button, Input, Alert } from '../../components/ui/Components';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function MatchCompany() {
  const [orgId, setOrgId] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handleMatch = async () => {
    if (!orgId.trim()) {
      setError('Please enter an organization ID');
      return;
    }
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const cleanId = orgId.trim().split(' ')[0].split('(')[0].split(',')[0].replace(/['"]/g, '').trim();
      const res = await fetch(`${API_BASE}/ai/match/company/${cleanId}`, {
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
        icon="🏢"
        title="AI Match — Company"
        subtitle="Match a company with best candidates"
        image="https://images.unsplash.com/photo-1497366216548-37526070297c?w=1600&q=80"
      />

      {error && <Alert type="danger" onClose={() => setError('')}>{error}</Alert>}

      <div className="bg-white rounded-xl shadow p-6 mb-6">
        <h3 className="font-bold mb-4">🏢 Organization ID</h3>
        <Input
          label="Organization ID"
          value={orgId}
          onChange={setOrgId}
          placeholder="Paste organization UUID here"
        />
        <div className="mt-3">
          <Button onClick={handleMatch} loading={loading} fullWidth>
            🎯 Find Candidates
          </Button>
        </div>
      </div>

      {loading && (
        <div className="text-center py-12 text-gray-400">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mb-3"></div>
          <p>AI matching candidates...</p>
        </div>
      )}

      {result && (
        <>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
            <Card title="Company" value={result.organization?.name || 'N/A'} icon="🏢" color="blue" />
            <Card title="Candidates" value={result.total || 0} icon="👥" color="green" />
            <Card title="Status" value={result.total > 0 ? 'Found' : 'None'} icon="✅" color="purple" />
          </div>

          {result.ai_note && (
            <div className="mb-6 p-4 bg-purple-50 border border-purple-200 rounded-lg text-sm text-purple-800">
              <strong>🤖 AI Note:</strong> {result.ai_note}
            </div>
          )}

          {result.matches?.length > 0 ? (
            <div className="bg-white rounded-xl shadow">
              <h3 className="font-bold p-4 border-b">👥 Top Candidates ({result.matches.length})</h3>
              <div className="divide-y">
                {result.matches.map((m, i) => (
                  <div key={i} className="p-4 hover:bg-gray-50">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <h4 className="font-semibold text-gray-800">{m.name}</h4>
                          <Badge color="green">{m.match_score}% match</Badge>
                        </div>
                        <p className="text-xs text-gray-500">📧 {m.email}</p>
                        {m.roles && <p className="text-xs text-gray-500 mt-1">Roles: {m.roles}</p>}
                        <p className="text-sm text-gray-600 mt-2">{m.reason}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="bg-white rounded-xl shadow p-12 text-center text-gray-400">
              No candidates found
            </div>
          )}
        </>
      )}
    </div>
  );
}