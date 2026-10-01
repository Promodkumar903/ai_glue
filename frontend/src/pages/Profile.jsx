import { useState, useEffect } from 'react';
import { User, Mail, Phone, Save, Camera } from 'lucide-react';
import { useAuth } from '../lib/auth-context';
import axios from '../utils/axios';

export default function Profile() {
  const { user } = useAuth();
  const [profile, setProfile] = useState({ full_name: user?.full_name || '', email: user?.email || '', phone: user?.phone || '' });
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    axios.get('/profile/me').catch(() => ({ data: {} }))
      .then(res => setProfile(p => ({ ...p, ...res.data })));
  }, []);

  const handleSave = async () => {
    setSaving(true);
    try {
      await axios.put('/profile/update', profile);
      alert('✅ Profile updated!');
    } catch { alert('❌ Failed'); }
    finally { setSaving(false); }
  };

  return (
    <div className="p-6 max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold text-slate-800 mb-6">👤 My Profile</h1>

      <div className="bg-white p-6 rounded-xl shadow-sm border mb-6 flex items-center gap-6">
        <div className="relative">
          <div className="w-24 h-24 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center text-white text-3xl font-bold">
            {(profile.full_name || user?.email || 'U')[0].toUpperCase()}
          </div>
          <button className="absolute bottom-0 right-0 bg-blue-600 p-2 rounded-full text-white shadow-lg">
            <Camera className="w-4 h-4" />
          </button>
        </div>
        <div>
          <h2 className="text-xl font-bold text-slate-800">{profile.full_name || 'User'}</h2>
          <p className="text-sm text-slate-500">{profile.email}</p>
          <span className="inline-block mt-2 px-3 py-1 bg-blue-100 text-blue-700 text-xs font-semibold rounded-full">
            {user?.role || 'USER'}
          </span>
        </div>
      </div>

      <div className="bg-white p-6 rounded-xl shadow-sm border space-y-4">
        <div>
          <label className="block text-sm font-semibold text-slate-700 mb-2">Full Name</label>
          <div className="relative">
            <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input type="text" value={profile.full_name || ''} onChange={e => setProfile({ ...profile, full_name: e.target.value })}
              className="w-full pl-10 pr-4 py-3 border rounded-xl focus:ring-2 focus:ring-blue-500 outline-none" />
          </div>
        </div>
        <div>
          <label className="block text-sm font-semibold text-slate-700 mb-2">Email</label>
          <div className="relative">
            <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input type="email" value={profile.email || ''} disabled className="w-full pl-10 pr-4 py-3 border rounded-xl bg-slate-50 text-slate-500" />
          </div>
        </div>
        <div>
          <label className="block text-sm font-semibold text-slate-700 mb-2">Phone</label>
          <div className="relative">
            <Phone className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input type="text" value={profile.phone || ''} onChange={e => setProfile({ ...profile, phone: e.target.value })}
              className="w-full pl-10 pr-4 py-3 border rounded-xl focus:ring-2 focus:ring-blue-500 outline-none" />
          </div>
        </div>
        <button onClick={handleSave} disabled={saving}
          className="w-full bg-gradient-to-b from-blue-500 to-blue-700 text-white py-3 rounded-xl font-semibold shadow-lg flex items-center justify-center gap-2 hover:brightness-110 disabled:opacity-50">
          <Save className="w-5 h-5" /> {saving ? 'Saving...' : 'Save Changes'}
        </button>
      </div>
    </div>
  );
}