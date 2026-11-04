"""Simple demo UI: enter a few shift details -> see the prediction.
Run from the project root:  streamlit run 07_UI/app.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import streamlit as st
import config as C
import predictor
from components.style import inject_css, banner, risk_badge

st.set_page_config(page_title="Production Delay AI", page_icon="🏭", layout="wide")
inject_css()
banner("🏭 Production Delay Prediction", "Enter shift details on the left → see the predicted delay risk on the right")
if not predictor.models_ready():
    st.error("Trained model not found. Run `python 03_Data_Preprocessing/preprocess.py` and `python 04_Training/train_model.py` first (see README)."); st.stop()

SCENARIOS = {  # downtime min, actual cycle sec, changeover min
    "Good shift": (15, 57, 0),
    "Average shift": (60, 65, 20),
    "Bad shift": (200, 85, 60),
}
left, right = st.columns([1, 1.2], gap="large")

with left:
    st.subheader("Input")
    sc = st.radio("Example scenario (fills the numbers below)", list(SCENARIOS), horizontal=True, index=1)
    dt0, ac0, co0 = SCENARIOS[sc]
    k = sc  # changing scenario resets the fields
    planned = st.number_input("Planned production quantity (units)", 50, 5000, 500, 10, key=f"p{k}")
    duration = st.number_input("Shift duration (minutes)", 240, 720, 450, 10, key=f"d{k}")
    designed = st.number_input("Planned cycle time (seconds)", 5.0, 600.0, 55.0, 1.0, key=f"dc{k}")
    actual = st.number_input("Actual cycle time (seconds)", 5.0, 900.0, float(ac0), 1.0, key=f"ac{k}")
    downtime = st.number_input("Machine downtime (minutes)", 0, 480, dt0, 5, key=f"dt{k}")
    changeover = st.number_input("Changeover time (minutes)", 0, 240, co0, 5, key=f"co{k}")
    go = st.button("Predict", type="primary", use_container_width=True)

with right:
    st.subheader("Output")
    if not go:
        st.info("Choose a scenario or change the numbers, then click **Predict**.")
    elif downtime > duration:
        st.error("Downtime cannot be longer than the shift.")
    else:
        rec = {"shift_number": 1, "shift_duration_minutes": float(duration), "planned_production_quantity": int(planned),
               "number_of_stations": 5, "takt_time_seconds": designed * 1.1, "designed_cycle_time_seconds": designed,
               "equipment_age_years": 15.0, "equipment_condition_score": 6.0, "operator_headcount_planned": 10,
               "product_family": "automotive_body", "line_type": "assembly_line", "automation_level": "semi_automated",
               "line_configuration": "serial", "planned_maintenance_flag": "no",
               "downtime_unplanned_minutes": float(downtime), "actual_cycle_time_avg_seconds": float(actual),
               "operator_headcount_actual": 10, "changeover_time_minutes": float(changeover),
               "downtime_event_count": max(0, round(downtime / 20))}
        r = predictor.predict_one(rec, "shift")
        st.caption("Delay risk")
        risk_badge(r["delay_risk"])
        a, b = st.columns(2)
        a.metric("Predicted production", f"{r['predicted_production']:,} units", f"{r['predicted_production'] - planned:+,} vs plan", delta_color="off")
        b.metric("Target achievement", f"{r['target_achievement_percentage']:.0f}%")
        st.progress(min(int(r["target_achievement_percentage"]), 100))
        st.markdown(f"**Possible bottleneck:** {r['possible_bottleneck']}")
        st.markdown(f"**Recommended action:** {r['recommended_action']}")
        st.caption("Demo on a synthetic dataset. Not validated on real factory data. Other fields use typical fixed values.")
