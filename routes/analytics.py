from collections import Counter

from flask import Blueprint, render_template
from flask_login import current_user, login_required

from models.incident import Incident

analytics_bp = Blueprint("analytics", __name__, url_prefix="/analytics")


@analytics_bp.route("/")
@login_required
def index():
    incidents = Incident.query.join(Incident.server).filter(Incident.server.has(user_id=current_user.id)).all()
    severity = Counter(i.severity for i in incidents)
    server_counts = Counter(i.server.name for i in incidents)
    status = Counter(i.status for i in incidents)
    risks = [m.failure_risk for s in current_user.servers for m in s.metrics.limit(100).all()]
    data = {
        "severity": severity,
        "servers": server_counts.most_common(6),
        "status": status,
        "average_risk": round(sum(risks) / len(risks), 1) if risks else 0,
        "total": len(incidents),
    }
    return render_template("analytics.html", data=data)
