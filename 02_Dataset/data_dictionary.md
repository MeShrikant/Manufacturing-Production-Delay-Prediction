# Data dictionary

Source file: `raw/mfg005_synthetic_line_performance.csv` - 3,000 rows x 118 columns, one row per production-line shift.
**The data is synthetic** (the file name says so). Column meanings below are inferred from the column names; check the dataset card on Hugging Face for the authoritative definitions.

Missing values: only `coolant_consumption_litres` (not used). Duplicate rows: 0.

## Targets (created by `preprocess.py`)
- `achievement_pct = actual_production_quantity / planned_production_quantity * 100` (regression target).
- `delay_risk`: **High** if achievement < 60.0%, **Medium** if < 75.0%, else **Low**. These thresholds are an assumption chosen for this dataset (no shift reaches 100%; mean is ~65%). Change them in `config.py`.
- Expected production quantity = predicted achievement % x planned quantity.

## Columns
| Column | Type | Example | Role |
|---|---|---|---|
| `line_id` | str | MFG-LINE-PLT-004-06 | Identifier / analysis only (not a feature) |
| `plant_id` | str | PLT-004 | Identifier / analysis only (not a feature) |
| `work_center_id` | str | WC-037 | Identifier / analysis only (not a feature) |
| `shift_id` | str | SHF-PLT-004-20210729-1 | Identifier / analysis only (not a feature) |
| `shift_date` | str | 2021-07-29 | Identifier / analysis only (not a feature) |
| `shift_number` | int64 | 1 | Feature (plan + shift models) |
| `shift_duration_minutes` | float64 | 475.1 | Feature (plan + shift models) |
| `product_id` | str | PRD-2021-SKU-05702 | Identifier / analysis only (not a feature) |
| `product_family` | str | industrial_machinery | Feature (plan + shift models) |
| `production_order_id` | str | WO-2021-98019 | Identifier / analysis only (not a feature) |
| `line_type` | str | chemical_process | Feature (plan + shift models) |
| `automation_level` | str | semi_automated | Feature (plan + shift models) |
| `number_of_stations` | int64 | 3 | Feature (plan + shift models) |
| `line_configuration` | str | job_shop | Feature (plan + shift models) |
| `plant_location` | str | Detroit_US | Identifier / analysis only (not a feature) |
| `industry_sector` | str | industrial | Identifier / analysis only (not a feature) |
| `takt_time_seconds` | float64 | 126.5 | Feature (plan + shift models) |
| `designed_cycle_time_seconds` | float64 | 112.6 | Feature (plan + shift models) |
| `actual_cycle_time_avg_seconds` | float64 | 121.036 | Feature (shift model only) |
| `actual_cycle_time_std_seconds` | float64 | 14.524 | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `actual_cycle_time_min_seconds` | float64 | 105.28 | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `actual_cycle_time_max_seconds` | float64 | 343.64 | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `cycle_time_percentile_p50` | float64 | 123.31 | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `cycle_time_percentile_p95` | float64 | 145.0 | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `cycle_time_cov` | float64 | 0.12 | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `bottleneck_station_id` | str | WC-003 | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `bottleneck_cycle_time_seconds` | float64 | 128.95 | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `bottleneck_utilisation_pct` | float64 | 96.85 | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `secondary_bottleneck_station_id` | str | WC-002 | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `cycle_time_loss_seconds` | float64 | 89.07 | EXCLUDED - target-derived or known only after the shift |
| `planned_production_quantity` | int64 | 252 | Feature (plan + shift models) |
| `actual_production_quantity` | int64 | 235 | Target source (achievement = actual / planned) |
| `good_units_produced` | int64 | 234 | EXCLUDED - target-derived or known only after the shift |
| `defective_units_produced` | int64 | 1 | EXCLUDED - target-derived or known only after the shift |
| `scrap_units` | int64 | 0 | EXCLUDED - target-derived or known only after the shift |
| `rework_units` | int64 | 1 | EXCLUDED - target-derived or known only after the shift |
| `throughput_rate_actual_uph` | float64 | 29.68 | EXCLUDED - target-derived or known only after the shift |
| `throughput_rate_design_uph` | float64 | 31.97 | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `throughput_rate_ratio` | float64 | 0.9284 | EXCLUDED - target-derived or known only after the shift |
| `rolled_throughput_yield_pct` | float64 | 99.8876 | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `total_parts_processed` | int64 | 235 | EXCLUDED - target-derived or known only after the shift |
| `wip_queue_avg_units` | float64 | 0.1 | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `wip_queue_max_units` | int64 | 0 | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `output_variance_pct` | float64 | -6.75 | EXCLUDED - target-derived or known only after the shift |
| `units_per_operator_hour` | float64 | 4.93 | EXCLUDED - target-derived or known only after the shift |
| `planned_production_time_minutes` | float64 | 475.1 | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `available_time_minutes` | float64 | 475.1 | EXCLUDED - target-derived or known only after the shift |
| `oee_availability` | float64 | 1.0 | EXCLUDED - target-derived or known only after the shift |
| `oee_performance` | float64 | 0.9282 | EXCLUDED - target-derived or known only after the shift |
| `oee_quality` | float64 | 0.9957 | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `oee_overall` | float64 | 0.9243 | EXCLUDED - target-derived or known only after the shift |
| `teep_pct` | float64 | 30.5 | EXCLUDED - target-derived or known only after the shift |
| `loading_pct` | float64 | 32.99 | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `availability_loss_minutes` | float64 | 0.0 | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `performance_loss_units` | float64 | 18.2 | EXCLUDED - target-derived or known only after the shift |
| `quality_loss_units` | int64 | 1 | EXCLUDED - target-derived or known only after the shift |
| `six_big_losses_breakdown` | str | idling_minor_stops | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `oee_benchmark_class` | str | world_class | EXCLUDED - target-derived or known only after the shift |
| `oee_loss_primary_driver` | str | performance_loss | EXCLUDED - target-derived or known only after the shift |
| `changeover_time_minutes` | float64 | 0.0 | Feature (shift model only) |
| `changeover_count` | int64 | 0 | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `downtime_unplanned_minutes` | float64 | 0.0 | Feature (shift model only) |
| `downtime_planned_minutes` | float64 | 0.0 | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `downtime_event_count` | int64 | 0 | Feature (shift model only) |
| `mtbf_minutes` | float64 | 475.1 | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `mttr_minutes` | float64 | 0.0 | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `largest_downtime_event_minutes` | float64 | 0.0 | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `equipment_failure_flag` | str | no | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `downtime_category_mechanical` | float64 | 0.0 | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `downtime_category_electrical` | float64 | 0.0 | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `downtime_category_tooling` | float64 | 0.0 | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `downtime_category_material` | float64 | 0.0 | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `downtime_category_operator` | float64 | 0.0 | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `downtime_category_quality_hold` | float64 | 0.0 | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `planned_maintenance_flag` | str | no | Feature (plan + shift models) |
| `maintenance_type_last` | str | predictive | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `equipment_age_years` | float64 | 6.6 | Feature (plan + shift models) |
| `equipment_condition_score` | float64 | 4.8 | Feature (plan + shift models) |
| `operator_headcount_planned` | int64 | 7 | Feature (plan + shift models) |
| `operator_headcount_actual` | int64 | 6 | Feature (shift model only) |
| `operator_utilisation_pct` | float64 | 84.8 | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `operator_skill_level_avg` | str | expert | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `absenteeism_rate_pct` | float64 | 12.6 | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `overtime_hours` | float64 | 2.0 | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `ergonomic_incident_flag` | str | no | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `operator_variance_flag` | str | no | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `cross_training_ratio_pct` | float64 | 31.7 | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `shift_supervisor_id` | str | SUP-089 | Identifier / analysis only (not a feature) |
| `defect_rate_ppm` | float64 | 1124.0 | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `sigma_level` | float64 | 4.56 | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `cpk_primary_characteristic` | float64 | 1.02 | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `cp_primary_characteristic` | float64 | 1.03 | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `primary_defect_type` | str | dimensional_out_of_spec | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `secondary_defect_type` | str | assembly_error | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `inspection_method` | str | sampling_plan_ansi | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `spc_control_chart_flag` | str | yes | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `control_chart_out_of_control` | str | no | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `quality_alert_issued` | str | no | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `customer_complaint_flag` | str | no | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `first_pass_yield_pct` | float64 | 99.8876 | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `right_first_time_pct` | float64 | 97.6058 | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `energy_consumption_kwh` | float64 | 950.5 | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `energy_per_good_unit_kwh` | float64 | 4.062 | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `peak_demand_kw` | float64 | 159.4 | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `compressed_air_consumption_m3` | float64 | 66.7 | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `coolant_consumption_litres` | float64 | 17.1 | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `energy_efficiency_score` | float64 | 7.3 | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `carbon_footprint_kg_co2` | float64 | 399.2 | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `direct_labour_cost_usd` | float64 | 2262.01 | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `overhead_cost_usd` | float64 | 5082.56 | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `material_cost_per_unit_usd` | float64 | 88.54 | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `scrap_cost_usd` | float64 | 0.0 | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `rework_cost_usd` | float64 | 22.14 | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `downtime_cost_per_minute_usd` | int64 | 100 | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `total_downtime_cost_usd` | float64 | 0.0 | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `cost_of_poor_quality_usd` | float64 | 22.14 | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `value_added_ratio_pct` | float64 | 32.8 | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `production_cost_per_unit_usd` | float64 | 120.3054 | Not used (outcome-side or unrelated to delay; kept for analysis) |
| `planned_load_ratio` | engineered | planned_qty x takt / shift seconds | Feature (plan + shift) |
| `cycle_time_ratio` | engineered | actual / designed cycle time | Feature (shift) |
| `downtime_share` | engineered | unplanned downtime / shift duration | Feature (shift) |
| `headcount_ratio` | engineered | operators actual / planned | Feature (shift) |
| `achievement_pct` | derived target | actual / planned x 100 | TARGET (regression) |
| `delay_risk` | derived target | High <60, Medium <75, Low otherwise | TARGET (classification) |

## Notes on leakage
`oee_overall` correlates 0.99 with achievement, and quantity-based columns (throughput, units, variance) are the target itself in another form, so none of them is an input. `available_time_minutes` equals planned time minus downtime and is known only after the shift, so the model uses `downtime_unplanned_minutes` as an explicit, labelled input instead.
