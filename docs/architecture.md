# Supply chain risk platform

## Implemented locally
- An original openly licensed CC0 synthetic supply-chain dataset and reproducible generator.
- Batch Bronze/Silver/Gold Parquet ETL with quality rejection and supplier analytics.
- Random forest classification of simulated disruption risk, chronological holdout and PR-AUC/ROC-AUC metrics.
- FastAPI scoring and Streamlit dashboard.
- Docker Compose and GitHub Actions tests/build.

## Production roadmap
- Ingest real, appropriately licensed logistics/shipment/port/weather datasets with provenance and source contracts.
- Spark/Delta Lake for incremental large-data processing and historical snapshots.
- Postgres operational metadata and optional object storage for Parquet.
- Batch and event streams with orchestration, idempotency and lineage.
- Secure API deployment with auth, observability, model drift tests and controlled rollbacks.

This is a learning prototype, not a validated production-risk or supply-chain forecasting system.
