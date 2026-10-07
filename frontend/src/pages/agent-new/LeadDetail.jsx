import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { PageHeader, Card, Badge, Alert, Button } from '../../components/ui/Components';
import { crmAPI } from '../../services/api';

const STAGES = ['NEW', 'CONTACTED', 'INTERESTED', 'PROFILE_READY', 'DOCUMENTS', 'APPLICATION', 'OFFER', 'VISA', 'ENROLLED', 'LOST'];
const DOC_TYPES = ['Passport', 'Marksheet 10th', 'Marksheet 12th', 'Degree', 'IELTS/TOEFL', 'SOP', 'LOR', 'Bank Statement', 'Offer Letter', 'Visa'];

export default function LeadDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [lead, setLead] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [noteText, setNoteText] = useState('');
  const [newDocType, setNewDocType] = useState('Passport');

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
      load();
    } catch (e) { setError('Stage change failed'); }
  };

  const addNote = async () => {
    if (!noteText.trim()) return;
    await crmAPI.addNote(id, noteText);
    setNoteText('');
    load();
  };

  const addDoc = async () => {
    await crmAPI.addDocument(id, { document_type: newDocType, document_name: newDocType });
    load();
  };

  const updateDocStatus = async (docId, status) => {
    await crmAPI.updateDocStatus(docId, status);
    load();
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

      {error && <Alert type="danger" onClose={() => setError('')}>{error}</Alert>}

      {/* Stage selector */}
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

      {/* Info grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
        <Card title="Country" value={lead.country || '—'} icon="🌍" color="blue" />
        <Card title="Course" value={lead.course || '—'} icon="📚" color="purple" />
        <Card title="Budget" value={lead.budget || '—'} icon="💰" color="green" />
        <Card title="Intake" value={lead.intake || '—'} icon="📅" color="orange" />
        <Card title="Source" value={lead.source || '—'} icon="📡" color="gray" />
        <Card title="Priority" value={lead.priority || '—'} icon="⚡" color="red" />
      </div>

      {/* Documents */}
      <div className="mt-6 bg-white rounded-lg border p-4">
        <h2 className="font-semibold mb-3">📄 Documents</h2>
        <div className="flex gap-2 mb-3">
          <select value={newDocType} onChange={e => setNewDocType(e.target.value)} className="border rounded px-3 py-2 text-sm">
            {DOC_TYPES.map(d => <option key={d} value={d}>{d}</option>)}
          </select>
          <Button onClick={addDoc}>+ Add Document</Button>
        </div>
        <div className="space-y-2">
          {(lead.documents || []).length === 0 && <p className="text-sm text-gray-500">No documents yet</p>}
          {(lead.documents || []).map(d => (
            <div key={d.id} className="flex justify-between items-center border rounded px-3 py-2">
              <div>
                <span className="font-medium text-sm">{d.document_type}</span>
                <Badge color={d.status === 'VERIFIED' ? 'green' : d.status === 'REJECTED' ? 'red' : d.status === 'MISSING' ? 'orange' : 'blue'}>{d.status}</Badge>
              </div>
              <div className="flex gap-2">
                <button onClick={() => updateDocStatus(d.id, 'VERIFIED')} className="text-xs text-green-600 hover:underline">Verify</button>
                <button onClick={() => updateDocStatus(d.id, 'REJECTED')} className="text-xs text-red-600 hover:underline">Reject</button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Notes */}
      <div className="mt-6 bg-white rounded-lg border p-4">
        <h2 className="font-semibold mb-3">📝 Notes & Activity</h2>
        <div className="flex gap-2 mb-4">
          <input
            value={noteText}
            onChange={e => setNoteText(e.target.value)}
            placeholder="Add a note..."
            className="flex-1 border rounded px-3 py-2 text-sm"
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