"""Chronological holdout forecasting baseline; evaluate future periods rather than random rows."""
import argparse
import json
from pathlib import Path
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import average_precision_score, roc_auc_score, precision_recall_fscore_support
from .features import FEATURES, TARGET


def train(source="data/public/supply_chain_synthetic.csv", output="models/risk_model.joblib"):
    df = pd.read_csv(source).sort_values("date")
    if not set(FEATURES + [TARGET]).issubset(df.columns):
        raise ValueError("Missing feature or target columns")
    split = int(len(df) * .8)
    x_train, x_test = df[FEATURES].iloc[:split], df[FEATURES].iloc[split:]
    y_train, y_test = df[TARGET].iloc[:split], df[TARGET].iloc[split:]
    if y_train.nunique() != 2 or y_test.nunique() != 2:
        raise ValueError("Need two outcome classes in both periods")
    model = RandomForestClassifier(n_estimators=150, min_samples_leaf=3, random_state=42, n_jobs=-1)
    model.fit(x_train, y_train)
    p = model.predict_proba(x_test)[:, 1]
    precision, recall, f1, _ = precision_recall_fscore_support(y_test, (p >= .5).astype(int), average="binary", zero_division=0)
    metrics = {"train_rows": len(x_train), "test_rows": len(x_test), "average_precision": float(average_precision_score(y_test, p)), "roc_auc": float(roc_auc_score(y_test, p)), "precision": float(precision), "recall": float(recall), "f1": float(f1), "evaluation": "chronological holdout on synthetic heuristic-generated targets"}
    target = Path(output)
    target.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, target)
    target.with_suffix(".metrics.json").write_text(json.dumps(metrics, indent=2))
    return metrics


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--source", default="data/public/supply_chain_synthetic.csv")
    args = p.parse_args()
    print(json.dumps(train(args.source), indent=2))
