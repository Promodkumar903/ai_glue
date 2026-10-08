import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Card, Badge, Alert, Button } from '../../components/ui/Components';
import { crmAPI } from '../../services/api';

const STATUSES = ['NOT_STARTED', 'DOCS_PENDING', 'APPLIED', 'UNDER_REVIEW', 'APPROVED', 'REJECTED', 'EXPIRED'];

const STATUS_COLORS = {
  NOT_STARTED: 'gray',
  DOCS_PENDING: 'orange',
  APPLIED: 'blue',
  UNDER_REVIEW: 'purple',
  APPROVED: 'green',
  REJECTED: 'red',
  EXPIRED: 'red',
};

const TRUST_BADGES = {
  VERIFIED: { color: 'green', icon: '🟢', label: 'Verified' },
  REPORTED: { color: 'orange', icon: '🟡', label: 'Reported' },
  UNVERIFIED: { color: 'red', icon: '🔴', label: 'Unverified' },
};

export default function VisaDetail() {
  const { id } = useParams();
  const [visa, setVisa] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [newApptDate, setNewApptDate] = useState('');
  const [newApptLocation, setNewApptLocation] = useState('');
  const [refNumber, setRefNumber] = useState('');
  const [autoChecking, setAutoChecking] = useState(false);
  const [smsPreview, setSmsPreview] = useState('');
  const [smsReason, setSmsReason] = useState('');

  const load = () => {
    setLoading(true);
    crmAPI.visaDetail(id)
      .then((r) => setVisa(r.data))
      .catch(() => setError('Visa case not found'))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, [id]);

  const changeStatus = async (newStatus) => {
    try {
      await crmAPI.updateVisaStatus(id, newStatus);
      setSuccess(`Status → ${newStatus}`);
      load();
    } catch (e) { setError('Status update failed'); }
  };

  const addAppointment = async () => {
    if (!newApptDate) { setError('Date required'); return; }
    try {
      await crmAPI.addVisaAppointment(id, { scheduled_at: newApptDate, location: newApptLocation });
      setSuccess('Appointment added');
      setNewApptDate(''); setNewApptLocation('');
      load();
    } catch (e) {
      setError('Appointment failed: ' + (e.response?.data?.detail || e.message));
    }
  };

  const runAutoCheck = async () => {
    setAutoChecking(true);
    setError('');
    try {
      const res = await crmAPI.visaAutoCheck(id, refNumber);
      const d = res.data;
      setSuccess(`Tier ${d.tier}: ${d.message || d.status}`);
      load();
    } catch (e) {
      setError('Auto-check failed: ' + (e.response?.data?.detail || e.message));
    } finally {
      setAutoChecking(false);
    }
  };

  const generateSMS = async () => {
    try {
      const res = await crmAPI.visaSendSMS(id, smsReason);
      setSmsPreview(res.data.sms_text);
      setSuccess('SMS text generated below');
    } catch (e) {
      setError('SMS failed: ' + (e.response?.data?.detail || e.message));
    }
  };

  if (loading) return <div className="p-6">Loading...</div>;
  if (!visa) return <div className="p-6 text-red-600">{error || 'Not found'}</div>;

  const trust = TRUST_BADGES[visa.trust_level] || TRUST_BADGES.REPORTED;

  return (
    <div className="p-6">
      <Link to="/agent/visa" className="text-blue-600 hover:underline text-sm">← Back to Visa Cases</Link>

      <div className="mt-3 flex justify-between items-center flex-wrap gap-2">
        <div>
          <h1 className="text-2xl font-bold">{visa.candidate_name || 'Unknown'}</h1>
          <p className="text-sm text-gray-500">
            {visa.candidate_email} • {visa.candidate_phone || '—'}
          </p>
        </div>
        <div className="flex gap-2">
          <Badge color={STATUS_COLORS[visa.status] || 'gray'}>{visa.status}</Badge>
          {visa.source_tier && (
            <Badge color="blue">{visa.source_tier}</Badge>
          )}
          <Badge color={trust.color}>{trust.icon} {trust.label}</Badge>
        </div>
      </div>

      {error && <div className="mt-3"><Alert type="danger" onClose={() => setError('')}>{error}</Alert></div>}
      {success && <div className="mt-3"><Alert type="success" onClose={() => setSuccess('')}>{success}</Alert></div>}

      {/* Status buttons */}
      <div className="mt-6 flex flex-wrap gap-2">
        {STATUSES.map((s) => (
          <button
            key={s}
            onClick={() => changeStatus(s)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium border ${
              visa.status === s
                ? 'bg-blue-600 text-white border-blue-600'
                : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
            }`}
          >
            {s}
          </button>
        ))}
      </div>

      {/* Info Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
        <Card title="Country" value={visa.country || '—'} icon="🌍" color="blue" />
        <Card title="Visa Type" value={visa.visa_type || '—'} icon="🛂" color="purple" />
        <Card title="Applied" value={visa.applied_at ? new Date(visa.applied_at).toLocaleDateString() : '—'} icon="📅" color="orange" />
        <Card title="Decision" value={visa.decision_at ? new Date(visa.decision_at).toLocaleDateString() : '—'} icon="✅" color="green" />
        <Card title="Last Checked" value={visa.last_checked_at ? new Date(visa.last_checked_at).toLocaleString() : 'Never'} icon="🔄" color="gray" />
        <Card title="SMS Sent" value={visa.sms_sent_at ? new Date(visa.sms_sent_at).toLocaleString() : 'No'} icon="📱" color="blue" />
      </div>

      {/* TIER CHECK — Auto API */}
      <div className="mt-6 bg-white rounded-lg border p-4">
        <h2 className="font-semibold mb-3">🤖 Auto Check (Tier 1/2 APIs)</h2>
        <p className="text-xs text-gray-500 mb-3">
          Tier 1: USA + UAE (Free) • Tier 2: UK, Australia (Paid) • Tier 3: Manual
        </p>
        <div className="flex flex-wrap gap-2">
          <input
            type="text"
            placeholder="Reference number (USCIS case ID, UK share code, etc.)"
            value={refNumber}
            onChange={(e) => setRefNumber(e.target.value)}
            className="border rounded px-3 py-2 text-sm flex-1 min-w-[250px]"
          />
          <Button onClick={runAutoCheck} disabled={autoChecking}>
            {autoChecking ? 'Checking...' : '🔍 Check Status'}
          </Button>
        </div>
      </div>

      {/* EMBASSY INFO */}
      <div className="mt-6 bg-white rounded-lg border p-4">
        <h2 className="font-semibold mb-3">🏛️ Embassy Information</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
          <div>
            <p className="text-xs text-gray-500">Embassy Name</p>
            <p className="font-medium">{visa.embassy_name || `${visa.country} Embassy`}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500">Website</p>
            {visa.embassy_url ? (
              <a href={visa.embassy_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                {visa.embassy_url}
              </a>
            ) : <p className="font-medium">—</p>}
          </div>
          <div>
            <p className="text-xs text-gray-500">Phone</p>
            <p className="font-medium">{visa.embassy_phone || '—'}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500">Processing Time</p>
            <p className="font-medium">{visa.processing_time || 'Varies'}</p>
          </div>
        </div>
      </div>

      {/* SMS — Manual fallback */}
      <div className="mt-6 bg-orange-50 border border-orange-200 rounded-lg p-4">
        <h2 className="font-semibold mb-3">📱 Send SMS to Candidate</h2>
        <p className="text-xs text-gray-600 mb-3">
          Manual status update ke liye — candidate ko SMS bhejo
        </p>
        <div className="flex flex-wrap gap-2 mb-3">
          <input
            type="text"
            placeholder="Reason (optional) — e.g. 'Visa interview on 15 Oct'"
            value={smsReason}
            onChange={(e) => setSmsReason(e.target.value)}
            className="border rounded px-3 py-2 text-sm flex-1 min-w-[250px]"
          />
          <Button onClick={generateSMS}>📱 Generate SMS</Button>
        </div>
        {smsPreview && (
          <div className="bg-white rounded border p-3 mt-2">
            <p className="text-xs text-gray-500 mb-1">SMS Preview:</p>
            <p className="text-sm whitespace-pre-wrap">{smsPreview}</p>
            <p className="text-xs text-green-700 mt-2">
              ✅ Ready to send — Twilio integration pending
            </p>
          </div>
        )}
      </div>

      {/* Appointments */}
      <div className="mt-6 bg-white rounded-lg border p-4">
        <h2 className="font-semibold mb-3">📅 Appointments</h2>
        <div className="flex flex-wrap gap-2 mb-4 pb-4 border-b">
          <input
            type="datetime-local"
            value={newApptDate}
            onChange={(e) => setNewApptDate(e.target.value)}
            className="border rounded px-3 py-2 text-sm"
          />
          <input
            type="text"
            placeholder="Location (e.g. VFS Delhi)"
            value={newApptLocation}
            onChange={(e) => setNewApptLocation(e.target.value)}
            className="border rounded px-3 py-2 text-sm flex-1 min-w-[200px]"
          />
          <Button onClick={addAppointment}>+ Add Appointment</Button>
        </div>
        <div className="space-y-2">
          {(visa.appointments || []).length === 0 ? (
            <p className="text-sm text-gray-500 text-center py-4">Koi appointment nahi hai</p>
          ) : (
            visa.appointments.map((a) => (
              <div key={a.id} className="flex justify-between items-center border rounded px-3 py-2">
                <div>
                  <p className="text-sm font-medium">
                    {a.scheduled_at ? new Date(a.scheduled_at).toLocaleString() : '—'}
                  </p>
                  <p className="text-xs text-gray-500">{a.location || '—'}</p>
                </div>
                <Badge color={a.status === 'COMPLETED' ? 'green' : a.status === 'CANCELLED' ? 'red' : 'blue'}>
                  {a.status}
                </Badge>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Checklist */}
      {visa.checklist && !visa.checklist.error && (
        <div className="mt-6 bg-white rounded-lg border p-4">
          <h2 className="font-semibold mb-3">📋 Document Checklist ({visa.country} {visa.visa_type})</h2>
          {Array.isArray(visa.checklist) ? (
            <div className="space-y-2">
              {visa.checklist.map((item, idx) => (
                <div key={idx} className="flex items-center gap-2 border rounded px-3 py-2">
                  <span className="text-lg">📄</span>
                  <span className="text-sm font-medium">
                    {typeof item === 'string' ? item : item.name || item.document || JSON.stringify(item)}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <pre className="text-xs bg-gray-50 p-3 rounded overflow-x-auto">
              {JSON.stringify(visa.checklist, null, 2)}
            </pre>
          )}
        </div>
      )}
    </div>
  );
}