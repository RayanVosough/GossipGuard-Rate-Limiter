const debugUrl = "/internal/gossip/debug";
const stateUrl = "/internal/gossip/state";
const probeUrl = "/protected/public";
const authMeUrl = "/auth/me";
const authTokenUrl = "/auth/token";

const els = {
  gate: document.getElementById("gate"),
  gateUsername: document.getElementById("gate-username"),
  gatePassword: document.getElementById("gate-password"),
  gateEnter: document.getElementById("gate-enter"),
  gateStatus: document.getElementById("gate-status"),
  shell: document.querySelector(".shell"),
  gossipPill: document.getElementById("gossip-pill"),
  nodePill: document.getElementById("node-pill"),
  nodeCount: document.getElementById("node-count"),
  peerCount: document.getElementById("peer-count"),
  snapshotSize: document.getElementById("snapshot-size"),
  lastSync: document.getElementById("last-sync"),
  lastSource: document.getElementById("last-source"),
  peerList: document.getElementById("peer-list"),
  snapshotJson: document.getElementById("snapshot-json"),
  probeButton: document.getElementById("probe-button"),
  refreshButton: document.getElementById("refresh-button"),
  probeStatus: document.getElementById("probe-status"),
  probeLimit: document.getElementById("probe-limit"),
  probeCurrent: document.getElementById("probe-current"),
  probeDetail: document.getElementById("probe-detail"),
};

function getStoredToken() {
  return localStorage.getItem("auth-token") ?? "";
}

function setStoredToken(token) {
  if (token) {
    localStorage.setItem("auth-token", token);
  } else {
    localStorage.removeItem("auth-token");
  }
}

function showDashboard() {
  els.gate.classList.add("is-hidden");
  els.shell.classList.remove("is-hidden");
}

function showGate(message) {
  els.shell.classList.add("is-hidden");
  els.gate.classList.remove("is-hidden");
  els.gateStatus.textContent = message;
}

function formatTime(value) {
  if (!value) {
    return "Never";
  }

  const date = new Date(value * 1000);
  return Number.isNaN(date.getTime()) ? "Unknown" : date.toLocaleString();
}

function renderPeers(peers, gossipEnabled) {
  if (!peers.length) {
    els.peerList.innerHTML = `
      <div class="peer">
        <div>
          <strong>No peers configured</strong>
          <span>Set PEER_URLS to see live gossip targets.</span>
        </div>
        <span class="status-warn">idle</span>
      </div>
    `;
    els.gossipPill.textContent = gossipEnabled ? "Gossip on" : "Gossip off";
    return;
  }

  els.peerList.innerHTML = peers
    .map((peer) => `
      <div class="peer">
        <div>
          <strong>${peer}</strong>
          <span>Gossip target</span>
        </div>
        <span class="status-up">configured</span>
      </div>
    `)
    .join("");

  els.gossipPill.textContent = gossipEnabled ? "Gossip on" : "Gossip off";
}

async function refreshDashboard() {
  const token = getStoredToken();
  const headers = token ? { Authorization: `Bearer ${token}` } : {};

  const [debugResponse, stateResponse] = await Promise.all([
    fetch(debugUrl, { headers }),
    fetch(stateUrl, { headers }),
  ]);
  const debug = await debugResponse.json();
  const state = await stateResponse.json();

  els.nodePill.textContent = `Node: ${debug.node_id}`;
  els.nodeCount.textContent = String(debug.node_count ?? 0);
  els.peerCount.textContent = `${(debug.peers ?? []).length} peers configured`;
  els.snapshotSize.textContent = String(debug.snapshot_size ?? 0);
  els.lastSync.textContent = formatTime(debug.last_sync?.received_at);
  els.lastSource.textContent = debug.last_sync?.source_node_id
    ? `Received from ${debug.last_sync.source_node_id}`
    : "No gossip envelope received yet";
  renderPeers(debug.peers ?? [], Boolean(debug.gossip_enabled));
  els.snapshotJson.textContent = JSON.stringify(state.snapshot ?? {}, null, 2);
}

async function probeRateLimit() {
  const token = getStoredToken();
  const headers = token ? { Authorization: `Bearer ${token}` } : {};

  els.probeStatus.textContent = "Sending...";

  const response = await fetch(probeUrl, { headers });
  const body = await response.json();
  const limit = response.headers.get("X-RateLimit-Limit") ?? "-";
  const current = response.headers.get("X-RateLimit-Current") ?? "-";

  els.probeStatus.textContent = response.ok ? "Accepted" : `HTTP ${response.status}`;
  els.probeLimit.textContent = limit;
  els.probeCurrent.textContent = current;
  els.probeDetail.textContent = JSON.stringify(
    {
      request: probeUrl,
      authorization: token ? "jwt sent" : "anonymous request",
      response: body,
    },
    null,
    2,
  );
}

async function unlockDashboard() {
  const username = els.gateUsername.value.trim();
  const password = els.gatePassword.value;

  if (!username || !password) {
    els.gateStatus.textContent = "Username and password required";
    return;
  }

  els.gateStatus.textContent = "Logging in...";

  const body = new URLSearchParams();
  body.set("username", username);
  body.set("password", password);

  const tokenResponse = await fetch(authTokenUrl, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });

  if (!tokenResponse.ok) {
    setStoredToken("");
    els.gateStatus.textContent = "Invalid username or password";
    return;
  }

  const { access_token: token } = await tokenResponse.json();

  const response = await fetch(authMeUrl, {
    headers: { Authorization: `Bearer ${token}` },
  });

  if (!response.ok) {
    setStoredToken("");
    els.gateStatus.textContent = "Login failed";
    return;
  }

  const user = await response.json();
  if (user.role !== "admin") {
    setStoredToken("");
    els.gateStatus.textContent = "Admin only";
    return;
  }

  setStoredToken(token);
  showDashboard();
  els.gateStatus.textContent = "Access granted";
  await refreshDashboard();
}

els.gateEnter.addEventListener("click", unlockDashboard);
els.probeButton.addEventListener("click", probeRateLimit);
els.refreshButton.addEventListener("click", refreshDashboard);

const storedToken = getStoredToken();
if (storedToken) {
  fetch(authMeUrl, {
    headers: { Authorization: `Bearer ${storedToken}` },
  })
    .then(async (response) => {
      if (!response.ok) {
        throw new Error("Token rejected");
      }

      const user = await response.json();
      if (user.role !== "admin") {
        throw new Error("Admin only");
      }

      showDashboard();
      await refreshDashboard();
    })
    .catch(() => {
      setStoredToken("");
      showGate("Admin login required");
    });
} else {
  showGate("Admin login required");
}

setInterval(() => {
  if (getStoredToken()) {
    refreshDashboard().catch(() => {});
  }
}, 5000);
