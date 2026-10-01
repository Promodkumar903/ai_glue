import { useState } from 'react';
import { Upload, Search, Sparkles, FileText } from 'lucide-react';
import axios from '../utils/axios';
import Hero from '../components/Hero';

export default function ResumeSearch() {
  const [resumeText, setResumeText] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    if (!resumeText.trim()) return;
    setLoading(true);
    try {
      const keywords = resumeText.split(/\s+/).filter(w => w.length > 3).slice(0, 5).join(' ');
      const res = await axios.get(`/search/opportunities?q=${encodeURIComponent(keywords)}&limit=20`);
      setResults(res.data?.results || res.data || []);
    } catch { alert('Search failed'); }
    finally { setLoading(false); }
  };

  return (
    <div className="p-6">
      <Hero
        title="✨ AI Resume Search"
        subtitle="Paste your resume and let AI find matching jobs"
        imageUrl="https://images.unsplash.com/photo-1586281380349-632531db7ed4?w=1600&q=80"
      />

      <div className="bg-white p-6 rounded-xl shadow-sm border mb-6">
        <h3 className="font-semibold text-slate-700 mb-3 flex items-center gap-2">
          <Upload className="w-5 h-5" /> Paste Your Resume
        </h3>
        <textarea
          value={resumeText}
          onChange={e => setResumeText(e.target.value)}
          placeholder="Paste your resume text here... (Skills, Experience, Education)"
          className="w-full h-48 p-4 border rounded-xl focus:ring-2 focus:ring-purple-500 outline-none resize-none font-mono text-sm"
        />
        <button onClick={handleSearch} disabled={loading || !resumeText.trim()}
          className="mt-4 bg-gradient-to-r from-blue-500 to-purple-600 text-white px-8 py-3 rounded-xl font-semibold shadow-lg flex items-center gap-2 hover:brightness-110 disabled:opacity-50">
          <Sparkles className="w-5 h-5" /> {loading ? 'Searching...' : 'Auto-Search Jobs'}
        </button>
      </div>

      {results.length > 0 && (
        <div>
          <h2 className="text-xl font-bold text-slate-800 mb-4">🎯 {results.length} Matching Jobs</h2>
          <div className="space-y-3">
            {results.map((r, i) => (
              <div key={i} className="bg-white p-4 rounded-xl shadow-sm border flex justify-between items-center hover:shadow-md">
                <div className="flex items-center gap-3">
                  <FileText className="w-8 h-8 text-blue-600" />
                  <div>
                    <h3 className="font-semibold text-slate-800">{r.title}</h3>
                    <p className="text-xs text-slate-500">{r.type}</p>
                  </div>
                </div>
                <button className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-semibold">Apply →</button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}