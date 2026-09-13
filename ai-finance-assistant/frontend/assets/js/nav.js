Auth.requireAuth();

const currentUser = Auth.getUser();
const sidebarUserEl = document.getElementById("sidebar-user");
if (sidebarUserEl && currentUser) {
  sidebarUserEl.textContent = currentUser.name;
}

const greetingEl = document.getElementById("greeting");
if (greetingEl && currentUser) {
  const firstName = currentUser.name.split(" ")[0];
  greetingEl.textContent = `Good to see you, ${firstName}`;
}

const logoutLink = document.getElementById("logout-link");
if (logoutLink) {
  logoutLink.addEventListener("click", (e) => {
    e.preventDefault();
    Auth.clear();
    window.location.href = "index.html";
  });
}
