import React, { useState, useEffect } from 'react';
import { Search, GraduationCap, Briefcase, Building2, Award, ArrowRight, Sparkles } from 'lucide-react';

const DEMO_QUERIES = [
  {
    q: 'Free CS Master in Germany',
    icon: GraduationCap,
    results: [
      { name: 'TU Munich', detail: 'MS Computer Science · $0/yr', tag: 'FREE' },
      { name: 'RWTH Aachen', detail: 'MS Data Science · $500/yr', tag: 'FREE' },
      { name: 'Heidelberg University', detail: 'MS Molecular Bio · $0/yr', tag: 'FREE' },
    ],
    count: '392 universities found',
  },
  {
    q: 'Nursing jobs Germany visa',
    icon: Briefcase,
    results: [
      { name: 'Nurse @ Charité Berlin', detail: '€3,500/mo · Visa sponsored', tag: 'HIRING' },
      { name: 'Nurse @ Munich Clinic', detail: '€3,200/mo · Accommodation', tag: 'HIRING' },
      { name: 'Nurse @ Frankfurt Hospital', detail: '€3,400/mo · 18-mo work', tag: 'HIRING' },
    ],
    count: '47 verified jobs found',
  },
  {
    q: 'Top scholarships for Indian students',
    icon: Award,
    results: [
      { name: 'DAAD Scholarship', detail: 'Germany · €12K · All subjects', tag: 'SCHOLARSHIP' },
      { name: 'Chevening', detail: 'UK · £35K · Full tuition', tag: 'SCHOLARSHIP' },
      { name: 'Fulbright', detail: 'USA · $40K · Masters/PhD', tag: 'SCHOLARSHIP' },
    ],
    count: '23 scholarships available',
  },
  {
    q: 'Google SDE salary band',
    icon: Building2,
    results: [
      { name: 'Entry (L3)', detail: '₹25L - ₹40L · India', tag: 'SALARY' },
      { name: 'Mid (L4)', detail: '₹45L - ₹70L · India', tag: 'SALARY' },
      { name: 'Senior (L5)', detail: '₹75L - ₹120L · India', tag: 'SALARY' },
    ],
    count: 'Salary bands verified',
  },
];

export default function LiveSearchPreview() {
  const [idx, setIdx] = useState(0);
  const [typed, setTyped] = useState('');
  const [showResults, setShowResults] = useState(false);

  // Type animation
  useEffect(() => {
    const q = DEMO_QUERIES[idx].q;
    setTyped('');
    setShowResults(false);
    let i = 0;
    const typeTimer = setInterval(() => {
      if (i <= q.length) {
        setTyped(q.slice(0, i));
        i++;
      } else {
        clearInterval(typeTimer);
        setTimeout(() => setShowResults(true), 400);
      }
    }, 50);
    return () => clearInterval(typeTimer);
  }, [idx]);

  // Auto-advance
  useEffect(() => {
    const t = setTimeout(() => {
      setIdx(i => (i + 1) % DEMO_QUERIES.length);
    }, 6000);
    return () => clearTimeout(t);
  }, [idx]);

  const current = DEMO_QUERIES[idx];
  const QueryIcon = current.icon;

  return (
    <section className="py-12 px-6 bg-gradient-to-b from-slate-950 via-purple-950/20 to-slate-950">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <div className="inline-block px-4 py-1.5 mb-4 rounded-full bg-purple-500/10 border border-purple-500/30 text-sm text-purple-300">
            <Sparkles className="w-3 h-3 inline mr-2" />
            Try Our AI Search
          </div>
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Ask. <span className="bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">Discover.</span> Apply.
          </h2>
        </div>

        {/* Fake browser window */}
        <div className="rounded-2xl bg-slate-900 border border-white/20 overflow-hidden shadow-2xl">
          {/* Browser bar */}
          <div className="px-4 py-3 bg-slate-950 border-b border-white/10 flex items-center gap-2">
            <div className="flex gap-1.5">
              <div className="w-3 h-3 rounded-full bg-red-500/80" />
              <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
              <div className="w-3 h-3 rounded-full bg-green-500/80" />
            </div>
            <div className="ml-4 text-xs text-gray-500">aiglueagent.com/search</div>
          </div>

          {/* Search bar */}
          <div className="p-4 border-b border-white/10">
            <div className="flex items-center gap-3 px-4 py-3 rounded-xl bg-white/5 border border-purple-500/40">
              <QueryIcon className="w-5 h-5 text-purple-400" />
              <span className="text-white flex-1">
                {typed}
                <span className="inline-block w-0.5 h-5 bg-purple-400 animate-pulse ml-0.5 align-middle" />
              </span>
            </div>
            {showResults && (
              <div className="mt-3 text-xs text-purple-400 flex items-center gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />
                {current.count}
              </div>
            )}
          </div>

          {/* Results */}
          <div className="p-4 min-h-[200px]">
            {showResults ? (
              <div className="space-y-3">
                {current.results.map((r, i) => (
                  <div
                    key={i}
                    className="p-4 rounded-xl bg-white/5 border border-white/10 hover:border-purple-500/40 transition flex items-center justify-between"
                    style={{ animation: `slideIn 0.4s ${i * 0.1}s both` }}
                  >
                    <div className="flex items-center gap-4">
                      <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-purple-500/30 to-pink-500/30 flex items-center justify-center">
                        <QueryIcon className="w-5 h-5 text-purple-300" />
                      </div>
                      <div>
                        <div className="font-semibold">{r.name}</div>
                        <div className="text-sm text-gray-400">{r.detail}</div>
                      </div>
                    </div>
                    <div className="px-3 py-1 rounded-full bg-purple-500/20 text-purple-300 text-xs font-semibold">
                      {r.tag}
                    </div>
                  </div>
                ))}
                <div className="text-center pt-4">
                  <button className="px-6 py-3 rounded-xl bg-gradient-to-r from-purple-500 to-pink-500 font-semibold text-sm inline-flex items-center gap-2">
                    Login to see all results <ArrowRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ) : (
              <div className="flex items-center justify-center h-full text-gray-600">
                <Search className="w-12 h-12" />
              </div>
            )}
          </div>
        </div>
      </div>

      <style>{`
        @keyframes slideIn {
          from { opacity: 0; transform: translateX(-20px); }
          to { opacity: 1; transform: translateX(0); }
        }
      `}</style>
    </section>
  );
}