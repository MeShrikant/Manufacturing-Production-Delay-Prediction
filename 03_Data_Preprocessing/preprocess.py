"""Cleaning, target creation, feature engineering and sklearn preprocessing pipelines.
Run:  python 03_Data_Preprocessing/preprocess.py"""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np, pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
import config as C
from data_validation import validate


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Ratios built only from inputs (never from the target). Safe for inference."""
    df = df.copy()
    shift_sec = df["shift_duration_minutes"] * 60
    df["planned_load_ratio"] = df["planned_production_quantity"] * df["takt_time_seconds"] / shift_sec
    if "actual_cycle_time_avg_seconds" in df:
        df["cycle_time_ratio"] = df["actual_cycle_time_avg_seconds"] / df["designed_cycle_time_seconds"]
    if "downtime_unplanned_minutes" in df:
        df["downtime_share"] = df["downtime_unplanned_minutes"] / df["shift_duration_minutes"]
    if "operator_headcount_actual" in df:
        df["headcount_ratio"] = df["operator_headcount_actual"] / df["operator_headcount_planned"].clip(lower=1)
    return df


def risk_from_achievement(a: float) -> str:
    return "High" if a < C.HIGH_RISK_BELOW else ("Medium" if a < C.MEDIUM_RISK_BELOW else "Low")


def add_targets(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["achievement_pct"] = df["actual_production_quantity"] / df["planned_production_quantity"] * 100
    df["delay_risk"] = df["achievement_pct"].map(risk_from_achievement)
    return df


def clean(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    required = ["shift_date", "planned_production_quantity", "actual_production_quantity"] + \
               C.CATEGORICAL + [c for c in C.FEATURE_SETS["shift"]["numeric"]
                                if c not in ("planned_load_ratio", "cycle_time_ratio", "downtime_share", "headcount_ratio")]
    rep = validate(raw, required)
    if not rep["valid"]:
        raise ValueError("; ".join(rep["errors"]))
    df = raw.drop_duplicates().copy()
    rep["rows_after_dedup"] = len(df)
    df["shift_date"] = pd.to_datetime(df["shift_date"], errors="coerce")
    before = len(df)
    df = df.dropna(subset=["shift_date", "planned_production_quantity", "actual_production_quantity"])
    ok = (df["planned_production_quantity"] > 0) & (df["shift_duration_minutes"] > 0) & \
         (df["takt_time_seconds"] > 0) & (df["designed_cycle_time_seconds"] > 0) & \
         (df["actual_production_quantity"] >= 0)
    df = df[ok]
    rep["rows_dropped_invalid"] = before - len(df)
    df = add_targets(engineer_features(df)).sort_values("shift_date").reset_index(drop=True)
    rep["rows_clean"] = len(df)
    rep["target_distribution"] = df["delay_risk"].value_counts().to_dict()
    return df, rep


def build_preprocessor(mode: str) -> ColumnTransformer:
    fs = C.FEATURE_SETS[mode]
    num = Pipeline([("imp", SimpleImputer(strategy="median")), ("sc", StandardScaler())])
    cat = Pipeline([("imp", SimpleImputer(strategy="most_frequent")),
                    ("oh", OneHotEncoder(handle_unknown="ignore", sparse_output=False))])
    return ColumnTransformer([("num", num, fs["numeric"]), ("cat", cat, fs["categorical"])])


def chronological_split(df: pd.DataFrame, train=0.70, val=0.15):
    """Time-ordered split by shift_date: oldest 70% train, next 15% validation, newest 15% test."""
    df = df.sort_values("shift_date").reset_index(drop=True)
    a, b = int(len(df) * train), int(len(df) * (train + val))
    return df.iloc[:a], df.iloc[a:b], df.iloc[b:]


def main():
    C.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    raw = pd.read_csv(C.RAW_FILE)
    df, rep = clean(raw)
    df.to_csv(C.CLEAN_FILE, index=False)
    tr, va, te = chronological_split(df)
    for name, part in (("train", tr), ("validation", va), ("test", te)):
        part.to_csv(C.PROCESSED_DIR / f"{name}.csv", index=False)
    rep["split_rows"] = {"train": len(tr), "validation": len(va), "test": len(te)}
    rep["split_date_ranges"] = {n: [str(p.shift_date.min().date()), str(p.shift_date.max().date())]
                                for n, p in (("train", tr), ("validation", va), ("test", te))}
    json.dump(rep, open(C.PROCESSED_DIR / "preprocessing_report.json", "w"), indent=2, default=str)
    print(json.dumps(rep, indent=2, default=str))
    # sample file for quick UI/API testing: 200 rows from the test period, columns needed by the shift model
    keep = ["line_id", "shift_date"] + C.CATEGORICAL + [c for c in C.FEATURE_SETS["shift"]["numeric"]
            if c not in ("planned_load_ratio", "cycle_time_ratio", "downtime_share", "headcount_ratio")]
    te.sample(200, random_state=1)[keep].to_csv(C.SAMPLE_FILE, index=False)
    print("sample_data.csv written")


if __name__ == "__main__":
    main()
