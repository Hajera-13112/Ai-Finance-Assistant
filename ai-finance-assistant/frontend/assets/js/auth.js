// If already signed in, skip straight to the dashboard.
if (Auth.getToken()) {
  window.location.href = "dashboard.html";
}

const loginPanel = document.getElementById("login-panel");
const registerPanel = document.getElementById("register-panel");

document.getElementById("show-register").addEventListener("click", (e) => {
  e.preventDefault();
  loginPanel.classList.add("hidden");
  registerPanel.classList.remove("hidden");
});

document.getElementById("show-login").addEventListener("click", (e) => {
  e.preventDefault();
  registerPanel.classList.add("hidden");
  loginPanel.classList.remove("hidden");
});

function setError(elementId, message) {
  const el = document.getElementById(elementId);
  if (!message) {
    el.classList.remove("show");
    el.textContent = "";
    return;
  }
  el.textContent = message;
  el.classList.add("show");
}

document.getElementById("login-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  setError("login-error", "");
  const email = document.getElementById("login-email").value.trim();
  const password = document.getElementById("login-password").value;

  try {
    const data = await apiRequest("/login", {
      method: "POST",
      auth: false,
      body: { email, password },
    });
    Auth.setSession(data.access_token, data.user);
    window.location.href = "dashboard.html";
  } catch (err) {
    setError("login-error", err.message);
  }
});

document.getElementById("register-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  setError("register-error", "");
  const name = document.getElementById("register-name").value.trim();
  const email = document.getElementById("register-email").value.trim();
  const password = document.getElementById("register-password").value;

  try {
    await apiRequest("/register", {
      method: "POST",
      auth: false,
      body: { name, email, password },
    });
    // Auto-login after successful registration.
    const data = await apiRequest("/login", {
      method: "POST",
      auth: false,
      body: { email, password },
    });
    Auth.setSession(data.access_token, data.user);
    window.location.href = "dashboard.html";
  } catch (err) {
    setError("register-error", err.message);
  }
});
