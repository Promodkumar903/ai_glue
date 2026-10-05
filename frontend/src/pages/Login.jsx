import { useState } from 'react';
import { useAuth } from '../lib/auth-context';
import { useNavigate } from 'react-router-dom';
import {
  GraduationCap, Briefcase, Users, Landmark, Building2, ShieldCheck,
  Sparkles, ArrowRight, CheckCircle2, Mail, Lock
} from 'lucide-react';

const roles = [
  { id: 'STUDENT', label: 'Student', icon: GraduationCap, desc: 'Study Abroad', gradient: 'from-sky-500 to-blue-600', glow: 'shadow-sky-500/40' },
  { id: 'JOB_SEEKER', label: 'Job Seeker', icon: Briefcase, desc: 'Career & Placement', gradient: 'from-emerald-500 to-teal-600', glow: 'shadow-emerald-500/40' },
  { id: 'AGENT', label: 'Agent', icon: Users, desc: 'Manage Candidates', gradient: 'from-purple-500 to-fuchsia-600', glow: 'shadow-purple-500/40' },
  { id: 'BROKER', label: 'Broker', icon: Landmark, desc: 'Agency & Revenue', gradient: 'from-amber-500 to-orange-600', glow: 'shadow-amber-500/40' },
  { id: 'EMPLOYER', label: 'Employer / HR', icon: Building2, desc: 'Hiring & Recruitment', gradient: 'from-rose-500 to-red-600', glow: 'shadow-rose-500/40' },
  { id: 'ADMIN', label: 'Admin', icon: ShieldCheck, desc: 'Platform Governance', gradient: 'from-indigo-500 to-slate-600', glow: 'shadow-indigo-500/40' },
];

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [selectedRole, setSelectedRole] = useState('STUDENT');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const result = await login(email, password, selectedRole);
      const actualRole = result?.role || selectedRole;
      const path = `/${actualRole.toLowerCase().replace('_', '-')}`;
      navigate(path);
    } catch (err) {
      const msg = err.response?.data?.detail
        || err.message
        || 'Login failed. Please check your credentials.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const currentRole = roles.find(r => r.id === selectedRole);

  return (
    <div className="min-h-screen flex items-center justify-center p-4 relative overflow-hidden">
      {/* Background Image */}
      <div
        className="absolute inset-0 bg-cover bg-center"
        style={{
          backgroundImage: `url('https://images.unsplash.com/photo-1523050854058-8df90110c9f1?w=1920&q=80')`,
        }}
      />
      <div className="absolute inset-0 hero-overlay" />

      {/* Animated Orbs */}
      <div className="absolute top-[-20%] right-[-10%] w-[600px] h-[600px] bg-blue-600 rounded-full mix-blend-screen filter blur-[120px] opacity-30 animate-pulse"></div>
      <div className="absolute bottom-[-20%] left-[-10%] w-[600px] h-[600px] bg-purple-600 rounded-full mix-blend-screen filter blur-[120px] opacity-30 animate-pulse"></div>

      {/* Main Card */}
      <div className="relative w-full max-w-6xl glass-dark p-8 md:p-12 animate-fade-in-up">

        {/* Header */}
        <div className="text-center mb-10">
          <div className="flex items-center justify-center mb-3">
           <img 
             src="/logo-dark.svg" 
             alt="AI Glue" 
             className="h-20 w-auto"
           />
         </div>
          <div className="inline-flex items-center gap-2 bg-white/10 border border-white/20 rounded-full px-4 py-1.5 text-xs font-mono text-gray-200 backdrop-blur-sm">
            <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse"></span>
            v8.1 Enterprise
          </div>
          <p className="text-gray-300 text-base mt-4">Manpower + Education Unified Platform</p>
        </div>

        {/* Grid: Roles + Login Form */}
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">

          {/* Left: Role Selection */}
          <div className="lg:col-span-3">
            <p className="text-sm font-semibold text-gray-300 uppercase tracking-widest mb-4 flex items-center gap-2">
              <span className="w-1 h-5 bg-gradient-to-b from-blue-400 to-purple-500 rounded-full"></span>
              Select Your Ecosystem
            </p>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {roles.map((role) => {
                const isSelected = selectedRole === role.id;
                const Icon = role.icon;

                return (
                  <button
                    key={role.id}
                    type="button"
                    onClick={() => setSelectedRole(role.id)}
                    className={`relative group flex flex-col items-start p-5 rounded-2xl border-2 transition-all duration-300 cursor-pointer text-left ${
                      isSelected
                        ? `bg-gradient-to-br ${role.gradient} border-transparent shadow-2xl ${role.glow} scale-[1.03]`
                        : 'bg-white/5 border-white/10 hover:bg-white/10 hover:border-white/30 hover:scale-[1.01]'
                    }`}
                  >
                    {isSelected && (
                      <div className="absolute top-2 right-2">
                        <CheckCircle2 className="w-5 h-5 text-white drop-shadow-lg" />
                      </div>
                    )}

                    <div className={`mb-3 p-2.5 rounded-xl ${isSelected ? 'bg-white/20 backdrop-blur-sm' : 'bg-slate-800/50'} transition-all`}>
                      <Icon className={`w-6 h-6 ${isSelected ? 'text-white' : 'text-gray-400 group-hover:text-white'} transition-colors`} />
                    </div>

                    <span className={`text-sm font-bold ${isSelected ? 'text-white' : 'text-gray-200 group-hover:text-white'} transition-colors`}>
                      {role.label}
                    </span>

                    <span className={`text-[10px] ${isSelected ? 'text-white/80' : 'text-gray-400'} font-medium mt-1 leading-tight transition-colors`}>
                      {role.desc}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Right: Login Form */}
          <div className="lg:col-span-2 bg-white/5 border border-white/10 rounded-2xl p-6 backdrop-blur-xl">
            <p className="text-sm font-semibold text-gray-200 uppercase tracking-widest mb-5 flex items-center gap-2">
              <span className="w-1 h-5 bg-gradient-to-b from-indigo-400 to-purple-500 rounded-full"></span>
              Secure Access
            </p>

            {error && (
              <div className="mb-4 p-3 bg-red-500/20 border border-red-400/30 rounded-lg text-red-200 text-sm whitespace-pre-wrap">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-gray-300 mb-2 uppercase tracking-wide">
                  Email Address
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    type="email"
                    name="email"
                    autoComplete="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 bg-slate-900/60 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                    placeholder="you@company.com"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-300 mb-2 uppercase tracking-wide">
                  Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    type="password"
                    name="current-password"
                    autoComplete="current-password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 bg-slate-900/60 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                    placeholder="••••••••"
                    required
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className={`w-full group relative overflow-hidden bg-gradient-to-b ${currentRole?.gradient || 'from-blue-500 to-blue-700'} hover:brightness-110 text-white font-bold py-3.5 px-4 rounded-xl transition-all duration-200 shadow-3d ${currentRole?.glow || 'shadow-blue-600/40'} flex items-center justify-center gap-2 active:translate-y-1 active:shadow-md disabled:opacity-50`}
              >
                <span>{loading ? 'Authenticating...' : `Continue as ${currentRole?.label}`}</span>
                {!loading && <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />}
              </button>

              <div className="text-center space-y-2">
                <a href="/forgot-password" className="text-sm text-yellow-300 hover:text-yellow-200 transition-colors block">
                  Forgot Password?
                </a>

                {selectedRole !== 'ADMIN' ? (
                  <p className="text-sm text-gray-300">
                    New user?{' '}
                    <a href="/register" className="text-blue-300 hover:text-blue-200 underline transition-colors font-semibold">
                      Create an Account
                    </a>
                  </p>
                ) : (
                  <p className="text-xs text-gray-400 italic">
                    Admin accounts managed by existing admins
                  </p>
                )}
              </div>

              <p className="text-center text-[10px] text-gray-400 pt-3 flex items-center justify-center gap-2 border-t border-white/10">
                <span className="w-1.5 h-1.5 rounded-full bg-green-400 inline-block animate-pulse"></span>
                Secure • End-to-End Encrypted • RBAC Enabled
              </p>
            </form>
          </div>
        </div>

        {/* Footer with Legal Links */}
        <div className="mt-8 text-center text-xs text-gray-400 border-t border-white/10 pt-6">
          <div className="flex items-center justify-center gap-4 flex-wrap mb-3">
            <a href="/about" className="hover:text-white transition">About Us</a>
            <span className="text-white/20">•</span>
            <a href="/contact" className="hover:text-white transition">Contact</a>
            <span className="text-white/20">•</span>
            <a href="/privacy" className="hover:text-white transition">Privacy Policy</a>
            <span className="text-white/20">•</span>
            <a href="/terms" className="hover:text-white transition">Terms of Service</a>
          </div>
          © 2026 AI Glue Systems • Deployed with love for Manpower & Education
        </div>
      </div>
    </div>
  );
}