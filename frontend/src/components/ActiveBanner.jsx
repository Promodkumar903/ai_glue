import React, { useState, useEffect } from 'react';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function ActiveBanner() {
  const [promotions, setPromotions] = useState([]);
  const [index, setIndex] = useState(0);

  useEffect(() => {
    fetch(`${API_BASE}/promotions/active`)
      .then((r) => r.json())
      .then((d) => setPromotions(d.promotions || []))
      .catch(() => setPromotions([]));
  }, []);

  // Auto-rotate every 5 seconds
  useEffect(() => {
    if (promotions.length <= 1) return;
    const interval = setInterval(() => {
      setIndex((i) => (i + 1) % promotions.length);
    }, 5000);
    return () => clearInterval(interval);
  }, [promotions]);

  if (promotions.length === 0) return null;

  const promo = promotions[index];

  return (
    <div className="bg-gradient-to-r from-purple-600 via-pink-500 to-red-500 text-white rounded-xl shadow-lg p-4 mb-4 relative overflow-hidden">
      {/* Decorative circle */}
      <div className="absolute -top-8 -right-8 w-32 h-32 bg-white bg-opacity-10 rounded-full" />
      <div className="absolute -bottom-8 -left-8 w-24 h-24 bg-white bg-opacity-10 rounded-full" />

      <div className="relative flex items-center gap-4 flex-wrap">
        {promo.image_data && (
          <img
            src={promo.image_data}
            alt={promo.title}
            className="w-20 h-20 object-cover rounded-lg border-2 border-white border-opacity-30"
          />
        )}

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs bg-white bg-opacity-20 px-2 py-0.5 rounded-full font-semibold uppercase">
              {promo.type}
            </span>
            {promo.type === 'promotion' && promo.discount_percent > 0 && (
              <span className="text-xs bg-yellow-400 text-gray-900 px-2 py-0.5 rounded-full font-bold">
                {promo.discount_percent}% OFF
              </span>
            )}
          </div>
          <h3 className="font-bold text-lg truncate">🎉 {promo.title}</h3>
          {promo.message && (
            <p className="text-sm text-white text-opacity-90 truncate">{promo.message}</p>
          )}
          {promo.end_date && (
            <p className="text-xs text-white text-opacity-75 mt-1">
              Valid till {promo.end_date}
            </p>
          )}
        </div>

        {/* Pagination dots */}
        {promotions.length > 1 && (
          <div className="flex flex-col gap-1">
            {promotions.map((_, i) => (
              <button
                key={i}
                onClick={() => setIndex(i)}
                className={`h-2 rounded-full transition-all ${
                  i === index ? 'bg-white w-6' : 'bg-white bg-opacity-40 w-2'
                }`}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}