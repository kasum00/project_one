// ================== ELEMENTS ==================
const chatWindow = document.querySelector(".chat-window");
const chatForm = document.querySelector(".chat-input");
const chatInput = chatForm.querySelector("input");

let selectedWardrobeItem = null;
let currentMode = null; // "similar" | "outfit"

// ================== UTIL ==================
function scrollBottom() {
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

function addMessage(html, sender = "bot") {
  const div = document.createElement("div");
  div.className = `chat-message ${sender}`;
  div.innerHTML = html;
  chatWindow.appendChild(div);
  scrollBottom();
}

function addTyping() {
  const div = document.createElement("div");
  div.className = "chat-message bot typing";
  div.id = "typingIndicator";
  div.innerHTML = "<span></span><span></span><span></span>";
  chatWindow.appendChild(div);
  scrollBottom();
}

function removeTyping() {
  document.getElementById("typingIndicator")?.remove();
}

// ================== INIT ==================
window.addEventListener("DOMContentLoaded", () => {
  addMessage("Hello!  How can I help you?");
  showActionOptions();
});

// ================== ACTION OPTIONS ==================
function showActionOptions() {
  if (document.querySelector(".chat-action-options")) return;

  const box = document.createElement("div");
  box.className = "chat-message bot chat-action-options";
  box.innerHTML = `
    <div style="margin-bottom:8px">Please choose an option:</div>
    <div style="display:flex; gap:10px">
      <button class="chat-option-btn" data-action="similar">
         Find similar item
      </button>
      <button class="chat-option-btn" data-action="outfit">
         Find matching outfit
      </button>
    </div>
  `;

  chatWindow.appendChild(box);
  scrollBottom();

  box.querySelectorAll("button").forEach(btn => {
    btn.onclick = () => {
      box.remove();
      handleAction(btn.dataset.action);
    };
  });
}

// ================== HANDLE ACTION ==================
function handleAction(type) {
  currentMode = type;

  addMessage(
    type === "similar"
      ? "Find similar item"
      : "Find matching outfit",
    "user"
  );

  addMessage("Please choose an item from your wardrobe.", "bot");
  openItemPicker();
}

// ================== ITEM PICKER (OVERLAY) ==================
async function openItemPicker() {
  const overlay = document.getElementById("itemPickerOverlay");
  const grid = document.getElementById("itemPickerGrid");

  grid.innerHTML = "";
  overlay.classList.remove("hidden");

  try {
    const items = await apiFetch("/wardrobe");

    items.forEach(item => {
      const img = document.createElement("img");
      img.src = `http://localhost:3000/${item.image_path}`;
      img.style.cursor = "pointer";

      img.onclick = () => {
        overlay.classList.add("hidden");
        handlePickedItem(item);
      };

      grid.appendChild(img);
    });
  } catch (e) {
    overlay.classList.add("hidden");
    addMessage(" Failed to load wardrobe.", "bot");
  }
}

document.getElementById("closeItemPicker").onclick = () => {
  document.getElementById("itemPickerOverlay").classList.add("hidden");
};

// ================== AFTER PICK ITEM ==================
async function handlePickedItem(item) {
  selectedWardrobeItem = item;

  addMessage("I choose this item.", "user");
  addMessage(
    `<img src="http://localhost:3000/${item.image_path}"
          style="width:160px;border-radius:16px">`,
    "user"
  );

  if (currentMode === "similar") {
    await runFindSimilar();
  } else {
    await runFindOutfit();
  }
}

// ================== FIND SIMILAR ==================
async function runFindSimilar() {
  addMessage("Finding similar items for this piece… ", "bot");
  addTyping();

  try {
    const res = await apiFetch("/chatbot/similar", {
      method: "POST",
      body: JSON.stringify({ itemId: selectedWardrobeItem.id }),
      headers: { "Content-Type": "application/json" }
    });

    removeTyping();

    if (!res.items || !res.items.length) {
      addMessage("No similar items found.", "bot");
      showActionOptions();
      return;
    }

    showResultGrid(res.items);
    showActionOptions();
  } catch (e) {
    removeTyping();
    addMessage(" Failed to find similar items.", "bot");
  }
}

// ================== FIND OUTFIT ==================
async function runFindOutfit() {
  addMessage("Creating a matching outfit for this item… ", "bot");
  addTyping();

  try {
    const res = await apiFetch("/chatbot/outfit", {
      method: "POST",
      body: JSON.stringify({ itemId: selectedWardrobeItem.id }),
      headers: { "Content-Type": "application/json" }
    });

    removeTyping();

    if (!res.outfit || !res.outfit.length) {
      addMessage("No suitable outfit found.", "bot");
      showActionOptions();
      return;
    }

    showResultGrid(res.outfit);
    showActionOptions();
  } catch (e) {
    removeTyping();
    addMessage(" Failed to generate outfit.", "bot");
  }
}

// ================== RESULT GRID (CHAT – GỌN) ==================
function showResultGrid(items) {
  const grid = document.createElement("div");
  grid.className = "chat-message bot image-grid";

  items.forEach(item => {
    const img = document.createElement("img");
    img.src = `http://localhost:3000/${item.image_path}`;
    grid.appendChild(img);
  });

  chatWindow.appendChild(grid);
  scrollBottom();
}

// ================== TEXT INPUT ==================
chatForm.addEventListener("submit", e => {
  e.preventDefault();
  const text = chatInput.value.trim();
  if (!text) return;

  addMessage(text, "user");
  chatInput.value = "";

  addTyping();
  setTimeout(() => {
    removeTyping();
    addMessage("Please choose an option below.", "bot");
    showActionOptions();
  }, 500);
});
