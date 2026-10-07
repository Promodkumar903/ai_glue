import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { PageHeader, Card, DataTable, Badge, Alert, Tabs, Button } from '../../components/ui/Components';
import { crmAPI } from '../../services/api';

const safeArr = (v) => {
  if (Array.isArray(v)) return v;
  if (v && Array.isArray(v.leads)) return v.leads;
  if (v && Array.isArray(v.data)) return v.data;
  return [];
};

const STAGES = ['NEW', 'CONTACTED', 'INTERESTED', 'PROFILE_READY', 'DOCUMENTS', 'APPLICATION', 'OFFER', 'VISA', 'ENROLLED', 'LOST'];

export default function Leads() {
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState('all');
  const [error, setError] = useState('');
  const [showAdd, setShowAdd] = useState(false);
  const [form, setForm] = useState({
    student_name: '', email: '', phone: '', country: '', course: '',
    budget: '', intake: '', source: 'manual', priority: 'MEDIUM', notes: ''
  });

  const load = () => {
    setLoading(true);
    const params = tab === 'all' ? {} : { stage: tab };
    crmAPI.listLeads(params)
      .then((r) => setLeads(safeArr(r.data)))
      .catch(() => setLeads([]))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, [tab]);

  const handleAdd = async () => {
    if (!form.student_name) { setError('Student name required'); return; }
    try {
      await crmAPI.createLead(form);
      setShowAdd(false);
      setForm({ student_name: '', email: '', phone: '', country: '', course: '', budget: '', intake: '', source: 'manual', priority: 'MEDIUM', notes: '' });
      load();
    } catch (e) {
      setError('Failed to create lead');
    }
  };

  const countByStage = (s) => leads.filter(l => l.stage === s).length;

  return (
    <div className="p-6">
      <PageHeader icon="👥" title="Leads / CRM" subtitle="Manage all your student leads" />

      {error && <Alert type="danger" onClose={() => setError('')}>{error}</Alert>}

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <Card title="Total Leads" value={leads.length} icon="📋" color="blue" />
        <Card title="New" value={countByStage('NEW')} icon="🆕" color="green" />
        <Card title="In Progress" value={leads.filter(l => !['NEW','ENROLLED','LOST'].includes(l.stage)).length} icon="⏳" color="orange" />
        <Card title="Enrolled" value={countByStage('ENROLLED')} icon="🎓" color="purple" />
      </div>

      <div className="flex justify-between items-center mb-4">
        <Tabs
          active={tab}
          onChange={setTab}
          tabs={[
            { id: 'all', label: 'All', count: leads.length },
            { id: 'NEW', label: 'New' },
            { id: 'CONTACTED', label: 'Contacted' },
            { id: 'INTERESTED', label: 'Interested' },
            { id: 'APPLICATION', label: 'Application' },
            { id: 'OFFER', label: 'Offer' },
            { id: 'ENROLLED', label: 'Enrolled' },
          ]}
        />
        <Button onClick={() => setShowAdd(true)}>+ Add Lead</Button>
      </div>

      {showAdd && (
        <div className="mb-6 p-4 bg-white rounded-lg border border-gray-200 shadow">
          <h3 className="font-semibold mb-3">New Lead</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <input placeholder="Student Name *" value={form.student_name} onChange={e => setForm({...form, student_name: e.target.value})} className="border rounded px-3 py-2" />
            <input placeholder="Email" value={form.email} onChange={e => setForm({...form, email: e.target.value})} className="border rounded px-3 py-2" />
            <input placeholder="Phone" value={form.phone} onChange={e => setForm({...form, phone: e.target.value})} className="border rounded px-3 py-2" />
            <input placeholder="Country (target)" value={form.country} onChange={e => setForm({...form, country: e.target.value})} className="border rounded px-3 py-2" />
            <input placeholder="Course" value={form.course} onChange={e => setForm({...form, course: e.target.value})} className="border rounded px-3 py-2" />
            <input placeholder="Budget" value={form.budget} onChange={e => setForm({...form, budget: e.target.value})} className="border rounded px-3 py-2" />
            <input placeholder="Intake (e.g. Fall 2026)" value={form.intake} onChange={e => setForm({...form, intake: e.target.value})} className="border rounded px-3 py-2" />
            <select value={form.priority} onChange={e => setForm({...form, priority: e.target.value})} className="border rounded px-3 py-2">
              <option value="HIGH">High Priority</option>
              <option value="MEDIUM">Medium</option>
              <option value="LOW">Low</option>
            </select>
            <input placeholder="Source (instagram/website/walkin)" value={form.source} onChange={e => setForm({...form, source: e.target.value})} className="border rounded px-3 py-2" />
          </div>
          <textarea placeholder="Notes" value={form.notes} onChange={e => setForm({...form, notes: e.target.value})} className="w-full border rounded px-3 py-2 mt-3" rows={2} />
          <div className="flex gap-2 mt-3">
            <Button onClick={handleAdd}>Save</Button>
            <Button variant="secondary" onClick={() => setShowAdd(false)}>Cancel</Button>
          </div>
        </div>
      )}

      <DataTable
        loading={loading}
        empty="Koi lead nahi mila. + Add Lead click karo."
        columns={[
          { key: 'student_name', label: 'Name', render: (r) => (
              <Link to={`/agent/leads/${r.id}`} className="font-semibold text-blue-600 hover:underline">{r.student_name || '—'}</Link>
          )},
          { key: 'phone', label: 'Phone', render: (r) => r.phone || '—' },
          { key: 'country', label: 'Country', render: (r) => r.country || '—' },
          { key: 'course', label: 'Course', render: (r) => r.course || '—' },
          { key: 'stage', label: 'Stage', render: (r) => {
              const colors = { NEW: 'blue', CONTACTED: 'purple', INTERESTED: 'orange', PROFILE_READY: 'purple', DOCUMENTS: 'orange', APPLICATION: 'blue', OFFER: 'green', VISA: 'green', ENROLLED: 'green', LOST: 'red' };
              return <Badge color={colors[r.stage] || 'gray'}>{r.stage || '—'}</Badge>;
          }},
          { key: 'priority', label: 'Priority', render: (r) => {
              const c = { HIGH: 'red', MEDIUM: 'orange', LOW: 'gray' };
              return <Badge color={c[r.priority] || 'gray'}>{r.priority || '—'}</Badge>;
          }},
          { key: 'next_followup', label: 'Next Follow-up', render: (r) => r.next_followup ? new Date(r.next_followup).toLocaleDateString() : '—' },
        ]}
        data={leads}
      />
    </div>
  );
}