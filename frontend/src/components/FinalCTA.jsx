import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, ArrowRight, Zap } from 'lucide-react';

export default function FinalCTA() {
  const navigate = useNavigate();

  return (
    <section className="py-12 px-6 relative overflow-hidden">
      {/* Glow background */}
      <div className="absolute inset-0 opacity-40">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] rounded-full bg-purple-500/30 blur-[120px]" />
        <div className="absolute top-1/2 left-1/4 -translate-y-1/2 w-[400px] h-[400px] rounded-full bg-pink-500/30 blur-[120px]" />
      </div>

      <div className="relative max-w-4xl mx-auto text-center">
        <div className="inline-flex items-center gap-2 px-4 py-1.5 mb-6 rounded-full bg-purple-500/20 border border-purple-500/40 backdrop-blur text-sm text-purple-200">
          <Zap className="w-4 h-4" />
          Start Your Journey Today
        </div>

        <h2 className="text-4xl md:text-5xl font-bold mb-6 leading-tight">
          Your Global Career
          <br />
          <span className="bg-gradient-to-r from-purple-400 via-pink-400 to-purple-400 bg-clip-text text-transparent">
            Starts Here.
          </span>
        </h2>

        <p className="text-lg text-gray-300 mb-10 max-w-2xl mx-auto">
          Join 5,000+ opportunities, 4,957 universities, and 24 top companies — all in one AI-powered platform.
        </p>

        <div className="flex flex-wrap gap-4 justify-center mb-8">
          <button
            onClick={() => navigate('/login?role=Student')}
            className="px-8 py-4 rounded-2xl bg-gradient-to-r from-purple-500 to-pink-500 text-lg font-bold hover:opacity-90 inline-flex items-center gap-3 shadow-2xl shadow-purple-500/50 hover:scale-105 transition"
          >
            <Sparkles className="w-5 h-5" />
            Get Started Free
            <ArrowRight className="w-5 h-5" />
          </button>
          <button
            onClick={() => navigate('/login?role=JOBSEEKER')}
            className="px-8 py-4 rounded-2xl bg-white/10 backdrop-blur border border-white/20 text-lg font-semibold hover:bg-white/20 inline-flex items-center gap-2 transition"
          >
            Explore Jobs
          </button>
        </div>

        <div className="flex flex-wrap justify-center gap-6 text-sm text-gray-400">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-green-400" />
            No credit card required
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-green-400" />
            100% free for students
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-green-400" />
            Setup in 30 seconds
          </div>
        </div>
      </div>
    </section>
  );
}