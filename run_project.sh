#!/usr/bin/env bash
# Linux/macOS: preprocess, train, evaluate, test, then start API (background) and UI.
set -e
cd "$(dirname "$0")"
python 03_Data_Preprocessing/preprocess.py
python 04_Training/train_model.py
python 04_Training/evaluate_model.py
python -m pytest 09_Tests -q
uvicorn main:app --app-dir 06_API --port 8000 &
API_PID=$!
trap 'kill $API_PID 2>/dev/null' EXIT
streamlit run 07_UI/app.py
