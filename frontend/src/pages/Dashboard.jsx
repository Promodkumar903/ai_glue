import { useAuth } from '../lib/auth-context';

export default function Dashboard() {
  const { user, logout } = useAuth();

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-4xl mx-auto bg-white p-6 rounded shadow">
        <div className="flex justify-between items-center mb-4">
          <h1 className="text-2xl font-bold">Dashboard</h1>
          <button onClick={logout} className="bg-red-500 text-white px-4 py-2 rounded">
            Logout
          </button>
        </div>
        <div className="border-t pt-4">
          <p><strong>Name:</strong> {user?.full_name || 'User'}</p>
          <p><strong>Email:</strong> {user?.email || 'No email'}</p>
          <p><strong>Status:</strong> {user?.status || 'Active'}</p>
        </div>
      </div>
    </div>
  );
}