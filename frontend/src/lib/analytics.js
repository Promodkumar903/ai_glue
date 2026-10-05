const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const trackEvent = async (eventType, metadata = {}) => {
  try {
    const userStr = localStorage.getItem('user');
    const user = userStr ? JSON.parse(userStr) : null;

    await fetch(`${API_BASE}/analytics/track`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        event_type: eventType,
        page: window.location.pathname,
        user_id: user?.id || '',
        metadata: metadata,
      }),
    });
  } catch (e) {
    // Silent fail — analytics shouldn't break the app
  }
};

// Auto-track page views
export const trackPageView = () => {
  trackEvent('page_view');
};

// Auto-track button clicks
export const trackClick = (buttonName, extra = {}) => {
  trackEvent('click', { button: buttonName, ...extra });
};

// Auto-track downloads
export const trackDownload = (fileName, fileType = 'unknown') => {
  trackEvent('download', { file: fileName, type: fileType });
};