import React, { useState } from 'react';
import { PageHeader, Alert, Badge, Button } from '../../components/ui/Components';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function VerifyDocument() {
  const [documentType, setDocumentType] = useState('Passport');
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handleFile = (e) => {
    const f = e.target.files?.[0];
    if (!f) return;
    if (f.size > 5 * 1024 * 1024) {
      setError('File too large (max 5MB)');
      return;
    }
    setFile(f);
    setError('');
    const reader = new FileReader();
    reader.onload = (ev) => setPreview(ev.target.result);
    reader.readAsDataURL(f);
  };

  const handleVerify = async () => {
    if (!file) {
      setError('Please select a file');
      return;
    }
    setLoading(true);
    setError('');
    setResult(null);

    const formData = new FormData();
    formData.append('document_type', documentType);
    formData.append('file', file);

    try {
      const res = await fetch(`${API_BASE}/documents/upload-and-verify`, {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Verification failed');
      setResult(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6">
      <PageHeader
        icon="🔍"
        title="AI Document Verification"
        subtitle="Upload your document — AI will verify and extract information"
        image="https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=1600&q=80"
      />

      {error && <Alert type="danger" onClose={() => setError('')}>{error}</Alert>}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Left: Upload */}
        <div className="bg-white rounded-xl shadow p-6">
          <h3 className="font-bold mb-4">📤 Upload Document</h3>

          <label className="block text-sm font-medium text-gray-700 mb-2">Document Type</label>
          <select
            value={documentType}
            onChange={(e) => setDocumentType(e.target.value)}
            className="w-full border rounded-lg px-3 py-2 mb-4"
          >
            <option>Passport</option>
            <option>Marksheet</option>
            <option>IELTS Score</option>
            <option>TOEFL Score</option>
            <option>Bank Statement</option>
            <option>Admission Letter</option>
            <option>Visa</option>
          </select>

          <label className="block text-sm font-medium text-gray-700 mb-2">Choose File (Image)</label>
          <input
            type="file"
            accept="image/*"
            onChange={handleFile}
            className="w-full border-2 border-dashed border-gray-300 rounded-lg p-4 cursor-pointer hover:border-blue-500 mb-4"
          />

          {preview && (
            <div className="mb-4">
              <img src={preview} alt="Preview" className="max-h-64 rounded-lg border" />
            </div>
          )}

          <Button onClick={handleVerify} loading={loading} fullWidth disabled={!file}>
            🔍 Verify with AI
          </Button>
        </div>

        {/* Right: Result */}
        <div className="bg-white rounded-xl shadow p-6">
          <h3 className="font-bold mb-4">📋 Verification Result</h3>

          {!result && !loading && (
            <div className="text-center py-12 text-gray-400">
              Upload a document to see AI verification
            </div>
          )}

          {loading && (
            <div className="text-center py-12 text-gray-400">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mb-3"></div>
              <p>AI analyzing document...</p>
            </div>
          )}

          {result && (
            <div className="space-y-4">
              <div className={`p-4 rounded-lg ${result.is_valid ? 'bg-emerald-50 border border-emerald-300' : 'bg-red-50 border border-red-300'}`}>
                <div className="flex items-center gap-2">
                  <span className="text-2xl">{result.is_valid ? '✅' : '❌'}</span>
                  <span className={`font-bold ${result.is_valid ? 'text-emerald-700' : 'text-red-700'}`}>
                    {result.is_valid ? 'Document Valid' : 'Issues Found'}
                  </span>
                </div>
              </div>

              {result.extracted_data && (
                <div>
                  <h4 className="font-semibold text-gray-700 mb-2">📝 Extracted Data</h4>
                  <div className="space-y-2 text-sm">
                    {Object.entries(result.extracted_data).map(([k, v]) => (
                      v ? (
                        <div key={k} className="flex justify-between py-1 border-b border-gray-100">
                          <span className="text-gray-500 capitalize">{k.replace(/_/g, ' ')}</span>
                          <span className="font-medium text-gray-800">{v}</span>
                        </div>
                      ) : null
                    ))}
                  </div>
                </div>
              )}

              {result.issues?.length > 0 && (
                <div>
                  <h4 className="font-semibold text-red-700 mb-2">⚠️ Issues</h4>
                  <ul className="list-disc list-inside text-sm text-red-600 space-y-1">
                    {result.issues.map((iss, i) => <li key={i}>{iss}</li>)}
                  </ul>
                </div>
              )}

              {result.ai_note && (
                <div className="p-3 bg-purple-50 border border-purple-200 rounded-lg">
                  <p className="text-xs text-purple-800">✨ {result.ai_note}</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}