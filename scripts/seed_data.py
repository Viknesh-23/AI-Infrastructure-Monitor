"""Reset the local database and populate a realistic monitoring demo.

Run from the project root with: python scripts/seed_data.py
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import app  # noqa: E402
from models import db  # noqa: E402
from models.metric import Metric  # noqa: E402
from models.server import Server  # noqa: E402
from models.user import User  # noqa: E402
from services.monitoring_service import generate_metric  # noqa: E402


SERVERS = [
    ("SRV-WEB-01", "Production Web Gateway", "10.10.1.10", "Ubuntu 22.04 LTS", "Production"),
    ("SRV-API-01", "Production API Cluster", "10.10.1.21", "Ubuntu 22.04 LTS", "Production"),
    ("SRV-DB-01", "Primary PostgreSQL", "10.10.2.15", "Rocky Linux 9", "Production"),
    ("SRV-QA-01", "QA Automation Host", "10.20.1.17", "Windows Server 2022", "Testing"),
    ("SRV-DEV-01", "Development Services", "10.30.1.8", "Ubuntu 24.04 LTS", "Development"),
]


def seed():
    with app.app_context():
        db.drop_all()
        db.create_all()

        admin = User(username="admin", email="admin@example.com")
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.flush()

        servers = []
        for code, name, ip_address, os_name, environment in SERVERS:
            server = Server(
                server_code=code,
                name=name,
                ip_address=ip_address,
                os=os_name,
                environment=environment,
                status="Healthy",
                user_id=admin.id,
            )
            db.session.add(server)
            servers.append(server)
        db.session.flush()

        # Establish a history large enough for Isolation Forest on the next sample.
        for server in servers:
            for _ in range(14):
                generate_metric(server, incident_threshold=65)
        # Deliberately create representative initial incidents for the demo.
        generate_metric(servers[1], simulate_failure=True, incident_threshold=65)
        generate_metric(servers[2], simulate_failure=True, incident_threshold=65)
        db.session.commit()

        metric_count = Metric.query.count()
        print(f"Seeded {len(servers)} servers, {metric_count} metrics, and demo incidents.")
        print("Default login: admin / admin123")


if __name__ == "__main__":
    seed()
