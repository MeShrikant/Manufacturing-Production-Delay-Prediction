"""Central configuration: paths, target definition, feature sets. Imported by every module."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
for sub in ("03_Data_Preprocessing", "04_Training", "06_API"):
    p = str(ROOT / sub)
    if p not in sys.path:
        sys.path.insert(0, p)

RAW_FILE = ROOT / "02_Dataset" / "raw" / "mfg005_synthetic_line_performance.csv"
PROCESSED_DIR = ROOT / "02_Dataset" / "processed"
CLEAN_FILE = PROCESSED_DIR / "clean_data.csv"
MODELS_DIR = ROOT / "05_Models"
RESULTS_DIR = ROOT / "08_Results"
SAMPLE_FILE = ROOT / "02_Dataset" / "sample_data.csv"

# ---- Target definitions -------------------------------------------------------------
# achievement_pct = actual_production_quantity / planned_production_quantity * 100
# delay_risk is derived from achievement_pct. The thresholds are an ASSUMPTION fitted to this
# synthetic dataset (no row reaches 100%, mean ~65%). Change them for a real factory.
HIGH_RISK_BELOW = 60.0     # achievement < 60%        -> High
MEDIUM_RISK_BELOW = 75.0   # 60% <= achievement < 75% -> Medium ; >= 75% -> Low
LABELS = ["Low", "Medium", "High"]

# ---- Feature sets (no target-derived columns) ---------------------------------------
CATEGORICAL = ["product_family", "line_type", "automation_level", "line_configuration",
               "planned_maintenance_flag"]
PLAN_NUMERIC = ["shift_number", "shift_duration_minutes", "planned_production_quantity",
                "number_of_stations", "takt_time_seconds", "designed_cycle_time_seconds",
                "equipment_age_years", "equipment_condition_score", "operator_headcount_planned",
                "planned_load_ratio"]
SHIFT_EXTRA = ["downtime_unplanned_minutes", "actual_cycle_time_avg_seconds",
               "operator_headcount_actual", "changeover_time_minutes", "downtime_event_count",
               "cycle_time_ratio", "downtime_share", "headcount_ratio"]
FEATURE_SETS = {
    "plan": {"categorical": CATEGORICAL, "numeric": PLAN_NUMERIC,
             "description": "Pre-shift planning risk. Uses only information known before the shift starts."},
    "shift": {"categorical": CATEGORICAL, "numeric": PLAN_NUMERIC + SHIFT_EXTRA,
              "description": "Current-shift risk estimate. Adds downtime, cycle time, headcount and changeover "
                             "values observed or expected for the shift."},
}
# Columns that must NEVER be used as inputs (they are the target or computed from it).
LEAKAGE_COLUMNS = ["actual_production_quantity", "good_units_produced", "defective_units_produced",
                   "scrap_units", "rework_units", "total_parts_processed", "throughput_rate_actual_uph",
                   "throughput_rate_ratio", "output_variance_pct", "units_per_operator_hour",
                   "oee_overall", "oee_performance", "oee_availability", "teep_pct",
                   "performance_loss_units", "quality_loss_units", "cycle_time_loss_seconds",
                   "oee_benchmark_class", "oee_loss_primary_driver", "available_time_minutes",
                   "achievement_pct", "delay_risk"]
