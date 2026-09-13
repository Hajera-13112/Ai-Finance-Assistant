// Base URL of the FastAPI backend. Change this if you deploy the API elsewhere.
const API_BASE = "http://127.0.0.1:8000";

const Auth = {
  getToken() {
    return localStorage.getItem("afa_token");
  },
  setSession(token, user) {
    localStorage.setItem("afa_token", token);
    localStorage.setItem("afa_user", JSON.stringify(user));
  },
  getUser() {
    const raw = localStorage.getItem("afa_user");
    return raw ? JSON.parse(raw) : null;
  },
  clear() {
    localStorage.removeItem("afa_token");
    localStorage.removeItem("afa_user");
  },
  requireAuth() {
    if (!this.getToken()) {
      window.location.href = "index.html";
    }
  },
};

async function apiRequest(path, { method = "GET", body = null, auth = true } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (auth) {
    const token = Auth.getToken();
    if (!token) {
      window.location.href = "index.html";
      return;
    }
    headers["Authorization"] = `Bearer ${token}`;
  }

  let response;
  try {
    response = await fetch(`${API_BASE}${path}`, {
      method,
      headers,
      body: body ? JSON.stringify(body) : null,
    });
  } catch (err) {
    throw new Error(
      "Could not reach the API server. Make sure the backend is running at " + API_BASE
    );
  }

  if (response.status === 401) {
    Auth.clear();
    window.location.href = "index.html";
    return;
  }

  if (response.status === 204) return null;

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    const message = Array.isArray(data.detail)
      ? data.detail.map((d) => d.msg).join(", ")
      : data.detail || "Something went wrong.";
    throw new Error(message);
  }

  return data;
}

function showToast(message, isError = false) {
  let toast = document.querySelector(".toast");
  if (!toast) {
    toast = document.createElement("div");
    toast.className = "toast";
    document.body.appendChild(toast);
  }
  toast.textContent = message;
  toast.classList.toggle("error", isError);
  toast.classList.add("show");
  clearTimeout(toast._timer);
  toast._timer = setTimeout(() => toast.classList.remove("show"), 3200);
}

function formatCurrency(value) {
  const num = Number(value || 0);
  return "\u20b9" + num.toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function formatDate(isoDate) {
  const d = new Date(isoDate);
  return d.toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" });
}
