/* AMS - shared JavaScript (no frameworks, vanilla only) */

(function () {
  'use strict';

  // ---------------------------------------------------------------------
  // Confirmation dialog for dangerous actions.
  // Use: <form method="post" data-confirm="Delete this member?"> ... </form>
  // ---------------------------------------------------------------------
  let confirmForm = null;

  function openConfirmModal(form) {
    confirmForm = form;
    const overlay = document.getElementById('confirm-modal');
    const text = form.getAttribute('data-confirm') || 'Are you sure?';
    overlay.querySelector('.modal p').textContent = text;
    overlay.classList.add('open');
  }

  function closeConfirmModal() {
    const overlay = document.getElementById('confirm-modal');
    if (overlay) overlay.classList.remove('open');
    confirmForm = null;
  }

  document.addEventListener('submit', function (e) {
    const form = e.target;
    if (form.matches('form[data-confirm]')) {
      e.preventDefault();
      openConfirmModal(form);
    }
  });

  // Confirm dialog buttons
  document.addEventListener('click', function (e) {
    const cancel = e.target.closest('[data-modal-cancel]');
    const confirmBtn = e.target.closest('[data-modal-confirm]');
    if (cancel) closeConfirmModal();
    if (confirmBtn && confirmForm) {
      confirmForm.submit();
      closeConfirmModal();
    }
  });

  // ---------------------------------------------------------------------
  // Loading state: disable submit button while the form is being sent.
  // Use: <form class="js-loading"> ... <button type="submit">Save</button>
  // ---------------------------------------------------------------------
  document.addEventListener('submit', function (e) {
    const form = e.target;
    if (!form.classList.contains('js-loading')) return;
    const btn = form.querySelector('button[type="submit"]');
    if (btn) {
      btn.disabled = true;
      const original = btn.textContent;
      btn.dataset.originalText = original;
      btn.textContent = 'Please wait...';
    }
  });

  // ---------------------------------------------------------------------
  // Auto-dismiss toast messages.
  // ---------------------------------------------------------------------
  function dismissToasts() {
    document.querySelectorAll('#messages-container .toast').forEach(function (toast) {
      setTimeout(function () {
        toast.style.transition = 'opacity 0.4s';
        toast.style.opacity = '0';
        setTimeout(function () { toast.remove(); }, 400);
      }, 4000);
    });
  }
  dismissToasts();
})();
