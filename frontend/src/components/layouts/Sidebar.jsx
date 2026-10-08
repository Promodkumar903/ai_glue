import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard, Users, Building2, Briefcase, FileText,
  Search, MessageSquare, ShieldCheck, GraduationCap,
  DollarSign, BookOpen, Home, LogOut, Video, Award,
  Handshake, Hotel, Sparkles, Library, Heart,
  GraduationCap as EduIcon, Store, Target, TrendingUp, Package, Bell
} from 'lucide-react';
import { useAuth } from '../../lib/auth-context';

const roleNavItems = {
  // ==================== STUDENT ====================
  STUDENT: [
    { path: '/student', label: 'Dashboard', icon: LayoutDashboard },
    { divider: true, label: '📚 Study' },
    { path: '/student/education', label: 'Education', icon: GraduationCap },
    { path: '/student/life', label: 'Student Life', icon: Heart },
    { path: '/student/journey', label: 'Journey', icon: Sparkles },
    { path: '/student/housing', label: 'Housing', icon: Home },
    { path: '/student/books', label: 'Books', icon: Library },
    { path: '/student/visa', label: 'Student Visa', icon: ShieldCheck },
    { path: '/student/scholarships', label: 'Scholarships', icon: Award },
    { path: '/student/documents', label: 'Documents', icon: FileText },
    { divider: true, label: '📋 Applications' },
    { path: '/student-new/applications', label: 'My Applications', icon: FileText },
    { path: '/student-new/apply', label: 'Apply to College', icon: GraduationCap },
    { path: '/student-new/seats', label: 'Seat Availability', icon: BookOpen },
    { path: '/student-new/books', label: 'Books Library', icon: Library },
    { path: '/student-new/documents', label: 'Documents Vault', icon: ShieldCheck },
    { path: '/student-new/checklist', label: 'Document Checklist', icon: FileText },
    { path: '/student-new/verify', label: 'AI Verify Document', icon: ShieldCheck },
    { path: '/student-new/resume-converter', label: 'AI Resume Converter', icon: FileText },
    { divider: true, label: '💼 Work & Visa' },
    { path: '/jobseeker-new/offers', label: 'Job Offers', icon: Award },
    { path: '/jobseeker-new/visa', label: 'Visa Tracker', icon: ShieldCheck },
    { path: '/jobseeker-new/accommodation', label: 'Accommodation', icon: Hotel },
    { divider: true, label: '🌍 Explore' },
    { path: '/study-abroad', label: 'Study Abroad', icon: GraduationCap },
    { path: '/work-abroad', label: 'Work Abroad', icon: Briefcase },
    { path: '/trust', label: 'Trust Directory', icon: ShieldCheck },
    { divider: true, label: '💬 Communication' },
    { path: '/messages', label: 'Messages', icon: MessageSquare },
    { path: '/agent/followups', label: 'Follow-ups', icon: MessageSquare },
  ],

  // ==================== JOB SEEKER ====================
  JOB_SEEKER: [
    { path: '/job-seeker', label: 'Dashboard', icon: LayoutDashboard },
    { divider: true, label: '🔍 Find Work' },
    { path: '/jobseeker-new/search', label: 'Job Search', icon: Search },
    { path: '/jobseeker-new/resume', label: 'My Resume', icon: FileText },
    { path: '/jobseeker-new/resume-builder', label: 'AI Job Resume', icon: Sparkles },
    { path: '/job-seeker/resume-search', label: 'AI Resume Search', icon: Sparkles },
    { path: '/jobseeker-new/applications', label: 'My Applications', icon: Briefcase },
    { path: '/jobseeker-new/documents', label: 'Documents Vault', icon: ShieldCheck },
    { divider: true, label: '📋 Work Flow' },
    { path: '/job-seeker/vacancies', label: 'Vacancies', icon: Briefcase },
    { path: '/job-seeker/applications', label: 'Applications', icon: FileText },
    { path: '/job-seeker/interviews', label: 'Interviews', icon: Video },
    { path: '/jobseeker-new/offers', label: 'Offers', icon: Award },
    { path: '/job-seeker/deals', label: 'Deals', icon: Handshake },
    { path: '/jobseeker-new/accommodation', label: 'Accommodation', icon: Hotel },
    { path: '/jobseeker-new/visa', label: 'Work Visa', icon: ShieldCheck },
    { path: '/job-seeker/documents', label: 'Documents', icon: FileText },
    { path: '/jobseeker-new/offers', label: 'Job Offers', icon: Award },
    { path: '/jobseeker-new/visa', label: 'Visa Tracker', icon: ShieldCheck },
    { divider: true, label: '🌍 Explore' },
    { path: '/work-abroad', label: 'Work Abroad', icon: Briefcase },
    { path: '/trust', label: 'Trust Directory', icon: ShieldCheck },
    { divider: true, label: '💬 Communication' },
    { path: '/messages', label: 'Messages', icon: MessageSquare },
  ],

  // ==================== AGENT ====================
  AGENT: [
    { divider: true, label: '🎯 Actions' },
    { path: '/agent-new/candidates', label: 'Candidates', icon: Users },
    { path: '/agent/leads', label: 'Leads (CRM)', icon: Users },
    { path: '/agent/followups', label: 'Follow-ups', icon: MessageSquare },
    { path: '/agent', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/agent/dashboard', label: 'CRM Dashboard', icon: Target },
    { path: '/agent-new/funnel', label: 'Funnel', icon: Briefcase },
    { path: '/agent-new/commission', label: 'My Commission', icon: DollarSign },
    { path: '/agent/grades', label: 'My Grade', icon: Award },
    { path: '/agent-new/referral', label: 'Referral', icon: Sparkles },
    { divider: true, label: '🌍 Explore' },
    { path: '/study-abroad', label: 'Study Abroad', icon: GraduationCap },
    { path: '/trust', label: 'Trust Directory', icon: ShieldCheck },
    { divider: true, label: '💬 Communication' },
    { path: '/messages', label: 'Messages', icon: MessageSquare },
  ],

  // ==================== BROKER ====================
  BROKER: [
    { path: '/broker', label: 'Dashboard', icon: LayoutDashboard },
    { divider: true, label: '📊 Performance' },
    { path: '/broker-new/leaderboard', label: 'Agent Leaderboard', icon: Award },
    { path: '/broker-new/commission', label: 'Commission', icon: DollarSign },
    { path: '/broker-new/clients', label: 'Clients', icon: Building2 },
    { divider: true, label: '💬 Communication' },
    { path: '/messages', label: 'Messages', icon: MessageSquare },
  ],

  // ==================== EMPLOYER ====================
  EMPLOYER: [
    { path: '/employer', label: 'Dashboard', icon: LayoutDashboard },
    { divider: true, label: '💼 Hiring' },
    { path: '/employer-new/post-job', label: 'Post Job', icon: Briefcase },
    { path: '/employer-new/applicants', label: 'Applicants', icon: Users },
    { path: '/employer-new/contracts', label: 'Contracts', icon: FileText },
    { divider: true, label: '💬 Communication' },
    { path: '/messages', label: 'Messages', icon: MessageSquare },
  ],

  // ==================== ADMIN ====================
  ADMIN: [
    { path: '/admin', label: 'War Room', icon: LayoutDashboard },
    { path: '/admin/search', label: 'Universal Search', icon: Search },
    { path: '/admin/analytics', label: 'Analytics', icon: TrendingUp },
    { path: '/admin/sub-admin', label: 'Create Sub-Admin', icon: Users },
    { path: '/admin/email', label: 'Email Composer', icon: FileText },
    { path: '/admin/promotions', label: 'Promotions', icon: FileText },
    { path: '/admin/ads', label: 'Ads & Banners', icon: FileText },
    { path: '/my-subscription', label: 'My Subscription', icon: FileText },
    { path: '/my-payments', label: 'My Payments', icon: FileText },
    { path: '/pricing', label: 'Pricing Plans', icon: FileText },
    { path: '/admin/orchestration', label: 'AI Orchestration', icon: Sparkles },
    { path: '/admin/match/job-seeker', label: 'Match Job Seeker', icon: Target },
    { path: '/admin/match/student', label: 'Match Student', icon: Users },
    { path: '/admin/match/company', label: 'Match Company', icon: Building2 },
    { divider: true, label: '👥 Users' },
    { path: '/admin/users', label: 'Users', icon: Users },
    { path: '/admin/organizations', label: 'Organizations', icon: Building2 },
    { path: '/admin/audit', label: 'Audit Logs', icon: ShieldCheck },
    { divider: true, label: '🎓 Education' },
    { path: '/admin/education', label: 'Education Control', icon: EduIcon },
    { divider: true, label: '🏨 Vendors' },
    { path: '/admin/vendors', label: 'Vendor Control', icon: Store },
    { divider: true, label: '💼 Commands' },
    { path: '/admin/jobseekers', label: 'Job Seeker Command', icon: Target },
    { path: '/admin/students', label: 'Student Command', icon: Users },
    { path: '/admin/agents-brokers', label: 'Agent & Broker', icon: Handshake },
    { path: '/admin/revenue', label: 'Revenue & Reports', icon: TrendingUp },
    { path: '/admin/payment-settings', label: 'Payment Settings', icon: FileText },
    { path: '/admin/pending-payments', label: 'Pending Payments', icon: FileText },
    { divider: true, label: '📦 Operations' },
    { path: '/admin/bulk', label: 'Bulk Operations', icon: Package },
    { divider: true, label: '💬 Communication' },
    { path: '/messages', label: 'Messages', icon: MessageSquare },
  ],
};

export default function Sidebar({ role = 'STUDENT', isOpen, onClose }) {
  const { user, logout } = useAuth();
  const navItems = roleNavItems[role] || roleNavItems.STUDENT;

  return (
    <>
      {/* Mobile overlay — jab sidebar khula ho */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 md:hidden"
          onClick={onClose}
        />
      )}

      <aside className={`
        fixed md:static inset-y-0 left-0 z-50
        w-64 bg-slate-900 text-white flex flex-col shadow-2xl
        transform transition-transform duration-300
        ${isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
      `}>
        {/* Logo */}
        <div className="p-6 border-b border-slate-700">
          <div className="flex flex-col gap-1">
            <img src="/logo-dark.svg" alt="AI Glue" className="h-10 w-auto" />
            <p className="text-xs text-slate-400">{role}</p>
          </div>
        </div>
        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
          {navItems.map((item, idx) => {
            if (item.divider) {
              return (
                <div key={`div-${idx}`} className="pt-3 pb-1 px-4">
                  <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                    {item.label}
                  </p>
                </div>
              );
            }
            const Icon = item.icon;
            return (
              <NavLink
                key={`${item.path}-${idx}`}
                to={item.path}
                end={item.path.split('/').length === 2}
                onClick={onClose}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-4 py-2.5 rounded-lg transition-all duration-200 ${
                    isActive
                      ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg shadow-blue-500/30'
                      : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                  }`
                }
              >
                <Icon className="w-5 h-5" />
                <span className="text-sm font-medium">{item.label}</span>
              </NavLink>
            );
          })}
        </nav>

        {/* User */}
        <div className="p-4 border-t border-slate-700">
          <div className="flex items-center gap-3 mb-3 px-2">
            <div className="w-9 h-9 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center text-white font-bold text-sm">
              {(user?.full_name || user?.email || 'U')[0].toUpperCase()}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{user?.full_name || 'User'}</p>
              <p className="text-xs text-slate-400 truncate">{user?.email}</p>
            </div>
          </div>
          <button
            onClick={logout}
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg text-slate-300 hover:bg-red-600 hover:text-white transition-all"
          >
            <LogOut className="w-4 h-4" />
            <span className="text-sm font-medium">Logout</span>
          </button>
        </div>
      </aside>
    </>
  );
}