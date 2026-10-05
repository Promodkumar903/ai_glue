import React from 'react';
import { Link } from 'react-router-dom';
import { Sparkles } from 'lucide-react';

export default function AboutUs() {
  return (
    <div className="min-h-screen bg-slate-50">
      <div className="relative h-[400px] overflow-hidden">
        <div className="absolute inset-0 bg-cover bg-center" style={{ backgroundImage: `url('https://images.unsplash.com/photo-1521737604893-d14cc237f11d?w=1920&q=80')` }} />
        <div className="absolute inset-0 bg-gradient-to-r from-purple-900/90 via-purple-800/80 to-pink-900/90" />
        <div className="relative h-full flex flex-col items-center justify-center px-6 text-center text-white">
          <div className="w-16 h-16 bg-white/20 backdrop-blur-md rounded-2xl flex items-center justify-center border border-white/30 mb-4">
            <Sparkles className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-5xl md:text-6xl font-extrabold mb-4 tracking-tight">About AI Glue</h1>
          <p className="text-xl md:text-2xl opacity-90 max-w-3xl">Connecting talent with global opportunities</p>
        </div>
      </div>

      <div className="max-w-5xl mx-auto py-16 px-6 -mt-12 relative z-10">
        <div className="bg-white rounded-3xl shadow-2xl p-10 mb-12 border border-slate-100">
          <div className="flex items-center gap-4 mb-6">
            <div className="w-14 h-14 bg-gradient-to-br from-purple-500 to-pink-500 rounded-2xl flex items-center justify-center text-3xl">🎯</div>
            <h2 className="text-3xl font-bold text-slate-800">Our Mission</h2>
          </div>
          <p className="text-slate-600 leading-relaxed text-lg">
            AI Glue is a <strong>unified platform</strong> that connects students, job seekers, agents, brokers, and employers across the globe. We leverage artificial intelligence to make international education and career opportunities accessible to everyone.
          </p>
        </div>

        <h2 className="text-3xl font-bold text-slate-800 mb-6 text-center">Who We Serve</h2>
        <div className="grid md:grid-cols-2 gap-6 mb-12">
          <div className="bg-white rounded-2xl shadow-lg p-6 border-l-4 border-blue-500 hover:shadow-xl transition">
            <div className="text-4xl mb-3">🎓</div>
            <h3 className="text-xl font-bold text-slate-800 mb-2">For Students</h3>
            <p className="text-slate-600 text-sm leading-relaxed">AI-powered university matching, visa assistance, document verification, and end-to-end application support.</p>
          </div>
          <div className="bg-white rounded-2xl shadow-lg p-6 border-l-4 border-green-500 hover:shadow-xl transition">
            <div className="text-4xl mb-3">💼</div>
            <h3 className="text-xl font-bold text-slate-800 mb-2">For Job Seekers</h3>
            <p className="text-slate-600 text-sm leading-relaxed">Real-time job matching, AI resume builder, interview prep, and global placement opportunities.</p>
          </div>
          <div className="bg-white rounded-2xl shadow-lg p-6 border-l-4 border-purple-500 hover:shadow-xl transition">
            <div className="text-4xl mb-3">🤝</div>
            <h3 className="text-xl font-bold text-slate-800 mb-2">For Agents & Brokers</h3>
            <p className="text-slate-600 text-sm leading-relaxed">Manage candidates, track commissions, grow your network, and access a global marketplace.</p>
          </div>
          <div className="bg-white rounded-2xl shadow-lg p-6 border-l-4 border-orange-500 hover:shadow-xl transition">
            <div className="text-4xl mb-3">🏢</div>
            <h3 className="text-xl font-bold text-slate-800 mb-2">For Employers</h3>
            <p className="text-slate-600 text-sm leading-relaxed">AI-matched candidates, streamlined hiring, bulk hiring support, and pre-verified global talent.</p>
          </div>
        </div>

        <div className="bg-gradient-to-br from-purple-600 via-pink-500 to-red-500 rounded-3xl shadow-2xl p-10 mb-12 text-white">
          <h2 className="text-3xl font-bold mb-6">🚀 What Makes Us Different</h2>
          <ul className="space-y-4">
            <li className="flex items-start gap-3"><span className="text-yellow-300 font-bold text-xl flex-shrink-0">✓</span><span><strong>All-in-one platform</strong> — Admission, visa, job, accommodation — sab ek jagah</span></li>
            <li className="flex items-start gap-3"><span className="text-yellow-300 font-bold text-xl flex-shrink-0">✓</span><span><strong>AI-powered matching</strong> — Right university, right job</span></li>
            <li className="flex items-start gap-3"><span className="text-yellow-300 font-bold text-xl flex-shrink-0">✓</span><span><strong>Transparent pricing</strong> — No hidden charges</span></li>
            <li className="flex items-start gap-3"><span className="text-yellow-300 font-bold text-xl flex-shrink-0">✓</span><span><strong>Global reach</strong> — India, Nepal, worldwide</span></li>
          </ul>
        </div>

        <div className="bg-white rounded-3xl shadow-xl p-10 text-center border border-slate-100">
          <h2 className="text-3xl font-bold text-slate-800 mb-3">Ready to Get Started?</h2>
          <p className="text-slate-600 mb-6 text-lg">Join thousands of students, professionals, and employers.</p>
          <div className="flex gap-3 justify-center flex-wrap">
            <Link to="/register" className="bg-gradient-to-r from-purple-600 to-pink-600 hover:opacity-90 text-white px-8 py-3 rounded-xl font-semibold transition shadow-lg shadow-purple-500/30">Create Account</Link>
            <Link to="/pricing" className="bg-white hover:bg-slate-50 text-purple-600 px-8 py-3 rounded-xl font-semibold border-2 border-purple-200 transition">View Plans</Link>
          </div>
        </div>
      </div>
    </div>
  );
}