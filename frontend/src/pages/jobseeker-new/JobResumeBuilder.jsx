import React, { useState, useEffect } from 'react';
import jsPDF from 'jspdf';
import { PageHeader, Alert, Badge, Button } from '../../components/ui/Components';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const COUNTRIES = [
  { id: 'Germany', label: '🇩🇪 Germany' },
  { id: 'USA', label: '🇺🇸 USA' },
  { id: 'UK', label: '🇬🇧 UK' },
  { id: 'Canada', label: '🇨🇦 Canada' },
  { id: 'UAE', label: '🇦🇪 UAE (Gulf)' },
  { id: 'Japan', label: '🇯🇵 Japan' },
];

const PHOTO_COUNTRIES = ['Germany', 'UAE', 'Japan'];

export default function JobResumeBuilder() {
  const [country, setCountry] = useState('Germany');
  const [targetRole, setTargetRole] = useState('');
  const [targetCompany, setTargetCompany] = useState('');
  const [file, setFile] = useState(null);
  const [photo, setPhoto] = useState(null);
  const [photoPreview, setPhotoPreview] = useState('');
  const [documentTypes, setDocumentTypes] = useState([]);
  const [selectedDocs, setSelectedDocs] = useState({});
  const [loading, setLoading] = useState(false);
  const [loadingDocs, setLoadingDocs] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('');
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    setLoadingDocs(true);
    setResult(null);
    fetch(`${API_BASE}/ai/job-document-types/${country}`)
      .then((r) => r.json())
      .then((d) => {
        const docs = d.documents || [];
        setDocumentTypes(docs);
        const initial = {};
        docs.forEach((doc) => { initial[doc.id] = true; });
        setSelectedDocs(initial);
      })
      .catch(() => setDocumentTypes([]))
      .finally(() => setLoadingDocs(false));
  }, [country]);

  const handleFile = (e) => {
    const f = e.target.files?.[0];
    if (!f) return;
    if (f.size > 5 * 1024 * 1024) { setError('File too large (max 5MB)'); return; }
    setFile(f);
    setError('');
    setResult(null);
  };

  const handlePhoto = (e) => {
    const f = e.target.files?.[0];
    if (!f) return;
    if (f.size > 2 * 1024 * 1024) { setError('Photo too large (max 2MB)'); return; }
    setPhoto(f);
    setError('');
    const reader = new FileReader();
    reader.onload = (ev) => setPhotoPreview(ev.target.result);
    reader.readAsDataURL(f);
  };

  const toggleDoc = (id) => {
    setSelectedDocs((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const handleGenerate = async () => {
    if (!file) { setError('Please select a resume file'); return; }
    const selectedIds = Object.keys(selectedDocs).filter((k) => selectedDocs[k]);
    if (selectedIds.length === 0) { setError('Please select at least one document'); return; }

    setLoading(true);
    setError('');
    setResult(null);

    const formData = new FormData();
    formData.append('country', country);
    formData.append('document_ids', selectedIds.join(','));
    formData.append('target_role', targetRole);
    formData.append('target_company', targetCompany);
    formData.append('file', file);
    if (photo) formData.append('photo', photo);

    try {
      const res = await fetch(`${API_BASE}/ai/generate-job-documents`, {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Generation failed');
      setResult(data);
      const firstDoc = Object.keys(data.documents || {})[0];
      setActiveTab(firstDoc || '');
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = () => {
    const text = result?.documents?.[activeTab] || '';
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownloadTXT = () => {
    const text = result?.documents?.[activeTab] || '';
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${activeTab}-${country.toLowerCase()}-${Date.now()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleDownloadPDF = () => {
    const doc = new jsPDF('p', 'mm', 'a4');
    const pageWidth = 210;
    const pageHeight = 297;
    const margin = 15;
    let yPos = margin;

    if (result?.photo_b64) {
      try {
        const imgData = `data:image/jpeg;base64,${result.photo_b64}`;
        doc.addImage(imgData, 'JPEG', margin, yPos, 30, 40);
        yPos += 45;
      } catch (e) { console.warn('Photo embed failed:', e); }
    }

    doc.setFontSize(16);
    doc.setFont('helvetica', 'bold');
    const docName = documentTypes.find((d) => d.id === activeTab)?.name || activeTab;
    doc.text(docName, margin, yPos);
    yPos += 10;

    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    const content = result?.documents?.[activeTab] || '';
    const lines = doc.splitTextToSize(content, pageWidth - margin * 2);

    lines.forEach((line) => {
      if (yPos > pageHeight - margin) { doc.addPage(); yPos = margin; }
      doc.text(line, margin, yPos);
      yPos += 5;
    });

    doc.save(`${activeTab}-${country.toLowerCase()}-${Date.now()}.pdf`);
  };

  const needsPhoto = PHOTO_COUNTRIES.includes(country);

  return (
    <div className="p-6">
      <PageHeader
        icon="💼"
        title="AI Job Resume Builder"
        subtitle="Country-specific job resume + cover letter — ATS-friendly"
        image="https://images.unsplash.com/photo-1586281380349-632531db7ed4?w=1600&q=80"
      />

      {error && <Alert type="danger" onClose={() => setError('')}>{error}</Alert>}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow p-6">
          <h3 className="font-bold mb-4">📤 Upload & Configure</h3>

          <label className="block text-sm font-medium text-gray-700 mb-2">Target Country</label>
          <select
            value={country}
            onChange={(e) => setCountry(e.target.value)}
            className="w-full border rounded-lg px-3 py-2 mb-4"
          >
            {COUNTRIES.map((c) => (
              <option key={c.id} value={c.id}>{c.label}</option>
            ))}
          </select>

          <label className="block text-sm font-medium text-gray-700 mb-2">
            Documents Needed ({country})
          </label>
          {loadingDocs ? (
            <p className="text-sm text-gray-400 mb-4">Loading documents...</p>
          ) : (
            <div className="space-y-2 mb-4">
              {documentTypes.map((doc) => (
                <label key={doc.id} className="flex items-start gap-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50">
                  <input
                    type="checkbox"
                    checked={selectedDocs[doc.id] || false}
                    onChange={() => toggleDoc(doc.id)}
                    className="mt-1 w-4 h-4"
                  />
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-sm text-gray-800">{doc.name}</span>
                      {doc.required && <Badge color="red">Required</Badge>}
                    </div>
                    <p className="text-xs text-gray-500 mt-0.5">Language: {doc.lang}</p>
                  </div>
                </label>
              ))}
            </div>
          )}

          <label className="block text-sm font-medium text-gray-700 mb-2">Target Role (optional)</label>
          <input
            type="text"
            value={targetRole}
            onChange={(e) => setTargetRole(e.target.value)}
            placeholder="e.g. Senior Python Developer"
            className="w-full border rounded-lg px-3 py-2 mb-4"
          />

          <label className="block text-sm font-medium text-gray-700 mb-2">Target Company (optional)</label>
          <input
            type="text"
            value={targetCompany}
            onChange={(e) => setTargetCompany(e.target.value)}
            placeholder="e.g. Google, Siemens, KOC"
            className="w-full border rounded-lg px-3 py-2 mb-4"
          />

          <label className="block text-sm font-medium text-gray-700 mb-2">
            Upload Current Resume (PDF, DOCX, TXT)
          </label>
          <input
            type="file"
            accept=".pdf,.docx,.txt"
            onChange={handleFile}
            className="w-full border-2 border-dashed border-gray-300 rounded-lg p-4 cursor-pointer hover:border-blue-500 mb-4"
          />

          {file && (
            <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg text-sm">
              📎 {file.name} ({(file.size / 1024).toFixed(1)} KB)
            </div>
          )}

          {needsPhoto && (
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Passport Photo (optional — {country} needs photo)
              </label>
              <input
                type="file"
                accept="image/*"
                onChange={handlePhoto}
                className="w-full border-2 border-dashed border-gray-300 rounded-lg p-3 cursor-pointer hover:border-blue-500"
              />
              {photoPreview && (
                <div className="mt-2 flex items-center gap-3">
                  <img src={photoPreview} alt="Photo" className="w-20 h-24 object-cover rounded border-2 border-gray-300" />
                  <button
                    type="button"
                    onClick={() => { setPhoto(null); setPhotoPreview(''); }}
                    className="text-xs text-red-600 hover:text-red-700"
                  >
                    ✕ Remove
                  </button>
                </div>
              )}
            </div>
          )}

          <Button onClick={handleGenerate} loading={loading} fullWidth disabled={!file}>
            ✨ Generate Job Documents
          </Button>
        </div>

        <div className="bg-white rounded-xl shadow p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="font-bold">📋 Generated Documents</h3>
            {result && (
              <div className="flex gap-2">
                <button
                  onClick={handleCopy}
                  className="text-xs bg-gray-100 hover:bg-gray-200 px-3 py-1.5 rounded font-medium"
                >
                  {copied ? '✓ Copied' : '📋 Copy'}
                </button>
                <button
                  onClick={handleDownloadTXT}
                  className="text-xs bg-blue-600 hover:bg-blue-700 text-white px-3 py-1.5 rounded font-medium"
                >
                  ⬇ TXT
                </button>
                <button
                  onClick={handleDownloadPDF}
                  className="text-xs bg-emerald-600 hover:bg-emerald-700 text-white px-3 py-1.5 rounded font-medium"
                >
                  ⬇ PDF
                </button>
              </div>
            )}
          </div>

          {!result && !loading && (
            <div className="text-center py-12 text-gray-400">
              Select country, choose documents, upload resume → AI will generate job-ready documents
            </div>
          )}

          {loading && (
            <div className="text-center py-12 text-gray-400">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mb-3"></div>
              <p>AI generating job documents...</p>
              <p className="text-xs mt-2">This may take 20-30 seconds</p>
            </div>
          )}

          {result && (
            <div>
              <div className="flex gap-1 mb-3 border-b overflow-x-auto">
                {Object.keys(result.documents || {}).map((docId) => {
                  const docMeta = documentTypes.find((d) => d.id === docId);
                  return (
                    <button
                      key={docId}
                      onClick={() => setActiveTab(docId)}
                      className={`px-3 py-2 text-xs font-medium border-b-2 whitespace-nowrap ${
                        activeTab === docId
                          ? 'border-blue-600 text-blue-600'
                          : 'border-transparent text-gray-500 hover:text-gray-700'
                      }`}
                    >
                      {docMeta?.name || docId}
                    </button>
                  );
                })}
              </div>

              <div className="bg-gray-50 rounded-lg p-4 max-h-[500px] overflow-y-auto">
                <pre className="text-xs whitespace-pre-wrap font-mono text-gray-800">
                  {result.documents?.[activeTab] || ''}
                </pre>
              </div>

              {result.verification && (
                <div className={`mt-3 p-3 rounded-lg text-xs ${
                  result.verification.status === 'PASS'
                    ? 'bg-emerald-50 border border-emerald-200 text-emerald-800'
                    : result.verification.status === 'PASS_WITH_WARNINGS'
                    ? 'bg-amber-50 border border-amber-200 text-amber-800'
                    : 'bg-red-50 border border-red-200 text-red-800'
                }`}>
                  <strong>Verification: {result.verification.status}</strong>
                  {' — '}
                  {result.verification.errorCount || 0} errors, {result.verification.warningCount || 0} warnings
                </div>
              )}

              <div className="mt-3 p-3 bg-amber-50 border border-amber-200 rounded-lg text-xs text-amber-800">
                ⚡ <strong>AI-generated</strong> — review and fill [X] placeholders with your real numbers.
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}