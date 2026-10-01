import { useEffect, useState } from 'react';
import { Briefcase, MapPin, DollarSign, Building2, Search } from 'lucide-react';
import axios from '../../utils/axios';
import Hero from '../../components/Hero';

export default function JobSeekerVacancies() {
  const [vacancies, setVacancies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    axios.get('/search/opportunities?type=VACANCY&limit=50')
      .then(res => setVacancies(res.data?.results || res.data || []))
      .catch(() => setVacancies([]))
      .finally(() => setLoading(false));
  }, []);

  const filtered = vacancies.filter(v =>
    !search || v.title?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="p-6">
      <Hero
        title="💼 Job Vacancies"
        subtitle={`${vacancies.length} jobs from verified companies`}
        imageUrl="https://images.unsplash.com/photo-1497366216548-37526070297c?w=1600&q=80"
      />

      <div className="bg-white rounded-xl shadow-sm border p-4 mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search jobs..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 border rounded-xl focus:ring-2 focus:ring-emerald-500 outline-none"
          />
        </div>
      </div>

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
            <div key={job.id} className="bg-white p-5 rounded-xl shadow-sm border hover:shadow-lg transition">
              <div className="flex justify-between items-start mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-lg flex items-center justify-center">
                    <Building2 className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h3 className="font-bold text-lg text-slate-800">{job.title}</h3>
                    <p className="text-sm text-slate-500">Full Time • Verified</p>
                  </div>
                </div>
                <span className="px-2 py-1 bg-green-100 text-green-700 text-xs font-semibold rounded-full">
                  Active
                </span>
              </div>
              <div className="space-y-2 mb-4 text-sm">
                <div className="flex items-center gap-2 text-slate-600">
                  <MapPin className="w-4 h-4" /> Germany • Remote
                </div>
                <div className="flex items-center gap-2 text-slate-600">
                  <DollarSign className="w-4 h-4" /> €50,000 - €80,000/year
                </div>
              </div>
              <button className="w-full bg-gradient-to-b from-emerald-500 to-teal-600 hover:brightness-110 text-white py-2.5 rounded-lg font-semibold shadow-md">
                Apply Now →
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}