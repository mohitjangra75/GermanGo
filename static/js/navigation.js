/**
 * Navigation: sticky state, mobile drawer, toasts and modals.
 */

import { $, $$, throttle } from './utils.js';

function initStickyNav() {
  const nav = $('[data-nav]');
  if (!nav) return;
  const onScroll = throttle(() => {
    nav.classList.toggle('is-stuck', window.scrollY > 8);
  }, 80);
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });
}

function initDrawer() {
  const toggle = $('[data-nav-toggle]');
  const drawer = $('[data-nav-drawer]');
  if (!toggle || !drawer) return;

  const close = () => {
    drawer.classList.remove('is-open');
    toggle.setAttribute('aria-expanded', 'false');
    document.body.style.overflow = '';
  };

  toggle.addEventListener('click', () => {
    const open = drawer.classList.toggle('is-open');
    toggle.setAttribute('aria-expanded', String(open));
    document.body.style.overflow = open ? 'hidden' : '';
  });

  drawer.addEventListener('click', (event) => {
    if (event.target.closest('a')) close();
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && drawer.classList.contains('is-open')) {
      close();
      toggle.focus();
    }
  });

  window.addEventListener('resize', throttle(() => {
    if (window.innerWidth > 999) close();
  }, 200));
}

function initToasts() {
  const container = $('[data-toasts]');
  if (!container) return;

  const dismiss = (toast) => {
    toast.style.transition = 'opacity .25s, transform .25s';
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(16px)';
    setTimeout(() => toast.remove(), 260);
  };

  container.addEventListener('click', (event) => {
    const close = event.target.closest('[data-toast-close]');
    if (close) dismiss(close.closest('.toast'));
  });

  $$('.toast', container).forEach((toast) => {
    setTimeout(() => { if (toast.isConnected) dismiss(toast); }, 6000);
  });
}

/** Details/summary FAQ items: only one open at a time. */
function initAccordions() {
  $$('[data-accordion]').forEach((group) => {
    const items = $$('details', group);
    items.forEach((item) => {
      item.addEventListener('toggle', () => {
        if (!item.open) return;
        items.forEach((other) => { if (other !== item) other.open = false; });
      });
    });
  });
}

export function initNavigation() {
  initStickyNav();
  initDrawer();
  initToasts();
  initAccordions();
}

export { initToasts };
