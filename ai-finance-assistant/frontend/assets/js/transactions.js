document.getElementById("tx-date").valueAsDate = new Date();

loadTransactions();

document.getElementById("tx-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const date = document.getElementById("tx-date").value;
  const description = document.getElementById("tx-description").value.trim();
  const amount = parseFloat(document.getElementById("tx-amount").value);
  const type = document.getElementById("tx-type").value;
  const category = document.getElementById("tx-category").value || null;

  try {
    const tx = await apiRequest("/transactions", {
      method: "POST",
      body: { date, description, amount, type, category },
    });
    const note = tx.predicted_category
      ? `Added — AI categorized this as "${tx.predicted_category}" (${Math.round(tx.confidence * 100)}% confidence).`
      : "Transaction added.";
    showToast(note);
    document.getElementById("tx-form").reset();
    document.getElementById("tx-date").valueAsDate = new Date();
    loadTransactions();
  } catch (err) {
    showToast(err.message, true);
  }
});

document.getElementById("filter-apply").addEventListener("click", () => loadTransactions());

async function loadTransactions() {
  const type = document.getElementById("filter-type").value;
  const search = document.getElementById("filter-search").value.trim();

  const params = new URLSearchParams();
  if (type) params.set("type", type);
  if (search) params.set("search", search);

  const tbody = document.getElementById("tx-table-body");
  tbody.innerHTML = '<tr><td colspan="5" class="empty-note">Loading…</td></tr>';

  try {
    const transactions = await apiRequest(`/transactions?${params.toString()}`);
    if (!transactions || transactions.length === 0) {
      tbody.innerHTML = '<tr><td colspan="5" class="empty-note">No transactions yet. Add your first one above.</td></tr>';
      return;
    }

    tbody.innerHTML = transactions.map(renderRow).join("");

    document.querySelectorAll("[data-delete-id]").forEach((btn) => {
      btn.addEventListener("click", () => deleteTransaction(btn.dataset.deleteId));
    });
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="5" class="empty-note">${err.message}</td></tr>`;
  }
}

function renderRow(tx) {
  const isExpense = tx.type === "expense";
  const sign = isExpense ? "\u2212" : "+";
  const confidenceNote =
    tx.predicted_category && tx.category === tx.predicted_category
      ? `<div class="confidence-note">AI-predicted \u00b7 ${Math.round(tx.confidence * 100)}% confidence</div>`
      : "";

  return `
    <tr>
      <td>${formatDate(tx.date)}</td>
      <td>${escapeHtml(tx.description)}</td>
      <td>
        <span class="tag ${tx.category === "Other" ? "other" : ""}">${tx.category || "—"}</span>
        ${confidenceNote}
      </td>
      <td class="amount-cell ${isExpense ? "expense" : "income"}">${sign} ${formatCurrency(tx.amount)}</td>
      <td class="row-actions">
        <button class="btn-danger" data-delete-id="${tx.transaction_id}">Delete</button>
      </td>
    </tr>`;
}

async function deleteTransaction(id) {
  if (!confirm("Delete this transaction?")) return;
  try {
    await apiRequest(`/transactions/${id}`, { method: "DELETE" });
    showToast("Transaction deleted.");
    loadTransactions();
  } catch (err) {
    showToast(err.message, true);
  }
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}
