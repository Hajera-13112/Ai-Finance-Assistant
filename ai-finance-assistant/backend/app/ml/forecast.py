"""
Spending forecast.

Per SRS 11.2: uses historical monthly expense totals and a simple linear
regression (time index -> spend) to estimate next month's spending.
Falls back gracefully when there isn't enough historical data yet (SRS 9.6).
"""
from typing import List, Optional, Tuple

import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error

MIN_MONTHS_FOR_FORECAST = 3


def forecast_next_month(monthly_totals: List[float]) -> Tuple[Optional[float], str]:
    """
    monthly_totals: chronologically ordered list of total expense per month.
    Returns (forecast_value_or_None, human_readable_note).
    """
    n = len(monthly_totals)

    if n == 0:
        return None, "No transaction history yet. Add expenses to unlock a forecast."

    if n < MIN_MONTHS_FOR_FORECAST:
        avg = float(np.mean(monthly_totals))
        return (
            round(avg, 2),
            f"Only {n} month(s) of history available, so this is a simple average "
            f"rather than a trend-based estimate. Add more months of data for a "
            f"more reliable forecast.",
        )

    X = np.arange(n).reshape(-1, 1)
    y = np.array(monthly_totals)

    model = LinearRegression()
    model.fit(X, y)

    next_index = np.array([[n]])
    forecast = float(model.predict(next_index)[0])
    forecast = max(forecast, 0.0)  # spending can't be negative

    y_pred_hist = model.predict(X)
    mae = mean_absolute_error(y, y_pred_hist)
    rmse = mean_squared_error(y, y_pred_hist) ** 0.5

    note = (
        f"Estimated from a linear trend over the last {n} months "
        f"(historical fit MAE \u2248 {mae:.2f}, RMSE \u2248 {rmse:.2f}). "
        f"This is an estimate, not a guaranteed value."
    )
    return round(forecast, 2), note
