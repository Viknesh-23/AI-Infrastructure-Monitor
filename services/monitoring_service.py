import random

from models import db
from models.alert import Alert
from models.metric import Metric
from services.anomaly_detector import detect_anomaly
from services.incident_service import create_incident_if_needed
from services.risk_predictor import calculate_failure_risk, risk_label


def _normal_values():
    return {
        "cpu_usage": round(random.uniform(18, 68), 1),
        "memory_usage": round(random.uniform(28, 72), 1),
        "disk_usage": round(random.uniform(35, 78), 1),
        "network_latency": round(random.uniform(15, 105), 1),
        "network_traffic": round(random.uniform(15, 180), 1),
        "error_rate": round(random.uniform(0, 1.8), 2),
        "response_time": round(random.uniform(80, 550), 1),
        "system_load": round(random.uniform(0.25, 2.8), 2),
    }


def _failure_values():
    return {
        "cpu_usage": round(random.uniform(91, 99), 1),
        "memory_usage": round(random.uniform(88, 98), 1),
        "disk_usage": round(random.uniform(82, 98), 1),
        "network_latency": round(random.uniform(270, 700), 1),
        "network_traffic": round(random.uniform(220, 650), 1),
        "error_rate": round(random.uniform(5.5, 18), 2),
        "response_time": round(random.uniform(1300, 3500), 1),
        "system_load": round(random.uniform(6, 16), 2),
    }


def generate_metric(server, simulate_failure=False, incident_threshold=65):
    """Generate, score, and persist one simulated metric record."""
    values = _failure_values() if simulate_failure else _normal_values()
    history = server.metrics.order_by(Metric.timestamp.desc()).limit(60).all()
    is_anomaly, method = detect_anomaly(history, values)
    risk = calculate_failure_risk(values, is_anomaly)
    metric = Metric(
        server=server,
        **values,
        is_anomaly=is_anomaly,
        anomaly_method=method,
        risk_score=risk,
    )
    db.session.add(metric)
    db.session.flush()

    if risk >= 81:
        server.status = "Critical"
    elif risk >= 45 or is_anomaly:
        server.status = "Warning"
    else:
        server.status = "Healthy"

    incident = create_incident_if_needed(server, metric, incident_threshold)
    if is_anomaly and not incident:
        db.session.add(
            Alert(
                user_id=server.user_id,
                server_id=server.id,
                title=f"Anomaly detected on {server.name}",
                message=f"Metric outlier detected via {method.replace('_', ' ')}. Risk: {risk}% ({risk_label(risk)}).",
                severity="Warning",
            )
        )
    return metric, incident
