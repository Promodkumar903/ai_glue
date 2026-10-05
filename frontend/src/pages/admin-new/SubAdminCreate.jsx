import React, { useState } from 'react';
import { PageHeader, Card, Badge, Button, Input, Dropdown, Alert } from '../../components/ui/Components';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const ROLES = [
  { value: 'SUB_ADMIN', label: '⚙️ Sub Admin (Full access)' },
  { value: 'VENDOR_ADMIN', label: '🏪 Vendor Admin (Manage vendors)' },
  { value: 'EDU_ADMIN', label: '🎓 Education Admin (Manage colleges)' },
  { value: 'JOB_ADMIN', label: '💼 Job Admin (Manage jobs)' },
  { value: 'FINANCE_ADMIN', label: '💰 Finance Admin (Revenue)' },
];

export default function SubAdminCreate() {
  const [email, setEmail] = useState('');
  const [fullName, setFullName] = useState('');
  const [phone, setPhone] = useState('');
  const [country, setCountry] = useState('');
  const [role, setRole] = useState('SUB_ADMIN');
  const [customPassword, setCustomPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);
  const [copied, setCopied] = useState(false);

  const handleCreate = async () => {
    if (!email || !fullName) {
      setError('Email and Full Name are required');
      return;
    }
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const res = await fetch(`${API_BASE}/admin/create-sub-admin`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email,
          full_name: fullName,
          phone,
          country,
          role,
          password: customPassword,
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Creation failed');
      setResult(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = () => {
    if (!result) return;
    const text = `Email: ${result.email}\nPassword: ${result.generated_password}\nRole: ${result.role}`;
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleReset = () => {
    setEmail('');
    setFullName('');
    setPhone('');
    setCountry('');
    setRole('SUB_ADMIN');
    setCustomPassword('');
    setResult(null);
    setError('');
  };

  return (
    <div className="p-6">
      <PageHeader
        icon="👤"
        title="Create Sub-Admin"
        subtitle="Create new admin accounts with specific permissions"
        image="https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=1600&q=80"
      />

      {error && <Alert type="danger" onClose={() => setError('')}>{error}</Alert>}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Form */}
        <div className="bg-white rounded-xl shadow p-6">
          <h3 className="font-bold mb-4">📝 New Account Details</h3>

          <Input
            label="Email *"
            value={email}
            onChange={setEmail}
            type="email"
            placeholder="admin@company.com"
          />

          <Input
            label="Full Name *"
            value={fullName}
            onChange={setFullName}
            placeholder="John Doe"
          />

          <Input
            label="Phone"
            value={phone}
            onChange={setPhone}
            placeholder="+91 98765 43210"
          />

          <Dropdown
            label="Role"
            value={role}
            onChange={setRole}
            options={ROLES}
          />

          <Dropdown
            label="Country (Optional)"
            value={country}
            onChange={setCountry}
            options={[
              { value: 'India', label: 'India' },
              { value: 'Germany', label: 'Germany' },
              { value: 'USA', label: 'USA' },
              { value: 'UK', label: 'UK' },
              { value: 'Canada', label: 'Canada' },
              { value: 'UAE', label: 'UAE' },
            ]}
            placeholder="Select country"
          />

          <Input
            label="Custom Password (Optional — leave blank to auto-generate)"
            value={customPassword}
            onChange={setCustomPassword}
            placeholder="Leave blank for auto-generate"
          />

          <div className="flex gap-2 mt-4">
            <Button onClick={handleCreate} loading={loading} fullWidth>
              ✨ Create Sub-Admin
            </Button>
            <Button onClick={handleReset} variant="ghost">Reset</Button>
          </div>
        </div>

        {/* Result */}
        <div className="bg-white rounded-xl shadow p-6">
          <h3 className="font-bold mb-4">✅ Created Account</h3>

          {!result && !loading && (
            <div className="text-center py-12 text-gray-400">
              Fill the form and click Create → credentials will appear here
            </div>
          )}

          {loading && (
            <div className="text-center py-12 text-gray-400">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mb-3"></div>
              <p>Creating account...</p>
            </div>
          )}

          {result && (
            <div className="space-y-4">
              <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-lg">
                <p className="text-emerald-800 font-semibold mb-2">✅ Sub-Admin Created Successfully</p>
                <p className="text-xs text-emerald-700">Save these credentials — password won't be shown again</p>
              </div>

              <div className="space-y-3">
                <div className="flex justify-between items-center py-2 border-b">
                  <span className="text-sm text-gray-500">Email</span>
                  <span className="font-mono text-sm text-gray-800">{result.email}</span>
                </div>
                <div className="flex justify-between items-center py-2 border-b">
                  <span className="text-sm text-gray-500">Password</span>
                  <span className="font-mono text-sm text-emerald-600 font-bold bg-emerald-50 px-2 py-1 rounded">
                    {result.generated_password}
                  </span>
                </div>
                <div className="flex justify-between items-center py-2 border-b">
                  <span className="text-sm text-gray-500">Role</span>
                  <Badge color="purple">{result.role}</Badge>
                </div>
                <div className="flex justify-between items-center py-2 border-b">
                  <span className="text-sm text-gray-500">Full Name</span>
                  <span className="text-sm text-gray-800">{result.full_name}</span>
                </div>
              </div>

              <button
                onClick={handleCopy}
                className={`w-full py-3 rounded-lg font-medium transition ${
                  copied
                    ? 'bg-emerald-600 text-white'
                    : 'bg-blue-600 hover:bg-blue-700 text-white'
                }`}
              >
                {copied ? '✓ Copied!' : '📋 Copy Credentials'}
              </button>

              <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg text-xs text-amber-800">
                ⚠️ <strong>Important:</strong> Share these credentials securely. User must change password after first login.
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}