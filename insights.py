import pandas as pd
from typing import Dict, Any
import numpy as np

def _safe_num(x):
    try:
        return float(x)
    except Exception:
        return None

def basic_profile(df: pd.DataFrame) -> Dict[str, Any]:
    profile = {
        "row_count": int(df.shape[0]),
        "col_count": int(df.shape[1]),
        "columns": [],
    }
    for c in df.columns:
        col = df[c]
        dtype = str(col.dtype)
        non_null = int(col.notna().sum())
        nulls = int(col.isna().sum())
        sample = col.dropna().astype(str).head(3).tolist()
        profile["columns"].append({
            "name": c,
            "dtype": dtype,
            "non_null": non_null,
            "nulls": nulls,
            "sample_values": sample
        })
    return profile

def guess_semantics(df: pd.DataFrame) -> Dict[str, str]:
    mapping = {}
    for c in df.columns:
        lc = c.lower()
        if any(k in lc for k in ["date", "dt", "month", "created", "signup"]):
            mapping[c] = "date"
        elif any(k in lc for k in ["rev", "mrr", "arr", "revenue", "gmv", "sales"]):
            mapping[c] = "currency"
        elif any(k in lc for k in ["churn", "cancel", "drop"]):
            mapping[c] = "percentage"
        elif any(k in lc for k in ["user", "customer", "account", "id"]):
            mapping[c] = "dimension"
        else:
            # numeric/dimension guess
            mapping[c] = "measure" if pd.api.types.is_numeric_dtype(df[c]) else "dimension"
    return mapping

def recommend_visuals(df: pd.DataFrame) -> Dict[str, Any]:
    semantics = guess_semantics(df)
    visuals = []

    date_cols = [c for c, t in semantics.items() if t == "date"]
    measure_cols = [c for c, t in semantics.items() if t in ("currency","measure","percentage")]
    dim_cols = [c for c, t in semantics.items() if t == "dimension"]

    # Time series if we have a date column
    if date_cols and measure_cols:
        visuals.append({
            "title": "Trend Over Time",
            "type": "line",
            "x": date_cols[0],
            "y": measure_cols[:3],
            "why": "Shows growth/decline across time for key measures."
        })

    # Top categories
    if dim_cols and measure_cols:
        visuals.append({
            "title": "Top Categories",
            "type": "bar",
            "x": dim_cols[0],
            "y": measure_cols[0],
            "agg": "sum",
            "why": "Ranks top contributing categories (customers, plans, regions)."
        })

    # Cohort-like suggestion if any signup/date + retention-like column exists
    if any("signup" in c.lower() for c in df.columns) and any("active" in c.lower() or "retention" in c.lower() for c in df.columns):
        visuals.append({
            "title": "Retention by Signup Cohort",
            "type": "heatmap",
            "x": "signup_month",
            "y": "cohort_month",
            "value": "retention_rate",
            "why": "Highlights user retention patterns."
        })

    return {"semantics": semantics, "visuals": visuals}

def generate_insights(df: pd.DataFrame) -> Dict[str, Any]:
    # Very light heuristic demo insights
    insights = []
    numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    date_cols = [c for c in df.columns if "date" in c.lower() or "month" in c.lower()]

    # Detect spike/drop in the first numeric column
    if numeric_cols:
        c = numeric_cols[0]
        series = df[c].dropna().astype(float)
        if len(series) >= 3:
            last = series.iloc[-1]
            prev = series.iloc[-2]
            change = (last - prev) / (abs(prev) + 1e-9) * 100.0
            if change > 15:
                insights.append(f"{c}: Significant uptick of {change:.1f}% in the latest period.")
            elif change < -15:
                insights.append(f"{c}: Significant drop of {change:.1f}% in the latest period.")
            else:
                insights.append(f"{c}: Stable trend (Δ {change:.1f}%).")

    # Generic suggestions
    insights.extend([
        "Consider tracking MRR, churn %, ARPU, and cohort retention if applicable.",
        "Add segmentation by plan/tier to spot high-ARPU cohorts.",
        "Investigate onboarding flow if churn increased while signups are steady."
    ])
    return {"insights": insights}

def powerbi_spec(df: pd.DataFrame) -> Dict[str, Any]:
    # Provide suggested visuals and common DAX formulas
    dax = {
        "MRR": "MRR = SUM('Table'[MRR])",
        "ARR": "ARR = [MRR] * 12",
        "Churn %": "Churn % = DIVIDE(SUM('Table'[ChurnCount]), SUM('Table'[CustomersPrevMonth]))",
        "ARPU": "ARPU = DIVIDE(SUM('Table'[Revenue]), SUM('Table'[ActiveUsers]))",
        "MoM Growth %": "MoM Growth % = DIVIDE([MRR] - CALCULATE([MRR], DATEADD('Calendar'[Date], -1, MONTH)), CALCULATE([MRR], DATEADD('Calendar'[Date], -1, MONTH)))"
    }
    visuals = recommend_visuals(df)["visuals"]
    return {"powerbi": {"dax": dax, "visuals": visuals}}

def generate_dashboard_spec_and_insights(df: pd.DataFrame):
    profile = basic_profile(df)
    visuals = recommend_visuals(df)
    insights = generate_insights(df)
    pbi = powerbi_spec(df)
    return {
        "profile": profile,
        "dashboard_spec": visuals,
        **insights,
        **pbi
    }
