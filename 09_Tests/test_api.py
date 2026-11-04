import io
import pytest
pytest.importorskip("fastapi"); pytest.importorskip("httpx"); pytest.importorskip("multipart")
from fastapi.testclient import TestClient
import config as C
from main import app
from test_prediction import REC

client = TestClient(app)


def test_health():
    r = client.get("/health"); assert r.status_code == 200 and r.json()["model_loaded"] is True


def test_model_info():
    r = client.get("/model-info"); assert r.status_code == 200 and "metadata" in r.json()


def test_predict_ok():
    r = client.post("/predict", json={"mode": "shift", **REC})
    assert r.status_code == 200
    assert {"delay_risk", "predicted_production", "target_achievement_percentage", "possible_bottleneck", "recommended_action"} <= set(r.json())


def test_predict_invalid_input():
    assert client.post("/predict", json={"mode": "shift", **{**REC, "planned_production_quantity": -1}}).status_code == 422
    assert client.post("/predict", json={"mode": "shift", **{**REC, "line_type": "bogus"}}).status_code == 422


def test_predict_missing_shift_fields():
    rec = {k: v for k, v in REC.items() if k != "downtime_unplanned_minutes"}
    assert client.post("/predict", json={"mode": "shift", **rec}).status_code == 422


def test_upload_csv_ok():
    with open(C.SAMPLE_FILE, "rb") as f:
        r = client.post("/upload-csv?mode=shift", files={"file": ("sample.csv", f, "text/csv")})
    assert r.status_code == 200 and r.json()["rows_predicted"] > 0


def test_upload_missing_columns():
    r = client.post("/upload-csv", files={"file": ("x.csv", io.BytesIO(b"a,b\n1,2\n"), "text/csv")})
    assert r.status_code == 422


def test_upload_empty_and_wrong_type():
    assert client.post("/upload-csv", files={"file": ("x.csv", io.BytesIO(b""), "text/csv")}).status_code in (400, 422)
    assert client.post("/upload-csv", files={"file": ("x.txt", io.BytesIO(b"a"), "text/plain")}).status_code == 400


def test_sample_data():
    r = client.get("/sample-data?rows=3"); assert r.status_code == 200 and len(r.json()) == 3
