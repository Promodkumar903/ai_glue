import { useState, useEffect } from 'react';
import { LogOut, Bell, Search, X, Menu } from 'lucide-react';
import { useAuth } from '../../lib/auth-context';
import { useNavigate } from 'react-router-dom';
import axios from '../../utils/axios';

export default function Header({ onMenuClick }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [showNotifications, setShowNotifications] = useState(false);
  const [notifications, setNotifications] = useState([]);

  // Fetch notifications
  useEffect(() => {
    const fetchNotifications = async () => {
      try {
        const res = await axios.get('/notifications').catch(() => ({ data: {} }));
        const data = res.data;
        let list = [];
        if (Array.isArray(data)) {
        list = data;
      } else if (data?.notifications && Array.isArray(data.notifications)) {
        list = data.notifications;
      }
        setNotifications(list);
      } catch (e) {
        console.error('Notifications error:', e);
      }
    };
    fetchNotifications();
  }, []);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  // ✅ Search Function — Click या Enter दोनों से चलेगा
  const handleSearch = () => {
    const q = searchQuery.trim();
    if (!q) return;
    // Search page पर भेजो (query parameter के साथ)
    navigate(`/search?q=${encodeURIComponent(q)}`);
  };

  // Enter Key के लिए
  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleSearch();
    }
  };

  return (
       <header className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-4 md:px-6 shrink-0 gap-2">
      {/* ===== Hamburger (mobile only) ===== */}
      <button
        onClick={onMenuClick}
        className="md:hidden p-2 text-gray-600 hover:bg-gray-100 rounded-lg"
        title="Menu"
      >
        <Menu className="w-5 h-5" />
      </button>

      {/* ===== Logo ===== */}
      <img src="/logo.svg" alt="AI Glue" className="h-8 w-auto shrink-0 hidden md:block" />

      {/* ===== Search Bar ===== */}
      <div className="flex items-center gap-2 flex-1 max-w-xl">
        <div className="relative w-full">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Search University, Candidate, Job..."
            className="w-full pl-9 pr-2 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* ✅ Search Button — Mobile + Desktop दोनों के लिए */}
        <button
          onClick={handleSearch}
          disabled={!searchQuery.trim()}
          className="bg-gradient-to-b from-blue-500 to-blue-700 hover:brightness-110 text-white px-4 py-2 rounded-lg font-semibold shadow-md disabled:opacity-50 transition flex items-center gap-2 shrink-0"
          title="Search"
        >
          <Search className="w-4 h-4" />
          <span className="hidden md:inline">Search</span>
        </button>
      </div>

      {/* ===== Right Side ===== */}
      <div className="flex items-center gap-2 md:gap-4">
        {/* Notification Bell */}
        <div className="relative">
          <button
            onClick={() => setShowNotifications(!showNotifications)}
            className="relative p-2 text-gray-400 hover:text-gray-600 rounded-full hover:bg-gray-100 transition"
            title="Notifications"
          >
            <Bell className="w-5 h-5" />
            {notifications.length > 0 && (
              <span className="absolute top-1 right-1 w-4 h-4 bg-red-500 rounded-full text-white text-[10px] flex items-center justify-center font-bold">
                {notifications.length > 9 ? '9+' : notifications.length}
              </span>
            )}
          </button>

          {/* Notifications Dropdown */}
          {showNotifications && (
            <div className="absolute right-0 mt-2 w-80 md:w-96 bg-white rounded-xl shadow-2xl border border-slate-200 z-50 max-h-[500px] overflow-hidden flex flex-col">
              {/* Header */}
              <div className="flex justify-between items-center px-4 py-3 border-b border-slate-100 bg-slate-50">
                <h3 className="font-semibold text-slate-800 text-sm">Notifications</h3>
                <button
                  onClick={() => setShowNotifications(false)}
                  className="p-1 rounded-full hover:bg-slate-200"
                >
                  <X className="w-4 h-4 text-slate-500" />
                </button>
              </div>

              {/* List */}
              <div className="flex-1 overflow-y-auto">
                {notifications.length === 0 ? (
                  <div className="p-8 text-center">
                    <Bell className="w-10 h-10 text-slate-300 mx-auto mb-2" />
                    <p className="text-sm text-slate-500">No notifications yet</p>
                  </div>
                ) : (
                  notifications.map((n, i) => (
                    <div
                      key={i}
                      className="px-4 py-3 border-b border-slate-100 hover:bg-slate-50 transition cursor-pointer"
                    >
                      <p className="text-sm text-slate-700">{n.message || n.type || 'Notification'}</p>
                      <p className="text-xs text-slate-400 mt-1">
                        {n.created_at ? new Date(n.created_at).toLocaleString() : ''}
                      </p>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        {/* User Info */}
        <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 bg-slate-50 rounded-lg border border-slate-200">
          <div className="w-7 h-7 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center text-white font-bold text-xs">
            {(user?.full_name || user?.email || 'U')[0].toUpperCase()}
          </div>
          <span className="text-sm font-semibold text-slate-700">
            {user?.role || 'USER'}
          </span>
        </div>

        {/* Logout */}
        <button
          onClick={handleLogout}
          className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-full transition"
          title="Logout"
        >
          <LogOut className="w-5 h-5" />
        </button>
      </div>
    </header>
  );
}