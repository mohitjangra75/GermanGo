/**
 * The Germany map quiz.
 *
 * Django renders the city list; this runs the round. The score is posted at
 * the end so the school can see engagement, but the game itself stays on the
 * client — a wrong guess should feel instant, not like a form submission.
 */

import { $, $$, csrfToken, formatClock, announce, prefersReducedMotion } from './utils.js';

const REVEAL_MS = 1500;

class MapQuiz {
  constructor(root) {
    this.root = root;
    this.stage = $('[data-germany-map]', root);
    this.resultUrl = root.dataset.resultUrl || '';
    this.roundLength = parseInt(root.dataset.roundLength || '8', 10);

    this.promptEl = $('[data-quiz-prompt]', root);
    this.hintEl = $('[data-quiz-hint]', root);
    this.hintBtn = $('[data-quiz-hint-btn]', root);
    this.feedbackEl = $('[data-quiz-feedback]', root);
    this.scoreEl = $('[data-quiz-score]', root);
    this.countEl = $('[data-quiz-count]', root);
    this.timerEl = $('[data-quiz-timer]', root);
    this.progressEl = $('[data-quiz-progress]', root);
    this.startPanel = $('[data-quiz-start]', root);
    this.playPanel = $('[data-quiz-play]', root);
    this.resultPanel = $('[data-quiz-result]', root);

    try {
      this.allCities = JSON.parse(this.stage?.dataset.cities || '[]');
    } catch {
      this.allCities = [];
    }

    if (!this.allCities.length) return;
    this.bind();
  }

  bind() {
    this.root.addEventListener('click', (event) => {
      const action = event.target.closest('[data-quiz-action]');
      if (!action) return;
      const name = action.dataset.quizAction;
      if (name === 'start') this.start();
      if (name === 'hint') this.showHint();
      if (name === 'skip') this.answer(null);
      if (name === 'again') this.start();
    });

    // A guess can come from the 3D marker or the accessible city buttons.
    this.stage?.addEventListener('map:guess', (event) => this.answer(event.detail.slug));
    this.root.addEventListener('click', (event) => {
      const button = event.target.closest('[data-quiz-pick]');
      if (button && this.playing) this.answer(button.dataset.quizPick);
    });
  }

  /** Shuffle a copy, easiest cities first so the opening question is winnable. */
  buildRound() {
    const pool = [...this.allCities];
    for (let i = pool.length - 1; i > 0; i -= 1) {
      const j = Math.floor(Math.random() * (i + 1));
      [pool[i], pool[j]] = [pool[j], pool[i]];
    }
    pool.sort((a, b) => (a.difficulty || 1) - (b.difficulty || 1));
    return pool.slice(0, Math.min(this.roundLength, pool.length));
  }

  start() {
    this.round = this.buildRound();
    this.index = 0;
    this.score = 0;
    this.hints = 0;
    this.startedAt = Date.now();
    this.playing = true;

    if (this.startPanel) this.startPanel.hidden = true;
    if (this.resultPanel) { this.resultPanel.hidden = true; this.resultPanel.innerHTML = ''; }
    if (this.playPanel) this.playPanel.hidden = false;

    this.tick = setInterval(() => this.updateClock(), 1000);
    this.ask();
  }

  get current() {
    return this.round[this.index];
  }

  ask() {
    const city = this.current;
    if (!city) return;

    window.GermanGoMap?.resetRound?.();

    if (this.promptEl) this.promptEl.textContent = `Wo ist ${city.name}?`;
    if (this.hintEl) { this.hintEl.textContent = ''; this.hintEl.hidden = true; }
    if (this.hintBtn) this.hintBtn.hidden = !city.hint;
    if (this.feedbackEl) { this.feedbackEl.textContent = ''; this.feedbackEl.className = 'quiz__feedback'; }

    this.updateHud();
    announce(`Question ${this.index + 1} of ${this.round.length}. Where is ${city.name}?`);
  }

  showHint() {
    const city = this.current;
    if (!city?.hint || !this.hintEl || !this.hintEl.hidden) return;
    this.hints += 1;
    this.hintEl.textContent = city.hint;
    this.hintEl.hidden = false;
    if (this.hintBtn) this.hintBtn.hidden = true;
  }

  answer(slug) {
    if (!this.playing || this.locked) return;
    this.locked = true;

    const city = this.current;
    const correct = slug === city.slug;
    if (correct) this.score += 1;

    window.GermanGoMap?.reveal?.({ guessed: slug, correct: city.slug });

    if (this.feedbackEl) {
      this.feedbackEl.className = `quiz__feedback ${correct ? 'is-correct' : 'is-wrong'}`;
      if (correct) {
        this.feedbackEl.textContent = city.fact
          ? `Richtig! ${city.fact}`
          : `Richtig! ${city.name} it is.`;
      } else if (slug) {
        const picked = this.allCities.find((item) => item.slug === slug);
        this.feedbackEl.textContent =
          `That was ${picked ? picked.name : 'somewhere else'}. ${city.name} is highlighted in green.`;
      } else {
        this.feedbackEl.textContent = `Skipped — ${city.name} is highlighted in green.`;
      }
    }

    announce(correct ? 'Correct' : `Not quite. ${city.name} is shown on the map.`);
    this.updateHud();

    window.setTimeout(() => {
      this.locked = false;
      this.index += 1;
      if (this.index >= this.round.length) this.finish();
      else this.ask();
    }, REVEAL_MS);
  }

  updateHud() {
    if (this.scoreEl) this.scoreEl.textContent = String(this.score);
    if (this.countEl) {
      this.countEl.textContent = `${Math.min(this.index + 1, this.round.length)} / ${this.round.length}`;
    }
    if (this.progressEl) {
      const percent = Math.round((this.index / this.round.length) * 100);
      this.progressEl.style.width = `${percent}%`;
    }
  }

  updateClock() {
    if (!this.timerEl || !this.playing) return;
    this.timerEl.textContent = formatClock((Date.now() - this.startedAt) / 1000);
  }

  async finish() {
    this.playing = false;
    clearInterval(this.tick);
    window.GermanGoMap?.resetRound?.();

    const seconds = Math.round((Date.now() - this.startedAt) / 1000);
    if (this.playPanel) this.playPanel.hidden = true;
    if (this.progressEl) this.progressEl.style.width = '100%';

    if (!this.resultPanel || !this.resultUrl) return;
    this.resultPanel.hidden = false;
    this.resultPanel.innerHTML = '<div class="loader">Saving your score…</div>';

    try {
      const response = await fetch(this.resultUrl, {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrfToken(),
          'Content-Type': 'application/x-www-form-urlencoded',
          'HX-Request': 'true',
        },
        body: new URLSearchParams({
          score: String(this.score),
          total: String(this.round.length),
          seconds: String(seconds),
          hints: String(this.hints),
        }),
      });
      if (!response.ok) throw new Error('save failed');
      this.resultPanel.innerHTML = await response.text();
      window.htmx?.process(this.resultPanel);
    } catch {
      // Offline or the endpoint is down: still show the player their score.
      this.resultPanel.innerHTML =
        `<div class="quiz-result"><div class="quiz-result__score">${this.score}/${this.round.length}</div>
         <p class="muted">We could not save that round, but well played.</p>
         <button type="button" class="btn btn--primary" data-quiz-action="again">Play again</button></div>`;
    }

    if (!prefersReducedMotion() && window.gsap) {
      window.gsap.from(this.resultPanel, { opacity: 0, y: 16, duration: 0.45 });
    }
  }
}

export function initMapQuiz(root = document) {
  $$('[data-map-quiz]', root).forEach((element) => {
    if (element.dataset.ready) return;
    element.dataset.ready = 'true';
    new MapQuiz(element);
  });
}
