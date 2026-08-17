// ============================================
// PASTE YOUR API GATEWAY INVOKE URL HERE
// ============================================
const API_URL = "https://iyxzn2e6w6.execute-api.us-east-1.amazonaws.com/Prod";

window.onload = () => {
  listNotes();
};

async function createNote() {
  const text = document.getElementById("noteText").value.trim();
  if (!text) return alert("Note text cannot be empty.");

  try {
    const response = await fetch(`${API_URL}/notes`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: text })
    });

    if (!response.ok) throw new Error(`Create failed with status ${response.status}`);

    document.getElementById("noteText").value = "";
    listNotes();
  } catch (err) {
    console.error(err);
    alert("Failed to create note. Check the console for details.");
  }
}

async function listNotes() {
  const container = document.getElementById("notes");

  try {
    const response = await fetch(`${API_URL}/notes`);
    if (!response.ok) throw new Error(`List failed with status ${response.status}`);

    const notes = await response.json();
    container.innerHTML = "";

    notes.forEach(n => {
      const div = document.createElement("div");
      div.className = "note";
      div.innerHTML = `
        <p><strong>${n.text}</strong></p>
        <p>ID: ${n.id}</p>
        <button onclick="updateNote('${n.id}')">Update</button>
        <button onclick="deleteNote('${n.id}')">Delete</button>
      `;
      container.appendChild(div);
    });
  } catch (err) {
    console.error(err);
    container.innerHTML = "<p>Failed to load notes. Check the console for details.</p>";
  }
}

async function updateNote(id) {
  const newText = prompt("Enter new text:");
  if (!newText) return;

  try {
    const response = await fetch(`${API_URL}/notes/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: newText })
    });

    if (!response.ok) throw new Error(`Update failed with status ${response.status}`);
    listNotes();
  } catch (err) {
    console.error(err);
    alert("Failed to update note. Check the console for details.");
  }
}

async function deleteNote(id) {
  try {
    const response = await fetch(`${API_URL}/notes/${id}`, { method: "DELETE" });
    if (!response.ok) throw new Error(`Delete failed with status ${response.status}`);
    listNotes();
  } catch (err) {
    console.error(err);
    alert("Failed to delete note. Check the console for details.");
  }
}

async function getNote() {
  const id = document.getElementById("getNoteId").value.trim();
  const resultDiv = document.getElementById("singleNoteResult");

  if (!id) return alert("Please paste a note ID.");

  try {
    const response = await fetch(`${API_URL}/notes/${id}`);

    if (response.status === 404) {
      resultDiv.innerHTML = "<p>No note found with that ID.</p>";
      return;
    }

    if (!response.ok) throw new Error(`Get failed with status ${response.status}`);

    const note = await response.json();
    resultDiv.innerHTML = `
      <div class="note">
        <p><strong>${note.text}</strong></p>
        <p>ID: ${note.id}</p>
        <p>Created: ${note.createdAt}</p>
      </div>
    `;
  } catch (err) {
    console.error(err);
    resultDiv.innerHTML = "<p>Failed to fetch note. Check the console for details.</p>";
  }
}