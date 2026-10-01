import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Briefcase, MapPin, DollarSign, Calendar, Search } from 'lucide-react';
import axios from '../../utils/axios';
import Hero from '../../components/Hero';

export default function StudentJobs() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    axios.get('/search/opportunities?type=VACANCY&limit=50')
      .then(res => setJobs(res.data?.results || res.data || []))
      .catch(() => setJobs([]))
      .finally(() => setLoading(false));
  }, []);

  const filtered = jobs.filter(j =>
    !search || j.title?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="p-6">
      <Hero
        title="💼 Jobs & Internships"
        subtitle={`${jobs.length} opportunities found for you`}
        imageUrl="https://images.unsplash.com/photo-1521737604893-d14cc237f11d?w=1600&q=80"
      />

      {/* Search */}
      <div className="bg-white rounded-xl shadow-sm border p-4 mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search jobs..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 border rounded-xl focus:ring-2 focus:ring-blue-500 outline-none"
          />
        </div>
      </div>

      {/* Job Cards */}
      {loading ? (
        <div className="text-center py-12 text-slate-400">Loading...</div>
      ) : filtered.length === 0 ? (
        <div className="bg-white p-12 rounded-xl shadow-sm text-center">
          <Briefcase className="w-14 h-14 text-slate-300 mx-auto mb-3" />
          <p className="text-slate-500">No jobs found</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filtered.map(job => (
            <div key={job.id} className="bg-white p-5 rounded-xl shadow-sm border hover:shadow-md transition">
              <div className="flex justify-between items-start mb-3">
                <div>
                  <h3 className="font-semibold text-lg text-slate-800">{job.title}</h3>
                  <p className="text-sm text-slate-500">{job.type || 'Full Time'}</p>
                </div>
                <span className="px-2 py-1 bg-green-100 text-green-700 text-xs font-semibold rounded-full">
                  {job.status || 'Active'}
                </span>
              </div>
              <p className="text-sm text-slate-600 mb-3 line-clamp-2">
                {job.description || 'No description provided'}
              </p>
              <div className="flex flex-wrap gap-3 text-xs text-slate-500 mb-4">
                <span className="flex items-center gap-1"><MapPin className="w-3 h-3" /> Remote</span>
                <span className="flex items-center gap-1"><DollarSign className="w-3 h-3" /> Competitive</span>
                <span className="flex items-center gap-1"><Calendar className="w-3 h-3" /> Open</span>
              </div>
              <button className="w-full bg-gradient-to-b from-blue-500 to-blue-700 hover:brightness-110 text-white py-2 rounded-lg font-semibold shadow-md">
                Apply Now →
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}