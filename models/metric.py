from datetime import datetime

from models import db


class Metric(db.Model):
    __tablename__ = "metrics"

    id = db.Column(db.Integer, primary_key=True)
    server_id = db.Column(db.Integer, db.ForeignKey("servers.id"), nullable=False, index=True)
    cpu_usage = db.Column(db.Float, nullable=False)
    memory_usage = db.Column(db.Float, nullable=False)
    disk_usage = db.Column(db.Float, nullable=False)
    network_latency = db.Column(db.Float, nullable=False)
    network_traffic = db.Column(db.Float, nullable=False)
    error_rate = db.Column(db.Float, nullable=False)
    response_time = db.Column(db.Float, nullable=False)
    system_load = db.Column(db.Float, nullable=False)
    is_anomaly = db.Column(db.Boolean, default=False, nullable=False)
    anomaly_method = db.Column(db.String(40), default="threshold", nullable=False)
    risk_score = db.Column(db.Float, default=0, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    server = db.relationship("Server", back_populates="metrics")

    @property
    def failure_risk(self):
        """Compatibility name for the calculated failure-risk percentage."""
        return self.risk_score

    @property
    def recorded_at(self):
        """Compatibility name for timestamp used by existing visualisations."""
        return self.timestamp

    def as_dict(self):
        return {
            "cpu_usage": self.cpu_usage,
            "memory_usage": self.memory_usage,
            "disk_usage": self.disk_usage,
            "network_latency": self.network_latency,
            "network_traffic": self.network_traffic,
            "error_rate": self.error_rate,
            "response_time": self.response_time,
            "system_load": self.system_load,
            "is_anomaly": self.is_anomaly,
            "risk_score": self.risk_score,
            "failure_risk": self.risk_score,
            "timestamp": self.timestamp.isoformat(),
        }
