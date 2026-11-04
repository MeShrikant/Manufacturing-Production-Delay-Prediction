# Installation
Requires Python 3.10 or newer. Tested with Python 3.13, pandas 3.0, scikit-learn 1.9, numpy 2.5.

## Windows (PowerShell / VS Code terminal)
```
python -m venv .venv
.venv\Scripts\Activate.ps1          (if blocked: Set-ExecutionPolicy -Scope Process Bypass)
pip install -r requirements.txt
```
or just double-click `run_project.bat`, which does everything below and starts the API and UI.

## Linux / macOS
```
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
./run_project.sh
```

## Step by step (any OS)
1. Dataset: already in `02_Dataset/raw/`. If missing, see `01_Reference/dataset_source.md`.
2. Preprocess: `python 03_Data_Preprocessing/preprocess.py`
3. Train: `python 04_Training/train_model.py`
4. Evaluate: `python 04_Training/evaluate_model.py` (writes metrics and plots to `08_Results/`)
5. API: `uvicorn main:app --app-dir 06_API --port 8000`  (Swagger UI: http://localhost:8000/docs)
6. UI (second terminal, same environment): `streamlit run 07_UI/app.py`
7. Tests: `python -m pytest 09_Tests -q`

Trained models are not stored in the repository. Step 3 creates `05_Models/*.pkl` on your machine, so they always match your scikit-learn version.
