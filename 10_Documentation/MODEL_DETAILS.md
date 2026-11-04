# Model details
**Split:** chronological by `shift_date`: oldest 70% train, next 15% validation, newest 15% test. Model choice uses validation only; the winner is refit on train+validation; test is reported once.
**Preprocessing:** median imputation + standard scaling (numeric), most-frequent imputation + one-hot (categorical, unknown categories ignored). Fitted on training data only.
**Candidates:** classification - LogisticRegression, RandomForest, XGBoost (scikit-learn HistGradientBoosting is used instead if `xgboost` is not installed); regression - Ridge, RandomForest, XGBoost/HistGB. Selection: macro-F1 (classification), MAE (regression).
**Validation scores** (from `05_Models/training_log.json`):
| Model set | Classifier val macro-F1: LogReg / RF / HistGB | Regressor val MAE: Ridge / RF / HistGB |
|---|---|---|
| plan | 0.420 / 0.446 / 0.407 | 10.60 / 10.45 / 10.84 |
| shift | 0.974 / 0.857 / 0.943 | 1.38 / 1.14 / 0.91 |
**Leakage control:** features are listed in `config.py`; `LEAKAGE_COLUMNS` are asserted absent at training time and in a unit test.
**Feature importance (shift classifier, shuffle test):** cycle-time ratio, changeover time, downtime share, unplanned downtime.
**Bottleneck / action:** rule-based; picks the largest of downtime share, changeover share, cycle-time slowdown (1 - designed/actual) if >= 5%. Plan mode only flags planned load > 120% of takt capacity or condition score < 5. Not an ML output, and not machine-level.
**Probabilities** are raw classifier outputs and are not calibrated.
## Testing
`python -m pytest 09_Tests -q` runs 31 tests (22 if the optional API packages are not installed): preprocessing, validation, empty datasets, duplicates, missing columns, invalid values, model loading, predictions and the API (upload, invalid input, missing columns, wrong file type). API tests are skipped automatically if `fastapi`, `httpx` or `python-multipart` is not installed. Models and processed data are created automatically by the test setup if they are missing.
