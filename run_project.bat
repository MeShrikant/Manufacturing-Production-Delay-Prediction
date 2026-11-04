@echo off
REM Manufacturing_Production_Delay_Prediction_AI - Windows one-click setup and run
cd /d "%~dp0"
if not exist .venv ( python -m venv .venv || goto :err )
call .venv\Scripts\activate.bat
pip install -r requirements.txt || goto :err
if not exist 02_Dataset\raw\mfg005_synthetic_line_performance.csv (
  echo Dataset missing - see 02_Dataset\download_dataset.py or INSTALLATION.md & goto :err )
python 03_Data_Preprocessing\preprocess.py || goto :err
python 04_Training\train_model.py || goto :err
python 04_Training\evaluate_model.py || goto :err
python -m pytest 09_Tests -q
start "FastAPI" cmd /k "call .venv\Scripts\activate.bat && uvicorn main:app --app-dir 06_API --port 8000"
streamlit run 07_UI\app.py
goto :eof
:err
echo Something failed - read the message above.
pause
