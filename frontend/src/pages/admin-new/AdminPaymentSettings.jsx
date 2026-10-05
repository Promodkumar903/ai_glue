import React, { useState, useEffect } from 'react';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function AdminPaymentSettings() {
  const [form, setForm] = useState({
    upi_id_1: '', upi_id_2: '', upi_qr_image: '',
    esewa_id: '', esewa_name: '', esewa_qr_image: '',
    paypal_link: '', paypal_qr_image: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    fetch(`${API_BASE}/payments/settings`).then(r => r.json()).then(d => {
      if (d.settings) setForm(d.settings);
    });
  }, []);

  const handleUpload = (field) => (e) => {
    const file = e.target.files[0];
    if (!file) return;
    if (file.size > 2 * 1024 * 1024) { setError('Image 2MB se chhoti honi chahiye'); return; }
    const reader = new FileReader();
    reader.onloadend = () => setForm(prev => ({ ...prev, [field]: reader.result }));
    reader.readAsDataURL(file);
  };

  const handleSave = async () => {
    setLoading(true); setError(''); setSuccess('');
    try {
      const res = await fetch(`${API_BASE}/admin/payments/settings`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });
      if (!res.ok) throw new Error('Save failed');
      setSuccess('✅ Payment settings updated');
    } catch (e) { setError(e.message); }
    finally { setLoading(false); }
  };

  return (
    <div className="p-6 max-w-4xl">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-800">💳 Payment Settings</h1>
        <p className="text-sm text-slate-500 mt-1">Upload UPI/eSewa/PayPal QR codes and IDs</p>
      </div>

      {error && <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-lg">{error}</div>}
      {success && <div className="mb-4 p-3 bg-green-100 text-green-700 rounded-lg">{success}</div>}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow p-5">
          <h3 className="font-bold mb-3">🇮🇳 Direct UPI (India)</h3>
          <div className="mb-3">
            <label className="text-sm font-medium block mb-1">UPI ID 1</label>
            <input type="text" value={form.upi_id_1} onChange={e => setForm({ ...form, upi_id_1: e.target.value })} className="w-full border rounded-lg px-3 py-2 text-sm" placeholder="pramod.rf@oksbi" />
          </div>
          <div className="mb-3">
            <label className="text-sm font-medium block mb-1">UPI ID 2</label>
            <input type="text" value={form.upi_id_2} onChange={e => setForm({ ...form, upi_id_2: e.target.value })} className="w-full border rounded-lg px-3 py-2 text-sm" placeholder="8174015550@idfcfirst" />
          </div>
          <div>
            <label className="text-sm font-medium block mb-1">UPI QR Image</label>
            <input type="file" accept="image/*" onChange={handleUpload('upi_qr_image')} className="text-sm" />
            {form.upi_qr_image && <img src={form.upi_qr_image} alt="UPI QR" className="mt-2 w-32 rounded border" />}
          </div>
        </div>

        <div className="bg-white rounded-xl shadow p-5">
          <h3 className="font-bold mb-3">🇳🇵 eSewa (Nepal)</h3>
          <div className="mb-3">
            <label className="text-sm font-medium block mb-1">eSewa ID</label>
            <input type="text" value={form.esewa_id} onChange={e => setForm({ ...form, esewa_id: e.target.value })} className="w-full border rounded-lg px-3 py-2 text-sm" placeholder="9826448788" />
          </div>
          <div className="mb-3">
            <label className="text-sm font-medium block mb-1">eSewa Name</label>
            <input type="text" value={form.esewa_name} onChange={e => setForm({ ...form, esewa_name: e.target.value })} className="w-full border rounded-lg px-3 py-2 text-sm" placeholder="Promod Kumar" />
          </div>
          <div>
            <label className="text-sm font-medium block mb-1">eSewa QR Image</label>
            <input type="file" accept="image/*" onChange={handleUpload('esewa_qr_image')} className="text-sm" />
            {form.esewa_qr_image && <img src={form.esewa_qr_image} alt="eSewa QR" className="mt-2 w-32 rounded border" />}
          </div>
        </div>

        <div className="bg-white rounded-xl shadow p-5 md:col-span-2">
          <h3 className="font-bold mb-3">🌍 PayPal (Global)</h3>
          <div className="mb-3">
            <label className="text-sm font-medium block mb-1">PayPal link</label>
            <input type="text" value={form.paypal_link} onChange={e => setForm({ ...form, paypal_link: e.target.value })} className="w-full border rounded-lg px-3 py-2 text-sm" placeholder="https://paypal.me/aiglueagent" />
          </div>
          <div>
            <label className="text-sm font-medium block mb-1">PayPal QR Image</label>
            <input type="file" accept="image/*" onChange={handleUpload('paypal_qr_image')} className="text-sm" />
            {form.paypal_qr_image && <img src={form.paypal_qr_image} alt="PayPal QR" className="mt-2 w-32 rounded border" />}
          </div>
        </div>
      </div>

      <div className="mt-6">
        <button onClick={handleSave} disabled={loading} className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-lg font-semibold">
          {loading ? 'Saving...' : '💾 Save Settings'}
        </button>
      </div>
    </div>
  );
}