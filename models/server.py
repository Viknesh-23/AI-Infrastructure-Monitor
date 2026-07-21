from datetime import datetime

from models import db


class Server(db.Model):
    __tablename__ = "servers"

    id = db.Column(db.Integer, primary_key=True)
    server_code = db.Column(db.String(40), unique=True, nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    ip_address = db.Column(db.String(45), nullable=False)
    os = db.Column(db.String(100), nullable=False)
    environment = db.Column(db.String(30), nullable=False, default="Development")
    status = db.Column(db.String(20), nullable=False, default="Healthy")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

    owner = db.relationship("User", back_populates="servers")
    metrics = db.relationship("Metric", back_populates="server", cascade="all, delete-orphan", lazy="dynamic")
    incidents = db.relationship("Incident", back_populates="server", cascade="all, delete-orphan", lazy="dynamic")

    @property
    def operating_system(self):
        """Readable alias used by the presentation layer."""
        return self.os

    @property
    def latest_metric(self):
        return self.metrics.order_by(db.desc("timestamp")).first()

    def __repr__(self):
        return f"<Server {self.server_code}>"
