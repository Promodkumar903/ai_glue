import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  GraduationCap, Briefcase, Building2, Users, Sparkles, ArrowRight,
  MapPin, TrendingUp, Award, Globe, Star, CheckCircle, DollarSign,
  Plane, Shield, Zap, Target, BookOpen
} from 'lucide-react';
import CareerPathway from '../components/CareerPathway';
import LiveSearchPreview from '../components/LiveSearchPreview';
import HowItWorks from '../components/HowItWorks';
import FAQ from '../components/FAQ';
import FinalCTA from '../components/FinalCTA';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// ============ HERO SLIDES (Auto-rotating) ============
const HERO_SLIDES = [
  {
    img: 'https://images.unsplash.com/photo-1523050854058-8df90110c9f1?w=1920&q=80',
    icon: GraduationCap,
    badge: 'STUDY ABROAD',
    title: 'Study in 4,957 Global Universities',
    sub: 'Free tuition in Germany. Scholarships worth ₹35L in UK. 1,346 PR-friendly universities.',
    stat: '4,957',
    statLabel: 'Universities',
  },
  {
    img: 'https://images.unsplash.com/photo-1521737604893-d14cc237f11d?w=1920&q=80',
    icon: Briefcase,
    badge: 'GLOBAL JOBS',
    title: 'Jobs with Free Visa + Relocation',
    sub: 'Nursing in Germany. SDE at Google. Real jobs with verified visa sponsorship & accommodation.',
    stat: '255+',
    statLabel: 'Live Jobs',
  },
  {
    img: 'https://images.unsplash.com/photo-1531482615713-2afd69097998?w=1920&q=80',
    icon: Sparkles,
    badge: 'AI COPILOT',
    title: 'Ask Anything. Get Answers.',
    sub: 'Real-time intelligence on universities, jobs, salaries & scholarships. Powered by Groq + Llama.',
    stat: '24/7',
    statLabel: 'AI Support',
  },
  {
    img: 'https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=1920&q=80',
    icon: Building2,
    badge: 'TOP COMPANIES',
    title: 'Hire or Get Hired Globally',
    sub: 'Google, Microsoft, Amazon, Tesla — verified salary bands, hiring criteria, top colleges.',
    stat: '24+',
    statLabel: 'Companies',
  },
  {
    img: 'https://images.unsplash.com/photo-1523240795612-9a054b0db644?w=1920&q=80',
    icon: Award,
    badge: 'SCHOLARSHIPS',
    title: 'Win ₹35L+ Scholarships',
    sub: 'DAAD, Chevening, Fulbright, MEXT — 23 verified scholarships for Indian & Nepali students.',
    stat: '23',
    statLabel: 'Scholarships',
  },
];

// ============ FEATURED UNIVERSITIES ============
const FEATURED_UNIS = [
  { 
    name: 'Stanford University', country: 'USA', rank: '#2 QS', 
    img: 'https://images.unsplash.com/photo-1541339907198-e08756dedf3f?w=800&q=80', 
    tag: 'AI · CS · MBA', fees: '$55K/yr', accent: 'from-red-500 to-orange-500'
  },
  { 
    name: 'University of Oxford', country: 'UK', rank: '#3 QS', 
    img: 'https://images.unsplash.com/photo-1523050854058-8df90110c9f1?w=800&q=80', 
    tag: 'Law · Medicine', fees: '£35K/yr', accent: 'from-blue-500 to-indigo-500'
  },
  { 
    name: 'TU Munich', country: 'Germany', rank: '#28 QS', 
    img: 'https://images.unsplash.com/photo-1467269204594-9661b134dd2b?w=800&q=80', 
    tag: 'Free Tuition · Engineering', fees: '$0/yr', accent: 'from-yellow-500 to-orange-500'
  },
  { 
    name: 'IIT Bombay', country: 'India', rank: '#118 QS', 
    img: 'https://images.unsplash.com/photo-1562774053-701939374585?w=800&q=80', 
    tag: 'Engineering · CS', fees: '₹2L/yr', accent: 'from-green-500 to-emerald-500'
  },
  { 
    name: 'MIT', country: 'USA', rank: '#1 QS', 
    img: 'https://images.unsplash.com/photo-1564981797816-1043664bf78d?w=800&q=80', 
    tag: 'AI · Robotics', fees: '$60K/yr', accent: 'from-pink-500 to-rose-500'
  },
  { 
    name: 'University of Toronto', country: 'Canada', rank: '#25 QS', 
    img: 'https://images.unsplash.com/photo-1569605803663-e9337d901ff9?w=800&q=80', 
    tag: 'CS · Medicine · PR', fees: 'CAD 45K/yr', accent: 'from-cyan-500 to-blue-500'
  },
  { 
    name: 'NUS Singapore', country: 'Singapore', rank: '#8 QS', 
    img: 'https://images.unsplash.com/photo-1565967511849-76a60a516170?w=800&q=80', 
    tag: 'Business · Tech', fees: 'S$38K/yr', accent: 'from-purple-500 to-pink-500'
  },
  { 
    name: 'University of Tokyo', country: 'Japan', rank: '#32 QS', 
    img: 'https://images.unsplash.com/photo-1542051841857-5f90071e7989?w=800&q=80', 
    tag: 'Research · Robotics', fees: '$5K/yr', accent: 'from-rose-500 to-red-500'
  },
];

// ============ FEATURED COMPANIES ============
const FEATURED_COMPANIES = [
  { name: 'Google', logoUrl: 'https://logo.clearbit.com/google.com', country: 'USA', roles: 'SDE, PM, Research', salary: '₹45L–120L' },
  { name: 'Microsoft', logoUrl: 'https://logo.clearbit.com/microsoft.com', country: 'USA', roles: 'SDE, Cloud, AI', salary: '₹40L–90L' },
  { name: 'Amazon', logoUrl: 'https://logo.clearbit.com/amazon.com', country: 'USA', roles: 'SDE, Data', salary: '₹35L–105L' },
  { name: 'Goldman Sachs', logoUrl: 'https://logo.clearbit.com/goldmansachs.com', country: 'USA', roles: 'Analyst, Quant', salary: '₹35L–120L' },
  { name: 'Tesla', logoUrl: 'https://logo.clearbit.com/tesla.com', country: 'USA', roles: 'SWE, Design', salary: '₹100L+' },
  { name: 'McKinsey', logoUrl: 'https://logo.clearbit.com/mckinsey.com', country: 'USA', roles: 'Consultant, BA', salary: '₹30L–90L' },
  { name: 'Apple', logoUrl: 'https://logo.clearbit.com/apple.com', country: 'USA', roles: 'SWE, Design', salary: '₹110L+' },
  { name: 'Meta', logoUrl: 'https://logo.clearbit.com/meta.com', country: 'USA', roles: 'SWE, AI', salary: '₹120L+' },
  { name: 'Infosys', logoUrl: 'https://logo.clearbit.com/infosys.com', country: 'India', roles: 'SE, Dev', salary: '₹4L–15L' },
];

// ============ TICKER ============
const TICKER_ITEMS = [
  '🇩🇪 Nurse @ Berlin — Visa sponsored, €3500/mo',
  '🇨🇦 SDE @ Toronto — ₹85L, 3-yr PR pathway',
  '🎓 TU Munich — Free tuition, CS Master',
  '🇯🇵 Engineer @ Tokyo — MEXT scholarship',
  '🇬🇧 Data Scientist @ London — £60K, Tier 2 visa',
  '🇦🇺 Nurse @ Sydney — PR pathway, 24-mo work',
  '🎓 Stanford — Need-blind for internationals',
  '🇺🇸 Google — SDE position, ₹45L+ package',
];

// ============ SUCCESS STORIES ============
const SUCCESS_STORIES = [
  { name: 'Rajesh K.', from: 'Delhi → Berlin', role: 'Nurse @ Charité', img: 'https://images.unsplash.com/photo-1531384441138-2736e62e0919?w=200&q=80', quote: 'AI Glue ne visa + job + accommodation sab free me milwa diya.' },
  { name: 'Priya S.', from: 'Mumbai → Toronto', role: 'SDE @ Shopify', img: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=200&q=80', quote: '₹85L package, 3-year PR. Family proud.' },
  { name: 'Amit V.', from: 'Nepal → Tokyo', role: 'Engineer @ Toyota', img: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&q=80', quote: 'Japan ka MEXT scholarship yahan se discover kiya.' },
];

export default function Landing() {
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    universities: 4957, jobs: 255, scholarships: 23, companies: 24, pr_friendly: 1346,
  });
  const [slide, setSlide] = useState(0);

  useEffect(() => {
    fetch(`${API_BASE}/api/oie/stats`)
      .then(r => r.json())
      .then(data => {
        if (data && typeof data === 'object' && !data.detail) {
          setStats(prev => ({ ...prev, ...data }));
        }
      })
      .catch(() => {});
  }, []);

  // Auto-rotate hero every 4 sec
  useEffect(() => {
    const t = setInterval(() => {
      setSlide(s => (s + 1) % HERO_SLIDES.length);
    }, 4000);
    return () => clearInterval(t);
  }, []);

  const openLogin = (role = 'Student') => navigate(`/login?role=${role}`);

  const currentSlide = HERO_SLIDES[slide];
  const SlideIcon = currentSlide.icon;

  return (
    <div className="min-h-screen bg-slate-950 text-white overflow-x-hidden">

      {/* HEADER */}
      <header className="fixed top-0 left-0 right-0 z-50 backdrop-blur-lg bg-slate-950/80 border-b border-white/10">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <img src="/logo-dark.svg" alt="AI Glue" className="h-10 w-auto" />
            <span className="text-xl font-bold">
              AI Glue <span className="text-purple-400">OIE</span>
            </span>
            <span className="px-2 py-0.5 text-xs rounded-full bg-green-500/20 text-green-400 border border-green-500/30">v8.1</span>
          </div>
          <button
            onClick={() => openLogin()}
            className="px-5 py-2 rounded-lg bg-gradient-to-r from-purple-500 to-pink-500 text-sm font-semibold hover:opacity-90"
          >
            Login
          </button>
        </div>
      </header>

      {/* HERO CAROUSEL */}
      <section className="relative h-[80vh] min-h-[560px] overflow-hidden">
        {/* Background Images — crossfade */}
        {HERO_SLIDES.map((s, i) => (
          <div
            key={i}
            className={`absolute inset-0 transition-opacity duration-1000 ${i === slide ? 'opacity-100' : 'opacity-0'}`}
          >
            <img src={s.img} alt="" className="w-full h-full object-cover" />
            <div className="absolute inset-0 bg-gradient-to-r from-slate-950 via-slate-950/85 to-slate-950/40" />
          </div>
        ))}

        {/* Content */}
        <div className="relative z-10 h-full flex items-center">
          <div className="max-w-7xl mx-auto px-6 w-full grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <div className="inline-flex items-center gap-2 px-4 py-1.5 mb-6 rounded-full bg-white/10 backdrop-blur border border-white/20 text-sm">
                <SlideIcon className="w-4 h-4 text-purple-400" />
                <span className="font-semibold tracking-wide">{currentSlide.badge}</span>
              </div>
              <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold mb-6 leading-tight">
                {currentSlide.title.split(' ').map((w, i) =>
                  i >= currentSlide.title.split(' ').length - 2 ? (
                    <span key={i} className="bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                      {w}{' '}
                    </span>
                  ) : (
                    <span key={i}>{w} </span>
                  )
                )}
              </h1>
              <p className="text-lg text-gray-300 mb-8 max-w-xl">{currentSlide.sub}</p>

              <div className="flex flex-wrap gap-4 mb-10">
                <button
                  onClick={() => openLogin()}
                  className="px-8 py-4 rounded-xl bg-gradient-to-r from-purple-500 to-pink-500 font-semibold hover:opacity-90 inline-flex items-center gap-2 text-lg"
                >
                  Get Started Free <ArrowRight className="w-5 h-5" />
                </button>
                <button
                  onClick={() => openLogin('JOBSEEKER')}
                  className="px-8 py-4 rounded-xl bg-white/10 backdrop-blur border border-white/20 font-semibold hover:bg-white/20 inline-flex items-center gap-2 text-lg"
                >
                  Explore Jobs
                </button>
              </div>

              {/* Slide Dots */}
              <div className="flex gap-2">
                {HERO_SLIDES.map((_, i) => (
                  <button
                    key={i}
                    onClick={() => setSlide(i)}
                    className={`h-1.5 rounded-full transition-all ${
                      i === slide ? 'w-12 bg-purple-400' : 'w-6 bg-white/30 hover:bg-white/60'
                    }`}
                  />
                ))}
              </div>
            </div>

            {/* Right: Live stat card */}
            <div className="hidden lg:block">
              <div className="p-6 rounded-3xl bg-white/5 backdrop-blur-xl border border-white/20 shadow-2xl">
                <div className="text-sm text-gray-400 mb-2">Currently available</div>
                <div className="text-6xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent mb-2">
                  {currentSlide.stat}
                </div>
                <div className="text-xl text-gray-300 mb-6">{currentSlide.statLabel}</div>

                <div className="space-y-3 pt-6 border-t border-white/10">
                  {[
                    { icon: GraduationCap, label: 'Universities', value: stats.universities.toLocaleString() },
                    { icon: Briefcase, label: 'Live Jobs', value: stats.jobs },
                    { icon: Award, label: 'Scholarships', value: stats.scholarships },
                    { icon: Globe, label: 'PR-Friendly', value: stats.pr_friendly.toLocaleString() },
                  ].map((s, i) => (
                    <div key={i} className="flex items-center justify-between">
                      <div className="flex items-center gap-3 text-gray-300">
                        <s.icon className="w-4 h-4 text-purple-400" />
                        <span className="text-sm">{s.label}</span>
                      </div>
                      <span className="font-bold">{s.value}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom wave */}
        <div className="absolute bottom-0 left-0 right-0 h-24 bg-gradient-to-t from-slate-950 to-transparent" />
      </section>

      {/* LIVE TICKER */}
      <section className="py-5 bg-gradient-to-r from-purple-500/10 via-pink-500/10 to-purple-500/10 border-y border-white/10 overflow-hidden">
        <div className="flex items-center gap-4 mb-3 max-w-7xl mx-auto px-6">
          <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
          <span className="text-xs font-bold text-red-400 tracking-wider">LIVE</span>
          <span className="text-xs text-gray-500">Real-time from 20+ global sources</span>
        </div>
        <div className="flex animate-marquee whitespace-nowrap">
          {[...TICKER_ITEMS, ...TICKER_ITEMS].map((item, i) => (
            <div key={i} className="inline-block mx-8 text-gray-300 text-sm">{item}</div>
          ))}
        </div>
        <style>{`
          @keyframes marquee {
            from { transform: translateX(0); }
            to { transform: translateX(-50%); }
          }
          .animate-marquee { animation: marquee 40s linear infinite; }
        `}</style>
      </section>
      {/* CAREER PATHWAY VISUALIZER */}
      <CareerPathway />
      {/* LIVE SEARCH PREVIEW */}
      <LiveSearchPreview />
      {/* 4 THINGS INSIDE */}
      <section className="py-12 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-10">
            <div className="inline-block px-4 py-1.5 mb-4 rounded-full bg-purple-500/10 border border-purple-500/30 text-sm text-purple-300">
              What's Inside
            </div>
            <h2 className="text-3xl md:text-4xl font-bold mb-4">Everything in One Platform</h2>
            <p className="text-gray-400 text-lg">From finding a university to landing a global job — full pathway.</p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              { icon: GraduationCap, title: 'Study', desc: '4,957 universities in 25 countries', stat: '4,957', color: 'from-blue-500 to-cyan-500' },
              { icon: Briefcase, title: 'Work', desc: 'Real jobs with visa sponsorship', stat: '255+', color: 'from-purple-500 to-pink-500' },
              { icon: Award, title: 'Scholarships', desc: 'DAAD, Chevening, Fulbright', stat: '23', color: 'from-yellow-500 to-orange-500' },
              { icon: Building2, title: 'Companies', desc: 'Salary bands & hiring criteria', stat: '24+', color: 'from-green-500 to-emerald-500' },
            ].map((card, i) => (
              <div key={i} className="p-5 rounded-xl bg-white/5 border border-white/10 hover:border-purple-500/40 transition group">
                <div className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${card.color} flex items-center justify-center mb-4 group-hover:scale-110 transition`}>
                  <card.icon className="w-7 h-7 text-white" />
                </div>
                <div className="ttext-2xl font-bold mb-1">{card.stat}</div>
                <div className="text-lg font-semibold mb-2">{card.title}</div>
                <p className="text-sm text-gray-400">{card.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* FEATURED UNIVERSITIES */}
      <section className="py-12 px-6 bg-white/[0.02]">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-end justify-between mb-10">
            <div>
              <h2 className="text-4xl font-bold mb-2">Featured Universities</h2>
              <p className="text-gray-400">Top-ranked institutions with real placement data</p>
            </div>
            <button onClick={() => openLogin()} className="text-purple-400 hover:underline flex items-center gap-1 text-sm">
              View all {stats.universities.toLocaleString()} <ArrowRight className="w-4 h-4" />
            </button>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
            {FEATURED_UNIS.map((uni, i) => (
              <div key={i} onClick={() => openLogin()} className="group rounded-2xl overflow-hidden bg-white/5 border border-white/10 hover:border-purple-500/40 cursor-pointer transition-all hover:-translate-y-2">
                <div className="h-32 overflow-hidden relative">
  <img 
    src={uni.img} 
    alt={uni.name} 
    loading="lazy"
    className="w-full h-full object-cover group-hover:scale-110 transition duration-700"
    onError={(e) => { 
      e.target.style.display = 'none';
      e.target.parentElement.classList.add('bg-gradient-to-br', uni.accent);
    }}
  />
  <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-transparent to-transparent" />
  <div className="absolute top-3 right-3 px-2 py-1 rounded-full bg-black/70 backdrop-blur text-xs font-semibold">{uni.rank}</div>
  <div className="absolute bottom-3 left-3 flex items-center gap-1 text-xs text-white/90">
    <MapPin className="w-3 h-3" /> {uni.country}
  </div>
</div>
                <div className="p-5">
                  <h3 className="font-bold mb-1">{uni.name}</h3>
                  <div className="flex items-center gap-1 text-xs text-gray-500 mb-3">
                    <MapPin className="w-3 h-3" /> {uni.country}
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-400">{uni.tag}</span>
                    <span className="text-purple-300 font-semibold">{uni.fees}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* FEATURED COMPANIES */}
      <section className="py-12 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-end justify-between mb-10">
            <div>
              <h2 className="text-4xl font-bold mb-2">Top Hiring Companies</h2>
              <p className="text-gray-400">Verified salary bands & career paths</p>
            </div>
            <button onClick={() => openLogin()} className="text-purple-400 hover:underline flex items-center gap-1 text-sm">
              View all {stats.companies} <ArrowRight className="w-4 h-4" />
            </button>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {FEATURED_COMPANIES.map((c, i) => (
              <div key={i} onClick={() => openLogin()} className="p-5 rounded-xl bg-white/5 border border-white/10 hover:border-purple-500/40 cursor-pointer transition-all">
                <div className="flex items-center gap-4 mb-4">
                  <div className="w-14 h-14 rounded-2xl bg-white flex items-center justify-center overflow-hidden p-2">
  <img 
    src={c.logoUrl} 
    alt={c.name}
    className="w-full h-full object-contain"
    onError={(e) => { e.target.src = 'https://via.placeholder.com/56?text=' + c.name[0]; }}
  />
</div>
                  <div>
                    <div className="font-bold text-lg">{c.name}</div>
                    <div className="text-xs text-gray-500">{c.country}</div>
                  </div>
                </div>
                <div className="text-sm text-gray-400 mb-3">{c.roles}</div>
                <div className="flex items-center gap-2 text-purple-300">
                  <TrendingUp className="w-4 h-4" />
                  <span className="font-semibold">{c.salary}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* SUCCESS STORIES */}
      <section className="py-12 px-6 bg-white/[0.02]">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-4xl font-bold mb-2 text-center">Success Stories</h2>
          <p className="text-gray-400 mb-8 text-center">Real people, real journeys</p>
          <div className="grid md:grid-cols-3 gap-4">
            {SUCCESS_STORIES.map((s, i) => (
              <div key={i} className="p-5 rounded-xl bg-white/5 border border-white/10 hover:border-purple-500/40 transition">
                <div className="flex items-center gap-4 mb-4">
                  <img src={s.img} alt={s.name} className="w-16 h-16 rounded-full object-cover ring-2 ring-purple-500/40" />
                  <div>
                    <div className="font-bold">{s.name}</div>
                    <div className="text-xs text-gray-500">{s.from}</div>
                  </div>
                </div>
                <div className="flex items-center gap-2 text-purple-300 mb-3">
                  <Award className="w-4 h-4" />
                  <span className="text-sm font-semibold">{s.role}</span>
                </div>
                <p className="text-sm text-gray-300 italic">"{s.quote}"</p>
                <div className="flex gap-1 mt-4">
                  {[...Array(5)].map((_, j) => <Star key={j} className="w-4 h-4 text-yellow-400 fill-yellow-400" />)}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
      {/* COMPARISON TABLE */}
<section className="py-12 px-6 bg-white/[0.02]">
  <div className="max-w-5xl mx-auto">
    <div className="text-center mb-8">
      <h2 className="text-3xl md:text-4xl font-bold mb-4">Why Choose Us?</h2>
      <p className="text-lg text-gray-400">See how AI Glue OIE compares</p>
    </div>

    <div className="rounded-2xl bg-slate-900/60 border border-white/10 overflow-hidden">
      {/* Header */}
      <div className="grid grid-cols-4 p-4 border-b border-white/10 bg-white/5">
        <div className="text-sm text-gray-400 font-semibold">Feature</div>
        <div className="text-center">
          <div className="text-sm font-bold text-purple-300">AI Glue OIE</div>
          <div className="text-xs text-purple-400">✨ Our Edge</div>
        </div>
        <div className="text-center text-sm text-gray-400">Traditional Agents</div>
        <div className="text-center text-sm text-gray-400">Other Platforms</div>
      </div>

      {/* Rows */}
      {[
        { feature: 'Real-time live data', us: true, agents: false, others: false },
        { feature: 'Verified evidence per claim', us: true, agents: false, others: false },
        { feature: 'AI Copilot 24/7', us: true, agents: false, others: false },
        { feature: 'Student → Uni → Company pathway', us: true, agents: false, others: false },
        { feature: '4,957 universities direct', us: true, agents: false, others: true },
        { feature: 'Real salary bands', us: true, agents: false, others: false },
        { feature: 'Transparent (no hidden fee)', us: true, agents: false, others: true },
        { feature: 'Free for students', us: true, agents: false, others: true },
      ].map((row, i) => (
        <div key={i} className="grid grid-cols-4 p-4 border-b border-white/5 hover:bg-white/5 transition">
          <div className="text-sm text-gray-300">{row.feature}</div>
          <div className="text-center">
            {row.us ? <CheckCircle className="w-5 h-5 text-green-400 mx-auto" /> : <span className="text-red-400">✕</span>}
          </div>
          <div className="text-center">
            {row.agents ? <CheckCircle className="w-5 h-5 text-green-400 mx-auto" /> : <span className="text-red-400">✕</span>}
          </div>
          <div className="text-center">
            {row.others ? <CheckCircle className="w-5 h-5 text-green-400 mx-auto" /> : <span className="text-red-400">✕</span>}
          </div>
        </div>
      ))}
    </div>
  </div>
</section>

      {/* WHY US */}
      <section className="py-12 px-6">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-4xl font-bold mb-8 text-center">Why AI Glue OIE?</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              { icon: Shield, title: 'Verified Data', desc: 'Every claim has source evidence & trust score', color: 'from-green-500 to-emerald-500' },
              { icon: Globe, title: 'Global Reach', desc: '25 countries, 4,957 unis, 24+ top companies', color: 'from-blue-500 to-cyan-500' },
              { icon: DollarSign, title: 'Free Education', desc: '392 universities with zero tuition fee', color: 'from-yellow-500 to-orange-500' },
              { icon: Target, title: 'Career Pathway', desc: 'Student → University → Company end-to-end', color: 'from-purple-500 to-pink-500' },
            ].map((card, i) => (
              <div key={i} className="p-5 rounded-xl bg-white/5 border border-white/10 hover:border-purple-500/40 transition">
                <div className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${card.color} flex items-center justify-center mb-4`}>
                  <card.icon className="w-7 h-7 text-white" />
                </div>
                <h3 className="font-bold mb-2 text-lg">{card.title}</h3>
                <p className="text-sm text-gray-400">{card.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 4 ECOSYSTEMS */}
      <section className="py-12 px-6 bg-white/[0.02]">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-4xl font-bold mb-4 text-center">Choose Your Ecosystem</h2>
          <p className="text-gray-400 mb-8 text-center">Login and unlock your dashboard</p>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              { icon: GraduationCap, title: 'Student', desc: 'Universities, scholarships, study abroad', color: 'from-blue-500 to-cyan-500', role: 'Student' },
              { icon: Briefcase, title: 'Job Seeker', desc: 'Global jobs with visa sponsorship', color: 'from-purple-500 to-pink-500', role: 'JOBSEEKER' },
              { icon: Building2, title: 'Company', desc: 'Hire verified candidates', color: 'from-green-500 to-emerald-500', role: 'EMPLOYER' },
              { icon: Users, title: 'University', desc: 'Placement stats, rankings', color: 'from-orange-500 to-yellow-500', role: 'UNIVERSITY' },
            ].map((card, i) => (
              <div key={i} onClick={() => openLogin(card.role)} className="p-5 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 hover:border-purple-500/40 transition cursor-pointer group">
                <div className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${card.color} flex items-center justify-center mb-4 group-hover:scale-110 transition`}>
                  <card.icon className="w-7 h-7 text-white" />
                </div>
                <h3 className="text-xl font-bold mb-2">{card.title}</h3>
                <p className="text-sm text-gray-400 mb-4">{card.desc}</p>
                <div className="flex items-center text-purple-400 text-sm font-semibold">
                  Login <ArrowRight className="w-4 h-4 ml-1 group-hover:translate-x-1 transition" />
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* TRUST */}
      <section className="py-12 px-6 border-y border-white/10">
        <div className="max-w-6xl mx-auto text-center">
          <p className="text-xs text-gray-500 mb-6 tracking-wider">POWERED BY TRUSTED GLOBAL SOURCES</p>
          <div className="flex flex-wrap justify-center items-center gap-5 text-gray-500 text-sm">
            <span>Make it in Germany</span><span>·</span>
            <span>NCS India</span><span>·</span>
            <span>Hipolabs</span><span>·</span>
            <span>NIRF</span><span>·</span>
            <span>QS Rankings</span><span>·</span>
            <span>EURES</span>
          </div>
        </div>
      </section>
      {/* HOW IT WORKS */}
      <HowItWorks />

      {/* FAQ */}
      <FAQ />
      <section className="py-14 px-6">
        <div className="max-w-3xl mx-auto text-center">
          <Zap className="w-12 h-12 text-purple-400 mx-auto mb-6" />
          <h2 className="text-3xl md:text-4xl font-bold mb-6">
            Ready to explore <span className="bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">5,000+ opportunities</span>?
          </h2>
          <p className="text-lg text-gray-400 mb-8">Join thousands of students, job seekers, and companies.</p>
          <button
            onClick={() => openLogin()}
            className="px-10 py-5 rounded-xl bg-gradient-to-r from-purple-500 to-pink-500 text-lg font-semibold hover:opacity-90 inline-flex items-center gap-2"
          >
            Get Started Free <ArrowRight className="w-5 h-5" />
          </button>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="py-8 px-6 text-center text-sm text-gray-500 border-t border-white/10">
        © 2026 AI Glue OIE · Manpower + Education Unified Platform
      </footer>
    </div>
  );
}