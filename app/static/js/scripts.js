/**
 * Enhanced user experience scripts.
 * 
 * Provides:
 * - Loading states for forms
 * - Keyboard shortcuts
 * - Better form feedback
 * - Toast notifications
 */
document.addEventListener('DOMContentLoaded', () => {
  // Confirmation modal for delete actions
  const modal = document.getElementById('confirmDeleteModal');
  if (modal) {
    let formToDelete = null;

    modal.addEventListener('show.bs.modal', event => {
      const button = event.relatedTarget;
      if (button) {
        formToDelete = button.closest('form.delete-form');
        const type = button.getAttribute('data-type') || 'item';
        const targetSpan = document.getElementById('deleteTargetType');
        if (targetSpan) {
          targetSpan.textContent = `this ${type}`;
        }
      }
    });

    const confirmBtn = document.getElementById('confirmDeleteBtn');
    if (confirmBtn) {
      confirmBtn.addEventListener('click', () => {
        if (formToDelete) {
          // Show loading state
          confirmBtn.disabled = true;
          confirmBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Deleting...';
          formToDelete.submit();
        }
      });
    }
  }

  // Add loading states to all forms
  const forms = document.querySelectorAll('form');
  forms.forEach(form => {
    form.addEventListener('submit', function(e) {
      const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
      if (submitBtn && !form.classList.contains('no-loading')) {
        submitBtn.disabled = true;
        const originalText = submitBtn.textContent || submitBtn.value;
        submitBtn.innerHTML = originalText.includes('Loading') 
          ? originalText 
          : `<span class="spinner-border spinner-border-sm me-2"></span>${originalText}`;
      }
    });
  });

  // Keyboard shortcuts
  document.addEventListener('keydown', (e) => {
    // Ctrl+S or Cmd+S to save forms
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
      const form = document.querySelector('form:not(.no-shortcut)');
      if (form && form.checkValidity()) {
        e.preventDefault();
        form.requestSubmit();
      }
    }
    
    // Escape to close modals
    if (e.key === 'Escape') {
      const modals = document.querySelectorAll('.modal.show');
      modals.forEach(modal => {
        const bsModal = bootstrap.Modal.getInstance(modal);
        if (bsModal) {
          bsModal.hide();
        }
      });
    }
  });

  // Auto-dismiss flash messages after 5 seconds
  const flashMessages = document.querySelectorAll('.alert:not(.alert-permanent)');
  flashMessages.forEach(msg => {
    setTimeout(() => {
      const bsAlert = new bootstrap.Alert(msg);
      bsAlert.close();
    }, 5000);
  });

  // Add tooltips to all elements with data-bs-toggle="tooltip"
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });

  // Form validation feedback
  const validatedForms = document.querySelectorAll('.needs-validation');
  validatedForms.forEach(form => {
    form.addEventListener('submit', function(event) {
      if (!form.checkValidity()) {
        event.preventDefault();
        event.stopPropagation();
      }
      form.classList.add('was-validated');
    }, false);
  });

  // Focus first input in modals when they open
  const modals = document.querySelectorAll('.modal');
  modals.forEach(modal => {
    modal.addEventListener('shown.bs.modal', function() {
      const firstInput = modal.querySelector('input, textarea, select');
      if (firstInput) {
        firstInput.focus();
      }
    });
  });
});
