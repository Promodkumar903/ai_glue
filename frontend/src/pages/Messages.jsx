import { useState, useEffect, useRef } from 'react';
import { useAuth } from '../lib/auth-context';
import { Send, Shield, AlertTriangle, User, Search } from 'lucide-react';
import axios from '../utils/axios';

export default function Messages() {
  const { user } = useAuth();
  const [messages, setMessages] = useState([]);
  const [sentMessages, setSentMessages] = useState([]);
  const [input, setInput] = useState('');
  const [selectedUser, setSelectedUser] = useState(null);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [policy, setPolicy] = useState(null);
  const messagesEndRef = useRef(null);

  // Fetch policy + messages + users
  useEffect(() => {
    const fetchData = async () => {
      try {
        const policyRes = await axios.get('/communication/policy').catch(() => ({ data: null }));
        setPolicy(policyRes.data);

        const inboxRes = await axios.get('/communication/messages/inbox').catch(() => ({ data: [] }));
        setMessages(Array.isArray(inboxRes.data) ? inboxRes.data : []);

        const sentRes = await axios.get('/communication/messages/sent').catch(() => ({ data: [] }));
        setSentMessages(Array.isArray(sentRes.data) ? sentRes.data : []);

        // Fetch users (for demo — from admin endpoint or fallback)
        const usersRes = await axios.get('/admin/users').catch(() => ({ data: [] }));
        const filteredUsers = (Array.isArray(usersRes.data) ? usersRes.data : [])
          .filter(u => u.id !== user?.id)
          .slice(0, 10);
        setUsers(filteredUsers);
      } catch (e) {
        console.error('Messages fetch error:', e);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [user]);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, selectedUser]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || !selectedUser) return;

    try {
      const res = await axios.post('/communication/messages/send', {
        receiver_id: selectedUser.id,
        message: input,
        context_type: 'GENERAL',
      });

      setSentMessages(prev => [res.data, ...prev]);
      setInput('');

      // Show muted warning
      if (res.data.is_muted) {
        alert('⚠️ Your message contained restricted terms and was muted.');
      } else if (res.data.message !== input) {
        alert('⚠️ Your message contained contact info and was auto-redacted.');
      }
    } catch (err) {
      alert('Failed to send. ' + (err.response?.data?.detail || ''));
    }
  };

  // Combine inbox + sent for selected user
  const conversationMessages = [
    ...messages.filter(m => m.sender_id === selectedUser?.id || m.receiver_id === selectedUser?.id),
    ...sentMessages.filter(m => m.sender_id === selectedUser?.id || m.receiver_id === selectedUser?.id),
  ].sort((a, b) => new Date(a.created_at) - new Date(b.created_at));

  return (
    <div className="h-screen flex flex-col bg-slate-50">
      {/* Header */}
      <div className="bg-white border-b px-6 py-4 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-800">💬 Messages</h1>
          <p className="text-sm text-slate-500">Platform-Only Secure Communication</p>
        </div>
        <div className="flex items-center gap-2 bg-green-50 border border-green-200 rounded-lg px-3 py-1.5 text-xs font-medium text-green-700">
          <Shield className="w-4 h-4" />
          Walled Garden Active
        </div>
      </div>

      {/* Policy Banner */}
      {policy && (
        <div className="bg-yellow-50 border-b border-yellow-200 px-6 py-2 flex items-center gap-2 text-xs text-yellow-800">
          <AlertTriangle className="w-4 h-4" />
          <span>
            <strong>Restrictions:</strong> Email, Phone, WhatsApp, Social Media, and terms like
            "contract", "payment", "commission" are automatically muted/redacted.
          </span>
        </div>
      )}

      <div className="flex-1 flex overflow-hidden">
        {/* Left: Users List */}
        <div className="w-80 bg-white border-r flex flex-col">
          <div className="p-4 border-b">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search users..."
                className="w-full pl-10 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
          <div className="flex-1 overflow-y-auto">
            {loading ? (
              <p className="text-center text-gray-400 py-8 text-sm">Loading...</p>
            ) : users.length === 0 ? (
              <p className="text-center text-gray-400 py-8 text-sm">No users found</p>
            ) : (
              users.map(u => (
                <button
                  key={u.id}
                  onClick={() => setSelectedUser(u)}
                  className={`w-full text-left px-4 py-3 border-b hover:bg-slate-50 transition ${
                    selectedUser?.id === u.id ? 'bg-blue-50 border-l-4 border-l-blue-500' : ''
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center text-white font-bold">
                      {(u.full_name || u.email || 'U')[0].toUpperCase()}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-semibold text-slate-800 truncate">
                        {u.full_name || u.email}
                      </p>
                      <p className="text-xs text-slate-500 truncate">{u.email}</p>
                    </div>
                  </div>
                </button>
              ))
            )}
          </div>
        </div>

        {/* Right: Chat Area */}
        <div className="flex-1 flex flex-col bg-slate-50">
          {selectedUser ? (
            <>
              {/* Chat Header */}
              <div className="bg-white border-b px-6 py-3 flex items-center gap-3">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center text-white font-bold">
                  {(selectedUser.full_name || selectedUser.email || 'U')[0].toUpperCase()}
                </div>
                <div>
                  <p className="font-semibold text-slate-800">
                    {selectedUser.full_name || selectedUser.email}
                  </p>
                  <p className="text-xs text-slate-500">Platform-Verified User</p>
                </div>
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-6 space-y-3">
                {conversationMessages.length === 0 ? (
                  <p className="text-center text-gray-400 py-10 text-sm">
                    No messages yet. Start the conversation!
                  </p>
                ) : (
                  conversationMessages.map(msg => {
                    const isMine = msg.sender_id === user?.id;
                    return (
                      <div key={msg.id} className={`flex ${isMine ? 'justify-end' : 'justify-start'}`}>
                        <div className={`max-w-md px-4 py-2 rounded-2xl ${
                          isMine ? 'bg-blue-600 text-white' : 'bg-white border text-slate-800'
                        }`}>
                          <p className={`text-sm ${msg.is_muted ? 'italic opacity-75' : ''}`}>
                            {msg.is_muted ? '🔇 [MUTED: Restricted terms detected]' : msg.message}
                          </p>
                          <p className={`text-[10px] mt-1 ${isMine ? 'text-blue-100' : 'text-slate-400'}`}>
                            {new Date(msg.created_at).toLocaleString()}
                          </p>
                        </div>
                      </div>
                    );
                  })
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Input */}
              <form onSubmit={handleSend} className="bg-white border-t p-4 flex gap-2">
                <input
                  type="text"
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  placeholder="Type your message... (contact info will be redacted)"
                  className="flex-1 px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                />
                <button
                  type="submit"
                  disabled={!input.trim()}
                  className="bg-gradient-to-b from-blue-500 to-blue-700 hover:brightness-110 text-white px-6 py-3 rounded-xl font-semibold shadow-lg flex items-center gap-2 disabled:opacity-50 transition"
                >
                  <Send className="w-4 h-4" />
                  Send
                </button>
              </form>
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center">
                <User className="w-16 h-16 text-slate-300 mx-auto mb-4" />
                <p className="text-slate-500">Select a user to start messaging</p>
                <p className="text-xs text-slate-400 mt-2">All communication is platform-only and audited</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}