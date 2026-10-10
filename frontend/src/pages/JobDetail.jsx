import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';

export default function JobDetail() {
  const { jobId } = useParams();
  const navigate = useNavigate();
  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadJob();
  }, [jobId]);

  const loadJob = async () => {
    try {
      setLoading(true);
      const r = await api.get(`/admin/oie/job-detail/${jobId}`);
      setJob(r.data);
    } catch (e) {
      setError('Job not found or expired');
    } finally {
      setLoading(false);
    }
  };

  const handleApply = () => {
    // Redirect to original source listing (external site)
    if (job?.job_url) {
      window.open(job.job_url, '_blank');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="text-slate-500">Loading job details...</div>
      </div>
    );
  }

  if (error || !job) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50 p-4">
        <div className="bg-white rounded-xl p-8 max-w-md text-center shadow-sm border border-slate-200">
          <div className="text-4xl mb-3">🔍</div>
          <div className="text-lg font-semibold mb-2">Job Not Found</div>
          <div className="text-sm text-slate-500 mb-4">
            This job may have expired or the link is invalid.
          </div>
          <button
            onClick={() => navigate('/')}
            className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
          >
            Go Home
          </button>
        </div>
      </div>
    );
  }

  // Company initials
  const words = (job.company_name || '').split(' ').filter(w => w);
  const initials = words.length >= 2
    ? (words[0][0] + words[1][0]).toUpperCase()
    : (words[0]?.slice(0, 2) || 'CO').toUpperCase();

  return (
    <div className="min-h-screen bg-slate-50 py-8 px-4">
      <div className="max-w-2xl mx-auto">

        {/* Back button */}
        <button
          onClick={() => navigate(-1)}
          className="mb-4 text-sm text-slate-600 hover:text-slate-900 flex items-center gap-1"
        >
          ← Back
        </button>

        {/* Header card */}
        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
          <div className="bg-gradient-to-r from-purple-600 to-indigo-600 p-6 text-white">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 bg-white rounded-xl flex items-center justify-center text-purple-600 font-bold text-2xl">
                {initials}
              </div>
              <div>
                <div className="text-xs uppercase tracking-wide text-purple-200 mb-1">
                  Verified Job
                </div>
                <h1 className="text-2xl font-bold">{job.job_title}</h1>
                <div className="text-sm text-purple-100 mt-1">{job.company_name}</div>
              </div>
            </div>
          </div>

          {/* Details */}
          <div className="p-6 space-y-5">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="text-xs text-slate-500 mb-1">Location</div>
                <div className="font-semibold">📍 {job.country || 'Unknown'}</div>
              </div>
              <div>
                <div className="text-xs text-slate-500 mb-1">Region</div>
                <div className="font-semibold">{job.region || '—'}</div>
              </div>
              <div>
                <div className="text-xs text-slate-500 mb-1">Match Score</div>
                <div className="font-semibold text-purple-600">{job.verification_score || 85}%</div>
              </div>
              <div>
                <div className="text-xs text-slate-500 mb-1">Source</div>
                <div className="font-semibold text-xs">
                  {job.job_url ? 'Verified Listing' : 'Direct'}
                </div>
              </div>
            </div>

            {/* Benefits */}
            <div className="bg-indigo-50 rounded-xl p-4 border-l-4 border-purple-500">
              <div className="font-semibold text-sm text-purple-800 mb-3">✅ Benefits</div>
              <div className="space-y-2 text-sm">
                <BenefitRow label="Free Visa" ok={job.free_visa} />
                <BenefitRow label="Free Air Ticket" ok={job.free_ticket} />
                <BenefitRow label="Accommodation" ok={job.accommodation} />
                <BenefitRow label="No Commission" ok={job.no_commission} />
              </div>
            </div>

            {/* Warning */}
            <div className="text-xs text-slate-500 bg-slate-50 rounded-lg p-3 border border-slate-200">
              🔒 <b>Safety:</b> AI Glue verified this job from official sources. Never pay
              any money for a job offer. Report suspicious activity to our team.
            </div>

            {/* Apply button */}
            <div className="pt-2 space-y-3">
              <button
                onClick={handleApply}
                className="w-full py-4 bg-purple-600 text-white rounded-xl font-bold text-lg hover:bg-purple-700 transition shadow-lg shadow-purple-200"
              >
                Apply on Official Site →
              </button>
              {job.job_url && (
                <div className="text-xs text-center text-slate-400 break-all">
                  {job.job_url}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* AI Glue footer */}
        <div className="text-center mt-8 text-sm text-slate-500">
          <div className="font-bold text-purple-600">🔗 AI Glue</div>
          <div className="text-xs mt-1">Verified Jobs · Global Opportunities</div>
        </div>
      </div>
    </div>
  );
}

function BenefitRow({ label, ok }) {
  return (
    <div className="flex items-center gap-2">
      <span className={ok ? 'text-green-600' : 'text-red-400'}>
        {ok ? '✅' : '❌'}
      </span>
      <span className={ok ? 'text-slate-700' : 'text-slate-400'}>
        {label} {ok ? 'provided' : 'not mentioned'}
      </span>
    </div>
  );
}