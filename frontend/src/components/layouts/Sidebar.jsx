import { useState } from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard, Users, Building2, Briefcase, FileText,
  Search, MessageSquare, ShieldCheck, GraduationCap,
  DollarSign, BookOpen, Home, LogOut, Video, Award,
  Handshake, Hotel, Sparkles, User, Library, Heart,
  GraduationCap as EduIcon, Store, Target, TrendingUp, Package
} from 'lucide-react';
import { useAuth } from '../../lib/auth-context';

const roleNavItems = {
  // ==================== STUDENT (Study Abroad) ====================
  STUDENT: [
    { path: '/student', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/student/education', label: 'Education', icon: GraduationCap },
    { path: '/student/life', label: 'Student Life', icon: Heart },
    { path: '/student/journey', label: 'Journey', icon: Sparkles },
    { path: '/student/housing', label: 'Housing', icon: Home },
    { path: '/student/books', label: 'Books', icon: Library },
    { path: '/student/visa', label: 'Student Visa', icon: ShieldCheck },
    { path: '/student/scholarships', label: 'Scholarships', icon: Award },
    { path: '/student/documents', label: 'Documents', icon: FileText },
    { path: '/messages', label: 'Messages', icon: MessageSquare },
    { path: '/jobseeker-new/offers', label: 'Job Offers', icon: Award },
    { path: '/jobseeker-new/visa', label: 'Visa Tracker', icon: ShieldCheck },
    { path: '/jobseeker-new/accommodation', label: 'Accommodation', icon: Hotel },
    { path: '/student-new/applications', label: 'My Applications', icon: FileText },
    { path: '/student-new/seats', label: 'Seat Availability', icon: BookOpen },
    { path: '/student-new/books', label: 'Books Library', icon: Library },
    { path: '/student-new/documents', label: 'Documents Vault', icon: ShieldCheck },
    { path: '/study-abroad', label: 'Study Abroad', icon: GraduationCap },
    { path: '/work-abroad', label: 'Work Abroad', icon: Briefcase },
    { path: '/trust', label: 'Trust Directory', icon: ShieldCheck },
  ],

  // ==================== JOB SEEKER (Work Abroad) ====================
  JOB_SEEKER: [
    { path: '/job-seeker', label: 'Dashboard', icon: LayoutDashboard },
    { divider: true, label: '🔍 Find Work' },
    { path: '/jobseeker-new/search', label: 'Job Search', icon: Search },
    { path: '/jobseeker-new/resume', label: 'My Resume', icon: FileText },
    { path: '/jobseeker-new/applications', label: 'My Applications', icon: Briefcase },
    { path: '/jobseeker-new/documents', label: 'Documents Vault', icon: ShieldCheck },
    { divider: true, label: '📋 Work Flow' },
    { path: '/job-seeker/vacancies', label: 'Vacancies', icon: Briefcase },
    { path: '/job-seeker/applications', label: 'Applications', icon: FileText },
    { path: '/job-seeker/interviews', label: 'Interviews', icon: Video },
    { path: '/job-seeker/offers', label: 'Offers', icon: Award },
    { path: '/job-seeker/deals', label: 'Deals', icon: Handshake },
    { path: '/job-seeker/accommodation', label: 'Accommodation', icon: Hotel },
    { path: '/job-seeker/visa', label: 'Work Visa', icon: ShieldCheck },
    { path: '/job-seeker/documents', label: 'Documents', icon: FileText },
    { path: '/job-seeker/resume-search', label: 'AI Resume Search', icon: Sparkles },
    { path: '/messages', label: 'Messages', icon: MessageSquare },
    { path: '/jobseeker-new/offers', label: 'Job Offers', icon: Award },
    { path: '/jobseeker-new/visa', label: 'Visa Tracker', icon: ShieldCheck },
    { path: '/jobseeker-new/accommodation', label: 'Accommodation', icon: Hotel },
    { path: '/work-abroad', label: 'Work Abroad', icon: Briefcase },
    { path: '/trust', label: 'Trust Directory', icon: ShieldCheck },
  ],

  // ==================== AGENT ====================
  AGENT: [
    { path: '/agent', label: 'Dashboard', icon: LayoutDashboard },
    { divider: true, label: '🎯 Actions' },
    { path: '/agent-new/candidates', label: 'Candidates', icon: Users },
    { path: '/agent-new/funnel', label: 'Funnel', icon: Briefcase },
    { path: '/agent-new/commission', label: 'My Commission', icon: DollarSign },
    { path: '/agent-new/referral', label: 'Referral', icon: Sparkles },
    { path: '/messages', label: 'Messages', icon: MessageSquare },
    { path: '/study-abroad', label: 'Study Abroad', icon: GraduationCap },
    { path: '/trust', label: 'Trust Directory', icon: ShieldCheck },
  ],

  // ==================== BROKER ====================
  BROKER: [
    { path: '/broker', label: 'Dashboard', icon: LayoutDashboard },
    { divider: true, label: '📊 Performance' },
    { path: '/broker-new/leaderboard', label: 'Agent Leaderboard', icon: Award },
    { path: '/broker-new/commission', label: 'Commission', icon: DollarSign },
    { path: '/broker-new/clients', label: 'Clients', icon: Building2 },
    { path: '/messages', label: 'Messages', icon: MessageSquare },
  ],

  // ==================== EMPLOYER ====================
  EMPLOYER: [
    { path: '/employer', label: 'Dashboard', icon: LayoutDashboard },
    { divider: true, label: '💼 Hiring' },
    { path: '/employer-new/post-job', label: 'Post Job', icon: Briefcase },
    { path: '/employer-new/applicants', label: 'Applicants', icon: Users },
    { path: '/employer-new/contracts', label: 'Contracts', icon: FileText },
    { path: '/messages', label: 'Messages', icon: MessageSquare },
  ],

  // ==================== ADMIN ====================
  ADMIN: [
    { path: '/admin', label: 'War Room', icon: LayoutDashboard },
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
    { divider: true, label: '📦 Operations' },
    { path: '/admin/bulk', label: 'Bulk Operations', icon: Package },
    { path: '/messages', label: 'Messages', icon: MessageSquare },
    { path: '/study-abroad', label: 'Study Abroad', icon: GraduationCap },
    { path: '/work-abroad', label: 'Work Abroad', icon: Briefcase },
    { path: '/trust', label: 'Trust Directory', icon: ShieldCheck },
  ],
};

export default function Sidebar({ role = 'STUDENT' }) {
  const { user, logout } = useAuth();
  const navItems = roleNavItems[role] || roleNavItems.STUDENT;
  const [isMobileOpen, setIsMobileOpen] = useState(false);

  return (
    <>
      {/* Mobile hamburger button — mobile only */}
      <button
        onClick={() => setIsMobileOpen(!isMobileOpen)}
        className="md:hidden fixed top-4 left-4 z-[9999] p-2.5 rounded-xl bg-slate-900 text-white shadow-lg"
        aria-label="Toggle menu"
      >
        {isMobileOpen ? (
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        ) : (
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        )}
      </button>

      {/* Mobile backdrop — tap to close */}
      {isMobileOpen && (
        <div
          onClick={() => setIsMobileOpen(false)}
          className="md:hidden fixed inset-0 bg-black/50 z-40"
        />
      )}

      {/* Sidebar */}
      <aside
        className={`w-64 bg-slate-900 text-white flex flex-col shadow-2xl
          fixed md:relative inset-y-0 left-0 z-50
          transform transition-transform duration-300 ease-in-out
          ${isMobileOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
        `}
      >
        {/* Logo */}
        <div className="p-6 border-b border-slate-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/30">
              <GraduationCap className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-bold">AI Glue</h1>
              <p className="text-xs text-slate-400">{role}</p>
            </div>
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
                key={item.path}
                to={item.path}
                end={item.path.split('/').length === 2}
                onClick={() => setIsMobileOpen(false)}
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