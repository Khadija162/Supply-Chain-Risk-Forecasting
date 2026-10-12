import os
import requests
import streamlit as st

st.set_page_config(page_title="Supply Chain Risk Control Center", layout="wide")
st.title("Supply Chain Risk Forecasting")
st.caption("Data engineering + risk analytics + ML · Openly licensed synthetic sample")
api = os.getenv("API_URL", "http://127.0.0.1:8000")
a, b, c = st.columns(3)
lead = a.number_input("Lead time (days)", min_value=0, max_value=365, value=8)
demand = b.number_input("Daily demand (units)", min_value=0, value=32)
inventory = c.number_input("Inventory (units)", min_value=0, value=240)
rate = a.slider("Supplier on-time rate", 0.0, 1.0, 0.9)
delay = b.number_input("Transport delay (days)", min_value=0, max_value=365, value=2)
if st.button("Forecast disruption risk"):
    payload = {"lead_time_days": lead, "daily_demand": demand, "inventory_units": inventory, "supplier_on_time_rate": rate, "transport_delay_days": delay}
    try:
        result = requests.post(api + "/api/forecast", json=payload, timeout=15)
        result.raise_for_status()
        estimate = result.json()
        st.metric("Estimated disruption probability", f"{estimate['estimated_disruption_risk']:.1%}")
        st.info(estimate["disclaimer"])
    except requests.RequestException as exc:
        st.error(str(exc))

st.subheader("Supplier analytics")
try:
    import pandas as pd
    from pathlib import Path
    path = Path("data/gold/supplier_risk.parquet")
    if path.exists():
        st.dataframe(pd.read_parquet(path), use_container_width=True)
    else:
        st.caption("Run the ETL pipeline to create supplier analytics.")
except Exception:
    st.caption("Supplier analytics unavailable.")
