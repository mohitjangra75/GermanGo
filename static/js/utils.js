/**
 * Small shared helpers. No DOM side effects on import.
 */

export const $ = (selector, root = document) => root.querySelector(selector);
export const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));

/** True when the learner or their OS has asked for less motion. */
export function prefersReducedMotion() {
  if (document.documentElement.dataset.reducedMotion === 'true') return true;
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}

/** True on small screens or coarse pointers — used to scale 3D scenes down. */
export function isCompactDevice() {
  return window.matchMedia('(max-width: 900px), (pointer: coarse)').matches;
}

/** Devices that should not attempt WebGL at all. */
export function supportsWebGL() {
  try {
    const canvas = document.createElement('canvas');
    return Boolean(
      window.WebGLRenderingContext &&
      (canvas.getContext('webgl2') || canvas.getContext('webgl'))
    );
  } catch {
    return false;
  }
}

export function debounce(fn, wait = 200) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), wait);
  };
}

export function throttle(fn, wait = 100) {
  let last = 0;
  let queued;
  return (...args) => {
    const now = Date.now();
    if (now - last >= wait) {
      last = now;
      fn(...args);
    } else {
      clearTimeout(queued);
      queued = setTimeout(() => {
        last = Date.now();
        fn(...args);
      }, wait - (now - last));
    }
  };
}

/** Django's CSRF cookie, needed for fetch() POSTs (HTMX reads it itself). */
export function csrfToken() {
  const match = document.cookie.match(/(^|;\s*)csrftoken=([^;]+)/);
  if (match) return decodeURIComponent(match[2]);
  const input = document.querySelector('input[name="csrfmiddlewaretoken"]');
  return input ? input.value : '';
}

export function formatClock(totalSeconds) {
  const seconds = Math.max(0, Math.floor(totalSeconds));
  const mm = String(Math.floor(seconds / 60)).padStart(2, '0');
  const ss = String(seconds % 60).padStart(2, '0');
  return `${mm}:${ss}`;
}

/**
 * Runs `callback` once the element first scrolls into view.
 * Falls back to running immediately where IntersectionObserver is missing.
 */
export function onEnterViewport(element, callback, options = {}) {
  if (!('IntersectionObserver' in window)) {
    callback(element);
    return () => {};
  }
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        observer.unobserve(entry.target);
        callback(entry.target);
      }
    });
  }, { rootMargin: '0px 0px -10% 0px', threshold: 0.15, ...options });
  observer.observe(element);
  return () => observer.disconnect();
}

/** Announce a message to screen readers without moving focus. */
export function announce(message) {
  let region = document.getElementById('sr-announcer');
  if (!region) {
    region = document.createElement('div');
    region.id = 'sr-announcer';
    region.className = 'visually-hidden';
    region.setAttribute('role', 'status');
    region.setAttribute('aria-live', 'polite');
    document.body.appendChild(region);
  }
  region.textContent = '';
  window.setTimeout(() => { region.textContent = message; }, 60);
}

/** Position a floating card near an anchor, kept inside `bounds`. */
export function placeCard(card, anchorRect, bounds) {
  const gap = 10;
  const cardRect = card.getBoundingClientRect();
  let left = anchorRect.left - bounds.left + anchorRect.width / 2 - cardRect.width / 2;
  let top = anchorRect.bottom - bounds.top + gap;

  left = Math.max(gap, Math.min(left, bounds.width - cardRect.width - gap));
  if (top + cardRect.height > bounds.height - gap) {
    top = anchorRect.top - bounds.top - cardRect.height - gap;
  }
  top = Math.max(gap, top);

  card.style.left = `${left}px`;
  card.style.top = `${top}px`;
}
