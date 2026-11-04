import pandas as pd, pytest
import config as C
from data_validation import validate
from preprocess import clean, chronological_split, risk_from_achievement


def raw():
    return pd.read_csv(C.RAW_FILE)


def test_valid_raw_data_passes():
    assert validate(raw(), ["planned_production_quantity", "shift_date"])["valid"]


def test_empty_dataset_rejected():
    rep = validate(pd.DataFrame(), ["planned_production_quantity"])
    assert not rep["valid"] and "empty" in rep["errors"][0].lower()


def test_missing_columns_reported():
    rep = validate(raw().drop(columns=["takt_time_seconds"]), ["takt_time_seconds"])
    assert not rep["valid"] and rep["missing_columns"] == ["takt_time_seconds"]


def test_duplicates_removed_by_clean():
    r = raw().head(200)
    df, rep = clean(pd.concat([r, r.head(20)], ignore_index=True))
    assert rep["duplicates"] == 20 and len(df) == 200


def test_invalid_values_dropped():
    r = raw().head(50).copy()
    r.loc[r.index[:3], "planned_production_quantity"] = 0
    df, rep = clean(r)
    assert rep["rows_dropped_invalid"] == 3 and len(df) == 47


def test_no_leakage_columns_in_features():
    for fs in C.FEATURE_SETS.values():
        assert not set(fs["numeric"] + fs["categorical"]) & set(C.LEAKAGE_COLUMNS)


def test_targets_and_split_are_chronological():
    df, _ = clean(raw())
    assert df["achievement_pct"].between(0, 100).all()
    tr, va, te = chronological_split(df)
    assert tr.shift_date.max() <= va.shift_date.min() and va.shift_date.max() <= te.shift_date.min()
    assert len(tr) + len(va) + len(te) == len(df)


@pytest.mark.parametrize("a,r", [(10, "High"), (59.9, "High"), (60, "Medium"), (74.9, "Medium"), (75, "Low"), (95, "Low")])
def test_risk_thresholds(a, r):
    assert risk_from_achievement(a) == r
