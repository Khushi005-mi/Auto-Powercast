from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.schemas import ProjectInputSchema, PredictionResponseSchema
from models.predictor import PowercastPredictor

app = FastAPI(
    title="Auto-Powercast API",
    description="Multi-Task Energy Infrastructure Budgeting & Risk Forecasting Engine",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

predictor = PowercastPredictor()

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "Auto-Powercast Intelligence Engine"}

@app.post("/predict", response_model=PredictionResponseSchema)
def predict_project(payload: ProjectInputSchema):
    try:
        results = predictor.predict(payload.model_dump())
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
