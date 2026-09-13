const monthInput = document.getElementById("budget-month");
monthInput.value = new Date().toISOString().slice(0, 7);

loadBudgets();

document.getElementById("budget-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const month = monthInput.value;
  const category = document.getElementById("budget-category").value || null;
  const limit_amount = parseFloat(document.getElementById("budget-limit").value);

  try {
    await apiRequest("/budgets", { method: "POST", body: { month, category, limit_amount } });
    showToast("Budget saved.");
    document.getElementById("budget-form").reset();
    monthInput.value = new Date().toISOString().slice(0, 7);
    loadBudgets();
  } catch (err) {
    showToast(err.message, true);
  }
});

async function loadBudgets() {
  const listEl = document.getElementById("budget-list");
  listEl.innerHTML = '<div class="empty-note">Loading…</div>';

  const month = new Date().toISOString().slice(0, 7);
  try {
    const budgets = await apiRequest(`/budgets?month=${month}`);
    if (!budgets || budgets.length === 0) {
      listEl.innerHTML = '<div class="empty-note">No budgets set for this month yet.</div>';
      return;
    }
    listEl.innerHTML = budgets.map(renderBudget).join("");

    document.querySelectorAll("[data-delete-budget]").forEach((btn) => {
      btn.addEventListener("click", () => deleteBudget(btn.dataset.deleteBudget));
    });
  } catch (err) {
    listEl.innerHTML = `<div class="empty-note">${err.message}</div>`;
  }
}

function renderBudget(b) {
  const pct = Math.min(b.percent_used, 100);
  const statusText =
    b.status === "exceeded"
      ? `Exceeded by ${formatCurrency(b.spent - b.limit_amount)}`
      : b.status === "warning"
      ? `${Math.round(b.percent_used)}% used — approaching the limit`
      : "";

  return `
    <div class="budget-item">
      <div class="budget-top">
        <span class="name">${b.category || "Overall"}</span>
        <span class="figures">${formatCurrency(b.spent)} of ${formatCurrency(b.limit_amount)}</span>
      </div>
      <div class="budget-track">
        <div class="budget-fill ${b.status}" style="width:${pct}%"></div>
      </div>
      ${statusText ? `<div class="budget-status-note ${b.status}">${statusText}</div>` : ""}
      <div style="margin-top:8px;">
        <button class="btn-danger" data-delete-budget="${b.budget_id}">Remove</button>
      </div>
    </div>`;
}

async function deleteBudget(id) {
  if (!confirm("Remove this budget?")) return;
  try {
    await apiRequest(`/budgets/${id}`, { method: "DELETE" });
    showToast("Budget removed.");
    loadBudgets();
  } catch (err) {
    showToast(err.message, true);
  }
}
