import { useEffect, useState } from 'react';
import { BookOpen } from 'lucide-react';
import axios from '../../utils/axios';
import Hero from '../../components/Hero';

export default function StudentBooks() {
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get('/student-life/books').catch(() => ({ data: [] }))
      .then(res => setBooks(Array.isArray(res.data) ? res.data : []))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="p-6">
      <Hero
        title="📚 Books Library"
        subtitle="Semester books and study material"
        imageUrl="https://images.unsplash.com/photo-1512820790803-83ca734da794?w=1600&q=80"
      />

      {loading ? (
        <div className="text-center py-12 text-slate-400">Loading...</div>
      ) : books.length === 0 ? (
        <div className="bg-white p-12 rounded-xl shadow-sm text-center">
          <BookOpen className="w-14 h-14 text-slate-300 mx-auto mb-3" />
          <p className="text-slate-500">No books in library yet</p>
        </div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {books.map((b, i) => (
            <div key={i} className="bg-white p-4 rounded-xl shadow-sm border text-center">
              <div className="w-20 h-28 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg mx-auto mb-3 flex items-center justify-center">
                <BookOpen className="w-8 h-8 text-white" />
              </div>
              <p className="font-medium text-sm text-slate-800 line-clamp-2">{b.title || 'Book'}</p>
              <p className="text-xs text-slate-500 mt-1">{b.author || 'Unknown'}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}