"""FastAPI backend.  Run from the project root:
    uvicorn main:app --app-dir 06_API --port 8000        (docs: http://localhost:8000/docs)"""
import io, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile, Query
from fastapi.responses import Response
import config as C
import predictor
from schemas import PredictRequest, PredictResponse

app = FastAPI(title="Manufacturing Production Delay Prediction AI", version="1.0",
              description="Predicts production delay risk and target achievement. Trained on a SYNTHETIC dataset; "
                          "validate with your own factory data before real use.")
MAX_UPLOAD_BYTES = 20 * 1024 * 1024


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": predictor.models_ready()}


@app.get("/model-info")
def model_info():
    if not predictor.models_ready():
        raise HTTPException(503, "Model not trained yet. Run 04_Training/train_model.py")
    return predictor.model_info()


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    try:
        rec = req.model_dump()
        mode = rec.pop("mode")
        return predictor.predict_one(rec, mode)
    except predictor.ModelNotReady as e:
        raise HTTPException(503, str(e))
    except ValueError as e:
        raise HTTPException(422, str(e))


@app.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...), mode: str = Query("shift", pattern="^(plan|shift)$"), limit: int = Query(1000, ge=1, le=10000)):
    if not (file.filename or "").lower().endswith(".csv"):
        raise HTTPException(400, "Please upload a .csv file.")
    raw = await file.read()
    if len(raw) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, "File too large (max 20 MB).")
    try:
        df = pd.read_csv(io.BytesIO(raw))
    except Exception:
        raise HTTPException(400, "Could not read the file as CSV.")
    from data_validation import validate
    report = validate(df, predictor.required_columns(mode))
    if not report["valid"]:
        raise HTTPException(422, {"message": "CSV is not valid for batch prediction.", "validation": report})
    try:
        res = predictor.predict_df(df, mode)
    except predictor.ModelNotReady as e:
        raise HTTPException(503, str(e))
    except ValueError as e:
        raise HTTPException(422, str(e))
    return {"validation": report, "rows_predicted": len(res), "rows_skipped_invalid": res.attrs.get("skipped_rows", 0),
            "risk_counts": res["delay_risk"].value_counts().to_dict(),
            "predictions": res.head(limit).to_dict("records")}


@app.get("/sample-data")
def sample_data(download: bool = False, rows: int = Query(20, ge=1, le=200)):
    if not C.SAMPLE_FILE.exists():
        raise HTTPException(404, "sample_data.csv not found. Run 03_Data_Preprocessing/preprocess.py")
    if download:
        return Response(C.SAMPLE_FILE.read_bytes(), media_type="text/csv",
                        headers={"Content-Disposition": "attachment; filename=sample_data.csv"})
    return pd.read_csv(C.SAMPLE_FILE).head(rows).to_dict("records")
