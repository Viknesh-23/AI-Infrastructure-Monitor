from flask import Blueprint, abort, current_app, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from models import db
from models.metric import Metric
from models.server import Server
from services.monitoring_service import generate_metric

monitoring_bp = Blueprint("monitoring", __name__, url_prefix="/monitoring")


def get_owned_server(server_id):
    server = db.session.get(Server, server_id)
    if not server or server.user_id != current_user.id:
        abort(404)
    return server


def _trim_history(server):
    """Keep the local demo database bounded without losing recent trends."""
    limit = current_app.config["MAX_METRICS_PER_SERVER"]
    stale = server.metrics.order_by(Metric.timestamp.desc()).offset(limit).all()
    for metric in stale:
        db.session.delete(metric)


def _collect_metric(server, simulate_failure=False):
    metric, incident = generate_metric(
        server,
        simulate_failure=simulate_failure,
        incident_threshold=current_app.config["INCIDENT_RISK_THRESHOLD"],
    )
    _trim_history(server)
    db.session.commit()
    return metric, incident


def _metric_response(server, metric, incident):
    return jsonify(
        {
            "message": f"{'Failure simulated' if metric.is_anomaly else 'Metrics generated'} for {server.name}.",
            "server": {"id": server.id, "name": server.name, "status": server.status},
            "metric": metric.as_dict(),
            "incident": {
                "id": incident.id,
                "code": incident.incident_code,
                "severity": incident.severity,
            }
            if incident
            else None,
        }
    )


@monitoring_bp.route("/")
@login_required
def monitoring_page():
    return render_template("monitoring.html", servers=current_user.servers)


@monitoring_bp.route("/generate/<int:server_id>", methods=["POST"])
@login_required
def generate(server_id):
    server = get_owned_server(server_id)
    metric, incident = _collect_metric(server)
    message = f"Metrics generated for {server.name}: {metric.failure_risk}% failure risk."
    if incident and incident.created_at == incident.updated_at:
        message += f" Incident {incident.incident_code} is active."
    flash(message, "warning" if metric.is_anomaly else "success")
    return redirect(request.referrer or url_for("servers.server_detail", server_id=server_id))


@monitoring_bp.route("/simulate-failure/<int:server_id>", methods=["POST"])
@login_required
def simulate_failure(server_id):
    server = get_owned_server(server_id)
    metric, incident = _collect_metric(server, simulate_failure=True)
    flash(
        f"Failure simulated on {server.name}. Risk is {metric.failure_risk}% and incident {incident.incident_code if incident else 'is already active'}.",
        "danger",
    )
    return redirect(request.referrer or url_for("servers.server_detail", server_id=server_id))


@monitoring_bp.route("/generate-all", methods=["POST"])
@login_required
def generate_all():
    count = 0
    for server in current_user.servers:
        generate_metric(server, incident_threshold=current_app.config["INCIDENT_RISK_THRESHOLD"])
        _trim_history(server)
        count += 1
    db.session.commit()
    flash(f"Generated a fresh metric sample for {count} server(s).", "success")
    return redirect(url_for("servers.list_servers"))


@monitoring_bp.route("/api/server/<int:server_id>/metrics", methods=["POST"])
@login_required
def generate_api(server_id):
    """Generate one normal telemetry sample for Fetch API consumers."""
    server = get_owned_server(server_id)
    metric, incident = _collect_metric(server)
    return _metric_response(server, metric, incident)


@monitoring_bp.route("/api/server/<int:server_id>/simulate-failure", methods=["POST"])
@login_required
def simulate_failure_api(server_id):
    """Generate one high-risk sample to exercise the incident workflow."""
    server = get_owned_server(server_id)
    metric, incident = _collect_metric(server, simulate_failure=True)
    return _metric_response(server, metric, incident)


@monitoring_bp.route("/api/server/<int:server_id>/history")
@login_required
def server_history(server_id):
    server = get_owned_server(server_id)
    metrics = server.metrics.order_by(Metric.timestamp.desc()).limit(40).all()[::-1]
    return jsonify({
        "labels": [m.timestamp.strftime("%d %b %H:%M") for m in metrics],
        "cpu": [m.cpu_usage for m in metrics],
        "memory": [m.memory_usage for m in metrics],
        "disk": [m.disk_usage for m in metrics],
        "latency": [m.network_latency for m in metrics],
        "risk": [m.failure_risk for m in metrics],
    })
