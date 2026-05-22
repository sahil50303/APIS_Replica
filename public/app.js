// State tracking
let activeKeys = [];
let replicatedAnnouncements = [];

// Page headers definitions
const headersConfig = {
    dashboard: { title: "Dashboard Overview", subtitle: "Monitor and manage your API replication status in real-time." },
    keys: { title: "API Authentication Keys", subtitle: "Generate, inspect, and revoke API access keys." },
    docs: { title: "API Endpoint Reference", subtitle: "Detailed instructions and curl commands to replicate client payloads." },
    logs: { title: "Replicated Database Logs", subtitle: "Inspect records successfully synced from clients to Supabase." }
};

// Initialize Dashboard on DOM Load
document.addEventListener("DOMContentLoaded", () => {
    loadAllData();
    // Default curl setup
    updateCurlCommand();
});

// Load everything from the backend API
async function loadAllData() {
    await Promise.all([
        fetchApiKeys(),
        fetchAnnouncements()
    ]);
    updateStats();
}

// Switch between Sidebar Navigation Tabs
function switchTab(tabId) {
    // Update menu items selection
    document.querySelectorAll(".nav-item").forEach(item => {
        item.classList.remove("active");
    });
    
    // Find active nav item and select it
    const activeNav = Array.from(document.querySelectorAll(".nav-item")).find(btn => 
        btn.textContent.toLowerCase().includes(tabId === "docs" ? "reference" : tabId)
    );
    if (activeNav) activeNav.classList.add("active");

    // Update main pane displays
    document.querySelectorAll(".tab-pane").forEach(pane => {
        pane.classList.remove("active");
    });
    const selectedPane = document.getElementById(`tab-${tabId}`);
    if (selectedPane) selectedPane.classList.add("active");

    // Update titles
    const config = headersConfig[tabId];
    if (config) {
        document.getElementById("page-title").textContent = config.title;
        document.getElementById("page-subtitle").textContent = config.subtitle;
    }

    // Refresh data depending on tab
    if (tabId === "keys") {
        fetchApiKeys();
    } else if (tabId === "logs" || tabId === "dashboard") {
        fetchAnnouncements();
    }
}

// ---------------------------------------------------------
// API Key Operations
// ---------------------------------------------------------
async function fetchApiKeys() {
    try {
        const response = await fetch("/api/keys");
        if (!response.ok) throw new Error("Failed to load API keys.");
        
        activeKeys = await response.json();
        renderKeysTable();
        populateKeyDropdown();
    } catch (err) {
        console.error("Error loading keys:", err);
        showToast("Error loading API keys. Is server running?");
    }
}

function renderKeysTable() {
    const tbody = document.getElementById("keys-tbody");
    if (!tbody) return;

    if (activeKeys.length === 0) {
        tbody.innerHTML = `<tr><td colspan="4" class="empty-placeholder">No active API keys found. Generate one below!</td></tr>`;
        return;
    }

    tbody.innerHTML = activeKeys.map(key => {
        const formattedDate = new Date(key.created_at).toLocaleString();
        return `
            <tr>
                <td><strong>${escapeHtml(key.key_name)}</strong></td>
                <td class="code-cell">${key.key_value}</td>
                <td>${formattedDate}</td>
                <td>
                    <button class="btn btn-danger btn-copy" style="padding: 0.35rem 0.75rem;" onclick="revokeKey('${key.id}', '${escapeHtml(key.key_name)}')">
                        <i class="fa-solid fa-trash-can"></i> Revoke
                    </button>
                </td>
            </tr>
        `;
    }).join("");
}

function populateKeyDropdown() {
    const select = document.getElementById("curl-key-select");
    if (!select) return;

    // Keep initial option
    select.innerHTML = '<option value="YOUR_API_KEY_HERE">Select a key to populate curl</option>';
    
    activeKeys.forEach(key => {
        const opt = document.createElement("option");
        // We put a placeholder if we display, but we can store the ID or name. 
        // We'll query if they want to copy, or store the fake masked one. 
        // For developer convenience, since key_value in list is masked, 
        // we will let them select the key name, and we'll keep a reference.
        opt.value = key.id;
        opt.textContent = `${key.key_name} (${key.key_value})`;
        select.appendChild(opt);
    });
}

async function generateApiKey(event) {
    event.preventDefault();
    const input = document.getElementById("key-name-input");
    const name = input.value.trim();
    if (!name) return;

    try {
        const response = await fetch("/api/keys", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ key_name: name })
        });

        if (!response.ok) throw new Error("Could not generate key");
        const keyData = await response.json();

        // Display new key alert
        const alertBox = document.getElementById("new-key-alert");
        const valueBox = document.getElementById("new-key-value");
        valueBox.textContent = keyData.key_value;
        alertBox.style.display = "block";

        input.value = "";
        
        // Reload keys list
        await fetchApiKeys();
        updateStats();
        
        showToast("Key generated successfully!");
        alertBox.scrollIntoView({ behavior: 'smooth' });
    } catch (err) {
        console.error(err);
        showToast("Error generating key.");
    }
}

async function revokeKey(keyId, keyName) {
    if (!confirm(`Are you sure you want to revoke the key: "${keyName}"?\nRequests using this key will immediately fail.`)) {
        return;
    }

    try {
        const response = await fetch(`/api/keys/${keyId}`, {
            method: "DELETE"
        });

        if (!response.ok) throw new Error("Failed to revoke key");
        
        showToast("Key revoked successfully.");
        await fetchApiKeys();
        updateStats();
    } catch (err) {
        console.error(err);
        showToast("Error revoking key.");
    }
}

// ---------------------------------------------------------
// Announcement / Logs Operations
// ---------------------------------------------------------
async function fetchAnnouncements() {
    try {
        const response = await fetch("/api/announcements");
        if (!response.ok) throw new Error("Failed to load records");
        replicatedAnnouncements = await response.json();
        
        renderLogsTable();
        renderRecentLogs();
    } catch (err) {
        console.error(err);
        showToast("Error fetching synced records.");
    }
}

function renderLogsTable() {
    const tbody = document.getElementById("logs-tbody");
    if (!tbody) return;

    if (replicatedAnnouncements.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" class="empty-placeholder">No announcements captured yet.</td></tr>`;
        return;
    }

    tbody.innerHTML = replicatedAnnouncements.map(ann => {
        const syncDate = new Date(ann.created_at).toLocaleString();
        const purpCount = ann.purposes.length;
        return `
            <tr>
                <td><strong>${ann.id}</strong></td>
                <td>${escapeHtml(ann.announcer_name || "N/A")}</td>
                <td style="color: var(--success); font-weight: 500;">₹${ann.announce_amount.toLocaleString()}</td>
                <td>${escapeHtml(ann.mob_no || "N/A")}</td>
                <td>${syncDate}</td>
                <td>
                    <button class="expand-btn" onclick="openDetailsModal(${ann.id})">
                        ${purpCount} Purpose${purpCount !== 1 ? 's' : ''} <i class="fa-solid fa-up-right-from-square" style="font-size: 0.75rem; margin-left: 2px;"></i>
                    </button>
                </td>
            </tr>
        `;
    }).join("");
}

function renderRecentLogs() {
    const tbody = document.getElementById("recent-logs-tbody");
    if (!tbody) return;

    if (replicatedAnnouncements.length === 0) {
        tbody.innerHTML = `<tr><td colspan="4" class="empty-placeholder">No announcements captured yet.</td></tr>`;
        return;
    }

    // Limit to 5
    const list = replicatedAnnouncements.slice(0, 5);
    tbody.innerHTML = list.map(ann => {
        const syncDate = new Date(ann.created_at).toLocaleDateString();
        return `
            <tr>
                <td><strong>#${ann.id}</strong></td>
                <td>${escapeHtml(ann.announcer_name || "N/A")}</td>
                <td style="color: var(--success);">₹${ann.announce_amount.toLocaleString()}</td>
                <td>${syncDate}</td>
            </tr>
        `;
    }).join("");
}

function updateStats() {
    const countTotal = replicatedAnnouncements.length;
    const countSuccess = replicatedAnnouncements.length; // Assuming successful ones exist in DB
    const countKeys = activeKeys.length;

    document.getElementById("stat-total-sync").textContent = countTotal;
    document.getElementById("stat-success-sync").textContent = countSuccess;
    document.getElementById("stat-active-keys").textContent = countKeys;
}

// ---------------------------------------------------------
// Details Modal Viewer
// ---------------------------------------------------------
function openDetailsModal(annId) {
    const record = replicatedAnnouncements.find(a => a.id === annId);
    if (!record) return;

    const modal = document.getElementById("detail-modal");
    const body = document.getElementById("modal-body-content");
    
    // Construct modal HTML content
    let purposesHtml = "";
    if (record.purposes.length === 0) {
        purposesHtml = "<p>No yojna details provided.</p>";
    } else {
        purposesHtml = `
            <div class="table-container" style="margin-top: 0.5rem;">
                <table>
                    <thead>
                        <tr>
                            <th>Yojna ID</th>
                            <th>Quantity</th>
                            <th>Amount</th>
                            <th>Bhojan Date</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${record.purposes.map(p => `
                            <tr>
                                <td><strong>${escapeHtml(p.yojna_id)}</strong></td>
                                <td>${escapeHtml(p.qty)}</td>
                                <td style="color: var(--success);">₹${p.amount.toLocaleString()}</td>
                                <td>${escapeHtml(p.bhojan_date || "N/A")}</td>
                            </tr>
                        `).join("")}
                    </tbody>
                </table>
            </div>
        `;
    }

    body.innerHTML = `
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-bottom: 2rem;">
            <div>
                <div class="modal-body-section">
                    <h4>Announcer Details</h4>
                    <p style="font-size: 1.1rem; font-weight: 600; color: white;">${escapeHtml(record.announcer_name || "Anonymous")}</p>
                    <p style="color: var(--text-secondary); margin-top: 0.2rem;">Mobile: ${escapeHtml(record.mob_no || "N/A")}</p>
                </div>
                <div class="modal-body-section">
                    <h4>Announced Amount</h4>
                    <p style="font-size: 1.25rem; font-weight: 700; color: var(--success);">₹${record.announce_amount.toLocaleString()}</p>
                </div>
            </div>
            <div>
                <div class="modal-body-section">
                    <h4>Replicated ID (Supabase PK)</h4>
                    <p style="font-family: monospace; font-size: 1.1rem; color: var(--primary); font-weight: bold;">${record.id}</p>
                </div>
                <div class="modal-body-section">
                    <h4>Replication Status</h4>
                    <p><span class="status-badge connected"><span class="dot"></span> Saved to DB</span></p>
                </div>
            </div>
        </div>
        
        <div class="modal-body-section">
            <h4>Annouce Purpose Details (Sub-items)</h4>
            ${purposesHtml}
        </div>
    `;

    modal.classList.add("show");
}

function closeModal() {
    document.getElementById("detail-modal").classList.remove("show");
}

// Close modal when clicking background
window.onclick = function(event) {
    const modal = document.getElementById("detail-modal");
    if (event.target === modal) {
        modal.classList.remove("show");
    }
}

// ---------------------------------------------------------
// Dynamic Curl Command Constructor
// ---------------------------------------------------------
function updateCurlCommand() {
    const select = document.getElementById("curl-key-select");
    const curlCode = document.getElementById("curl-code");
    if (!select || !curlCode) return;

    let keyToUse = select.value;
    
    // If a valid key ID is selected, get the active value
    if (keyToUse !== "YOUR_API_KEY_HERE") {
        const found = activeKeys.find(k => k.id === keyToUse);
        // Note: For display we can't show full key if masked, but since we save it 
        // upon creation, if they just generated a key, they have the full key copied.
        // On selection, we'll request them to use their copied key, or show the preview.
        // Actually, let's make it easy: when they select a key, we'll populate 
        // whatever key value is stored (the preview).
        keyToUse = found ? `NSS-${found.key_value.split("...")[0].substring(4)}...` : "YOUR_API_KEY_HERE";
    }

    const hostUrl = window.location.origin === "null" || !window.location.origin ? "http://127.0.0.1:8000" : window.location.origin;

    curlCode.textContent = `curl --location '${hostUrl}/api/nssapi/ashram/InsertAnnounceCreation' \\
--header 'X-API-Key: ${keyToUse}' \\
--header 'Content-Type: application/json' \\
--data '{
    "annoucePurposeList": [
        {
            "yojna_id": "9",
            "qty": "1",
            "amount": 5000.0,
            "bhojan_date": ""
        }
    ],
    "ashri": "MR.",
    "ashri_oth": "N.A.",
    "announcer_name": "hxxhchchchchc",
    "announce_amount": 5000.0,
    "address1": "hdchfhfhf",
    "address2": "hfhfuf",
    "address3": "",
    "ph_no": 0,
    "mob_no": "70734521314",
    "announce_through": "WHATSAPP",
    "announce_date": null,
    "announce_time": null,
    "std_code": 0,
    "email_id": "",
    "purpose": 0,
    "due_date": "06/11/2025",
    "due_time": "9:30 AM",
    "completed": 0,
    "remark1": "4",
    "first_remark": null,
    "second_remark": null,
    "third_remark": null,
    "city_code": null,
    "district_code": "1597.0",
    "state_code": "68.0",
    "remark2": "fhfhchc",
    "channel_code": 0,
    "pandit_code": 0,
    "bhag_city_code": 0,
    "user_name": "JATAN SINGH",
    "emp_code": 0,
    "live": "N",
    "ash_event_id": "0",
    "event_name": "",
    "user_id": "70",
    "cash_pickup": "N",
    "other_type": 0,
    "currency_id": "4.0",
    "cause_id": 0,
    "ngcode": "0",
    "data_flag": "GANGOTRI",
    "fy_id": "21",
    "dmobilewhatsapp1": "",
    "aadhar_number": "988989898986",
    "pan_number": "FHVJJ3456Q",
    "pincode_code": "76595.0",
    "country_code": "22",
    "pincode": "313001"
}'`;
}

// ---------------------------------------------------------
// Helper Utilities
// ---------------------------------------------------------
function copyToClipboard(elementId) {
    const text = document.getElementById(elementId).textContent;
    
    // Handle the masked key in the curl builder, prompt the user to double check
    if (elementId === "curl-code" && text.includes("...")) {
        // Just extract code and warn, or copy as is
    }

    navigator.clipboard.writeText(text).then(() => {
        showToast("Copied to clipboard!");
    }).catch(err => {
        console.error("Failed to copy text: ", err);
        showToast("Failed to copy. Please highlight and copy manually.");
    });
}

function showToast(message) {
    const toast = document.getElementById("toast");
    const msg = document.getElementById("toast-message");
    if (!toast || !msg) return;

    msg.textContent = message;
    toast.classList.add("show");
    
    setTimeout(() => {
        toast.classList.remove("show");
    }, 2800);
}

function escapeHtml(str) {
    if (!str) return "";
    return str
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
