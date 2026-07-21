from datetime import datetime

from models import db


class Incident(db.Model):
    __tablename__ = "incidents"

    id = db.Column(db.Integer, primary_key=True)
    incident_code = db.Column(db.String(40), unique=True, nullable=False, index=True)
    server_id = db.Column(db.Integer, db.ForeignKey("servers.id"), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    severity = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="Open", index=True)
    failure_risk = db.Column(db.Float, nullable=False)
    detected_metrics = db.Column(db.Text, nullable=False)
    ai_root_cause = db.Column(db.Text, nullable=False)
    ai_recommendation = db.Column(db.Text, nullable=False)
    issue_fingerprint = db.Column(db.String(100), nullable=False, default="performance")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    resolved_at = db.Column(db.DateTime, nullable=True)

    server = db.relationship("Server", back_populates="incidents")

    @property
    def metrics_dict(self):
        import json
        return json.loads(self.detected_metrics)
