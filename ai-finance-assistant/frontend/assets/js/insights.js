(async function () {
  const listEl = document.getElementById("insights-list");
  try {
    const data = await apiRequest("/insights");
    listEl.innerHTML = data.insights.map((text) => `<div class="insight-card">${text}</div>`).join("");
    document.getElementById("disclaimer-text").textContent = data.disclaimer;
  } catch (err) {
    listEl.innerHTML = `<div class="empty-note">${err.message}</div>`;
  }
})();
