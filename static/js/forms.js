/**
 * Enquiry-form behaviour.
 *
 * Validation is Django's — this only smooths the edges: inline feedback on
 * blur, a guard against double submission, and jumping to the first error.
 */

import { $, $$ } from './utils.js';

function markInvalid(field, invalid) {
  const wrapper = field.closest('.field');
  if (wrapper) wrapper.classList.toggle('field--invalid', invalid);
  field.setAttribute('aria-invalid', invalid ? 'true' : 'false');
}

/** Light client-side checks that mirror what Django will enforce anyway. */
function validate(field) {
  const value = field.value.trim();
  if (field.required && !value) return false;
  if (field.type === 'email' && value) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(value);
  }
  if (field.name === 'name' && value) return value.length >= 2;
  return true;
}

function initEnquiryForm(form) {
  if (form.dataset.ready) return;
  form.dataset.ready = 'true';

  const fields = $$('input:not([type=hidden]), textarea', form).filter(
    (input) => input.name !== 'website'
  );

  fields.forEach((field) => {
    // Only complain once someone has left the field, never as they type.
    field.addEventListener('blur', () => {
      if (field.value.trim()) markInvalid(field, !validate(field));
    });
    field.addEventListener('input', () => {
      if (field.getAttribute('aria-invalid') === 'true' && validate(field)) {
        markInvalid(field, false);
      }
    });
  });

  form.addEventListener('submit', (event) => {
    const bad = fields.filter((field) => !validate(field));
    bad.forEach((field) => markInvalid(field, true));

    if (bad.length) {
      event.preventDefault();
      event.stopPropagation();
      bad[0].focus();
      bad[0].scrollIntoView({ behavior: 'smooth', block: 'center' });
      return;
    }

    // HTMX disables the button itself; this covers the no-JS-swap fallback.
    const submit = $('[type="submit"]', form);
    if (submit && !window.htmx) {
      submit.disabled = true;
      submit.classList.add('htmx-request');
    }
  });
}

/** Move focus to a form when a page anchor points at its enquiry block. */
function focusFromHash() {
  if (!window.location.hash.startsWith('#enquiry-')) return;
  const section = document.querySelector(window.location.hash);
  const field = section?.querySelector('input[name="name"]');
  if (field) window.setTimeout(() => field.focus({ preventScroll: true }), 320);
}

export function initForms(root = document) {
  $$('.enquiry-form', root).forEach(initEnquiryForm);

  if (root === document) {
    focusFromHash();
    window.addEventListener('hashchange', focusFromHash);
  }
}
