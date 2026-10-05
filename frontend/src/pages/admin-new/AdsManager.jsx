import React, { useState, useEffect } from 'react';
import { PageHeader, Badge, Button, Input, Alert, DataTable } from '../../components/ui/Components';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function AdsManager() {
  const [ads, setAds] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const [form, setForm] = useState({
    title: '',
    banner_data: '',
    target_url: '',
    placement: 'dashboard',
    start_date: '',
    end_date: '',
  });

  const loadAds = () => {
    fetch(`${API_BASE}/admin/ads`)
      .then((r) => r.json())
      .then((d) => setAds(d.ads || []))
      .catch(() => setAds([]));
  };

  useEffect(() => {
    loadAds();
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
      setForm((prev) => ({ ...prev, banner_data: reader.result }));
    };
    reader.readAsDataURL(file);
  };

  const resetForm = () => {
    setForm({
      title: '',
      banner_data: '',
      target_url: '',
      placement: 'dashboard',
      start_date: '',
      end_date: '',
    });
  };

  const handleCreate = async () => {
    if (!form.title) {
      setError('Title required');
      return;
    }
    setLoading(true);
    setError('');
    setSuccess('');
    try {
      const res = await fetch(`${API_BASE}/admin/ads/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Failed');
      setSuccess(`✅ Ad "${form.title}" created`);
      resetForm();
      loadAds();
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this ad?')) return;
    try {
      await fetch(`${API_BASE}/admin/ads/${id}`, { method: 'DELETE' });
      loadAds();
    } catch (e) {
      setError(e.message);
    }
  };

  return (
    <div className="p-6">
      <PageHeader
        icon="📢"
        title="Ads & Banners"
        subtitle="Manage advertisement banners across the platform"
      />

      {error && <Alert type="danger" onClose={() => setError('')}>{error}</Alert>}
      {success && <Alert type="success" onClose={() => setSuccess('')}>{success}</Alert>}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div className="bg-white rounded-xl shadow p-6">
          <h3 className="font-bold mb-4">➕ Create Ad</h3>

          <Input
            label="Title *"
            value={form.title}
            onChange={(v) => setForm({ ...form, title: v })}
            placeholder="Summer Sale Banner"
          />

          <div className="mt-3">
            <label className="block text-sm font-medium text-gray-700 mb-1">Placement</label>
            <select
              value={form.placement}
              onChange={(e) => setForm({ ...form, placement: e.target.value })}
              className="w-full border rounded-lg px-3 py-2 text-sm"
            >
              <option value="dashboard">Dashboard</option>
              <option value="sidebar">Sidebar</option>
              <option value="popup">Popup</option>
            </select>
          </div>

          <Input
            label="Target URL (click hone pe kahan jaana)"
            value={form.target_url}
            onChange={(v) => setForm({ ...form, target_url: v })}
            placeholder="https://ai-glue-frontend.vercel.app/offers"
          />

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
              Banner Image (max 2MB)
            </label>
            <input type="file" accept="image/*" onChange={handleImageUpload} className="text-sm" />
            {form.banner_data && (
              <img
                src={form.banner_data}
                alt="preview"
                className="mt-2 h-32 rounded-lg border object-cover"
              />
            )}
          </div>

          <div className="mt-4 flex gap-2">
            <Button onClick={handleCreate} loading={loading}>
              💾 Save Ad
            </Button>
            <button
              onClick={resetForm}
              className="px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg text-sm"
            >
              Cancel
            </button>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow p-6">
          <h3 className="font-bold mb-4">ℹ️ Info</h3>
          <ul className="text-sm space-y-2 text-gray-600">
            <li>• <strong>Dashboard</strong> — user dashboard pe banner</li>
            <li>• <strong>Sidebar</strong> — sidebar mein chhota ad</li>
            <li>• <strong>Popup</strong> — login ke baad popup</li>
            <li>• Image 2MB se chhoti rakho (base64 DB mein store hoti hai)</li>
            <li>• Target URL optional — click pe redirect</li>
          </ul>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow">
        <div className="flex justify-between items-center p-4 border-b">
          <h3 className="font-bold">📜 All Ads</h3>
          <button onClick={loadAds} className="text-xs bg-gray-100 hover:bg-gray-200 px-3 py-1.5 rounded">
            🔄 Refresh
          </button>
        </div>
        <DataTable
          loading={false}
          empty="No ads yet"
          columns={[
            {
              key: 'banner_data',
              label: 'Banner',
              render: (r) =>
                r.banner_data ? (
                  <img src={r.banner_data} alt="" className="h-12 w-20 object-cover rounded" />
                ) : (
                  <span className="text-xs text-gray-400">No image</span>
                ),
            },
            { key: 'title', label: 'Title', render: (r) => <span className="text-sm font-medium">{r.title}</span> },
            { key: 'placement', label: 'Placement', render: (r) => <Badge color="blue">{r.placement}</Badge> },
            { key: 'target_url', label: 'URL', render: (r) => <span className="text-xs text-gray-500">{r.target_url || '—'}</span> },
            {
              key: 'actions',
              label: 'Actions',
              render: (r) => (
                <button
                  onClick={() => handleDelete(r.id)}
                  className="text-xs px-2 py-1 bg-red-100 hover:bg-red-200 rounded"
                >
                  🗑 Delete
                </button>
              ),
            },
          ]}
          data={ads}
        />
      </div>
    </div>
  );
}