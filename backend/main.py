from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import joblib

app = FastAPI(
    title="Auto PowerCast"
)

# Load models
cost_model = joblib.load("../cost_model.pkl")
duration_model = joblib.load("../duration_model.pkl")
risk_model = joblib.load("../risk_model.pkl")
encoder = joblib.load("../encoder.pkl")

class ProjectInput(BaseModel):
    project_type: str
    state: str
    region: str
    capacity_mw: int
    sanctioned_budget_cr: float
    planned_duration_months: int
    contractor_count: int
    land_acquisition_status: str
    project_complexity: str
    cost_overrun_pct: float
    delay_months: float

@app.get("/")
def home():
       return {
        "message": "Auto PowerCast API Running"
    }

@app.post("/predict")
def predict(data: ProjectInput):

    input_dict = {
        "project_type": [data.project_type],
        "state": [data.state],
        "region": [data.region],
        "capacity_mw": [data.capacity_mw],
        "sanctioned_budget_cr": [data.sanctioned_budget_cr],
        "planned_duration_months": [data.planned_duration_months],
        "contractor_count": [data.contractor_count],
        "land_acquisition_status": [data.land_acquisition_status],
        "project_complexity": [data.project_complexity],
        "cost_overrun_pct": [data.cost_overrun_pct],
        "delay_months": [data.delay_months]
    }

    input_df = pd.DataFrame(input_dict)


    categorical_cols = [
        "project_type",
        "state",
        "region",
        "land_acquisition_status",
        "project_complexity"
    ]

    encoded = encoder.transform(
        input_df[categorical_cols]
    )

    encoded_df = pd.DataFrame(
        encoded,
        columns=encoder.get_feature_names_out(
            categorical_cols
        )
    )    
    numeric_df = input_df.drop(
        columns=categorical_cols
    )

    final_df = pd.concat(
        [
            numeric_df.reset_index(drop=True),
            encoded_df.reset_index(drop=True)
        ],
        axis=1
    )
    predicted_cost = float(
        cost_model.predict(final_df)[0]
    )

    predicted_duration = float(
        duration_model.predict(final_df)[0]
    )

    predicted_risk = str(
        risk_model.predict(final_df)[0]
    )

    return {
        "predicted_cost_cr": round(predicted_cost, 2),
        "predicted_duration_months": round(predicted_duration, 2),
        "predicted_risk_level": predicted_risk
    }
