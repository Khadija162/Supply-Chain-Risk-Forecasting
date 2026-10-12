"""Deterministic original synthetic open dataset. CC0; not real supply-chain observations."""
from pathlib import Path
import numpy as np
import pandas as pd


def generate(rows=600, seed=42):
    rng = np.random.default_rng(seed)
    date = pd.date_range("2024-01-01", periods=rows, freq="D")
    supplier = rng.choice(["A", "B", "C", "D"], rows)
    lead = rng.integers(2, 19, rows)
    demand = rng.integers(8, 70, rows)
    inventory = rng.integers(20, 1000, rows)
    on_time = rng.uniform(.55, 1.0, rows)
    delay = rng.integers(0, 9, rows)
    # Risk is an illustrative, synthetic outcome. No actual real-world failures.
    risk_score = (inventory < demand * (lead + delay)) * 1.3 + (on_time < .77) * .9 + (delay >= 4) * .7
    risk = (risk_score >= 1.6).astype(int)
    return pd.DataFrame({
        "date": date.strftime("%Y-%m-%d"),
        "supplier_id": supplier,
        "lead_time_days": lead,
        "daily_demand": demand,
        "inventory_units": inventory,
        "supplier_on_time_rate": on_time.round(3),
        "transport_delay_days": delay,
        "disruption_risk": risk,
    })


if __name__ == "__main__":
    path = Path("data/public/supply_chain_synthetic.csv")
    path.parent.mkdir(parents=True, exist_ok=True)
    generate().to_csv(path, index=False)
    print(f"Wrote {path}")
