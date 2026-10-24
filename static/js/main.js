/**
 * Application entry point.
 *
 *   1. Boot navigation and the GSAP animation system.
 *   2. Wire HTMX for the enquiry form and the filter toolbars.
 *   3. Lazily load Three.js for the homepage hero, and only there.
 *
 * Everything here is progressive: with JavaScript off the site still
 * renders, the filters still submit, and the enquiry form still posts.
 */

import { $, $$, supportsWebGL, prefersReducedMotion, onEnterViewport } from './utils.js';
import { initNavigation } from './navigation.js';
import { initAnimations, refreshAnimations } from './animations.js';
import { initForms } from './forms.js';

let heroScene = null;
const mapScenes = [];

/* -------------------------------------------------------------------------
   Three.js — homepage only, deferred, and skipped whenever it would cost
   more than it adds.
   ------------------------------------------------------------------------- */

function threeAllowed() {
  if (prefersReducedMotion()) return false;
  if (!supportsWebGL()) return false;
  if (navigator.connection?.saveData) return false;
  return true;
}

function showSceneFallback(container) {
  container
    .querySelectorAll('[data-scene-loader], [data-map-loader]')
    .forEach((loader) => loader.classList.add('is-hidden'));
  // Chrome that refers to the 3D scene makes no sense without it.
  container
    .querySelectorAll('[data-map-legend], .scene-hint')
    .forEach((element) => { element.hidden = true; });
  container
    .querySelectorAll('[data-scene-fallback], [data-map-fallback]')
    .forEach((fallback) => { fallback.hidden = false; });
}

function initHero() {
  const container = $('[data-hero-scene]');
  if (!container) return;

  if (!threeAllowed()) {
    showSceneFallback(container);
    return;
  }

  onEnterViewport(container, async () => {
    try {
      const { initHeroScene } = await import('./three-hero.js');
      heroScene = initHeroScene(container);
      if (!heroScene) showSceneFallback(container);
    } catch (error) {
      console.warn('GermanGo: hero scene unavailable', error);
      showSceneFallback(container);
    }
  }, { rootMargin: '200px' });
}

/**
 * The 3D map, used by the quiz page and the homepage teaser. The quiz logic
 * is loaded first and separately, so the game is playable via the city
 * buttons even where WebGL is unavailable.
 */
function initMaps() {
  const quizRoot = $('[data-map-quiz]');
  if (quizRoot) {
    import('./map-quiz.js')
      .then((module) => module.initMapQuiz())
      .catch((error) => console.warn('GermanGo: quiz unavailable', error));
  }

  $$('[data-germany-map]').forEach((container) => {
    if (!threeAllowed()) {
      showSceneFallback(container);
      return;
    }
    onEnterViewport(container, async () => {
      try {
        const { initGermanyMap } = await import('./germany-map.js');
        const map = initGermanyMap(container);
        if (!map) {
          showSceneFallback(container);
          return;
        }
        mapScenes.push(map);
        // The quiz talks to the map through this handle.
        if (container.dataset.mode === 'quiz') window.GermanGoMap = map;
      } catch (error) {
        console.warn('GermanGo: map unavailable', error);
        showSceneFallback(container);
      }
    }, { rootMargin: '200px' });
  });
}

/* -------------------------------------------------------------------------
   HTMX
   ------------------------------------------------------------------------- */

function configureHtmx() {
  if (!window.htmx) return;

  window.htmx.config.defaultSwapStyle = 'innerHTML';
  window.htmx.config.includeIndicatorStyles = false;
  // 422 and 429 carry a re-rendered form, so HTMX must swap them in.
  window.htmx.config.responseHandling = [
    { code: '204', swap: false },
    { code: '[23]..', swap: true },
    { code: '422', swap: true, error: false },
    { code: '429', swap: true, error: false },
    { code: '[45]..', swap: false, error: true },
  ];

  document.body.addEventListener('htmx:afterSwap', (event) => {
    const target = event.detail.target || document;
    initForms(target);
    refreshAnimations(target);

    // Bring a successful enquiry into view so the confirmation is not missed.
    const success = target.querySelector?.('[data-enquiry-success]');
    if (success) {
      success.scrollIntoView({
        behavior: prefersReducedMotion() ? 'auto' : 'smooth',
        block: 'center',
      });
    }
  });

  document.body.addEventListener('htmx:responseError', () => {
    showToast('Something went wrong. Please try again, or call us.', 'error');
  });

  document.body.addEventListener('htmx:sendError', () => {
    showToast('You appear to be offline. Please check your connection.', 'warning');
  });
}

/** A toast, for failures HTMX cannot render inline. */
export function showToast(message, kind = 'info') {
  let container = $('[data-toasts]');
  if (!container) {
    container = document.createElement('div');
    container.className = 'toasts';
    container.setAttribute('data-toasts', '');
    container.setAttribute('role', 'status');
    container.setAttribute('aria-live', 'polite');
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast toast--${kind}`;
  toast.innerHTML = `<div></div>
    <button type="button" class="toast__close" data-toast-close aria-label="Dismiss">&times;</button>`;
  toast.firstElementChild.textContent = message;
  container.appendChild(toast);

  toast.querySelector('[data-toast-close]').addEventListener('click', () => toast.remove());
  window.setTimeout(() => toast.remove(), 6000);
}

/* -------------------------------------------------------------------------
   Boot
   ------------------------------------------------------------------------- */

/**
 * Takes the curtain out of the DOM once it has played.
 *
 * The CSS already hides it with `animation-fill-mode`, which is what covers
 * the no-JavaScript case. This is the belt to that pair of braces: a fixed,
 * full-viewport overlay is the last thing that should be left to a timing
 * assumption, so when JS is available we simply delete the element.
 */
function retireCurtain() {
  const curtain = $('[data-curtain-el]');
  if (!curtain) return;

  let done = false;
  const remove = () => {
    if (done) return;
    done = true;
    curtain.remove();
  };

  // Whichever lands first: the last panel finishing, or a hard backstop.
  const panels = Array.from(curtain.querySelectorAll('.curtain__panel'));
  let finished = 0;
  panels.forEach((panel) =>
    panel.addEventListener('animationend', () => {
      finished += 1;
      if (finished >= panels.length) remove();
    }, { once: true })
  );
  window.setTimeout(remove, 1900);
}

function boot() {
  // The `js` class and reduced-motion flag are set by an inline script in the
  // head so the stylesheet sees them on the first paint; repeated here for
  // anything that stripped that script.
  const root = document.documentElement;
  root.classList.add('js');
  root.classList.remove('no-js');
  if (prefersReducedMotion()) root.dataset.reducedMotion = 'true';

  initNavigation();
  initAnimations();
  initForms();
  configureHtmx();
  initHero();
  initMaps();
  retireCurtain();

  window.addEventListener('pagehide', () => {
    heroScene?.stop?.();
    mapScenes.forEach((map) => map?.stop?.());
  });
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', boot, { once: true });
} else {
  boot();
}

window.GermanGo = { showToast };
