import React, { useState, useEffect } from 'react';
import { PageHeader, Card, DataTable, Badge, Button, Modal, Input, Textarea, Dropdown, Alert } from '../../components/ui/Components';
import { companyAPI } from '../../services/api';

const safeArr = (v) => {
  if (Array.isArray(v)) return v;
  if (v && typeof v === 'object') {
    if (Array.isArray(v.items)) return v.items;
    if (Array.isArray(v.data)) return v.data;
  }
  return [];
};
const safeStr = (v, fb = '—') => (v == null || v === '') ? fb : String(v);

export default function PostJob() {
  const [vacancies, setVacancies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showNew, setShowNew] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [msg, setMsg] = useState(null);
  const [form, setForm] = useState({ title: '', type: 'VACANCY', country: '', salary: '', description: '' });

  const load = () => {
    setLoading(true);
    companyAPI.vacancies()
      .then((r) => setVacancies(safeArr(r.data)))
      .catch(() => setVacancies([]))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  const handleCreate = async () => {
    if (!form.title) return;
    setSubmitting(true);
    try {
      await companyAPI.createVacancy(form);
      setMsg({ type: 'success', text: '✅ Vacancy posted!' });
      setShowNew(false);
      setForm({ title: '', type: 'VACANCY', country: '', salary: '', description: '' });
      load();
    } catch (e) {
      setMsg({ type: 'danger', text: '❌ ' + (e.response?.data?.detail || e.message) });
    } finally { setSubmitting(false); }
  };

  const toggleStatus = async (v) => {
    const newStatus = v.status === 'open' ? 'closed' : 'open';
    try {
      await companyAPI.updateVacancyStatus({ vacancy_id: v.id, status: newStatus });
      load();
    } catch (e) {
      setMsg({ type: 'danger', text: '❌ ' + (e.response?.data?.detail || e.message) });
    }
  };

  const open = vacancies.filter((v) => (v.status || 'open').toLowerCase() === 'open').length;
  const closed = vacancies.length - open;

  return (
    <div className="p-6">
      <PageHeader
        icon="📢"
        title="My Job Postings"
        subtitle="Post and manage your job vacancies"
        action={<Button onClick={() => setShowNew(true)}>➕ Post New Job</Button>}
      />

      {msg && <Alert type={msg.type} onClose={() => setMsg(null)}>{msg.text}</Alert>}

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <Card title="Total Vacancies" value={vacancies.length} icon="💼" color="blue" />
        <Card title="Open" value={open} icon="🟢" color="green" />
        <Card title="Closed" value={closed} icon="🔴" color="red" />
        <Card title="Applicants" value={vacancies.reduce((s, v) => s + (v.applicants_count || 0), 0)} icon="👥" color="purple" />
      </div>

      <DataTable
        loading={loading}
        empty="Koi vacancy nahi — ➕ Post New Job se shuru karo"
        columns={[
          { key: 'title', label: 'Job Title', render: (r) => <span className="font-semibold">{safeStr(r.title || r.name)}</span> },
          { key: 'type', label: 'Type', render: (r) => <Badge color="blue">{safeStr(r.type, 'VACANCY')}</Badge> },
          { key: 'country', label: 'Country', render: (r) => safeStr(r.country) },
          { key: 'salary', label: 'Salary', render: (r) => r.salary ? `$${Number(r.salary).toLocaleString()}` : '—' },
          {
            key: 'status', label: 'Status',
            render: (r) => <Badge color={(r.status || 'open') === 'open' ? 'green' : 'gray'}>{safeStr(r.status, 'open')}</Badge>,
          },
          {
            key: 'actions', label: 'Action',
            render: (r) => (
              <Button size="sm" variant={r.status === 'open' ? 'warning' : 'success'} onClick={() => toggleStatus(r)}>
                {r.status === 'open' ? '⏸ Close' : '▶ Open'}
              </Button>
            ),
          },
        ]}
        data={vacancies}
      />

      <Modal open={showNew} onClose={() => setShowNew(false)} title="Post New Job" size="lg">
        <Input label="Job Title" value={form.title} onChange={(v) => setForm({ ...form, title: v })} required />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <Dropdown
            label="Type"
            value={form.type}
            onChange={(v) => setForm({ ...form, type: v })}
            options={[
              { value: 'VACANCY', label: 'Full-time Vacancy' },
              { value: 'INTERNSHIP', label: 'Internship' },
              { value: 'PART_TIME', label: 'Part-time' },
              { value: 'CONTRACT', label: 'Contract' },
            ]}
          />
          <Input label="Country" value={form.country} onChange={(v) => setForm({ ...form, country: v })} />
          <Input label="Salary (USD)" type="number" value={form.salary} onChange={(v) => setForm({ ...form, salary: v })} />
        </div>
        <Textarea label="Description" value={form.description} onChange={(v) => setForm({ ...form, description: v })} placeholder="Job description, requirements..." />
        <div className="flex gap-2 mt-4">
          <Button onClick={handleCreate} loading={submitting} fullWidth>📢 Post Job</Button>
          <Button variant="ghost" onClick={() => setShowNew(false)}>Cancel</Button>
        </div>
      </Modal>
    </div>
  );
}