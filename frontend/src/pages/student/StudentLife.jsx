import { useEffect, useState } from 'react';
import { Briefcase, BookOpen, Heart, Loader } from 'lucide-react';
import axios from '../../utils/axios';
import Hero from '../../components/Hero';

export default function StudentLife() {
  const [jobs, setJobs] = useState([]);
  const [books, setBooks] = useState([]);
  const [need, setNeed] = useState(null);
  const [loading, setLoading] = useState(true);

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

  if (loading) return <div className="text-center py-12 text-slate-400">Loading...</div>;

  return (
    <div className="p-6">
      <Hero
        title="❤️ Student Life"
        subtitle="Part-time jobs, books, and daily needs"
        imageUrl="https://images.unsplash.com/photo-1523050854058-8df90110c9f1?w=1600&q=80"
      />

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
                <h3 className="font-bold text-slate-800">{j.title || 'Job'}</h3>
                <p className="text-sm text-slate-500 mt-1">{j.company || 'Local'}</p>
                <p className="text-sm text-emerald-600 font-semibold mt-2">€{j.pay || 'N/A'}/hour</p>
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
                <p className="text-sm font-medium text-slate-800 line-clamp-2">{b.title || 'Book'}</p>
                <p className="text-xs text-slate-500 mt-1">{b.author || 'Unknown'}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}