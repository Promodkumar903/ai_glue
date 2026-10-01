import { useEffect, useState } from 'react';
import { FileText, Upload, CheckCircle, Clock, AlertCircle } from 'lucide-react';
import axios from '../../utils/axios';
import Hero from '../../components/Hero';

export default function StudentDocuments() {
  const [docs, setDocs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get('/documents/my').catch(() => ({ data: [] }))
      .then(res => setDocs(Array.isArray(res.data) ? res.data : []))
      .finally(() => setLoading(false));
  }, []);

  const handleUpload = (e) => {
    e.preventDefault();
    alert('Upload feature coming soon!');
  };

  return (
    <div className="p-6">
      <Hero
        title="📄 My Documents"
        subtitle="Manage your certificates and identification"
        imageUrl="https://images.unsplash.com/photo-1568667256549-094345857637?w=1600&q=80"
      />

      {/* Upload Zone */}
      <form onSubmit={handleUpload} className="bg-white p-6 rounded-xl shadow-sm border-2 border-dashed border-blue-200 mb-6 hover:border-blue-400 transition">
        <div className="text-center">
          <Upload className="w-12 h-12 text-blue-400 mx-auto mb-3" />
          <p className="text-slate-600 font-medium">Drag & drop files here</p>
          <p className="text-sm text-slate-400 mt-1">or click to browse</p>
          <button className="mt-4 bg-gradient-to-b from-blue-500 to-blue-700 text-white px-6 py-2 rounded-lg font-semibold shadow-md">
            Upload Document
          </button>
        </div>
      </form>

      {/* Documents List */}
      {loading ? (
        <div className="text-center py-12 text-slate-400">Loading...</div>
      ) : docs.length === 0 ? (
        <div className="bg-white p-12 rounded-xl shadow-sm text-center">
          <FileText className="w-14 h-14 text-slate-300 mx-auto mb-3" />
          <p className="text-slate-500">No documents uploaded yet</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {docs.map((d, i) => (
            <div key={i} className="bg-white p-4 rounded-xl shadow-sm border flex items-center gap-4">
              <div className="p-3 bg-blue-50 rounded-lg">
                <FileText className="w-6 h-6 text-blue-600" />
              </div>
              <div className="flex-1">
                <p className="font-medium text-slate-800">{d.type || 'Document'}</p>
                <p className="text-xs text-slate-500">v{d.version || 1}</p>
              </div>
              {d.verified ? (
                <CheckCircle className="w-5 h-5 text-green-500" />
              ) : (
                <Clock className="w-5 h-5 text-yellow-500" />
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}