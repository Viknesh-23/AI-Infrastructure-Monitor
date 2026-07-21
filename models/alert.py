from datetime import datetime

from models import db


class Alert(db.Model):
    __tablename__ = "alerts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    server_id = db.Column(db.Integer, db.ForeignKey("servers.id"), nullable=True)
    title = db.Column(db.String(180), nullable=False)
    message = db.Column(db.Text, nullable=False)
    severity = db.Column(db.String(20), nullable=False, default="Info")
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    user = db.relationship("User", back_populates="alerts")
    server = db.relationship("Server")

    @property
    def level(self):
        """CSS-friendly lowercase severity label."""
        return self.severity.lower()
