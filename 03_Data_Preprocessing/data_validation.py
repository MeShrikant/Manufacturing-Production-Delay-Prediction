"""Validation of production data (used by preprocessing, API and UI)."""
import pandas as pd

NUMERIC_POSITIVE = ["planned_production_quantity", "shift_duration_minutes", "takt_time_seconds",
                    "designed_cycle_time_seconds"]


def validate(df: pd.DataFrame, required: list[str]) -> dict:
    """Return a report. report['valid'] is True only if the data can be used for the given columns."""
    errors, warnings = [], []
    if df is None or len(df) == 0:
        return {"valid": False, "rows": 0, "errors": ["Dataset is empty."], "warnings": [],
                "missing_columns": list(required), "missing_values": {}, "duplicates": 0, "invalid_rows": 0}
    missing_cols = [c for c in required if c not in df.columns]
    if missing_cols:
        errors.append(f"Missing required columns: {missing_cols}")
    present = [c for c in required if c in df.columns]
    miss = {c: int(df[c].isna().sum()) for c in present if df[c].isna().any()}
    if miss:
        warnings.append(f"Missing values in required columns: {miss}")
    dups = int(df.duplicated().sum())
    if dups:
        warnings.append(f"{dups} duplicate rows (they are removed during preprocessing).")
    invalid = pd.Series(False, index=df.index)
    for c in present:
        if c in NUMERIC_POSITIVE:
            num = pd.to_numeric(df[c], errors="coerce")
            bad = num.isna() | (num <= 0)
            invalid |= bad
        elif df[c].dtype != object and str(df[c].dtype) not in ("str", "string", "category"):
            num = pd.to_numeric(df[c], errors="coerce")
            invalid |= (num < 0)
    n_inv = int(invalid.sum())
    if n_inv:
        warnings.append(f"{n_inv} rows contain invalid values (zero/negative where a positive number is required).")
    return {"valid": not errors, "rows": int(len(df)), "errors": errors, "warnings": warnings,
            "missing_columns": missing_cols, "missing_values": miss, "duplicates": dups, "invalid_rows": n_inv}
