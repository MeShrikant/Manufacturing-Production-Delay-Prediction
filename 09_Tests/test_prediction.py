import pandas as pd, pytest
import config as C
import predictor

REC = {"shift_number": 2, "shift_duration_minutes": 450, "planned_production_quantity": 500, "number_of_stations": 5,
       "takt_time_seconds": 60, "designed_cycle_time_seconds": 55, "equipment_age_years": 15, "equipment_condition_score": 6,
       "operator_headcount_planned": 10, "product_family": "automotive_body", "line_type": "assembly_line",
       "automation_level": "manual", "line_configuration": "serial", "planned_maintenance_flag": "no",
       "downtime_unplanned_minutes": 60, "actual_cycle_time_avg_seconds": 65, "operator_headcount_actual": 9,
       "changeover_time_minutes": 0, "downtime_event_count": 3}


def test_model_loads():
    models, pipes = predictor.load()
    assert set(models) == {"plan", "shift"} and set(pipes) == {"plan", "shift"}


def test_single_prediction_fields():
    r = predictor.predict_one(dict(REC), "shift")
    assert r["delay_risk"] in C.LABELS and 0 <= r["target_achievement_percentage"] <= 100
    assert 0 <= r["predicted_production"] <= REC["planned_production_quantity"]
    assert abs(sum(r["risk_probabilities"].values()) - 1) < 0.01


def test_more_downtime_does_not_lower_risk():
    low = predictor.predict_one({**REC, "downtime_unplanned_minutes": 5, "actual_cycle_time_avg_seconds": 56}, "shift")
    high = predictor.predict_one({**REC, "downtime_unplanned_minutes": 250, "actual_cycle_time_avg_seconds": 110}, "shift")
    assert high["target_achievement_percentage"] < low["target_achievement_percentage"]


def test_plan_mode_needs_no_shift_fields():
    rec = {k: v for k, v in REC.items() if k not in ("downtime_unplanned_minutes", "actual_cycle_time_avg_seconds",
           "operator_headcount_actual", "changeover_time_minutes", "downtime_event_count")}
    assert predictor.predict_one(rec, "plan")["delay_risk"] in C.LABELS


def test_shift_mode_missing_columns_raises():
    rec = {k: v for k, v in REC.items() if k != "downtime_unplanned_minutes"}
    with pytest.raises(ValueError):
        predictor.predict_one(rec, "shift")


def test_invalid_mode_raises():
    with pytest.raises(ValueError):
        predictor.predict_one(dict(REC), "future")


def test_empty_dataset_raises():
    with pytest.raises(ValueError):
        predictor.predict_df(pd.DataFrame(), "shift")


def test_batch_on_sample_file_and_duplicates():
    s = pd.read_csv(C.SAMPLE_FILE).head(30)
    res = predictor.predict_df(pd.concat([s, s.head(5)]), "shift")
    assert len(res) == 30  # duplicates removed
    assert res["delay_risk"].isin(C.LABELS).all()


def test_invalid_numeric_rows_skipped():
    s = pd.read_csv(C.SAMPLE_FILE).head(10).copy()
    s.loc[s.index[0], "planned_production_quantity"] = -5
    res = predictor.predict_df(s, "shift")
    assert len(res) == 9 and res.attrs["skipped_rows"] == 1
