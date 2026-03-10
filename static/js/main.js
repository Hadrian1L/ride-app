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
      const res = await fetch(`/events/exists/${code}`);
      const data = await res.json();


      if (res.ok && data.exists) {
        eventHint.textContent = `Event: ${data.event_name}`;
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
        alert(`Your event was created! Event code: ${data.event_code}. Please make sure to join the event yourself if you plan to drive or attend.`);
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
    const attend = document.getElementById("chk-attend");
    const skip = document.getElementById("chk-skip");
    
    const eventCode = document.getElementById("join-event-id").value.trim();
    const name = document.getElementById("join-name").value.trim();
    const location = document.getElementById("join-location").value.trim();
    const canDrive = document.getElementById("can-drive").checked;
    const seats = document.getElementById("available-seats").value || 0;

    let label;
    if (skip.checked && attend.checked) {
      alert("Only select one option for the sub-event");
      return;
    }
    if (attend.checked) {
      label = "A";
    } else if (skip.checked) {
      label = "no";
    } else {
      label = "indifferent";
    }

    const payload = {
      event_code: eventCode,
      name,
      location,
      can_drive: canDrive,
      seats,
      //sub_event: subEvents.join(', ')
      sub_event: label
    };
    
    if(!name || !location){
      alert("Please enter your information")
      return;
    }

    const isValid = await testGeocode(location);
    if (!isValid) {
      alert("We couldn't locate that address. "
            + "Please enter a more specific address "
            + "(e.g. 123 Main St, City, State).");
      return;
    }

    try {
      const res = await fetch(`/events/join/${eventCode}`, {
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

    const checkRes = await fetch(`/events/exists/${eventCode}`);
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

    const submitBtn = document.getElementById("submit-start-event");
    submitBtn.disabled = true;
    submitBtn.textContent = "Submitting...";
  
    try {
      const res = await fetch(`/events/assign/${eventCode}`);
  
      const data = await res.json();
      if (res.ok) {
        await start_event(eventCode)
        alert("Event started successfully! Rides will be emailed to host");
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
    console.log("Sending join request with event code:", code);
    if (!code) return alert("Please enter an event code");

    try {
      const res = await fetch(`/events/details/${code}`);
      if (!res.ok) throw new Error('Event not found');
      const eventData = await res.json();

      document.getElementById("event-title").textContent = eventData.event_name;
      document.getElementById("event-location-display").textContent = eventData.location;
      document.getElementById("event-description-display").textContent = eventData.description;

      document.getElementById("join-step1").style.display = 'none';
      document.getElementById("join-step2").style.display = 'block';

      const attend = document.getElementById("chk-attend");
      const skip = document.getElementById("chk-skip");

      attend.addEventListener("change", () => {
        if (attend.checked) skip.checked = false;
      });
      skip.addEventListener("change", () => {
        if (skip.checked) attend.checked = false;
      });

      document.querySelector("#joinModal .modal-content").style.width = '400px';
    } catch (err) {
      alert("Invalid event code. Please check and try again.");
    }
  });
  
});

async function testGeocode(address) {
  try {
    const res = await fetch(`/api/validate-address?location=${encodeURIComponent(address)}`);
    const data = await res.json();
    return res.ok && data.valid;
  } catch {
    return false;
  }
}

async function start_event(eventCode) {
  try {
    const res = await fetch(`/events/assign/${eventCode}`);
    const data = await res.json();

    if (!res.ok) {
      alert(data.error || "Failed to assign rides.");
      return;
    }

    const container = document.getElementById("assignmentsDisplay");
    container.innerHTML = "";

    data.forEach((group, index) => {
      const div = document.createElement("div");
      div.innerHTML = `
        <strong>Driver ${index + 1}: ${group.driver.name}</strong><br/>
        <em>Driver Location: ${group.driver.location}</em>
        <ul>
          ${group.riders.map(r => `<li>${r.name} (${r.location})</li>`).join("")}
        </ul>
        <hr/>
      `;
      container.appendChild(div);
    });

    //openModal("assignmentsModal");
  } catch (err) {
    alert("Error fetching assignments.");
  }
}

const MAX_SUB_EVENTS = 1; //temporary, might change to two
function confirmSubEvent() {
  const currentCount = document.querySelectorAll(".sub-event-input").length;

  if (currentCount >= MAX_SUB_EVENTS) {
    document.getElementById("add-sub-event").disabled = true;
    alert(`You can only add up to ${MAX_SUB_EVENTS} sub-event${MAX_SUB_EVENTS > 1 ? "s" : ""}.`);
    closeModal("subEventModal");
    return;
  }
  
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

function switchModal(fromId, toId) {
  closeModal(fromId);
  openModal(toId);
}

window.onclick = function(event) {
  const modals = ['eventModal', 'joinModal',
                'chooseJoinStartModal', 'startEventModal', 'subEventModal'];
  modals.forEach(id => {
    const modal = document.getElementById(id);
    if (event.target === modal) {
      modal.style.display = "none";
    }
  });
}
