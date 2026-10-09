import { useState, useEffect } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import {
  LayoutDashboard, Users, Building2, Briefcase, FileText,
  Search, MessageSquare, ShieldCheck, GraduationCap,
  DollarSign, BookOpen, Home, LogOut, Video, Award,
  Handshake, Hotel, Sparkles, Library, Heart, Phone,
  GraduationCap as EduIcon, Store, Target, TrendingUp, Package, Bell,
  ChevronDown, ChevronRight, Bot, Wallet, UserCheck, Globe
} from 'lucide-react';
import { useAuth } from '../../lib/auth-context';

const roleNavItems = {
  STUDENT: [
    { path: '/student', label: 'Dashboard', icon: LayoutDashboard },
    {
      label: 'Study', icon: GraduationCap, children: [
        { path: '/student/education', label: 'Education', icon: GraduationCap },
        { path: '/student/life', label: 'Student Life', icon: Heart },
        { path: '/student/journey', label: 'Journey', icon: Sparkles },
        { path: '/student/housing', label: 'Housing', icon: Home },
        { path: '/student/books', label: 'Books', icon: Library },
        { path: '/student/visa-cases', label: 'Student Visa', icon: ShieldCheck },
        { path: '/student/visa', label: 'Student Visa', icon: ShieldCheck },
        { path: '/student/scholarships', label: 'Scholarships', icon: Award },
        { path: '/student/documents', label: 'Documents', icon: FileText },
      ]
    },
    {
      label: 'Applications', icon: FileText, children: [
        { path: '/student-new/applications', label: 'My Applications', icon: FileText },
        { path: '/student-new/apply', label: 'Apply to College', icon: GraduationCap },
        { path: '/student-new/seats', label: 'Seat Availability', icon: BookOpen },
        { path: '/student-new/books', label: 'Books Library', icon: Library },
        { path: '/student-new/documents', label: 'Documents Vault', icon: ShieldCheck },
        { path: '/student-new/checklist', label: 'Document Checklist', icon: FileText },
      ]
    },
    {
      label: 'AI Tools', icon: Bot, children: [
        { path: '/student-new/verify', label: 'AI Verify Document', icon: ShieldCheck },
        { path: '/student-new/resume-converter', label: 'AI Resume Converter', icon: FileText },
      ]
    },
    {
      label: 'Explore', icon: Globe, children: [
        { path: '/study-abroad', label: 'Study Abroad', icon: GraduationCap },
        { path: '/work-abroad', label: 'Work Abroad', icon: Briefcase },
        { path: '/trust', label: 'Trust Directory', icon: ShieldCheck },
      ]
    },
    { path: '/messages', label: 'Messages', icon: MessageSquare },
  ],

  JOB_SEEKER: [
    { path: '/job-seeker', label: 'Dashboard', icon: LayoutDashboard },
    {
      label: 'Find Work', icon: Search, children: [
        { path: '/jobseeker-new/search', label: 'Job Search', icon: Search },
        { path: '/jobseeker-new/resume', label: 'My Resume', icon: FileText },
        { path: '/jobseeker-new/applications', label: 'Applications', icon: Briefcase },
        { path: '/jobseeker-new/documents', label: 'Documents Vault', icon: ShieldCheck },
      ]
    },
    {
      label: 'AI Tools', icon: Bot, children: [
        { path: '/jobseeker-new/resume-builder', label: 'AI Job Resume', icon: Sparkles },
        { path: '/job-seeker/resume-search', label: 'AI Resume Search', icon: Sparkles },
      ]
    },
    {
      label: 'Work Flow', icon: Briefcase, children: [
        { path: '/job-seeker/vacancies', label: 'Vacancies', icon: Briefcase },
        { path: '/job-seeker/applications', label: 'My Applications', icon: FileText },
        { path: '/job-seeker/interviews', label: 'Interviews', icon: Video },
        { path: '/jobseeker-new/offers', label: 'Offers', icon: Award },
        { path: '/job-seeker/deals', label: 'Deals', icon: Handshake },
      ]
    },
    {
      label: 'Post Landing', icon: Hotel, children: [
        { path: '/jobseeker-new/accommodation', label: 'Accommodation', icon: Hotel },
        { path: '/jobseeker-new/visa', label: 'Work Visa', icon: ShieldCheck },
        { path: '/jobseeker-new/visa-cases', label: 'Work Visa', icon: ShieldCheck },
        { path: '/job-seeker/documents', label: 'Documents', icon: FileText },
      ]
    },
    { path: '/work-abroad', label: 'Work Abroad', icon: Briefcase },
    { path: '/trust', label: 'Trust Directory', icon: ShieldCheck },
    { path: '/messages', label: 'Messages', icon: MessageSquare },
  ],

  AGENT: [
    { path: '/agent', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/agent/dashboard', label: 'CRM Dashboard', icon: Target },
    {
      label: 'Leads & CRM', icon: Users, children: [
        { path: '/agent/leads', label: 'Leads (CRM)', icon: Users },
        { path: '/agent/followups', label: 'Follow-ups', icon: MessageSquare },
        { path: '/agent/applications', label: 'Applications', icon: FileText },
        { path: '/agent-new/candidates', label: 'Candidates', icon: Users },
        { path: '/agent-new/funnel', label: 'Funnel', icon: Briefcase },
      ]
    },
    {
      label: 'Documents', icon: FileText, children: [
        { path: '/student-new/checklist', label: 'Document Checklist', icon: FileText },
        { path: '/student-new/verify', label: 'AI Verify', icon: ShieldCheck },
        { path: '/student-new/documents', label: 'Documents Vault', icon: ShieldCheck },
      ]
    },
    {
      label: 'Visa & Offers', icon: ShieldCheck, children: [
        { path: '/agent/visa', label: 'Visa Tracking', icon: ShieldCheck },
        { path: '/jobseeker-new/offers', label: 'Offers', icon: Award },
        { path: '/employer-new/contracts', label: 'Contracts', icon: FileText },
      ]
    },
    {
      label: 'AI Services', icon: Bot, children: [
        { path: '/admin/orchestration', label: 'AI Orchestration', icon: Sparkles },
        { path: '/admin/match/job-seeker', label: 'Match Job Seeker', icon: Target },
        { path: '/admin/match/student', label: 'Match Student', icon: Users },
      ]
    },
    {
      label: 'Money & Grade', icon: Wallet, children: [
        { path: '/agent-new/commission', label: 'My Commission', icon: DollarSign },
        { path: '/agent/grades', label: 'My Grade', icon: Award },
        { path: '/agent-new/referral', label: 'Referral', icon: Sparkles },
      ]
    },
    {
      label: 'Team', icon: UserCheck, children: [
        { path: '/profile', label: 'My Profile', icon: Users },
        { path: '/my-subscription', label: 'Subscription', icon: FileText },
      ]
    },
    { path: '/study-abroad', label: 'Study Abroad', icon: GraduationCap },
    { path: '/trust', label: 'Trust Directory', icon: ShieldCheck },
    { path: '/messages', label: 'Messages', icon: MessageSquare },
  ],

  BROKER: [
    { path: '/broker', label: 'Dashboard', icon: LayoutDashboard },
    {
      label: 'Performance', icon: TrendingUp, children: [
        { path: '/broker-new/leaderboard', label: 'Agent Leaderboard', icon: Award },
        { path: '/broker-new/commission', label: 'Commission', icon: DollarSign },
        { path: '/broker-new/clients', label: 'Clients', icon: Building2 },
      ]
    },
    { path: '/messages', label: 'Messages', icon: MessageSquare },
  ],

  EMPLOYER: [
    { path: '/employer', label: 'Dashboard', icon: LayoutDashboard },
    {
      label: 'Hiring', icon: Briefcase, children: [
        { path: '/employer-new/post-job', label: 'Post Job', icon: Briefcase },
        { path: '/employer-new/applicants', label: 'Applicants', icon: Users },
        { path: '/employer-new/contracts', label: 'Contracts', icon: FileText },
      ]
    },
    { path: '/messages', label: 'Messages', icon: MessageSquare },
  ],

  ADMIN: [
    { path: '/admin', label: 'War Room', icon: LayoutDashboard },
    {
  label: 'OIE Jobs', icon: Briefcase, children: [
    { path: '/admin/oie/jobs?tab=jobs', label: 'Jobs', icon: Briefcase },
    { path: '/admin/oie/jobs?tab=registry', label: 'Job Agents', icon: Building2 },
    { path: '/admin/oie/jobs?tab=requests', label: 'Requests', icon: MessageSquare },
    { path: '/admin/oie/jobs?tab=log', label: 'HR Contacts', icon: Phone },
  ]
},
{
  label: 'OIE Studies', icon: GraduationCap, children: [
    { path: '/admin/oie/studies?tab=universities', label: 'Universities', icon: GraduationCap },
    { path: '/admin/oie/studies?tab=registry', label: 'Study Agents', icon: Building2 },
    { path: '/admin/oie/studies?tab=requests', label: 'Requests', icon: MessageSquare },
    { path: '/admin/oie/studies?tab=contacts', label: 'Uni Contacts', icon: Phone },
  ]
},
    {
      label: 'Education', icon: EduIcon, children: [
        { path: '/admin/education', label: 'Education Control', icon: EduIcon },
        { path: '/admin/vendors', label: 'Vendor Control', icon: Store },
      ]
    },
    {
      label: 'Commands', icon: Target, children: [
        { path: '/admin/jobseekers', label: 'Job Seeker Command', icon: Target },
        { path: '/admin/students', label: 'Student Command', icon: Users },
        { path: '/admin/agents-brokers', label: 'Agent & Broker', icon: Handshake },
      ]
    },
    {
      label: 'AI Tools', icon: Bot, children: [
        { path: '/admin/orchestration', label: 'AI Orchestration', icon: Sparkles },
        { path: '/admin/match/job-seeker', label: 'Match Job Seeker', icon: Target },
        { path: '/admin/match/student', label: 'Match Student', icon: Users },
        { path: '/admin/match/company', label: 'Match Company', icon: Building2 },
        { path: '/admin/search', label: 'Universal Search', icon: Search },
      ]
    },
    {
      label: 'Revenue', icon: TrendingUp, children: [
        { path: '/admin/revenue', label: 'Revenue & Reports', icon: TrendingUp },
        { path: '/admin/payment-settings', label: 'Payment Settings', icon: FileText },
        { path: '/admin/pending-payments', label: 'Pending Payments', icon: FileText },
      ]
    },
    {
      label: 'Marketing', icon: Store, children: [
        { path: '/admin/promotions', label: 'Promotions', icon: FileText },
        { path: '/admin/ads', label: 'Ads & Banners', icon: FileText },
        { path: '/admin/email', label: 'Email Composer', icon: FileText },
      ]
    },
    {
      label: 'Operations', icon: Package, children: [
        { path: '/admin/analytics', label: 'Analytics', icon: TrendingUp },
        { path: '/admin/bulk', label: 'Bulk Operations', icon: Package },
        { path: '/pricing', label: 'Pricing Plans', icon: FileText },
        { path: '/my-subscription', label: 'My Subscription', icon: FileText },
        { path: '/my-payments', label: 'My Payments', icon: FileText },
      ]
    },
    { path: '/messages', label: 'Messages', icon: MessageSquare },
  ],
};

// ============================================================
// NESTED ITEM RENDERER
// ============================================================
function NestedItem({ item, idx, openGroups, toggleGroup, onClose, currentPath }) {
  const hasChildren = item.children && item.children.length > 0;

  // Divider
  if (item.divider) {
    return (
      <div className="pt-3 pb-1 px-4">
        <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
          {item.label}
        </p>
      </div>
    );
  }

  const Icon = item.icon;

  // Nested group
  if (hasChildren) {
    const groupKey = `grp-${idx}-${item.label}`;
    const isOpen = openGroups[groupKey];
    const hasActiveChild = item.children.some((c) => c.path && currentPath.startsWith(c.path));

    return (
      <div>
        <button
          onClick={() => toggleGroup(groupKey)}
          className={`w-full flex items-center justify-between gap-3 px-4 py-2.5 rounded-lg transition-all duration-200 ${
            hasActiveChild
              ? 'bg-slate-800 text-white'
              : 'text-slate-300 hover:bg-slate-800 hover:text-white'
          }`}
        >
          <div className="flex items-center gap-3">
            <Icon className="w-5 h-5" />
            <span className="text-sm font-medium">{item.label}</span>
          </div>
          {isOpen ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
        </button>

        {isOpen && (
          <div className="ml-5 mt-1 border-l border-slate-700 pl-2 space-y-0.5">
            {item.children.map((child, cidx) => {
              const ChildIcon = child.icon;
              const isChildActive = currentPath === child.path || currentPath.startsWith(child.path + '/');
              return (
                <NavLink
                  key={`${child.path}-${cidx}`}
                  to={child.path}
                  onClick={onClose}
                  className={`flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs transition ${
                    isChildActive
                      ? 'bg-blue-600 text-white'
                      : 'text-slate-400 hover:bg-slate-800 hover:text-white'
                  }`}
                >
                  <ChildIcon className="w-4 h-4" />
                  <span className="font-medium">{child.label}</span>
                </NavLink>
              );
            })}
          </div>
        )}
      </div>
    );
  }

  // Simple link
  return (
    <NavLink
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
}

// ============================================================
// MAIN SIDEBAR
// ============================================================
export default function Sidebar({ role = 'STUDENT', isOpen, onClose }) {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navItems = roleNavItems[role] || roleNavItems.STUDENT;
  const [openGroups, setOpenGroups] = useState({});

  // Auto-expand group if current route matches any child
  useEffect(() => {
    const newOpen = { ...openGroups };
    navItems.forEach((item, idx) => {
      if (item.children) {
        const groupKey = `grp-${idx}-${item.label}`;
        const hasActive = item.children.some((c) => c.path && location.pathname.startsWith(c.path));
        if (hasActive) {
          newOpen[groupKey] = true;
        }
      }
    });
    setOpenGroups(newOpen);
    // eslint-disable-next-line
  }, [location.pathname, role]);

  const toggleGroup = (key) => {
    setOpenGroups((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  return (
    <>
      {/* Mobile backdrop */}
      {isOpen && (
        <div
          onClick={onClose}
          className="fixed inset-0 bg-black/50 z-40 md:hidden"
        />
      )}

      <aside
        className={`
          fixed md:static inset-y-0 left-0 z-50
          w-64 bg-slate-900 text-white flex flex-col shadow-2xl
          transform transition-transform duration-300
          ${isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
        `}
      >
        {/* Logo */}
        <div className="p-6 border-b border-slate-700">
          <div className="flex flex-col gap-1">
            <img src="/logo-dark.svg" alt="AI Glue" className="h-10 w-auto" />
            <p className="text-xs text-slate-400">{role}</p>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
          {navItems.map((item, idx) => (
            <NestedItem
              key={`nav-${idx}-${item.label || item.path}`}
              item={item}
              idx={idx}
              openGroups={openGroups}
              toggleGroup={toggleGroup}
              onClose={onClose}
              currentPath={location.pathname}
            />
          ))}
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