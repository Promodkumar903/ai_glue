import React from 'react';
import { Shield } from 'lucide-react';

export default function PrivacyPolicy() {
  return (
    <div className="min-h-screen bg-slate-50">
      <div className="relative h-[350px] overflow-hidden">
        <div className="absolute inset-0 bg-cover bg-center" style={{ backgroundImage: `url('https://images.unsplash.com/photo-1563013544-824ae1b704d3?w=1920&q=80')` }} />
        <div className="absolute inset-0 bg-gradient-to-r from-purple-900/90 via-purple-800/80 to-pink-900/90" />
        <div className="relative h-full flex flex-col items-center justify-center px-6 text-center text-white">
          <div className="w-16 h-16 bg-white/20 backdrop-blur-md rounded-2xl flex items-center justify-center border border-white/30 mb-4">
            <Shield className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-5xl md:text-6xl font-extrabold mb-3 tracking-tight">Privacy Policy</h1>
          <p className="text-lg opacity-90">Last updated: October 5, 2026</p>
        </div>
      </div>

      <div className="max-w-4xl mx-auto py-16 px-6 -mt-12 relative z-10">
        <div className="bg-white rounded-3xl shadow-2xl p-10 border border-slate-100">
          <div className="space-y-8 text-slate-700 leading-relaxed">
            <section>
              <div className="flex items-center gap-3 mb-3">
                <span className="w-1 h-6 bg-gradient-to-b from-purple-500 to-pink-500 rounded-full"></span>
                <h2 className="text-2xl font-bold text-slate-800">1. Introduction</h2>
              </div>
              <p>AI Glue ("we", "our", "us") operates <strong>aiglueagent.com</strong>. We are committed to protecting your privacy. This Privacy Policy explains how we collect, use, disclose, and safeguard your information.</p>
            </section>

            <section>
              <div className="flex items-center gap-3 mb-3">
                <span className="w-1 h-6 bg-gradient-to-b from-purple-500 to-pink-500 rounded-full"></span>
                <h2 className="text-2xl font-bold text-slate-800">2. Information We Collect</h2>
              </div>
              <ul className="list-disc pl-6 space-y-2">
                <li><strong>Personal Info:</strong> Name, email, phone, encrypted password</li>
                <li><strong>Profile Data:</strong> Education, work history, resume, documents</li>
                <li><strong>Payment Info:</strong> Processed via Razorpay/UPI/eSewa — we don't store card details</li>
                <li><strong>Usage Data:</strong> IP address, browser, pages visited</li>
              </ul>
            </section>

            <section>
              <div className="flex items-center gap-3 mb-3">
                <span className="w-1 h-6 bg-gradient-to-b from-purple-500 to-pink-500 rounded-full"></span>
                <h2 className="text-2xl font-bold text-slate-800">3. How We Use Your Information</h2>
              </div>
              <ul className="list-disc pl-6 space-y-2">
                <li>Provide and improve our services</li>
                <li>Match you with relevant opportunities</li>
                <li>Process payments and send invoices</li>
                <li>Send service-related notifications</li>
                <li>Prevent fraud and ensure security</li>
              </ul>
            </section>

            <section>
              <div className="flex items-center gap-3 mb-3">
                <span className="w-1 h-6 bg-gradient-to-b from-purple-500 to-pink-500 rounded-full"></span>
                <h2 className="text-2xl font-bold text-slate-800">4. Information Sharing</h2>
              </div>
              <p className="mb-3">We <strong>never sell</strong> your personal data. We may share with:</p>
              <ul className="list-disc pl-6 space-y-2">
                <li><strong>Employers/Universities:</strong> Only when you apply</li>
                <li><strong>Service Providers:</strong> Razorpay (payments), SMTP (emails)</li>
                <li><strong>Legal:</strong> If required by law</li>
              </ul>
            </section>

            <section>
              <div className="flex items-center gap-3 mb-3">
                <span className="w-1 h-6 bg-gradient-to-b from-purple-500 to-pink-500 rounded-full"></span>
                <h2 className="text-2xl font-bold text-slate-800">5. Data Security</h2>
              </div>
              <p>We use industry-standard security — encrypted passwords (bcrypt), HTTPS, secure sessions. However, no system is 100% secure.</p>
            </section>

            <section>
              <div className="flex items-center gap-3 mb-3">
                <span className="w-1 h-6 bg-gradient-to-b from-purple-500 to-pink-500 rounded-full"></span>
                <h2 className="text-2xl font-bold text-slate-800">6. Your Rights</h2>
              </div>
              <ul className="list-disc pl-6 space-y-2">
                <li>Access your data anytime</li>
                <li>Update your data from profile</li>
                <li>Delete account: email support@aiglueagent.com</li>
                <li>Opt-out of marketing emails</li>
              </ul>
            </section>

            <section>
              <div className="flex items-center gap-3 mb-3">
                <span className="w-1 h-6 bg-gradient-to-b from-purple-500 to-pink-500 rounded-full"></span>
                <h2 className="text-2xl font-bold text-slate-800">7. Contact</h2>
              </div>
              <p>For privacy concerns: <a href="mailto:support@aiglueagent.com" className="text-purple-600 hover:underline font-medium">support@aiglueagent.com</a></p>
            </section>
          </div>
        </div>
      </div>
    </div>
  );
}