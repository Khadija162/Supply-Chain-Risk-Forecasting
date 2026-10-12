from fastapi.testclient import TestClient
from backend.main import app
from src.dataset import generate
from src.pipeline import run
from src.train import train


def test_data_generator():
    df = generate(120)
    assert len(df) == 120
    assert set(df["disruption_risk"].unique()).issubset({0, 1})


def test_etl(tmp_path):
    path = tmp_path / "data.csv"
    generate(120).to_csv(path, index=False)
    result = run(str(path), str(tmp_path / "lake"))
    assert result["raw"] == 120
    assert result["clean"] == 120
    assert result["suppliers"] == 4


def test_api_validation():
    client = TestClient(app)
    assert client.get("/health").status_code == 200
    assert client.post("/api/forecast", json={"lead_time_days": 4}).status_code == 422


def test_gold_analytics_api(tmp_path, monkeypatch):
    source = tmp_path / "data.csv"
    generate(120).to_csv(source, index=False)
    run(str(source), str(tmp_path / "lake"))
    monkeypatch.setenv("GOLD_SUPPLIERS_PATH", str(tmp_path / "lake/gold/supplier_risk.parquet"))
    monkeypatch.setenv("PIPELINE_METRICS_PATH", str(tmp_path / "lake/gold/pipeline_metrics.json"))
    client = TestClient(app)
    response = client.get("/api/suppliers")
    assert response.status_code == 200
    assert len(response.json()["suppliers"]) == 4
    assert client.get("/api/pipeline/metrics").json()["metrics"]["raw"] == 120


def test_missing_gold_files(tmp_path, monkeypatch):
    monkeypatch.setenv("GOLD_SUPPLIERS_PATH", str(tmp_path / "missing.parquet"))
    monkeypatch.setenv("PIPELINE_METRICS_PATH", str(tmp_path / "missing.json"))
    client = TestClient(app)
    assert client.get("/api/suppliers").json()["suppliers"] == []
    assert client.get("/api/pipeline/metrics").json()["metrics"] is None
