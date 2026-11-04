from typing import Literal, Optional
from pydantic import BaseModel, Field, model_validator

CATS = {
    "product_family": ["industrial_machinery", "automotive_body", "pharmaceutical", "food_beverage", "electronics_pcb", "medical_devices"],
    "line_type": ["chemical_process", "continuous_process", "fabrication", "hybrid", "packaging_line", "machining_cell",
                  "discrete_manufacturing", "batch_process", "assembly_line"],
    "automation_level": ["semi_automated", "lights_out", "manual", "highly_automated", "cobotic"],
    "line_configuration": ["job_shop", "serial", "transfer_line", "parallel", "flexible", "u_shaped"],
}


class PredictRequest(BaseModel):
    mode: Literal["plan", "shift"] = Field("shift", description="plan = pre-shift estimate; shift = current-shift estimate")
    shift_number: int = Field(..., ge=1, le=3)
    shift_duration_minutes: float = Field(..., gt=0, le=1440)
    planned_production_quantity: int = Field(..., gt=0)
    number_of_stations: int = Field(..., ge=1, le=100)
    takt_time_seconds: float = Field(..., gt=0)
    designed_cycle_time_seconds: float = Field(..., gt=0)
    equipment_age_years: float = Field(..., ge=0, le=100)
    equipment_condition_score: float = Field(..., ge=0, le=10)
    operator_headcount_planned: int = Field(..., ge=1, le=1000)
    product_family: str
    line_type: str
    automation_level: str
    line_configuration: str
    planned_maintenance_flag: Literal["yes", "no"] = "no"
    # needed only for mode="shift"
    downtime_unplanned_minutes: Optional[float] = Field(None, ge=0)
    actual_cycle_time_avg_seconds: Optional[float] = Field(None, gt=0)
    operator_headcount_actual: Optional[int] = Field(None, ge=0)
    changeover_time_minutes: Optional[float] = Field(None, ge=0)
    downtime_event_count: Optional[int] = Field(None, ge=0)

    @model_validator(mode="after")
    def _check(self):
        for k, allowed in CATS.items():
            if getattr(self, k) not in allowed:
                raise ValueError(f"{k} must be one of {allowed}")
        if self.mode == "shift":
            need = ["downtime_unplanned_minutes", "actual_cycle_time_avg_seconds", "operator_headcount_actual",
                    "changeover_time_minutes", "downtime_event_count"]
            miss = [n for n in need if getattr(self, n) is None]
            if miss:
                raise ValueError(f"mode='shift' requires: {miss}")
            if self.downtime_unplanned_minutes > self.shift_duration_minutes:
                raise ValueError("downtime_unplanned_minutes cannot exceed shift_duration_minutes")
        return self


class PredictResponse(BaseModel):
    mode: str
    prediction_type: str
    delay_risk: Literal["Low", "Medium", "High"]
    risk_probabilities: dict[str, float]
    predicted_production: int
    target_achievement_percentage: float
    possible_bottleneck: str
    recommended_action: str
