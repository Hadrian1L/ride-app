document.addEventListener('DOMContentLoaded', () => {
  const createBtn = document.getElementById('create-event-btn');
  const joinBtn = document.getElementById('join-event-btn');
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


  const eventIdInput = document.getElementById("join-event-id");
  const eventHint = document.getElementById("event-name-hint");


  eventIdInput?.addEventListener("input", async () => {
    const code = eventIdInput.value.trim();
    if (!code) {
      eventHint.textContent = "";
      return;
    }


    try {
      const res = await fetch(/events/exists/${code});
      const data = await res.json();


      if (res.ok && data.exists) {
        eventHint.textContent = Event: ${data.event_name};
        eventHint.style.color = "green";
      } else {
        eventHint.textContent = "No event found with this code.";
        eventHint.style.color = "red";
      }
    } catch (err) {
      eventHint.textContent = "Error checking event.";
      eventHint.style.color = "red";
    }
  });
 
  document.getElementById("submit-create-event")?.addEventListener("click", async () => {
    const email = document.querySelector("input[type=email]").value;
    const eventName = document.querySelector("input[placeholder='Event Name']").value;
    const startDate = document.querySelector("input[placeholder='From (MM/DD/YYYY)']").value;
    const endDate = document.querySelector("input[placeholder='To (MM/DD/YYYY)']").value;
    const eventLocation = document.getElementById("event-location").value.trim();
    const description = document.getElementById("event-description").value;
  
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      alert("Please enter a valid email address.");
      return;
    }
  
    if (!email || !eventName || !startDate || !endDate) {
      alert("Please fill in all required fields: Email, Event Name, Start Date, and End Date.");
      return;
    }
  
    if (startDate > endDate) {
      alert("Start date must be before end date.");
      return;
    }
  
    const subEvents = [...document.querySelectorAll(".sub-event-input")]
      .map(input => input.value.trim())
      .filter(v => v !== "");
  
    const payload = {
      email,
      event_name: eventName,
      start_date: startDate,
      end_date: endDate,
      location: eventLocation,
      description,
      sub_events: subEvents
    };
  
    const submitBtn = document.getElementById("submit-create-event");
    submitBtn.disabled = true;
    submitBtn.textContent = "Submitting...";
  
    try {
      const res = await fetch("/events/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
  
      const data = await res.json();
      if (res.ok) {
        alert(Your event was created! Event code: ${data.event_code}. Please make sure to join the event yourself if you plan to drive or attend.);
        closeModal("eventModal");
      } else {
        alert("Error creating event");
      }
    } catch (err) {
      alert("Network error or server issue.");
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = "Submit";
    }
  });

  document.getElementById("submit-join-event")?.addEventListener("click", async () => {
    const eventCode = document.getElementById("join-event-id").value.trim();
    const name = document.getElementById("join-name").value.trim();
    const location = document.getElementById("join-location").value.trim();
    const canDrive = document.getElementById("can-drive").checked;
    const seats = document.getElementById("available-seats").value || 0;
 
    const subEvents = [...document.querySelectorAll('input[name="sub-event"]:checked')]
      .map(input => input.value);

    const payload = {
      event_code: eventCode,
      name,
      location,
      can_drive: canDrive,
      seats,
      sub_event: subEvents.join(', ')
    };
  
    try {
      const res = await fetch("/events/join", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
  
      if (res.ok) {
        alert("Successfully joined event!");
        closeModal("joinModal");
      }
    } catch (err) {
      alert("Error joining event");
    }
  });
  document.getElementById("can-drive")?.addEventListener("change", (e) => {
    const seatsField = document.getElementById("available-seats");
    seatsField.style.display = e.target.checked ? "block" : "none";
  });

  document.getElementById("submit-start-event")?.addEventListener("click", async () => {
    const eventCode = document.getElementById("start-event-id").value.trim();
    const hostCode = document.getElementById("start-host-code").value.trim();
    const hostEmail = document.getElementById("start-email").value.trim();
  
    if (!eventCode || !hostCode || !hostEmail) {
      alert("Please fill in all fields.");
      return;
    }
  
    const payload = {
      event_code: eventCode,
      host_code: hostCode,
      email: hostEmail
    };

    const checkRes = await fetch(/events/exists/${eventCode});
    const checkData = await checkRes.json();

    if (!checkRes.ok || !checkData.exists) {
      alert("Invalid event code. No such event exists.");
      return;
    }

    const hostRes = await fetch("/events/validate-host", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ event_code: eventCode, host_code: hostCode, email: hostEmail })
    });
  
    const hostData = await hostRes.json();
    if (!hostRes.ok || !hostData.valid) {
      alert("Host code or email is incorrect for this event.");
      return;
    }
  
    try {
      const res = await fetch("/events/start", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
  
      const data = await res.json();
      if (res.ok) {
        alert("Event started successfully!");
        closeModal("startEventModal");
      } else {
        alert("Error: " + (data.message || "Could not start event."));
      }
    } catch (err) {
      alert("Network error or server not responding.");
    }
  });

  document.getElementById("verify-event-code")?.addEventListener("click", async () => {
    const code = document.getElementById("join-event-id").value.trim();
    if (!code) return alert("Please enter an event code");
  
    try {
      const res = await fetch(/events/details/${code});
      if (!res.ok) throw new Error('Event not found');
      const eventData = await res.json();

      document.getElementById("event-title").textContent = eventData.event_name;
      document.getElementById("event-location-display").textContent = eventData.location;
      document.getElementById("event-description-display").textContent = eventData.description;

      const subEventsContainer = document.getElementById("sub-events-checkboxes");
      subEventsContainer.innerHTML = eventData.sub_events.length > 0 
        ? eventData.sub_events.map((event, index) => `
            <div class="sub-event-row">
              <span class="sub-event-name">${event}</span>
              <input type="checkbox" name="sub-event" value="${event}" id="sub-event-${index}">
            </div>
          `).join('')
        : '<p style="color: #666;">No sub-events available</p>';

      document.getElementById("join-step1").style.display = 'none';
      document.getElementById("join-step2").style.display = 'block';
      document.querySelector("#joinModal .modal-content").style.width = '400px';
      
    } catch (err) {
      alert("Invalid event code. Please check and try again.");
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

function switchModal(fromId, toId) {
  closeModal(fromId);
  openModal(toId);
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
