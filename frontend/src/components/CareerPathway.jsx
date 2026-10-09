import React, { useState, useEffect } from 'react';
import { GraduationCap, Briefcase, Building2, ArrowRight, CheckCircle, TrendingUp, DollarSign, Award, MapPin } from 'lucide-react';

const PATHWAYS = [
  {
    student: { name: 'Rajesh K.', marks: '99.5%', cgpa: 8.2, budget: '₹2.5L/yr', country: '🇮🇳 India' },
    university: { name: 'TU Munich', country: '🇩🇪 Germany', course: 'MS in CS', fee: 'Free', duration: '2 years' },
    company: { name: 'Siemens', role: 'Software Engineer', package: '€65K/yr', location: 'Munich' },
    score: 94,
    benefits: ['Free tuition', '18-mo post-study work', 'PR pathway'],
  },
  {
    student: { name: 'Priya S.', marks: '98.2%', cgpa: 8.5, budget: '₹5L/yr', country: '🇮🇳 India' },
    university: { name: 'University of Toronto', country: '🇨🇦 Canada', course: 'MS in Data Science', fee: 'CAD 45K', duration: '16 months' },
    company: { name: 'Shopify', role: 'Senior SDE', package: '₹85L/yr', location: 'Toronto' },
    score: 97,
    benefits: ['3-year PR pathway', 'Top-50 QS', 'Strong alumni network'],
  },
  {
    student: { name: 'Amit V.', marks: '96.8%', cgpa: 8.0, budget: '₹3L/yr', country: '🇳🇵 Nepal' },
    university: { name: 'University of Tokyo', country: '🇯🇵 Japan', course: 'MS in Robotics', fee: '$5K', duration: '2 years' },
    company: { name: 'Toyota', role: 'Research Engineer', package: '¥7M/yr', location: 'Tokyo' },
    score: 91,
    benefits: ['MEXT scholarship', 'PR after 10 years', 'Tech hub'],
  },
];

export default function CareerPathway() {
  const [active, setActive] = useState(0);
  const [step, setStep] = useState(0);

  // Auto-advance pathway
  useEffect(() => {
    const t = setInterval(() => {
      setStep(s => {
        if (s >= 2) {
          setActive(a => (a + 1) % PATHWAYS.length);
          return 0;
        }
        return s + 1;
      });
    }, 2500);
    return () => clearInterval(t);
  }, []);

  const p = PATHWAYS[active];

  return (
    <section className="py-12 px-6 relative overflow-hidden">
      {/* Background grid */}
      <div className="absolute inset-0 opacity-20" style={{
        backgroundImage: 'radial-gradient(circle at 20% 50%, rgba(139,92,246,0.3) 0%, transparent 50%), radial-gradient(circle at 80% 80%, rgba(236,72,153,0.3) 0%, transparent 50%)'
      }} />

      <div className="relative max-w-7xl mx-auto">
        {/* Heading */}
        <div className="text-center mb-10">
          <div className="inline-block px-4 py-1.5 mb-4 rounded-full bg-purple-500/10 border border-purple-500/30 text-sm text-purple-300">
            ⚡ Signature Feature
          </div>
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Your{' '}
            <span className="bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
              Career Pathway
            </span>
            , Visualized
          </h2>
          <p className="text-lg text-gray-400 max-w-2xl mx-auto">
            We match you from student → university → dream company. In real-time.
          </p>
        </div>

        {/* Main pathway container */}
        <div className="grid lg:grid-cols-3 gap-4 items-stretch">

          {/* STEP 1: STUDENT */}
          <div className={`relative p-5 rounded-3xl border-2 transition-all duration-500 ${
            step >= 0 ? 'border-purple-500/60 bg-gradient-to-br from-purple-500/10 to-transparent shadow-2xl shadow-purple-500/20' : 'border-white/10 bg-white/5'
          }`}>
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center">
                <GraduationCap className="w-6 h-6 text-white" />
              </div>
              <div>
                <div className="text-xs text-gray-400 tracking-wider">STEP 1</div>
                <div className="font-bold">Student</div>
              </div>
            </div>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-sm text-gray-400">Name</span>
                <span className="text-sm font-semibold">{p.student.name}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-400">Marks</span>
                <span className="text-sm font-semibold">{p.student.marks}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-400">CGPA</span>
                <span className="text-sm font-semibold">{p.student.cgpa}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-400">Budget</span>
                <span className="text-sm font-semibold">{p.student.budget}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-400">Origin</span>
                <span className="text-sm font-semibold">{p.student.country}</span>
              </div>
            </div>
          </div>

          {/* STEP 2: UNIVERSITY */}
          <div className={`relative p-5 rounded-3xl border-2 transition-all duration-500 ${
            step >= 1 ? 'border-purple-500/60 bg-gradient-to-br from-purple-500/10 to-transparent shadow-2xl shadow-purple-500/20' : 'border-white/10 bg-white/5'
          }`}>
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                <Building2 className="w-6 h-6 text-white" />
              </div>
              <div>
                <div className="text-xs text-gray-400 tracking-wider">STEP 2</div>
                <div className="font-bold">University</div>
              </div>
            </div>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-sm text-gray-400">Name</span>
                <span className="text-sm font-semibold text-right">{p.university.name}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-400">Country</span>
                <span className="text-sm font-semibold">{p.university.country}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-400">Course</span>
                <span className="text-sm font-semibold">{p.university.course}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-400">Tuition</span>
                <span className="text-sm font-semibold text-green-400">{p.university.fee}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-400">Duration</span>
                <span className="text-sm font-semibold">{p.university.duration}</span>
              </div>
            </div>
          </div>

          {/* STEP 3: COMPANY */}
          <div className={`relative p-5 rounded-3xl border-2 transition-all duration-500 ${
            step >= 2 ? 'border-purple-500/60 bg-gradient-to-br from-purple-500/10 to-transparent shadow-2xl shadow-purple-500/20' : 'border-white/10 bg-white/5'
          }`}>
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-green-500 to-emerald-500 flex items-center justify-center">
                <Briefcase className="w-6 h-6 text-white" />
              </div>
              <div>
                <div className="text-xs text-gray-400 tracking-wider">STEP 3</div>
                <div className="font-bold">Dream Job</div>
              </div>
            </div>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-sm text-gray-400">Company</span>
                <span className="text-sm font-semibold">{p.company.name}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-400">Role</span>
                <span className="text-sm font-semibold">{p.company.role}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-400">Package</span>
                <span className="text-sm font-semibold text-green-400">{p.company.package}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-400">Location</span>
                <span className="text-sm font-semibold">{p.company.location}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-400">Match Score</span>
                <span className="text-sm font-bold text-purple-400">{p.score}/100</span>
              </div>
            </div>
          </div>

          {/* Arrow overlay between cards — desktop only */}
          <ArrowRight className="hidden lg:block absolute top-1/2 left-1/3 -translate-x-1/2 -translate-y-1/2 w-8 h-8 text-purple-400 animate-pulse" style={{ display: step >= 1 ? 'block' : 'none' }} />
        </div>

        {/* Benefits row */}
        <div className="mt-8 flex flex-wrap justify-center gap-3">
          {p.benefits.map((b, i) => (
            <div key={i} className="px-4 py-2 rounded-full bg-green-500/10 border border-green-500/30 text-sm text-green-300 flex items-center gap-2">
              <CheckCircle className="w-4 h-4" />
              {b}
            </div>
          ))}
        </div>

        {/* Pathway dots */}
        <div className="flex justify-center gap-2 mt-8">
          {PATHWAYS.map((_, i) => (
            <button
              key={i}
              onClick={() => { setActive(i); setStep(0); }}
              className={`h-2 rounded-full transition-all ${
                i === active ? 'w-10 bg-purple-400' : 'w-2 bg-white/30'
              }`}
            />
          ))}
        </div>
      </div>
    </section>
  );
}