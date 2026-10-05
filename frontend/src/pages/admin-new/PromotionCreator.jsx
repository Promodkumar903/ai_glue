import React, { useState, useEffect } from 'react';
import { PageHeader, Card, Badge, Button, Input, Alert, DataTable } from '../../components/ui/Components';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function PromotionCreator() {
  const [services, setServices] = useState([]);
  const [promotions, setPromotions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Form state
  const [form, setForm] = useState({
    title: '',
    type: 'promotion',
    discount_percent: 0,
    duration_days: 0,
    start_date: '',
    end_date: '',
    message: '',
    image_data: '',
    service_ids: [],
  });

  const loadServices = () => {
    fetch(`${API_BASE}/promotions/services`)
      .then((r) => r.json())
      .then((d) => setServices(d.services || []))
      .catch(() => setServices([]));
  };

  const loadPromotions = () => {
    fetch(`${API_BASE}/admin/promotions`)
      .then((r) => r.json())
      .then((d) => setPromotions(d.promotions || []))
      .catch(() => setPromotions([]));
  };

  useEffect(() => {
    loadServices();
    loadPromotions();
  }, []);

  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    if (file.size > 2 * 1024 * 1024) {
      setError('Image 2MB se chhoti honi chahiye');
      return;
    }
    const reader = new FileReader();
    reader.onloadend = () => {
      setForm((prev) => ({ ...prev, image_data: reader.result }));
    };
    reader.readAsDataURL(file);
  };

  const toggleService = (sid) => {
    setForm((prev) => ({
      ...prev,
      service_ids: prev.service_ids.includes(sid)
        ? prev.service_ids.filter((x) => x !== sid)
        : [...prev.service_ids, sid],
    }));
  };

  const resetForm = () => {
    setForm({
      title: '',
      type: 'promotion',
      discount_percent: 0,
      duration_days: 0,
      start_date: '',
      end_date: '',
      message: '',
      image_data: '',
      service_ids: [],
    });
  };

  const handleCreate = async () => {
    if (!form.title) {
      setError('Title required');
      return;
    }
    if (form.type === 'promotion' && !form.discount_percent) {
      setError('Promotion ke liye discount % required');
      return;
    }
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const res = await fetch(`${API_BASE}/admin/promotions/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Failed');
      setSuccess(`✅ Promotion "${form.title}" created`);
      resetForm();
      loadPromotions();
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this promotion?')) return;
    try {
      await fetch(`${API_BASE}/admin/promotions/${id}`, { method: 'DELETE' });
      loadPromotions();
      setSuccess('Deleted');
    } catch (e) {
      setError(e.message);
    }
  };

  const handleToggle = async (id, currentStatus) => {
    const newStatus = currentStatus === 'active' ? 'paused' : 'active';
    try {
      await fetch(`${API_BASE}/admin/promotions/${id}/status?status=${newStatus}`, {
        method: 'PATCH',
      });
      loadPromotions();
    } catch (e) {
      setError(e.message);
    }
  };

  return (
    <div className="p-6">
      <PageHeader
        icon="🎁"
        title="Promotions & Offers"
        subtitle="Create promotions, free offers, and paid offers with discounts"
      />

      {error && <Alert type="danger" onClose={() => setError('')}>{error}</Alert>}
      {success && <Alert type="success" onClose={() => setSuccess('')}>{success}</Alert>}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        {/* LEFT: Service Type Selector */}
        <div className="bg-white rounded-xl shadow p-6">
          <h3 className="font-bold mb-4">1️⃣ Service Type</h3>
          <div className="space-y-2">
            {[
              { id: 'promotion', label: '🎯 Promotion', desc: 'Discount offer' },
              { id: 'free', label: '🎁 Free', desc: 'Free service' },
              { id: 'paid', label: '💰 Paid', desc: 'Paid service' },
            ].map((t) => (
              <label
                key={t.id}
                className={`block p-3 border-2 rounded-lg cursor-pointer transition ${
                  form.type === t.id ? 'border-purple-500 bg-purple-50' : 'border-gray-200 hover:bg-gray-50'
                }`}
              >
                <input
                  type="radio"
                  name="type"
                  value={t.id}
                  checked={form.type === t.id}
                  onChange={() => setForm({ ...form, type: t.id })}
                  className="mr-2"
                />
                <span className="font-medium">{t.label}</span>
                <p className="text-xs text-gray-500 ml-6">{t.desc}</p>
              </label>
            ))}
          </div>

          <div className="mt-6">
            <h3 className="font-bold mb-3">📋 Services Apply</h3>
            <div className="space-y-1 max-h-48 overflow-auto">
              {services.map((s) => (
                <label key={s.id} className="flex items-center gap-2 text-sm p-1 hover:bg-gray-50 rounded cursor-pointer">
                  <input
                    type="checkbox"
                    checked={form.service_ids.includes(s.id)}
                    onChange={() => toggleService(s.id)}
                  />
                  {s.name}
                </label>
              ))}
            </div>
          </div>
        </div>

        {/* RIGHT: Dynamic Fields */}
        <div className="lg:col-span-2 bg-white rounded-xl shadow p-6">
          <h3 className="font-bold mb-4">2️⃣ Details</h3>

          <Input
            label="Title *"
            value={form.title}
            onChange={(v) => setForm({ ...form, title: v })}
            placeholder="Diwali Dhamaka 2026"
          />

          {form.type === 'promotion' && (
            <div className="grid grid-cols-2 gap-3 mt-3">
              <Input
                label="Discount %"
                type="number"
                value={form.discount_percent}
                onChange={(v) => setForm({ ...form, discount_percent: parseInt(v) || 0 })}
                placeholder="20"
              />
              <Input
                label="Duration (days)"
                type="number"
                value={form.duration_days}
                onChange={(v) => setForm({ ...form, duration_days: parseInt(v) || 0 })}
                placeholder="15"
              />
            </div>
          )}

          <div className="grid grid-cols-2 gap-3 mt-3">
            <Input
              label="Start Date"
              type="date"
              value={form.start_date}
              onChange={(v) => setForm({ ...form, start_date: v })}
            />
            <Input
              label="End Date"
              type="date"
              value={form.end_date}
              onChange={(v) => setForm({ ...form, end_date: v })}
            />
          </div>

          <div className="mt-3">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Message (SMS / Notification)
            </label>
            <textarea
              value={form.message}
              onChange={(e) => setForm({ ...form, message: e.target.value })}
              rows={3}
              placeholder="Diwali Dhamaka! 20% off on all services. Limited time offer!"
              className="w-full border rounded-lg px-3 py-2 text-sm"
            />
          </div>

          <div className="mt-3">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Attach Image (JPG/PNG, max 2MB)
            </label>
            <input
              type="file"
              accept="image/*"
              onChange={handleImageUpload}
              className="text-sm"
            />
            {form.image_data && (
              <div className="mt-2">
                <img
                  src={form.image_data}
                  alt="preview"
                  className="h-32 rounded-lg border object-cover"
                />
                <button
                  onClick={() => setForm({ ...form, image_data: '' })}
                  className="text-xs text-red-500 mt-1"
                >
                  ✕ Remove
                </button>
              </div>
            )}
          </div>

          <div className="mt-4 flex gap-2">
            <Button onClick={handleCreate} loading={loading}>
              💾 Save Promotion
            </Button>
            <button
              onClick={resetForm}
              className="px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg text-sm"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>

      {/* List */}
      <div className="bg-white rounded-xl shadow">
        <div className="flex justify-between items-center p-4 border-b">
          <h3 className="font-bold">📜 All Promotions</h3>
          <button onClick={loadPromotions} className="text-xs bg-gray-100 hover:bg-gray-200 px-3 py-1.5 rounded">
            🔄 Refresh
          </button>
        </div>
        <DataTable
          loading={false}
          empty="No promotions yet"
          columns={[
            { key: 'title', label: 'Title', render: (r) => <span className="font-medium text-sm">{r.title}</span> },
            { key: 'type', label: 'Type', render: (r) => <Badge color="purple">{r.type}</Badge> },
            { key: 'discount_percent', label: 'Discount', render: (r) => r.type === 'promotion' ? `${r.discount_percent}%` : '—' },
            { key: 'duration_days', label: 'Days', render: (r) => r.duration_days || '—' },
            { key: 'end_date', label: 'Ends', render: (r) => r.end_date || '—' },
            {
              key: 'status',
              label: 'Status',
              render: (r) => (
                <Badge color={r.status === 'active' ? 'green' : r.status === 'paused' ? 'yellow' : 'red'}>
                  {r.status}
                </Badge>
              ),
            },
            {
              key: 'actions',
              label: 'Actions',
              render: (r) => (
                <div className="flex gap-2">
                  <button
                    onClick={() => handleToggle(r.id, r.status)}
                    className="text-xs px-2 py-1 bg-yellow-100 hover:bg-yellow-200 rounded"
                  >
                    {r.status === 'active' ? '⏸ Pause' : '▶ Activate'}
                  </button>
                  <button
                    onClick={() => handleDelete(r.id)}
                    className="text-xs px-2 py-1 bg-red-100 hover:bg-red-200 rounded"
                  >
                    🗑 Delete
                  </button>
                </div>
              ),
            },
          ]}
          data={promotions}
        />
      </div>
    </div>
  );
}