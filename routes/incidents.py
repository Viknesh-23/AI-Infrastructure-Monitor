from datetime import datetime

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from models import db
from models.incident import Incident

incidents_bp = Blueprint("incidents", __name__, url_prefix="/incidents")


def owned_incident(incident_id):
    incident = db.session.get(Incident, incident_id)
    if not incident or incident.server.user_id != current_user.id:
        abort(404)
    return incident


@incidents_bp.route("/")
@login_required
def list_incidents():
    severity = request.args.get("severity", "")
    status = request.args.get("status", "")
    search = request.args.get("q", "").strip()
    query = Incident.query.join(Incident.server).filter(Incident.server.has(user_id=current_user.id))
    if severity:
        query = query.filter(Incident.severity == severity)
    if status:
        query = query.filter(Incident.status == status)
    if search:
        query = query.filter((Incident.title.ilike(f"%{search}%")) | (Incident.incident_code.ilike(f"%{search}%")))
    return render_template("incidents.html", incidents=query.order_by(Incident.created_at.desc()).all())


@incidents_bp.route("/<int:incident_id>")
@login_required
def incident_detail(incident_id):
    return render_template("incident_detail.html", incident=owned_incident(incident_id))


@incidents_bp.route("/<int:incident_id>/status", methods=["POST"])
@login_required
def update_status(incident_id):
    incident = owned_incident(incident_id)
    status = request.form.get("status")
    if status not in ("Open", "Investigating", "Resolved"):
        flash("Invalid incident status.", "danger")
    else:
        incident.status = status
        incident.resolved_at = datetime.utcnow() if status == "Resolved" else None
        if status == "Resolved":
            remaining_active = incident.server.incidents.filter(
                Incident.id != incident.id,
                Incident.status.in_(["Open", "Investigating"]),
            ).count()
            if remaining_active == 0:
                incident.server.status = "Healthy"
        db.session.commit()
        flash(f"Incident marked as {status}.", "success")
    return redirect(url_for("incidents.incident_detail", incident_id=incident.id))
