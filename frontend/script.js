// ===============================
// API Gateway endpoint (backend URL created by CloudFormation)
// All frontend requests will go to this URL.
const API = "https://hvq004yygk.execute-api.us-east-1.amazonaws.com/Prod/notes";
// ===============================


// When the page loads, automatically call GET /notes
window.onload = () => {
  listNotes();
};


// ===============================
// CREATE NOTE (POST /notes)
// ===============================
async function createNote() {
  // Get the text the user typed in the input box
  const text = document.getElementById("noteText").value.trim();

  // If the input is empty, stop and warn the user
  if (!text) {
    alert("Note text cannot be empty.");
    return;
  }

  // Send the note text to the backend using POST
  const response = await fetch(API, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text })   // send the note text as JSON
  });

  // If the backend returns 201, the note was created successfully
  if (response.status === 201) {
    // Clear the input box
    document.getElementById("noteText").value = "";

    // Reload the notes list so the new note appears
    listNotes();
  } else {
    alert("Error creating note.");
  }
}


// ===============================
// LIST NOTES (GET /notes)
// ===============================
async function listNotes() {
  // Ask the backend for all notes
  const response = await fetch(API);

  // Convert the backend JSON response into a JavaScript array
  const notes = await response.json();

  // Find the HTML container where notes will be displayed
  const container = document.getElementById("notes");

  // Clear old notes before adding new ones
  container.innerHTML = "";

  // Loop through each note and create a visual card for it
  notes.forEach(note => {
    const div = document.createElement("div");
    div.className = "note";

    // Build the HTML for each note card
    div.innerHTML = `
      <p><strong>${note.text}</strong></p>
      <p>ID: ${note.id}</p>
      <button onclick="updateNote('${note.id}')">Update</button>
      <button onclick="deleteNote('${note.id}')">Delete</button>
    `;

    // Add the note card to the page
    container.appendChild(div);
  });
}


// ===============================
// UPDATE NOTE (PUT /notes/{id})
// ===============================
async function updateNote(id) {
  // Ask the user for the new text
  const newText = prompt("Enter new text:");
  if (!newText) return;

// Send the updated text to the backend
  const response = await fetch(`${API}/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text: newText })
  });

  // If the backend returns 200, the update worked
  if (response.status === 200) {
    // Reload the notes list so the updated note appears
    listNotes();
  } else {
    alert("Error updating note.");
  }
}

// ===============================
// DELETE NOTE (DELETE /notes/{id})
// ===============================
async function deleteNote(id) {
  // Tell the backend to delete the note with this ID
  const response = await fetch(`${API}/${id}`, {
    method: "DELETE"
  });

  // If the backend returns 200, the delete worked
  if (response.status === 200) {
    // Reload the notes list so the deleted note disappears
    listNotes();
  } else {
    alert("Error deleting note.");
  }
}