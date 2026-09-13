const chatLog = document.getElementById("chat-log");
const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");

document.querySelectorAll(".chip").forEach((chip) => {
  chip.addEventListener("click", () => {
    sendMessage(chip.dataset.msg);
  });
});

chatForm.addEventListener("submit", (e) => {
  e.preventDefault();
  const message = chatInput.value.trim();
  if (!message) return;
  chatInput.value = "";
  sendMessage(message);
});

async function sendMessage(message) {
  appendBubble(message, "user");
  const typingEl = appendBubble("…", "bot");

  try {
    const data = await apiRequest("/chatbot", { method: "POST", body: { message } });
    typingEl.textContent = data.reply;
  } catch (err) {
    typingEl.textContent = "Sorry, I couldn't reach the server: " + err.message;
  }
  chatLog.scrollTop = chatLog.scrollHeight;
}

function appendBubble(text, who) {
  const row = document.createElement("div");
  row.className = `chat-row ${who}`;
  const bubble = document.createElement("div");
  bubble.className = `chat-bubble ${who}`;
  bubble.textContent = text;
  row.appendChild(bubble);
  chatLog.appendChild(row);
  chatLog.scrollTop = chatLog.scrollHeight;
  return bubble;
}
