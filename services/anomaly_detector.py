"""Isolation Forest anomaly detection with a transparent rules fallback."""

import numpy as np
from sklearn.ensemble import IsolationForest

FEATURES = (
    "cpu_usage",
    "memory_usage",
    "disk_usage",
    "network_latency",
    "error_rate",
    "response_time",
)
MIN_TRAINING_SAMPLES = 12


def threshold_anomaly(values):
    """Return True if any metric is outside a sensible operating range."""
    return (
        values["cpu_usage"] >= 90
        or values["memory_usage"] >= 90
        or values["disk_usage"] >= 92
        or values["network_latency"] >= 250
        or values["error_rate"] >= 5
        or values["response_time"] >= 1200
    )


def detect_anomaly(history, values):
    """Classify metric values; history must exclude the metric being assessed."""
    if len(history) < MIN_TRAINING_SAMPLES:
        return threshold_anomaly(values), "threshold"

    try:
        matrix = np.array([[getattr(item, field) for field in FEATURES] for item in history])
        candidate = np.array([[values[field] for field in FEATURES]])
        model = IsolationForest(contamination=0.12, random_state=42, n_estimators=100)
        model.fit(matrix)
        model_result = model.predict(candidate)[0] == -1
        # Hard limits always win even when a training sample is unusually noisy.
        return bool(model_result or threshold_anomaly(values)), "isolation_forest"
    except (ValueError, TypeError, np.linalg.LinAlgError):
        return threshold_anomaly(values), "threshold"
