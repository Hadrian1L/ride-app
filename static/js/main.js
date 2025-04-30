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
    openModal("subEventModal");
  });  
  

  document.getElementById("submit-create-event")?.addEventListener("click", async () => {
    const email = document.querySelector("input[type=email]").value;
    const eventName = document.querySelector("input[placeholder='Event Name']").value;
    const startDate = document.querySelector("input[placeholder='From (MM/DD/YYYY)']").value;
    const endDate = document.querySelector("input[placeholder='To (MM/DD/YYYY)']").value;
    const description = document.getElementById("event-description").value;

    const subEvents = [...document.querySelectorAll(".sub-event-input")]
      .map(input => input.value.trim())
      .filter(v => v !== "");
    if(!email || !eventName || !startDate || !endDate){
      alert("Please fill in all required fields: Email, Event Name, Start Date, and End Date.");
      return;
    }
    

    const payload = {
      email: email,
      event_name: eventName,
      start_date: startDate,
      end_date: endDate,
      description: description,
      sub_events: subEvents
    };

    if(startDate > endDate){
        alert("Start date invalid");
        return
    }
    
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

function confirmSubEvent() {
  const name = document.getElementById("sub-event-input").value.trim();
  if (!name) return;

  const input = document.createElement("input");
  input.type = "text";
  input.className = "sub-event-input";
  input.value = name;
  input.readOnly = true;
  input.style.marginTop = "5px";

  document.getElementById("sub-events-container").appendChild(input);
  document.getElementById("sub-event-input").value = "";
  closeModal("subEventModal");
}


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
