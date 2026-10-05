import React from 'react';
import { FileText } from 'lucide-react';

export default function TermsOfService() {
  return (
    <div className="min-h-screen bg-slate-50">
      <div className="relative h-[350px] overflow-hidden">
        <div className="absolute inset-0 bg-cover bg-center" style={{ backgroundImage: `url('https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=1920&q=80')` }} />
        <div className="absolute inset-0 bg-gradient-to-r from-purple-900/90 via-purple-800/80 to-pink-900/90" />
        <div className="relative h-full flex flex-col items-center justify-center px-6 text-center text-white">
          <div className="w-16 h-16 bg-white/20 backdrop-blur-md rounded-2xl flex items-center justify-center border border-white/30 mb-4">
            <FileText className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-5xl md:text-6xl font-extrabold mb-3 tracking-tight">Terms of Service</h1>
          <p className="text-lg opacity-90">Last updated: October 5, 2026</p>
        </div>
      </div>

      <div className="max-w-4xl mx-auto py-16 px-6 -mt-12 relative z-10">
        <div className="bg-white rounded-3xl shadow-2xl p-10 border border-slate-100">
          <div className="space-y-8 text-slate-700 leading-relaxed">
            <section>
              <div className="flex items-center gap-3 mb-3">
                <span className="w-1 h-6 bg-gradient-to-b from-purple-500 to-pink-500 rounded-full"></span>
                <h2 className="text-2xl font-bold text-slate-800">1. Acceptance of Terms</h2>
              </div>
              <p>By accessing <strong>aiglueagent.com</strong>, you agree to these Terms. If you don't agree, please don't use our platform.</p>
            </section>

            <section>
              <div className="flex items-center gap-3 mb-3">
                <span className="w-1 h-6 bg-gradient-to-b from-purple-500 to-pink-500 rounded-full"></span>
                <h2 className="text-2xl font-bold text-slate-800">2. Eligibility</h2>
              </div>
              <ul className="list-disc pl-6 space-y-2">
                <li>You must be 16+ years old</li>
                <li>Provide accurate information during registration</li>
                <li>One account per person (unless employer/organization)</li>
                <li>You are responsible for account security</li>
              </ul>
            </section>

            <section>
              <div className="flex items-center gap-3 mb-3">
                <span className="w-1 h-6 bg-gradient-to-b from-purple-500 to-pink-500 rounded-full"></span>
                <h2 className="text-2xl font-bold text-slate-800">3. Subscription & Payments</h2>
              </div>
              <ul className="list-disc pl-6 space-y-2">
                <li><strong>Plans:</strong> Free, Basic, Pro, Enterprise</li>
                <li><strong>Payment Methods:</strong> Razorpay, UPI, eSewa, PayPal</li>
                <li><strong>Manual Payments:</strong> Verified by admin within 24 hours</li>
                <li><strong>Currency:</strong> INR (India), NPR (Nepal), USD (International)</li>
                <li><strong>Refunds:</strong> Case-by-case. Email within 7 days</li>
                <li><strong>Cancellation:</strong> Anytime from dashboard</li>
              </ul>
            </section>

            <section>
              <div className="flex items-center gap-3 mb-3">
                <span className="w-1 h-6 bg-gradient-to-b from-purple-500 to-pink-500 rounded-full"></span>
                <h2 className="text-2xl font-bold text-slate-800">4. Acceptable Use</h2>
              </div>
              <p className="mb-3"><strong>You agree NOT to:</strong></p>
              <ul className="list-disc pl-6 space-y-2">
                <li>Post false or misleading information</li>
                <li>Impersonate others</li>
                <li>Upload malicious files or spam</li>
                <li>Attempt to hack or circumvent security</li>
                <li>Use platform for illegal activities</li>
                <li>Harass other users</li>
              </ul>
              <p className="mt-3 text-sm text-red-600 font-medium">Violation may result in account suspension without refund.</p>
            </section>

            <section>
              <div className="flex items-center gap-3 mb-3">
                <span className="w-1 h-6 bg-gradient-to-b from-purple-500 to-pink-500 rounded-full"></span>
                <h2 className="text-2xl font-bold text-slate-800">5. Content Ownership</h2>
              </div>
              <ul className="list-disc pl-6 space-y-2">
                <li><strong>Your content:</strong> You own your resume, documents, profile</li>
                <li><strong>Our platform:</strong> AI Glue owns the code, design, brand</li>
                <li><strong>License:</strong> By uploading, you grant us permission to use for matching/services</li>
              </ul>
            </section>

            <section>
              <div className="flex items-center gap-3 mb-3">
                <span className="w-1 h-6 bg-gradient-to-b from-purple-500 to-pink-500 rounded-full"></span>
                <h2 className="text-2xl font-bold text-slate-800">6. Disclaimer</h2>
              </div>
              <p>AI Glue is a <strong>platform</strong>. We don't guarantee job placement, visa approval, or university admission. Our AI matching is a tool — final decisions are with employers/universities/governments.</p>
            </section>

            <section>
              <div className="flex items-center gap-3 mb-3">
                <span className="w-1 h-6 bg-gradient-to-b from-purple-500 to-pink-500 rounded-full"></span>
                <h2 className="text-2xl font-bold text-slate-800">7. Limitation of Liability</h2>
              </div>
              <p>AI Glue is not liable for indirect/consequential damages. Total liability = amount paid in last 6 months (max).</p>
            </section>

            <section>
              <div className="flex items-center gap-3 mb-3">
                <span className="w-1 h-6 bg-gradient-to-b from-purple-500 to-pink-500 rounded-full"></span>
                <h2 className="text-2xl font-bold text-slate-800">8. Governing Law</h2>
              </div>
              <p>These terms are governed by Indian law. Disputes resolved in Indian courts.</p>
            </section>

            <section>
              <div className="flex items-center gap-3 mb-3">
                <span className="w-1 h-6 bg-gradient-to-b from-purple-500 to-pink-500 rounded-full"></span>
                <h2 className="text-2xl font-bold text-slate-800">9. Contact</h2>
              </div>
              <p>Questions? Email: <a href="mailto:support@aiglueagent.com" className="text-purple-600 hover:underline font-medium">support@aiglueagent.com</a></p>
            </section>
          </div>
        </div>
      </div>
    </div>
  );
}