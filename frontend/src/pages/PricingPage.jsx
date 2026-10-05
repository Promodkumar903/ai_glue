import React, { useState, useEffect } from 'react';
import { QRCodeSVG } from 'qrcode.react';
import { useAuth } from '../lib/auth-context';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Fallback values — agar admin settings load na ho toh
const DEFAULTS = {
  upi_id_1: 'pramod.rf@oksbi',
  upi_id_2: '8174015550@idfcfirst',
  esewa_id: '9826448788',
  esewa_name: 'Promod Kumar',
  paypal_link: 'https://paypal.me/promod662',
  paypal_username: 'promod662',
};

export default function PricingPage() {
  const { user } = useAuth();
  const [plans, setPlans] = useState([]);
  const [cycle, setCycle] = useState('monthly');
  const [activePromo, setActivePromo] = useState(null);
  const [selectedPlan, setSelectedPlan] = useState(null);
  const [success, setSuccess] = useState('');
  const [settings, setSettings] = useState(DEFAULTS);

  useEffect(() => {
    fetch(`${API_BASE}/subscriptions/plans`).then(r => r.json()).then(d => setPlans(d.plans || []));
    fetch(`${API_BASE}/promotions/active`).then(r => r.json()).then(d => {
      const promo = (d.promotions || []).find(p => p.type === 'promotion' && p.discount_percent > 0);
      if (promo) setActivePromo(promo);
    });
    fetch(`${API_BASE}/payments/settings`)
      .then(r => r.json())
      .then(d => {
        if (d.settings) {
          setSettings({
            upi_id_1: d.settings.upi_id_1 || DEFAULTS.upi_id_1,
            upi_id_2: d.settings.upi_id_2 || DEFAULTS.upi_id_2,
            esewa_id: d.settings.esewa_id || DEFAULTS.esewa_id,
            esewa_name: d.settings.esewa_name || DEFAULTS.esewa_name,
            paypal_link: d.settings.paypal_link || DEFAULTS.paypal_link,
            paypal_username: DEFAULTS.paypal_username,
          });
        }
      })
      .catch(() => {});
  }, []);

  const getPrice = (plan) => cycle === 'monthly' ? plan.price_monthly : plan.price_yearly;
  const getFinalPrice = (plan) => {
    const base = getPrice(plan);
    if (!activePromo || plan.name === 'Free') return base;
    return Math.round(base * (1 - activePromo.discount_percent / 100));
  };

  return (
    <div className="min-h-screen bg-slate-50 p-6">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-slate-800 mb-2">💰 Pricing Plans</h1>
          <p className="text-slate-500">Choose the plan that fits your journey</p>
          <div className="inline-flex bg-white rounded-lg shadow mt-6 p-1">
            <button onClick={() => setCycle('monthly')} className={`px-6 py-2 rounded-md font-medium ${cycle === 'monthly' ? 'bg-purple-600 text-white' : 'text-slate-600'}`}>Monthly</button>
            <button onClick={() => setCycle('yearly')} className={`px-6 py-2 rounded-md font-medium ${cycle === 'yearly' ? 'bg-purple-600 text-white' : 'text-slate-600'}`}>Yearly <span className="text-xs">(~17% off)</span></button>
          </div>
          {activePromo && (
            <div className="mt-4 inline-flex items-center gap-2 bg-gradient-to-r from-purple-100 to-pink-100 text-purple-800 px-4 py-2 rounded-full border border-purple-300">
              <span className="font-bold">🎉 {activePromo.title}</span>
              <span className="bg-yellow-300 px-2 py-0.5 rounded-full text-xs font-bold">{activePromo.discount_percent}% OFF</span>
            </div>
          )}
        </div>

        {success && <div className="max-w-xl mx-auto mb-4 p-3 bg-green-100 text-green-700 rounded-lg">{success}</div>}

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {plans.map((plan) => {
            const base = getPrice(plan);
            const final = getFinalPrice(plan);
            const hasDiscount = final < base;
            const isPopular = plan.name === 'Pro';
            const isFree = plan.price_monthly === 0 && plan.price_yearly === 0;
            return (
              <div key={plan.id} className={`relative bg-white rounded-2xl shadow-lg p-6 flex flex-col ${isPopular ? 'border-2 border-purple-500 ring-2 ring-purple-200' : 'border border-slate-200'}`}>
                {isPopular && <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-purple-600 text-white text-xs font-bold px-3 py-1 rounded-full">⭐ POPULAR</div>}
                <h3 className="text-xl font-bold text-slate-800">{plan.name}</h3>
                <p className="text-sm text-slate-500 mt-1 min-h-[40px]">{plan.description}</p>
                <div className="mt-4">
                  {hasDiscount && <div className="text-sm text-slate-400 line-through">₹{base}</div>}
                  <div className="flex items-baseline gap-1">
                    <span className={`text-4xl font-bold ${hasDiscount ? 'text-green-600' : 'text-slate-800'}`}>₹{final}</span>
                    <span className="text-sm text-slate-500">/{cycle === 'monthly' ? 'mo' : 'yr'}</span>
                  </div>
                  {hasDiscount && <div className="text-xs text-green-600 font-medium mt-1">Save ₹{base - final} ({activePromo.discount_percent}% off)</div>}
                </div>
                <ul className="mt-6 space-y-2 flex-1">
                  {(plan.features || []).map((f, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-slate-600"><span className="text-green-500 mt-0.5">✓</span><span>{f}</span></li>
                  ))}
                </ul>
                <button onClick={() => setSelectedPlan(plan)} className={`mt-6 w-full py-3 rounded-lg font-semibold ${isFree ? 'bg-slate-200 hover:bg-slate-300 text-slate-700' : isPopular ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white' : 'bg-purple-600 hover:bg-purple-700 text-white'}`}>
                  {isFree ? 'Get Started Free' : 'Subscribe Now'}
                </button>
              </div>
            );
          })}
        </div>
      </div>

      {selectedPlan && (
        <PaymentModal
          plan={selectedPlan}
          cycle={cycle}
          user={user}
          promo={activePromo}
          settings={settings}
          onClose={() => setSelectedPlan(null)}
          onSuccess={(msg) => { setSuccess(msg); setSelectedPlan(null); }}
        />
      )}
    </div>
  );
}

// ========== PAYMENT MODAL ==========
function PaymentModal({ plan, cycle, user, promo, settings, onClose, onSuccess }) {
  const [method, setMethod] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [utr, setUtr] = useState('');

  const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';
  const base = cycle === 'monthly' ? plan.price_monthly : plan.price_yearly;
  const final = (promo && plan.name !== 'Free') ? Math.round(base * (1 - promo.discount_percent / 100)) : base;
  const nprFinal = Math.round(final * 1.6);
  const usdFinal = (final / 83).toFixed(2);

  // Free plan — direct
  if (plan.price_monthly === 0 && plan.price_yearly === 0) {
    const handleFree = async () => {
      setLoading(true); setError('');
      try {
        const res = await fetch(`${API_BASE}/subscriptions/subscribe`, {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ user_id: user.id, plan_id: plan.id, billing_cycle: cycle }),
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail);
        onSuccess(`✅ Subscribed to ${data.plan} (Free)!`);
      } catch (e) { setError(e.message); }
      finally { setLoading(false); }
    };
    return (
      <ModalShell onClose={onClose} title="Free Plan">
        <p className="text-slate-600 mb-4">Activate Free plan? No payment needed.</p>
        {error && <p className="text-red-600 text-sm mb-3">{error}</p>}
        <button onClick={handleFree} disabled={loading} className="w-full bg-purple-600 text-white py-3 rounded-lg font-semibold">
          {loading ? 'Activating...' : 'Activate Free Plan'}
        </button>
      </ModalShell>
    );
  }

  // Razorpay — instant payment
  const handleRazorpay = async () => {
    if (!window.Razorpay) {
      setError('Razorpay loading... 2 sec wait karo phir retry');
      return;
    }
    setLoading(true); setError('');
    try {
      const res = await fetch(`${API_BASE}/payments/razorpay/create-order`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: user.id, plan_id: plan.id, billing_cycle: cycle }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail);

      const options = {
        key: data.key_id, amount: data.amount_paise, currency: data.currency,
        name: 'AI Glue', description: `${data.plan_name} — ${data.billing_cycle}`,
        order_id: data.order_id,
        prefill: { name: user.full_name || '', email: user.email || '', contact: user.phone || '' },
        theme: { color: '#9333ea' },
        handler: async (response) => {
          try {
            const vr = await fetch(`${API_BASE}/payments/razorpay/verify`, {
              method: 'POST', headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                user_id: user.id, plan_id: plan.id, billing_cycle: cycle,
                razorpay_order_id: response.razorpay_order_id,
                razorpay_payment_id: response.razorpay_payment_id,
                razorpay_signature: response.razorpay_signature,
              }),
            });
            const vd = await vr.json();
            if (!vr.ok) throw new Error(vd.detail);
            onSuccess(`✅ Subscribed to ${vd.plan}! Paid: ₹${vd.final_amount}`);
          } catch (e) { setError(e.message); }
          finally { setLoading(false); }
        },
        modal: { ondismiss: () => setLoading(false) },
      };
      new window.Razorpay(options).open();
    } catch (e) { setError(e.message); setLoading(false); }
  };

  // Manual submit (UPI / eSewa / PayPal)
  const handleManualSubmit = async () => {
    if (!utr.trim()) { setError('Transaction ID / UTR required'); return; }
    setLoading(true); setError('');
    try {
      const res = await fetch(`${API_BASE}/payments/manual/submit`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: user.id, user_email: user.email || '', plan_id: plan.id,
          billing_cycle: cycle, method, utr_number: utr.trim(),
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail);
      onSuccess(`✅ Payment submitted! Admin verify karega 24 ghante mein. Ref: ${data.payment_id.slice(0, 8)}`);
    } catch (e) { setError(e.message); }
    finally { setLoading(false); }
  };

  // ========== QR Strings (auto-generated) ==========
  // UPI deep links — standard UPI format, GPay/PhonePe/Paytm sab support karte hain
  const upiString = `upi://pay?pa=${settings.upi_id_1}&pn=AI%20Glue&am=${final}&cu=INR&tn=AI%20Glue%20${plan.name}`;
  const upiString2 = `upi://pay?pa=${settings.upi_id_2}&pn=AI%20Glue&am=${final}&cu=INR&tn=AI%20Glue%20${plan.name}`;
  // eSewa — personal wallet number
  const esewaString = `esewa://pay?pa=${settings.esewa_id}&pn=${encodeURIComponent(settings.esewa_name)}&am=${nprFinal}`;
  // PayPal.me link with USD amount
  const paypalUrl = `${settings.paypal_link}/${usdFinal}USD`;

  return (
    <ModalShell onClose={onClose} title={`Subscribe — ${plan.name}`}>
      <div className="bg-slate-50 rounded-lg p-3 mb-4">
        <div className="flex justify-between text-sm"><span>Plan:</span><b>{plan.name} ({cycle})</b></div>
        {promo && <div className="flex justify-between text-sm text-green-600"><span>Discount:</span><b>{promo.discount_percent}% off</b></div>}
        <div className="flex justify-between text-lg mt-1 pt-1 border-t"><span>Amount:</span><b>₹{final}</b></div>
      </div>

      {error && <p className="text-red-600 text-sm mb-3">{error}</p>}

      {/* Method Selection */}
      {!method && (
        <div className="space-y-2">
          <p className="text-sm text-slate-500 mb-2">Choose payment method:</p>
          <button onClick={handleRazorpay} disabled={loading} className="w-full flex items-center gap-3 p-3 border-2 border-slate-200 hover:border-purple-400 rounded-lg text-left">
            <span className="text-2xl">🔵</span>
            <div className="flex-1"><div className="font-semibold text-slate-800">Razorpay</div><div className="text-xs text-slate-500">Card / UPI / Netbanking — instant</div></div>
            <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">Instant</span>
          </button>
          <button onClick={() => setMethod('upi')} className="w-full flex items-center gap-3 p-3 border-2 border-slate-200 hover:border-purple-400 rounded-lg text-left">
            <span className="text-2xl">🟢</span>
            <div className="flex-1"><div className="font-semibold text-slate-800">UPI QR / GPay / PhonePe</div><div className="text-xs text-slate-500">Scan QR → Pay → Enter UTR</div></div>
          </button>
          <button onClick={() => setMethod('esewa')} className="w-full flex items-center gap-3 p-3 border-2 border-slate-200 hover:border-purple-400 rounded-lg text-left">
            <span className="text-2xl">🟣</span>
            <div className="flex-1"><div className="font-semibold text-slate-800">eSewa (Nepal)</div><div className="text-xs text-slate-500">Scan QR → Pay NPR {nprFinal}</div></div>
          </button>
          <button onClick={() => setMethod('paypal')} className="w-full flex items-center gap-3 p-3 border-2 border-slate-200 hover:border-purple-400 rounded-lg text-left">
            <span className="text-2xl">🟡</span>
            <div className="flex-1"><div className="font-semibold text-slate-800">PayPal (Global)</div><div className="text-xs text-slate-500">Pay ${usdFinal} USD</div></div>
          </button>
        </div>
      )}

      {/* ========== UPI QR ========== */}
      {method === 'upi' && (
        <div>
          <button onClick={() => setMethod(null)} className="text-sm text-slate-500 mb-3">← Back</button>
          <div className="text-center mb-3">
            <div className="text-sm text-slate-500">Scan & Pay</div>
            <div className="text-3xl font-bold text-purple-600">₹{final}</div>
          </div>

          {/* QR 1 — SBI */}
          <div className="bg-white border rounded-xl p-3 mb-3 text-center">
            <div className="text-xs font-medium text-slate-600 mb-2">Option 1 — State Bank of India</div>
            <QRCodeSVG value={upiString} size={180} className="mx-auto" />
            <div className="text-sm font-medium text-slate-700 mt-2">Promod Kumar</div>
            <div className="text-xs font-mono text-slate-500">{settings.upi_id_1}</div>
          </div>

          {/* QR 2 — IDFC */}
          <div className="bg-white border rounded-xl p-3 mb-3 text-center">
            <div className="text-xs font-medium text-slate-600 mb-2">Option 2 — IDFC First Bank</div>
            <QRCodeSVG value={upiString2} size={180} className="mx-auto" />
            <div className="text-sm font-medium text-slate-700 mt-2">Promod Kumar</div>
            <div className="text-xs font-mono text-slate-500">{settings.upi_id_2}</div>
          </div>

          <div className="border-t my-3"></div>
          <label className="text-xs text-slate-600 mb-1 block">UTR / Transaction ID *</label>
          <input type="text" value={utr} onChange={(e) => setUtr(e.target.value)} placeholder="e.g., 123456789012" className="w-full border rounded-lg px-3 py-2 mb-3 text-sm" />
          <button onClick={handleManualSubmit} disabled={loading} className="w-full bg-purple-600 text-white py-3 rounded-lg font-semibold">
            {loading ? 'Submitting...' : 'I have paid — Submit'}
          </button>
          <p className="text-xs text-slate-400 text-center mt-2">Admin verify karega 24 ghante mein</p>
        </div>
      )}

      {/* ========== eSewa QR ========== */}
      {method === 'esewa' && (
        <div>
          <button onClick={() => setMethod(null)} className="text-sm text-slate-500 mb-3">← Back</button>
          <div className="text-center mb-3">
            <div className="text-sm text-slate-500">Scan with eSewa App</div>
            <div className="text-3xl font-bold text-purple-600">NPR {nprFinal}</div>
          </div>

          <div className="bg-white border rounded-xl p-3 mb-3 text-center">
            <QRCodeSVG value={esewaString} size={200} className="mx-auto" />
            <div className="text-sm font-medium text-slate-700 mt-2">{settings.esewa_name}</div>
            <div className="text-xs font-mono text-slate-500">{settings.esewa_id}</div>
          </div>

          <div className="border-t my-3"></div>
          <label className="text-xs text-slate-600 mb-1 block">eSewa Transaction ID *</label>
          <input type="text" value={utr} onChange={(e) => setUtr(e.target.value)} placeholder="Transaction ID" className="w-full border rounded-lg px-3 py-2 mb-3 text-sm" />
          <button onClick={handleManualSubmit} disabled={loading} className="w-full bg-purple-600 text-white py-3 rounded-lg font-semibold">
            {loading ? 'Submitting...' : 'I have paid — Submit'}
          </button>
          <p className="text-xs text-slate-400 text-center mt-2">Admin verify karega 24 ghante mein</p>
        </div>
      )}

      {/* ========== PayPal ========== */}
      {method === 'paypal' && (
        <div>
          <button onClick={() => setMethod(null)} className="text-sm text-slate-500 mb-3">← Back</button>
          <div className="text-center mb-3">
            <div className="text-sm text-slate-500">Pay via PayPal</div>
            <div className="text-3xl font-bold text-blue-600">${usdFinal} USD</div>
            <div className="text-xs text-slate-400">(₹{final} ≈ ${usdFinal})</div>
          </div>

          <div className="bg-white border rounded-xl p-3 mb-3 text-center">
            <QRCodeSVG value={paypalUrl} size={200} className="mx-auto" />
            <div className="text-sm font-medium text-slate-700 mt-2">Promod Kumar</div>
            <div className="text-xs font-mono text-slate-500">@{settings.paypal_username}</div>
            <div className="text-xs text-slate-400 mt-1">paypal.me/{settings.paypal_username}</div>
          </div>

          <a href={paypalUrl} target="_blank" rel="noopener noreferrer" className="block text-center bg-blue-600 hover:bg-blue-700 text-white py-3 rounded-lg font-semibold mb-3">
            Open PayPal →
          </a>

          <div className="border-t my-3"></div>
          <label className="text-xs text-slate-600 mb-1 block">PayPal Transaction ID *</label>
          <input type="text" value={utr} onChange={(e) => setUtr(e.target.value)} placeholder="PayPal Transaction ID" className="w-full border rounded-lg px-3 py-2 mb-3 text-sm" />
          <button onClick={handleManualSubmit} disabled={loading} className="w-full bg-purple-600 text-white py-3 rounded-lg font-semibold">
            {loading ? 'Submitting...' : 'I have paid — Submit'}
          </button>
          <p className="text-xs text-slate-400 text-center mt-2">Admin verify karega 24 ghante mein</p>
        </div>
      )}
    </ModalShell>
  );
}

function ModalShell({ children, onClose, title }) {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center p-4 border-b sticky top-0 bg-white z-10">
          <h3 className="font-bold text-slate-800">{title}</h3>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 text-2xl leading-none">×</button>
        </div>
        <div className="p-5">{children}</div>
      </div>
    </div>
  );
}