import React, { useState } from 'react';
import { Mail, Send } from 'lucide-react';

export default function ContactUs() {
  const [form, setForm] = useState({ name: '', email: '', subject: '', message: '' });
  const [sent, setSent] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    setSent(true);
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="relative h-[400px] overflow-hidden">
        <div className="absolute inset-0 bg-cover bg-center" style={{ backgroundImage: `url('https://images.unsplash.com/photo-1423666639041-f56000c27a9a?w=1920&q=80')` }} />
        <div className="absolute inset-0 bg-gradient-to-r from-purple-900/90 via-purple-800/80 to-pink-900/90" />
        <div className="relative h-full flex flex-col items-center justify-center px-6 text-center text-white">
          <div className="w-16 h-16 bg-white/20 backdrop-blur-md rounded-2xl flex items-center justify-center border border-white/30 mb-4">
            <Mail className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-5xl md:text-6xl font-extrabold mb-4 tracking-tight">Contact Us</h1>
          <p className="text-xl md:text-2xl opacity-90 max-w-3xl">We would love to hear from you</p>
        </div>
      </div>

      <div className="max-w-5xl mx-auto py-16 px-6 -mt-12 relative z-10">
        <div className="grid md:grid-cols-2 gap-6 mb-10">
          <div className="bg-white rounded-2xl shadow-lg p-6 border-l-4 border-purple-500">
            <div className="text-4xl mb-3">📧</div>
            <h3 className="text-lg font-bold text-slate-800 mb-3">Email Support</h3>
            <p className="text-slate-500 text-xs mb-1">Support & Queries:</p>
            <a href="mailto:support@aiglueagent.com" className="text-purple-600 hover:underline font-medium">support@aiglueagent.com</a>
            <p className="text-slate-500 text-xs mt-3 mb-1">Business Partnerships:</p>
            <a href="mailto:business@aiglueagent.com" className="text-purple-600 hover:underline font-medium">business@aiglueagent.com</a>
          </div>

          <div className="bg-white rounded-2xl shadow-lg p-6 border-l-4 border-green-500">
            <div className="text-4xl mb-3">⏱️</div>
            <h3 className="text-lg font-bold text-slate-800 mb-3">Response Time</h3>
            <ul className="text-slate-600 text-sm space-y-2">
              <li><strong>Email support:</strong> 24-48 hours</li>
              <li><strong>Payment issues:</strong> Priority — 12 hours</li>
              <li><strong>Business queries:</strong> 2-3 working days</li>
            </ul>
          </div>
        </div>

        <div className="bg-white rounded-3xl shadow-2xl p-10 border border-slate-100">
          <div className="flex items-center gap-4 mb-6">
            <div className="w-14 h-14 bg-gradient-to-br from-purple-500 to-pink-500 rounded-2xl flex items-center justify-center">
              <Send className="w-7 h-7 text-white" />
            </div>
            <h2 className="text-3xl font-bold text-slate-800">Send us a message</h2>
          </div>

          {sent ? (
            <div className="p-8 bg-green-50 border-2 border-green-200 rounded-2xl text-center">
              <div className="text-5xl mb-3">✅</div>
              <h3 className="font-bold text-green-700 mb-2 text-xl">Message bhej diya!</h3>
              <p className="text-green-600">Hum 24-48 ghante mein reply karenge.</p>
              <button onClick={() => { setSent(false); setForm({ name: '', email: '', subject: '', message: '' }); }} className="mt-4 text-sm text-purple-600 underline font-medium">Naya message bhejo</button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Name *</label>
                  <input type="text" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} className="w-full p-3 border-2 border-slate-200 rounded-xl focus:outline-none focus:border-purple-500" required />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Email *</label>
                  <input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} className="w-full p-3 border-2 border-slate-200 rounded-xl focus:outline-none focus:border-purple-500" required />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Subject *</label>
                <input type="text" value={form.subject} onChange={(e) => setForm({ ...form, subject: e.target.value })} className="w-full p-3 border-2 border-slate-200 rounded-xl focus:outline-none focus:border-purple-500" required />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Message *</label>
                <textarea value={form.message} onChange={(e) => setForm({ ...form, message: e.target.value })} rows={6} className="w-full p-3 border-2 border-slate-200 rounded-xl focus:outline-none focus:border-purple-500" required />
              </div>
              <button type="submit" className="bg-gradient-to-r from-purple-600 to-pink-600 hover:opacity-90 text-white px-8 py-3 rounded-xl font-semibold transition shadow-lg shadow-purple-500/30">
                Send Message
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}