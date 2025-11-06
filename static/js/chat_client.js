const BASE_URL = "http://localhost:8001";

async function makeRequest(endpoint, method = "GET", data = null) {
  try {
    const options = {
      method: method,
      headers: {
        "Content-Type": "application/json",
      },
    };

    if (data && method !== "GET") {
      options.body = JSON.stringify(data);
    }

    const response = await fetch(`${BASE_URL}${endpoint}`, options);
    const text = await response.text();

    try {
      return JSON.parse(text);
    } catch {
      return { raw: text };
    }
  } catch (error) {
    return { error: error.message };
  }
}

function displayResponse(elementId, data, isError = false) {
  const element = document.getElementById(elementId);
  element.style.display = "block";
  element.className = "response" + (isError ? " error" : "");
  element.textContent = JSON.stringify(data, null, 2);
}

async function registerPeer() {
  const data = {
    peer_id: document.getElementById("peerId").value,
    ip: document.getElementById("peerIp").value,
    port: parseInt(document.getElementById("peerPort").value),
  };

  const result = await makeRequest("/submit-info", "POST", data);
  displayResponse("registerResponse", result, result.error);
}

async function getPeerList() {
  const result = await makeRequest("/get-list", "GET");
  displayResponse("registerResponse", result, result.error);

  if (result.peers) {
    const peerListDiv = document.getElementById("peerList");
    peerListDiv.innerHTML = "<h3>Active Peers:</h3>";
    result.peers.forEach((peer) => {
      peerListDiv.innerHTML += `
                  <div class="peer-item">
                      <strong>${peer.peer_id}</strong> - ${peer.ip}:${peer.port}
                      <span class="status connected">Online</span>
                  </div>
              `;
    });
  }
}

async function joinChannel() {
  const data = {
    peer_id: document.getElementById("channelPeerId").value,
    channel: document.getElementById("channelName").value,
  };

  const result = await makeRequest("/add-list", "POST", data);
  displayResponse("channelResponse", result, result.error);
}

async function connectPeer() {
  const data = {
    from_peer: document.getElementById("fromPeer").value,
    to_peer: document.getElementById("toPeer").value,
  };

  const result = await makeRequest("/connect-peer", "POST", data);
  displayResponse("connectResponse", result, result.error);
}

async function broadcastMessage() {
  const data = {
    peer_id: document.getElementById("broadcastPeerId").value,
    channel: document.getElementById("broadcastChannel").value,
    message: document.getElementById("broadcastMessage").value,
  };

  const result = await makeRequest("/broadcast-peer", "POST", data);
  displayResponse("broadcastResponse", result, result.error);
}

async function getMessages() {
  const data = {
    channel: document.getElementById("broadcastChannel").value,
  };

  const result = await makeRequest("/get-messages", "GET", data);
  displayResponse("broadcastResponse", result, result.error);

  if (result.messages) {
    const messageListDiv = document.getElementById("messageList");
    messageListDiv.innerHTML = "<h3>Messages:</h3>";
    result.messages.forEach((msg) => {
      messageListDiv.innerHTML += `
                  <div class="message-item">
                      <strong>${msg.from}</strong>: ${msg.message}
                      <br><small>${msg.timestamp}</small>
                  </div>
              `;
    });
  }
}

async function sendDirectMessage() {
  const data = {
    from_peer: document.getElementById("dmFromPeer").value,
    to_peer: document.getElementById("dmToPeer").value,
    message: document.getElementById("dmMessage").value,
  };

  const result = await makeRequest("/send-peer", "POST", data);
  displayResponse("dmResponse", result, result.error);
}

// Auto-refresh peer list every 5 seconds
setInterval(() => {
  if (document.getElementById("peerList").innerHTML !== "") {
    getPeerList();
  }
}, 5000);
