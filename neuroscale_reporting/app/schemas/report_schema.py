from pydantic import BaseModel
from typing import List

class ResourceMetric(BaseModel):
    timestamp: str
    lstm_predicted_cpu: float
    ppo_target_replicas: int

class NeuroScaleReportData(BaseModel):
    report_title: str
    start_date: str
    end_date: str
    total_cost_saved: float
    overload_prevented_events: int
    drift_status: str
    metrics: List[ResourceMetric]
