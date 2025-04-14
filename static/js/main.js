document.addEventListener('DOMContentLoaded', () => {
  const createBtn = document.getElementById('create-event-btn');
  const joinBtn = document.getElementById('join-event-btn');
  const overlay = document.getElementById('modal-overlay');
  const closeButtons = document.querySelectorAll('.modal .close');

  createBtn?.addEventListener('click', () => openModal('eventModal'));
  joinBtn?.addEventListener('click', () => openModal('joinModal'));

  closeButtons.forEach(button => {
    button.addEventListener('click', () => {
      const modal = button.closest('.modal');
      closeModal(modal.id);
    });
  });

  document.getElementById("add-sub-event")?.addEventListener("click", () => {
    const container = document.getElementById("sub-events-container");
    const msg = document.getElementById("no-sub-events-msg");
    if (msg) msg.remove();
  
    const input = document.createElement("input");
    input.type = "text";
    input.className = "sub-event-input";
    input.placeholder = "Sub-Event";
    input.style.marginTop = "5px";
    container.appendChild(input);
  });
  

  document.getElementById("submit-create-event")?.addEventListener("click", async () => {
    const email = document.querySelector("input[type=email]").value;
    const eventName = document.querySelector("input[placeholder='Event Name']").value;
    const startDate = document.querySelector("input[placeholder='From (MM/DD/YYYY)']").value;
    const endDate = document.querySelector("input[placeholder='To (MM/DD/YYYY)']").value;

    const subEvents = [...document.querySelectorAll(".sub-event-input")]
      .map(input => input.value.trim())
      .filter(v => v !== "");

    const payload = {
      email: email,
      event_name: eventName,
      start_date: startDate,
      end_date: endDate,
      sub_events: subEvents
    };

    const res = await fetch("/events/create", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    if (res.ok) {
      alert(`Your event was created! Event code: ${data.event_code}`);
      closeModal("eventModal");
    } else {
      alert("Error creating event");
    }
  });
});

function openModal(id) {
  document.getElementById(id).style.display = "block";
}

function closeModal(id) {
  document.getElementById(id).style.display = "none";
}

window.onclick = function(event) {
  const modals = ['eventModal', 'joinModal'];
  modals.forEach(id => {
    const modal = document.getElementById(id);
    if (event.target === modal) {
      modal.style.display = "none";
    }
  });
}
