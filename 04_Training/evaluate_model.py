"""Evaluate saved models on the held-out TEST split (never used for selection or fitting of the
preprocessor/model apart from the final train+validation refit). Writes 08_Results/*.
Run:  python 04_Training/evaluate_model.py"""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import joblib, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import (accuracy_score, precision_recall_fscore_support, confusion_matrix,
                             mean_absolute_error, mean_squared_error, ConfusionMatrixDisplay)
import config as C

L2I = {l: i for i, l in enumerate(C.LABELS)}


def main():
    models = joblib.load(C.MODELS_DIR / "production_delay_model.pkl")
    pipes = joblib.load(C.MODELS_DIR / "preprocessing_pipeline.pkl")
    log = json.load(open(C.MODELS_DIR / "training_log.json"))
    te = pd.read_csv(C.PROCESSED_DIR / "test.csv", parse_dates=["shift_date"])
    C.RESULTS_DIR.mkdir(exist_ok=True)
    out = {"data_is_synthetic": True, "note": "Metrics are on the newest 15% of a SYNTHETIC dataset. They are not real-factory results.",
           "test_rows": len(te), "test_period": [str(te.shift_date.min().date()), str(te.shift_date.max().date())], "modes": {}}
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    preds = {}
    for ax, (mode, fs) in zip(axes, C.FEATURE_SETS.items()):
        cols = fs["numeric"] + fs["categorical"]
        X = pipes[mode].transform(te[cols])
        y = te["delay_risk"].map(L2I)
        p = models[mode]["classifier"].predict(X)
        pr, rc, f1, _ = precision_recall_fscore_support(y, p, average="macro", zero_division=0)
        cm = confusion_matrix(y, p, labels=[0, 1, 2])
        # baseline: always predict the most frequent TRAIN class
        tr = pd.read_csv(C.PROCESSED_DIR / "train.csv")
        majority = tr["delay_risk"].map(L2I).mode()[0]
        base_acc = float((y == majority).mean())
        reg_p = models[mode]["regressor"].predict(X)
        reg_p = np.clip(reg_p, 0, 100)
        qty_p = reg_p / 100 * te["planned_production_quantity"]
        out["modes"][mode] = {
            "description": fs["description"],
            "classifier": log["modes"][mode]["selected_classifier"],
            "classification": {"accuracy": round(accuracy_score(y, p), 4), "precision_macro": round(pr, 4),
                               "recall_macro": round(rc, 4), "f1_macro": round(f1, 4),
                               "majority_class_baseline_accuracy": round(base_acc, 4),
                               "confusion_matrix_rows_true_cols_pred": {"labels": C.LABELS, "matrix": cm.tolist()}},
            "regressor": log["modes"][mode]["selected_regressor"],
            "regression_achievement_pct": {"MAE_pct_points": round(mean_absolute_error(te["achievement_pct"], reg_p), 3),
                                           "RMSE_pct_points": round(float(np.sqrt(mean_squared_error(te["achievement_pct"], reg_p))), 3),
                                           "baseline_MAE_predict_train_mean": round(float(mean_absolute_error(te["achievement_pct"], np.full(len(te), tr["achievement_pct"].mean()))), 3)},
            "regression_production_quantity": {"MAE_units": round(mean_absolute_error(te["actual_production_quantity"], qty_p), 2),
                                               "RMSE_units": round(float(np.sqrt(mean_squared_error(te["actual_production_quantity"], qty_p))), 2),
                                               "baseline_MAE_units_predict_planned_x_train_mean": round(float(mean_absolute_error(te["actual_production_quantity"], te["planned_production_quantity"] * tr["achievement_pct"].mean() / 100)), 2)},
        }
        ConfusionMatrixDisplay(cm, display_labels=C.LABELS).plot(ax=ax, colorbar=False, cmap="Blues")
        ax.set_title(f"{mode} model ({out['modes'][mode]['classifier'].split(' (')[0]})")
        preds[mode] = (p, reg_p, qty_p)
    fig.suptitle("Confusion matrix on held-out test data (synthetic dataset)"); fig.tight_layout()
    fig.savefig(C.RESULTS_DIR / "confusion_matrix.png", dpi=130); plt.close(fig)

    # permutation importance of the in-shift classifier, grouped back to original columns
    fs = C.FEATURE_SETS["shift"]; cols = fs["numeric"] + fs["categorical"]
    from sklearn.metrics import f1_score
    rng = np.random.default_rng(0)
    yt = te["delay_risk"].map(L2I)
    clf, pre = models["shift"]["classifier"], pipes["shift"]
    base = f1_score(yt, clf.predict(pre.transform(te[cols])), average="macro")
    drops = {}
    for c in cols:   # shuffle ONE raw column, keep the rest, measure the macro-F1 drop
        d = []
        for _ in range(8):
            t = te[cols].copy(); t[c] = rng.permutation(t[c].values)
            d.append(base - f1_score(yt, clf.predict(pre.transform(t)), average="macro"))
        drops[c] = float(np.mean(d))
    imp = type("I", (), {"importances_mean": [drops[c] for c in cols]})()
    s = pd.Series(imp.importances_mean, index=cols).sort_values().tail(15)
    fig, ax = plt.subplots(figsize=(8, 5.5)); s.plot.barh(ax=ax, color="#1f3a5f")
    ax.set_xlabel("Drop in macro-F1 when shuffled (test set)"); ax.set_title("Feature importance - in-shift risk model")
    fig.tight_layout(); fig.savefig(C.RESULTS_DIR / "feature_importance.png", dpi=130); plt.close(fig)
    out["feature_importance_top"] = {k: round(float(v), 4) for k, v in s.sort_values(ascending=False).head(10).items()}

    sp = te[["line_id", "shift_date", "planned_production_quantity", "actual_production_quantity", "achievement_pct", "delay_risk"]].copy()
    for mode in C.FEATURE_SETS:
        p, r, q = preds[mode]
        sp[f"{mode}_pred_risk"] = [C.LABELS[i] for i in p]
        sp[f"{mode}_pred_achievement_pct"] = r.round(1)
        sp[f"{mode}_pred_quantity"] = q.round(0)
    sp.head(100).to_csv(C.RESULTS_DIR / "sample_predictions.csv", index=False)
    json.dump(out, open(C.RESULTS_DIR / "model_metrics.json", "w"), indent=2)
    print(json.dumps({m: {"clf": v["classification"]["f1_macro"], "acc": v["classification"]["accuracy"], "base_acc": v["classification"]["majority_class_baseline_accuracy"],
                          "mae_pts": v["regression_achievement_pct"]["MAE_pct_points"], "base_mae": v["regression_achievement_pct"]["baseline_MAE_predict_train_mean"]} for m, v in out["modes"].items()}, indent=1))


if __name__ == "__main__":
    main()
