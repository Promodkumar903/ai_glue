import React, { useState, useEffect, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Card, Badge, Alert, Button } from '../../components/ui/Components';
import { crmAPI } from '../../services/api';

const STAGES = ['NEW', 'CONTACTED', 'INTERESTED', 'PROFILE_READY', 'DOCUMENTS', 'APPLICATION', 'OFFER', 'VISA', 'ENROLLED', 'LOST'];
const DOC_TYPES = ['Passport', 'Marksheet 10th', 'Marksheet 12th', 'Degree', 'IELTS/TOEFL', 'SOP', 'LOR', 'Bank Statement', 'Offer Letter', 'Visa'];

export default function LeadDetail() {
  const { id } = useParams();
  const [lead, setLead] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [noteText, setNoteText] = useState('');
  const [newDocType, setNewDocType] = useState('Passport');
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef(null);

  const load = () => {
    setLoading(true);
    crmAPI.getLead(id)
      .then((r) => setLead(r.data))
      .catch(() => setError('Lead not found'))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, [id]);

  const changeStage = async (newStage) => {
    try {
      await crmAPI.changeStage(id, newStage);
      setSuccess(`Stage changed to ${newStage}`);
      load();
    } catch (e) { setError('Stage change failed'); }
  };

  const addNote = async () => {
    if (!noteText.trim()) return;
    await crmAPI.addNote(id, noteText);
    setNoteText('');
    load();
  };

  const handleFileChange = (e) => {
    const f = e.target.files[0];
    if (f) {
      setSelectedFile(f);
      setSuccess(`Selected: ${f.name}`);
    }
  };

  const uploadDoc = async () => {
    if (!selectedFile) { setError('Pehle file choose karo'); return; }
    setUploading(true);
    setError('');
    try {
      await crmAPI.uploadDocument(id, newDocType, selectedFile);
      setSuccess(`Uploaded: ${selectedFile.name}`);
      setSelectedFile(null);
      if (fileInputRef.current) fileInputRef.current.value = '';
      load();
    } catch (e) {
      setError('Upload failed: ' + (e.response?.data?.detail || e.message));
    } finally {
      setUploading(false);
    }
  };

  const updateDocStatus = async (docId, status) => {
    await crmAPI.updateDocStatus(docId, status);
    setSuccess(`Document ${status}`);
    load();
  };

  const aiVerify = async (docId) => {
    setUploading(true);
    setError('');
    setSuccess('🤖 AI verify chal raha hai... 15-30 second lag sakte hain');
    try {
      const res = await crmAPI.aiVerify(docId);
      const data = res.data;
      if (data.status === 'error') {
        setError(`AI Verify failed: ${data.message}`);
      } else {
        const a = data.analysis || {};
        const verdict = a.verdict || 'REVIEW';
        const risk = a.risk_score || 0;
        setSuccess(`🤖 Verdict: ${verdict} | Risk: ${risk}% | ${a.recommendation || ''}`);
        if (verdict === 'PASS') {
          await crmAPI.updateDocStatus(docId, 'VERIFIED');
        } else if (verdict === 'FLAG') {
          await crmAPI.updateDocStatus(docId, 'REJECTED', 'AI flagged');
        }
      }
      load();
    } catch (e) {
      setError('AI Verify failed: ' + (e.response?.data?.detail || e.message));
    } finally {
      setUploading(false);
    }
  };

  if (loading) return <div className="p-6">Loading...</div>;
  if (!lead) return <div className="p-6 text-red-600">{error || 'Not found'}</div>;

  return (
    <div className="p-6">
      <Link to="/agent/leads" className="text-blue-600 hover:underline text-sm">← Back to Leads</Link>

      <div className="mt-3 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">{lead.student_name}</h1>
          <p className="text-sm text-gray-500">{lead.email} • {lead.phone}</p>
        </div>
        <Badge color="blue">{lead.stage}</Badge>
      </div>

      {error && <div className="mt-3"><Alert type="danger" onClose={() => setError('')}>{error}</Alert></div>}
      {success && <div className="mt-3"><Alert type="success" onClose={() => setSuccess('')}>{success}</Alert></div>}

      <div className="mt-6 flex flex-wrap gap-2">
        {STAGES.map(s => (
          <button
            key={s}
            onClick={() => changeStage(s)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium border ${lead.stage === s ? 'bg-blue-600 text-white border-blue-600' : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'}`}
          >
            {s}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
        <Card title="Country" value={lead.country || '—'} icon="🌍" color="blue" />
        <Card title="Course" value={lead.course || '—'} icon="📚" color="purple" />
        <Card title="Budget" value={lead.budget || '—'} icon="💰" color="green" />
        <Card title="Intake" value={lead.intake || '—'} icon="📅" color="orange" />
        <Card title="Source" value={lead.source || '—'} icon="📡" color="gray" />
        <Card title="Priority" value={lead.priority || '—'} icon="⚡" color="red" />
      </div>

      <div className="mt-6 bg-white rounded-lg border p-4">
        <h2 className="font-semibold mb-3">📄 Documents</h2>

        <div className="bg-blue-50 border-2 border-dashed border-blue-300 rounded-lg p-4 mb-4">
          <div className="flex flex-wrap gap-2 items-center">
            <select
              value={newDocType}
              onChange={e => setNewDocType(e.target.value)}
              className="border rounded px-3 py-2 text-sm bg-white"
            >
              {DOC_TYPES.map(d => <option key={d} value={d}>{d}</option>)}
            </select>

            <input
              ref={fileInputRef}
              type="file"
              onChange={handleFileChange}
              className="text-sm"
              accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
            />

            <Button onClick={uploadDoc} disabled={uploading || !selectedFile}>
              {uploading ? 'Uploading...' : '📤 Upload Document'}
            </Button>
          </div>
          {selectedFile && (
            <p className="text-xs text-blue-700 mt-2">
              Selected: <strong>{selectedFile.name}</strong> ({(selectedFile.size / 1024).toFixed(1)} KB)
            </p>
          )}
        </div>

        <div className="space-y-2">
          {(lead.documents || []).length === 0 && (
            <p className="text-sm text-gray-500 text-center py-4">
              Koi document nahi hai. Upar se file upload karo.
            </p>
          )}
          {(lead.documents || []).map(d => (
            <div key={d.id} className="flex justify-between items-center border rounded px-3 py-2">
              <div className="flex items-center gap-2">
                <span className="font-medium text-sm">{d.document_type}</span>
                {d.document_name && d.document_name !== d.document_type && (
                  <span className="text-xs text-gray-500">({d.document_name})</span>
                )}
                <Badge color={d.status === 'VERIFIED' ? 'green' : d.status === 'REJECTED' ? 'red' : d.status === 'MISSING' ? 'orange' : 'blue'}>
                  {d.status}
                </Badge>
              </div>
              <div className="flex gap-2 items-center">
                {d.file_url && (
                  <a
                    href={`http://localhost:8000${d.file_url}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs text-blue-600 hover:underline"
                  >
                    👁 View
                  </a>
                )}
                <button onClick={() => aiVerify(d.id)} disabled={uploading} className="text-xs text-purple-600 hover:underline font-semibold">🤖 AI Verify</button>
                <button onClick={() => updateDocStatus(d.id, 'VERIFIED')} className="text-xs text-green-600 hover:underline">✓ Verify</button>
                <button onClick={() => updateDocStatus(d.id, 'REJECTED')} className="text-xs text-red-600 hover:underline">✗ Reject</button>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="mt-6 bg-white rounded-lg border p-4">
        <h2 className="font-semibold mb-3">📝 Notes & Activity</h2>
        <div className="flex gap-2 mb-4">
          <input
            value={noteText}
            onChange={e => setNoteText(e.target.value)}
            placeholder="Add a note..."
            className="flex-1 border rounded px-3 py-2 text-sm"
            onKeyDown={e => e.key === 'Enter' && addNote()}
          />
          <Button onClick={addNote}>Add</Button>
        </div>
        <div className="space-y-2 max-h-80 overflow-y-auto">
          {(lead.activities || []).map(a => (
            <div key={a.id} className="border-l-2 border-blue-400 pl-3 py-1">
              <p className="text-sm">{a.description}</p>
              <p className="text-xs text-gray-400">{new Date(a.created_at).toLocaleString()}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}