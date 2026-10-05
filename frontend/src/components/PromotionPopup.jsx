import React, { useState, useEffect } from 'react';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function PromotionPopup() {
  const [promotions, setPromotions] = useState([]);
  const [ads, setAds] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    // Check if user already dismissed today
    const dismissed = localStorage.getItem('promo_dismissed');
    const today = new Date().toISOString().slice(0, 10);
    if (dismissed === today) return;

    // Fetch active promotions + popup ads
    Promise.all([
      fetch(`${API_BASE}/promotions/active`).then((r) => r.json()).catch(() => ({ promotions: [] })),
      fetch(`${API_BASE}/ads/active?placement=popup`).then((r) => r.json()).catch(() => ({ ads: [] })),
    ]).then(([p, a]) => {
      const allPromos = p.promotions || [];
      const allAds = (a.ads || []).map((ad) => ({
        id: ad.id,
        title: ad.title,
        type: 'ad',
        message: '',
        image_data: ad.banner_data,
        target_url: ad.target_url,
      }));
      const combined = [...allPromos, ...allAds];
      if (combined.length > 0) {
        setPromotions(combined);
        setTimeout(() => setVisible(true), 1500); // 1.5s delay
      }
    });
  }, []);

  const handleClose = () => {
    setVisible(false);
    const today = new Date().toISOString().slice(0, 10);
    localStorage.setItem('promo_dismissed', today);
  };

  const handleNext = () => {
    if (currentIndex < promotions.length - 1) {
      setCurrentIndex(currentIndex + 1);
    } else {
      handleClose();
    }
  };

  if (!visible || promotions.length === 0) return null;

  const promo = promotions[currentIndex];
  const isAd = promo.type === 'ad';

  const handleAction = () => {
    if (promo.target_url) {
      window.open(promo.target_url, '_blank');
    }
    handleNext();
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full overflow-hidden animate-[fadeIn_0.3s_ease]">
        {/* Header strip */}
        <div className={`px-4 py-2 text-white text-sm font-semibold flex justify-between items-center ${
          isAd ? 'bg-blue-600' : 'bg-gradient-to-r from-purple-600 to-pink-600'
        }`}>
          <span>
            {isAd ? '📢 Sponsored' : promo.type === 'promotion' ? '🎁 Special Offer' : promo.type === 'free' ? '🎉 Free Offer' : '💰 Paid Offer'}
          </span>
          <button onClick={handleClose} className="text-white hover:bg-white hover:bg-opacity-20 rounded px-2">
            ✕
          </button>
        </div>

        {/* Image */}
        {promo.image_data && (
          <img
            src={promo.image_data}
            alt={promo.title}
            className="w-full h-48 object-cover"
          />
        )}

        {/* Content */}
        <div className="p-5">
          <h3 className="font-bold text-lg mb-2">{promo.title}</h3>

          {!isAd && promo.type === 'promotion' && (
            <div className="flex items-center gap-3 mb-3">
              <span className="bg-red-100 text-red-700 font-bold text-2xl px-3 py-1 rounded-lg">
                {promo.discount_percent}%
              </span>
              <span className="text-sm text-gray-500">OFF</span>
            </div>
          )}

          {promo.message && (
            <p className="text-sm text-gray-700 mb-3">{promo.message}</p>
          )}

          {!isAd && promo.end_date && (
            <p className="text-xs text-gray-500 mb-3">
              ⏰ Valid till: <strong>{promo.end_date}</strong>
            </p>
          )}

          {/* Actions */}
          <div className="flex gap-2">
            {promo.target_url ? (
              <button
                onClick={handleAction}
                className="flex-1 bg-gradient-to-r from-purple-600 to-pink-600 text-white py-2.5 rounded-lg font-semibold hover:opacity-90"
              >
                {isAd ? 'Learn More' : 'Claim Now'}
              </button>
            ) : (
              <button
                onClick={handleNext}
                className="flex-1 bg-gradient-to-r from-purple-600 to-pink-600 text-white py-2.5 rounded-lg font-semibold hover:opacity-90"
              >
                {currentIndex < promotions.length - 1 ? 'Next →' : 'Got it!'}
              </button>
            )}
          </div>

          {/* Pagination dots */}
          {promotions.length > 1 && (
            <div className="flex justify-center gap-1.5 mt-3">
              {promotions.map((_, i) => (
                <span
                  key={i}
                  className={`h-1.5 rounded-full transition-all ${
                    i === currentIndex ? 'bg-purple-600 w-4' : 'bg-gray-300 w-1.5'
                  }`}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}