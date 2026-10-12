"""Full-stack supply-chain risk monitoring, with data fetched from FastAPI."""
import os
import requests
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Supply Chain Risk Control Center", layout="wide")
st.title("Supply Chain Risk Forecasting")
st.caption("Bronze / Silver / Gold · Supplier-level analytics · Synthetic research model")
api = os.getenv("API_URL", "http://127.0.0.1:8000")


def get(path):
    try:
        response = requests.get(api + path, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return {}


metrics = get("/api/pipeline/metrics").get("metrics")
if metrics:
    a, b, c = st.columns(3)
    a.metric("Raw records", metrics["raw"])
    b.metric("Validated records", metrics["clean"])
    c.metric("Rejected records", metrics["rejected"])
else:
    st.info("Run the ETL pipeline to generate monitoring metrics.")

st.subheader("Forecast disruption risk")
a, b, c = st.columns(3)
lead = a.number_input("Lead time (days)", min_value=0, max_value=365, value=8)
demand = b.number_input("Daily demand (units)", min_value=0, value=32)
inventory = c.number_input("Inventory (units)", min_value=0, value=240)
rate = a.slider("Supplier on-time rate", 0.0, 1.0, 0.9)
delay = b.number_input("Transport delay (days)", min_value=0, max_value=365, value=2)

if st.button("Forecast disruption risk"):
    payload = {"lead_time_days": int(lead), "daily_demand": int(demand),
               "inventory_units": int(inventory), "supplier_on_time_rate": rate,
               "transport_delay_days": int(delay)}
    try:
        response = requests.post(api + "/api/forecast", json=payload, timeout=15)
        response.raise_for_status()
        result = response.json()
        st.metric("Estimated disruption probability", f"{result['estimated_disruption_risk']:.1%}")
        st.info(result["disclaimer"])
    except requests.RequestException as exc:
        st.error(f"Risk model unavailable: {exc}")

st.subheader("Supplier analytics")
data = get("/api/suppliers").get("suppliers", [])
if data:
    frame = pd.DataFrame(data)
    st.dataframe(frame, use_container_width=True)
    st.bar_chart(frame.set_index("supplier_id")["disruption_rate"])
else:
    st.caption("No Gold analytics yet. Run the pipeline first.")
