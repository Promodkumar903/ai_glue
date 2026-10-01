import { useEffect, useState } from 'react';
import axios from '../utils/axios';
import { Loader, AlertCircle, FileText, ArrowLeft } from 'lucide-react';
import { Link } from 'react-router-dom';
import Hero from '../components/Hero';

export default function SubPage({ title, description, endpoint, columns, backPath, imageUrl }) {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await axios.get(endpoint);
        let result = res.data;
        if (Array.isArray(result)) setData(result);
        else if (result?.items) setData(result.items);
        else if (result?.results) setData(result.results);
        else if (result?.agents) setData(result.agents);
        else if (result?.clients) setData(result.clients);
        else if (result?.notifications) setData(result.notifications);
        else if (typeof result === 'object') setData([result]);
        else setData([]);
      } catch (e) {
        const errDetail = e.response?.data?.detail;
        let errMsg = 'Failed to load data';
        if (typeof errDetail === 'string') errMsg = errDetail;
        else if (Array.isArray(errDetail)) errMsg = errDetail.map(i => i.msg).join(', ');
        setError(errMsg);
        setData([]);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [endpoint]);

  return (
    <div>
      {backPath && (
        <Link to={backPath} className="inline-flex items-center gap-2 text-sm text-slate-500 hover:text-blue-600 mb-4">
          <ArrowLeft className="w-4 h-4" /> Back to Dashboard
        </Link>
      )}

      {imageUrl && <Hero title={title} subtitle={description} imageUrl={imageUrl} />}

      {!imageUrl && (
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-slate-800">{title}</h1>
          <p className="text-sm text-slate-500 mt-1">{description}</p>
        </div>
      )}

      {loading && (
        <div className="bg-white p-12 rounded-xl shadow-sm border text-center">
          <Loader className="w-8 h-8 animate-spin text-blue-500 mx-auto mb-3" />
          <span className="text-slate-500">Loading...</span>
        </div>
      )}

      {!loading && error && (
        <div className="bg-red-50 border border-red-200 p-5 rounded-xl flex items-center gap-3 text-red-700">
          <AlertCircle className="w-5 h-5" />
          <span>{error}</span>
        </div>
      )}

      {!loading && !error && data.length === 0 && (
        <div className="bg-white p-12 rounded-xl shadow-sm border text-center">
          <FileText className="w-14 h-14 text-slate-300 mx-auto mb-3" />
          <p className="text-slate-600 font-medium">No data available yet</p>
          <p className="text-sm text-slate-400 mt-1">Data will appear here once available</p>
        </div>
      )}

      {!loading && !error && data.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-100 bg-slate-50">
            <h2 className="font-semibold text-slate-700">Total Records: {data.length}</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-slate-50">
                <tr>
                  {columns.map(col => (
                    <th key={col.key} className="px-6 py-3 text-left font-semibold text-slate-600 text-xs uppercase">
                      {col.label}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {data.map((row, i) => (
                  <tr key={i} className="border-b last:border-0 hover:bg-slate-50">
                    {columns.map(col => (
                      <td key={col.key} className="px-6 py-3 text-slate-700">
                        {col.render ? col.render(row) : (row[col.key] ?? '-')}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}