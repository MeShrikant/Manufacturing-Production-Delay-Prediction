"""Train + compare models for two feature sets (plan / shift).
Classification target: delay_risk (Low/Medium/High).  Regression target: achievement_pct.
Selection uses the VALIDATION split only; the chosen model is refit on train+validation.
Run:  python 04_Training/train_model.py"""
import sys, json, warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import joblib, numpy as np, pandas as pd
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, HistGradientBoostingClassifier, HistGradientBoostingRegressor
from sklearn.metrics import f1_score, accuracy_score, mean_absolute_error
import config as C
from preprocess import build_preprocessor
warnings.filterwarnings("ignore")
try:
    from xgboost import XGBClassifier, XGBRegressor
    HAVE_XGB = True
except ImportError:
    HAVE_XGB = False

LABEL_TO_INT = {l: i for i, l in enumerate(C.LABELS)}


def clf_candidates():
    c = {"LogisticRegression": LogisticRegression(max_iter=2000, class_weight="balanced"),
         "RandomForest": RandomForestClassifier(n_estimators=300, min_samples_leaf=3, class_weight="balanced", n_jobs=-1, random_state=42)}
    if HAVE_XGB:
        c["XGBoost"] = XGBClassifier(n_estimators=300, learning_rate=0.05, max_depth=4, subsample=0.8, random_state=42, eval_metric="mlogloss")
    else:  # documented fallback so the comparison still contains a boosted-tree model
        c["HistGradientBoosting (XGBoost not installed)"] = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.05, random_state=42)
    return c


def reg_candidates():
    c = {"Ridge": Ridge(alpha=1.0),
         "RandomForest": RandomForestRegressor(n_estimators=300, min_samples_leaf=3, n_jobs=-1, random_state=42)}
    if HAVE_XGB:
        c["XGBoost"] = XGBRegressor(n_estimators=300, learning_rate=0.05, max_depth=4, subsample=0.8, random_state=42)
    else:
        c["HistGradientBoosting (XGBoost not installed)"] = HistGradientBoostingRegressor(max_iter=300, learning_rate=0.05, random_state=42)
    return c


def main():
    tr = pd.read_csv(C.PROCESSED_DIR / "train.csv", parse_dates=["shift_date"])
    va = pd.read_csv(C.PROCESSED_DIR / "validation.csv", parse_dates=["shift_date"])
    trva = pd.concat([tr, va], ignore_index=True)
    models, pipes, log = {}, {}, {"xgboost_available": HAVE_XGB, "modes": {}}
    for mode, fs in C.FEATURE_SETS.items():
        cols = fs["numeric"] + fs["categorical"]
        assert not set(cols) & set(C.LEAKAGE_COLUMNS), "leakage column in features!"
        pre = build_preprocessor(mode).fit(tr[cols])
        Xtr, Xva = pre.transform(tr[cols]), pre.transform(va[cols])
        ytr_c, yva_c = tr["delay_risk"].map(LABEL_TO_INT), va["delay_risk"].map(LABEL_TO_INT)
        ytr_r, yva_r = tr["achievement_pct"], va["achievement_pct"]
        mlog = {"features": cols, "classification": {}, "regression": {}}
        best_c, best_r = (None, -1), (None, 1e9)
        for name, m in clf_candidates().items():
            m.fit(Xtr, ytr_c); p = m.predict(Xva)
            s = {"accuracy": accuracy_score(yva_c, p), "f1_macro": f1_score(yva_c, p, average="macro")}
            mlog["classification"][name] = {k: round(float(v), 4) for k, v in s.items()}
            if s["f1_macro"] > best_c[1]: best_c = (name, s["f1_macro"])
        for name, m in reg_candidates().items():
            m.fit(Xtr, ytr_r); p = m.predict(Xva)
            mae = mean_absolute_error(yva_r, p)
            mlog["regression"][name] = {"mae_pct_points": round(float(mae), 4)}
            if mae < best_r[1]: best_r = (name, mae)
        mlog["selected_classifier"], mlog["selected_regressor"] = best_c[0], best_r[0]
        # refit selected models + preprocessor on train+validation
        pre_f = build_preprocessor(mode).fit(trva[cols])
        Xall = pre_f.transform(trva[cols])
        clf = clf_candidates()[best_c[0]].fit(Xall, trva["delay_risk"].map(LABEL_TO_INT))
        reg = reg_candidates()[best_r[0]].fit(Xall, trva["achievement_pct"])
        models[mode] = {"classifier": clf, "regressor": reg}
        pipes[mode] = pre_f
        log["modes"][mode] = mlog
        print(f"[{mode}] classifier -> {best_c[0]} (val F1 {best_c[1]:.3f}) | regressor -> {best_r[0]} (val MAE {best_r[1]:.2f} pts)")
    C.MODELS_DIR.mkdir(exist_ok=True)
    joblib.dump(models, C.MODELS_DIR / "production_delay_model.pkl")
    joblib.dump(pipes, C.MODELS_DIR / "preprocessing_pipeline.pkl")
    json.dump(log, open(C.MODELS_DIR / "training_log.json", "w"), indent=2)
    meta = {"data_is_synthetic": True, "dataset": "xpertsystems/mfg005-sample (synthetic line performance)",
            "target_definitions": {"achievement_pct": "actual_production_quantity / planned_production_quantity * 100",
                                   "delay_risk": f"High if achievement < {C.HIGH_RISK_BELOW}%, Medium if < {C.MEDIUM_RISK_BELOW}%, else Low (thresholds are assumptions)"},
            "labels": C.LABELS, "trained_rows": int(len(trva)), "split": "chronological 70/15/15 by shift_date",
            "feature_sets": {m: {"description": f["description"], "numeric": f["numeric"], "categorical": f["categorical"]} for m, f in C.FEATURE_SETS.items()},
            "selected": {m: {"classifier": l["selected_classifier"], "regressor": l["selected_regressor"]} for m, l in log["modes"].items()},
            "xgboost_available": HAVE_XGB}
    json.dump(meta, open(C.MODELS_DIR / "model_metadata.json", "w"), indent=2)
    print(json.dumps(log["modes"], indent=1))


if __name__ == "__main__":
    main()
