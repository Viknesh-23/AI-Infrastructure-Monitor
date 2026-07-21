from flask import Blueprint, current_app, render_template
from flask_login import current_user, login_required

from models.alert import Alert
from models.incident import Incident

dashboard_bp = Blueprint("dashboard", __name__)


def _dashboard_stats(user):
    servers = user.servers
    latest_metrics = [server.latest_metric for server in servers]
    latest_metrics = [metric for metric in latest_metrics if metric]
    active_incidents = Incident.query.join(Incident.server).filter(
        Incident.server.has(user_id=user.id), Incident.status.in_(["Open", "Investigating"])
    ).count()
    resolved_incidents = Incident.query.join(Incident.server).filter(
        Incident.server.has(user_id=user.id), Incident.status == "Resolved"
    ).count()
    return {
        "total": len(servers),
        "healthy": sum(s.status == "Healthy" for s in servers),
        "warning": sum(s.status == "Warning" for s in servers),
        "critical": sum(s.status in ("Critical", "Offline") for s in servers),
        "active_incidents": active_incidents,
        "resolved_incidents": resolved_incidents,
        "avg_cpu": round(sum(m.cpu_usage for m in latest_metrics) / len(latest_metrics), 1) if latest_metrics else 0,
        "avg_memory": round(sum(m.memory_usage for m in latest_metrics) / len(latest_metrics), 1) if latest_metrics else 0,
    }


@dashboard_bp.route("/")
@dashboard_bp.route("/dashboard")
@login_required
def index():
    servers = current_user.servers
    alerts = Alert.query.filter_by(user_id=current_user.id).order_by(Alert.created_at.desc()).limit(6).all()
    recent_incidents = Incident.query.join(Incident.server).filter(
        Incident.server.has(user_id=current_user.id)
    ).order_by(Incident.created_at.desc()).limit(6).all()
    chart_servers = []
    for server in servers:
        metric = server.latest_metric
        if metric:
            chart_servers.append({"name": server.name, "cpu": metric.cpu_usage, "memory": metric.memory_usage, "risk": metric.failure_risk})
    return render_template(
        "dashboard.html",
        stats=_dashboard_stats(current_user),
        servers=servers,
        alerts=alerts,
        recent_incidents=recent_incidents,
        chart_servers=chart_servers,
    )


@dashboard_bp.route("/settings")
@login_required
def settings():
    return render_template("settings.html", incident_threshold=current_app.config["INCIDENT_RISK_THRESHOLD"])
