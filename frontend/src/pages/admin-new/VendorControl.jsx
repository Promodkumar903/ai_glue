import React, { useState } from 'react';
import { PageHeader, DataTable, Dropdown, Button, Modal, Input, Card, Alert, Badge } from '../../components/ui/Components';
import { vendorAPI } from '../../services/api';
import { useFetch } from '../../hooks/useFetch';

const CATEGORY_ICONS = {
  hotel: '🏨',
  book: '📚',
  furniture: '🛋️',
  library: '📖',
  grocery: '🛒',
  transport: '🚕',
};

const VALID_CATEGORIES = ['hotel', 'book', 'furniture', 'library', 'grocery', 'transport'];

export default function VendorControl() {
  const [showAdd, setShowAdd] = useState(false);
  const [filterCat, setFilterCat] = useState('');
  const [search, setSearch] = useState('');
  const [form, setForm] = useState({ name: '', category: '', city: '', contact: '', email: '', address: '' });

  const { data: vendors, loading, error, reload } = useFetch(vendorAPI.list);
  const { data: categories } = useFetch(vendorAPI.categories);

  const vendorsArr = Array.isArray(vendors) ? vendors : vendors?.items || [];
  const catsArr = Array.isArray(categories) ? categories : categories?.items || [];

  const filtered = vendorsArr.filter((v) => {
    const matchCat = !filterCat || v.category === filterCat;
    const matchSearch = !search || (v.name || '').toLowerCase().includes(search.toLowerCase())
      || (v.city || '').toLowerCase().includes(search.toLowerCase());
    return matchCat && matchSearch;
  });

    const handleAdd = async () => {
    if (!form.name || !form.category) return alert('Name and Category required');
    if (!form.city) return alert('Location/City required');
    if (!form.contact) return alert('Phone/Contact required');

    // 🎯 Backend expects: name, category, location, phone
    const payload = {
      name: form.name,
      category: form.category,
      location: form.city,      // city → location
      phone: form.contact,       // contact → phone
      address: form.address || null,
    };

    try {
      await vendorAPI.create(payload);
      setShowAdd(false);
      setForm({ name: '', category: '', city: '', contact: '', email: '', address: '' });
      reload();
      alert('✅ Vendor added successfully!');
    } catch (e) {
      // Better error handling
      let msg = 'Unknown error';
      const detail = e.response?.data?.detail;
      if (typeof detail === 'string') {
        msg = detail;
      } else if (Array.isArray(detail)) {
        msg = detail.map((d) => `${d.loc?.join('.')}: ${d.msg}`).join('\n');
      } else if (detail) {
        msg = JSON.stringify(detail);
      } else {
        msg = e.message;
      }
      alert('❌ ' + msg);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this vendor?')) return;
    try {
      // Assuming DELETE /vendors/vendors/{id} exists — if not, will show error
      await fetch(`http://localhost:8000/vendors/vendors/${id}`, { method: 'DELETE' });
      reload();
    } catch { alert('Delete API not available yet'); }
  };

  // 🔄 Dynamic categories — jo data mein hain wahi dikhao
  const uniqueCats = [...new Set(vendorsArr.map((v) => v.category).filter(Boolean))];
  const counts = uniqueCats.map((cat) => ({
    cat,
    count: vendorsArr.filter((v) => v.category === cat).length,
  }));

  return (
    <div className="p-6">
      <PageHeader
        icon="🏨"
        title="Vendor Control"
        subtitle="Hotels, Books, Furniture, Library, Grocery — Sab yahan"
        action={<Button onClick={() => setShowAdd(true)}>➕ Add Vendor</Button>}
      />

      {error && <Alert type="danger" title="API Error">{error}</Alert>}

      {/* Category Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3 mb-6">
        {counts.slice(0, 6).map(({ cat, count }) => (
          <div
            key={cat}
            onClick={() => setFilterCat(filterCat === cat ? '' : cat)}
            className={`bg-white rounded-xl shadow p-3 text-center cursor-pointer transition hover:shadow-lg ${filterCat === cat ? 'ring-2 ring-blue-500' : ''}`}
          >
            <p className="text-3xl">{CATEGORY_ICONS[cat?.toLowerCase()] || '🏪'}</p>
            <p className="text-sm font-medium mt-1 capitalize">{cat}</p>
            <p className="text-lg font-bold text-blue-600">{count}</p>
          </div>
        ))}
      </div>

      {/* Filter Bar */}
      <div className="bg-white rounded-xl shadow p-4 mb-4 flex flex-wrap gap-3 items-end">
        <div className="flex-1 min-w-[200px]">
          <label className="block text-sm font-medium text-gray-700 mb-1">Search</label>
          <input
            value={search} onChange={(e) => setSearch(e.target.value)}
            placeholder="Search vendor name or city..."
            className="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
          />
        </div>
        <Dropdown
          label="Category"
          value={filterCat}
          onChange={setFilterCat}
          options={catsArr.map((c) => ({ value: c.name ?? c, label: c.name ?? c }))}
          placeholder="All Categories"
        />
        {(filterCat || search) && (
          <Button variant="ghost" onClick={() => { setFilterCat(''); setSearch(''); }}>Clear</Button>
        )}
      </div>

      {/* Table */}
      <DataTable
        loading={loading}
        empty="Koi vendor nahi mila — ➕ Add Vendor se add karo"
        columns={[
          {
            key: 'icon', label: '',
            render: (r) => <span className="text-2xl">{CATEGORY_ICONS[r.category?.toLowerCase()] || '🏪'}</span>,
            width: '50px',
          },
          { key: 'name', label: 'Vendor', render: (r) => <span className="font-semibold">{r.name}</span> },
          { key: 'category', label: 'Category', render: (r) => <Badge color="blue">{r.category || 'N/A'}</Badge> },
          { key: 'city', label: 'City' },
          { key: 'contact', label: 'Contact' },
          { key: 'email', label: 'Email' },
          {
            key: 'actions', label: 'Actions',
            render: (r) => (
              <div className="flex gap-2">
                <Button size="sm" variant="danger" onClick={() => handleDelete(r.id)}>🗑 Remove</Button>
              </div>
            ),
          },
        ]}
        data={filtered}
      />

      {/* Add Modal */}
      <Modal open={showAdd} onClose={() => setShowAdd(false)} title="Add New Vendor" size="lg">
        <Alert type="info">Hotel, Book Store, Furniture, Library, Grocery, Transport — koi bhi vendor add karo.</Alert>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <Input label="Vendor Name" value={form.name} onChange={(v) => setForm({ ...form, name: v })} required />
          <Dropdown
           label="Category"
            value={form.category}
            onChange={(v) => setForm({ ...form, category: v })}
            options={VALID_CATEGORIES.map((c) => ({ value: c, label: c.charAt(0).toUpperCase() + c.slice(1) }))}
            required
           />
          <Input label="City" value={form.city} onChange={(v) => setForm({ ...form, city: v })} />
          <Input label="Contact" value={form.contact} onChange={(v) => setForm({ ...form, contact: v })} />
          <Input label="Email" type="email" value={form.email} onChange={(v) => setForm({ ...form, email: v })} />
          <Input label="Address" value={form.address} onChange={(v) => setForm({ ...form, address: v })} />
        </div>
        <div className="flex gap-2 mt-4">
          <Button onClick={handleAdd} fullWidth>💾 Save Vendor</Button>
          <Button variant="ghost" onClick={() => setShowAdd(false)}>Cancel</Button>
        </div>
      </Modal>
    </div>
  );
}