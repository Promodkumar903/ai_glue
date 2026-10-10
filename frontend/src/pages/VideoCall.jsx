import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from '../utils/axios';

const JITSI_SERVER = 'https://meet.ffmuc.net';

export default function VideoCall() {
  const { roomId } = useParams();
  const navigate = useNavigate();
  const [interview, setInterview] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [displayName, setDisplayName] = useState('');
  const [opened, setOpened] = useState(false);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    axios.get(`/interview/interview/room/${roomId}`)
      .then(res => {
        setInterview(res.data);
        setDisplayName(res.data.candidate_name || 'Guest');
      })
      .catch(err => setError(err.response?.data?.detail || 'Invalid or expired link'))
      .finally(() => setLoading(false));
  }, [roomId]);

  const videoUrl = `${JITSI_SERVER}/${roomId}#userInfo.displayName="${encodeURIComponent(displayName || 'Guest')}"&config.prejoinPageEnabled=false`;

  const handleJoin = () => {
    if (!displayName.trim()) {
      alert('Please enter your name');
      return;
    }
    // Open video call in new tab (frame-ancestors policy blocks iframe)
    window.open(videoUrl, '_blank', 'noopener,noreferrer');
    setOpened(true);
  };

  const copyLink = () => {
    navigator.clipboard.writeText(videoUrl);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="text-center">
          <div className="animate-spin w-10 h-10 border-4 border-purple-500 border-t-transparent rounded-full mx-auto mb-3"></div>
          <div className="text-slate-500">Loading interview...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50 p-4">
        <div className="bg-white rounded-2xl p-8 max-w-md text-center shadow-lg border border-slate-200">
          <div className="text-5xl mb-3">🔒</div>
          <h2 className="text-xl font-bold mb-2">Link Not Valid</h2>
          <p className="text-slate-500 text-sm mb-6">{error}</p>
          <button
            onClick={() => navigate('/')}
            className="px-6 py-2 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700"
          >
            Go Home
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 p-4">
      <div className="bg-white rounded-2xl max-w-lg w-full shadow-lg border border-slate-200 overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600 to-indigo-600 p-6 text-white">
          <div className="text-3xl mb-2">📹</div>
          <h1 className="text-2xl font-bold">{interview.title || 'Interview'}</h1>
          <p className="text-purple-100 text-sm mt-1">
            with {interview.interviewer_name || 'Interviewer'}
          </p>
        </div>

        <div className="p-6 space-y-4">
          {interview.scheduled_at && (
            <div className="bg-slate-50 p-3 rounded-lg text-sm">
              <div className="text-slate-500 text-xs">Scheduled for</div>
              <div className="font-semibold">{interview.scheduled_at}</div>
            </div>
          )}

          {!opened ? (
            <>
              <div>
                <label className="text-sm font-medium text-slate-700">Your name</label>
                <input
                  type="text"
                  value={displayName}
                  onChange={(e) => setDisplayName(e.target.value)}
                  placeholder="Enter your name"
                  className="w-full mt-1 px-4 py-3 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500 outline-none"
                />
              </div>

              <button
                onClick={handleJoin}
                className="w-full py-3 bg-purple-600 text-white rounded-lg font-semibold hover:bg-purple-700 transition shadow-md"
              >
                🎥 Join Video Call
              </button>

              <div className="flex items-center gap-2 text-xs text-slate-500 justify-center">
                🔒 Private room · Only people with the link can join
              </div>
            </>
          ) : (
            <>
              <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-center">
                <div className="text-3xl mb-2">✅</div>
                <div className="font-semibold text-green-800">
                  Video call opened in a new tab
                </div>
                <div className="text-xs text-green-700 mt-1">
                  If the tab didn't open, click the button below.
                </div>
              </div>

              <a
                href={videoUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="block w-full py-3 bg-purple-600 text-white rounded-lg font-semibold hover:bg-purple-700 transition text-center"
              >
                🎥 Open Video Call
              </a>

              <button
                onClick={copyLink}
                className="w-full py-2 bg-slate-100 text-slate-700 rounded-lg text-sm hover:bg-slate-200 transition"
              >
                {copied ? '✅ Link Copied' : '📋 Copy Invite Link'}
              </button>

              <div className="text-xs text-slate-500 text-center mt-2">
                Share this link with the other participant so they can join
              </div>
            </>
          )}
        </div>

        {/* Footer info */}
        <div className="bg-slate-50 px-6 py-3 border-t border-slate-200 text-xs text-slate-500">
          Room ID: <code className="font-mono">{roomId}</code>
        </div>
      </div>
    </div>
  );
}