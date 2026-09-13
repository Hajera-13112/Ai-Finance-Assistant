# AI Finance Assistant

A beginner-friendly personal finance web app with AI-based expense categorization,
budget tracking, dashboards, spending forecasts, and rule-based financial insights —
built from the accompanying Software Requirements Specification.

**Stack:** FastAPI (backend) · local JSON file (storage) · scikit-learn (ML) · plain HTML/CSS/JS (frontend)

This is an educational/portfolio project. It does not provide professional
investment, tax, or financial advice.

---

## 1. Project structure

```
ai-finance-assistant/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI app + router wiring
│   │   ├── config.py          # env-based configuration
│   │   ├── storage.py         # JSON file storage engine (no DB server needed)
│   │   ├── schemas.py         # Pydantic request/response models
│   │   ├── security.py        # password hashing + JWT
│   │   ├── deps.py            # auth dependency
│   │   ├── utils.py           # budget/date aggregation helpers
│   │   ├── ml/
│   │   │   ├── classifier.py      # TF-IDF + Logistic Regression expense classifier
│   │   │   ├── forecast.py        # linear-regression spending forecast
│   │   │   └── insights_engine.py # rule-based insights
│   │   ├── chatbot.py          # rule-based finance chatbot (intent matching)
│   │   └── routers/
│   │       ├── auth.py, transactions.py, budgets.py, predict.py, dashboard.py, insights.py, chatbot.py
│   ├── data/
│   │   ├── generate_dataset.py     # regenerates the sample dataset (optional)
│   │   └── sample_transactions.csv # training data for the classifier
│   ├── data_store/              # created automatically -- holds db.json (all app data)
│   ├── models_store/            # trained model files (already included)
│   ├── train_model.py           # trains + saves the classifier
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── index.html               # login / register
    ├── dashboard.html
    ├── transactions.html
    ├── budgets.html
    ├── insights.html
    ├── chatbot.html
    └── assets/
        ├── css/style.css
        └── js/ (api.js, auth.js, nav.js, dashboard.js, transactions.js, budgets.js, insights.js, chatbot.js)
```

---

## 2. Prerequisites

- Python 3.10+
- A modern browser
- **No database server required.** All data (users, transactions, budgets,
  predictions, insights) is stored in a single JSON file at
  `backend/data_store/db.json`, created automatically the first time the
  server starts.

---

## 3. Backend setup

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
```

Open `.env` and set `JWT_SECRET_KEY` to a random string (used to sign login
tokens). Generate one with:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Train the ML expense classifier

A trained model is already included in `models_store/`, so this step is
optional. Retrain any time with:

```bash
python train_model.py
```

This trains a TF-IDF + Logistic Regression model on `data/sample_transactions.csv`
and prints accuracy, precision, recall, F1, and a confusion matrix (SRS 11.3).
To train on your own data instead:

```bash
python train_model.py path/to/your_transactions.csv
```

The CSV needs at least `description` and `category` columns.

### Run the API

```bash
uvicorn app.main:app --reload --port 8000
```

- API docs (interactive): http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health

---

## 4. Frontend setup

The frontend is static HTML/CSS/JS — no build step. Serve it with any static
file server so the browser doesn't hit `file://` CORS issues:

```bash
cd frontend
python -m http.server 8080
```

Then open **http://127.0.0.1:8080** in your browser.

If you run the backend on a different host/port, update `API_BASE` at the top
of `frontend/assets/js/api.js`.

---

## 5. Using the app

1. Register a new account, then sign in.
2. Add a few transactions on the **Transactions** page. Leave the category
   blank on an expense (e.g. "swiggy dinner 450") and the AI model will
   predict a category automatically — the UI shows the prediction and its
   confidence.
3. Set a monthly budget (overall or per category) on the **Budgets** page.
4. Check the **Dashboard** for balance, category breakdown, a monthly trend
   chart, and a next-month spending estimate.
5. Visit **Insights** for rule-based observations (high-spend categories,
   month-over-month changes, budget warnings, savings rate).
6. Try the **Chatbot** page for quick questions like "what's my balance?",
   "what's my budget status?", "give me an insight", or "how do I add a
   transaction?" -- it answers using your own data plus a small set of
   how-to explanations (SRS System Module 8).

---

## 6. About the JSON storage

`backend/app/storage.py` implements a small file-based store: the whole
`db.json` file is loaded, mutated, and rewritten atomically for every
request, guarded by a process-wide lock so concurrent requests don't corrupt
the file. This makes the project trivial to run (no server to install,
no schema migrations) and is well-suited to a single-user demo or fresher
portfolio project.

It intentionally trades away things a real database gives you:
- No indexing — every query scans the relevant list in memory.
- No safe concurrent writers across multiple processes (fine for the single
  `uvicorn` dev process this project runs).
- The whole file is rewritten on every write, which won't scale to a large
  number of transactions.

If you want to go further, the SRS lists MySQL, PostgreSQL, or MongoDB as
production-ready alternatives — swapping `storage.py` for a real database
layer (e.g. SQLAlchemy + MySQL) would be a natural next step and wouldn't
require changing any router logic beyond how `json_db()` is called.

To reset all data, stop the server and delete `backend/data_store/db.json` —
it will be recreated empty on the next startup.

---

## 7. API reference

| Method | Path | Description |
|---|---|---|
| POST | `/register` | Create a user account |
| POST | `/login` | Authenticate, returns a JWT |
| GET | `/me` | Current user profile |
| POST | `/transactions` | Add a transaction (auto-categorized if expense + no category) |
| GET | `/transactions` | List/filter transactions (`type`, `category`, `search`, `start_date`, `end_date`) |
| PUT | `/transactions/{id}` | Update a transaction |
| DELETE | `/transactions/{id}` | Delete a transaction |
| POST | `/predict-category` | Predict a category for a raw description |
| GET | `/dashboard` | Income/expense totals, category breakdown, monthly trend, forecast |
| POST | `/budgets` | Create a budget (overall or category-scoped, per month) |
| GET | `/budgets` | List budgets with computed usage |
| DELETE | `/budgets/{id}` | Remove a budget |
| GET | `/insights` | Rule-based financial insights for the current month |
| POST | `/chatbot` | Ask a question; answers use your own data + how-to guidance |

All endpoints except `/register` and `/login` require `Authorization: Bearer <token>`.

---

## 8. Notes on scope (matches SRS sections 5 & 26)

- Out of scope, as specified: real-time trading, professional investment advice,
  production banking integrations, loan decisions, tax filing, automatic transfers.
- ML predictions depend on training data quality/quantity; the bundled dataset is
  synthetic and meant as a starting point — swap in real (anonymized) data for
  better real-world accuracy.
- Forecasts are estimates, not guarantees, and degrade gracefully with limited history.
