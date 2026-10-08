import React, { useState, useEffect } from 'react';
import { PageHeader, Card, Badge, Alert, Button } from '../../components/ui/Components';
import { crmAPI } from '../../services/api';

const GRADE_COLORS = {
  A: { bg: 'from-yellow-400 to-amber-500', text: 'text-yellow-900', label: 'Elite' },
  B: { bg: 'from-blue-400 to-blue-600', text: 'text-blue-900', label: 'Trusted' },
  C: { bg: 'from-orange-400 to-orange-600', text: 'text-orange-900', label: 'Verified' },
  D: { bg: 'from-gray-400 to-gray-600', text: 'text-gray-900', label: 'Standard' },
  E: { bg: 'from-red-400 to-red-600', text: 'text-red-900', label: 'Probation' },
};

const TREND_ICONS = {
  up: '📈',
  down: '📉',
  stable: '➡️',
};

export default function Grades() {
  const [grade, setGrade] = useState(null);
  const [leaderboard, setLeaderboard] = useState([]);
  const [loading, setLoading] = useState(true);
  const [recalculating, setRecalculating] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const load = () => {
    setLoading(true);
    Promise.all([
      crmAPI.myGrade().catch(() => ({ data: null })),
      crmAPI.gradesLeaderboard(20).catch(() => ({ data: { leaderboard: [] } })),
    ])
      .then(([g, l]) => {
        setGrade(g.data);
        setLeaderboard(l.data?.leaderboard || []);
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  const recalculate = async () => {
    setRecalculating(true);
    setError('');
    try {
      const res = await crmAPI.recalculateGrade();
      if (res.data?.error) {
        setError('Recalc failed: ' + res.data.error);
      } else {
        setSuccess(`Grade recalculated: ${res.data.grade} (${res.data.score})`);
        load();
      }
    } catch (e) {
      setError('Failed: ' + (e.response?.data?.detail || e.message));
    } finally {
      setRecalculating(false);
    }
  };

  if (loading) return <div className="p-6">Loading grades...</div>;

  const myGrade = grade?.grade;
  const style = GRADE_COLORS[myGrade] || GRADE_COLORS.C;

  return (
    <div className="p-6">
      <PageHeader icon="🏆" title="Agent Grades" subtitle="Week-based performance grading" />

      {error && <div className="mb-3"><Alert type="danger" onClose={() => setError('')}>{error}</Alert></div>}
      {success && <div className="mb-3"><Alert type="success" onClose={() => setSuccess('')}>{success}</Alert></div>}

      {/* My Grade Card */}
      <div className="mb-6 bg-white rounded-lg border p-6">
        <div className="flex justify-between items-start mb-4">
          <h2 className="text-lg font-semibold">📊 My Grade</h2>
          <Button onClick={recalculate} disabled={recalculating}>
            {recalculating ? 'Calculating...' : '🔄 Recalculate'}
          </Button>
        </div>

        {!myGrade ? (
          <div className="text-center py-8">
            <p className="text-gray-500 mb-3">Abhi tak koi grade nahi hai.</p>
            <Button onClick={recalculate} disabled={recalculating}>
              {recalculating ? 'Calculating...' : '🎯 Calculate Now'}
            </Button>
          </div>
        ) : (
          <>
            <div className="flex items-center gap-6 mb-6">
              <div className={`w-24 h-24 bg-gradient-to-br ${style.bg} rounded-2xl flex items-center justify-center shadow-lg`}>
                <span className={`text-5xl font-bold ${style.text}`}>{myGrade}</span>
              </div>
              <div>
                <h3 className="text-2xl font-bold">{style.label}</h3>
                <p className="text-gray-600">
                  Score: <strong className="text-lg">{grade.score}</strong>
                  <span className="ml-3">{TREND_ICONS[grade.trend] || '➡️'} {grade.trend || 'stable'}</span>
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  Week: {grade.week_start?.slice(0, 10) || '—'}
                </p>
              </div>
            </div>

            {/* Factor breakdown */}
            {grade.week_completion_rate !== undefined && (
              <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                <div className="bg-gray-50 rounded p-3 text-center">
                  <p className="text-xs text-gray-600 mb-1">Week Completion</p>
                  <p className="font-bold">{((grade.week_completion_rate || 0) * 100).toFixed(0)}%</p>
                </div>
                <div className="bg-gray-50 rounded p-3 text-center">
                  <p className="text-xs text-gray-600 mb-1">Career</p>
                  <p className="font-bold">{((grade.career_completion_rate || 0) * 100).toFixed(0)}%</p>
                </div>
                <div className="bg-gray-50 rounded p-3 text-center">
                  <p className="text-xs text-gray-600 mb-1">Rating</p>
                  <p className="font-bold">{grade.rating || 0}/5</p>
                </div>
                <div className="bg-gray-50 rounded p-3 text-center">
                  <p className="text-xs text-gray-600 mb-1">Disputes</p>
                  <p className="font-bold">{grade.disputes || 0}</p>
                </div>
                <div className="bg-gray-50 rounded p-3 text-center">
                  <p className="text-xs text-gray-600 mb-1">Status</p>
                  <p className="font-bold text-green-700">Active</p>
                </div>
              </div>
            )}
          </>
        )}
      </div>

      {/* Grade Scale */}
      <div className="mb-6 bg-white rounded-lg border p-4">
        <h2 className="font-semibold mb-3">📏 Grade Scale</h2>
        <div className="grid grid-cols-5 gap-3">
          {Object.entries(GRADE_COLORS).map(([g, s]) => (
            <div key={g} className={`bg-gradient-to-br ${s.bg} rounded-lg p-3 text-center`}>
              <p className={`text-2xl font-bold ${s.text}`}>{g}</p>
              <p className={`text-xs ${s.text} font-medium`}>{s.label}</p>
              <p className={`text-xs ${s.text} opacity-75`}>
                {g === 'A' ? '90+' : g === 'B' ? '75+' : g === 'C' ? '60+' : g === 'D' ? '40+' : '0+'}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Leaderboard */}
      <div className="bg-white rounded-lg border p-4">
        <h2 className="font-semibold mb-3">🏅 Leaderboard — Top Agents</h2>
        {leaderboard.length === 0 ? (
          <p className="text-sm text-gray-500 text-center py-6">
            Koi grade calculate nahi hua abhi. Recalculate karo.
          </p>
        ) : (
          <div className="space-y-2">
            {leaderboard.map((entry, idx) => {
              const s = GRADE_COLORS[entry.grade] || GRADE_COLORS.C;
              return (
                <div key={entry.agent_id} className="flex items-center gap-3 border rounded px-3 py-2">
                  <span className="text-lg font-bold text-gray-400 w-8">#{idx + 1}</span>
                  <div className={`w-10 h-10 bg-gradient-to-br ${s.bg} rounded-lg flex items-center justify-center`}>
                    <span className={`font-bold ${s.text}`}>{entry.grade}</span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">Agent {entry.agent_id.slice(0, 8)}...</p>
                    <p className="text-xs text-gray-500">Score: {entry.score}</p>
                  </div>
                  <span className="text-lg">{TREND_ICONS[entry.trend] || '➡️'}</span>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}