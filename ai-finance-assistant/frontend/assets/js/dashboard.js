(async function () {
  try {
    const data = await apiRequest("/dashboard");

    document.getElementById("balance-amount").textContent = formatCurrency(data.balance);
    document.getElementById("total-income").textContent = formatCurrency(data.total_income);
    document.getElementById("total-expense").textContent = formatCurrency(data.total_expense);

    renderCategoryBreakdown(data.category_breakdown);
    renderTrendChart(data.monthly_trend);
    renderForecast(data.forecast_next_month, data.forecast_note);
  } catch (err) {
    showToast(err.message, true);
  }
})();

function renderCategoryBreakdown(categories) {
  const container = document.getElementById("category-breakdown");
  if (!categories || categories.length === 0) {
    container.innerHTML = '<div class="empty-note">No expenses recorded yet.</div>';
    return;
  }
  const max = Math.max(...categories.map((c) => c.total));
  container.innerHTML = categories
    .map((c) => {
      const pct = max > 0 ? Math.round((c.total / max) * 100) : 0;
      return `
        <div class="cat-row">
          <div>${c.category}</div>
          <div class="cat-bar-track"><div class="cat-bar-fill" style="width:${pct}%"></div></div>
          <div class="cat-amount">${formatCurrency(c.total)}</div>
        </div>`;
    })
    .join("");
}

function renderTrendChart(monthlyTrend) {
  const canvas = document.getElementById("trend-chart");
  if (!monthlyTrend || monthlyTrend.length === 0) {
    canvas.replaceWith(Object.assign(document.createElement("div"), {
      className: "empty-note",
      textContent: "Add a few transactions to see your monthly trend.",
    }));
    return;
  }

  const labels = monthlyTrend.map((m) => m.month);
  const income = monthlyTrend.map((m) => m.income);
  const expense = monthlyTrend.map((m) => m.expense);

  new Chart(canvas, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "Income",
          data: income,
          borderColor: "#2F6F5E",
          backgroundColor: "rgba(47,111,94,0.08)",
          tension: 0.25,
          fill: true,
        },
        {
          label: "Expense",
          data: expense,
          borderColor: "#B1502F",
          backgroundColor: "rgba(177,80,47,0.08)",
          tension: 0.25,
          fill: true,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: { position: "bottom", labels: { boxWidth: 10, font: { family: "Inter", size: 12 } } },
      },
      scales: {
        x: { grid: { display: false }, ticks: { font: { family: "Inter", size: 11 } } },
        y: { grid: { color: "#D9D0BC" }, ticks: { font: { family: "Inter", size: 11 } } },
      },
    },
  });
}

function renderForecast(value, note) {
  const amountEl = document.getElementById("forecast-amount");
  const noteEl = document.getElementById("forecast-note");
  amountEl.textContent = value === null || value === undefined ? "Not enough data" : formatCurrency(value);
  noteEl.textContent = note || "";
}
