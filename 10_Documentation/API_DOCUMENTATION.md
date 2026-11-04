# API
Start: `uvicorn main:app --app-dir 06_API --port 8000`. Swagger UI: `/docs`.
| Endpoint | Description |
|---|---|
| `GET /health` | `{status, model_loaded}` |
| `GET /model-info` | metadata, selected models, test metrics (503 if not trained) |
| `POST /predict` | JSON body below; returns the result. 422 for invalid input |
| `POST /upload-csv?mode=shift\|plan&limit=1000` | multipart CSV; validates, predicts; 400 wrong type/unreadable, 413 >20 MB, 422 invalid columns |
| `GET /sample-data?rows=20&download=false` | sample rows as JSON, or the CSV file |

Example `/predict` body (`mode` = `shift`):
```json
{"mode":"shift","shift_number":2,"shift_duration_minutes":450,"planned_production_quantity":500,"number_of_stations":5,
 "takt_time_seconds":60,"designed_cycle_time_seconds":55,"equipment_age_years":15,"equipment_condition_score":6,
 "operator_headcount_planned":10,"product_family":"automotive_body","line_type":"assembly_line","automation_level":"manual",
 "line_configuration":"serial","planned_maintenance_flag":"no","downtime_unplanned_minutes":60,
 "actual_cycle_time_avg_seconds":65,"operator_headcount_actual":9,"changeover_time_minutes":0,"downtime_event_count":3}
```
Response fields: `mode, prediction_type, delay_risk, risk_probabilities, predicted_production, target_achievement_percentage, possible_bottleneck, recommended_action`. Allowed categories are listed in `06_API/schemas.py`.
