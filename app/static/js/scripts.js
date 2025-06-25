document.addEventListener('DOMContentLoaded', () => {
  const modal = document.getElementById('confirmDeleteModal');
  if (modal) {
    let formToDelete = null;

    modal.addEventListener('show.bs.modal', event => {
      const button = event.relatedTarget;
      if (button) {
        // Find the closest form with the .delete-form class
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
          formToDelete.submit();
        }
      });
    }
  }
});