document.addEventListener('DOMContentLoaded', () => {
    // Button elements
    const createBtn = document.getElementById('create-event-btn');
    const joinBtn = document.getElementById('join-event-btn');
  
    // Modal overlay
    const overlay = document.getElementById('modal-overlay');
  
    // Close buttons
    const closeButtons = document.querySelectorAll('.modal .close');
  
    // Event Listeners for opening modals
    createBtn.addEventListener('click', () => openModal('createModal'));
    joinBtn.addEventListener('click', () => openModal('joinModal'));
  
    // Event Listeners for closing modals
    closeButtons.forEach(button => {
      button.addEventListener('click', () => {
        const modal = button.closest('.modal');
        closeModal(modal.id);
      });
    });
  
    // Functions
    function openModal(modalId) {
      document.getElementById(modalId).classList.remove('hidden');
      overlay.classList.remove('hidden');
    }
  
    function closeModal(modalId) {
      document.getElementById(modalId).classList.add('hidden');
      overlay.classList.add('hidden');
    }
  });
  