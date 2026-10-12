# Supply Chain Risk Forecasting — Data Engineering + AI + Full Stack

An end-to-end **local research prototype** for supply-chain disruption risk analytics: an openly licensed synthetic dataset, batch Bronze/Silver/Gold data pipeline, machine-learning risk classification, FastAPI backend, Streamlit dashboard, Docker Compose and GitHub Actions CI.

> **Status:** Source and configuration committed; end-to-end runtime and CI results are not yet independently verified. This model predicts a synthetic target generated from input features; do not use its estimates for real operational decisions.

## Architecture

```text
CC0 synthetic supply-chain dataset
  ├── Pandas ingestion → Bronze Parquet → validated Silver Parquet → Gold supplier analytics
  └── chronological training split → RandomForest risk model
                                              |
                               FastAPI /api/forecast
                                              |
                                 Streamlit frontend
             Docker Compose · pytest · GitHub Actions
```

## Included open data

[data/public/supply_chain_synthetic.csv](data/public/supply_chain_synthetic.csv) contains **600 originally generated, synthetic shipments**. It is made openly available under **CC0 1.0**. See [data details and provenance](data/public/README.md).

**Important:** Openly licensed is not the same as real-world. These are illustrative observations and heuristic-generated disruption labels, **not actual shipping incidents**. Model metrics cannot be used as evidence of real-world forecasting performance.

## Windows quick start

```powershell
git clone https://github.com/Khadija162/Supply-Chain-Risk-Forecasting.git
cd Supply-Chain-Risk-Forecasting
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m src.pipeline
.\.venv\Scripts\python.exe -m src.train
.\.venv\Scripts\python.exe -m pytest -q
```

You can regenerate similar seeded synthetic examples using `python -m src.dataset`; this **overwrites the included sample CSV** with newly generated values.

## Launch the application

Terminal 1:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload
```

Terminal 2:

```powershell
.\.venv\Scripts\python.exe -m streamlit run frontend/app.py
```

- API documentation: http://127.0.0.1:8000/docs
- Frontend dashboard: http://127.0.0.1:8501

Or run the containers **after training creates** `models/risk_model.joblib`:

```powershell
docker compose up --build
```

Docker ports bind to localhost; the model artifact remains a host-side file mounted read-only in the API service.

## Files

| Folder | Contents |
|---|---|
| `data/public/` | Included CC0 synthetic dataset and provenance |
| `src/pipeline.py` | Bronze/Silver/Gold ETL, validations and supplier metrics |
| `src/train.py` | Risk model and chronological evaluation |
| `backend/main.py` | FastAPI /api/forecast |
| `frontend/app.py` | Streamlit risk dashboard |
| `tests/` | API and pipeline tests |
| `.github/workflows/` | Python tests and Docker build |
| `Dockerfile`, `docker-compose.yml` | Local containers |
| `docs/architecture.md` | Scope, limitations, future improvements |

## Next engineering upgrades

Add real licensed transportation/shipment datasets, incremental Spark/Delta Lake processing, drift monitoring, orchestration and secure cloud deployment. Real-world validation should include data temporal integrity, leakage checks, well-defined prediction horizons, monitored label availability and operational review.

**Security:** The prototype API has no authentication. Never expose it publicly without authorization, rate limits, secret handling and monitoring. No cloud services have been provisioned.

## Full-stack dashboard enhancements (October 2026)

The dashboard now reads the Gold supplier analytics and ETL run metrics through FastAPI, including within Docker Compose. Added API endpoints:

- `GET /api/suppliers`: supplier-level disruption rates from Gold Parquet
- `GET /api/pipeline/metrics`: raw, clean, rejected and supplier counts
- `POST /api/forecast`: research-only shipment risk probability

The container API mounts `data/gold/` read-only. Generate pipeline data and train the model **before** launching `docker compose up --build`. The frontend no longer needs direct access to local Gold Parquet files.

This repository uses original **CC0 synthetic open data**, not an external dataset of actual disruptions. It is sufficient for demonstrating ETL, API, forecasting and container integration but not for claiming real-world forecast accuracy. Continuous ingestion, probabilistic time-series forecasting, cloud deployment and production monitoring remain future work.
