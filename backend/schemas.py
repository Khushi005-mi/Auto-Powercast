from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class ProjectInputSchema(BaseModel):
    capacity_mw: float = Field(..., ge=1.0, le=5000.0, description="Installed power capacity in Megawatts", example=250.0)
    project_type: str = Field(..., description="Energy technology type", example="Solar PV")
    region: str = Field(..., description="Geographical deployment region", example="North America")
    contractor_tier: str = Field(default="Tier-1", description="Contractor qualification level", example="Tier-1")

class PredictionResponseSchema(BaseModel):
    estimated_cost_usd_millions: float
    estimated_duration_months: float
    risk_assessment: Dict[str, Any]
