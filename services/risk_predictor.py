"""Interpretable failure-risk scoring for a metric sample."""


def _ratio(value, warning, critical):
    if value <= warning:
        return 0.0
    return min(1.0, (value - warning) / (critical - warning))


def calculate_failure_risk(values, is_anomaly=False):
    """Calculate a weighted 0-100 score from operating-system signals."""
    score = (
        _ratio(values["cpu_usage"], 55, 100) * 18
        + _ratio(values["memory_usage"], 60, 100) * 16
        + _ratio(values["disk_usage"], 70, 100) * 14
        + _ratio(values["network_latency"], 80, 400) * 12
        + _ratio(values["network_traffic"], 180, 650) * 5
        + _ratio(values["error_rate"], 0.5, 10) * 16
        + _ratio(values["response_time"], 350, 2000) * 12
        + _ratio(values["system_load"], 2.0, 16) * 7
    )
    if is_anomaly:
        score += 12
    return round(min(100, max(0, score)), 1)


def risk_label(risk):
    if risk <= 30:
        return "Low"
    if risk <= 60:
        return "Medium"
    if risk <= 80:
        return "High"
    return "Critical"


def severity_for(values, risk):
    """Map the full metric context to an incident severity."""
    if risk > 80 or values["error_rate"] >= 8 or values["response_time"] >= 1800:
        return "Critical"
    if risk > 60 or values["cpu_usage"] >= 90 or values["memory_usage"] >= 90:
        return "High"
    if risk > 30 or values["network_latency"] >= 180 or values["disk_usage"] >= 88:
        return "Medium"
    return "Low"
