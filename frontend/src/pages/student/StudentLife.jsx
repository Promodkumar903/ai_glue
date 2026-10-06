import { useEffect, useState } from 'react';
import { Briefcase, BookOpen, Heart, Sparkles } from 'lucide-react';
import axios from '../../utils/axios';
import Hero from '../../components/Hero';

const CATEGORIES = [
  { id: 'sim', label: '📱 SIM / Internet' },
  { id: 'bank', label: '🏦 Bank Account' },
  { id: 'health', label: '🏥 Health Insurance' },
  { id: 'accommodation', label: '🏠 Accommodation' },
  { id: 'transport', label: '🚌 Transport' },
  { id: 'food', label: '🍔 Food / Grocery' },
  { id: 'books', label: '📚 Books / Study' },
  { id: 'emergency', label: '🆘 Emergency' },
];

export default function StudentLife() {
  const [jobs, setJobs] = useState([]);
  const [books, setBooks] = useState([]);
  const [need, setNeed] = useState(null);
  const [loading, setLoading] = useState(true);

  // AI Suggest state
  const [category, setCategory] = useState('sim');
  const [country, setCountry] = useState('Germany');
  const [aiLoading, setAiLoading] = useState(false);
  const [aiResult, setAiResult] = useState(null);
  const [aiError, setAiError] = useState('');

  useEffect(() => {
    Promise.all([
      axios.get('/student-life/jobs').catch(() => ({ data: [] })),
      axios.get('/student-life/books').catch(() => ({ data: [] })),
      axios.get('/student-life/me').catch(() => ({ data: null })),
    ]).then(([jRes, bRes, mRes]) => {
      setJobs(Array.isArray(jRes.data) ? jRes.data : []);
      setBooks(Array.isArray(bRes.data) ? bRes.data : []);
      setNeed(mRes.data);
      setLoading(false);
    });
  }, []);

  const handleAiSuggest = async () => {
    setAiLoading(true);
    setAiError('');
    setAiResult(null);
    try {
      const res = await axios.post('/student-life/ai-suggest', {
        category,
        country,
      });
      setAiResult(res.data);
    } catch (err) {
      setAiError(err.response?.data?.detail || 'AI suggestion failed');
    } finally {
      setAiLoading(false);
    }
  };

  if (loading) return <div className="text-center py-12 text-slate-400">Loading...</div>;

  return (
    <div className="p-6">
      <Hero
        title="❤️ Student Life"
        subtitle="Part-time jobs, books, and daily needs"
        imageUrl="https://images.unsplash.com/photo-1523050854058-8df90110c9f1?w=1600&q=80"
      />

      {/* AI Suggest Box */}
      <div className="bg-gradient-to-r from-purple-50 to-pink-50 border border-purple-200 rounded-2xl p-6 mb-6">
        <div className="flex items-center gap-3 mb-4">
          <Sparkles className="w-6 h-6 text-purple-600" />
          <h2 className="text-lg font-bold text-slate-800">AI Suggestions</h2>
        </div>
        <p className="text-sm text-slate-600 mb-4">
          Select what you need — AI will suggest the best options for your country.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-[1fr_1fr_auto] gap-3">
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="p-3 border-2 border-purple-200 rounded-xl bg-white focus:outline-none focus:border-purple-500"
          >
            {CATEGORIES.map((c) => (
              <option key={c.id} value={c.id}>{c.label}</option>
            ))}
          </select>

          <input
            type="text"
            value={country}
            onChange={(e) => setCountry(e.target.value)}
            placeholder="Country (e.g. Germany)"
            className="p-3 border-2 border-purple-200 rounded-xl bg-white focus:outline-none focus:border-purple-500"
          />

          <button
            onClick={handleAiSuggest}
            disabled={aiLoading}
            className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-6 py-3 rounded-xl font-semibold hover:opacity-90 disabled:opacity-50 flex items-center justify-center gap-2"
          >
            <Sparkles className="w-4 h-4" />
            {aiLoading ? 'Thinking...' : 'Get AI Suggestions'}
          </button>
        </div>

        {aiError && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
            {aiError}
          </div>
        )}

        {aiResult && aiResult.items?.length > 0 && (
          <div className="mt-6">
            {aiResult.ai_note && (
              <p className="text-sm text-slate-600 italic mb-4">💡 {aiResult.ai_note}</p>
            )}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {aiResult.items.map((item, i) => (
                <div key={i} className="bg-white rounded-xl p-4 border border-purple-100 shadow-sm hover:shadow-md transition">
                  <h3 className="font-bold text-slate-800">{item.name}</h3>
                  <p className="text-sm text-slate-600 mt-1">{item.description}</p>
                  <div className="flex items-center justify-between mt-3">
                    {item.cost && (
                      <span className="text-xs bg-emerald-100 text-emerald-700 px-2 py-1 rounded-full font-medium">
                        {item.cost}
                      </span>
                    )}
                    {item.link && (
                      <a
                        href={item.link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs text-purple-600 hover:underline font-medium"
                      >
                        Learn more →
                      </a>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Current Need */}
      {need?.current_need && (
        <div className="bg-yellow-50 border border-yellow-200 p-4 rounded-xl mb-6 flex items-center gap-3">
          <Heart className="w-5 h-5 text-yellow-600" />
          <span className="text-sm text-yellow-800">
            Current Need: <strong>{need.current_need}</strong>
          </span>
        </div>
      )}

      {/* Part-time Jobs */}
      <div className="mb-8">
        <h2 className="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">
          <Briefcase className="w-5 h-5 text-blue-600" /> Part-time Jobs ({jobs.length})
        </h2>
        {jobs.length === 0 ? (
          <p className="text-slate-500 text-sm">No part-time jobs listed yet</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {jobs.map((j, i) => (
              <div key={i} className="bg-white p-5 rounded-xl shadow-sm border hover:shadow-md">
                <h3 className="font-bold text-slate-800">{j.title || j.job_title || 'Job'}</h3>
                <p className="text-sm text-slate-500 mt-1">{j.company || 'Local'}</p>
                <p className="text-sm text-emerald-600 font-semibold mt-2">€{j.pay || j.pay_rate || 'N/A'}/hour</p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Books */}
      <div>
        <h2 className="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">
          <BookOpen className="w-5 h-5 text-purple-600" /> Books Library ({books.length})
        </h2>
        {books.length === 0 ? (
          <p className="text-slate-500 text-sm">No books available</p>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {books.map((b, i) => (
              <div key={i} className="bg-white p-4 rounded-xl shadow-sm border text-center">
                <div className="w-20 h-28 bg-gradient-to-br from-purple-500 to-pink-600 rounded-lg mx-auto mb-3 flex items-center justify-center">
                  <BookOpen className="w-8 h-8 text-white" />
                </div>
                <p className="text-sm font-medium text-slate-800 line-clamp-2">{b.title || b.book_name || 'Book'}</p>
                <p className="text-xs text-slate-500 mt-1">{b.author || 'Unknown'}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}