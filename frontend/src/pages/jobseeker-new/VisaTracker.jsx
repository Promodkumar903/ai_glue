import React, { useState, useEffect } from 'react';
import { PageHeader, Card, DataTable, Badge, Button, Alert, Modal, Input, Dropdown, ProgressBar } from '../../components/ui/Components';
import { visaAPI } from '../../services/api';

const safeArr = (v) => {
  if (Array.isArray(v)) return v;
  if (v && typeof v === 'object') {
    if (Array.isArray(v.items)) return v.items;
    if (Array.isArray(v.data)) return v.data;
  }
  return [];
};
const safeStr = (v, fb = '—') => (v == null || v === '') ? fb : String(v);

const STATUS_STEPS = ['applied', 'documents', 'interview', 'approved'];
const STATUS_COLORS = { applied: 'blue', documents: 'purple', interview: 'yellow', approved: 'green', rejected: 'red', pending: 'orange' };

export default function VisaTracker() {
  const [cases, setCases] = useState([]);
  const [funnel, setFunnel] = useState({});
  const [loading, setLoading] = useState(true);
  const [showNew, setShowNew] = useState(false);
  const [msg, setMsg] = useState(null);
  const [form, setForm] = useState({ country: '', visa_type: 'work' });
  const [submitting, setSubmitting] = useState(false);

  const load = () => {
    setLoading(true);
    Promise.allSettled([visaAPI.cases(), visaAPI.funnel()])
      .then(([c, f]) => {
        if (c.status === 'fulfilled') setCases(safeArr(c.value.data));
        if (f.status === 'fulfilled') setFunnel(typeof f.value.data === 'object' ? f.value.data : {});
        setLoading(false);
      });
  };

  useEffect(() => { load(); }, []);

  const handleCreate = async () => {
    setSubmitting(true);
    try {
      await visaAPI.create(form);
      setMsg({ type: 'success', text: '✅ Visa case created!' });
      setShowNew(false);
      setForm({ country: '', visa_type: 'work' });
      load();
    } catch (e) {
      setMsg({ type: 'danger', text: '❌ ' + (e.response?.data?.detail || e.message) });
    } finally { setSubmitting(false); }
  };

  const approved = cases.filter((c) => (c.status || '').toLowerCase() === 'approved').length;
  const pending = cases.filter((c) => !['approved', 'rejected'].includes((c.status || '').toLowerCase())).length;
  const rejected = cases.filter((c) => (c.status || '').toLowerCase() === 'rejected').length;

  return (
    <div className="p-6">
      <PageHeader
        icon="🛂"
        title="Visa Tracker"
        subtitle="Track your work visa application status"
        action={<Button onClick={() => setShowNew(true)}>➕ New Visa Case</Button>}
      />

      {msg && <Alert type={msg.type} onClose={() => setMsg(null)}>{msg.text}</Alert>}

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <Card title="Total Cases" value={cases.length} icon="🛂" color="blue" />
        <Card title="Approved" value={approved} icon="✅" color="green" />
        <Card title="Pending" value={pending} icon="⏳" color="orange" />
        <Card title="Rejected" value={rejected} icon="❌" color="red" />
      </div>

      {/* Visa Pipeline Funnel */}
      {cases.length > 0 && (
        <div className="bg-white rounded-xl shadow p-5 mb-6">
          <h3 className="font-bold mb-4">🛂 Visa Pipeline</h3>
          <div className="space-y-3">
            {STATUS_STEPS.map((step, i) => {
              const count = cases.filter((c) => (c.status || '').toLowerCase() === step).length;
              return <ProgressBar key={step} label={step.charAt(0).toUpperCase() + step.slice(1)} value={count} max={cases.length} color={['blue','purple','yellow','green'][i]} />;
            })}
          </div>
        </div>
      )}

      <DataTable
        loading={loading}
        empty="Koi visa case nahi — ➕ New Visa Case se shuru karo"
        columns={[
          { key: 'id', label: 'Case ID', render: (r) => <span className="font-mono text-xs">{safeStr(r.id || r.visa_case_id)}</span> },
          { key: 'country', label: 'Country', render: (r) => safeStr(r.country) },
          { key: 'visa_type', label: 'Type', render: (r) => <Badge color="blue">{safeStr(r.visa_type || r.type, 'N/A')}</Badge> },
          {
            key: 'status', label: 'Status',
            render: (r) => {
              const st = (r.status || '').toLowerCase();
              return <Badge color={STATUS_COLORS[st] || 'gray'}>{safeStr(r.status, 'N/A')}</Badge>;
            },
          },
          { key: 'appointment', label: 'Appointment', render: (r) => r.appointment_date ? new Date(r.appointment_date).toLocaleDateString() : '—' },
          { key: 'applied_at', label: 'Applied', render: (r) => (r.applied_at || r.created_at) ? new Date(r.applied_at || r.created_at).toLocaleDateString() : '—' },
        ]}
        data={cases}
      />

      <Modal open={showNew} onClose={() => setShowNew(false)} title="Create New Visa Case">
        <Input label="Country" value={form.country} onChange={(v) => setForm({ ...form, country: v })} required placeholder="e.g. Germany, Canada" />
        <Dropdown
          label="Visa Type"
          value={form.visa_type}
          onChange={(v) => setForm({ ...form, visa_type: v })}
          options={[
            { value: 'work', label: 'Work Visa' },
            { value: 'student', label: 'Student Visa' },
            { value: 'tourist', label: 'Tourist Visa' },
          ]}
        />
        <div className="flex gap-2 mt-3">
          <Button onClick={handleCreate} loading={submitting} fullWidth>💾 Create Case</Button>
          <Button variant="ghost" onClick={() => setShowNew(false)}>Cancel</Button>
        </div>
      </Modal>
    </div>
  );
}