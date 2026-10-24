/**
 * GSAP animation system.
 *
 * Everything here is additive: if GSAP fails to load, or the learner has
 * asked for reduced motion, the page still renders correctly because
 * `[data-animate]` elements are only hidden while `.js` is on the html
 * element and reduced motion is off (see tokens.css).
 */

import { $$, prefersReducedMotion, onEnterViewport } from './utils.js';

let gsap = null;
let ScrollTrigger = null;

export function getGsap() {
  return gsap;
}

function revealAll() {
  $$('[data-animate]').forEach((el) => { el.style.opacity = '1'; });
}

/**
 * Entrance animation for anything marked `data-animate`.
 * `data-animate="up|fade|scale"` picks the flavour, `data-animate-delay`
 * staggers it, and `data-animate-scroll` defers it until scrolled into view.
 */
function buildEntrance(element) {
  const kind = element.dataset.animate || 'up';
  const from = { opacity: 0 };
  if (kind === 'up') from.y = 26;
  if (kind === 'down') from.y = -20;
  if (kind === 'left') from.x = -26;
  if (kind === 'right') from.x = 26;
  if (kind === 'scale') { from.scale = 0.95; from.y = 14; }
  return from;
}

function animateOnLoad() {
  const immediate = $$('[data-animate]:not([data-animate-scroll])');
  if (!immediate.length) return;

  immediate.forEach((element) => {
    gsap.fromTo(
      element,
      buildEntrance(element),
      {
        opacity: 1,
        x: 0,
        y: 0,
        scale: 1,
        duration: 0.72,
        ease: 'power3.out',
        delay: parseFloat(element.dataset.animateDelay || 0),
      }
    );
  });
}

function animateOnScroll() {
  if (!ScrollTrigger) return;
  $$('[data-animate-scroll]').forEach((element) => {
    gsap.fromTo(
      element,
      buildEntrance(element),
      {
        opacity: 1,
        x: 0,
        y: 0,
        scale: 1,
        duration: 0.8,
        ease: 'power3.out',
        delay: parseFloat(element.dataset.animateDelay || 0),
        scrollTrigger: {
          trigger: element,
          start: 'top 86%',
          once: true,
        },
      }
    );
  });
}

/** Stagger the children of any `[data-stagger]` container. */
function animateStaggers() {
  $$('[data-stagger]').forEach((container) => {
    const children = Array.from(container.children);
    if (!children.length) return;
    gsap.fromTo(
      children,
      { opacity: 0, y: 22 },
      {
        opacity: 1,
        y: 0,
        duration: 0.62,
        ease: 'power3.out',
        stagger: parseFloat(container.dataset.stagger) || 0.07,
        scrollTrigger: ScrollTrigger
          ? { trigger: container, start: 'top 88%', once: true }
          : undefined,
      }
    );
  });
}

/** The finished journey: rail fully drawn, every marker lit. */
function finishJourneys() {
  $$('[data-journey]').forEach((journey) => {
    journey.style.setProperty('--seg', '1');
    $$('[data-journey-step]', journey).forEach((step) => step.classList.add('is-lit'));
  });
}

/**
 * The "how it works" journey. For each step in turn: the marker pops and
 * ripples, its number pill snaps on, the icon draws itself, the title and
 * body slide in, then a spark carries the rail on to the next marker,
 * which lights as it arrives. `--seg` is the segment progress that the
 * stylesheet scales the fill by and positions the spark with.
 */
function animateJourneys() {
  const STEP = 0.78; // seconds between one marker lighting and the next
  const TRAVEL_AT = 0.22; // when, within a step, the spark sets off
  const TRAVEL = STEP - TRAVEL_AT;

  $$('[data-journey]').forEach((journey) => {
    const steps = $$('[data-journey-step]', journey);
    if (!steps.length) return;

    // Played by an IntersectionObserver rather than ScrollTrigger: content
    // above (the hero scene, lazy images) settles after ScrollTrigger has
    // measured, and a stale position would start this run off-screen.
    const timeline = gsap.timeline({ paused: true });
    onEnterViewport(journey, () => timeline.play(), { rootMargin: '0px 0px -18% 0px', threshold: 0.1 });

    steps.forEach((step, index) => {
      const at = index * STEP;
      const marker = step.querySelector('.journey__marker');
      const num = step.querySelector('.journey__num');
      const title = step.querySelector('.journey__title');
      const body = step.querySelector('.journey__body');
      const spark = step.querySelector('.journey__spark');
      // Every stroke in the icon, each with its own length, so the drawing
      // finishes together whatever the shape.
      const strokes = Array.from(marker.querySelectorAll('path, circle, rect, line, polyline'));

      timeline
        .add(() => step.classList.add('is-lit'), at)
        .fromTo(marker, { scale: 0.5, opacity: 0 },
          { scale: 1, opacity: 1, duration: 0.55, ease: 'back.out(2)' }, at)
        .fromTo(num, { scale: 0, rotate: -12 },
          { scale: 1, rotate: 0, duration: 0.45, ease: 'back.out(2.5)' }, at + 0.12)
        .fromTo(title, { x: -14, opacity: 0 },
          { x: 0, opacity: 1, duration: 0.45, ease: 'power3.out' }, at + 0.14)
        .fromTo(body, { y: 12, opacity: 0 },
          { y: 0, opacity: 1, duration: 0.5, ease: 'power3.out' }, at + 0.26);

      strokes.forEach((stroke) => {
        const length = stroke.getTotalLength?.() || 0;
        if (!length) return;
        timeline.fromTo(stroke, { strokeDasharray: length, strokeDashoffset: length },
          { strokeDashoffset: 0, duration: 0.55, ease: 'power2.inOut' }, at + 0.1);
      });

      // The spark sets off once the marker has settled and lands exactly as
      // the next one lights.
      if (index < steps.length - 1 && spark) {
        timeline
          .fromTo(step, { '--seg': 0 },
            { '--seg': 1, duration: TRAVEL, ease: 'power1.inOut' }, at + TRAVEL_AT)
          .fromTo(spark, { opacity: 0 }, { opacity: 1, duration: 0.12 }, at + TRAVEL_AT)
          .to(spark, { opacity: 0, duration: 0.14 }, at + STEP - 0.1);
      }
    });
  });
}

/** Count a number up when its card scrolls into view. */
function animateCounters(root = document) {
  $$('[data-count-to]', root).forEach((element) => {
    const target = parseFloat(element.dataset.countTo);
    if (Number.isNaN(target)) return;
    const suffix = element.dataset.countSuffix || '';
    const counter = { value: 0 };
    gsap.to(counter, {
      value: target,
      duration: 1.5,
      ease: 'power2.out',
      onUpdate: () => {
        element.textContent = Math.round(counter.value).toLocaleString() + suffix;
      },
      scrollTrigger: ScrollTrigger
        ? { trigger: element, start: 'top 92%', once: true }
        : undefined,
    });
  });
}

/** Grow progress bars from zero as they enter the viewport. */
export function animateProgressBars(root = document) {
  const bars = $$('.progress__fill', root);
  if (!bars.length) return;

  if (!gsap || prefersReducedMotion()) {
    bars.forEach((bar) => { bar.style.width = bar.dataset.percent + '%'; });
    return;
  }

  bars.forEach((bar) => {
    const percent = parseFloat(bar.dataset.percent || 0);
    gsap.fromTo(
      bar,
      { width: '0%' },
      {
        width: `${percent}%`,
        duration: 1.1,
        ease: 'power2.out',
        scrollTrigger: ScrollTrigger
          ? { trigger: bar, start: 'top 95%', once: true }
          : undefined,
      }
    );
  });
}

/** Sweep an SVG ring to its value. */
export function animateRings(root = document) {
  $$('.ring__value', root).forEach((ring) => {
    const target = ring.getAttribute('stroke-dashoffset');
    const circumference = ring.getAttribute('stroke-dasharray');
    if (!gsap || prefersReducedMotion()) return;
    gsap.fromTo(
      ring,
      { strokeDashoffset: circumference },
      {
        strokeDashoffset: target,
        duration: 1.3,
        ease: 'power2.out',
        scrollTrigger: ScrollTrigger
          ? { trigger: ring, start: 'top 95%', once: true }
          : undefined,
      }
    );
  });
}

/** A short celebratory pop, used on correct answers and unlocks. */
export function celebrate(element) {
  if (!gsap || prefersReducedMotion() || !element) return;
  gsap.fromTo(
    element,
    { scale: 0.92, opacity: 0 },
    { scale: 1, opacity: 1, duration: 0.5, ease: 'back.out(1.7)' }
  );
}

/** Expand a learning-path node's lesson list. */
export function expandNode(panel, open) {
  if (!panel) return;
  if (!gsap || prefersReducedMotion()) {
    panel.style.height = open ? 'auto' : '0px';
    panel.style.opacity = open ? '1' : '0';
    return;
  }
  if (open) {
    gsap.set(panel, { height: 'auto', opacity: 1 });
    gsap.from(panel, { height: 0, opacity: 0, duration: 0.42, ease: 'power3.out' });
  } else {
    gsap.to(panel, { height: 0, opacity: 0, duration: 0.3, ease: 'power2.in' });
  }
}

/** Page-entrance transition for the main content column. */
function pageEntrance() {
  const main = document.getElementById('main');
  if (!main) return;
  gsap.fromTo(
    main,
    { opacity: 0, y: 10 },
    { opacity: 1, y: 0, duration: 0.5, ease: 'power2.out' }
  );
}

/** Parallax the hero art very slightly as the page scrolls. */
function heroParallax() {
  const scene = document.querySelector('[data-hero-parallax]');
  if (!scene || !ScrollTrigger) return;
  gsap.to(scene, {
    yPercent: 7,
    ease: 'none',
    scrollTrigger: { trigger: scene, start: 'top top', end: 'bottom top', scrub: 0.6 },
  });
}

export function initAnimations() {
  if (prefersReducedMotion()) {
    revealAll();
    finishJourneys();
    animateProgressBars();
    return;
  }

  gsap = window.gsap || null;
  if (!gsap) {
    // GSAP did not load; make sure nothing stays invisible.
    revealAll();
    finishJourneys();
    return;
  }

  ScrollTrigger = window.ScrollTrigger || null;
  if (ScrollTrigger) gsap.registerPlugin(ScrollTrigger);

  pageEntrance();
  animateOnLoad();
  animateOnScroll();
  animateStaggers();
  animateJourneys();
  animateCounters();
  animateProgressBars();
  animateRings();
  heroParallax();
}

/** Re-run the cheap animations after an HTMX swap. */
export function refreshAnimations(root) {
  if (!gsap || prefersReducedMotion()) {
    animateProgressBars(root);
    return;
  }
  animateProgressBars(root);
  animateRings(root);
  animateCounters(root);
  if (ScrollTrigger) ScrollTrigger.refresh();
}
