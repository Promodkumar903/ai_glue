import React, { useState } from 'react';
import { ChevronDown, HelpCircle } from 'lucide-react';

const FAQS = [
  {
    q: 'Is AI Glue OIE free to use?',
    a: 'Yes! Creating an account and browsing opportunities is 100% free for students and job seekers. Premium features like unlimited copilot queries and salary intelligence are available on paid plans.',
  },
  {
    q: 'How is the data verified?',
    a: 'Every opportunity is backed by source evidence. We pull data from government portals (Make it in Germany, NCS India), official university sites, and Hipolabs. Each claim has a trust score.',
  },
  {
    q: 'Can I find free education programs?',
    a: 'Absolutely. We track 392 universities with zero or near-zero tuition fees, especially in Germany, Norway, and Finland. Filter by "Free Education" in your dashboard.',
  },
  {
    q: 'Do you help with visa sponsorship?',
    a: 'Yes. We specifically highlight jobs with visa sponsorship, accommodation, and relocation support. Our AI Copilot tells you exactly which opportunities include these benefits.',
  },
  {
    q: 'What countries do you cover?',
    a: 'Currently 25+ countries including Germany, USA, UK, Canada, Australia, Japan, Netherlands, Singapore, and more. We add new countries every month.',
  },
  {
    q: 'How does the AI Copilot work?',
    a: 'Ask anything in natural language — "Germany nursing jobs with visa" or "Free CS masters in Canada". Our AI understands context and gives you real, verified answers from our database.',
  },
  {
    q: 'Is my data safe?',
    a: 'Yes. We use end-to-end encryption, RBAC access control, and never share your data without consent. Your profile is yours alone.',
  },
  {
    q: 'Can agents and consultants use this platform?',
    a: 'Yes! Agents, brokers, and consultants get dedicated dashboards to manage candidates, track leads, and find verified opportunities for their clients.',
  },
];

export default function FAQ() {
  const [open, setOpen] = useState(0);

  return (
    <section className="py-12 px-6 bg-white/[0.02]">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-10">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 mb-4 rounded-full bg-purple-500/10 border border-purple-500/30 text-sm text-purple-300">
            <HelpCircle className="w-3 h-3" />
            FAQ
          </div>
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Questions? <span className="bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">Answered.</span>
          </h2>
          <p className="text-base text-gray-400">Everything you need to know about AI Glue OIE</p>
        </div>

        <div className="space-y-3">
          {FAQS.map((faq, i) => (
            <div
              key={i}
              className={`rounded-2xl border transition-all ${
                open === i
                  ? 'bg-white/10 border-purple-500/40'
                  : 'bg-white/5 border-white/10 hover:border-purple-500/20'
              }`}
            >
              <button
                onClick={() => setOpen(open === i ? -1 : i)}
                className="w-full p-4 flex items-center justify-between text-left"
              >
                <span className="font-semibold text-base pr-4">{faq.q}</span>
                <ChevronDown
                  className={`w-5 h-5 text-purple-400 flex-shrink-0 transition-transform ${
                    open === i ? 'rotate-180' : ''
                  }`}
                />
              </button>
              {open === i && (
                <div className="px-6 pb-6 text-gray-400 leading-relaxed animate-fadeIn">
                  {faq.a}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(-8px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fadeIn { animation: fadeIn 0.3s ease-out; }
      `}</style>
    </section>
  );
}