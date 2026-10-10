import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Video, Calendar, Clock, Plus, X, User } from 'lucide-react';
import axios from '../utils/axios';
import { useAuth } from '../lib/auth-context';

export default function Interviews() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const userId = user?.id || 'test_student_001';
  const userRole = user?.role || 'JOB_SEEKER';

  const [tab, setTab] = useState('with-me'); // with-me | by-me
  const [interviews, setInterviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState({
    title: 'Interview',
    candidate_id: '',
    candidate_email: '',
    candidate_name: '',
    scheduled_at: '',
    duration_minutes: 30,
    notes: '',
  });
  const [creating, setCreating] = useState(false);

  const canSchedule = ['ADMIN', 'AGENT', 'EMPLOYER', 'BROKER', 'HR'].includes(userRole);

  useEffect(() => {
    loadInterviews();
  }, [tab]);

  const loadInterviews = async () => {
    setLoading(true);
    try {
      const endpoint = tab === 'with-me'
        ? `/interview/interview/my?user_id=${userId}`
        : `/interview/interview/created?user_id=${userId}`;
      const r = await axios.get(endpoint);
      setInterviews(r.data.interviews || []);
    } catch (e) {
      setInterviews([]);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    if (!form.candidate_id || !form.title) {
      alert('Title and Candidate ID required');
      return;
    }
    setCreating(true);
    try {
      const r = await axios.post(
        `/interview/interview/create?interviewer_id=${userId}&interviewer_name=${encodeURIComponent(user?.full_name || 'HR')}&interviewer_role=${userRole}`,
        form
      );
      alert(`✅ Interview created!\nRoom: ${r.data.room_id}\nInvite email sent: ${r.data.email_sent}`);
      setShowModal(false);
      setForm({ title: 'Interview', candidate_id: '', candidate_email: '', candidate_name: '', scheduled_at: '', duration_minutes: 30, notes: '' });
      setTab('by-me');
    } catch (e) {
      alert('Failed: ' + (e.response?.data?.detail || e.message));
    } finally {
      setCreating(false);
    }
  };

  const joinCall = (roomId) => {
    navigate(`/video-call/${roomId}`);
  };

  return (
    <div className="min-h-screen bg-slate-50 p-6">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold text-slate-900 flex items-center gap-2">
              <Video className="w-8 h-8 text-purple-600" />
              Video Interviews
            </h1>
            <p className="text-slate-500 mt-1">
              Invite-only secure video interviews
            </p>
          </div>
          {canSchedule && (
            <button
              onClick={() => setShowModal(true)}
              className="px-5 py-2.5 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700 transition flex items-center gap-2"
            >
              <Plus className="w-4 h-4" />
              Schedule New
            </button>
          )}
        </div>

        {/* Tabs */}
        <div className="flex gap-1 border-b border-slate-200 mb-6">
          <button
            onClick={() => setTab('with-me')}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition ${
              tab === 'with-me'
                ? 'border-purple-600 text-purple-600'
                : 'border-transparent text-slate-500 hover:text-slate-700'
            }`}
          >
            📥 Scheduled With Me
          </button>
          <button
            onClick={() => setTab('by-me')}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition ${
              tab === 'by-me'
                ? 'border-purple-600 text-purple-600'
                : 'border-transparent text-slate-500 hover:text-slate-700'
            }`}
          >
            📤 Scheduled By Me
          </button>
        </div>

        {/* List */}
        {loading ? (
          <div className="text-center py-12 text-slate-400">Loading...</div>
        ) : interviews.length === 0 ? (
          <div className="bg-white rounded-xl border border-slate-200 p-12 text-center">
            <Video className="w-16 h-16 text-slate-300 mx-auto mb-4" />
            <div className="text-lg font-semibold mb-2">No interviews yet</div>
            <div className="text-sm text-slate-500">
              {tab === 'with-me'
                ? 'Interviews scheduled with you will appear here'
                : canSchedule
                ? 'Click "Schedule New" to create your first interview'
                : 'You don\'t have permission to schedule interviews'}
            </div>
          </div>
        ) : (
          <div className="space-y-3">
            {interviews.map((iv) => (
              <div
                key={iv.id}
                className="bg-white rounded-xl border border-slate-200 p-5 hover:border-purple-300 hover:shadow-md transition"
              >
                <div className="flex items-start gap-4">
                  <div className="w-14 h-14 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-xl flex items-center justify-center text-white flex-shrink-0">
                    <Video className="w-7 h-7" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <h3 className="font-bold text-slate-900">{iv.title}</h3>
                        <div className="text-sm text-slate-500 mt-0.5 flex items-center gap-2">
                          <User className="w-3 h-3" />
                          {tab === 'with-me'
                            ? `with ${iv.interviewer_name || 'Interviewer'}`
                            : `with ${iv.candidate_name || 'Candidate'}`}
                        </div>
                      </div>
                      <span
                        className={`text-xs px-2 py-1 rounded-full font-semibold ${
                          iv.status === 'SCHEDULED'
                            ? 'bg-green-100 text-green-700'
                            : iv.status === 'COMPLETED'
                            ? 'bg-blue-100 text-blue-700'
                            : iv.status === 'CANCELLED'
                            ? 'bg-red-100 text-red-700'
                            : 'bg-slate-100 text-slate-700'
                        }`}
                      >
                        {iv.status || 'SCHEDULED'}
                      </span>
                    </div>

                    <div className="flex items-center gap-4 text-xs text-slate-500 mb-3">
                      {iv.scheduled_at && (
                        <span className="flex items-center gap-1">
                          <Calendar className="w-3 h-3" />
                          {iv.scheduled_at}
                        </span>
                      )}
                      <span className="flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {iv.duration_minutes || 30} min
                      </span>
                    </div>

                    <div className="flex gap-2">
                      {iv.status === 'SCHEDULED' && (
                        <button
                          onClick={() => joinCall(iv.room_id)}
                          className="px-4 py-2 bg-purple-600 text-white rounded-lg text-sm font-medium hover:bg-purple-700 flex items-center gap-2"
                        >
                          <Video className="w-4 h-4" />
                          Join Interview
                        </button>
                      )}
                      <button
                        onClick={() => {
                          navigator.clipboard.writeText(`${window.location.origin}/video-call/${iv.room_id}`);
                          alert('Invite link copied!');
                        }}
                        className="px-4 py-2 bg-slate-100 text-slate-700 rounded-lg text-sm hover:bg-slate-200"
                      >
                        📋 Copy Link
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Schedule Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b border-slate-200 p-5 flex items-center justify-between">
              <h2 className="text-lg font-bold">Schedule New Interview</h2>
              <button onClick={() => setShowModal(false)}>
                <X className="w-5 h-5 text-slate-400" />
              </button>
            </div>
            <div className="p-5 space-y-4">
              <div>
                <label className="text-xs text-slate-500 font-medium">Title</label>
                <input
                  type="text"
                  value={form.title}
                  onChange={(e) => setForm({ ...form, title: e.target.value })}
                  placeholder="Frontend Developer Interview"
                  className="w-full mt-1 px-3 py-2 border border-slate-300 rounded-lg text-sm"
                />
              </div>
              <div>
                <label className="text-xs text-slate-500 font-medium">Candidate User ID *</label>
                <input
                  type="text"
                  value={form.candidate_id}
                  onChange={(e) => setForm({ ...form, candidate_id: e.target.value })}
                  placeholder="test_student_001"
                  className="w-full mt-1 px-3 py-2 border border-slate-300 rounded-lg text-sm"
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs text-slate-500 font-medium">Candidate Name</label>
                  <input
                    type="text"
                    value={form.candidate_name}
                    onChange={(e) => setForm({ ...form, candidate_name: e.target.value })}
                    placeholder="Promod Kumar"
                    className="w-full mt-1 px-3 py-2 border border-slate-300 rounded-lg text-sm"
                  />
                </div>
                <div>
                  <label className="text-xs text-slate-500 font-medium">Candidate Email</label>
                  <input
                    type="email"
                    value={form.candidate_email}
                    onChange={(e) => setForm({ ...form, candidate_email: e.target.value })}
                    placeholder="candidate@example.com"
                    className="w-full mt-1 px-3 py-2 border border-slate-300 rounded-lg text-sm"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs text-slate-500 font-medium">Scheduled At</label>
                  <input
                    type="datetime-local"
                    value={form.scheduled_at}
                    onChange={(e) => setForm({ ...form, scheduled_at: e.target.value })}
                    className="w-full mt-1 px-3 py-2 border border-slate-300 rounded-lg text-sm"
                  />
                </div>
                <div>
                  <label className="text-xs text-slate-500 font-medium">Duration (min)</label>
                  <input
                    type="number"
                    value={form.duration_minutes}
                    onChange={(e) => setForm({ ...form, duration_minutes: parseInt(e.target.value) || 30 })}
                    className="w-full mt-1 px-3 py-2 border border-slate-300 rounded-lg text-sm"
                  />
                </div>
              </div>
              <div>
                <label className="text-xs text-slate-500 font-medium">Notes</label>
                <textarea
                  rows="3"
                  value={form.notes}
                  onChange={(e) => setForm({ ...form, notes: e.target.value })}
                  placeholder="Technical round, discuss React experience..."
                  className="w-full mt-1 px-3 py-2 border border-slate-300 rounded-lg text-sm"
                />
              </div>
              <button
                onClick={handleCreate}
                disabled={creating}
                className="w-full py-3 bg-purple-600 text-white rounded-lg font-semibold hover:bg-purple-700 disabled:opacity-50"
              >
                {creating ? 'Creating...' : '🎥 Create Interview & Send Invite'}
              </button>
              <div className="text-xs text-slate-500 text-center">
                🔒 Candidate will receive email + notification with private join link
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}