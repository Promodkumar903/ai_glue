import { useState } from 'react';

export default function ComingSoon() {
  const [email, setEmail] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!email) return;
    // Save to localStorage for now (backend endpoint later)
    const subs = JSON.parse(localStorage.getItem('waitlist') || '[]');
    if (!subs.includes(email)) subs.push(email);
    localStorage.setItem('waitlist', JSON.stringify(subs));
    setSubmitted(true);
    setTimeout(() => setSubmitted(false), 5000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-600 via-indigo-600 to-purple-700 flex items-center justify-center p-6">
      <div className="max-w-2xl w-full text-center text-white">
        
        {/* Logo */}
        <div className="mb-8 flex justify-center">
          <img src="/logo-dark.png" alt="AI Glue" className="h-16 w-auto" />
        </div>

        {/* Badge */}
        <div className="inline-block px-4 py-1.5 bg-white/10 backdrop-blur rounded-full text-sm font-medium mb-6 border border-white/20">
          🚀 Launching Soon
        </div>

        {/* Title */}
        <h1 className="text-4xl md:text-6xl font-bold mb-4 leading-tight">
          AI Glue is Almost Ready
        </h1>
        <p className="text-lg md:text-xl text-purple-100 mb-8 max-w-xl mx-auto">
          We're putting the final touches on our verified jobs platform —
          connecting you with 3000+ verified opportunities worldwide.
        </p>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-4 mb-10 max-w-md mx-auto">
          <div className="bg-white/10 backdrop-blur rounded-xl p-4 border border-white/20">
            <div className="text-2xl font-bold">3,225+</div>
            <div className="text-xs text-purple-200 mt-1">Verified Jobs</div>
          </div>
          <div className="bg-white/10 backdrop-blur rounded-xl p-4 border border-white/20">
            <div className="text-2xl font-bold">4,957+</div>
            <div className="text-xs text-purple-200 mt-1">Study Programs</div>
          </div>
          <div className="bg-white/10 backdrop-blur rounded-xl p-4 border border-white/20">
            <div className="text-2xl font-bold">15+</div>
            <div className="text-xs text-purple-200 mt-1">Countries</div>
          </div>
        </div>

        {/* Waitlist Form */}
        {!submitted ? (
          <form onSubmit={handleSubmit} className="max-w-md mx-auto mb-8">
            <div className="flex gap-2">
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="your@email.com"
                required
                className="flex-1 px-4 py-3 rounded-lg bg-white/10 backdrop-blur border border-white/20 text-white placeholder-purple-200 focus:outline-none focus:ring-2 focus:ring-white/40"
              />
              <button
                type="submit"
                className="px-6 py-3 bg-white text-purple-700 font-bold rounded-lg hover:bg-purple-50 transition whitespace-nowrap"
              >
                Notify Me
              </button>
            </div>
            <p className="text-xs text-purple-200 mt-3">
              Be first to know when we launch. No spam, promise.
            </p>
          </form>
        ) : (
          <div className="max-w-md mx-auto mb-8 bg-white/10 backdrop-blur rounded-xl p-6 border border-white/20">
            <div className="text-4xl mb-2">✅</div>
            <div className="font-semibold">You're on the list!</div>
            <div className="text-sm text-purple-200 mt-1">
              We'll email you when we launch.
            </div>
          </div>
        )}

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-4 max-w-2xl mx-auto text-left mt-12">
          <div className="bg-white/5 backdrop-blur rounded-xl p-4 border border-white/10">
            <div className="text-2xl mb-2">🎯</div>
            <div className="font-semibold text-sm mb-1">AI-Matched Jobs</div>
            <div className="text-xs text-purple-200">
              Personalized job matches based on your profile
            </div>
          </div>
          <div className="bg-white/5 backdrop-blur rounded-xl p-4 border border-white/10">
            <div className="text-2xl mb-2">✅</div>
            <div className="font-semibold text-sm mb-1">100% Verified</div>
            <div className="text-xs text-purple-200">
              Only jobs from official company sources
            </div>
          </div>
          <div className="bg-white/5 backdrop-blur rounded-xl p-4 border border-white/10">
            <div className="text-2xl mb-2">📹</div>
            <div className="font-semibold text-sm mb-1">Video Interviews</div>
            <div className="text-xs text-purple-200">
              Connect directly with employers
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-16 pt-8 border-t border-white/10 text-xs text-purple-200 space-y-2">
          <div>
            AI Glue is a product of <span className="text-white font-medium">KOWA Construction and Traders Pvt Ltd</span>
          </div>
          <div>© 2026 KOWA Construction and Traders Pvt Ltd</div>
        </div>
      </div>
    </div>
  );
}