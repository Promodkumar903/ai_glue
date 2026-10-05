import { Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { useAuth } from './lib/auth-context';

// ========== ROLE PROTECTION ==========
function ProtectedRoute({ allowedRoles, children }) {
  const { user } = useAuth();
  if (!user) return <Navigate to="/login" />;
  if (!allowedRoles.includes(user.role)) {
    const rolePath = user.role.toLowerCase().replace('_', '-');
    return <Navigate to={`/${rolePath}`} />;
  }
  return children;
}

// ========== IMPORTS ==========
import Search from './pages/Search';
import StudentJobs from './pages/student/Jobs';
import StudentHousing from './pages/student/Housing';
import StudentDocuments from './pages/student/Documents';
import StudentVisa from './pages/student/Visa';
import StudentBooks from './pages/student/Books';
import BrokerAgents from './pages/broker/Agents';
import BrokerClients from './pages/broker/Clients';
import EmployerVacancies from './pages/employer/Vacancies';
import EmployerApplicants from './pages/employer/Applicants';
import Profile from './pages/Profile';
import ResumeSearch from './pages/ResumeSearch';
import StudentMyApplications from './pages/student-new/MyApplications';
import SeatAvailability from './pages/student-new/SeatAvailability';
import BooksLibrary from './pages/student-new/BooksLibrary';
import StudentDocumentsVault from './pages/student-new/DocumentsVault';
import AgentCandidates from './pages/agent-new/Candidates';
import AgentFunnel from './pages/agent-new/Funnel';
import AgentCommission from './pages/agent-new/Commission';
import ReferralLink from './pages/agent-new/ReferralLink';
import BrokerAgentLeaderboard from './pages/broker-new/AgentLeaderboard';
import BrokerCommissionTracker from './pages/broker-new/CommissionTracker';
import ClientDistribution from './pages/broker-new/ClientDistribution';
import PostJob from './pages/employer-new/PostJob';
import ApplicantTracking from './pages/employer-new/ApplicantTracking';
import Contracts from './pages/employer-new/Contracts';
import StudyAbroad from './pages/study-abroad/StudyAbroad';
import StudentEducation from './pages/student/Education';
import StudentLife from './pages/student/StudentLife';
import StudentJourney from './pages/student/Journey';
import StudentScholarships from './pages/student/Scholarships';
import JobSeekerVacancies from './pages/job-seeker/Vacancies';
import JobSeekerInterviews from './pages/job-seeker/Interviews';
import JobSeekerOffers from './pages/job-seeker/Offers';
import JobSeekerDeals from './pages/job-seeker/Deals';
import JobSeekerAccommodation from './pages/job-seeker/Accommodation';
import WorkAbroad from './pages/work-abroad/WorkAbroad';
import TrustDirectory from './pages/trust/TrustDirectory';
import EducationControl from './pages/admin-new/EducationControl';
import VendorControl from './pages/admin-new/VendorControl';
import JobSeekerCommand from './pages/admin-new/JobSeekerCommand';
import StudentCommand from './pages/admin-new/StudentCommand';
import AgentBrokerCommand from './pages/admin-new/AgentBrokerCommand';
import RevenueAnalytics from './pages/admin-new/RevenueAnalytics';
import BulkOperations from './pages/admin-new/BulkOperations';
import UploadResume from './pages/jobseeker-new/UploadResume';
import JobSearch from './pages/jobseeker-new/JobSearch';
import MyApplications from './pages/jobseeker-new/MyApplications';
import DocumentsVault from './pages/jobseeker-new/DocumentsVault';
import Offers from './pages/jobseeker-new/Offers';
import VisaTracker from './pages/jobseeker-new/VisaTracker';
import Accommodation from './pages/jobseeker-new/Accommodation';
import ApplyCollege from './pages/student-new/ApplyCollege';

import Sidebar from './components/layouts/Sidebar';
import Header from './components/layouts/Header';

import Login from './pages/Login';
import Register from './pages/Register';
import ForgotPassword from './pages/ForgotPassword';
import ResetPassword from './pages/ResetPassword';

import StudentDashboard from './pages/StudentDashboard';
import JobSeekerDashboard from './pages/JobSeekerDashboard';
import AgentDashboard from './pages/AgentDashboard';
import BrokerDashboard from './pages/BrokerDashboard';
import EmployerDashboard from './pages/EmployerDashboard';
import AdminDashboard from './pages/AdminDashboard';

import Messages from './pages/Messages';
import SubPage from './pages/SubPage';

// Layout Component
function Layout() {
  const { user } = useAuth();
  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar role={user?.role || 'STUDENT'} />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto p-6 bg-gray-50">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

function App() {
  const { user } = useAuth();
  const rolePath = user?.role?.toLowerCase().replace('_', '-') || 'student';

  return (
    <Routes>
      {/* Public */}
      <Route path="/login" element={user ? <Navigate to={`/${rolePath}`} /> : <Login />} />
      <Route path="/register" element={user ? <Navigate to={`/${rolePath}`} /> : <Register />} />
      <Route path="/forgot-password" element={<ForgotPassword />} />
      <Route path="/reset-password" element={<ResetPassword />} />

      {/* Protected with Layout */}
      <Route element={user ? <Layout /> : <Navigate to="/login" />}>
        
        {/* ========== STUDENT ROUTES ========== */}
        <Route path="/student" element={
          <ProtectedRoute allowedRoles={['STUDENT']}><StudentDashboard /></ProtectedRoute>
        } />
        <Route path="/student/jobs" element={
          <ProtectedRoute allowedRoles={['STUDENT']}><StudentJobs /></ProtectedRoute>
        } />
        <Route path="/student/housing" element={
          <ProtectedRoute allowedRoles={['STUDENT']}><StudentHousing /></ProtectedRoute>
        } />
        <Route path="/student/documents" element={
          <ProtectedRoute allowedRoles={['STUDENT']}><StudentDocuments /></ProtectedRoute>
        } />
        <Route path="/student/visa" element={
          <ProtectedRoute allowedRoles={['STUDENT']}><StudentVisa /></ProtectedRoute>
        } />
        <Route path="/student/books" element={
          <ProtectedRoute allowedRoles={['STUDENT']}><StudentBooks /></ProtectedRoute>
        } />
        <Route path="/student/education" element={
          <ProtectedRoute allowedRoles={['STUDENT']}><StudentEducation /></ProtectedRoute>
        } />
        <Route path="/student/life" element={
          <ProtectedRoute allowedRoles={['STUDENT']}><StudentLife /></ProtectedRoute>
        } />
        <Route path="/student/journey" element={
          <ProtectedRoute allowedRoles={['STUDENT']}><StudentJourney /></ProtectedRoute>
        } />
        <Route path="/student/scholarships" element={
          <ProtectedRoute allowedRoles={['STUDENT']}><StudentScholarships /></ProtectedRoute>
        } />
        <Route path="/student-new/applications" element={
          <ProtectedRoute allowedRoles={['STUDENT']}><StudentMyApplications /></ProtectedRoute>
        } />
        <Route path="/student-new/seats" element={
          <ProtectedRoute allowedRoles={['STUDENT']}><SeatAvailability /></ProtectedRoute>
        } />
        <Route path="/student-new/books" element={
          <ProtectedRoute allowedRoles={['STUDENT']}><BooksLibrary /></ProtectedRoute>
        } />
        <Route path="/student-new/documents" element={
          <ProtectedRoute allowedRoles={['STUDENT']}><StudentDocumentsVault /></ProtectedRoute>
        } />
        <Route path="/student-new/apply" element={
          <ProtectedRoute allowedRoles={['STUDENT']}><ApplyCollege /></ProtectedRoute>
        } />

        {/* ========== JOB SEEKER ROUTES ========== */}
        <Route path="/job-seeker" element={
          <ProtectedRoute allowedRoles={['JOB_SEEKER']}><JobSeekerDashboard /></ProtectedRoute>
        } />
        <Route path="/job-seeker/vacancies" element={
          <ProtectedRoute allowedRoles={['JOB_SEEKER']}><JobSeekerVacancies /></ProtectedRoute>
        } />
        <Route path="/job-seeker/interviews" element={
          <ProtectedRoute allowedRoles={['JOB_SEEKER']}><JobSeekerInterviews /></ProtectedRoute>
        } />
        <Route path="/job-seeker/offers" element={
          <ProtectedRoute allowedRoles={['JOB_SEEKER']}><JobSeekerOffers /></ProtectedRoute>
        } />
        <Route path="/job-seeker/deals" element={
          <ProtectedRoute allowedRoles={['JOB_SEEKER']}><JobSeekerDeals /></ProtectedRoute>
        } />
        <Route path="/job-seeker/accommodation" element={
          <ProtectedRoute allowedRoles={['JOB_SEEKER']}><JobSeekerAccommodation /></ProtectedRoute>
        } />
        <Route path="/jobseeker-new/resume" element={
          <ProtectedRoute allowedRoles={['JOB_SEEKER']}><UploadResume /></ProtectedRoute>
        } />
        <Route path="/jobseeker-new/search" element={
          <ProtectedRoute allowedRoles={['JOB_SEEKER']}><JobSearch /></ProtectedRoute>
        } />
        <Route path="/jobseeker-new/applications" element={
          <ProtectedRoute allowedRoles={['JOB_SEEKER']}><MyApplications /></ProtectedRoute>
        } />
        <Route path="/jobseeker-new/documents" element={
          <ProtectedRoute allowedRoles={['JOB_SEEKER']}><DocumentsVault /></ProtectedRoute>
        } />
        <Route path="/jobseeker-new/offers" element={
          <ProtectedRoute allowedRoles={['JOB_SEEKER']}><Offers /></ProtectedRoute>
        } />
        <Route path="/jobseeker-new/visa" element={
          <ProtectedRoute allowedRoles={['JOB_SEEKER']}><VisaTracker /></ProtectedRoute>
        } />
        <Route path="/jobseeker-new/accommodation" element={
          <ProtectedRoute allowedRoles={['JOB_SEEKER']}><Accommodation /></ProtectedRoute>
        } />

        {/* ========== AGENT ROUTES ========== */}
        <Route path="/agent" element={
          <ProtectedRoute allowedRoles={['AGENT']}><AgentDashboard /></ProtectedRoute>
        } />
        <Route path="/agent-new/candidates" element={
          <ProtectedRoute allowedRoles={['AGENT']}><AgentCandidates /></ProtectedRoute>
        } />
        <Route path="/agent-new/funnel" element={
          <ProtectedRoute allowedRoles={['AGENT']}><AgentFunnel /></ProtectedRoute>
        } />
        <Route path="/agent-new/commission" element={
          <ProtectedRoute allowedRoles={['AGENT']}><AgentCommission /></ProtectedRoute>
        } />
        <Route path="/agent-new/referral" element={
          <ProtectedRoute allowedRoles={['AGENT']}><ReferralLink /></ProtectedRoute>
        } />

        {/* ========== BROKER ROUTES ========== */}
        <Route path="/broker" element={
          <ProtectedRoute allowedRoles={['BROKER']}><BrokerDashboard /></ProtectedRoute>
        } />
        <Route path="/broker-new/leaderboard" element={
          <ProtectedRoute allowedRoles={['BROKER']}><BrokerAgentLeaderboard /></ProtectedRoute>
        } />
        <Route path="/broker-new/commission" element={
          <ProtectedRoute allowedRoles={['BROKER']}><BrokerCommissionTracker /></ProtectedRoute>
        } />
        <Route path="/broker-new/clients" element={
          <ProtectedRoute allowedRoles={['BROKER']}><ClientDistribution /></ProtectedRoute>
        } />

        {/* ========== EMPLOYER ROUTES ========== */}
        <Route path="/employer" element={
          <ProtectedRoute allowedRoles={['EMPLOYER']}><EmployerDashboard /></ProtectedRoute>
        } />
        <Route path="/employer-new/post-job" element={
          <ProtectedRoute allowedRoles={['EMPLOYER']}><PostJob /></ProtectedRoute>
        } />
        <Route path="/employer-new/applicants" element={
          <ProtectedRoute allowedRoles={['EMPLOYER']}><ApplicantTracking /></ProtectedRoute>
        } />
        <Route path="/employer-new/contracts" element={
          <ProtectedRoute allowedRoles={['EMPLOYER']}><Contracts /></ProtectedRoute>
        } />

        {/* ========== ADMIN ROUTES ========== */}
        <Route path="/admin" element={
          <ProtectedRoute allowedRoles={['ADMIN']}><AdminDashboard /></ProtectedRoute>
        } />
        <Route path="/admin/agents-brokers" element={
          <ProtectedRoute allowedRoles={['ADMIN']}><AgentBrokerCommand /></ProtectedRoute>
        } />
        <Route path="/admin/revenue" element={
          <ProtectedRoute allowedRoles={['ADMIN']}><RevenueAnalytics /></ProtectedRoute>
        } />
        <Route path="/admin/bulk" element={
          <ProtectedRoute allowedRoles={['ADMIN']}><BulkOperations /></ProtectedRoute>
        } />
        <Route path="/admin/education" element={
          <ProtectedRoute allowedRoles={['ADMIN']}><EducationControl /></ProtectedRoute>
        } />
        <Route path="/admin/vendors" element={
          <ProtectedRoute allowedRoles={['ADMIN']}><VendorControl /></ProtectedRoute>
        } />
        <Route path="/admin/jobseekers" element={
          <ProtectedRoute allowedRoles={['ADMIN']}><JobSeekerCommand /></ProtectedRoute>
        } />
        <Route path="/admin/students" element={
          <ProtectedRoute allowedRoles={['ADMIN']}><StudentCommand /></ProtectedRoute>
        } />

        {/* ========== COMMON ROUTES (All Roles) ========== */}
        <Route path="/profile" element={<Profile />} />
        <Route path="/messages" element={<Messages />} />
        <Route path="/study-abroad" element={<StudyAbroad />} />
        <Route path="/work-abroad" element={<WorkAbroad />} />
        <Route path="/trust" element={<TrustDirectory />} />
      </Route>

      {/* Default */}
      <Route path="/" element={<Navigate to={user ? `/${rolePath}` : '/login'} />} />
      <Route path="*" element={<Navigate to="/login" />} />
      <Route path="/search" element={<Search />} />
    </Routes>
  );
}

export default App;