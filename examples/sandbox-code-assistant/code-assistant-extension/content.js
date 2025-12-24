let socket = null;

chrome.runtime.onMessage.addListener((msg) => {
  if (msg.type === "OPEN_PANEL") {
    openPanel();
  }
});

// -------------------------------------------------
// WEBPAGE TEXT EXTRACTOR
// -------------------------------------------------
function extractWebpageContent() {
  const cloned = document.cloneNode(true);
  cloned.querySelectorAll("script, style, iframe, noscript").forEach(e => e.remove());

  let main =
    cloned.querySelector("article") ||
    cloned.querySelector("main") ||
    cloned.querySelector("#content") ||
    cloned.body;

  const text = Array.from(main.querySelectorAll("h1, h2, h3, p"))
    .map(el => el.innerText.trim())
    .filter(Boolean)
    .join("\n\n");

  return text;
}

// -------------------------------------------------
// PANEL UI
// -------------------------------------------------
function openPanel() {
  const old = document.getElementById("assistant-box");
  if (old) old.remove();

  const box = document.createElement("div");
  box.id = "assistant-box";

  box.innerHTML = `
    <div id="assistant-container">
      <div id="assistant-header">
        <h3>Code Assistant</h3>
        <button id="assistant-close">×</button>
      </div>

      <textarea id="assistant-input" placeholder="Message Agent..."></textarea>

      <div class="btn-row">
        <button id="connect-btn">Connect</button>
        <button id="disconnect-btn">Disconnect</button>
        <button id="send-btn">Send</button>
        <button id="extract-btn">Extract</button>
      </div>

      <div id="assistant-result">Not connected.</div>
    </div>
  `;

  document.body.appendChild(box);

  document.getElementById("assistant-close").onclick = () => box.remove();

  const resultBox = document.getElementById("assistant-result");
  const inputBox = document.getElementById("assistant-input");

  // -------------------------------------------------
  // TEXT SELECTION LISTENER
  // -------------------------------------------------
  document.addEventListener("mouseup", () => {
    const selection = window.getSelection().toString().trim();
    if (!selection) return;

    // Append selected text to message box
    inputBox.value += (inputBox.value ? "\n\n" : "") + selection;

    // Scroll text area to bottom
    inputBox.scrollTop = inputBox.scrollHeight;
  });

  // -------------------------------------------------
  // CONNECT
  // -------------------------------------------------
  document.getElementById("connect-btn").onclick = () => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      resultBox.innerText = "Already connected.";
      return;
    }

    socket = new WebSocket("ws://localhost:8000/ws");

    socket.onopen = () => {
      resultBox.innerText = "Connected to WebSocket.";
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      resultBox.innerText += "\n\nAssistant:\n" + data.reply;
      resultBox.scrollTop = resultBox.scrollHeight;
    };

    socket.onerror = () => {
      resultBox.innerText = "WebSocket error.";
    };

    socket.onclose = () => {
      resultBox.innerText = "Disconnected.";
    };
  };

  // -------------------------------------------------
  // DISCONNECT
  // -------------------------------------------------
  document.getElementById("disconnect-btn").onclick = () => {
    if (socket) socket.close();
  };

  // -------------------------------------------------
  // SEND MESSAGE
  // -------------------------------------------------
  document.getElementById("send-btn").onclick = () => {
    const context = inputBox.value;

    if (!socket || socket.readyState !== WebSocket.OPEN) {
      resultBox.innerText = "Not connected.";
      return;
    }

    socket.send(JSON.stringify({ message: context }));

    inputBox.value = "";

    resultBox.innerText += "\n\nYou:\n" + context;
  };

  // -------------------------------------------------
  // EXTRACT PAGE → ADD TO MESSAGE BOX
  // -------------------------------------------------
  document.getElementById("extract-btn").onclick = () => {
    const extracted = extractWebpageContent();

    if (!extracted || extracted.length < 10) {
      resultBox.innerText = "Could not extract useful content.";
      return;
    }

    // Add extracted text to input box (not sent automatically)
    inputBox.value += (inputBox.value ? "\n\n" : "") + extracted;

    // Scroll text area
    inputBox.scrollTop = inputBox.scrollHeight;

    resultBox.innerText = "📄 Extracted content added to message box.";
  };
}
