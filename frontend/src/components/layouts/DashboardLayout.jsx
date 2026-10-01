import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import Header from './Header';
import { useAuth } from '../../lib/auth-context';
import { MessageSquare } from 'lucide-react';

export default function DashboardLayout() {
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