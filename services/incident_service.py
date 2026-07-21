import json
import uuid

from models import db
from models.alert import Alert
from models.incident import Incident
from services.gemini_service import get_ai_analysis
from services.risk_predictor import severity_for


def describe_issue(values):
    contributors = []
    if values["cpu_usage"] >= 85:
        contributors.append("high CPU")
    if values["memory_usage"] >= 85:
        contributors.append("high memory")
    if values["disk_usage"] >= 88:
        contributors.append("disk capacity")
    if values["network_latency"] >= 180:
        contributors.append("high network latency")
    if values["error_rate"] >= 3:
        contributors.append("application errors")
    if values["response_time"] >= 900:
        contributors.append("slow response time")
    return contributors or ["abnormal performance pattern"]


def create_incident_if_needed(server, metric, threshold):
    """Create one active incident per server, preventing alert storms."""
    if not metric.is_anomaly and metric.failure_risk < threshold:
        return None

    active = server.incidents.filter(Incident.status.in_(["Open", "Investigating"])).first()
    if active:
        return active

    values = metric.as_dict()
    contributors = describe_issue(values)
    severity = severity_for(values, metric.failure_risk)
    analysis = get_ai_analysis(server, values, metric.failure_risk, severity)
    incident = Incident(
        incident_code=f"INC-{uuid.uuid4().hex[:8].upper()}",
        server=server,
        title=f"{severity} infrastructure alert: {', '.join(contributors[:2])}",
        description=(
            f"Automated monitoring detected {', '.join(contributors)} on {server.name}. "
            f"The calculated failure risk is {metric.failure_risk}% and anomaly status is {metric.is_anomaly}."
        ),
        severity=severity,
        failure_risk=metric.failure_risk,
        detected_metrics=json.dumps(values),
        ai_root_cause=analysis["root_cause"],
        ai_recommendation=analysis["recommendation"],
        issue_fingerprint="performance",
    )
    db.session.add(incident)
    db.session.add(
        Alert(
            user_id=server.user_id,
            server_id=server.id,
            title=f"{severity} incident created for {server.name}",
            message=f"{incident.incident_code}: {incident.title}",
        severity="Critical" if severity == "Critical" else "Warning",
        )
    )
    return incident
