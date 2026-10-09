import React from 'react';
import { UserPlus, Search, Send, ArrowRight } from 'lucide-react';

export default function HowItWorks() {
  const steps = [
    {
      num: '01',
      icon: UserPlus,
      title: 'Create Your Profile',
      desc: 'Sign up free in 30 seconds. Add your marks, budget, skills, and dream destination.',
      color: 'from-blue-500 to-cyan-500',
    },
    {
      num: '02',
      icon: Search,
      title: 'AI Finds Your Match',
      desc: 'Our OIE engine scans 5,000+ opportunities and matches you with the best fit — verified.',
      color: 'from-purple-500 to-pink-500',
    },
    {
      num: '03',
      icon: Send,
      title: 'Apply & Get Hired',
      desc: 'Direct applications, visa support, and accommodation — all in one pathway.',
      color: 'from-green-500 to-emerald-500',
    },
  ];

  return (
    <section className="py-12 px-6">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-10">
          <div className="inline-block px-4 py-1.5 mb-4 rounded-full bg-purple-500/10 border border-purple-500/30 text-sm text-purple-300">
            Simple Process
          </div>
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            How It <span className="bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">Works</span>
          </h2>
          <p className="text-lg text-gray-400">From signup to global career in 3 steps</p>
        </div>

        <div className="grid md:grid-cols-3 gap-6 relative">
          {/* Connecting line */}
          <div className="hidden md:block absolute top-24 left-1/4 right-1/4 h-0.5 bg-gradient-to-r from-purple-500/30 via-purple-500/60 to-purple-500/30" />

          {steps.map((s, i) => (
            <div key={i} className="relative">
              <div className="p-6 rounded-3xl bg-white/5 border border-white/10 hover:border-purple-500/40 transition group">
                {/* Step number */}
                <div className="text-4xl font-bold text-white/5 mb-2">{s.num}</div>

                {/* Icon */}
                <div className={`w-12 h-12 rounded-2xl bg-gradient-to-br ${s.color} flex items-center justify-center mb-6 group-hover:scale-110 transition`}>
                  <s.icon className="w-8 h-8 text-white" />
                </div>

                <h3 className="text-2xl font-bold mb-3">{s.title}</h3>
                <p className="text-gray-400">{s.desc}</p>

                {i < steps.length - 1 && (
                  <ArrowRight className="hidden md:block absolute -right-6 top-1/2 -translate-y-1/2 w-8 h-8 text-purple-400/50" />
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}