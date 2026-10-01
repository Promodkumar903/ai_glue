import React, { useState } from 'react';
import { PageHeader, Card, Button, Modal, Input, Textarea, Alert, DataTable, Badge } from '../../components/ui/Components';
import { contractsAPI } from '../../services/api';

const safeStr = (v, fb = '—') => (v == null || v === '') ? fb : String(v);

export default function Contracts() {
  const [showNew, setShowNew] = useState(false);
  const [form, setForm] = useState({ candidate_id: '', position: '', salary: '', start_date: '', terms: '' });
  const [submitting, setSubmitting] = useState(false);
  const [msg, setMsg] = useState(null);
  const [contracts, setContracts] = useState([]);

  const handleCreate = async () => {
    if (!form.candidate_id || !form.position) return;
    setSubmitting(true);
    try {
      const res = await contractsAPI.create(form);
      setContracts([...contracts, res.data]);
      setMsg({ type: 'success', text: '✅ Contract created!' });
      setShowNew(false);
      setForm({ candidate_id: '', position: '', salary: '', start_date: '', terms: '' });
    } catch (e) {
      setMsg({ type: 'danger', text: '❌ ' + (e.response?.data?.detail || e.message) });
    } finally { setSubmitting(false); }
  };

  const handleSign = async (id) => {
    try {
      await contractsAPI.sign(id);
      setContracts(contracts.map((c) => c.id === id ? { ...c, status: 'signed' } : c));
      setMsg({ type: 'success', text: '✅ Contract signed!' });
    } catch (e) {
      setMsg({ type: 'danger', text: '❌ ' + (e.response?.data?.detail || e.message) });
    }
  };

  return (
    <div className="p-6">
      <PageHeader
        icon="📜"
        title="Employment Contracts"
        subtitle="Create, sign and manage contracts"
        action={<Button onClick={() => setShowNew(true)}>➕ New Contract</Button>}
      />

      {msg && <Alert type={msg.type} onClose={() => setMsg(null)}>{msg.text}</Alert>}

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <Card title="Total Contracts" value={contracts.length} icon="📜" color="blue" />
        <Card title="Signed" value={contracts.filter((c) => c.status === 'signed').length} icon="✅" color="green" />
        <Card title="Pending" value={contracts.filter((c) => c.status !== 'signed').length} icon="⏳" color="orange" />
        <Card title="Total Value" value={`$${contracts.reduce((s, c) => s + Number(c.salary || 0), 0).toLocaleString()}`} icon="💰" color="purple" />
      </div>

      <DataTable
        empty="Koi contract nahi — ➕ New Contract se shuru karo"
        columns={[
          { key: 'id', label: 'Contract ID', render: (r) => <span className="font-mono text-xs">{safeStr(r.id || r.contract_id)}</span> },
          { key: 'position', label: 'Position', render: (r) => safeStr(r.position) },
          { key: 'candidate', label: 'Candidate', render: (r) => safeStr(r.candidate_name || r.candidate_id) },
          { key: 'salary', label: 'Salary', render: (r) => r.salary ? `$${Number(r.salary).toLocaleString()}` : '—' },
          { key: 'start_date', label: 'Start Date', render: (r) => r.start_date ? new Date(r.start_date).toLocaleDateString() : '—' },
          {
            key: 'status', label: 'Status',
            render: (r) => <Badge color={r.status === 'signed' ? 'green' : 'yellow'}>{safeStr(r.status, 'draft')}</Badge>,
          },
          {
            key: 'actions', label: 'Action',
            render: (r) => r.status === 'signed' ? <span className="text-xs text-gray-400">✅ Signed</span> : (
              <Button size="sm" variant="success" onClick={() => handleSign(r.id)}>✍ Sign</Button>
            ),
          },
        ]}
        data={contracts}
      />

      <Modal open={showNew} onClose={() => setShowNew(false)} title="Create Contract" size="lg">
        <Input label="Candidate ID" value={form.candidate_id} onChange={(v) => setForm({ ...form, candidate_id: v })} required />
        <Input label="Position" value={form.position} onChange={(v) => setForm({ ...form, position: v })} required />
        <div className="grid grid-cols-2 gap-3">
          <Input label="Salary (USD)" type="number" value={form.salary} onChange={(v) => setForm({ ...form, salary: v })} />
          <Input label="Start Date" type="date" value={form.start_date} onChange={(v) => setForm({ ...form, start_date: v })} />
        </div>
        <Textarea label="Terms & Conditions" value={form.terms} onChange={(v) => setForm({ ...form, terms: v })} rows={5} />
        <div className="flex gap-2 mt-4">
          <Button onClick={handleCreate} loading={submitting} fullWidth>📜 Create Contract</Button>
          <Button variant="ghost" onClick={() => setShowNew(false)}>Cancel</Button>
        </div>
      </Modal>
    </div>
  );
}