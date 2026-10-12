"""Bronze/Silver/Gold Parquet analytics and validation."""
import argparse
import json
from pathlib import Path
import pandas as pd
from .features import FEATURES, TARGET


def run(source="data/public/supply_chain_synthetic.csv", output="data"):
    frame = pd.read_csv(source)
    expected = {"date", "supplier_id", *FEATURES, TARGET}
    missing = expected - set(frame.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")
    root = Path(output)
    for folder in ("bronze", "silver", "gold"):
        (root / folder).mkdir(parents=True, exist_ok=True)
    frame.to_parquet(root / "bronze" / "events.parquet", index=False)
    numeric = frame[FEATURES + [TARGET]].apply(pd.to_numeric, errors="coerce")
    valid = numeric.notna().all(axis=1)
    valid &= (numeric[FEATURES[:3]] >= 0).all(axis=1)
    valid &= numeric["supplier_on_time_rate"].between(0, 1)
    valid &= (numeric["transport_delay_days"] >= 0)
    valid &= numeric[TARGET].isin([0, 1])
    valid &= pd.to_datetime(frame["date"], errors="coerce").notna()
    valid &= frame["supplier_id"].notna()
    silver = frame.loc[valid].copy()
    silver.to_parquet(root / "silver" / "events.parquet", index=False)
    frame.loc[~valid].to_parquet(root / "silver" / "rejected.parquet", index=False)
    gold = silver.groupby("supplier_id", as_index=False).agg(
        shipments=("disruption_risk", "count"),
        disruptions=("disruption_risk", "sum"),
        average_lead_time=("lead_time_days", "mean"),
        average_on_time_rate=("supplier_on_time_rate", "mean"),
    )
    gold["disruption_rate"] = gold["disruptions"] / gold["shipments"]
    gold.to_parquet(root / "gold" / "supplier_risk.parquet", index=False)
    report = {"raw": len(frame), "clean": len(silver), "rejected": int((~valid).sum()), "suppliers": len(gold)}
    (root / "gold" / "pipeline_metrics.json").write_text(json.dumps(report, indent=2))
    return report


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--source", default="data/public/supply_chain_synthetic.csv")
    p.add_argument("--output", default="data")
    args = p.parse_args()
    print(run(args.source, args.output))
