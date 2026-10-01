import { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import axios from '../utils/axios';
import { Search as SearchIcon, Loader, FileText, Building2, Briefcase, GraduationCap } from 'lucide-react';

export default function Search() {
  const [searchParams] = useSearchParams();
  const query = searchParams.get('q') || '';
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState('ALL');

  useEffect(() => {
    const fetchResults = async () => {
      if (!query) return;
      setLoading(true);
      try {
        // Opportunities search (Jobs, Programs, Scholarships)
        const res = await axios.get(`/search/opportunities?q=${encodeURIComponent(query)}&limit=50`)
          .catch(() => ({ data: { results: [] } }));

        let items = [];
        if (Array.isArray(res.data)) items = res.data;
        else if (res.data?.results) items = res.data.results;
        else if (res.data?.items) items = res.data.items;

        setResults(items);
      } catch (e) {
        console.error('Search error:', e);
        setResults([]);
      } finally {
        setLoading(false);
      }
    };
    fetchResults();
  }, [query]);

  const filtered = filter === 'ALL'
    ? results
    : results.filter(r => r.type === filter);

  const getTypeIcon = (type) => {
    switch (type) {
      case 'VACANCY': return <Briefcase className="w-4 h-4" />;
      case 'PROGRAMME': return <GraduationCap className="w-4 h-4" />;
      case 'SCHOLARSHIP': return <FileText className="w-4 h-4" />;
      default: return <Building2 className="w-4 h-4" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
          <SearchIcon className="w-6 h-6 text-blue-600" />
          Search Results
        </h1>
        <p className="text-sm text-slate-500 mt-1">
          Showing results for: <span className="font-semibold text-slate-700">"{query}"</span>
        </p>
      </div>

      {/* Filter Tabs */}
      <div className="flex gap-2 flex-wrap">
        {['ALL', 'VACANCY', 'PROGRAMME', 'SCHOLARSHIP'].map(f => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
              filter === f
                ? 'bg-blue-600 text-white shadow-md'
                : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'
            }`}
          >
            {f === 'ALL' ? 'All' : f.charAt(0) + f.slice(1).toLowerCase()}
          </button>
        ))}
      </div>

      {/* Loading */}
      {loading && (
        <div className="bg-white p-12 rounded-xl shadow-sm border text-center">
          <Loader className="w-8 h-8 animate-spin text-blue-500 mx-auto mb-2" />
          <p className="text-slate-500">Searching...</p>
        </div>
      )}

      {/* Empty */}
      {!loading && filtered.length === 0 && (
        <div className="bg-white p-12 rounded-xl shadow-sm border text-center">
          <FileText className="w-14 h-14 text-slate-300 mx-auto mb-3" />
          <p className="text-slate-600 font-medium">No results found</p>
          <p className="text-sm text-slate-400 mt-1">Try different keywords</p>
        </div>
      )}

      {/* Results */}
      {!loading && filtered.length > 0 && (
        <div className="space-y-3">
          {filtered.map((r, i) => (
            <div key={i} className="bg-white p-5 rounded-xl shadow-sm border border-slate-100 hover:shadow-md transition">
              <div className="flex items-start gap-4">
                <div className="p-3 bg-blue-50 rounded-lg text-blue-600">
                  {getTypeIcon(r.type)}
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-slate-800">{r.title || 'Untitled'}</h3>
                  <p className="text-sm text-slate-500 mt-1">
                    Type: <span className="font-medium">{r.type || 'Unknown'}</span>
                    {r.status && <> • Status: <span className="font-medium">{r.status}</span></>}
                  </p>
                  {r.description && (
                    <p className="text-sm text-slate-600 mt-2 line-clamp-2">
                      {r.description.substring(0, 150)}...
                    </p>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}