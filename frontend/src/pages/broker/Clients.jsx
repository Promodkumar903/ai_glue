import { useEffect, useState } from 'react';
import { Building2 } from 'lucide-react';
import axios from '../../utils/axios';
import Hero from '../../components/Hero';

export default function BrokerClients() {
  const [clients, setClients] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get('/broker/clients').catch(() => ({ data: { clients: [] } }))
      .then(res => setClients(res.data?.clients || []))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="p-6">
      <Hero
        title="🏢 Client Distribution"
        subtitle="Applications by client organization"
        imageUrl="https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=1600&q=80"
      />

      {loading ? (
        <div className="text-center py-12 text-slate-400">Loading...</div>
      ) : clients.length === 0 ? (
        <div className="bg-white p-12 rounded-xl shadow-sm text-center">
          <Building2 className="w-14 h-14 text-slate-300 mx-auto mb-3" />
          <p className="text-slate-500">No client data yet</p>
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
          <table className="w-full">
            <thead className="bg-slate-50 border-b">
              <tr>
                <th className="text-left px-6 py-3 text-xs font-semibold text-slate-600 uppercase">Client</th>
                <th className="text-left px-6 py-3 text-xs font-semibold text-slate-600 uppercase">Applications</th>
                <th className="text-left px-6 py-3 text-xs font-semibold text-slate-600 uppercase">Shortlisted</th>
                <th className="text-left px-6 py-3 text-xs font-semibold text-slate-600 uppercase">Hired</th>
              </tr>
            </thead>
            <tbody>
              {clients.map((c, i) => (
                <tr key={i} className="border-b hover:bg-slate-50">
                  <td className="px-6 py-4 font-medium text-slate-800">{c.client_name}</td>
                  <td className="px-6 py-4">{c.total_apps}</td>
                  <td className="px-6 py-4 text-green-600">{c.shortlisted}</td>
                  <td className="px-6 py-4 text-purple-600">{c.hired}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}