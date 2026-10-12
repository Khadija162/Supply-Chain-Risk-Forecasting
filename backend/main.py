"""Supply chain risk serving API. Local research demo, not authenticated for production."""
import os
from pathlib import Path
from functools import lru_cache
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, ConfigDict
from src.features import FEATURES

app = FastAPI(title="Supply Chain Risk Forecasting API", version="0.2.0")


class ShipmentFeatures(BaseModel):
    model_config = ConfigDict(extra="forbid")
    lead_time_days: int = Field(ge=0, le=365)
    daily_demand: int = Field(ge=0)
    inventory_units: int = Field(ge=0)
    supplier_on_time_rate: float = Field(ge=0, le=1, allow_inf_nan=False)
    transport_delay_days: int = Field(ge=0, le=365)


@lru_cache(maxsize=1)
def model():
    path = Path(os.getenv("MODEL_PATH", "models/risk_model.joblib"))
    if not path.is_file():
        raise FileNotFoundError("Train the risk model first")
    return joblib.load(path)  # Trusted, locally trained model artifacts only.


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
    return {"estimated_disruption_risk": round(probability, 4),
            "risk_level": "high" if probability >= .5 else "low",
            "disclaimer": "Synthetic research model; not a validated business forecast"}


@app.get("/api/suppliers")
def suppliers():
    """Read model-independent Gold analytics rather than exposing local file paths."""
    path = Path(os.getenv("GOLD_SUPPLIERS_PATH", "data/gold/supplier_risk.parquet"))
    if not path.is_file():
        return {"suppliers": [], "message": "Run python -m src.pipeline first"}
    df = pd.read_parquet(path).sort_values("disruption_rate", ascending=False)
    return {"suppliers": df.to_dict(orient="records")}


@app.get("/api/pipeline/metrics")
def pipeline_metrics():
    import json
    path = Path(os.getenv("PIPELINE_METRICS_PATH", "data/gold/pipeline_metrics.json"))
    return {"metrics": json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None}
