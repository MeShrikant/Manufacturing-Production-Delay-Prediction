"""Prediction service shared by the FastAPI backend and the Streamlit UI.
Two modes:
  plan  - pre-shift risk using only planning information
  shift - current-shift estimate (adds downtime / cycle time / headcount / changeover)"""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import joblib, numpy as np, pandas as pd
import config as C
from preprocess import engineer_features
from data_validation import validate

DERIVED = {"planned_load_ratio", "cycle_time_ratio", "downtime_share", "headcount_ratio"}
OUTPUT_LABEL = {"plan": "Pre-shift risk estimate (planning data only)",
                "shift": "Current-shift estimate (uses downtime/cycle-time values for this shift)"}
_cache: dict = {}


class ModelNotReady(RuntimeError):
    pass


def required_columns(mode: str) -> list[str]:
    fs = C.FEATURE_SETS[mode]
    return [c for c in fs["numeric"] + fs["categorical"] if c not in DERIVED]


def models_ready() -> bool:
    return all((C.MODELS_DIR / f).exists() for f in ("production_delay_model.pkl", "preprocessing_pipeline.pkl"))


def load():
    if not _cache:
        if not models_ready():
            raise ModelNotReady("Trained model not found in 05_Models/. Run: python 04_Training/train_model.py")
        _cache["models"] = joblib.load(C.MODELS_DIR / "production_delay_model.pkl")
        _cache["pipes"] = joblib.load(C.MODELS_DIR / "preprocessing_pipeline.pkl")
    return _cache["models"], _cache["pipes"]


def model_info() -> dict:
    meta = json.load(open(C.MODELS_DIR / "model_metadata.json")) if (C.MODELS_DIR / "model_metadata.json").exists() else {}
    metrics = json.load(open(C.RESULTS_DIR / "model_metrics.json")) if (C.RESULTS_DIR / "model_metrics.json").exists() else {}
    return {"metadata": meta, "test_metrics": metrics.get("modes", {}), "metrics_note": metrics.get("note", "")}


def bottleneck_and_action(row: pd.Series, mode: str, risk: str) -> tuple[str, str]:
    """Rule-based explanation computed from the inputs (NOT a machine-level ML prediction)."""
    if mode == "shift":
        dur = float(row["shift_duration_minutes"])
        losses = {
            "High unplanned downtime": float(row["downtime_unplanned_minutes"]) / dur,
            "Long changeovers": float(row["changeover_time_minutes"]) / dur,
            "Cycle time slower than design": max(0.0, 1 - 1 / float(row["cycle_time_ratio"])),
        }
        name, val = max(losses.items(), key=lambda kv: kv[1])
        if val < 0.05:
            reason = "No single dominant loss in the entered data"
            action = "Monitor the shift; no major loss factor found in the inputs." if risk == "Low" else \
                     "Risk is raised but no single input explains it; review quality holds and other losses not captured here."
            return reason, action
        actions = {
            "High unplanned downtime": "Inspect machine downtime causes (mechanical/electrical/tooling) and prepare maintenance support.",
            "Long changeovers": "Reduce changeover time (pre-stage tooling, SMED) or re-sequence jobs.",
            "Cycle time slower than design": "Check line speed settings, minor stops and the slowest station against the designed cycle time.",
        }
        return name, actions[name]
    # plan mode: only planning info is known
    if float(row["planned_load_ratio"]) > 1.2:
        return "Planned quantity is more than 20% above line capacity at takt time", "Reduce the planned quantity or add capacity/overtime for this shift."
    if float(row["equipment_condition_score"]) < 5:
        return "Poor equipment condition", "Schedule inspection or preventive maintenance before the shift."
    return "Not determinable before the shift (no downtime or cycle-time data yet)", \
           "Re-run in 'shift' mode once downtime and cycle-time data are available." if risk != "Low" else "No action needed based on planning data."


def predict_df(df: pd.DataFrame, mode: str = "shift") -> pd.DataFrame:
    if mode not in C.FEATURE_SETS:
        raise ValueError(f"mode must be one of {list(C.FEATURE_SETS)}")
    rep = validate(df, required_columns(mode))
    if not rep["valid"]:
        raise ValueError("; ".join(rep["errors"]) or "Invalid data")
    models, pipes = load()
    d = df.drop_duplicates().copy()
    for c in required_columns(mode):
        if c in C.CATEGORICAL:
            d[c] = d[c].astype(str)
        else:
            d[c] = pd.to_numeric(d[c], errors="coerce")
    bad = d[[c for c in required_columns(mode) if c not in C.CATEGORICAL]].isna().any(axis=1)
    bad |= (d["planned_production_quantity"] <= 0) | (d["shift_duration_minutes"] <= 0) | \
           (d["takt_time_seconds"] <= 0) | (d["designed_cycle_time_seconds"] <= 0)
    if bad.all():
        raise ValueError("All rows contain missing or invalid numeric values.")
    d = engineer_features(d)
    ok = d[~bad]
    cols = C.FEATURE_SETS[mode]["numeric"] + C.FEATURE_SETS[mode]["categorical"]
    X = pipes[mode].transform(ok[cols])
    proba = models[mode]["classifier"].predict_proba(X)
    risk = [C.LABELS[i] for i in proba.argmax(axis=1)]
    ach = np.clip(models[mode]["regressor"].predict(X), 0, 100)
    out = ok.copy()
    out["delay_risk"] = risk
    for i, l in enumerate(C.LABELS):
        out[f"prob_{l.lower()}"] = proba[:, i].round(3)
    out["predicted_target_achievement_pct"] = ach.round(1)
    out["predicted_production_quantity"] = (ach / 100 * ok["planned_production_quantity"]).round(0).astype(int)
    be = [bottleneck_and_action(r, mode, rk) for (_, r), rk in zip(ok.iterrows(), risk)]
    out["possible_bottleneck"] = [b[0] for b in be]
    out["recommended_action"] = [b[1] for b in be]
    out["prediction_type"] = OUTPUT_LABEL[mode]
    out["mode"] = mode
    keep = [c for c in ("line_id", "shift_date") if c in out.columns] + ["planned_production_quantity"]
    res = out[keep + ["delay_risk", "prob_low", "prob_medium", "prob_high", "predicted_target_achievement_pct",
                      "predicted_production_quantity", "possible_bottleneck", "recommended_action", "prediction_type", "mode"]]
    res.attrs["skipped_rows"] = int(bad.sum())
    return res


def predict_one(record: dict, mode: str = "shift") -> dict:
    r = predict_df(pd.DataFrame([record]), mode).iloc[0]
    return {"mode": mode, "prediction_type": r["prediction_type"], "delay_risk": r["delay_risk"],
            "risk_probabilities": {"Low": float(r["prob_low"]), "Medium": float(r["prob_medium"]), "High": float(r["prob_high"])},
            "predicted_production": int(r["predicted_production_quantity"]),
            "target_achievement_percentage": float(r["predicted_target_achievement_pct"]),
            "possible_bottleneck": r["possible_bottleneck"], "recommended_action": r["recommended_action"]}
