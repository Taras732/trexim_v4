/**
 * Trexim Analytics - Client-side tracking (requires consent)
 */
const TreximAnalytics = {
    sessionId: null,
    scrollDepths: new Set(),
    heartbeatInterval: null,
    startTime: Date.now(),

    /**
     * Initialize tracking (only if consent given)
     */
    init() {
        if (!this.hasConsent()) {
            return;
        }

        this.startSession();
        this.trackScrollDepth();
        this.trackCTAClicks();
        this.trackOutboundLinks();
        this.startHeartbeat();
        this.trackPageLeave();
    },

    /**
     * Check if user gave consent
     */
    hasConsent() {
        return localStorage.getItem('analytics_consent') === 'accepted';
    },

    /**
     * Start a new session
     */
    async startSession() {
        try {
            const response = await fetch('/api/analytics/session', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({})
            });
            const data = await response.json();
            if (data.session_id) {
                this.sessionId = data.session_id;
                sessionStorage.setItem('trexim_session', this.sessionId);
            }
        } catch (e) {
            console.log('Analytics session error:', e);
        }
    },

    /**
     * Send an event to the server
     */
    async trackEvent(type, data = {}) {
        if (!this.hasConsent()) return;

        try {
            await fetch('/api/analytics/event', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    type: type,
                    data: data,
                    path: window.location.pathname,
                    session_id: this.sessionId || sessionStorage.getItem('trexim_session')
                })
            });
        } catch (e) {
            console.log('Analytics event error:', e);
        }
    },

    /**
     * Track scroll depth (25%, 50%, 75%, 100%)
     */
    trackScrollDepth() {
        const checkScroll = () => {
            const scrollTop = window.scrollY;
            const docHeight = document.documentElement.scrollHeight - window.innerHeight;
            const scrollPercent = Math.round((scrollTop / docHeight) * 100);

            const milestones = [25, 50, 75, 100];
            for (const milestone of milestones) {
                if (scrollPercent >= milestone && !this.scrollDepths.has(milestone)) {
                    this.scrollDepths.add(milestone);
                    this.trackEvent('scroll_depth', { depth: milestone });
                }
            }
        };

        let ticking = false;
        window.addEventListener('scroll', () => {
            if (!ticking) {
                window.requestAnimationFrame(() => {
                    checkScroll();
                    ticking = false;
                });
                ticking = true;
            }
        });
    },

    /**
     * Track CTA button clicks
     */
    trackCTAClicks() {
        document.addEventListener('click', (e) => {
            const target = e.target.closest('[data-track], .cta-button, a[href*="contact"], button[type="submit"]');
            if (!target) return;

            const trackData = target.dataset.track || target.innerText.trim().substring(0, 50);
            const trackCategory = target.dataset.trackCategory || 'cta';

            this.trackEvent('cta_click', {
                text: trackData,
                category: trackCategory,
                href: target.href || null
            });
        });
    },

    /**
     * Track outbound link clicks
     */
    trackOutboundLinks() {
        document.addEventListener('click', (e) => {
            const link = e.target.closest('a[href^="http"]');
            if (!link) return;

            const href = link.href;
            if (href.includes(window.location.hostname)) return;

            this.trackEvent('outbound_click', {
                url: href,
                text: link.innerText.trim().substring(0, 50)
            });
        });
    },

    /**
     * Send heartbeat every 30 seconds to track time on page
     */
    startHeartbeat() {
        this.heartbeatInterval = setInterval(() => {
            const timeOnPage = Math.round((Date.now() - this.startTime) / 1000);
            this.trackEvent('heartbeat', { seconds: timeOnPage });
        }, 30000);
    },

    /**
     * Track when user leaves the page
     */
    trackPageLeave() {
        window.addEventListener('beforeunload', () => {
            const timeOnPage = Math.round((Date.now() - this.startTime) / 1000);

            // Use sendBeacon for reliable delivery
            if (navigator.sendBeacon) {
                navigator.sendBeacon('/api/analytics/event', JSON.stringify({
                    type: 'page_leave',
                    data: {
                        seconds: timeOnPage,
                        scroll_depths: Array.from(this.scrollDepths)
                    },
                    path: window.location.pathname,
                    session_id: this.sessionId || sessionStorage.getItem('trexim_session')
                }));
            }
        });
    },

    /**
     * Track form submissions
     */
    trackForm(formType, formData = {}) {
        this.trackEvent('form_submit', {
            form_type: formType,
            ...formData
        });
    }
};

// Auto-initialize if consent already given
document.addEventListener('DOMContentLoaded', () => {
    if (localStorage.getItem('analytics_consent') === 'accepted') {
        TreximAnalytics.init();
    }
});
