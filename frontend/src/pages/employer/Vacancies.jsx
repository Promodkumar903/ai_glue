import { useEffect, useState } from 'react';
import { Briefcase, Plus } from 'lucide-react';
import axios from '../../utils/axios';
import Hero from '../../components/Hero';

export default function EmployerVacancies() {
  const [vacancies, setVacancies] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get('/company/vacancy').catch(() => ({ data: [] }))
      .then(res => setVacancies(Array.isArray(res.data) ? res.data : []))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="p-6">
      <Hero
        title="💼 My Vacancies"
        subtitle="Manage your job openings"
        imageUrl="https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=1600&q=80"
      >
        <button className="bg-white text-blue-700 px-4 py-2 rounded-lg font-semibold shadow-md flex items-center gap-2 hover:bg-blue-50">
          <Plus className="w-4 h-4" /> Post New Vacancy
        </button>
      </Hero>

      {loading ? (
        <div className="text-center py-12 text-slate-400">Loading...</div>
      ) : vacancies.length === 0 ? (
        <div className="bg-white p-12 rounded-xl shadow-sm text-center">
          <Briefcase className="w-14 h-14 text-slate-300 mx-auto mb-3" />
          <p className="text-slate-500">No vacancies yet</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {vacancies.map(v => (
            <div key={v.id} className="bg-white p-5 rounded-xl shadow-sm border">
              <div className="flex justify-between mb-3">
                <div>
                  <h3 className="font-semibold text-slate-800">{v.title}</h3>
                  <p className="text-sm text-slate-500">{v.type}</p>
                </div>
                <span className={`px-3 py-1 text-xs font-semibold rounded-full ${
                  v.status === 'ACTIVE' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'
                }`}>
                  {v.status}
                </span>
              </div>
              <p className="text-sm text-slate-600 mb-4 line-clamp-2">{v.description || 'No description'}</p>
              <div className="flex gap-2">
                <button className="flex-1 bg-blue-600 text-white py-2 rounded-lg text-sm font-semibold">Edit</button>
                <button className="flex-1 border border-red-300 text-red-600 py-2 rounded-lg text-sm font-semibold">Close</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}