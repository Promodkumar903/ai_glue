import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../utils/axios';

const SIGNUP_ROLES = [
  { id: 'STUDENT', label: 'Student', desc: 'Study Abroad' },
  { id: 'JOB_SEEKER', label: 'Job Seeker', desc: 'Career & Placement' },
  { id: 'AGENT', label: 'Agent', desc: 'Manage Candidates' },
  { id: 'BROKER', label: 'Broker', desc: 'Agency & Revenue' },
  { id: 'EMPLOYER', label: 'Employer / HR', desc: 'Hiring & Recruitment' },
];

export default function Register() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [role, setRole] = useState('STUDENT');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await api.post(`/auth/register?role=${role}`, { email, password, full_name: fullName });
      navigate('/login');
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 p-4">
      <div className="bg-white p-8 rounded shadow-md w-full max-w-md">
        <img src="/logo.svg" alt="AI Glue" className="h-14 w-auto mx-auto mb-4" />  
        <h1 className="text-2xl font-bold mb-6 text-slate-800">Register</h1>
        {error && <div className="text-red-600 bg-red-50 border border-red-200 p-3 rounded mb-4 text-sm">{error}</div>}
        <form onSubmit={handleSubmit} className="space-y-4">
          <input type="text" name="name" autoComplete="name" placeholder="Full Name" value={fullName} onChange={(e) => setFullName(e.target.value)} className="w-full p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500" required />
          <input type="email" name="email" autoComplete="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} className="w-full p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500" required />
          <input type="password" name="new-password" autoComplete="new-password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} className="w-full p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500" required />
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">I am a:</label>
            <select name="role" value={role} onChange={(e) => setRole(e.target.value)} className="w-full p-3 border rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-green-500">
              {SIGNUP_ROLES.map((r) => (<option key={r.id} value={r.id}>{r.label} — {r.desc}</option>))}
            </select>
          </div>
          <button type="submit" disabled={loading} className="w-full bg-green-600 hover:bg-green-700 text-white py-3 rounded-lg font-semibold disabled:opacity-50">
            {loading ? 'Registering...' : 'Register'}
          </button>
        </form>
        <p className="mt-6 text-center text-sm text-slate-600">Already have account? <Link to="/login" className="text-blue-600 font-semibold hover:underline">Login</Link></p>
      </div>
    </div>
  );
}