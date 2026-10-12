"""Supply chain risk serving API. No public deployment without authentication."""
import os
from pathlib import Path
from functools import lru_cache
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, ConfigDict
from src.features import FEATURES

app = FastAPI(title="Supply Chain Risk Forecasting API", version="0.1.0")


class ShipmentFeatures(BaseModel):
    model_config = ConfigDict(extra="forbid")
    lead_time_days: int = Field(ge=0, le=365)
    daily_demand: int = Field(ge=0)
    inventory_units: int = Field(ge=0)
    supplier_on_time_rate: float = Field(ge=0, le=1)
    transport_delay_days: int = Field(ge=0, le=365)


@lru_cache(maxsize=1)
def model():
    path = Path(os.getenv("MODEL_PATH", "models/risk_model.joblib"))
    if not path.is_file():
        raise FileNotFoundError("Train the risk model first")
    return joblib.load(path)  # Never load untrusted artifacts.


@app.get("/health")
def health():
    return {"status": "ok", "model_ready": Path(os.getenv("MODEL_PATH", "models/risk_model.joblib")).is_file()}


@app.post("/api/forecast")
def forecast(features: ShipmentFeatures):
    try:
        fitted = model()
    except FileNotFoundError as exc:
        raise HTTPException(503, str(exc)) from exc
    frame = pd.DataFrame([features.model_dump()])[FEATURES]
    probability = float(fitted.predict_proba(frame)[0, 1])
    return {"estimated_disruption_risk": round(probability, 4), "risk_level": "high" if probability >= .5 else "low", "disclaimer": "Synthetic research model; not a validated business forecast"}
