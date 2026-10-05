import React, { useState, useEffect } from 'react';
import { PageHeader, Card, Badge, Button, Input, Dropdown, Alert, DataTable } from '../../components/ui/Components';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function EmailComposer() {
  const [templates, setTemplates] = useState([]);
  const [template, setTemplate] = useState('custom');
  const [toEmail, setToEmail] = useState('');
  const [subject, setSubject] = useState('');
  const [body, setBody] = useState('');
  const [templateData, setTemplateData] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [logs, setLogs] = useState([]);

  const loadTemplates = () => {
    fetch(`${API_BASE}/email/templates`)
      .then((r) => r.json())
      .then((d) => setTemplates(d.templates || []))
      .catch(() => setTemplates([]));
  };

  const loadLogs = () => {
    fetch(`${API_BASE}/admin/email/logs?limit=20`)
      .then((r) => r.json())
      .then((d) => setLogs(d.logs || []))
      .catch(() => setLogs([]));
  };

  useEffect(() => {
    loadTemplates();
    loadLogs();
  }, []);

  const handleSend = async () => {
    if (!toEmail) {
      setError('Recipient email required');
      return;
    }
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      let res;
      if (template === 'custom') {
        if (!subject || !body) {
          setError('Subject and body required for custom email');
          setLoading(false);
          return;
        }
        res = await fetch(`${API_BASE}/email/send`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ to_email: toEmail, subject, body, template: 'custom' }),
        });
      } else {
        res = await fetch(`${API_BASE}/email/send-template`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ to_email: toEmail, template, data: templateData }),
        });
      }

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Failed to send');
      setSuccess(`✅ Email sent to ${toEmail}`);
      loadLogs();
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const templateOptions = templates.map((t) => ({
    value: t.id,
    label: `${t.name} — ${t.description}`,
  }));

  return (
    <div className="p-6">
      <PageHeader
        icon="📧"
        title="Email Composer"
        subtitle="Send custom emails or use templates"
        image="https://images.unsplash.com/photo-1596526131083-e8c633c948d2?w=1600&q=80"
      />

      {error && <Alert type="danger" onClose={() => setError('')}>{error}</Alert>}
      {success && <Alert type="success" onClose={() => setSuccess('')}>{success}</Alert>}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div className="bg-white rounded-xl shadow p-6">
          <h3 className="font-bold mb-4">📤 Compose Email</h3>

          <Input
            label="To Email *"
            value={toEmail}
            onChange={setToEmail}
            type="email"
            placeholder="recipient@example.com"
          />

          <Dropdown
            label="Template"
            value={template}
            onChange={setTemplate}
            options={templateOptions}
            placeholder="Select template"
          />

          {template === 'custom' ? (
            <>
              <Input
                label="Subject"
                value={subject}
                onChange={setSubject}
                placeholder="Email subject"
              />
              <div className="mb-3">
                <label className="block text-sm font-medium text-gray-700 mb-1">Body (HTML allowed)</label>
                <textarea
                  value={body}
                  onChange={(e) => setBody(e.target.value)}
                  rows={6}
                  placeholder="<h2>Hello!</h2><p>Your message...</p>"
                  className="w-full border rounded-lg px-3 py-2 text-sm"
                />
              </div>
            </>
          ) : (
            <div className="space-y-3 mb-3">
              <p className="text-xs text-gray-500">Fill the fields for this template:</p>
              {template === 'welcome' && (
                <Input label="Name" value={templateData.name || ''} onChange={(v) => setTemplateData({ ...templateData, name: v })} placeholder="John Doe" />
              )}
              {template === 'invitation' && (
                <>
                  <Input label="Name" value={templateData.name || ''} onChange={(v) => setTemplateData({ ...templateData, name: v })} placeholder="John Doe" />
                  <Input label="Role" value={templateData.role || ''} onChange={(v) => setTemplateData({ ...templateData, role: v })} placeholder="Agent / Company / Vendor" />
                  <Input label="Source" value={templateData.source || ''} onChange={(v) => setTemplateData({ ...templateData, source: v })} placeholder="LinkedIn / Google" />
                </>
              )}
              {(template === 'job_match' || template === 'student_match' || template === 'hr_alert') && (
                <>
                  <Input label="Name" value={templateData.name || ''} onChange={(v) => setTemplateData({ ...templateData, name: v })} placeholder="John Doe" />
                  <Input label="Count" value={templateData.count || ''} onChange={(v) => setTemplateData({ ...templateData, count: v })} placeholder="5" />
                </>
              )}
            </div>
          )}

          <div className="mt-3">
            <Button onClick={handleSend} loading={loading} fullWidth>
              📧 Send Email
            </Button>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow p-6">
          <h3 className="font-bold mb-4">📋 Available Templates</h3>
          <div className="space-y-2">
            {templates.map((t, i) => (
              <div key={i} className="p-3 border rounded-lg hover:bg-gray-50">
                <div className="flex items-center gap-2">
                  <Badge color="purple">{t.id}</Badge>
                  <span className="font-medium text-sm">{t.name}</span>
                </div>
                <p className="text-xs text-gray-500 mt-1">{t.description}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow">
        <div className="flex justify-between items-center p-4 border-b">
          <h3 className="font-bold">📜 Recent Email Logs</h3>
          <button onClick={loadLogs} className="text-xs bg-gray-100 hover:bg-gray-200 px-3 py-1.5 rounded">
            🔄 Refresh
          </button>
        </div>
        <DataTable
          loading={false}
          empty="No emails sent yet"
          columns={[
            { key: 'recipient', label: 'To', render: (r) => <span className="text-sm">{r.recipient}</span> },
            { key: 'subject', label: 'Subject', render: (r) => <span className="text-sm">{r.subject}</span> },
            { key: 'template', label: 'Template', render: (r) => <Badge color="blue">{r.template}</Badge> },
            {
              key: 'status',
              label: 'Status',
              render: (r) => <Badge color={r.status === 'sent' ? 'green' : 'red'}>{r.status}</Badge>,
            },
            {
              key: 'created_at',
              label: 'Sent',
              render: (r) => r.created_at ? new Date(r.created_at).toLocaleString() : '—',
            },
          ]}
          data={logs}
        />
      </div>
    </div>
  );
}